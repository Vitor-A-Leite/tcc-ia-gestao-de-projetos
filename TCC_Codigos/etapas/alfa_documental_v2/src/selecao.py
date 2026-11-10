"""Seleção explícita do engenheiro e contrato compacto de sugestões offline."""
from copy import deepcopy
from .vendor.interpretacao_no.contratos import hash_json


def catalogo(grafo):
    return [dict(id=n['id'], nome=n['name'], tipo=n['type'],
                 descricao=n.get('description', n['name']), aliases=n.get('aliases', []))
            for n in grafo['nodes'] if n.get('parametros')]


def limite(valor, maximo, minimo=1):
    if valor == 'todos': valor = maximo
    if isinstance(valor, str) and valor.isascii() and valor.isdecimal(): valor = int(valor)
    if type(valor) is not int or not minimo <= valor <= maximo:
        raise ValueError(f'Digite um inteiro entre {minimo} e {maximo} nós.')
    return valor


def validar(grafo, evento, entradas, max_nos, versao, escopo='impacto_do_evento'):
    ids = {n['id'] for n in catalogo(grafo)}
    if versao != evento['versao_projeto']: raise ValueError('Versão do projeto mudou; refaça a seleção.')
    if not isinstance(entradas, list) or not entradas or any(not isinstance(n, str) for n in entradas):
        raise ValueError('Selecione ao menos um ponto executável.')
    if len(set(entradas)) != len(entradas): raise ValueError('Entradas duplicadas.')
    if not set(entradas) <= ids: raise ValueError('Nó inexistente ou não executável na versão atual.')
    if escopo not in ('impacto_do_evento', 'teste_delimitado'): raise ValueError('Escopo inválido.')
    ausentes = sorted(set(evento['entidades_mencionadas']) - set(entradas))
    return dict(modo='manual', nos_entrada=sorted(entradas),
                limite_nos_analise=limite(max_nos, len(ids), len(entradas)),
                projeto_versao=versao, escopo=escopo, mencoes_fora_da_selecao=ausentes,
                maximo_disponivel=len(ids), total_nos_grafo=len(grafo['nodes']))


def sugerir(evento, grafo, transporte, *, cache, pedido_id, modo='simulacao_offline'):
    """Uma chamada explicitamente pedida; contrato separado de análise local.

    O modo real é explícito e exige transporte identificado e contador de uso.
    A confirmação do engenheiro é obrigatória e separada.
    """
    origem = getattr(transporte, 'origem', None)
    if modo not in ('simulacao_offline', 'ia_real'): raise ValueError('Modo de sugestão inválido.')
    if origem != ('openai_real' if modo == 'ia_real' else 'simulado'):
        raise ValueError('Origem do transporte incompatível com o modo de sugestão.')
    if modo == 'ia_real' and not callable(getattr(transporte, 'snapshot', None)):
        raise ValueError('Sugestão real sem contabilização de consumo.')
    pedido = dict(evento_id=evento['evento_id'], versao=evento['versao_projeto'],
                  relato=evento['relato'], catalogo=catalogo(grafo))
    chave = hash_json([pedido_id, pedido])
    if chave in cache:
        if cache[chave].get('erro'): raise ValueError(cache[chave]['erro'])
        return deepcopy(cache[chave]), False
    # Reservar identidade antes do envio também impede repetição após erro.
    cache[chave] = {'erro': 'Pedido já tentado sem resposta válida; faça um novo pedido explícito.', 'pedido_hash': hash_json(pedido)}
    resposta = transporte(deepcopy(pedido))
    if not isinstance(resposta, dict) or set(resposta) != {'sugestoes', 'ambiguidades'}:
        raise ValueError('Formato de sugestão inválido.')
    ids = {n['id'] for n in pedido['catalogo']}; vistos = set()
    if not isinstance(resposta['ambiguidades'], list) or not all(isinstance(x, str) for x in resposta['ambiguidades']):
        raise ValueError('Ambiguidades inválidas.')
    for x in resposta['sugestoes']:
        if set(x) != {'no_id', 'justificativa'} or x['no_id'] not in ids or x['no_id'] in vistos or not isinstance(x['justificativa'], str) or not x['justificativa'].strip():
            raise ValueError('Sugestão contém alvo inválido ou justificativa ausente.')
        vistos.add(x['no_id'])
    r = dict(**deepcopy(resposta), pedido_hash=hash_json(pedido), origem=modo,
             confirmada=False, chamadas_api=1 if modo == 'ia_real' else 0,
             solicitacoes_simuladas=0 if modo == 'ia_real' else 1)
    cache[chave] = r
    return deepcopy(r), True
