"""Interpretações manuais injetadas: verificam integração, não inteligência artificial.

Nunca lê referências de avaliação nem calcula a resposta final esperada.
"""
from copy import deepcopy
from .modelo import conhecimento
from hibrido_v07_r3.adaptador import SimuladoV07R3
from hibrido_v07_r3.wire import WIRE


def interpretador(fixture, grafo):
    owners={n['id']:[p['id'] for p in grafo['parcelas'] if p['proprietario']==n['id']] for n in grafo['nodes']}
    def responder(c):
        source=next(f for f in c['fontes'] if f['documento_id']==c['evento']['origem']['documento_id'])
        ref=dict(fonte_id=source['id'],localizador=source['localizador'])
        proposals=[]
        for ch in fixture['mudancas']:
            if ch['no']!=c['no_id']: continue
            if ch['campo']=='cost' and len(owners[ch['no']])!=1:
                raise ValueError('Parcela ambígua: fixture exige identificação explícita antes de simular')
            op,alvo,at,unit={
                'release':('substituir_restricao','release_'+ch['no'],'valor','dia_corrido'),
                'duration':('substituir_duracao',ch['no'],'duracao','dia_corrido'),
                'cost':('substituir_parcela',next(iter(owners.get(ch['no'],[])),None),'valor_centavos','BRL_centavo')}[ch['campo']]
            val=conhecimento(ch['valor'],[ref]);val.pop('direcao')
            proposals.append(dict(operacao=op,alvo_id=alvo,atributo=at,unidade=unit,valor=val,evidencias=[ref],relacao_refs=[],regra_refs=[],condicoes=[],origem_ref=ref))
        rules=[]
        for r in c['regras']:
            if 'no_id' not in r: continue
            # Fixture declara explicitamente que a duração da montagem se mantém.
            idx=[i for i,p in enumerate(proposals,1) if p['operacao']=='substituir_duracao']
            if idx:
                for i in idx: proposals[i-1]['regra_refs']=[r['id']]
            else:
                proposals.append(dict(operacao='confirmar_manutencao_atributo',alvo_id=c['no_id'],atributo='duracao',unidade='dia_corrido',valor=c['no']['atributos']['duracao']['valor'],
                    evidencias=[ref,r['clausula']],relacao_refs=[],regra_refs=[r['id']],condicoes=[dict(predicado='aplicabilidade_'+r['id'],estado='confirmada',evidencias=[ref,r['clausula']])],origem_ref=ref))
                idx=[len(proposals)]
            rules.append(dict(regra_id=r['id'],propostas_indices=idx))
        # Exercita uma obrigação real de coordenação: o componente pede à montagem
        # resolver a duração. O nó responsável tem de emitir a confirmação escopada.
        routes=[]
        if c['no_id']=='C_MOTOR' and any(x['no']=='SUP_MOTOR' and x['campo']=='release' for x in fixture['mudancas']):
            route=next(r for r in c['responsabilidades_operacionais'] if r['no_id']=='T_ASSEMBLY' and r['operacao']=='substituir_duracao')
            routes=[dict(**route,motivo='Conferir duração da montagem à luz do aviso de entrega',evidencias=[ref])]
        return dict(schema_version=WIRE,propostas=proposals,justificativa='Resposta manual de simulação; o motor calculará o impacto.',lacunas=[],pendencias_operacionais=[],encaminhamentos=routes,resolucoes_regras=rules)
    return SimuladoV07R3(responder)
