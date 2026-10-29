"""Contrato v06: responsabilidade local e encaminhamento externo explícitos."""
from copy import deepcopy

from hibrido_v05.formato import SISTEMA as SISTEMA_V05, compilar as compilar_v05
from .contratos import SCHEMA, VERSAO

SISTEMA = SISTEMA_V05.replace('v5.0', 'v6.0').replace('v05', 'v06').replace(
    'versão do formato é 5.0', 'versão do formato é 6.0'
).replace('2.0-analise-local', SCHEMA) + '''
RESPONSABILIDADE OPERACIONAL H v06:
O catálogo responsabilidades_operacionais informa quem pode propor cada operação.
Ele é roteamento técnico: não contém fatos novos nem prova que algo foi resolvido.
Proponha SOMENTE operações de permissoes do nó corrente. Para uma alteração
pertinente que cabe a OUTRO nó, use encaminhamentos, copiando a rota EXATA do
catálogo (no_id, operacao, alvo_id, atributo, unidade), com motivo string e evidencias.
encaminhamentos é uma lista obrigatória, vazia quando não há encaminhamento.
Uma mesma rota só pode aparecer uma vez. Nunca encaminhe sua obrigação local.
Operações confirmar_* não admitem encaminhamento: são resoluções locais por cláusula.
O coordenador só resolve o encaminhamento quando uma proposta aceita do responsável
corresponde à operação/alvo/atributo/unidade. Outro encaminhamento não a resolve.
Não crie pendencias_operacionais apenas porque essa operação externa não é sua:
registre o encaminhamento. Se não houver responsável no catálogo ou faltar fato
local que não caiba em proposta indeterminada, preserve pendencias_operacionais.
Encaminhar não substitui fatos locais, predecessores ou alterações de duração.
Não declare fato confirmado, custo zero ou ausência de impacto por haver responsável.
Uma alteração factual desconhecida continua desconhecida mesmo após encaminhamento.
O solver continua calculando cronograma e incidência temporal; não encaminhe o
cálculo do fim global como se fosse um aditivo de regra ou um dado faltante.
'''


def compilar(contexto, efeitos):
    contrato = compilar_v05(contexto, efeitos)
    contrato.update(
        versao_formato=VERSAO, schema_version_resposta=SCHEMA,
        parser_obrigatorio='hibrido_v06.contratos.validar',
        responsabilidades_operacionais=deepcopy(contexto['responsabilidades_operacionais']),
        contrato_encaminhamento=dict(
            campos=['no_id', 'operacao', 'alvo_id', 'atributo', 'unidade', 'motivo', 'evidencias'],
            no_id='nó responsável externo; copiar rota exata do catálogo',
            motivo='string não vazia', evidencias='referências visíveis no contexto',
            fechamento='exige proposta aceita correspondente, sem inferir suporte semântico',
        ),
    )
    contrato['campos_analise'].append('encaminhamentos')
    contrato['tipos_campos']['encaminhamentos'] = 'lista de rotas externas tipadas; [] quando nenhuma'
    return contrato
