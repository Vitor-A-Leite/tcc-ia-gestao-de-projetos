"""Retomada técnica de uma rodada final interrompida por falhas de conexão.

Executa as tarefas ainda pendentes e refaz UMA vez apenas as tarefas cuja
tentativa original falhou por rede (código 'rede') ou ficou interrompida
('em_andamento'). O registro original é preservado em
casos/_tentativas_originais/ e cada nova tentativa usa uma rodada própria no
ledger (sufixo ':rt1'). Falhas de contrato (erro do modelo) nunca são refeitas.

O código congelado no manifesto precisa estar intacto: só este script pode ter
sido acrescentado depois do preparo.
"""
import argparse
import json
from pathlib import Path
import shutil

from ..src import ROOT
from ..src import lote_ia as lote
from ..src import avaliacao_final as AF
from ..src import extracao as X
from ..src import ia_sozinha as D
from ..src.auditoria import SessaoAuditoriaReal
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.sessoes import gravar
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json
from . import avaliacao_final as AV
from .avaliar_revisor_v2 import hashes_codigo, RESERVA_NANO

ESTE = str(Path(__file__).resolve().relative_to(ROOT))
SUFIXO = 'rt1'


def validar(pasta):
    m = AV.ler(pasta/'manifesto.json')
    exigir(m['hash'] == hash_json({k: v for k, v in m.items() if k != 'hash'}), 'Manifesto adulterado')
    AF.configurar(m.get('rodada', 'final'))
    atual = hashes_codigo()
    exigir(all(atual.get(p) == h for p, h in m['codigo'].items()), 'Código congelado foi alterado')
    exigir(set(atual) - set(m['codigo']) <= {ESTE}, 'Há arquivos de código novos além da retomada técnica')
    exigir(m['modelo'] == MODELO and m['configuracao'] == CONFIG, 'Configuração mudou')
    exigir(m['prompts'] == dict(extracao=hash_json(X.SISTEMA), ia_sozinha=hash_json(D.SISTEMA)), 'Instruções mudaram')
    exigir(m['origens'] == AV.origens(), 'Material, gabarito ou cenários mudaram')
    for e in m['entradas']:
        exigir(lote.sha(pasta/e['arquivo']) == e['sha256'], 'Entrada mudou')
    return m


def refazer(reg):
    if reg['estado'] == 'em_andamento':
        return True
    erros = (reg.get('resultado') or {}).get('erros', [])
    return reg['estado'] == 'falha' and bool(erros) and erros[0].get('codigo') == 'rede'


def tentar(pasta, t, rep, m, chave, original, *, http=None):
    nome = f"r{rep}_{t['id']}"
    destino = pasta/'casos'/f'{nome}.json'
    transporte = TransporteReal(pasta/'chamadas'/f'{nome}_{SUFIXO}', chave, lote.comprometido(lote.HISTORICO), http=http,
        ledger=lote.LEDGER, rodada=f"{m['id']}:{nome}:{SUFIXO}", teto_total_nano=m['teto_total_nano'],
        teto_rodada_nano=RESERVA_NANO, max_chamadas=1, grupo=m['id'], teto_grupo_nano=m['teto_rodada_nano'])
    try:
        exigir(transporte.snapshot()['chamadas_api'] == 0, 'Retomada técnica já tentada para esta tarefa')
        reg = dict(tarefa=t['id'], condicao=t['condicao'], repeticao=rep, manifesto_hash=m['hash'], estado='em_andamento',
                   resultado=None, modo='ia_real' if http is None else 'teste_http_injetado',
                   retomada_tecnica=dict(sufixo=SUFIXO, tentativa_original=original))
        with destino.open('x', encoding='utf8') as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
        sessao = SessaoAuditoriaReal(reg, destino, dict(max_solicitacoes=1, max_tokens_entrada=64000,
            max_tokens_saida=16000, max_segundos=600, max_custo_centavos=1.5))
        adaptador = X.TransporteExtracaoReal(transporte)
        if t['condicao'] == 'B':
            r = X.ExtratorIA(adaptador, modelo=MODELO, configuracao=CONFIG, modo='ia_real',
                             modo_validacao=m.get('modo_validacao', 'estrito')).extrair(t['documento'], sessao=sessao)
            ok = r['estado'] == 'extracao_recebida'
        else:
            r = D.AnotadorIA(adaptador, modelo=MODELO, configuracao=CONFIG, modo='ia_real').anotar(t['evento'], t['documentos'], sessao=sessao)
            ok = r['estado'] == 'anotacao_recebida'
        reg['resultado'], reg['estado'] = r, ('concluido' if ok else 'falha')
        sessao.salvar()
        return reg
    finally:
        transporte.db.close()


def executar(pasta, *, autorizacao, repeticoes=None, http=None):
    exigir(isinstance(autorizacao, str) and bool(autorizacao.strip()), 'Autorização obrigatória')
    pasta = Path(pasta)
    m = validar(pasta)
    reps = repeticoes or list(range(1, m['repeticoes']+1))
    arquivo = pasta/f"retomada_tecnica_{'_'.join(map(str, reps))}.json"
    registro = dict(manifesto_hash=m['hash'], autorizacao=autorizacao, inicio=lote.agora(), refeitas={}, pendentes={})
    chave = None
    arquivo_orig = pasta/'casos'/'_tentativas_originais'
    for rep in reps:
        for e in m['entradas']:
            t = AV.ler(pasta/e['arquivo'])
            nome = f"r{rep}_{t['id']}"
            caso = pasta/'casos'/f'{nome}.json'
            if chave is None:
                chave = lote.ler_chave() if http is None else 'chave-ficticia-teste'
            if not caso.exists():
                registro['pendentes'][nome] = AV.executar_tarefa(pasta, t, rep, m, chave, http=http)['estado']
            elif refazer(AV.ler(caso)):
                arquivo_orig.mkdir(exist_ok=True)
                guardado = arquivo_orig/f'{nome}.json'
                exigir(not guardado.exists(), 'Tarefa já teve retomada técnica')
                shutil.move(str(caso), guardado)
                original = dict(arquivo=str(guardado.relative_to(pasta)), estado=AV.ler(guardado)['estado'])
                registro['refeitas'][nome] = tentar(pasta, t, rep, m, chave, original, http=http)['estado']
            else:
                continue
            gravar(arquivo, registro)
    registro['fim'] = lote.agora()
    completos = all((pasta/'casos'/f"r{r}_{e['id']}.json").exists() for r in range(1, m['repeticoes']+1) for e in m['entradas'])
    if completos:
        AV.comparar(pasta, m)
    registro['estado'] = 'comparacao_gerada' if completos else 'parcial'
    gravar(arquivo, registro)
    return registro


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pasta')
    p.add_argument('--autorizacao', default='')
    p.add_argument('--repeticao', type=int, action='append')
    a = p.parse_args()
    r = executar(a.pasta, autorizacao=a.autorizacao, repeticoes=a.repeticao)
    print(json.dumps(dict(estado=r['estado'], refeitas=r['refeitas'], pendentes=len(r['pendentes'])), ensure_ascii=False))


if __name__ == '__main__':
    main()
