"""Projeção explícita do Alfa no contrato já validado pelo motor histórico."""
from copy import deepcopy
import json
from . import ROOT, VERSION
from motor_deterministico.motor import preparar


def carregar():
    return json.loads((ROOT/'inputs/grafo.json').read_text()), json.loads((ROOT/'inputs/documentos.json').read_text())


def conhecimento(valor, refs, lacuna='Magnitude não informada na fonte'):
    return dict(estado='exato' if valor is not None else 'indeterminado',valor=valor,direcao='desconhecida',evidencias=deepcopy(refs),lacunas=[] if valor is not None else [lacuna],motivo=None)


def fontes(documento):
    return [dict(id=t['id'],documento_id=documento['id'],versao=documento['versao'],localizador=t['localizador'],trecho=t['texto']) for t in documento['trechos']]


def projetar(grafo, documentos):
    fs=[f for d in documentos if d['papel']=='planejamento' for f in fontes(d)]
    refs={f['id']:dict(fonte_id=f['id'],localizador=f['localizador']) for f in fs}
    e=dict(schema_version='1.0-proposta',projeto_id=grafo['id'],versao=VERSION,moeda='BRL',
           calendario=dict(unidade='dia_corrido',indice_inicial=0),marco_final_id='M_RELEASE',fontes=fs,
           entidades=[],atividades=[],relacoes=[],parcelas_base=[],regras_custo=[],regras_transferencia=[],regras_locais=[],
           declaracoes_completude={k:dict(completa=True,fonte_refs=[refs['BASE']]) for k in ('entregas','custos','relacoes')},
           linha_base=dict(fim=conhecimento(grafo['fim_base'],[refs['BASE']]),custo_centavos=conhecimento(grafo['custo_base'],[refs['BASE']])))
    for n in grafo['nodes']:
        if not n['parametros']: continue  # Pessoas/áreas permanecem no grafo documental, não no solver.
        p=n['parametros']; r=n['fontes']
        # Fornecedores/componentes são pontos de disponibilidade (atividade de duração zero).
        # Tipo de domínio permanece no grafo; o motor recebe somente a projeção matemática.
        e['entidades'].append(dict(id=n['id'],tipo='marco' if n['type']=='Milestone' else 'atividade',nome=n['name'],atributos={},fonte_refs=r))
        e['atividades'].append(dict(id=n['id'],entidade_id=n['id'],duracao=conhecimento(p['duracao'],r),fonte_refs=r,
            restricoes_liberacao=[dict(id='release_'+n['id'],atividade_id=n['id'],tipo='nao_antes',valor=conhecimento(p['nao_antes'],r),fonte_refs=r)]))
    for r in grafo['edges']:
        if r['classe']=='temporal':
            e['relacoes'].append(dict(id=r['id'],origem_id=r['source'],destino_id=r['target'],tipo='precede_FS',lag_dias=0,fonte_refs=r['fontes']))
    for p in grafo['parcelas']:
        e['parcelas_base'].append(dict(id=p['id'],escopo_id=grafo['id'],descricao=p['descricao'],valor_centavos=p['valor_centavos'],moeda='BRL',fonte_refs=p['fontes']))
    for rid,parcel,start,end,days,rate,fixed,source in [
        ('OVERHEAD','p_19','D0','M_RELEASE',40,30000,1200000,'R.OVERHEAD'),
        ('LAB','p_17','M_PROTO_READY','M_VALIDATION',10,50000,2000000,'R.LAB')]:
        rf=[refs[source]]
        e['regras_custo'].append(dict(id=rid,parcela_id=parcel,taxa_centavos_dia=rate,unidade_taxa='BRL_centavo/dia_corrido',base_contratada_dias=days,politica_reducao='sem_credito',
            intervalo=dict(inicio_ref='D0' if start=='D0' else dict(atividade_id=start,atributo='fim'),fim_ref=dict(atividade_id=end,atributo='fim')),
            condicao='Extensão além da franquia contratada, uma cobrança por obrigação',fonte_refs=rf,
            decomposicao_base=dict(fixo_centavos=conhecimento(fixed,rf),incidencia_centavos=conhecimento(0,rf))))
    r=refs['LOCAL.ASSEMBLY']
    # substituir_duracao já é permissão nativa da atividade; não duplicá-la.
    e['regras_locais']=[dict(id='ASSEMBLY_DURATION',no_id='T_ASSEMBLY',clausula=r,fonte_refs=[r],condicao_textual=next(f['trecho'] for f in fs if f['id']=='LOCAL.ASSEMBLY'),operacoes_permitidas=['confirmar_manutencao_atributo'],atributos_alvo=['duracao'])]
    preparar(e)  # Não altera baseline para coincidir com cálculo; rejeita discrepância.
    return e


def normalizar(cenario, estado):
    d=cenario['documento']
    from .cadastro import validar_documento
    validar_documento(d,[n['id'] for n in estado['entidades']])
    if d['papel']!='mudanca' or not d['trechos']: raise ValueError('Documento de mudança sem texto')
    mentioned=cenario['entidades_mencionadas']
    if not mentioned or not set(mentioned)<={n['id'] for n in estado['entidades']}:
        raise ValueError('Cadastro de menções precisa de revisão')
    return dict(evento_id=cenario['id'],projeto_id=estado['projeto_id'],versao_projeto=estado['versao'],instante_observacao=0,
                relato='\n'.join(t['texto'] for t in d['trechos']),origem=dict(autor=d['autoria'],documento_id=d['id'],data_registro='2026-11-09'),
                entidades_mencionadas=mentioned,escopo='Prospectivo D0; somente universo sintético Alfa v1',lacunas=[],evidencias=fontes(d))


def grafo_documental(grafo, documentos, cenario):
    g=deepcopy(grafo)
    ds=deepcopy(documentos)
    # Só acrescentar versão nova, nunca substituir o documento anterior.
    current=cenario['registro_vigente']
    if not any(d['id']==current['id'] and d['versao']==current['versao'] for d in ds): ds.append(deepcopy(current))
    ds.append(deepcopy(cenario['documento']))
    for d in ds:
        uid=d['id']+'@'+d['versao']
        g['nodes'].append(dict(id=uid,name=d['nome']+' v'+d['versao'],type='Document',documento=d,parametros={},fontes=[]))
        for t in d['trechos']:
            relation='registra_situacao' if d['papel']=='situacao' else 'comunica_mudanca' if d['papel']=='mudanca' else 'estabelece_condicao' if d['id']=='DOC_CONTRACT' else 'descreve'
            for target in t['vinculos']:
                if target=='PROJECT': target='M_RELEASE'
                if target=='DOC_CAD': target='DOC_CAD@1'
                g['edges'].append(dict(id=uid+'/'+t['id']+'/'+target,source=uid,target=target,type=relation,classe='documental',trecho=t['id']))
        if d['anterior']:
            g['edges'].append(dict(id=uid+'/anterior',source=uid,target=d['anterior'],type='revisa_versao',classe='documental'))
    g['edges'].append(dict(id='produz_cad',source='T_CAD',target='DOC_CAD@1',type='produz',classe='documental'))
    # Incidência financeira é explícita e não vira precedência.
    for node in ['TEST_LOAD','TEST_THERMAL','TEST_LIFE','TEST_SEAL','TEST_EMC']:
        g['edges'].append(dict(id='custo_'+node,source=node,target='M_VALIDATION',type='incide_em_obrigacao_compartilhada',classe='financeira',parcela_id='p_17'))
    return g
