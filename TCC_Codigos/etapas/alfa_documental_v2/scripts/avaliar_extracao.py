"""Rodada real de extração de afirmações (F5) com carteira persistente.

`preparar` congela documentos, catálogo, código e referências, sem chamar a API.
`executar` exige autorização textual, faz uma tentativa por documento (sem retry
nem cache) e só depois lê as referências para comparar: métricas de extração e
condição B (afirmações extraídas pela IA) em D01–D09, offline.
"""
import argparse
from collections import Counter
from copy import deepcopy
import fcntl
import json
from pathlib import Path
import uuid

from ..src import ROOT
from ..src import lote_ia as lote
from ..src import conteudo as C
from ..src.auditoria import SessaoAuditoriaReal
from ..src.extracao import (VERSAO, ExtratorIA, TransporteExtracaoReal, catalogo_entidades,
                            comparar_extracoes, montar_pedido, SISTEMA, _chave)
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.pipeline import ler_cenario, simular
from ..src.sessoes import gravar
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json
from .avaliar_revisor_v2 import hashes_codigo, RESERVA_NANO, TETO_TOTAL_NANO

REFERENCIAS = ROOT/'avaliacao/referencias/conteudo'
CENARIOS = tuple(f'D0{i}' for i in range(1, 10))


def ler(path):
    return json.loads(Path(path).read_text())


def origens_congeladas():
    caminhos = [C.CORPUS, REFERENCIAS/'afirmacoes_referencia.json', REFERENCIAS/'dev/estados_esperados.json',
                ROOT/'data/projetos/alfa/grafo.json', ROOT/'data/projetos/alfa/documentos.json']
    return {str(p.relative_to(ROOT)): lote.sha(p) for p in caminhos}


def preparar(destino):
    destino = Path(destino)
    catalogo = catalogo_entidades()
    documentos = C.carregar_corpus()['documentos']
    total_antes = lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER)
    teto = len(documentos)*RESERVA_NANO
    exigir(total_antes+teto <= TETO_TOTAL_NANO, 'Saldo insuficiente para as reservas')
    destino.mkdir(parents=True, exist_ok=False)
    entradas = []
    for d in documentos:
        caso = dict(id=f"{d['id']}@{d['versao']}", documento=d, catalogo=catalogo,
                    pedido_previsto=montar_pedido(d, catalogo))
        arquivo = destino/'entradas'/f"{d['id']}_{d['versao']}.json"
        gravar(arquivo, caso)
        entradas.append(dict(id=caso['id'], arquivo=str(arquivo.relative_to(destino)), sha256=lote.sha(arquivo),
                             caracteres_pedido=len(SISTEMA)+len(json.dumps(caso['pedido_previsto'], ensure_ascii=False))))
    manifesto = dict(id='extracao-'+uuid.uuid4().hex, preparado_em=lote.agora(), versao=VERSAO,
        modelo=MODELO, configuracao=CONFIG, entradas=entradas, origens=origens_congeladas(), codigo=hashes_codigo(),
        prompt_hash=hash_json(SISTEMA), catalogo_hash=hash_json(catalogo),
        historico_externo_sha256=lote.sha(lote.HISTORICO), comprometido_antes_nano=total_antes,
        teto_rodada_nano=teto, teto_total_nano=TETO_TOTAL_NANO,
        interpretacao='Uma tentativa por documento. A IA recebe só o documento e os catálogos; referências e estados esperados são lidos após todas as respostas.')
    manifesto['hash'] = hash_json(manifesto)
    gravar(destino/'manifesto.json', manifesto)
    return manifesto


def validar_manifesto(pasta):
    m = ler(pasta/'manifesto.json')
    exigir(m['hash'] == hash_json({k: v for k, v in m.items() if k != 'hash'}), 'Manifesto adulterado')
    exigir(m['codigo'] == hashes_codigo() and m['versao'] == VERSAO, 'Implementação mudou desde o preparo')
    exigir(m['modelo'] == MODELO and m['configuracao'] == CONFIG, 'Configuração mudou')
    exigir(m['prompt_hash'] == hash_json(SISTEMA), 'Prompt mudou')
    exigir(m['historico_externo_sha256'] == lote.sha(lote.HISTORICO), 'Histórico financeiro mudou')
    exigir(m['origens'] == origens_congeladas(), 'Dados ou referências mudaram')
    for e in m['entradas']:
        exigir(lote.sha(pasta/e['arquivo']) == e['sha256'], 'Entrada mudou')
    return m


