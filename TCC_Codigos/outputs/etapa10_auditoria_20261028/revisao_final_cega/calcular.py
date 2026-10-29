#!/usr/bin/env python3
"""Auditoria independente: somente inputs; nenhuma importação do motor ou referências.

Reconstrói durações/valores das fontes literais e transcreve as seis relações
com suas citações. estado_projeto é confrontado depois, nunca usado no cálculo.
As contraprovas B usam exclusivamente fatos comuns e variantes possíveis da
ficha ausente. A enumeração FS0 é condicional, pois FS0 está na ficha ausente.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path('/Users/vaugusto/Desktop/Faculdade/TCC')
INPUT = ROOT / 'TCC_Codigos/data/final/etapa10_v1/inputs'
OUTPUT = Path(__file__).resolve().parent

def read_json(name):
    return json.loads((INPUT / name).read_text())

base = read_json('base.json')
fontes = read_json('fontes.json')['fontes']
cenarios = read_json('cenarios.json')['casos']
estado = read_json('estado_projeto.json')
literal = {}
for path in sorted((INPUT / 'fontes').glob('*.txt')):
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'(L\d+) \[(f_\w+)\] (.*)', line)
        assert match, (path.name, line)
        loc, fid, text = match.groups()
        assert fid not in literal
        literal[fid] = dict(documento_id=path.stem, localizador=loc, trecho=text)

checks = []
def check(label, condition):
    checks.append(dict(verificacao=label, conforme=bool(condition)))
    assert condition, label

for f in fontes:
    check('fonte_literal:' + f['id'], all(f[k] == literal[f['id']][k]
          for k in ('documento_id', 'localizador', 'trecho')))
check('mesmo_conjunto_fontes', set(literal) == {f['id'] for f in fontes})

def text(fid):
    return literal[fid]['trecho']

def cite(fid):
    return dict(fonte_id=fid, documento=literal[fid]['documento_id'] + '.txt',
                localizador=literal[fid]['localizador'])

scope = text('f_30ebc9d46a')
durations = {n: int(v) for n, v in re.findall(r'(n_\w+), (\d+) dias', scope)}
milestone = re.search(r'(n_\w+), marco de duração zero', scope)[1]
durations[milestone] = 0
A, B, C, D, E, M = durations
aliases = dict(zip('ABCDE M'.replace(' ', ''), durations))
edge_sources = [(A,C,'f_f0babac4b4'), (A,D,'f_f0babac4b4'),
                (B,D,'f_f0babac4b4'), (C,E,'f_db8a874f25'),
                (D,E,'f_db8a874f25'), (E,M,'f_db8a874f25')]
edges = [(a,b,0) for a,b,_ in edge_sources]
# Relações transcritas da leitura semântica das duas linhas literais; cada
# entidade da relação deve estar na respectiva linha, além da checagem humana.
for a,b,fid in edge_sources:
    check('entidades_na_fonte_relacao:' + a + ':' + b, a in text(fid) and b in text(fid))
check('semantica_FS0_literal', all('fim-início com defasagem zero' in text(f)
      for f in ('f_f0babac4b4','f_db8a874f25')))
parcels = {p: int(v) for p,v in re.findall(r'(p_\w+) [^;:.]+, (\d+) centavos', text('f_e631c91e32'))}
support = text('f_6e0d1bf111')
fixed = int(re.search(r'fixo de (\d+) centavos', support)[1])
coverage = int(re.search(r'cobre (\d+) dias', support)[1])
rate = int(re.search(r'cobrar (\d+) centavos por dia', support)[1])
reference = text('f_2702245368')
ref_end, ref_cost = map(int, re.search(r'término em D(\d+) e custo de (\d+) centavos', reference).groups())
total_fixed = sum(parcels.values())

def schedule(durations, edges):
    """Ordenação topológica própria e programação no início mais cedo."""
    pending = set(durations)
    out = {}
    while pending:
        ready = sorted(n for n in pending if all(a in out for a,b,_ in edges if b == n))
        if not ready:
            raise ValueError('ciclo')
        for n in ready:
            start = max([0] + [out[a]['fim'] + lag for a,b,lag in edges if b == n])
            out[n] = dict(inicio=start, fim=start + durations[n], duracao=durations[n])
            pending.remove(n)
    return out

def evaluate(ds, relation=edges, credit=0, tax=rate):
    sched = schedule(ds, relation)
    finish = sched[M]['fim']
    extension = max(0, finish - coverage)
    value = total_fixed - credit + extension * tax if tax is not None else None
    return dict(cronograma=sched, fim_dia=finish, delta_prazo_dias=finish-ref_end,
                extensao_dias=extension, custo_centavos=value,
                delta_custo_centavos=value-ref_cost if value is not None else None)

baseline = evaluate(durations)
check('baseline_literal_recalculada', (baseline['fim_dia'], baseline['custo_centavos']) == (ref_end, ref_cost))
check('base_duracoes', {a['id']:a['duracao']['valor'] for a in base['atividades']} == durations)
check('estado_duracoes', {a['id']:a['duracao']['valor'] for a in estado['atividades']} == durations)
check('entidades_base_estado', {n['id'] for n in base['entidades']} == {n['id'] for n in estado['entidades']} == set(durations))
check('nomes_entidades', {n['id']:n['nome'] for n in base['entidades']} == {n['id']:n['nome'] for n in estado['entidades']})
check('base_parcelas', {p['id']:p['valor_centavos'] for p in base['parcelas_base']} == parcels)
check('estado_parcelas', {p['id']:p['valor_centavos'] for p in estado['parcelas_base']} == parcels)
check('estado_relacoes_exatas', {(r['origem_id'],r['destino_id'],r['lag_dias']) for r in estado['relacoes']} == set(edges) and len(estado['relacoes']) == len(edges) and all(r['tipo']=='precede_FS' for r in estado['relacoes']))
for activity in base['atividades']:
    rs = activity['restricoes_contratuais']
    check('liberacao_base:' + activity['id'], len(rs)==1 and rs[0]['tipo']=='nao_antes' and rs[0]['valor_dia']==0)
for activity in estado['atividades']:
    rs = activity['restricoes_liberacao']
    check('liberacao_estado:' + activity['id'], len(rs)==1 and rs[0]['tipo']=='nao_antes' and rs[0]['valor']['valor']==0)
rule, = estado['regras_custo']
check('apoio_estado', rule['taxa_centavos_dia']==rate and rule['base_contratada_dias']==coverage and rule['politica_reducao']=='sem_credito' and rule['intervalo']['fim_ref']['atividade_id']==M and rule['decomposicao_base']['fixo_centavos']['valor']==fixed and rule['decomposicao_base']['incidencia_centavos']['valor']==0)
check('ausencia_regras_extras_estado', not estado['regras_transferencia'] and not estado['regras_locais'])
check('referencias_base_estado', base['linha_base_declarada']['fim_dia']==ref_end and base['linha_base_declarada']['custo_centavos']==ref_cost and estado['linha_base']['fim']['valor']==ref_end and estado['linha_base']['custo_centavos']['valor']==ref_cost)
for f in estado['fontes']:
    check('fonte_estado:' + f['id'], all(f[k]==literal[f['id']][k] for k in ('documento_id','localizador','trecho')))
for node in base['entidades']:
    check('entidade_nome_tipo_fonte:' + node['id'], node['nome'].lower() in scope.lower() and node['tipo']==('marco' if node['id']==M else 'atividade'))
for row in estado['relacoes']:
    fid = next(f for a,b,f in edge_sources if a==row['origem_id'] and b==row['destino_id'])
    check('proveniencia_relacao:' + row['id'], row['fonte_refs']==[{'fonte_id':fid,'localizador':literal[fid]['localizador']}])
check('completude_estado', all(estado['declaracoes_completude'][key]['completa'] is True for key in ('entregas','custos','relacoes')))
check('marco_final_base_estado', base['marco_final_id']==estado['marco_final_id']==M)
check('unidades_calendario', base['calendario']['unidade']==estado['calendario']['unidade']=='dia_corrido' and base['calendario']['indice_inicial']==estado['calendario']['indice_inicial']==0 and base['moeda']==estado['moeda']=='BRL' and base['unidade_monetaria']=='BRL_centavo')

results = []
changed = []
for case in cenarios:
    fid, = case['evidencia_ids']
    notice = text(fid)
    check('relato_literal:' + case['caso_id'], case['relato']==notice and case['documento_evento_vigente']==literal[fid]['documento_id'])
    check('documentos_vigentes:' + case['caso_id'], case['documentos_comuns_vigentes']==base['documentos_comuns'] and case['documentos_relacionais_vigentes']==base['documentos_relacionais'])
    ds = durations.copy()
    credit = 0
    tax = rate
    for n, old, new in re.findall(r'(n_\w+) passa de (\d+) para (\d+) dias', notice):
        check('duracao_anterior_aviso:' + n, ds[n]==int(old))
        ds[n] = int(new)
    for n,new,old in re.findall(r'(n_\w+) dura (\d+) dias em substituição aos (\d+) dias', notice):
        check('duracao_anterior_aviso:' + n, ds[n]==int(old))
        ds[n] = int(new)
    credit_match = re.search(r'crédito definitivo de (\d+) centavos sobre a obrigação existente (p_\w+)', notice)
    if credit_match:
        credit = int(credit_match[1])
        check('credito_parcela_existente', credit_match[2] in parcels and parcels[credit_match[2]]>=credit)
    if 'taxa substituta' in notice:
        tax = None
        check('taxa_indefinida_expressa', 'inteiro não negativo' in notice and 'Não se pode usar a taxa revogada' in notice and 'limite superior' in notice)
    r = evaluate(ds, credit=credit, tax=tax)
    r.update(caso_id=case['caso_id'], aviso=cite(fid), duracoes=ds,
             ajuste_direto_centavos=-credit, taxa_extensao_centavos_dia=tax)
    if tax is None:
        r.update(custo_estado='indeterminado_com_limite_inferior',
                 custo_formula=f'{total_fixed} + {r["extensao_dias"]} * r',
                 dominio_r='inteiro >= 0, sem limite superior',
                 custo_limites_centavos={'inferior_inclusivo':total_fixed,'superior':None},
                 delta_custo_limites_centavos={'inferior_inclusivo':0,'superior':None},
                 custo_direcao='nao_diminuicao; aumento estrito nao demonstrado',
                 contraprova_taxa=[{'r':t,'custo_centavos':total_fixed+r['extensao_dias']*t} for t in (0,1,10000)])
    else:
        r['custo_estado']='exato'
    changed.append(ds)
    results.append(r)

# Enumeração de TODOS os DAGs das 5 atividades; cada sumidouro converge em M.
# Esta prova acrescenta hipoteticamente a B as convenções FS0/mais cedo/D15
# recalculado; não usa as seis arestas verdadeiras nem os papéis dos nomes.
nodes = list(durations)[:-1]
seen = set()
possible = [set(),set(),set()]
witnesses = [{},{},{}]
compatible = 0
for order in itertools.permutations(nodes):
    pairs = list(itertools.combinations(order,2))
    for mask in range(1 << len(pairs)):
        pairs_on = tuple(sorted(pairs[i] for i in range(len(pairs)) if mask >> i & 1))
        if pairs_on in seen:
            continue
        seen.add(pairs_on)
        sinks = [n for n in nodes if not any(a==n for a,b in pairs_on)]
        ee = [(a,b,0) for a,b in pairs_on] + [(n,M,0) for n in sinks]
        if evaluate(durations, ee)['fim_dia'] != ref_end:
            continue
        compatible += 1
        for i,ds in enumerate(changed):
            t = evaluate(ds, ee)['fim_dia']
            possible[i].add(t)
            witnesses[i].setdefault(str(t), ee)

# Duas contraprovas adicionais demonstram por que os limites FS0 não são
# garantidos pelo corpus B: o tipo e o lag das relações só aparecem na ficha.
lag_models = [
    dict(nome='B_pode_preservar_D15_no_aviso_duracoes',
         relacoes=[(C,E,4),(E,M,0),(A,M,0),(B,M,0),(D,M,0)]),
    dict(nome='B_pode_chegar_D22_no_aviso_duracoes',
         relacoes=[(A,B,4),(B,M,0),(C,M,0),(D,M,0),(E,M,0)])]
for model in lag_models:
    model['baseline']=evaluate(durations,model['relacoes'])
    model['aviso_1']=evaluate(changed[0],model['relacoes'])
    check('contraprova_lag_base:' + model['nome'], model['baseline']['fim_dia']==ref_end)

report = dict(
    auditoria='tecnica independente por agente; cega antes de confronto; nao parecer humano',
    corpus_lido='Somente inputs/base.json, fontes.json, cenarios.json, fontes/*.txt e estado_projeto.json como representacao a conferir',
    convencao_calculo='Termino factivel mais cedo; nenhuma ociosidade deliberada. Esta convencao deve constar no protocolo para transformar limites inferiores em previsoes exatas.',
    aliases=aliases, fontes_citadas={f:cite(f) for f in literal},
    topologia=[{'origem':a,'destino':b,'tipo':'FS','lag_dias':0,'citacao':cite(f)} for a,b,f in edge_sources],
    duracoes_fonte=durations, parcelas_fonte_centavos=parcels,
    custo_fixo_soma_centavos=total_fixed, custo_apoio_regra=f'{fixed} fixos ja incluidos + {rate} * max(0, fim-{coverage})',
    baseline=baseline,
    caminhos_baseline=[{'atividades':[A,C,E,M],'duracao':15,'critico':True}, {'atividades':[B,D,E,M],'duracao':15,'critico':True}, {'atividades':[A,D,E,M],'duracao':12,'critico':False}],
    casos_uniao_completa_H_T=results,
    B={'baseline':'D15 e 520400 declarados; custo reconstruivel; topologia nao reconstruivel',
       'caso_1':'Prazo e custo exatos nao identificaveis; contraprovas abaixo. Limites FS0 sao condicionais, pois B nao recebe a afirmacao FS0.',
       'caso_2':{'fim_dia':15,'delta_prazo_dias':0,'custo_centavos':508800,'delta_custo_centavos':-11600,'justificativa':'Aviso preserva todas as variaveis temporais e apoio, credito unico sobre parcela conhecida; usa referencia fixa comum.'},
       'caso_3':{'fim_exato':None,'delta_prazo_exato':None,'custo_exato':None,'delta_custo_exato':None,'custo_minimo_centavos':520400,'delta_custo_minimo_centavos':0,'justificativa':'Taxa nao negativa, fixos preservados, extensao nao negativa. Zero e admissivel, nao e estimativa identificada. Ficha ausente permite com e sem extensao.'},
       'enumeracao_FS0_condicional':{'premissas_adicionais':['DAG','FS0','todos os sumidouros convergem no marco','inicio mais cedo','baseline recalculado D15'],'DAGs_totais':len(seen),'DAGs_compativeis_D15':compatible,'fins_possiveis_por_caso':[sorted(v) for v in possible],'testemunhas_por_fim':witnesses},
       'contraprovas_sem_assumir_FS0':lag_models},
    confronto_estruturado=checks,
    conclusao={'coerencia_fonte_dados':'conforme nos fatos e quantidades auditados',
               'congelamento':'condicionado a explicitar termino mais cedo no protocolo e a nao atribuir a B premissas exclusivas da ficha relacional',
               'lacunas_caso_3':'cenarios.json traz lacunas=[] apesar da taxa expressamente indefinida; ambiguidade de metadado se lista pretende ser exaustiva',
               'assimetria_H_T':'Nao ha diferenca informacional sob uniao completa; resultado matematico deve coincidir',
               'zero_vs_indeterminado':'Caso 2: prazo zero demonstrado. Caso 3: delta custo zero possivel, mas indeterminado com limite inferior zero.'})
OUTPUT.mkdir(parents=True,exist_ok=True)
(OUTPUT/'derivacoes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verificacoes':len(checks),'casos':[{k:r[k] for k in ('caso_id','fim_dia','delta_prazo_dias','custo_centavos','delta_custo_centavos')} for r in results],'B_fins_FS0_condicionais':[sorted(v) for v in possible]},ensure_ascii=False))
