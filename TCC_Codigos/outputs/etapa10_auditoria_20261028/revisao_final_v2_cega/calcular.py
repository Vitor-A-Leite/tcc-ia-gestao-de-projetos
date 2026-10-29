#!/usr/bin/env python3
"""Revisão cega do delta v1->v2. Biblioteca padrão, fontes literais e DAG próprio.
Não importa motor nem lê referências, previsões, outros agentes ou parecer v1.
Reutiliza o raciocínio independente da revisão v1, reimplementado aqui.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT=Path('/Users/vaugusto/Desktop/Faculdade/TCC/TCC_Codigos')
OLD=ROOT/'data/final/etapa10_v1/inputs'
NEW=ROOT/'data/final/etapa10_v2/inputs'
OUT=Path(__file__).resolve().parent

def load(path): return json.loads(path.read_text())
def differences(a,b,path=''):
    if type(a)!=type(b): return [{'path':path,'v1':a,'v2':b}]
    if isinstance(a,dict):
        result=[]
        for k in sorted(a.keys() | b.keys()):
            if k not in a or k not in b: result.append({'path':path+'/'+k,'v1':a.get(k),'v2':b.get(k)})
            else: result.extend(differences(a[k],b[k],path+'/'+k))
        return result
    if isinstance(a,list):
        if len(a)!=len(b): return [{'path':path,'v1':a,'v2':b}]
        return [v for i,(x,y) in enumerate(zip(a,b)) for v in differences(x,y,path+'/'+str(i))]
    return [] if a==b else [{'path':path,'v1':a,'v2':b}]

checks=[]
def check(name,condition):
    checks.append({'verificacao':name,'conforme':bool(condition)})
    assert condition,name

old_names={p.relative_to(OLD) for p in OLD.rglob('*') if p.is_file()}
new_names={p.relative_to(NEW) for p in NEW.rglob('*') if p.is_file()}
check('mesmos_arquivos_v1_v2',old_names==new_names)
delta={}
for name in sorted(new_names):
    a,b=(OLD/name).read_text(),(NEW/name).read_text()
    if a!=b:
        delta[str(name)]=differences(json.loads(a),json.loads(b)) if name.suffix=='.json' else {'v1':a,'v2':b}
check('apenas_cinco_arquivos_alterados',set(delta)=={'base.json','cenarios.json','estado_projeto.json','fontes.json','fontes/d_00804cfe59.txt'})
expected_paths={
 'base.json':{'/status','/versao_projeto'},
 'cenarios.json':{'/casos/0/versao_projeto','/casos/1/versao_projeto','/casos/2/versao_projeto','/casos/2/lacunas'},
 'estado_projeto.json':{'/versao','/fontes/0/trecho','/fontes/1/trecho'},
 'fontes.json':{'/fontes/0/trecho','/fontes/1/trecho'}}
for name,paths in expected_paths.items(): check('delta_campos:'+name,{d['path'] for d in delta[name]}==paths)

base=load(NEW/'base.json'); state=load(NEW/'estado_projeto.json')
sources=load(NEW/'fontes.json')['fontes']; scenarios=load(NEW/'cenarios.json')['casos']
literal={}
for p in sorted((NEW/'fontes').glob('*.txt')):
    for line in p.read_text().splitlines():
        if not line.strip(): continue
        m=re.fullmatch(r'(L\d+) \[(f_\w+)\] (.*)',line)
        assert m
        loc,fid,txt=m.groups()
        check('fonte_unica:'+fid,fid not in literal)
        literal[fid]={'documento_id':p.stem,'localizador':loc,'trecho':txt}
def txt(fid): return literal[fid]['trecho']
def cite(fid): return {'fonte_id':fid,**{k:literal[fid][k] for k in ('documento_id','localizador')}}
for source in sources+state['fontes']:
    check('transcricao:'+source['id'], all(source[k]==literal[source['id']][k] for k in ('documento_id','localizador','trecho')))
check('conjunto_fontes_literal',set(literal)=={f['id'] for f in sources})

old_sources={f['id']:f for f in load(OLD/'fontes.json')['fontes']}
common=txt('f_2702245368')
old_common=old_sources['f_2702245368']['trecho']
check('comum_apenas_acrescimo',common.startswith(old_common))
check('identidade_apenas_versao',txt('f_30ebc9d46a')==old_sources['f_30ebc9d46a']['trecho'].replace('v1.0-etapa10-final','v2.0-etapa10-final'))
for phrase in ('grafo temporal é acíclico','fim-início com defasagem zero','convergem direta ou indiretamente no marco final','começa no instante factível mais cedo','não se acrescenta ociosidade deliberada','menor término factível'):
    check('convencao_comum:'+phrase,phrase in common)
check('fonte_convencoes_visivel_B',literal['f_2702245368']['documento_id'] in base['documentos_comuns'] and all(literal['f_2702245368']['documento_id'] in c['documentos_comuns_vigentes'] for c in scenarios))

dur={n:int(v) for n,v in re.findall(r'(n_\w+), (\d+) dias',txt('f_30ebc9d46a'))}
M=re.search(r'(n_\w+), marco de duração zero',txt('f_30ebc9d46a'))[1]
dur[M]=0
A,B,C,D,E,M=dur
aliases=dict(zip('ABCDEM',dur))
# Transcrição independente das seis relações, lidas em L01/L02 da ficha.
source_edges=[(A,C,'f_f0babac4b4'),(A,D,'f_f0babac4b4'),(B,D,'f_f0babac4b4'),(C,E,'f_db8a874f25'),(D,E,'f_db8a874f25'),(E,M,'f_db8a874f25')]
edges=[(a,b) for a,b,_ in source_edges]
parcels={p:int(v) for p,v in re.findall(r'(p_\w+) [^;:.]+, (\d+) centavos',txt('f_e631c91e32'))}
fixed=sum(parcels.values())
end_ref,cost_ref=map(int,re.search(r'término em D(\d+) e custo de (\d+) centavos',common).groups())
support=txt('f_6e0d1bf111')
coverage=int(re.search(r'cobre (\d+) dias',support)[1]); rate=int(re.search(r'cobrar (\d+) centavos por dia',support)[1])

def schedule(ds,ee):
    pending=set(ds); result={}
    while pending:
        ready=sorted(n for n in pending if all(a in result for a,b in ee if b==n))
        if not ready: raise ValueError('ciclo')
        for n in ready:
            start=max([0]+[result[a]['fim'] for a,b in ee if b==n])
            result[n]={'inicio':start,'fim':start+ds[n],'duracao':ds[n]}; pending.remove(n)
    return result
def result(ds,ee,credit=0,tax=rate):
    sched=schedule(ds,ee); end=sched[M]['fim']; extension=max(0,end-coverage)
    cost=fixed-credit+extension*tax if tax is not None else None
    return {'cronograma':sched,'fim_dia':end,'delta_prazo_dias':end-end_ref,'extensao_dias':extension,'custo_centavos':cost,'delta_custo_centavos':cost-cost_ref if cost is not None else None}

baseline=result(dur,edges)
check('baseline_recalculado',baseline['fim_dia']==end_ref and baseline['custo_centavos']==cost_ref)
for label,obj in [('base',base),('estado',state)]:
    check(label+':duracoes',{a['id']:a['duracao']['valor'] for a in obj['atividades']}==dur)
    check(label+':parcelas',{p['id']:p['valor_centavos'] for p in obj['parcelas_base']}==parcels)
    check(label+':marco',obj['marco_final_id']==M)
check('estado_topologia',len(state['relacoes'])==len(edges) and {(r['origem_id'],r['destino_id']) for r in state['relacoes']}==set(edges) and all(r['tipo']=='precede_FS' and r['lag_dias']==0 for r in state['relacoes']))
check('versoes_projeto',base['versao_projeto']==state['versao']=='v2.0-etapa10-final' and all(c['versao_projeto']==base['versao_projeto'] for c in scenarios))
check('lacuna_taxa_anotada',len(scenarios[2]['lacunas'])==1 and 'não definida' in scenarios[2]['lacunas'][0] and 'taxa revogada' in scenarios[2]['lacunas'][0])
check('outros_campos_sem_mudancas',all({x['path'] for x in delta[k]}==paths for k,paths in expected_paths.items()))

cases=[]; ds_cases=[]; credits=[]
for case in scenarios:
    fid,=case['evidencia_ids']; notice=txt(fid); ds=dur.copy(); credit=0; tax=rate
    check('aviso_literal:'+case['caso_id'],case['relato']==notice)
    for n,old,new in re.findall(r'(n_\w+) passa de (\d+) para (\d+) dias',notice):
        check('duracao_anterior:'+n,ds[n]==int(old)); ds[n]=int(new)
    for n,new,old in re.findall(r'(n_\w+) dura (\d+) dias em substituição aos (\d+) dias',notice):
        check('duracao_anterior:'+n,ds[n]==int(old)); ds[n]=int(new)
    match=re.search(r'crédito definitivo de (\d+) centavos sobre a obrigação existente (p_\w+)',notice)
    if match: credit=int(match[1]); check('credito_parcela_existente',match[2] in parcels)
    if 'taxa substituta' in notice:
        tax=None
        check('taxa_sem_valor_nao_negativa','inteiro não negativo' in notice and 'não foi definida' in notice and 'Não se pode usar a taxa revogada' in notice)
    r=result(ds,edges,credit,tax); r.update(caso_id=case['caso_id'],citacao_aviso=cite(fid),taxa=tax,ajuste_direto_centavos=-credit)
    if tax is None:
        r.update(custo_estado='indeterminado_com_limite_inferior',custo_formula=f'{fixed}+{r["extensao_dias"]}*r',dominio_r='inteiros nao negativos, sem teto',custo_minimo_centavos=fixed,delta_custo_minimo_centavos=0,custo_maximo_centavos=None,contraprovas_taxa=[{'r':t,'custo':fixed+r['extensao_dias']*t} for t in (0,1,10000)])
    else: r['custo_estado']='exato'
    ds_cases.append(ds); credits.append(credit); cases.append(r)

# Todas as possíveis arestas entre cinco atividades são consideradas, sem ler
# as arestas verdadeiras para restringir a enumeração B. Um DAG admite ao
# menos uma permutação topológica; duplicatas são removidas por conjunto.
# Ligar todo sumidouro ao marco garante convergência. Arestas adicionais ao
# marco são temporalmente redundantes e não mudam o espaço de resultados.
nodes=list(dur)[:-1]; seen=set(); compatible=0
ends=[set() for _ in cases]; witnesses=[{} for _ in cases]
for order in itertools.permutations(nodes):
    pairs=list(itertools.combinations(order,2))
    for mask in range(1<<len(pairs)):
        selected=tuple(sorted(pairs[i] for i in range(len(pairs)) if mask>>i&1))
        if selected in seen: continue
        seen.add(selected)
        ee=list(selected)+[(n,M) for n in nodes if not any(a==n for a,b in selected)]
        if schedule(dur,ee)[M]['fim']!=end_ref: continue
        compatible+=1
        for i,ds in enumerate(ds_cases):
            end=schedule(ds,ee)[M]['fim']; ends[i].add(end)
            witnesses[i].setdefault(str(end),ee)

b_results=[]
for i,case in enumerate(cases):
    possible_ends=sorted(ends[i]); deltas=[v-end_ref for v in possible_ends]
    br={'caso_id':case['caso_id'],'fins_dia_possiveis':possible_ends,'delta_prazo_dias_possiveis':deltas,'prazo_exato':len(possible_ends)==1,'limite_prazo_dia':[min(possible_ends),max(possible_ends)],'testemunhas_topologias':witnesses[i]}
    if case['taxa'] is not None:
        costs=sorted({fixed-credits[i]+max(0,v-coverage)*rate for v in possible_ends})
        br.update(custos_centavos_possiveis=costs,delta_custo_centavos_possiveis=[v-cost_ref for v in costs],custo_exato=len(costs)==1,custo_limites_centavos=[min(costs),max(costs)])
    else:
        br.update(custo_exato=False,custo_minimo_centavos=fixed,custo_maximo_centavos=None,delta_custo_minimo_centavos=0,dominio_custo='todos os inteiros >= custo minimo; ha testemunha com extensao 1 e taxa inteiro >=0',zero_delta_custo='possivel, nao identificado',zero_delta_prazo='possivel, nao identificado')
    b_results.append(br)

report={'tipo':'revisao tecnica por agente do delta v1->v2; independente de gabaritos/previsoes; nao parecer humano',
 'corpus_lido':'somente inputs v1/v2; sem motor, rede, credenciais ou outros agentes; algoritmo independente proprio',
 'delta_arquivos':delta,'verificacoes':checks,'aliases':aliases,'fontes_citadas':{f:cite(f) for f in literal},
 'convencoes_comuns':{'citacao':cite('f_2702245368'),'novas_premissas_literais':common[len(old_common):]},
 'topologia_H_T':[{'origem':a,'destino':b,'lag':0,'fonte':cite(f)} for a,b,f in source_edges],
 'parcelas_centavos':parcels,'baseline':baseline,'casos_H_T':cases,
 'enumeracao_B':{'DAGs_rotulados_cinco_atividades':len(seen),'DAGs_compativeis_com_baseline_D15':compatible,'premissas':'Agora todas comuns: DAG, FS0, convergencia, inicio mais cedo; baseline D15 estipulado','nenhuma_aresta_real_usada_para_restringir_B':True,'resultados':b_results},
 'parecer':{'delta_material':'somente convencoes declaradas, identificacao de versao/status e anotacao de lacuna; valores/avisos/arestas inalterados',
 'ambiguidades_v1':'resolvidas pelo delta v2',
 'congelamento':'apto quanto a coerencia e inferibilidade aqui auditadas, sem avaliar motor ou previsoes',
 'B_caso_1':'indeterminado em valor unico, mas atraso e aumento de custo estritos demonstraveis; limites finitos calculados',
 'B_caso_2':'plenamente inferivel; zero temporal demonstrado',
 'B_caso_3':'prazo limitado mas nao unico; custo inferior conhecido e sem teto; zero apenas possivel',
 'H_T_caso_3':'prazo exato; custo indeterminado discreto 520400+6r, r inteiro>=0'}}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'derivacoes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verificacoes':len(checks),'baseline':{k:baseline[k] for k in ('fim_dia','custo_centavos')},'H_T':[{k:c[k] for k in ('caso_id','fim_dia','delta_prazo_dias','custo_centavos','delta_custo_centavos')} for c in cases],'B_fins':[sorted(x) for x in ends],'DAGs':len(seen),'DAGs_D15':compatible},ensure_ascii=False))
