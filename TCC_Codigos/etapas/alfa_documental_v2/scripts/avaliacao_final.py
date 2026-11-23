"""Rodada final: condição B (sistema híbrido) × condição D (IA sozinha), 3 repetições.

`preparar` congela material, gabarito, cenários, código, instruções e regra de
agregação, sem chamar a API. `executar` exige autorização textual; cada chamada
tem uma única tentativa, checkpoint e reserva no ledger. O gabarito só é lido
em `comparar`, depois de todas as respostas.

    python -m TCC_Codigos.etapas.alfa_documental_v2.scripts.avaliacao_final preparar PASTA
    python -m ... executar PASTA --autorizacao "..." [--repeticao N]
"""
import argparse
from collections import Counter
import fcntl
import json
from pathlib import Path
import uuid

from ..src import ROOT, DATA
from ..src import lote_ia as lote
from ..src import conteudo as C
from ..src import avaliacao_final as AF
from ..src import extracao as X
from ..src import ia_sozinha as D
from ..src.auditoria import SessaoAuditoriaReal
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.pipeline import ler_cenario, simular
from ..src.sessoes import gravar
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json
from .avaliar_revisor_v2 import hashes_codigo, RESERVA_NANO, TETO_TOTAL_NANO

REPETICOES = 3


def ler(p):
    return json.loads(Path(p).read_text())


def origens():
    caminhos = [AF.MATERIAL, AF.GABARITO, DATA/'grafo.json', DATA/'documentos.json']
    caminhos += sorted((DATA/'cenarios/final').glob('*.json')) + sorted((DATA/'simulacoes/final').glob('*.json'))
    return {str(p.relative_to(ROOT)): lote.sha(p) for p in caminhos}


def tarefas():
    docs = {d['id']: d for d in AF.documentos_finais()}
    evs = AF.eventos()
    t = [dict(id=f'B_{i}', condicao='B', documento=docs[i]) for i in docs]
    for e in AF.EVENTOS:
        for n, g in enumerate(AF.GRUPOS_D, 1):
            t.append(dict(id=f'D_{e}_G{n}', condicao='D', evento=evs[e], documentos=[docs[i] for i in g]))
    return t


def preparar(destino, repeticoes=REPETICOES):
    destino = Path(destino)
    ts = tarefas()
    chamadas = len(ts)*repeticoes
    total_antes = lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER)
    teto = chamadas*RESERVA_NANO
    exigir(total_antes+teto <= TETO_TOTAL_NANO, 'Saldo insuficiente para as reservas')
    destino.mkdir(parents=True, exist_ok=False)
    entradas = []
    for t in ts:
        arq = destino/'entradas'/f"{t['id']}.json"
        gravar(arq, t)
        entradas.append(dict(id=t['id'], condicao=t['condicao'], arquivo=str(arq.relative_to(destino)), sha256=lote.sha(arq)))
    catalogo = X.catalogo_entidades()
    gab, _ = AF.carregar_gabarito()
    m = dict(id='final-'+uuid.uuid4().hex, preparado_em=lote.agora(), modelo=MODELO, configuracao=CONFIG,
        repeticoes=repeticoes, entradas=entradas, chamadas_previstas=chamadas, origens=origens(), codigo=hashes_codigo(),
        versoes=dict(extracao=X.VERSAO, ia_sozinha=D.VERSAO, conteudo=C.VERSAO),
        prompts=dict(extracao=hash_json(X.SISTEMA), ia_sozinha=hash_json(D.SISTEMA)), catalogo_hash=hash_json(catalogo),
        regra_agregacao=AF.REGRA_AGREGACAO, grupos_d=[list(g) for g in AF.GRUPOS_D],
        gabarito=dict(sha256=lote.sha(AF.GABARITO), estado=gab['estado'], kappa=gab['concordancia']['kappa_cohen']),
        metricas='Principal: precisão, revocação e F1 de REVISAR por par (evento, trecho). Secundárias: acurácia em 4 classes '
                 '(REVISAR, DECISAO_HUMANA, PRESERVAR, NAO_REVISAR) e 5 rótulos, falsos alertas em trechos corretos, '
                 'compatibilidade de motivo nos acertos, falhas, consumo; média, mínimo e máximo entre repetições.',
        historico_externo_sha256=lote.sha(lote.HISTORICO), comprometido_antes_nano=total_antes,
        reserva_por_chamada_nano=RESERVA_NANO, teto_rodada_nano=teto, teto_total_nano=TETO_TOTAL_NANO,
        interpretacao='B: a IA extrai afirmações de cada documento (independente do evento) e o código compara com o cálculo. '
                      'D: a IA recebe regras, estado inicial, evento e documentos e rotula cada trecho, sem estado calculado. '
                      'Uma tentativa por chamada; falhas preservadas nos denominadores.')
    m['hash'] = hash_json(m)
    gravar(destino/'manifesto.json', m)
    return m


