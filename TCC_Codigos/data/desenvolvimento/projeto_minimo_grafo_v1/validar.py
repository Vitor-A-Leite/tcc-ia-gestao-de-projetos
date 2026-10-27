"""Conferência estrutural específica do snapshot Íris; não calcula agenda/impactos."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def require(ok, code):
    if not ok:
        raise ValueError(code)

def unique(items):
    ids = [x['id'] for x in items]
    require(len(ids) == len(set(ids)), 'ID_DUPLICADO')
    return {x['id']: x for x in items}

def dag(edges):
    nodes = {n for a, b in edges for n in (a, b)}
    active, done = set(), set()
    def visit(n):
        require(n not in active, 'CICLO')
        if n in done:
            return
        active.add(n)
        for a, b in edges:
            if a == n:
                visit(b)
        active.remove(n)
        done.add(n)
    for n in nodes:
        visit(n)

def validate(s, projection):
    entities = unique(s['entidades'])
    activities = unique(s['atividades'])
    sources = unique(s['fontes'])
    relations = unique(s['relacoes'])
    transfers = unique(s['regras_transferencia'])
    parcels = unique(s['parcelas_base'])
    unique(s['regras_locais']); unique(s['regras_custo'])
    require(set(entities) == {'n_73fa','n_c820','n_42be','n_915c','n_a367','n_08df','n_e659'}, 'ENTIDADES')
    require(s['moeda'] == 'BRL' and s['calendario']['unidade'] == 'dia_corrido' and s['calendario']['indice_inicial'] == 0, 'UNIDADE_GLOBAL')
    allowed = {'d_71ba','d_482e','d_59c1','d_8c23','d_aa83'}
    require({f['documento_id'] for f in sources.values()} == allowed, 'SELECAO_FONTES')
    for f in sources.values():
        lines = (ROOT/'fontes'/f"{f['documento_id']}.txt").read_text().splitlines()
        require(f"[{f['localizador']}] {f['trecho']}" in lines, 'TRECHO_LITERAL')
    def evidence(ref):
        require(ref['fonte_id'] in sources, 'FONTE_INVALIDA')
        require(ref['localizador'] == sources[ref['fonte_id']]['localizador'], 'LOCALIZADOR')
    def walk(x):
        if isinstance(x, list):
            for v in x: walk(v)
        elif isinstance(x, dict):
            require(not any(a.startswith('expected_') for a in x), 'GABARITO')
            for field in ('fonte_refs','evidencias'):
                if field in x:
                    require(bool(x[field]), 'EVIDENCIA_VAZIA')
                    for ref in x[field]: evidence(ref)
            if 'clausula' in x: evidence(x['clausula'])
            if 'estado' in x:
                state, value = x['estado'], x['valor']
                require(state in {'exato','direcao','indeterminado','inaplicavel'}, 'ESTADO')
                require(x['direcao'] in {'aumento','reducao','zero','desconhecida'}, 'DIRECAO')
                require(x['unidade'] in {'dia_corrido','BRL_centavo'}, 'UNIDADE')
                if state == 'exato':
                    require(type(value) is int and value >= 0 and not x['lacunas'], 'VALOR_EXATO')
                    require(x['direcao']=='desconhecida', 'ABSOLUTO_DIRECAO')
                else:
                    require(value is None, 'LACUNA_NAO_ZERO')
                    if state == 'direcao': require(x['direcao'] in {'aumento','reducao'}, 'DIRECAO_ESTADO')
                    if state == 'indeterminado': require(bool(x['lacunas']) and x['direcao']=='desconhecida', 'LACUNA')
                    if state == 'inaplicavel': require(bool(x['motivo']) and not x['lacunas'] and x['direcao']=='desconhecida', 'INAPLICAVEL')
            for v in x.values(): walk(v)
    walk(s)
    require(set(activities)=={i for i,e in entities.items() if e['tipo'] in {'atividade','marco'}}, 'ATIVIDADES')
    restrictions = unique([r for a in activities.values() for r in a['restricoes_liberacao']])
    original = json.loads((ROOT.parent/'projeto_minimo_v1/inputs/base.json').read_text())
    for a in activities.values():
        require(a['entidade_id']==a['id'] and a['duracao']['unidade']=='dia_corrido', 'ATIVIDADE_ID_UNIDADE')
        for r in a['restricoes_liberacao']:
            require(r['atividade_id']==a['id'] and r['tipo'] in {'nao_antes','disponibilidade_requerida'} and r['valor']['unidade']=='dia_corrido', 'RESTRICAO')
    for a in original['atividades']:
        require(activities[a['id']]['duracao']['valor']==a['duracao']['valor'], 'DURACAO_SNAPSHOT')
        for r in a['restricoes_contratuais']:
            n=restrictions[r['id']]
            require(n['atividade_id']==a['id'] and n['tipo']==r['tipo'] and n['valor']['valor']==r['valor_dia'], 'PISO_PRESERVADO')
    require(len(restrictions)==6, 'RESTRICOES')
    fs=[]; expected=[]
    for r in relations.values():
        a,b=r['origem_id'],r['destino_id']
        require(a in entities and b in entities, 'ENDPOINT_INVALIDO')
        if r['tipo']=='precede_FS':
            require(a in activities and b in activities and r['lag_dias']==0, 'FS_TIPO_LAG')
            fs.append((a,b))
            expected.append((a,b,r['id'],None,'precedencia_FS_lag0',None))
        elif r['tipo']=='fornece':
            require(entities[a]['tipo']=='fornecedor' and entities[b]['tipo']=='componente', 'FORNECE_TIPO')
        elif r['tipo']=='requer':
            require(a in activities and entities[b]['tipo']=='componente', 'REQUER_DIRECAO')
        else: require(False, 'TIPO_RELACAO')
    dag(fs)
    expected_relations = {
        'l_0f81': ('n_73fa','n_c820','fornece','f_11ebeff90b'),
        'l_b6d2': ('n_42be','n_c820','requer','f_aab5d508ec'),
        'l_938a': ('n_42be','n_a367','precede_FS','f_e847b102df'),
        'l_263e': ('n_915c','n_a367','precede_FS','f_e847b102df'),
        'l_d405': ('n_a367','n_08df','precede_FS','f_e847b102df'),
        'l_8a19': ('n_08df','n_e659','precede_FS','f_e847b102df')}
    require(set(relations)==set(expected_relations), 'RELACOES_SNAPSHOT')
    for rid,(a,b,kind,fid) in expected_relations.items():
        r=relations[rid]
        require((r['origem_id'],r['destino_id'],r['tipo'])==(a,b,kind) and r['fonte_refs']==[{'fonte_id':fid,'localizador':sources[fid]['localizador']}], 'RELACAO_FONTE_SNAPSHOT')
    require(len(transfers)==1, 'TRANSFERENCIAS')
    for t in transfers.values():
        require(t['relacao_id'] in relations, 'TRANSFERENCIA_RELACAO')
        r=relations[t['relacao_id']]
        require(r['tipo']=='requer' and t['operacao']=='disponibilidade_para_restricao' and t['origem_atributo']=='disponibilidade', 'TRANSFERENCIA_TIPO')
        n=restrictions[t['restricao_destino_id']]
        require(n['atividade_id']==r['origem_id'] and n['regra_transferencia_id']==t['id'] and n['atributo_origem_ref']=={'entidade_id':r['destino_id'],'atributo':'disponibilidade'}, 'TRANSFERENCIA_ALVO')
        require(n['valor']['valor']==entities[r['destino_id']]['atributos']['disponibilidade']['conhecimento']['valor'], 'MATERIALIZACAO')
        expected.append((r['destino_id'],r['origem_id'],r['id'],t['id'],'disponibilidade_para_restricao',n['id']))
    actual=[(p['origem_id'],p['destino_id'],p['relacao_id'],p['regra_transferencia_id'],p['efeito_permitido'],p.get('restricao_id')) for p in projection]
    require(set(actual)==set(expected) and len(actual)==len(expected), 'PROJECAO_DIRECAO_REGRA')
    edges=[(p['origem_id'],p['destino_id']) for p in projection]
    dag(edges)
    require(not any('n_73fa' in edge for edge in edges), 'CONTEXTUAL_NAO_PROPAGA')
    def reaches(start, end, visited=None):
        visited=set() if visited is None else visited
        if start==end:return True
        if start in visited:return False
        visited.add(start)
        return any(reaches(b,end,visited) for a,b in edges if a==start)
    require(all(reaches(n,s['marco_final_id']) for n in activities), 'FECHAMENTO_MARCO')
    require({a for a,b in fs if b=='n_a367'}=={'n_42be','n_915c'}, 'CONVERGENCIA')
    require(entities[s['marco_final_id']]['tipo']=='marco' and activities[s['marco_final_id']]['duracao']['valor']==0, 'MARCO')
    require(s['parcelas_base']==[{**p,'fonte_refs':[{'fonte_id':i,'localizador':sources[i]['localizador']} for i in p['fonte_refs']]} for p in original['parcelas_base']], 'PARCELAS_SNAPSHOT')
    for c in s['regras_custo']:
        require(c['parcela_id'] in parcels and c['intervalo']['fim_ref']=={'atividade_id':s['marco_final_id'],'atributo':'fim'} and c['intervalo']['inicio_ref']=='D0', 'CUSTO_REFERENCIAS')
        require(c['taxa_centavos_dia']==10000 and c['base_contratada_dias']==10 and c['politica_reducao']=='sem_credito' and c['unidade_taxa']=='BRL_centavo/dia_corrido', 'CUSTO_UNIDADES')
    require(len(s['regras_custo'])==1 and len(s['regras_locais'])==1, 'CATALOGOS')
    local=s['regras_locais'][0]
    require(local['no_id']=='n_a367' and set(local['operacoes_permitidas'])=={'confirmar_manutencao_atributo','confirmar_ausencia_parcela_adicional'}, 'REGRA_LOCAL')
    require('satisfeita' not in local and 'resultado' not in local, 'CONDICAO_NAO_APLICADA')
    require(all(v['completa'] is True for v in s['declaracoes_completude'].values()), 'COMPLETUDE')
    require(s['linha_base']['fim']['valor']==10 and s['linha_base']['custo_centavos']['valor']==500000, 'BASE_DECLARADA')
    # Conferência de orçamento, sem incidência/cronograma calculados.
    require(sum(p['valor_centavos'] for p in parcels.values())==500000, 'SOMA_ORCAMENTO')

def main():
    manifest=json.loads((ROOT/'manifesto.json').read_text())
    for f in manifest['proveniencia']:
        data=(ROOT.parent/'projeto_minimo_v1'/f['arquivo']).read_bytes()
        require(hashlib.sha256(data).hexdigest()==f['sha256'], 'HASH_ORIGEM')
    s=json.loads((ROOT/'estado_projeto.json').read_text())
    p=json.loads((ROOT/'projecao_causal.json').read_text())
    validate(s,p)
    print('OK: proveniência, fontes literais, IDs, unidades, pisos, DAG, projeção, convergência, marco, catálogos e orçamento.')
    trials=[]
    bad=copy.deepcopy(s);bad['relacoes'][2]['destino_id']='inexistente';trials.append(('ID inválido',bad,p,'ENDPOINT_INVALIDO'))
    bad=copy.deepcopy(s);bad['relacoes'][1]['origem_id'],bad['relacoes'][1]['destino_id']='n_c820','n_42be';trials.append(('requer invertido',bad,p,'REQUER_DIRECAO'))
    badp=copy.deepcopy(p);badp[0]['origem_id'],badp[0]['destino_id']='n_42be','n_c820';trials.append(('projeção invertida',s,badp,'PROJECAO_DIRECAO_REGRA'))
    bad=copy.deepcopy(s);bad['relacoes'].append(dict(id='l_teste',origem_id='n_e659',destino_id='n_a367',tipo='precede_FS',lag_dias=0,fonte_refs=bad['relacoes'][2]['fonte_refs']));trials.append(('ciclo',bad,p,'CICLO'))
    bad=copy.deepcopy(s);bad['atividades'][0]['restricoes_liberacao'][0]['valor']['valor']=2;trials.append(('piso sobrescrito',bad,p,'PISO_PRESERVADO'))
    bad=copy.deepcopy(s);bad['atividades'][0]['duracao']['unidade']='hora';trials.append(('unidade inválida',bad,p,'UNIDADE'))
    for name,state,proj,code in trials:
        try: validate(state,proj)
        except ValueError as err:
            require(str(err)==code, f'CONTRAPROVA_DIAGNOSTICO:{name}:{err}')
            print(f'REJEITADO: {name} ({code})')
        else: raise ValueError(f'CONTRAPROVA_ACEITA:{name}')
    print('7 nós; 6 relações; 5 arcos causais; 1 regra de transferência; 1 local; 1 custo; 6 contraprovas rejeitadas.')

if __name__=='__main__':
    main()
