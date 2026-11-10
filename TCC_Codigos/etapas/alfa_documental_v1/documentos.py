"""Verifica afirmações previamente cadastradas, sem parser automático de prosa.

A seleção de um registro não implica necessidade de edição. Recomendações são
rascunhos; aprovação é registro separado, sem rotina de escrita no oficial.
"""
from copy import deepcopy
from interpretacao_no.contratos import hash_json


def chave(doc, trecho):
    a=trecho['afirmacao']
    return f"{doc['id']}@{doc['versao']}:{trecho['id']}:{a['campo']}"


def verificar(result, scenario, documentos):
    status=scenario['registro_vigente']
    selecionados=[dict(documento_id=status['id'],versao=status['versao'],artefato='status_report',motivo='Resumo do projeto e vínculos de afirmações com entidades/calculos',politica='comparacao_campos_cadastrados')]
    analysis=[]; recommendations=[]
    nodes={n['no_id']:n for n in result.get('resultados_nos',[])}
    for t in status['trechos']:
        a=t['afirmacao'];target=a['entidade'];field=a['campo']
        diagnostic=None
        if field=='custo': q=deepcopy(result.get('custo_novo'))
        elif field=='versao': q=dict(estado='exato',valor='1',evidencias=[dict(fonte_id='CAD.1',localizador='§CAD.1')],lacunas=[])
        elif target=='M_RELEASE': q=deepcopy(result.get('fim_novo'))
        else:
            n=nodes.get(target,{})
            q=deepcopy(n.get(field, n.get('quantitativo',{}).get(field)))
            if n.get('processamento') in ('bloqueado','nao_avaliado'): q=None
        if q is None:
            outcome='nao_verificavel';new=None;diagnostic='Sem estado calculado validado para esta afirmação'
        elif q['estado']=='exato':
            new=q['valor'];outcome='ja_atualizado' if new==a['valor'] else 'revisar'
        else:
            new=None
            # Incerteza de informação é diferente de falha de execução/cobertura.
            if result.get('pendencias_execucao'):
                outcome='nao_verificavel';diagnostic='Execução incompleta: não afirmar desatualização'
            else:
                outcome='ja_atualizado' if a['valor'] is None else 'revisar'
        unit=chave(status,t)
        record=dict(unidade=unit,documento_id=status['id'],versao=status['versao'],trecho_id=t['id'],localizador=t['localizador'],afirmacao=deepcopy(a),conteudo_atual=t['texto'],estado=outcome,calculado=q,motivo=diagnostic)
        analysis.append(record)
        if outcome!='revisar': continue
        event_refs=[dict(documento_id=scenario['documento']['id'],versao=scenario['documento']['versao'],trecho_id=x['id'],localizador=x['localizador'],texto=x['texto']) for x in scenario['documento']['trechos']]
        all_sources={f['id']:dict(documento_id=d['id'],versao=d['versao'],trecho_id=f['id'],localizador=f['localizador'],texto=f['texto']) for d in documentos for f in d['trechos']}
        cited=[]
        for ref in q.get('evidencias',[]):
            if ref['fonte_id'] in all_sources: cited.append(all_sources[ref['fonte_id']])
            elif any(x['trecho_id']==ref['fonte_id'] for x in event_refs): cited.extend(x for x in event_refs if x['trecho_id']==ref['fonte_id'])
        ancestors={target}
        while True:
            new_ancestors={e['origem'] for e in result['propagacao'] if e['destino'] in ancestors}-ancestors
            if not new_ancestors: break
            ancestors.update(new_ancestors)
        causal=[e for e in result['propagacao'] if e['estado']!='sem_alteracao' and (field=='custo' or e['destino'] in ancestors)]
        # O cálculo possui o subgrafo inteiro e cada aresta tem sua fonte; não
        # enumeramos exponencialmente todos os caminhos de uma convergência.
        for e in causal:
            for ref in e['fonte_refs']:
                if ref['fonte_id'] in all_sources: cited.append(all_sources[ref['fonte_id']])
        evidence=list({(x['documento_id'],x['versao'],x['trecho_id']):x for x in cited+event_refs}.values())
        value_text=f"{new} {a['unidade']}" if new is not None else 'indeterminado; obter a informação faltante antes de publicar magnitude'
        proposed=f'{target}.{field}: {value_text}.'
        rec=dict(id=hash_json([result['inputs_hash'],unit,proposed])[:20],unidade=unit,documento_id=status['id'],versao_base=status['versao'],trecho_id=t['id'],campo=field,localizador=t['localizador'],
                 conteudo_atual=t['texto'],valor_atual=a['valor'],alteracao_proposta=proposed,valor_proposto=new,
                 justificativa='A afirmação vigente diverge do cálculo condicional.' if new is not None else 'O registro afirma magnitude exata que as informações atuais não sustentam.',
                 estado='recomendacao_pendente_validacao_humana',aprovacao_humana=None,atualizacao_executada=False,
                 evidencias=evidence,calculo_ref=dict(execucao_id=result['execucao_id'],inputs_hash=result['inputs_hash'],quantidade=q,arestas=[x['relacao_id'] for x in causal]),
                 suporte='rastreabilidade_estrutural_verificada; semantica_requer_revisao',origem=result['modo'],execucao_global=result['execucao']['estado'])
        recommendations.append(rec)
    # Não criar ações/riscos/decisões com base apenas no atraso. Implementada a
    # triagem de relações e preservação; extração/atualização própria está pendente.
    relevant=set(scenario['entidades_mencionadas'])|set(result['nos_com_mudanca_quantitativa'])
    triagem=[]
    for d in documentos:
        if d.get('artefato') not in ('action_log','risk_register','decision_log'): continue
        linked=any(set(t['vinculos'])&relevant for t in d['trechos'])
        if linked:
            selecionados.append(dict(documento_id=d['id'],versao=d['versao'],artefato=d['artefato'],motivo='Relação explícita com entidade consultada/alterada',politica='triagem_sem_criacao_automatica'))
        triagem.append(dict(documento_id=d['id'],versao=d['versao'],selecionado=linked,estado='avaliacao_especifica_pendente' if linked else 'fora_do_escopo',recomendacoes=[],
            regra={'action_log':'Exige compromisso, responsável e prazo explícitos; atraso não cria ação.', 'risk_register':'Exige evento futuro incerto; fato ocorrido não é novo risco automaticamente.', 'decision_log':'Exige decisão tomada por autoridade e sua evidência; preservar decisões históricas.'}[d['artefato']]))
    return dict(unidade_avaliacao='documento@versao:trecho:campo',selecionados=selecionados,afirmacoes=analysis,recomendacoes=recommendations,triagem_outros_artefatos=triagem,
                artefatos_implementados=['status_report:comparacao_campos_cadastrados'],artefatos_parciais=['action_log:triagem','risk_register:triagem','decision_log:triagem'])


def registrar_decisao(recomendacao, decisao, revisor, justificativa, documento_atual, destino):
    """Decisão append-only separada. Não toca o documento oficial."""
    import json
    from datetime import datetime, timezone
    if decisao not in ('aprovar','rejeitar') or not revisor.strip() or not justificativa.strip(): raise ValueError('Decisão humana incompleta')
    if documento_atual['id']!=recomendacao['documento_id'] or documento_atual['versao']!=recomendacao['versao_base']: raise ValueError('Documento mudou; rever recomendação')
    t=next(t for t in documento_atual['trechos'] if t['id']==recomendacao['trecho_id'])
    if t['texto']!=recomendacao['conteudo_atual']: raise ValueError('Trecho mudou; recomendação obsoleta')
    entry=dict(recomendacao_id=recomendacao['id'],recomendacao_hash=hash_json(recomendacao),decisao=decisao,revisor=revisor,justificativa=justificativa,instante=datetime.now(timezone.utc).isoformat(),atualizacao_executada=False)
    with destino.open('x',encoding='utf8') as f: json.dump(entry,f,ensure_ascii=False,indent=2)
    return entry
