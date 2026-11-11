"""Revisa somente propostas ainda não tentadas, preservando pareceres inválidos.

Após inspeção da parada D02, erro de contrato com consumo conhecido passa a
ser resultado da revisão, sem nova tentativa. Rede/uso desconhecido ainda para.
O runtime e os pedidos permanecem congelados; esta decisão fica no adendo.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sqlite3

from .retomar_lote_d04 import ler, hashes_originais
from ..src import lote_ia as lote
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.sessoes import gravar
from ..src.auditoria import auditar_arquivo, TransporteRevisaoReal
from ..src.revisao import RevisorIA
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json


class RevisorComRespostasPreservadas(RevisorIA):
    def carregar_anteriores(self, auditoria):
        self.anteriores={r['pacote']['pacote_hash']:r for r in (auditoria or {}).get('registros',[])}
        self.reutilizados=[]

    def revisar(self, pacote, *, sessao=None):
        h=pacote['pacote_hash']
        if h in self.anteriores:
            r=self.anteriores[h]
            exigir(pacote==r['pacote'], 'Pacote mudou; não reutilizar nem repetir')
            self.reutilizados.append(h)
            return deepcopy(r['revisao_semantica'])
        return super().revisar(pacote,sessao=sessao)


def executar(manifesto, anterior, destino, autorizacao, *, autorizar=False):
    exigir(autorizar is True and bool(autorizacao.strip()), 'Continuação não autorizada')
    manifesto=Path(manifesto).resolve();anterior=Path(anterior).resolve();destino=Path(destino).resolve()
    m=ler(manifesto);lote.validar_manifesto(m);p=m['protocolo'];old=ler(anterior/'execucao.json')
    exigir(old['lote_id']==m['lote_id'] and old['estado']=='interrompido' and old['fase']=='revisao:D02'
           and old.get('originais_preservados') is True, 'Parada diferente da inspecionada')
    exigir(all(x['coleta']=='concluida' for x in old['cenarios'].values()), 'Coleta incompleta')
    a2=ler(anterior/'D02/auditoria.json');bad=a2['registros'][0]['revisao_semantica']
    exigir(len(a2['registros'])==1 and bad['estado']=='requer_revisao'
           and bad['erros']==[dict(codigo='ContratoInvalido',mensagem='Entidade/alvo/atributo sustentado divergente')]
           and not a2['sessao_revisao']['consumo']['uso_desconhecido'], 'Falha diferente da inspecionada')
    fontes={cid:Path(path) for cid,path in old['resultados'].items()}
    origens={manifesto.parent,anterior,*[path.parent.parent for path in fontes.values()]}
    exigir(all(not destino.is_relative_to(x) for x in origens),'Destino deve ser separado')
    with sqlite3.connect(lote.LEDGER.resolve().as_uri()+'?mode=ro',uri=True) as db:
        prefixo=m['lote_id']+':revisao-restante:'
        exigir(db.execute('SELECT count(*) FROM chamadas WHERE substr(rodada,1,?)=?',
                          (len(prefixo),prefixo)).fetchone()[0]==0, 'Revisão restante já iniciada')
    destino.mkdir(parents=True,exist_ok=False)
    with (manifesto.parent.parent/(m['lote_id']+'-revisao-restante.json')).open('x') as f:
        json.dump(dict(destino=str(destino),autorizacao=autorizacao),f,ensure_ascii=False)
    adendo=dict(manifesto_hash=m['manifesto_hash'],autorizacao=autorizacao,inicio=lote.agora(),
        executor_sha256=lote.sha(__file__),originais={str(x):hashes_originais(x) for x in sorted(origens)},
        decisao=dict(autor='assistente_executor',natureza='inspecao_nao_aprovacao_humana',
            motivo='D02 devolveu descrições onde o parser exige IDs exatos. Preservar a falha como resultado; revisar apenas propostas ainda não tentadas.',
            resposta_inspecionada_hash=hash_json(bad),
            desvio_protocolo='Depois da inspeção, resposta inválida com uso conhecido não impede revisar propostas distintas. Não há retry, correção de resposta ou relaxamento do parser.',
            parada_preservada='Transporte interrompido, consumo desconhecido, orçamento ou pacote inválido'))
    gravar(destino/'adendo.json',adendo)
    r=dict(lote_id=m['lote_id'],estado='em_andamento',inicio=lote.agora(),fase='revisao:D01',erro=None,
        adendo_hash=hash_json(adendo),cenarios=deepcopy(old['cenarios']),resultados=old['resultados'],
        auditorias={},transportes={},pareceres_invalidos=[])
    transportes=[];chave=None

    def salvar():
        r['transportes']={cid:t.snapshot() for cid,t in transportes}
        r['comprometido_total_nano']=lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER)
        gravar(destino/'execucao.json',r)

    try:
        salvar();chave=lote.ler_chave()
        for cid in lote.CENARIOS:
            anterior_a=ler(anterior/cid/'auditoria.json') if (anterior/cid/'auditoria.json').exists() else None
            consumo=(anterior_a or {}).get('sessao_revisao',{}).get('consumo',{})
            exigir(not consumo.get('uso_desconhecido'),'Uso anterior desconhecido')
            limites=deepcopy(p['limites_revisao'])
            for campo,origem in (('max_solicitacoes','solicitacoes_reais'),('max_tokens_entrada','tokens_entrada'),
                                 ('max_tokens_saida','tokens_saida'),('max_segundos','segundos')):
                limites[campo]-=consumo.get(origem,0)
            limites['max_custo_centavos']-=100*consumo.get('comprometido_api_usd',0)
            exigir(all(v>0 for v in limites.values()),'Limite restante esgotado')
            t=TransporteReal(destino/'chamadas'/cid,chave,m['financeiro']['historico_externo_nano'],
                ledger=lote.LEDGER,rodada=m['lote_id']+':revisao-restante:'+cid,
                teto_total_nano=p['teto_total_nano'],teto_rodada_nano=round(limites['max_custo_centavos']*10_000_000),
                max_chamadas=limites['max_solicitacoes'],grupo=m['lote_id'],teto_grupo_nano=p['teto_lote_nano'])
            transportes.append((cid,t))
            revisor=RevisorComRespostasPreservadas(TransporteRevisaoReal(t),modelo=MODELO,configuracao=CONFIG,modo='ia_real')
            revisor.carregar_anteriores(anterior_a)
            r['fase']='revisao:'+cid;r['cenarios'][cid]['revisao']='em_andamento';salvar()
            path=destino/cid/'auditoria.json'
            a=auditar_arquivo(fontes[cid],path,revisor=revisor,limites=limites,parar_em_falha=False)
            exigir(not t.parado and not t.snapshot()['uso_desconhecido'], 'Transporte interrompido; parar sem retry')
            ruins=[]
            for item in a['registros']:
                exigir(item.get('pacote') is not None, 'Pacote inválido')
                v=item['revisao_semantica']
                if v['estado']!='parecer_recebido':
                    exigir(not v.get('uso_desconhecido') and v.get('erros')
                           and all(e['codigo']=='ContratoInvalido' for e in v['erros']), 'Falha diferente de contrato; inspecionar')
                    ruins.append(dict(cenario_id=cid,no_id=item['no_id'],pacote_hash=item['pacote']['pacote_hash'],erros=v['erros']))
            r['pareceres_invalidos'].extend(ruins)
            r['cenarios'][cid]['revisao']='concluida_com_parecer_invalido' if ruins else 'concluida'
            r['auditorias'][cid]=dict(arquivo=str(path),total=len(a['registros']),invalidos=len(ruins),
                                      reutilizados=revisor.reutilizados,origem_reuso=str(anterior/cid/'auditoria.json') if anterior_a else None)
            salvar()
        r['fase']='avaliacao';salvar()
        from ..src.avaliacao import resumo
        refs=ler(lote.REFERENCIA)
        for cid in lote.CENARIOS:
            got=resumo(ler(fontes[cid]));comp=dict(equivalente=got==refs[cid],observado=got,referencia=refs[cid],
                natureza='Referência autoral de desenvolvimento; não revisão independente')
            gravar(destino/cid/'comparacao.json',comp)
            r['cenarios'][cid]['equivalente_referencia_autoral']=comp['equivalente']
        exigir(all(hashes_originais(x)==adendo['originais'][str(x)] for x in origens),'Originais mudaram')
        r.update(estado='concluido_com_pareceres_invalidos' if r['pareceres_invalidos'] else 'concluido',fase='encerrado')
    except BaseException as exc:
        msg=str(exc).replace(chave,'[REDACTED]') if chave else str(exc)
        r.update(estado='interrompido',erro=dict(tipo=type(exc).__name__,mensagem=msg))
        fase=r['fase'].split(':')
        if len(fase)==2 and fase[0]=='revisao':r['cenarios'][fase[1]]['revisao']='interrompida'
        if isinstance(exc,(KeyboardInterrupt,SystemExit)):raise
    finally:
        r['fim']=lote.agora();r['originais_preservados']=all(hashes_originais(x)==adendo['originais'][str(x)] for x in origens)
        salvar()
        for _,t in transportes:t.db.close()
    return r


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifesto');p.add_argument('--anterior',required=True);p.add_argument('--destino',required=True)
    p.add_argument('--autorizacao',required=True);p.add_argument('--autorizar-coleta',action='store_true')
    a=p.parse_args();r=executar(a.manifesto,a.anterior,a.destino,a.autorizacao,autorizar=a.autorizar_coleta)
    print(json.dumps({k:r[k] for k in ('estado','fase','erro','comprometido_total_nano')},ensure_ascii=False))
    if r['estado']=='interrompido':raise SystemExit(1)


if __name__=='__main__':main()
