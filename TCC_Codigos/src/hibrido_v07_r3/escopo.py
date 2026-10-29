"""Roteamento técnico derivado das permissões; não infere fatos nem valores."""
from copy import deepcopy

from hibrido_v05.contratos import montar_contexto
from interpretacao_no.contratos import campos, exigir, hash_json, lista, texto

CAMPOS_PERMISSAO = ('operacao', 'alvo_id', 'atributo', 'unidade')
CAMPOS_ROTA = ('no_id',) + CAMPOS_PERMISSAO


def chave(item):
    return tuple(item[k] for k in CAMPOS_ROTA)


def catalogar(estado, evento, politica):
    """Somente IDs/operações/unidades, sem valores, propostas ou gabaritos."""
    rotas = []
    donos = {}
    for no_id, selecao in sorted(politica.plano.items()):
        contexto = montar_contexto(
            estado, evento, execucao_id=politica.execucao_id,
            no_id=no_id, revisao=1, **selecao,
        )
        for permissao in contexto['permissoes']:
            if permissao['operacao'] == 'aplicar_regra_catalogada':
                permissao['operacao'] = 'alterar_parametros_contratuais'
            identidade = tuple(permissao[k] for k in CAMPOS_PERMISSAO)
            exigir(identidade not in donos or donos[identidade] == no_id,
                   'Responsabilidade operacional ambígua')
            donos[identidade] = no_id
            rota = dict(no_id=no_id, **permissao)
            if rota not in rotas:
                rotas.append(rota)
    return sorted(rotas, key=chave)


def validar_catalogo(contexto):
    rotas = contexto['responsabilidades_operacionais']
    lista(rotas)
    donos = {}
    for rota in rotas:
        campos(rota, ' '.join(CAMPOS_ROTA))
        for valor in rota.values():
            texto(valor)
        identidade = tuple(rota[k] for k in CAMPOS_PERMISSAO)
        exigir(identidade not in donos, 'Responsabilidade duplicada ou ambígua')
        donos[identidade] = rota['no_id']
    exigir(rotas == sorted(rotas, key=chave), 'Catálogo fora de ordem canônica')
    locais = [{k: r[k] for k in CAMPOS_PERMISSAO}
              for r in rotas if r['no_id'] == contexto['no_id']]
    exigir(sorted(locais, key=hash_json) == sorted(contexto['permissoes'], key=hash_json),
           'Catálogo não corresponde às permissões locais')


def reconciliar(encaminhamentos, propostas, regras_locais):
    """Só propostas já aceitas da passagem atual satisfazem encaminhamentos.

    Uma permissão, outro encaminhamento, cache de passagem anterior ou nota em
    prosa não é resolução. Valores indeterminados continuam indeterminados no motor.
    """
    resolucoes = []
    for registro in encaminhamentos:
        pedido = registro['encaminhamento']
        correspondentes = [p for p in propostas if chave(p) == chave(pedido)]
        criterio = 'operacao_exata'
        if not correspondentes and pedido['operacao'] == 'substituir_duracao':
            regras = [r for r in regras_locais if r['no_id'] == pedido['no_id'] and 'duracao' in r['atributos_alvo']]
            if len(regras) == 1:
                regra = regras[0]
                correspondentes = [p for p in propostas
                    if p['operacao'] == 'confirmar_manutencao_atributo'
                    and all(p[k] == pedido[k] for k in ('no_id', 'alvo_id', 'atributo', 'unidade'))
                    and p['regra_refs'] == [regra['id']]
                    and regra['clausula'] in p['evidencias']
                    and any(x['predicado'] == 'aplicabilidade_' + regra['id'] and x['estado'] == 'confirmada' for x in p['condicoes'])]
                if correspondentes:
                    criterio = 'manutencao_escopada_clausula_unica'
        resolucoes.append(dict(
            **deepcopy(registro),
            estado='resolvido_operacional_condicional' if correspondentes else 'pendente',
            propostas_refs=[p['id'] for p in correspondentes],
            criterio=criterio if correspondentes else None,
            suporte_semantico='nao_auditado',
        ))
    return resolucoes
