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
    caminhos += sorted((DATA/'cenarios'/AF.PARTICAO).glob('*.json')) + sorted((DATA/'simulacoes'/AF.PARTICAO).glob('*.json'))
    return {str(p.relative_to(ROOT)): lote.sha(p) for p in caminhos}


def tarefas():
    docs = {d['id']: d for d in AF.documentos_finais()}
    evs = AF.eventos()
    t = [dict(id=f'B_{i}', condicao='B', documento=docs[i]) for i in docs]
    for e in AF.EVENTOS:
        for n, g in enumerate(AF.GRUPOS_D, 1):
            t.append(dict(id=f'D_{e}_G{n}', condicao='D', evento=evs[e], documentos=[docs[i] for i in g]))
    return t


def preparar(destino, repeticoes=REPETICOES, modo_validacao='parcial', rodada='final'):
    AF.configurar(rodada)
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
    m = dict(id=rodada+'-'+uuid.uuid4().hex, rodada=rodada, preparado_em=lote.agora(), modelo=MODELO, configuracao=CONFIG,
        repeticoes=repeticoes, entradas=entradas, chamadas_previstas=chamadas, origens=origens(), codigo=hashes_codigo(),
        versoes=dict(extracao=X.VERSAO, ia_sozinha=D.VERSAO, conteudo=C.VERSAO),
        prompts=dict(extracao=hash_json(X.SISTEMA), ia_sozinha=hash_json(D.SISTEMA)), catalogo_hash=hash_json(catalogo),
        regra_agregacao=AF.REGRA_AGREGACAO, regra_e=AF.REGRA_E, modo_validacao=modo_validacao, grupos_d=[list(g) for g in AF.GRUPOS_D],
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
    AF.configurar(m.get('rodada', 'final'))
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
            r = X.ExtratorIA(adaptador, modelo=MODELO, configuracao=CONFIG, modo='ia_real',
                             modo_validacao=m.get('modo_validacao', 'estrito')).extrair(t['documento'], sessao=sessao)
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


def _extracoes_b(pasta, rep, docs, modo, modo_manifesto, catalogo, versao=None):
    """Extração válida de cada documento numa repetição; revalida a resposta bruta se o modo pedido difere do congelado."""
    saida = {}
    for d in docs:
        arq = pasta/'casos'/f"r{rep}_B_{d['id']}.json"
        if not arq.exists():
            continue
        reg = ler(arq)
        res = reg.get('resultado') or {}
        if modo == modo_manifesto:
            if reg['estado'] == 'concluido':
                saida[d['id']] = res['extracao']
            continue
        if res.get('resposta_bruta'):
            try:
                saida[d['id']] = X.validar_extracao(json.loads(res['resposta_bruta']), d, catalogo, modo=modo, versao=versao)
            except Exception:
                pass
    return saida


def _anotacoes_d(pasta, rep, ev):
    an = {}
    for n in range(1, len(AF.GRUPOS_D)+1):
        arq = pasta/'casos'/f'r{rep}_D_{ev}_G{n}.json'
        if arq.exists():
            reg = ler(arq)
            if reg['estado'] == 'concluido':
                an.update(reg['resultado']['anotacoes'])
    return an


def comparar(pasta, m, *, modo_validacao=None, arquivo='comparacao.json', natureza='resultado_principal_congelado'):
    """Métricas de B, D, E (B+D) e das variantes com voto entre as leituras de B.

    Com `modo_validacao` diferente do congelado, as respostas brutas de B são revalidadas
    (análise pós-hoc, gravada em outro arquivo).
    """
    docs = AF.documentos_finais()
    catalogo = X.catalogo_entidades()
    _, gab = AF.carregar_gabarito()
    exigir(lote.sha(AF.GABARITO) == m['gabarito']['sha256'], 'Gabarito mudou desde o preparo')
    modo_manifesto = m.get('modo_validacao', 'estrito')
    modo = modo_validacao or modo_manifesto
    AF.configurar(m.get('rodada', 'final'))
    resultados = {e: simular(e, AF.PARTICAO) for e in AF.EVENTOS}
    cenarios = {e: ler_cenario(e, AF.PARTICAO) for e in AF.EVENTOS}
    reps = list(range(1, m['repeticoes']+1))
    ext = {r: _extracoes_b(pasta, r, docs, modo, modo_manifesto, catalogo, m.get('versoes', {}).get('extracao')) for r in reps}
    anot = {(r, ev): _anotacoes_d(pasta, r, ev) for r in reps for ev in AF.EVENTOS}
    voto = {}
    for d in docs:
        leituras = [ext[r][d['id']] for r in reps if d['id'] in ext[r]]
        if leituras:
            voto[d['id']] = X.combinar_extracoes(leituras, d)

    def condicao_b(extracoes, d_rep=None):
        pred, mot, pred_e, mot_e = {}, {}, {}, {}
        for ev in AF.EVENTOS:
            rev = C.revisar_documentos(resultados[ev], cenarios[ev], list(extracoes.values()), condicao='B')
            for t, r in AF.agregar_b(rev, docs).items():
                pred[(ev, t)] = r
            for t, ms in AF.motivos_b(rev).items():
                mot[(ev, t)] = ms
            if d_rep is not None:
                re_, me_ = AF.agregar_e(rev, anot[(d_rep, ev)], docs)
                for t, r in re_.items():
                    pred_e[(ev, t)] = r
                for t, ms in me_.items():
                    mot_e[(ev, t)] = ms
        return pred, mot, pred_e, mot_e

    por = {c: [] for c in ('B', 'D', 'E', 'E_voto')}
    saida = dict(manifesto=m['id'], natureza=natureza, modo_validacao=modo, regra_agregacao=m['regra_agregacao'],
                 regra_e=AF.REGRA_E, gabarito=m['gabarito'], repeticoes={})
    pb_voto, mb_voto, _, _ = condicao_b(voto)
    saida['B_voto'] = AF.metricas(pb_voto, gab, mb_voto)
    saida['B_voto']['documentos_com_leitura'] = len(voto)
    for r in reps:
        pb, mb, pe, me = condicao_b(ext[r], r)
        _, _, pev, mev = condicao_b(voto, r)
        pd, md = {}, {}
        for ev in AF.EVENTOS:
            for d in docs:
                for t in d['trechos']:
                    a = anot[(r, ev)].get(t['id'])
                    pd[(ev, t['id'])] = a['rotulo'] if a else 'FALHA'
                    if a:
                        md[(ev, t['id'])] = {i['motivo'] for i in a['informacoes']}
        res = dict(B=AF.metricas(pb, gab, mb), D=AF.metricas(pd, gab, md), E=AF.metricas(pe, gab, me), E_voto=AF.metricas(pev, gab, mev))
        res['B']['documentos_com_leitura'] = len(ext[r])
        for c in por:
            por[c].append(res[c])
        saida['repeticoes'][r] = res
        if arquivo == 'comparacao.json':
            gravar(pasta/f'predicoes_r{r}.json', {c: {f'{k[0]}|{k[1]}': v for k, v in p.items()} for c, p in (('B', pb), ('D', pd), ('E', pe), ('E_voto', pev))})
    saida['resumo'] = {c: AF.resumo_repeticoes(v) for c, v in por.items()}
    consumo, erros = {'B': Counter(), 'D': Counter()}, {'B': Counter(), 'D': Counter()}
    for arq in (pasta/'casos').glob('*.json'):
        reg = ler(arq)
        uso = reg.get('sessao_revisao', {}).get('consumo', {})
        for k in ('chamadas_api', 'tokens_entrada', 'tokens_saida', 'custo_api_usd', 'comprometido_api_usd'):
            consumo[reg['condicao']][k] += uso.get(k, 0)
        erros[reg['condicao']].update(x['codigo'] for x in (reg.get('resultado') or {}).get('erros', []))
    saida['consumo'] = {c: dict(v) for c, v in consumo.items()}
    saida['erros'] = {c: dict(v) for c, v in erros.items()}
    saida['comprometido_historico_total_usd'] = (lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER))/1e9
    gravar(pasta/arquivo, saida)
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
    p.add_argument('--posthoc-modo-validacao', choices=('estrito', 'parcial'))
    p.add_argument('--rodada', choices=tuple(AF.RODADAS), default='final')
    a = p.parse_args()
    if a.acao == 'preparar':
        m = preparar(a.pasta, rodada=a.rodada)
        print(json.dumps(dict(manifesto=m['id'], chamadas=m['chamadas_previstas'], reserva_maxima_usd=m['teto_rodada_nano']/1e9,
                              comprometido_antes_usd=m['comprometido_antes_nano']/1e9), ensure_ascii=False))
    elif a.acao == 'executar':
        r = executar(a.pasta, autorizacao=a.autorizacao, repeticoes=a.repeticao)
        print(json.dumps(dict(estado=r['estado'], tarefas=len(r['tarefas'])), ensure_ascii=False))
    else:
        pasta = Path(a.pasta)
        m = validar_manifesto(pasta) if not a.posthoc_modo_validacao else ler(pasta/'manifesto.json')
        if a.posthoc_modo_validacao:
            r = comparar(pasta, m, modo_validacao=a.posthoc_modo_validacao, arquivo=f'comparacao_posthoc_{a.posthoc_modo_validacao}.json',
                         natureza='PÓS-HOC: código e/ou validação diferentes dos congelados; não substitui o resultado principal')
        else:
            r = comparar(pasta, m)
        print(json.dumps({c: {k: (round(v['media'], 3) if isinstance(v, dict) and v else v) for k, v in s.items()} for c, s in r['resumo'].items()}, ensure_ascii=False, indent=1))
        print('B_voto', json.dumps({k: r['B_voto'][k] for k in ('revisar', 'acuracia_4_classes', 'falhas')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
