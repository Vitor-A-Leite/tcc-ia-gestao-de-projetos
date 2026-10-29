"""Somente pós-coleta: estatísticas descritivas e comparação sem reparar outputs."""
from pathlib import Path
import sqlite3,json
from collections import Counter
from statistics import mean,median
O=Path(__file__).parent;W=O.parent/'etapa9_piloto_real_aprovado_20261026';db=sqlite3.connect('file:'+str(W/'ledger.sqlite')+'?mode=ro',uri=True)
regs=[json.loads(r)for r, in db.execute('SELECT resultado FROM slots_v07_r2 WHERE resultado IS NOT NULL')]
calls=[dict(id=i,slot=s,estado=e,comprometido=t,custo=ci,registro=json.loads(r)if r else{})for i,s,e,t,ci,r in db.execute('SELECT id,slot,estado,comprometido,custo_inferencia,registro FROM chamadas WHERE id>790')]
normal=json.loads((O/'normalizacao.json').read_text());metrics=json.loads((O/'avaliacao_autoral.json').read_text())['metricas']
old=json.loads((O.parent/'etapa9_piloto_v06_20261027/avaliacao_autoral.json').read_text())['metricas']
por={};latcalls={};locals_=Counter();closure=Counter();notas=0;pendencias=[]
for reg in regs:
    r=reg['resultado'];cond=reg['metadados']['condicao']
    tent=r.get('consumo',{}).get('tentativas',[])if cond!='H'else[t for p in r.get('rastro_orquestracao',[])for t in p.get('analise',{}).get('execucao',{}).get('tentativas',[])]
    for t in tent:
        cid=t.get('metadados',{}).get('call_id')
        if cid and isinstance(t.get('latencia_ms'),(int,float)):latcalls[cid]=dict(condicao=cond,segundos=t['latencia_ms']/1000)
    if cond=='H':
        closure[r.get('registro_operacional',{}).get('fechamento_final',{}).get('estado','ausente')]+=1
        notas+=len(r.get('notas_diagnosticas_locais',[]))
        for p in r.get('rastro_orquestracao',[]):
            a=p.get('analise',{})
            if a:
                locals_['total']+=1;locals_[a.get('execucao',{}).get('estado','ausente')]+=1
                for e in a.get('execucao',{}).get('erros',[]):locals_['erro:'+e['mensagem']]+=1
                for pendencia in a.get('pendencias_operacionais',[]):
                    texto=pendencia['motivo'];baixo=texto.lower();tipo='alegacao_limite_permissao_ou_catalogo'if any(x in baixo for x in ('permiss','catálogo','catalogo'))else 'alegacao_fato_ausente_ou_outra_pendencia_a_auditar'
                    pendencias.append(dict(execucao_id=reg['metadados']['execucao_id'],no_id=p['no_id'],texto=texto,dimensao_declarada=pendencia['dimensao'],classe_lexical_nao_semantica=tipo,contexto_hash=p.get('contexto',{}).get('contexto_hash'),permissoes=p.get('contexto',{}).get('permissoes'))) 
for c in 'BHT':
    rr=[r['resultado']for r in regs if r['metadados']['condicao']==c];ids={r['metadados']['execucao_id']for r in regs if r['metadados']['condicao']==c}
    cc=[r for r in calls if r['slot']in ids];times=[r['tempo_slot_s']for r in rr if isinstance(r.get('tempo_slot_s'),(int,float))]
    lat=[r['segundos']for r in latcalls.values()if r['condicao']==c]
    def stat(v):return dict(n=len(v),media=mean(v)if v else None,mediana=median(v)if v else None,min=min(v)if v else None,max=max(v)if v else None)
    por[c]=dict(planejado=30,registros=len(rr),estados=dict(Counter(r['execucao']['estado']for r in rr)),chamadas=len(cc),inferencias_enviadas=sum(r['registro'].get('response')is not None for r in cc),inferencia_conhecida_nanoUSD=sum(r['custo']or 0 for r in cc),comprometido_nanoUSD=sum(r['comprometido']for r in cc),latencia_slot_s=stat(times),latencia_chamada_s=stat(lat),metricas={d:metrics[c+':'+d]for d in ('prazo','custo')},comparacao_v06={d:dict(cobertura_v06=old[c+':'+d]['cobertura_numerica'],cobertura_v07=metrics[c+':'+d]['cobertura_numerica'],erro_v06=old[c+':'+d]['erro_numerico'],erro_v07=metrics[c+':'+d]['erro_numerico'])for d in ('prazo','custo')})
# Exact predictions against nonexact authored truth or contradictory exact/lower bounds warrant review.
refs={(r['caso_id'],r['versao_projeto']):r for r in json.loads((O/'referencias_avaliacao_autoral.json').read_text())};suspeitas=[]
for l in normal['linhas']:
    s=l['slot'];truth=refs[(s['caso_id'],s['versao_projeto'])]['verdade']
    for d,q in l['desfechos'].items():
        if q['classe']=='exato'and(truth[d]['estado']!='exato'or q['quantidade']['valor']!=truth[d]['valor']):suspeitas.append(dict(execucao_id=s['execucao_id'],condicao=s['condicao'],caso_id=s['caso_id'],repeticao=s['repeticao'],desfecho=d,predicao=q['quantidade'],referencia=truth[d],rotulo='divergencia_numerica_ou_falsa_precisao_a_revisar_semanticamente'))
n,t,ci=db.execute('SELECT count(*),sum(comprometido),sum(custo_inferencia)FROM chamadas').fetchone();unknown=db.execute("SELECT count(*)FROM chamadas WHERE estado!='conciliado'").fetchone()[0]
r=dict(por_condicao=por,analises_H=dict(locals_),fechamentos_H=dict(closure),notas_diagnosticas_H=notas,suspeitas=suspeitas,pendencias_H=pendencias,classes_lexicais_pendencias=dict(Counter(p['classe_lexical_nao_semantica']for p in pendencias)),latencias_por_call_id=latcalls,carteira=dict(tentativas=n,comprometido_nanoUSD=t,inferencia_conhecida_nanoUSD=ci,provisao_contagem_nanoUSD=n*2000000,reserva_inferencia_desconhecida_nanoUSD=t-ci-n*2000000,saldo_nanoUSD=5000000000-t,custos_desconhecidos=unknown),paradas_originais=db.execute('SELECT motivo FROM parada_v07_r2').fetchall(),paradas_retomada=[])
(O/'resumo_descritivo.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');db.close();print(json.dumps({k:v for k,v in r.items()if k in ('carteira','analises_H','fechamentos_H')},ensure_ascii=False))