def extrair_caso(pasta, caso, manifesto, chave, *, http=None):
    nome = caso['id'].replace('@', '_')
    destino = pasta/'casos'/f'{nome}.json'
    doc_hash = hash_json(caso['documento'])
    if destino.exists():
        existente = ler(destino)
        exigir(existente['documento_hash'] == doc_hash and existente['manifesto_hash'] == manifesto['hash'],
               'Checkpoint de outra entrada ou versão')
        return existente
    transporte = TransporteReal(pasta/'chamadas'/nome, chave, lote.comprometido(lote.HISTORICO),
        http=http, ledger=lote.LEDGER, rodada=manifesto['id']+':'+nome,
        teto_total_nano=manifesto['teto_total_nano'], teto_rodada_nano=RESERVA_NANO, max_chamadas=1,
        grupo=manifesto['id'], teto_grupo_nano=manifesto['teto_rodada_nano'])
    try:
        exigir(transporte.snapshot()['chamadas_api'] == 0, 'Carteira já possui tentativa para este documento')
        extrator = ExtratorIA(TransporteExtracaoReal(transporte), modelo=MODELO, configuracao=CONFIG,
                              modo='ia_real', catalogo=caso['catalogo'])
        registro = dict(caso_id=caso['id'], manifesto_hash=manifesto['hash'], documento_hash=doc_hash,
                        estado='em_andamento', extracao=None, modo='ia_real' if http is None else 'teste_http_injetado')
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open('x', encoding='utf8') as f:
            json.dump(registro, f, ensure_ascii=False, indent=2)
        sessao = SessaoAuditoriaReal(registro, destino, dict(max_solicitacoes=1, max_tokens_entrada=64000,
            max_tokens_saida=16000, max_segundos=600, max_custo_centavos=1.5))
        registro['extracao'] = extrator.extrair(caso['documento'], sessao=sessao)
        registro['estado'] = 'concluido' if registro['extracao']['estado'] == 'extracao_recebida' else 'falha_extracao'
        sessao.salvar()
        return registro
    finally:
        transporte.db.close()


def _casar(referencia, obtidas):
    """Para cada afirmação de referência, a extraída correspondente (ou None); e as sobras."""
    livres = list(obtidas)
    pares = {}
    for a in referencia:
        cands = [x for x in livres if _chave(x) == _chave(a)]
        par = next((x for x in cands if x['valor'] == a['valor'] and x['conhecimento'] == a['conhecimento']), None) or (cands[0] if cands else None)
        pares[a['id']] = par
        if par is not None:
            livres.remove(par)
    return pares, livres


