"""Proveniência de escopo e comparações sobre afirmações extraídas pelo revisor."""
from copy import deepcopy
import json

from . import DATA
from .vendor.interpretacao_no.contratos import hash_json

CADASTRO_ESCOPO = DATA/'escopo_revisao.json'
ID_ESCOPO = 'CONTEXTO.ESCOPO'
CONHECIMENTOS = ('exato', 'indeterminado', 'alternativas', 'ausente')
CAMPOS_ESCOPO = ('projeto_id', 'versao_projeto', 'inicio_dia', 'fim_dia')


def carregar_cadastro():
    return json.loads(CADASTRO_ESCOPO.read_text())


def montar_escopo(referencia, evento, fontes, cadastro):
    """Vínculos conferidos contra cadastro explícito, com snapshot para releitura."""
    divergencias = []
    lacunas = []
    for campo in ('projeto_id', 'versao_projeto'):
        if referencia[campo] != cadastro[campo]:
            divergencias.append(campo)
    registro = cadastro['eventos'].get(referencia['evento_id'])
    if evento['evento_id'] != referencia['evento_id']:
        divergencias.append('evento_id')
    if registro is None:
        lacunas.append('evento_sem_cadastro')
    else:
        documento_id = evento['origem']['documento_id']
        if documento_id != registro['documento_id']:
            divergencias.append('documento_id')
        versoes = {f['versao'] for f in fontes if f['documento_id'] == documento_id}
        if versoes != {registro['versao_documento']}:
            divergencias.append('versao_documento')
    vigencia = cadastro['declaracoes_vigencia'].get(evento['escopo'])
    if vigencia is None:
        lacunas.append('vigencia_sem_cadastro')
    estado = 'verificado'
    if lacunas:
        estado = 'indisponivel'
    if divergencias:
        estado = 'divergente'
    return dict(id=ID_ESCOPO, tipo='cadastro_escopo', estado=estado,
        cadastro=deepcopy(cadastro), cadastro_hash=hash_json(cadastro),
        contexto_hash=referencia['contexto_hash'],
        origem_campos=['referencia.projeto_id', 'referencia.versao_projeto',
                       'referencia.evento_id', 'evento.origem', 'evento.escopo', 'fontes'],
        vigencia=deepcopy(vigencia), divergencias=divergencias, lacunas=lacunas)


def valores_avaliados(pacote):
    valor = pacote['proposto']
    if pacote['proposta']['operacao'] == 'alterar_parametros_contratuais':
        unidades = dict(taxa_centavos_dia='BRL_centavo/dia_corrido',
                        base_contratada_dias='dia_corrido', politica_reducao='politica_reducao')
        return {k: dict(valor=v, unidade=unidades[k]) for k, v in valor.items()}
    return {pacote['proposta']['atributo']: dict(valor=deepcopy(valor), unidade=pacote['proposta']['unidade'])}


def comparar_afirmacao(proposto, fundamento):
    """Compara magnitude e conhecimento após o alinhamento declarado pela IA."""
    if fundamento['aplicabilidade'] != 'mesmo_objeto_e_vigencia':
        return 'insuficiente'
    conhecimento = fundamento['conhecimento']
    indeterminado = proposto is None or isinstance(proposto, dict) and proposto.get('estado') != 'exato'
    if conhecimento == 'ausente':
        return 'insuficiente'
    if conhecimento == 'indeterminado':
        return 'sustentado' if indeterminado else 'insuficiente'
    if indeterminado:
        return 'contradito' if conhecimento == 'exato' else 'ambiguo'
    coincide = hash_json(proposto) in {hash_json(v) for v in fundamento['valores']}
    if not coincide:
        return 'contradito'
    return 'ambiguo' if conhecimento == 'alternativas' else 'sustentado'


def combinar_estados(estados):
    for estado in ('contradito', 'insuficiente', 'ambiguo'):
        if estado in estados:
            return estado
    return 'sustentado'


def comparar_escopo(pacote, restricoes):
    metadados = pacote['metadados_escopo']
    estados = [{'verificado': 'sustentado', 'divergente': 'contradito',
                'indisponivel': 'insuficiente'}[metadados['estado']]]
    cadastro = metadados['cadastro']
    valores = {k: pacote['referencia'][k] for k in ('projeto_id', 'versao_projeto')}
    valores.update({k: (metadados['vigencia'] or {}).get(k) for k in ('inicio_dia', 'fim_dia')})
    for restricao in restricoes:
        campo = restricao['campo']
        fundamento = deepcopy(restricao)
        fundamento['aplicabilidade'] = 'mesmo_objeto_e_vigencia'
        if campo == 'projeto_id':
            fundamento['valores'] = [cadastro['projeto_id'] if v in cadastro['aliases_projeto'] else v
                                     for v in fundamento['valores']]
        if campo == 'versao_projeto':
            fundamento['valores'] = [cadastro['versao_projeto'] if v in cadastro['aliases_versao'] else v
                                     for v in fundamento['valores']]
        if valores[campo] is None:
            estados.append('insuficiente')
        else:
            estados.append(comparar_afirmacao(valores[campo], fundamento))
    return combinar_estados(estados)
