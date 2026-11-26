"""Análise de sensibilidade PÓS-HOC da rodada final (sem chamadas de IA).

Reavalia a condição B sobre as respostas brutas já gravadas, com dois ajustes
identificados depois da rodada. Não substitui o resultado principal congelado:
(a) validador tolerante: citação comparada sem diferença de maiúsculas e
    "não mapeados" repetidos do mesmo trecho fundidos;
(b) (a) mais normalização de versão ("revisão 1" = "1").
"""
from copy import deepcopy
import json
import re
from pathlib import Path
import sys

from ..src import avaliacao_final as AF
from ..src import conteudo as C
from ..src import extracao as X
from ..src.pipeline import ler_cenario, simular


def _tolerante(resposta, documento):
    r = deepcopy(resposta)
    textos = {t['id']: t['texto'] for t in documento['trechos']}
    for a in r.get('afirmacoes', []):
        txt = textos.get(a.get('trecho_id'), '')
        i = txt.lower().find(a.get('citacao', '').lower())
        if a.get('citacao') and i >= 0:
            a['citacao'] = txt[i:i+len(a['citacao'])]
    vistos, nao = set(), []
    for n in r.get('nao_mapeados', []):
        if n['trecho_id'] not in vistos:
            vistos.add(n['trecho_id']); nao.append(n)
    r['nao_mapeados'] = nao
    return r


def extracoes(pasta, rep, tolerante):
    docs = {d['id']: d for d in AF.documentos_finais()}
    cat = X.catalogo_entidades()
    saida = []
    for d in docs:
        reg = json.loads((pasta/'casos'/f'r{rep}_B_{d}.json').read_text())
        res = reg.get('resultado') or {}
        if reg['estado'] == 'concluido':
            saida.append(res['extracao']); continue
        if not tolerante or not res.get('resposta_bruta'):
            continue
        try:
            saida.append(X.validar_extracao(_tolerante(json.loads(res['resposta_bruta']), docs[d]), docs[d], cat))
        except Exception:
            pass
    return saida


def avaliar(pasta, tolerante, versao):
    _, gab = AF.carregar_gabarito()
    docs = AF.documentos_finais()
    resultados = {e: simular(e, 'final') for e in AF.EVENTOS}
    cenarios = {e: ler_cenario(e, 'final') for e in AF.EVENTOS}
    norm = lambda s: re.sub(r'\D', '', str(s)) or str(s)
    reps = []
    for rep in (1, 2, 3):
        ext = extracoes(pasta, rep, tolerante)
        if versao:
            for e in ext:
                for a in e['afirmacoes']:
                    if a['predicado'] == 'versao' and isinstance(a['valor'], str):
                        a['valor'] = norm(a['valor'])
        pred, mot = {}, {}
        for ev in AF.EVENTOS:
            rev = C.revisar_documentos(resultados[ev], cenarios[ev], ext, condicao='B_sensibilidade')
            for t, r in AF.agregar_b(rev, docs).items():
                pred[(ev, t)] = r
            for t, ms in AF.motivos_b(rev).items():
                mot[(ev, t)] = ms
        m = AF.metricas(pred, gab, mot)
        m['documentos_validos'] = len(ext)
        reps.append(m)
    return dict(repeticoes=reps, resumo=AF.resumo_repeticoes(reps))


def main():
    pasta = Path(sys.argv[1])
    out = dict(natureza='PÓS-HOC: ajustes identificados após a rodada; não substitui o resultado principal congelado.',
               B_principal=json.loads((pasta/'comparacao.json').read_text())['resumo']['B'],
               B_validador_tolerante=avaliar(pasta, True, False),
               B_tolerante_e_versao_normalizada=avaliar(pasta, True, True))
    (pasta/'sensibilidade_posthoc.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for k in ('B_validador_tolerante', 'B_tolerante_e_versao_normalizada'):
        r = out[k]['resumo']
        print(k, {x: round(r[x]['media'], 3) for x in ('precisao', 'revocacao', 'f1', 'acuracia_4_classes')},
              'falhas', r['falhas'], 'docs válidos', [m['documentos_validos'] for m in out[k]['repeticoes']])


if __name__ == '__main__':
    main()
