"""Continuação após inspeção da sugestão D09, sem solicitar outra sugestão.

Exceção registrada ao filtro automático: o aviso refere-se ao preço ausente,
não à identidade do nó. Não altera a resposta, o evento ou os prompts.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sqlite3

from .retomar_lote_d04 import ler, hashes_originais
from ..src import lote_ia as lote
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.sessoes import Sessoes, gravar
from ..src.vendor.hibrido_v07_r3.adaptador import LocalV07R3
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json
from ..src.auditoria import auditar_arquivo, TransporteRevisaoReal
from ..src.revisao import RevisorIA

AVISO_INSPECIONADO = 'O valor da parcela p_10 está desconhecido, aguardando confirmação em centavos de BRL.'
RELATO_INSPECIONADO = ('SUP_MOTOR: novo valor total da parcela p_10 = desconhecida; aguardando confirmação centavos BRL. '
    'Demais parâmetros contratuais e durações mantidos. Sem alteração técnica da montagem, ação nova, risco futuro ou decisão adicional comunicada.')


def inspecionar(sugestao, cenario):
    """Vincula a decisão deste episódio à resposta e à fonte efetivamente lidas."""
    exigir(cenario['id'] == 'D09' and cenario['entidades_mencionadas'] == ['SUP_MOTOR'], 'Evento diferente')
    exigir([s['no_id'] for s in sugestao['sugestoes']] == ['SUP_MOTOR']
           and sugestao['ambiguidades'] == [AVISO_INSPECIONADO], 'Sugestão diferente da inspecionada')
    exigir(cenario['documento']['trechos'][0]['texto'] == RELATO_INSPECIONADO, 'Fonte diferente da inspecionada')
    return dict(autor='assistente_executor', natureza='inspecao_do_assistente_nao_aprovacao_humana',
        selecao=['SUP_MOTOR'], sugestao_hash=hash_json(sugestao), cenario_hash=hash_json(cenario),
        evidencia=dict(fonte_id='CHANGE.D09', localizador='§1', texto=RELATO_INSPECIONADO),
        justificativa='O nó está identificado na sugestão e na fonte. O aviso apenas registra o preço desconhecido, que permanece desconhecido na análise.',
        desvio_protocolo='Aceitação por inspeção após o filtro automático parar por ambiguidade; não é seleção automática sem ambiguidade.',
        resposta_original_modificada=False, nova_sugestao_solicitada=False)


def executar(manifesto, retomada, destino, autorizacao, *, autorizar=False):
    exigir(autorizar is True and bool(autorizacao.strip()), 'Coleta não autorizada')
    manifesto=Path(manifesto).resolve(); retomada=Path(retomada).resolve(); destino=Path(destino).resolve()
    m=ler(manifesto); lote.validar_manifesto(m); p=m['protocolo']; anterior=ler(retomada/'execucao.json')
    exigir(anterior['lote_id']==m['lote_id'] and anterior['estado']=='interrompido'
           and anterior['fase']=='coleta:D09', 'Interrupção diferente')
    exigir(all(v['coleta']=='concluida' for cid,v in anterior['cenarios'].items() if cid!='D09')
           and all(v['revisao']=='nao_executada' for v in anterior['cenarios'].values()), 'Fases incompatíveis')
    exigir(anterior.get('originais_preservados') is True, 'Originais não preservados')
    c=ler(retomada/'D09/evento.json'); sugestao=ler(retomada/'D09/sugestao.json')
    decisao=inspecionar(sugestao,c)
    s=ler(retomada/'D09/sessao.json')
    exigir(s['estado']=='pronta' and not s['selecao_confirmada'] and not s['cache'] and not s['tentativas']
           and not s['consumo'].get('uso_desconhecido') and s['cenario_snapshot']==c,
           'Checkpoint diferente: não reexecutar análises')
    exigir(s==ler(retomada/'D09/sessoes'/f"{s['id']}.json"), 'Checkpoints divergem')
    with sqlite3.connect(lote.LEDGER.resolve().as_uri()+'?mode=ro',uri=True) as db:
        rows=db.execute('SELECT estado,comprometido FROM chamadas WHERE rodada=?',
                        (m['lote_id']+':retomada-D04:D09-coleta',)).fetchall()
        prefixo=m['lote_id']+':conclusao-D09:'
        exigir(db.execute('SELECT count(*) FROM chamadas WHERE substr(rodada,1,?)=?',
                          (len(prefixo),prefixo)).fetchone()[0]==0, 'Continuação já iniciada')
    exigir(len(rows)==1 and rows[0][0]=='conciliada'
           and rows[0][1]==round(s['consumo']['comprometido_api_usd']*1e9), 'Consumo anterior divergente')
    origens=[manifesto.parent,retomada]
    exigir(all(not destino.is_relative_to(x) for x in origens), 'Destino deve ser separado')
    destino.mkdir(parents=True,exist_ok=False)
    with (manifesto.parent.parent/(m['lote_id']+'-conclusao-D09.json')).open('x') as f:
        json.dump(dict(destino=str(destino),autorizacao=autorizacao),f,ensure_ascii=False)
    adendo=dict(manifesto_hash=m['manifesto_hash'],autorizacao=autorizacao,inicio=lote.agora(),
        decisao_selecao=decisao,executor_sha256=lote.sha(__file__),
        originais={str(x):hashes_originais(x) for x in origens},consumo_d09_anterior=deepcopy(s['consumo']))
    gravar(destino/'adendo.json',adendo)
    fontes={cid:Path(path) for cid,path in anterior['resultados'].items()}
    fontes['D09']=destino/'D09/resultado.json'
    r=dict(lote_id=m['lote_id'],estado='em_andamento',inicio=lote.agora(),fase='coleta:D09',erro=None,
           cenarios=deepcopy(anterior['cenarios']),adendo_hash=hash_json(adendo),
           resultados={k:str(v) for k,v in fontes.items()},transportes={})
    transportes=[];chave=None

    def salvar():
        r['transportes']={etapa:t.snapshot() for etapa,t in transportes}
        r['comprometido_total_nano']=lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER)
        gravar(destino/'execucao.json',r)

    def transporte(etapa,limites,*,descontar=False):
        t=TransporteReal(destino/'chamadas'/etapa,chave,m['financeiro']['historico_externo_nano'],
            ledger=lote.LEDGER,rodada=m['lote_id']+':conclusao-D09:'+etapa,
            teto_total_nano=p['teto_total_nano'],
            teto_rodada_nano=round(limites['max_custo_centavos']*10_000_000)-(rows[0][1] if descontar else 0),
            max_chamadas=limites['max_solicitacoes']-(1 if descontar else 0),
            grupo=m['lote_id'],teto_grupo_nano=p['teto_lote_nano'])
        transportes.append((etapa,t));return t

    try:
        salvar();chave=lote.ler_chave()
        dest=destino/'D09';dest.mkdir();manager=Sessoes(dest/'sessoes')
        s['inspecao_selecao']=decisao;manager.salvar(s)
        gravar(dest/'checkpoint_entrada.json',s)
        gravar(dest/'selecao.json',decisao)
        t=transporte('D09-coleta',p['limites_coleta'],descontar=True)
        r['cenarios']['D09']['coleta']='em_andamento';salvar()
        try:
            s=manager.selecionar(s['id'],decisao['selecao'],'todos',origem='ia_autorizada_pelo_usuario')
            s=manager.executar(s['id'],adaptador_real=LocalV07R3(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180))
        finally:
            s=manager.ler(s['id']);gravar(dest/'sessao.json',s)
            if s.get('resultado') is not None:gravar(dest/'resultado.json',s['resultado'])
            salvar()
        exigir(s['estado']=='concluida' and s['resultado']['execucao']['estado']!='erro'
               and not s.get('falha_real_bloqueante') and not t.snapshot()['uso_desconhecido'],
               'Coleta incompleta; preservar sem repetir')
        r['cenarios']['D09'].update(coleta='concluida',estado_previsao=s['resultado']['execucao']['estado'],
                                   completude=deepcopy(s['resultado']['completude']))
        salvar()
        for cid in lote.CENARIOS:
            r['fase']='revisao:'+cid;r['cenarios'][cid]['revisao']='em_andamento';salvar()
            t=transporte(cid+'-revisao',p['limites_revisao'])
            revisor=RevisorIA(TransporteRevisaoReal(t),modelo=MODELO,configuracao=CONFIG,modo='ia_real')
            a=auditar_arquivo(fontes[cid],destino/cid/'auditoria.json',revisor=revisor,
                              limites=p['limites_revisao'],parar_em_falha=True)
            lote.conferir_auditoria(a);r['cenarios'][cid]['revisao']='concluida';salvar()
        r['fase']='avaliacao';salvar()
        from ..src.avaliacao import resumo
        refs=ler(lote.REFERENCIA)
        for cid in lote.CENARIOS:
            got=resumo(ler(fontes[cid]));comp=dict(equivalente=got==refs[cid],observado=got,referencia=refs[cid],
                natureza='Referência autoral de desenvolvimento; não revisão independente')
            gravar(destino/cid/'comparacao.json',comp)
            r['cenarios'][cid]['equivalente_referencia_autoral']=comp['equivalente']
        exigir(all(hashes_originais(x)==adendo['originais'][str(x)] for x in origens), 'Originais mudaram')
        r.update(estado='concluido',fase='encerrado')
    except BaseException as exc:
        msg=str(exc).replace(chave,'[REDACTED]') if chave else str(exc)
        r.update(estado='interrompido',erro=dict(tipo=type(exc).__name__,mensagem=msg))
        fase=r['fase'].split(':')
        if len(fase)==2 and fase[0] in ('coleta','revisao'):r['cenarios'][fase[1]][fase[0]]='interrompida'
        if isinstance(exc,(KeyboardInterrupt,SystemExit)):raise
    finally:
        r['fim']=lote.agora()
        r['originais_preservados']=all(hashes_originais(x)==adendo['originais'][str(x)] for x in origens)
        salvar()
        for _,t in transportes:t.db.close()
    return r


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifesto');p.add_argument('--retomada',required=True);p.add_argument('--destino',required=True)
    p.add_argument('--autorizacao',required=True);p.add_argument('--autorizar-coleta',action='store_true')
    a=p.parse_args();r=executar(a.manifesto,a.retomada,a.destino,a.autorizacao,autorizar=a.autorizar_coleta)
    print(json.dumps({k:r[k] for k in ('estado','fase','erro','comprometido_total_nano')},ensure_ascii=False))
    if r['estado']!='concluido':raise SystemExit(1)


if __name__=='__main__':main()
