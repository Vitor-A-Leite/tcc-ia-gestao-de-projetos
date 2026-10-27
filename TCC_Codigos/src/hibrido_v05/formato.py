"""Pedido local v05 explícito, sem API ou reparo de conteúdo observado."""
from copy import deepcopy
from formato_local_v04.contrato import SISTEMA as ANTERIOR,compilar as compilar_anterior
from .contratos import VERSAO,SCHEMA
SISTEMA=ANTERIOR.replace('FORMATO LOCAL v4.0.','FORMATO LOCAL H v5.0.').replace('A versão do formato é 4.0; schema_version da resposta continua 1.0-proposta.','A versão do formato é 5.0; schema_version da resposta é 2.0-analise-local.').replace('confirmar_ausencia_parcela_adicional: valor é INTEIRO ESCALAR 0;avaliacao.custo deve\nser ConhecimentoDelta exato 0, direcao zero, evidências e nenhuma lacuna.','confirmar_ausencia_parcela_adicional: valor é INTEIRO ESCALAR 0 SOMENTE para a cláusula identificada em regra_refs; isso NÃO declara custo total zero do nó.').replace('Justificativa textual fica em justificativa;referências às fontes em evidencias;','justificativa DEVE ser STRING não vazia, nunca array/lista/objeto.\nReferências às fontes ficam em evidencias;')+'''
CONTRATO H v05: cada confirmação identifica UMA única regra local em regra_refs,
usa o predicado aplicabilidade_<regra_id> e cita também a cláusula específica.
Não confirme ausência e custo não zero/indeterminado para a MESMA cláusula.
Obrigações independentes no mesmo nó podem ter custo positivo: preserve suas IDs.
Lacuna de readequação usa a obrigação_lacuna_id da regra em escopos_regras e a regra
em regra_refs. Resolver uma cláusula não resolve outras cláusulas no mesmo nó.
A LLM interpreta fatos, condições e alterações locais. Python calcula convergência
por máximo, cronograma FINAL e incidência das regras temporais já catalogadas.
Não invente taxa/aditivo nem registre custo desconhecido somente porque depende do
fim global: deixe a regra intacta e o motor calculará depois de receber as propostas.
Quando faltar duração/taxa/valor factual, proponha Conhecimento indeterminado ou
registrar_lacuna_custo, com evidência e lacuna específica, sem inventar valor.
pendencias_operacionais é campo OBRIGATÓRIO: lista de strings não vazias e únicas.
Use [] quando fatos pertinentes estiverem representados por propostas/conhecimentos.
Use uma pendência explícita quando falta factual pertinente NÃO puder ser representada
pelas permissões; não use baseline como substituto silencioso de fato desconhecido.
Não conhecer o término global antes do solver não é pendência operacional.
avaliacao é diagnóstico local, não previsão global. lacunas contém notas diagnósticas;
nenhuma nota, hash ou citação autoriza semanticamente proposta. Faltas factuais têm
de estar em propostas indeterminadas ou pendencias_operacionais, não só em prosa.
Não repare hashes, não converta justificativa em lista e não alegue auditoria.
'''

def compilar(c,efeitos):
    d=compilar_anterior(c,efeitos)
    d.update(versao_formato=VERSAO,parser_obrigatorio='hibrido_v05.contratos.validar',schema_version_resposta=SCHEMA,escopos_regras=deepcopy(c['escopos_regras']),tipos_campos=dict(justificativa='string não vazia; array é inválido, sem conversão',pendencias_operacionais='lista de strings; [] quando nenhuma falta factual fora do estado/propostas',lacunas='lista de notas diagnósticas; não substitui estado quantitativo ou pendência operacional'),responsabilidade=dict(LLM='interpretar condições/regras e propor fatos/alterações locais',solver='calcular datas finais e custos das regras catalogadas com o cronograma consolidado'))
    d['campos_analise'].append('pendencias_operacionais')
    for p in d['operacoes_permitidas']:
        if p['operacao'].startswith('confirmar_'):
            p['regra_refs_tipo']='lista de exatamente uma regra local compatível'
            p['clausula_e_predicado_da_mesma_regra_obrigatorios']=True
        if p['operacao']=='confirmar_ausencia_parcela_adicional':
            p.pop('avaliacao_custo_exigida',None)
            p['zero_escopado']='somente cobrança adicional da regra; custo total do nó independente'
    return d