def validar_manifesto(pasta):
    m = ler(pasta/'manifesto.json')
    exigir(m['hash'] == hash_json({k: v for k, v in m.items() if k != 'hash'}), 'Manifesto adulterado')
    exigir(m['codigo'] == hashes_codigo(), 'Implementação mudou desde o preparo')
    exigir(m['modelo'] == MODELO and m['configuracao'] == CONFIG, 'Configuração mudou')
    exigir(m['prompts'] == dict(extracao=hash_json(X.SISTEMA), ia_sozinha=hash_json(D.SISTEMA)), 'Instruções mudaram')
    exigir(m['origens'] == origens(), 'Material, gabarito ou cenários mudaram')
    exigir(m['historico_externo_sha256'] == lote.sha(lote.HISTORICO), 'Histórico financeiro mudou')
    for e in m['entradas']:
        exigir(lote.sha(pasta/e['arquivo']) == e['sha256'], 'Entrada mudou')
    return m


def executar_tarefa(pasta, t, rep, m, chave, *, http=None):
    nome = f"r{rep}_{t['id']}"
    destino = pasta/'casos'/f'{nome}.json'
    if destino.exists():
        reg = ler(destino)
        exigir(reg['manifesto_hash'] == m['hash'], 'Checkpoint de outro manifesto')
        return reg
    transporte = TransporteReal(pasta/'chamadas'/nome, chave, lote.comprometido(lote.HISTORICO), http=http, ledger=lote.LEDGER,
        rodada=m['id']+':'+nome, teto_total_nano=m['teto_total_nano'], teto_rodada_nano=RESERVA_NANO, max_chamadas=1,
        grupo=m['id'], teto_grupo_nano=m['teto_rodada_nano'])
    try:
        exigir(transporte.snapshot()['chamadas_api'] == 0, 'Carteira já possui tentativa para esta tarefa')
        reg = dict(tarefa=t['id'], condicao=t['condicao'], repeticao=rep, manifesto_hash=m['hash'], estado='em_andamento',
                   resultado=None, modo='ia_real' if http is None else 'teste_http_injetado')
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open('x', encoding='utf8') as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
        sessao = SessaoAuditoriaReal(reg, destino, dict(max_solicitacoes=1, max_tokens_entrada=64000,
            max_tokens_saida=16000, max_segundos=600, max_custo_centavos=1.5))
        adaptador = X.TransporteExtracaoReal(transporte)
        if t['condicao'] == 'B':
            r = X.ExtratorIA(adaptador, modelo=MODELO, configuracao=CONFIG, modo='ia_real').extrair(t['documento'], sessao=sessao)
            ok = r['estado'] == 'extracao_recebida'
        else:
            r = D.AnotadorIA(adaptador, modelo=MODELO, configuracao=CONFIG, modo='ia_real').anotar(t['evento'], t['documentos'], sessao=sessao)
            ok = r['estado'] == 'anotacao_recebida'
        reg['resultado'] = r
        reg['estado'] = 'concluido' if ok else 'falha'
        sessao.salvar()
        return reg
    finally:
        transporte.db.close()


def comparar(pasta, m):
    docs = AF.documentos_finais()
    gab_meta, gab = AF.carregar_gabarito()
    exigir(lote.sha(AF.GABARITO) == m['gabarito']['sha256'], 'Gabarito mudou desde o preparo')
    resultados = {e: simular(e, 'final') for e in AF.EVENTOS}
    cenarios = {e: ler_cenario(e, 'final') for e in AF.EVENTOS}
    saida = dict(manifesto=m['id'], regra_agregacao=m['regra_agregacao'], gabarito=m['gabarito'], repeticoes={}, consumo={}, erros={})
    por_cond = {'B': [], 'D': []}
    consumo = {'B': Counter(), 'D': Counter()}
    erros = {'B': Counter(), 'D': Counter()}
    for rep in range(1, m['repeticoes']+1):
        regs = {}
        for e in m['entradas']:
            p = pasta/'casos'/f"r{rep}_{e['id']}.json"
            if p.exists():
                regs[e['id']] = ler(p)
        for reg in regs.values():
            uso = reg.get('sessao_revisao', {}).get('consumo', {})
            for k in ('chamadas_api', 'tokens_entrada', 'tokens_saida', 'custo_api_usd', 'comprometido_api_usd'):
                consumo[reg['condicao']][k] += uso.get(k, 0)
            erros[reg['condicao']].update(x['codigo'] for x in (reg.get('resultado') or {}).get('erros', []))
        # Condição B
        extr = [regs[f'B_{d["id"]}']['resultado']['extracao'] for d in docs
                if regs.get(f'B_{d["id"]}', {}).get('estado') == 'concluido']
        pred_b, mot_b = {}, {}
        for ev in AF.EVENTOS:
            rev = C.revisar_documentos(resultados[ev], cenarios[ev], extr, condicao='B')
            for t, r in AF.agregar_b(rev, docs).items():
                pred_b[(ev, t)] = r
            for t, ms in AF.motivos_b(rev).items():
                mot_b[(ev, t)] = ms
        # Condição D
        pred_d, mot_d = {}, {}
        for ev in AF.EVENTOS:
            for n, g in enumerate(AF.GRUPOS_D, 1):
                reg = regs.get(f'D_{ev}_G{n}')
                ok = reg and reg['estado'] == 'concluido'
                for d in docs:
                    if d['id'] not in g:
                        continue
                    for t in d['trechos']:
                        a = reg['resultado']['anotacoes'][t['id']] if ok else None
                        pred_d[(ev, t['id'])] = a['rotulo'] if a else 'FALHA'
                        if a:
                            mot_d[(ev, t['id'])] = {i['motivo'] for i in a['informacoes']}
        mb, md = AF.metricas(pred_b, gab, mot_b), AF.metricas(pred_d, gab, mot_d)
        por_cond['B'].append(mb); por_cond['D'].append(md)
        saida['repeticoes'][rep] = dict(B=mb, D=md)
        gravar(pasta/f'predicoes_r{rep}.json', dict(B={f'{k[0]}|{k[1]}': v for k, v in pred_b.items()},
                                                     D={f'{k[0]}|{k[1]}': v for k, v in pred_d.items()}))
    saida['resumo'] = {c: AF.resumo_repeticoes(v) for c, v in por_cond.items()}
    saida['consumo'] = {c: dict(v) for c, v in consumo.items()}
    saida['erros'] = {c: dict(v) for c, v in erros.items()}
    saida['comprometido_historico_total_usd'] = (lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER))/1e9
    gravar(pasta/'comparacao.json', saida)
    return saida


