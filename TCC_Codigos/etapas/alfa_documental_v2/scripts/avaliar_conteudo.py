"""Avaliação offline da revisão de conteúdo em D01–D09 (casos de desenvolvimento).

Condição A: afirmações cadastradas manualmente no registro vigente (linha de base).
Condição C: afirmações de referência dos documentos em prosa.
Condição B (extração por IA) depende da rodada real F5 e não é executada aqui.
Nenhuma chamada de IA é feita; as referências só são lidas depois das avaliações.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from ..src import ROOT
from ..src import conteudo as C
from ..src.pipeline import ler_cenario, simular
from ..src.vendor.interpretacao_no.contratos import hash_json

REFERENCIAS = ROOT/'avaliacao/referencias/conteudo'
CENARIOS = tuple(f'D0{i}' for i in range(1, 10))


def ler(p):
    return json.loads(Path(p).read_text())


def extracoes_referencia(cenario):
    ref = ler(REFERENCIAS/'afirmacoes_referencia.json')
    idx = {(e['documento_id'], e['versao']): e for e in ref['extracoes']}
    return [idx[(d['id'], d['versao'])] for d in C.documentos_do_cenario(cenario)]


def revisar(cid, condicao, resultado=None):
    cenario = ler_cenario(cid)
    resultado = resultado or simular(cid)
    ext = C.afirmacoes_cadastro(cenario) if condicao == 'cadastro' else extracoes_referencia(cenario)
    return C.revisar_documentos(resultado, cenario, ext, condicao=condicao), resultado


def _contagens(pares):
    """pares: (esperado, obtido) de (estado, motivo)."""
    vp = sum(e[0] == 'revisar' and o[0] == 'revisar' for e, o in pares)
    fp = sum(e[0] != 'revisar' and o[0] == 'revisar' for e, o in pares)
    fn = sum(e[0] == 'revisar' and o[0] != 'revisar' for e, o in pares)
    return dict(afirmacoes=len(pares), estado_igual=sum(e[0] == o[0] for e, o in pares),
                estado_e_motivo_iguais=sum(e == o for e, o in pares),
                revisar_vp=vp, revisar_fp=fp, revisar_fn=fn,
                precisao_revisar=vp/(vp+fp) if vp+fp else None, revocacao_revisar=vp/(vp+fn) if vp+fn else None)


def executar(destino):
    destino = Path(destino)
    if destino.exists():
        raise FileExistsError('Destino já existe; escolha um novo diretório')
    destino.mkdir(parents=True)
    revisoes, linha_base = {}, {}
    for cid in CENARIOS:
        rc, resultado = revisar(cid, 'referencia')
        ra, _ = revisar(cid, 'cadastro', resultado)
        revisoes[cid] = dict(referencia=rc, cadastro=ra)
        antigo = {x['trecho_id']: x['estado'] for x in resultado['verificacao_documental']['afirmacoes']}
        novo = {r['afirmacao']['trecho_id']: r['estado'] for r in ra['documentos'][0]['afirmacoes']}
        linha_base[cid] = dict(reproduz_verificacao_atual=antigo == novo, verificar=antigo, cadastro=novo)
        (destino/f'{cid}.json').write_text(json.dumps(revisoes[cid], ensure_ascii=False, indent=1))
    # Referências lidas somente após gravar todas as revisões.
    esperado = ler(REFERENCIAS/'dev/estados_esperados.json')
    por_cenario, todos, divergencias = {}, [], []
    for cid in CENARIOS:
        obt = {r['afirmacao']['id']: (r['estado'], r['motivo'])
               for d in revisoes[cid]['referencia']['documentos'] for r in d['afirmacoes']}
        pares = []
        for aid, e in esperado['cenarios'][cid].items():
            o = obt.get(aid, ('ausente', None))
            pares.append(((e['estado'], e['motivo']), o))
            if (e['estado'], e['motivo']) != o:
                divergencias.append(dict(cenario=cid, afirmacao=aid, esperado=e, obtido=dict(estado=o[0], motivo=o[1])))
        por_cenario[cid] = _contagens(pares)
        todos += pares
    comparacao = dict(
        versao=C.VERSAO, data=datetime.now(timezone.utc).isoformat(),
        natureza='desenvolvimento_offline: D01–D09 são casos expostos; a referência foi redigida pelo agente antes do avaliador e não substitui a anotação independente da dupla',
        condicoes=dict(A='cadastro manual do registro vigente', C='afirmações de referência dos documentos em prosa',
                       B='extração por IA — pendente (F5 exige autorização e orçamento)'),
        linha_base_A=linha_base, condicao_C=dict(total=_contagens(todos), por_cenario=por_cenario, divergencias=divergencias),
        hashes=dict(referencia=hash_json(ler(REFERENCIAS/'afirmacoes_referencia.json')), esperado=hash_json(esperado),
                    corpus=hash_json(C.carregar_corpus())),
        chamadas_ia=0)
    (destino/'comparacao.json').write_text(json.dumps(comparacao, ensure_ascii=False, indent=1))
    return comparacao


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('destino')
    a = p.parse_args()
    r = executar(a.destino)
    print(json.dumps(dict(A_reproduz=all(x['reproduz_verificacao_atual'] for x in r['linha_base_A'].values()),
                          C=r['condicao_C']['total'], divergencias=len(r['condicao_C']['divergencias'])), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
