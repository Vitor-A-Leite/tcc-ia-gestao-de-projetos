"""Autoria explícita do fixture sintético. Não importa o preditor ou o motor.

Referências aritméticas são constantes autorais calculadas antes das execuções.
Não regenerar inputs selados para acomodar previsões.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
from . import ROOT, REPO, VERSION


def gravar(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def criar(dest):
    original = REPO / 'TCC_Codigos/data/project_graph.json'
    g = json.loads(original.read_text())
    docs, refs = [], {}
    def documento(id, nome, papel, versao='1', anterior=None, artefato=None):
        d = dict(id=id, nome=nome, papel=papel, versao=versao, anterior=anterior,
                 sintetico=True, autoria='Equipe fictícia Alfa / fixture acadêmico',
                 formato='texto_preparado_json', artefato=artefato, trechos=[])
        docs.append(d)
        return d
    def trecho(d, id, texto, vinculos):
        t = dict(id=id, localizador='§'+id, texto=texto, vinculos=vinculos)
        d['trechos'].append(t)
        refs[id] = dict(fonte_id=id, localizador=t['localizador'])
        return refs[id]
    plan = documento('DOC_PLAN', 'Plano integrado Alfa ampliado', 'planejamento')
    contract = documento('DOC_CONTRACT', 'Contratos e parcelas Alfa', 'planejamento')
    cad = documento('DOC_CAD', 'Desenho CAD do atuador', 'planejamento')
    trecho(cad, 'CAD.1', 'Desenho CAD revisão 1 produzido pela atividade T_CAD. Geometria mantida nos cenários de entrega e custo.', ['T_CAD','C_HOUSING'])
    schedule = {'T_REQ':2,'T_DESIGN':3,'T_CAD':5,'T_FEA':4,'T_PROC':6,'T_ASSEMBLY':5,'T_DOC':3,'T_RELEASE':2,
                'TEST_LOAD':4,'TEST_THERMAL':6,'TEST_LIFE':10,'TEST_SEAL':3,'TEST_EMC':5}
    releases = {'SUP_MOTOR':18,'SUP_GEAR':20,'SUP_HOUSING':17,'SUP_SENSOR':16,'SUP_ELEC':19,'C_COUPLING':18}
    nodes = deepcopy(g['nodes'])
    for n in nodes:
        quantitative = n['type'] in ('Supplier','Component','Task','Test','Milestone')
        n.update(origem='Alfa original', sintetico_parametros=True, parametros={})
        if quantitative:
            n['parametros'] = dict(duracao=schedule.get(n['id'],0), nao_antes=releases.get(n['id'],0))
            n['fontes'] = [trecho(plan, 'N.'+n['id'], f"{n['name']} ({n['id']}): duração {schedule.get(n['id'],0)} dias corridos; não antes de D{releases.get(n['id'],0)}. Fornecedor representa disponibilidade contratada; componente representa ponto de disponibilidade, ambos com duração zero.", [n['id']])]
        else:
            n['fontes'] = [trecho(plan, 'N.'+n['id'], f"{n['name']} ({n['id']}) é entidade contextual, sem propagação quantitativa.", [n['id']])]
    edges = []
    for i, e in enumerate(g['edges']):
        kind = 'temporal' if e['type'] in ('supplies','required_for','precedes') else 'contexto'
        rid = 'E'+str(i+1).zfill(3)
        ref = trecho(plan, rid, f"{e['source']} → {e['target']}: {e['type']}; " + ('fim-início, lag zero, obrigação conjunta.' if kind=='temporal' else 'contexto; não propaga prazo nem custo.'), [e['source'],e['target']])
        edges.append(dict(id=rid, **e, classe=kind, fontes=[ref]))
    trecho(plan, 'BASE', 'D0=2026-11-09, dias corridos inteiros. Entregas já contratadas em D0. Baseline: término D40, custo total 15200000 centavos BRL. Calendários úteis, nivelamento de recursos, impostos e probabilidade não modelados. Custos e dependências completos somente no universo deste fixture.', ['M_RELEASE'])
    trecho(plan, 'LOCAL.ASSEMBLY', 'T_ASSEMBLY dura 5 dias. Mudança exclusivamente de entrega ou preço mantém a duração. Somente uma alteração técnica explícita pode substituir a duração; ausência de informação técnica não autoriza retrabalho.', ['T_ASSEMBLY'])
    parcels = []
    specifications = [('p_10','Motor',3000000,'SUP_MOTOR'),('p_11','Redutor',2000000,'SUP_GEAR'),('p_12','MetalForm',1500000,'SUP_HOUSING'),('p_13','Sensor',500000,'SUP_SENSOR'),('p_14','Eletrônica',1000000,'SUP_ELEC'),('p_15','Engenharia',2500000,'T_CAD'),('p_16','Montagem',1000000,'T_ASSEMBLY'),('p_17','Laboratório compartilhado',2000000,'M_VALIDATION'),('p_18','Frete compartilhado',500000,'SUP_HOUSING'),('p_19','Gestão e instalação',1200000,'M_RELEASE')]
    for id,name,cost,owner in specifications:
        f = trecho(contract, 'P.'+id, f'{id}: {name}; valor fixo {cost} centavos BRL; custódia operacional {owner}. Uma obrigação única; não multiplicar por componentes ou caminhos.', [owner])
        parcels.append(dict(id=id,descricao=name,valor_centavos=cost,proprietario=owner,fontes=[f]))
    trecho(contract,'R.OVERHEAD','Gestão p_19: fixo 1200000 centavos; extensão de D0 ao fim de M_RELEASE além de 40 dias a 30000 centavos/dia; sem crédito por redução. Cobrança única por projeto.', ['M_RELEASE'])
    trecho(contract,'R.LAB','Laboratório p_17: fixo 2000000 centavos; inclui 10 dias entre fim de M_PROTO_READY e fim de M_VALIDATION; excedente a 50000 centavos/dia. Laboratório compartilhado por todos os ensaios; cobrar uma vez o intervalo comum, sem somar ramos paralelos. Sem crédito por redução.', ['M_PROTO_READY','M_VALIDATION','TEST_LOAD','TEST_THERMAL','TEST_LIFE','TEST_SEAL','TEST_EMC'])
    old = documento('STATUS','Status Report Alfa','situacao', '0', artefato='status_report')
    trecho(old,'SR0.FINISH','Previsão anterior não vigente: marco final D39.', ['M_RELEASE'])
    status = documento('STATUS','Status Report Alfa','situacao', '1', 'STATUS@0', 'status_report')
    claims = [('FINISH','M_RELEASE','fim',40,'dia_corrido'),('COST','PROJECT','custo',15200000,'BRL_centavo'),('MOTOR','SUP_MOTOR','fim',18,'dia_corrido'),('FREEZE','M_DESIGN_FREEZE','fim',14,'dia_corrido'),('CAD','DOC_CAD','versao','1','versao')]
    for id,node,field,val,unit in claims:
        trecho(status,'SR.'+id,f'{id}: {node}.{field} = {val} {unit}.', [node])
        status['trechos'][-1]['afirmacao'] = dict(entidade=node,campo=field,valor=val,unidade=unit)
    for id,name,artifact,text,links in [
        ('ACTION','Action Log','action_log','A-01: Carla deve confirmar recebimento dos pedidos; prazo D12, aberta. Um atraso não cria automaticamente nova ação.', ['SUP_MOTOR','P_CARLA']),
        ('RISK','Risk Register','risk_register','R-01: evento futuro de nova ruptura de fornecimento, probabilidade não avaliada, responsável Carla. Um atraso ocorrido é fato, não novo risco automaticamente.', ['SUP_MOTOR','P_CARLA']),
        ('DECISION','Decision Log','decision_log','DEC-01: decisão histórica de manter arquitetura mecânica aprovada na baseline. Novos impactos não alteram uma decisão histórica.', ['T_CAD','M_RELEASE'])]:
        d=documento(id,name,'situacao',artefato=artifact)
        trecho(d,id+'.1',text,links)
    graph = dict(id='ALFA-AMPLIADO',versao=VERSION,nome=g['name']+' — extensão documental sintética',
                 original_path=str(original.relative_to(REPO)), original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                 nodes=nodes,edges=edges,parcelas=parcels,moeda='BRL',D0='2026-11-09',fim_base=40,custo_base=15200000,
                 desconhecidos={'probabilidade_riscos':None,'cambio':None,'calendario_util':None},
                 papeis_documentais=['planejamento','mudanca','situacao'])
    # Gabaritos são autorais e independentes do solver. Fórmula manual:
    # montagem=max(20, entregas); fim=montagem+5+max(4,6,10,3,5)+3+2.
    # custo=15200000+30000*(fim-40)+50000*max(0, max(ensaios)-10)+delta fixo.
    specs = [
      ('D01','Folga absorve entrega','dev',[('SUP_MOTOR','release',19)],40,15200000,19, ['SR.MOTOR']),
      ('D02','Atraso crítico do motor','dev',[('SUP_MOTOR','release',25)],45,15350000,25,['SR.FINISH','SR.COST','SR.MOTOR']),
      ('D03','Preço sem atraso','dev',[('SUP_MOTOR','cost',3300000)],40,15500000,18,['SR.COST']),
      ('D04','Data de entrega desconhecida','dev',[('SUP_MOTOR','release',None)],None,None,None,['SR.FINISH','SR.COST','SR.MOTOR']),
      ('D05','Fornecedor comum e ramos convergentes','dev',[('SUP_HOUSING','release',24),('SUP_MOTOR','release',23)],44,15320000,23,['SR.FINISH','SR.COST','SR.MOTOR']),
      ('D06','Laboratório compartilhado','dev',[('TEST_LOAD','duration',12),('TEST_THERMAL','duration',14)],44,15520000,18,['SR.FINISH','SR.COST']),
      ('D07','Relatório já atualizado','dev',[('SUP_MOTOR','release',25)],45,15350000,25,[]),
      ('D08','Confirmação sem efeito','dev',[('SUP_MOTOR','release',18)],40,15200000,18,[]),
      ('D09','Custo desconhecido com prazo exato','dev',[('SUP_MOTOR','cost',None)],40,None,18,['SR.COST']),
      ('H01','Caso reservado 01','final',[('SUP_GEAR','release',27)],47,15410000,18,['SR.FINISH','SR.COST']),
      ('H02','Caso reservado 02','final',[('SUP_SENSOR','release',19)],40,15200000,18,[]),
      ('H03','Caso reservado 03','final',[('SUP_ELEC','cost',900000)],40,15100000,18,['SR.COST']),
      ('H04','Caso reservado 04','final',[('SUP_HOUSING','release',None)],None,None,18,['SR.FINISH','SR.COST']),
      ('H05','Caso reservado 05','final',[('SUP_MOTOR','release',23),('SUP_GEAR','release',26)],46,15380000,23,['SR.FINISH','SR.COST','SR.MOTOR']),
      ('H06','Caso reservado 06','final',[('TEST_LOAD','duration',13),('TEST_LIFE','duration',12)],43,15440000,18,['SR.FINISH','SR.COST']),
      ('H07','Caso reservado 07','final',[('SUP_MOTOR','release',22)],42,15260000,22,[]),
      ('H08','Caso reservado 08','final',[('SUP_ELEC','release',19)],40,15200000,18,[]),
    ]
    for id,title,split,changes,end,cost,motor,updates in specs:
        d = dict(id='CHANGE-'+id,nome=title,papel='mudanca',versao='1',anterior=None,sintetico=True,autoria='Fornecedor/equipe fictícios Alfa',formato='texto_preparado_json',artefato=None,trechos=[])
        statements=[]
        for node,field,value in changes:
            parcel=next((p['id'] for p in parcels if p['proprietario']==node),None)
            statements.append(f"{node}: "+({'release':'nova disponibilidade contratada','duration':'nova duração','cost':f'novo valor total da parcela {parcel}'}[field])+f" = {'desconhecida; aguardando confirmação' if value is None else value} "+('centavos BRL' if field=='cost' else 'dias corridos desde D0' if field=='release' else 'dias corridos')+'.')
        statements.append('Demais parâmetros contratuais e durações mantidos. Sem alteração técnica da montagem, ação nova, risco futuro ou decisão adicional comunicada.')
        source='CHANGE.'+id
        d['trechos']=[dict(id=source,localizador='§1',texto=' '.join(statements),vinculos=sorted({x[0] for x in changes}))]
        current=deepcopy(status)
        if id in ('D07','H07'):
            current['versao']='2';current['anterior']='STATUS@1'
            for t in current['trechos']:
                v={'SR.FINISH':end,'SR.COST':cost,'SR.MOTOR':motor}.get(t['id'],t['afirmacao']['valor'])
                t['afirmacao']['valor']=v;t['texto']=f"{t['id']}: {t['afirmacao']['entidade']}.{t['afirmacao']['campo']} = {v} {t['afirmacao']['unidade']}."
        scenario=dict(id=id,titulo=title,particao=split,documento=d,registro_vigente=current,entidades_mencionadas=d['trechos'][0]['vinculos'])
        fixture=dict(origem='simulacao_offline_manual',mudancas=[dict(no=node,campo=field,valor=value) for node,field,value in changes])
        truth=dict(id=id,autoria='Referência autoral prospectiva, sem revisão independente',fim=end,custo=cost,
                   revisar=updates,nao_revisar=sorted(set(t['id'] for t in status['trechos'])-set(updates)),
                   calculo_manual=f'fim={end}; custo={cost}; comparação campo a campo com versão vigente; None significa indeterminado')
        gravar(dest/'cenarios'/split/(id+'.json'),scenario)
        gravar(dest/'simulacoes'/split/(id+'.json'),fixture)
        gravar(dest/'referencias'/split/(id+'.json'),truth)
    gravar(dest/'grafo.json',graph);gravar(dest/'documentos.json',docs)
    manifest={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*.json') if p.name!='SELO.json'}
    gravar(dest/'SELO.json',dict(versao=VERSION,instante_autoria='antes da primeira execução',referencias_prospectivas=True,arquivos=manifest))


def main():
    dest=ROOT/'inputs'
    if dest.exists():
        raise SystemExit('Inputs existentes: recusa sobrescrever. Nova autoria exige nova versão/destino.')
    criar(dest)
if __name__=='__main__': main()