def executar(pasta, *, autorizacao, repeticoes=None, http=None):
    exigir(isinstance(autorizacao, str) and bool(autorizacao.strip()), 'Autorização obrigatória')
    pasta = Path(pasta)
    m = validar_manifesto(pasta)
    reps = repeticoes or list(range(1, m['repeticoes']+1))
    exigir(all(1 <= r <= m['repeticoes'] for r in reps), 'Repetição fora do manifesto')
    sufixo = '_'.join(map(str, reps))
    with (pasta/f'execucao_{sufixo}.lock').open('a') as trava:
        fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
        registro = dict(manifesto_hash=m['hash'], estado='em_andamento', autorizacao=autorizacao, repeticoes=reps,
                        inicio=lote.agora(), tarefas={}, modo='ia_real' if http is None else 'teste_http_injetado')
        arquivo = pasta/f'execucao_{sufixo}.json'
        chave = None
        try:
            for rep in reps:
                for e in m['entradas']:
                    t = ler(pasta/e['arquivo'])
                    nome = f"r{rep}_{t['id']}"
                    registro['tarefa_atual'] = nome
                    gravar(arquivo, registro)
                    if chave is None and not (pasta/'casos'/f'{nome}.json').exists():
                        chave = lote.ler_chave() if http is None else 'chave-ficticia-teste'
                    registro['tarefas'][nome] = executar_tarefa(pasta, t, rep, m, chave, http=http)['estado']
                    gravar(arquivo, registro)
            completos = all((pasta/'casos'/f"r{r}_{e['id']}.json").exists() for r in range(1, m['repeticoes']+1) for e in m['entradas'])
            if completos:
                comparar(pasta, m)
            registro['estado'] = ('concluido' if all(v == 'concluido' for v in registro['tarefas'].values()) else 'concluido_com_falhas') if completos else 'parcial_aguardando_outras_repeticoes'
        except BaseException as exc:
            mensagem = str(exc).replace(chave, '[REDACTED]') if chave else str(exc)
            registro.update(estado='interrompido', erro=dict(tipo=type(exc).__name__, mensagem=mensagem))
            raise
        finally:
            registro['fim'] = lote.agora()
            gravar(arquivo, registro)
    return registro


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('acao', choices=('preparar', 'executar', 'comparar'))
    p.add_argument('pasta')
    p.add_argument('--autorizacao', default='')
    p.add_argument('--repeticao', type=int, action='append')
    a = p.parse_args()
    if a.acao == 'preparar':
        m = preparar(a.pasta)
        print(json.dumps(dict(manifesto=m['id'], chamadas=m['chamadas_previstas'], reserva_maxima_usd=m['teto_rodada_nano']/1e9,
                              comprometido_antes_usd=m['comprometido_antes_nano']/1e9), ensure_ascii=False))
    elif a.acao == 'executar':
        r = executar(a.pasta, autorizacao=a.autorizacao, repeticoes=a.repeticao)
        print(json.dumps(dict(estado=r['estado'], tarefas=len(r['tarefas'])), ensure_ascii=False))
    else:
        pasta = Path(a.pasta)
        r = comparar(pasta, validar_manifesto(pasta))
        print(json.dumps(r['resumo'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
