"""Integração H explícita e isolada; B/T não importam esta fronteira."""
from copy import deepcopy
from interpretacao_no.contratos import hash_json
from condicoes.views import conferir_snapshot, projetar, FONTE


def executar_h(base, evento_comum, fontes, estado, evento, view, interpretador, politica, *, vinculo, origem):
    conferir_snapshot(base,fontes,estado,vinculo)
    if origem not in ('simulado','transporte_mock','llm_transporte_injetado'):
        raise ValueError('Origem H obrigatória')
    from interpretacao_no import Simulado
    if (isinstance(interpretador,Simulado) or getattr(interpretador,'origem',None)=='simulado') and origem!='simulado':
        raise ValueError('Interpretador simulado não pode ser rotulado real')
    if view['condicao']!='H' or view['view_hash']!=hash_json({k:v for k,v in view.items() if k!='view_hash'}):
        raise ValueError('View H inválida')
    from condicoes.views import montar_views
    if montar_views(base,evento_comum,fontes,estado,vinculo=vinculo)['H']!=view:
        raise ValueError('View H não corresponde ao snapshot')
    for k in ('evento_id','projeto_id','instante_observacao','relato','origem','escopo','lacunas'):
        if evento[k]!=evento_comum[k]: raise ValueError('Evento H divergente '+k)
    if evento['versao_projeto']!=estado['versao']:
        raise ValueError('Versão H divergente')
    esperadas=sorted([projetar(f,FONTE) for f in fontes if f['id'] in evento_comum['evidencia_ids']],key=lambda f:f['id'])
    if sorted([projetar(f,FONTE) for f in evento['evidencias']],key=lambda f:f['id'])!=esperadas:
        raise ValueError('Evidências H divergentes')
    # Importação tardia somente na condição H; não cria política automática.
    from .orquestracao import avaliar
    r=avaliar(deepcopy(estado),deepcopy(evento),interpretador,politica)
    r['condicao_orquestracao']=r.get('condicao')
    r.update(condicao='H', contrato_h='2.0-h', view_hash=view['view_hash'],snapshot_hash=hash_json(estado),evento_hash=hash_json(evento))
    r['execucao'].update(origem=origem,modelo=getattr(interpretador,'modelo',None),
        config_hash=hash_json(getattr(interpretador,'configuracao',{})),
        configuracao=deepcopy(getattr(interpretador,'configuracao',{})))
    r['vinculo_informacional']=deepcopy(vinculo)
    r['politica_versao']=politica.versao
    return r
