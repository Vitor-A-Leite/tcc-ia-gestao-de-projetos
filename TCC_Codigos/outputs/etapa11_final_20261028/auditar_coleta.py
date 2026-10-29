"""Auditoria offline da coleta. Nunca chama a API nem altera preditores/resultados."""
from pathlib import Path
from collections import Counter
from statistics import mean,median
import hashlib,importlib.util,json,sqlite3,sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'TCC_Codigos/src'))
from interpretacao_no.contratos import hash_json
from hibrido_v07_r3.avaliacao import normalizar
from hibrido_v07_r3.metricas import avaliar
from piloto_real.runner import gravar_novo

def ler(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(c,m):
    if not c:raise ValueError(m)
def modulo(nome,p):
    spec=importlib.util.spec_from_file_location(nome,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def ro(p):return sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)

def main():
    adendo=ler(OUT/'adendo_aprovado.json');manifesto=ler(OUT/'manifesto.json')
    check(manifesto==adendo['manifesto'],'Manifesto divergente')
    ex=modulo('executor_final',ROOT/'TCC_Codigos/experimentos/etapa11/executor.py')
    etapa10=ROOT/'TCC_Codigos/outputs/etapa10_auditoria_20261028'
    frozen=ler(etapa10/'congelamento.json')['artefatos']
    check(sha(etapa10/'congelamento.json')==adendo['congelamento_etapa10_sha256'],'Selo etapa10')
    for p,h in {**frozen,**adendo['runtime']}.items():check(sha(ROOT/p)==h,'Congelamento divergente: '+p)
    views=ler(etapa10/'preparacao_final_v2/views.json')
    slots={s['execucao_id']:s for s in manifesto['execucoes']}
    inventario=ler(OUT/'integridade_antes.json')
    permitidos={'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite','TCC_Codigos/docs/desenvolvimento/STATUS.md','TCC_Codigos/docs/desenvolvimento/PLANO_MESTRE.md'}
    alterados=[p for p,h in inventario.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    check(set(alterados)<=permitidos,'Arquivo histórico alterado: '+str(set(alterados)-permitidos))
    with ro(OUT/'ledger_antes.sqlite')as antes,ro(ex.CARTEIRA/'ledger.sqlite')as db,ro(OUT/'ledger_final.sqlite')as final:
        h=ex.historico(antes)
        check(h==adendo['historico_sha256']==ex.historico(db)==ex.historico(final),'Histórico anterior alterado')
        estados=db.execute('select id,estado,resultado from slots_etapa11 order by rowid').fetchall()
        check([i for i,_,_ in estados]==adendo['slots'],'Ordem divergente')
        check(all(e=='terminado' for _,e,_ in estados),'Coleta incompleta')
        check(not db.execute('select * from parada_etapa11').fetchall(),'Parada de protocolo registrada')
        registros=[json.loads(raw) for _,_,raw in estados]
        for (eid,_,_),r in zip(estados,registros):check(ler(OUT/(eid+'.json'))==r,'Arquivo/ledger divergentes')
        check(estados==final.execute('select id,estado,resultado from slots_etapa11 order by rowid').fetchall(),'Snapshot divergente')
        linhas=[]
        calls=db.execute('select id,slot,estado,request_hash,contado,custo_inferencia,comprometido,uso,registro,contagem_iniciada,inferencia_iniciada from chamadas where id>1114 order by id').fetchall()
        check(calls==final.execute('select id,slot,estado,request_hash,contado,custo_inferencia,comprometido,uso,registro,contagem_iniciada,inferencia_iniciada from chamadas where id>1114 order by id').fetchall(),'Snapshot de chamadas divergente')
        check(0<len(calls)<=30 and [r[0]for r in calls]==list(range(1115,1115+len(calls))),'Tentativas inválidas')
        for cid,slot,estado,reqhash,contado,custo,comprometido,uso,raw,ncount,ninfer in calls:
            r=json.loads(raw);q=r['payload'];resp=r.get('response',{});calc=None
            check(slot in adendo['slots'] and hash_json(q)==reqhash,'Vínculo de chamada')
            check(all(q[k]==r['contagem_payload'][k] for k in ('model','input','reasoning','text')),'Payload contagem/geração')
            user=json.loads(q['input'][1]['content']);s=slots[slot]
            if s['condicao'] in ('B','T'):
                check(user['execucao_id']==slot and user['view']==views[s['caso_id']][s['condicao']],'View global enviada divergente')
            else:
                ctx=user['contexto']
                check(ctx['execucao_id']==slot and ctx['snapshot_original_hash']==s['snapshot_hash'] and ctx['contexto_hash']==hash_json({k:v for k,v in ctx.items()if k!='contexto_hash'}),'Contexto local enviado divergente')
            check(q['model']=='gpt-6-luna' and q['reasoning']=={'effort':'high'} and q['max_output_tokens']==25000 and q['prompt_cache_options']=={'ttl':'30m'} and q['tools']==[] and q['store'] is False and q['service_tier']=='default' and q['stream'] is True and q['truncation']=='disabled' and r['retry']==0,'Protocolo divergente')
            tokens={}
            if estado=='conciliado':
                u=resp['usage'];d=u['input_tokens_details'];cache=d.get('cached_tokens',0);write=d.get('cache_write_tokens',0);simples=u['input_tokens']-cache-write
                check(simples>=0 and not d.get('cache_write_tokens_details',{}).get('ttl_12h_tokens',0),'Composição do cache')
                calc=simples*100+cache*10+write*125+u['output_tokens']*500
                check(json.loads(uso)==u and calc==custo and comprometido==calc+2000000,'Custo divergente')
                check(contado==r['contagem_oficial']<=16000 and u['input_tokens']<=16000 and u['output_tokens']<=25000,'Limite tokens')
                check(ncount==ninfer==1 and resp['status']=='completed' and resp['model']=='gpt-6-luna','Estado observado')
                tokens=dict(input_simples=simples,input_cache=cache,input_escrita30m=write,output_total=u['output_tokens'],reasoning=u.get('output_tokens_details',{}).get('reasoning_tokens'))
            else:check(comprometido==16500000 and custo is None,'Reserva desconhecida liberada')
            linhas.append(dict(call_id=cid,slot=slot,estado=estado,contagem_oficial=contado,calculado_nanoUSD=calc,comprometido_nanoUSD=comprometido,tokens=tokens))
        por=Counter(x['slot']for x in linhas)
        for s in manifesto['execucoes']:check(por[s['execucao_id']]<=(8 if s['condicao']=='H' else 1),'Limite por slot')
        n,total,known=db.execute('select count(*),sum(comprometido),sum(custo_inferencia) from chamadas').fetchone()
        unknown=db.execute("select count(*),sum(comprometido-2000000) from chamadas where estado!='conciliado'").fetchone()
        check(n==1114+len(calls) and total==4480425665+sum(x['comprometido_nanoUSD'] for x in linhas) and total<=5000000000,'Teto/acumulação')
    uso=dict(chamadas=len(linhas),estados=dict(Counter(x['estado']for x in linhas)),inferencia_nanoUSD=sum(x['calculado_nanoUSD'] or 0 for x in linhas),provisao_contagem_nanoUSD=2000000*len(linhas),incremento_nanoUSD=sum(x['comprometido_nanoUSD']for x in linhas),acumulado_nanoUSD=total,saldo_nanoUSD=5000000000-total,tentativas_acumuladas=n,inferencia_acumulada_nanoUSD=known,provisao_contagem_acumulada_nanoUSD=n*2000000,reservas_desconhecidas=dict(n=unknown[0],inferencia_nanoUSD=unknown[1]),linhas=linhas,nota='Recalculado diretamente de usage; provisão de contagem e reservas desconhecidas não comprovam faturamento.')
    norm=normalizar(manifesto,registros)
    check(not norm['anomalias'] and len(norm['linhas'])==9,'Normalização')
    av=modulo('avaliador_final_congelado',etapa10/'avaliar_final.py')
    metricas=av.executar(registros)
    refs=ler(ROOT/'TCC_Codigos/data/final/etapa10_v2/referencias/referencias_avaliacao.json')
    # Recontagem independente: não chama o agregador para obter denominadores ou erros.
    idx={r['caso_id']:r for r in refs};indep={}
    for c in ('B','H','T'):
        ls=[l for l in norm['linhas']if l['slot']['condicao']==c]
        for d in ('prazo','custo'):
            erros=[];corretos=0;eleg=0;falsa=0;classes=Counter()
            for l in ls:
                p=l['desfechos'][d];v=idx[l['slot']['caso_id']]['verdade'][d];vis=idx[l['slot']['caso_id']]['por_view'][c][d]
                classes[p['classe']]+=1;eleg+=v['estado']=='exato'
                if p['classe']=='exato':
                    falsa+=vis['estado'] in ('direcao','indeterminado')
                    if v['estado']=='exato':
                        erro=abs(p['quantidade']['valor']-v['valor']);erros.append(erro);corretos+=erro==0
            x=dict(N=len(ls),cobertura=classes['exato'],pares_exatos=len(erros),MAE=mean(erros)if erros else None,acertos=corretos,referencias_exatas=eleg,falsa_precisao=falsa)
            esperado=metricas['metricas'][c+':'+d]
            check(x['N']==esperado['N'] and x['cobertura']==esperado['cobertura_numerica']['n'] and x['pares_exatos']==esperado['erro_numerico']['n'] and x['MAE']==esperado['erro_numerico']['MAE'] and x['acertos']==esperado['acerto_exato']['n'] and x['referencias_exatas']==esperado['acerto_exato']['elegiveis'] and x['falsa_precisao']==esperado['falsa_certeza']['n'],'Agregação divergente')
            indep[c+':'+d]=x
    operacional={}
    for c in ('B','H','T'):
        rr=[r for r in registros if r['metadados']['condicao']==c];ids={r['metadados']['execucao_id']for r in rr};tt=[r['resultado']['tempo_slot_s']for r in rr];ll=[x for x in linhas if x['slot']in ids]
        operacional[c]=dict(N=len(rr),estados=dict(Counter(r['resultado']['execucao']['estado']for r in rr)),latencia_s=dict(mediana=median(tt),minimo=min(tt),maximo=max(tt),soma=sum(tt)),chamadas=len(ll),inferencia_nanoUSD=sum(x['calculado_nanoUSD']or 0 for x in ll),compromisso_nanoUSD=sum(x['comprometido_nanoUSD']for x in ll))
    for name,obj in [('registros.json',registros),('normalizacao.json',norm),('metricas_referencias.json',metricas),('recontagem_metricas.json',indep),('auditoria_uso.json',uso),('operacional.json',operacional),('integridade_depois.json',dict(arquivos_inventariados=len(inventario),alterados_autorizados=alterados,artefatos_etapa10_conferidos=len(frozen),runtime_conferido=len(adendo['runtime']),historico_sha256=h,chamadas_historicas_preservadas=1114,snapshot_final_conferido=True,coleta_completa=True))]:gravar_novo(OUT/name,obj)
    auditfile=OUT/'auditoria_semantica.json'
    if auditfile.exists():
        audits=ler(auditfile);check(len(audits)==18,'Auditorias faltantes')
        audited=avaliar(manifesto,registros,refs,auditorias=audits)
        check(audited['auditorias_nao_vinculadas']==0,'Auditoria sem vínculo')
        gravar_novo(OUT/'metricas_auditadas.json',dict(audited,dominios_auditados_suplementares=metricas['dominios_auditados_suplementares'],revisao_humana=False,revisao_cega_das_respostas=False))
    print(json.dumps(dict(slots=9,chamadas=len(linhas),comprometido_nanoUSD=total,saldo_nanoUSD=5000000000-total,integridade=True,auditoria_semantica=auditfile.exists()),ensure_ascii=False))

if __name__=='__main__':main()
