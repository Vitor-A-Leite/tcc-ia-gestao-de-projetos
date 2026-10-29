"""Inspeção pós-coleta: classifica evidências sem alterar previsões ou referências."""
from pathlib import Path
from collections import Counter
import json

O=Path(__file__).parent

def read(p):return json.loads(p.read_text())

def main():
    n=read(O/'normalizacao.json')
    refs={(r['caso_id'],r['versao_projeto']):r for r in read(O/'referencias_avaliacao_autoral.json')}
    old=read(O.parent/'etapa9_piloto_v06_20261027/normalizacao.json')
    mapa={(l['slot']['caso_id'],l['slot']['repeticao'],l['slot']['condicao']):l for l in old['linhas']}
    itens=[];matriz=[]
    for l in n['linhas']:
        s=l['slot'];r=l.get('resultado_original',{});g=refs[(s['caso_id'],s['versao_projeto'])]['verdade'];prev=mapa[(s['caso_id'],s['repeticao'],s['condicao'])]
        if s['condicao']!='H':continue
        erro_local=[];validas=[];tipadas=[]
        for t in r.get('rastro_orquestracao',[]):
            a=t.get('analise',{});c=t.get('contexto',{})
            if not a:continue
            if a.get('execucao',{}).get('estado')!='ok':
                erro_local.append(dict(no_id=t['no_id'],erros=a['execucao'].get('erros',[]),contexto_hash=c.get('contexto_hash')))
            else:
                validas.append(dict(no_id=t['no_id'],contexto_hash=c['contexto_hash'],avaliacao=a['avaliacao'],propostas=a['propostas'],resolucoes_regras=a['resolucoes_regras']))
                tipadas.extend(dict(no_id=t['no_id'],**p) for p in a['pendencias_operacionais'])
        fechamento=r.get('registro_operacional',{}).get('fechamento_final',{})
        rejeitadas=[d for d in r.get('registro_operacional',{}).get('decisoes',[]) if d['operacao_estrutural']!='permitida_condicional']
        for d in ('prazo','custo'):
            q=l['desfechos'][d];exato=q['classe']=='exato';verdade=g[d]
            if erro_local:causa='falha_local'
            elif rejeitadas:causa='decisao_operacional_rejeitada'
            elif r.get('pendencias_execucao'):causa='pendencia_temporal_ou_execucao'
            elif fechamento.get('pendencias_por_dimensao',{}).get(d):causa='fechamento_'+d+'_pendente'
            elif not exato:causa='conhecimento_nao_exato_no_motor'
            else:causa='exato'
            matriz.append(dict(caso=s['caso_id'],repeticao=s['repeticao'],desfecho=d,referencia_estado=verdade['estado'],referencia_valor=verdade['valor'],v06_classe=prev['desfechos'][d]['classe'],v07_classe=q['classe'],v07_valor=q.get('quantidade',{}).get('valor'),causa=causa,falsa_precisao_candidata=exato and verdade['estado']!='exato',divergencia_numerica=exato and verdade['estado']=='exato' and q['quantidade']['valor']!=verdade['valor'],direcao_autoral=verdade['direcao'],direcao_prevista=q.get('quantidade',{}).get('direcao'),direcao_sustentada_nao_recuperada=verdade['estado']=='direcao' and q.get('quantidade',{}).get('direcao')!=verdade['direcao']))
        itens.append(dict(caso_id=s['caso_id'],repeticao=s['repeticao'],execucao_id=s['execucao_id'],resultado_hash=l.get('resultado_hash'),estado=r.get('execucao',{}).get('estado'),previsao=l['desfechos'],referencia=refs[(s['caso_id'],s['versao_projeto'])]['verdade'],erros_locais=erro_local,decisoes_rejeitadas=rejeitadas,pendencias_tipadas=tipadas,fechamento=fechamento,lacunas=r.get('lacunas',[]),analises_validas=validas))
    por={}
    for d in ('prazo','custo'):
        linhas=[m for m in matriz if m['desfecho']==d]
        por[d]=dict(N=len(linhas),referencias_exatas=sum(m['referencia_estado']=='exato'for m in linhas),previsoes_exatas=sum(m['v07_classe']=='exato'for m in linhas),exatos_corretos_elegiveis=sum(m['v07_classe']=='exato'and m['referencia_estado']=='exato'and not m['divergencia_numerica']for m in linhas),referencias_nao_exatas=sum(m['referencia_estado']!='exato'for m in linhas),nao_exatos_preservados=sum(m['referencia_estado']!='exato'and m['v07_classe'] in ('indeterminado','direcao') for m in linhas),falsa_precisao=sum(m['falsa_precisao_candidata']for m in linhas),divergencias_numericas=sum(m['divergencia_numerica']for m in linhas),direcoes_sustentadas_nao_recuperadas=sum(m['direcao_sustentada_nao_recuperada']for m in linhas),causas=dict(Counter(m['causa']for m in linhas)))
    result=dict(natureza='auditoria técnica de desenvolvimento pelo mesmo autor; não independente',resumo_H=por,matriz_H=matriz,casos_H=itens)
    (O/'auditoria_tecnica.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(por,ensure_ascii=False))

if __name__=='__main__':main()