def comparar(pasta, manifesto):
    ref = {(e['documento_id'], e['versao']): e for e in ler(REFERENCIAS/'afirmacoes_referencia.json')['extracoes']}
    esperado = ler(REFERENCIAS/'dev/estados_esperados.json')['cenarios']
    extracoes, linhas, consumo, erros = {}, [], Counter(), Counter()
    for e in manifesto['entradas']:
        reg = ler(pasta/'casos'/f"{e['id'].replace('@', '_')}.json")
        x = reg.get('extracao') or {}
        doc_id, versao = e['id'].split('@', 1)
        uso = reg.get('sessao_revisao', {}).get('consumo', {})
        for k in ('chamadas_api', 'tokens_entrada', 'tokens_saida', 'custo_api_usd', 'comprometido_api_usd'):
            consumo[k] += uso.get(k, 0)
        erros.update(er['codigo'] for er in x.get('erros', []))
        valido = x.get('estado') == 'extracao_recebida'
        if valido:
            extracoes[(doc_id, versao)] = x['extracao']
        linhas.append(dict(documento=e['id'], estado=x.get('estado', 'interrompida'), erros=x.get('erros', []),
                           metricas=comparar_extracoes(ref[(doc_id, versao)], x['extracao'] if valido else None)))
    # Condição B: estados calculados sobre as afirmações extraídas, casadas à referência.
    pares_b, extras = [], []
    for cid in CENARIOS:
        cen = ler_cenario(cid)
        res = simular(cid)
        for d in C.documentos_do_cenario(cen):
            chave = (d['id'], d['versao'])
            r = ref[chave]
            if chave not in extracoes:
                for a in r['afirmacoes']:
                    pares_b.append((cid, a['id'], esperado[cid][a['id']], dict(estado='extracao_invalida', motivo=None)))
                continue
            ext = extracoes[chave]
            rev = C.revisar_documentos(res, cen, [ext], condicao='extracao_ia')
            por_id = {x['afirmacao']['id']: x for x in rev['documentos'][0]['afirmacoes']}
            casados, sobras = _casar(r['afirmacoes'], ext['afirmacoes'])
            for a in r['afirmacoes']:
                x = casados[a['id']]
                obtido = dict(estado=por_id[x['id']]['estado'], motivo=por_id[x['id']]['motivo']) if x else dict(estado='omitida', motivo=None)
                pares_b.append((cid, a['id'], esperado[cid][a['id']], obtido))
            for s in sobras:
                extras.append(dict(cenario=cid, afirmacao=s, estado=por_id[s['id']]['estado'], motivo=por_id[s['id']]['motivo']))
    vp = sum(e['estado'] == 'revisar' and o['estado'] == 'revisar' for _, _, e, o in pares_b)
    fp = sum(e['estado'] != 'revisar' and o['estado'] == 'revisar' for _, _, e, o in pares_b) + sum(x['estado'] == 'revisar' for x in extras)
    fn = sum(e['estado'] == 'revisar' and o['estado'] != 'revisar' for _, _, e, o in pares_b)
    resumo = dict(versao=VERSAO, manifesto=manifesto['id'],
        natureza='Desenvolvimento: casos D01–D09 expostos e referências redigidas pelo agente; mede a extração por IA e seu efeito na revisão, não generalização.',
        extracao=dict(documentos=linhas, validos=sum(l['estado'] == 'extracao_recebida' for l in linhas), total=len(linhas),
                      verdadeiros_positivos=sum(l['metricas']['verdadeiros_positivos'] for l in linhas),
                      falsos_positivos=sum(l['metricas']['falsos_positivos'] for l in linhas),
                      falsos_negativos=sum(l['metricas']['falsos_negativos'] for l in linhas),
                      valor_correto=sum(l['metricas']['valor_correto'] for l in linhas), erros=dict(erros)),
        condicao_B=dict(afirmacoes=len(pares_b), estado_e_motivo_iguais=sum(e == o for _, _, e, o in pares_b),
                        estado_igual=sum(e['estado'] == o['estado'] for _, _, e, o in pares_b),
                        revisar_vp=vp, revisar_fp=fp, revisar_fn=fn,
                        precisao_revisar=vp/(vp+fp) if vp+fp else None, revocacao_revisar=vp/(vp+fn) if vp+fn else None,
                        divergencias=[dict(cenario=c, afirmacao=a, esperado=e, obtido=o) for c, a, e, o in pares_b if e != o],
                        afirmacoes_extras=extras),
        consumo=dict(consumo),
        comprometido_historico_total_usd=(lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER))/1e9)
    gravar(pasta/'comparacao.json', resumo)
    return resumo


def executar(pasta, *, autorizacao, http=None):
    exigir(isinstance(autorizacao, str) and bool(autorizacao.strip()), 'Autorização obrigatória')
    pasta = Path(pasta)
    with (pasta/'execucao.lock').open('a') as trava:
        fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifesto = validar_manifesto(pasta)
        registro = dict(manifesto_hash=manifesto['hash'], estado='em_andamento', autorizacao=autorizacao,
                        inicio=lote.agora(), casos={}, modo='ia_real' if http is None else 'teste_http_injetado')
        chave = None
        try:
            for e in manifesto['entradas']:
                caso = ler(pasta/e['arquivo'])
                registro['caso_atual'] = caso['id']
                gravar(pasta/'execucao.json', registro)
                if chave is None and not (pasta/'casos'/f"{caso['id'].replace('@', '_')}.json").exists():
                    chave = lote.ler_chave() if http is None else 'chave-ficticia-teste'
                registro['casos'][caso['id']] = extrair_caso(pasta, caso, manifesto, chave, http=http)['estado']
                gravar(pasta/'execucao.json', registro)
            resumo = comparar(pasta, manifesto)
            registro['estado'] = 'concluido' if resumo['extracao']['validos'] == resumo['extracao']['total'] else 'concluido_com_falhas'
        except BaseException as exc:
            mensagem = str(exc).replace(chave, '[REDACTED]') if chave else str(exc)
            registro.update(estado='interrompido', erro=dict(tipo=type(exc).__name__, mensagem=mensagem))
            raise
        finally:
            registro['fim'] = lote.agora()
            gravar(pasta/'execucao.json', registro)
    return registro


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('acao', choices=('preparar', 'executar'))
    p.add_argument('pasta')
    p.add_argument('--autorizacao', default='')
    a = p.parse_args()
    if a.acao == 'preparar':
        m = preparar(a.pasta)
        print(json.dumps(dict(documentos=len(m['entradas']), reserva_maxima_usd=m['teto_rodada_nano']/1e9,
                              comprometido_antes_usd=m['comprometido_antes_nano']/1e9), ensure_ascii=False))
    else:
        r = executar(a.pasta, autorizacao=a.autorizacao)
        print(json.dumps(dict(estado=r['estado'], casos=r['casos']), ensure_ascii=False))


if __name__ == '__main__':
    main()
