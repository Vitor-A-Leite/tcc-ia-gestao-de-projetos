"""Fechamento por dimensão, reconstruível a partir de catálogos e análises aceitas."""
from copy import deepcopy
from .contratos import hash_json
from .escopo import reconciliar


def fechar(*, nos, vistos, regras, novos, propostas, encaminhamentos, pendencias_tipadas, evento_id):
    pendencias = dict(prazo=[], custo=[])
    def registrar(motivo, dimensao='ambos'):
        # Uma lacuna temporal também pode alterar incidência monetária.
        for d in (('custo',) if dimensao == 'custo' else ('prazo', 'custo')):
            if motivo not in pendencias[d]:
                pendencias[d].append(motivo)
    if set(vistos) != set(nos):
        registrar('Cobertura operacional incompleta de nós: ' + ', '.join(sorted(set(nos) - set(vistos))))
    for r in regras:
        ps = [p for p in propostas if p['no_id'] == r['no_id']]
        if 'duracao' in r['atributos_alvo'] and not any(
                p['operacao'] in ('confirmar_manutencao_atributo', 'substituir_duracao')
                and p['alvo_id'] == r['no_id'] and r['id'] in p['regra_refs'] for p in ps):
            registrar('Regra local de duração sem resolução operacional: ' + r['id'])
        if 'readequacao' in r['atributos_alvo'] and not any(
                (p['operacao'] == 'confirmar_ausencia_parcela_adicional' and p['regra_refs'] == [r['id']])
                or (p['operacao'] == 'registrar_lacuna_custo' and r['id'] in p['regra_refs']
                    and p['alvo_id'] == 'lacuna_' + hash_json([evento_id, r['id'], 'readequacao'])[:16]) for p in ps):
            registrar('Regra local de custo sem resolução operacional: ' + r['id'], 'custo')
    cobertas = {p['alvo_id'] for p in propostas if p['operacao'] in ('adicionar_parcela', 'registrar_lacuna_custo')}
    if not set(novos) <= cobertas:
        registrar('Obrigação literal sem reconciliação final: ' + ', '.join(sorted(set(novos) - cobertas)), 'custo')
    resolucoes = reconciliar(encaminhamentos, propostas, regras)
    for item in resolucoes:
        if item['estado'] == 'pendente':
            pedido = item['encaminhamento']
            registrar('Encaminhamento não resolvido: ' + item['no_origem'] + ' -> ' + pedido['no_id'] + ' / ' + pedido['operacao'] + ' / ' + pedido['alvo_id'],
                      'custo' if pedido['unidade'] in ('BRL_centavo', 'contrato_temporal') else 'ambos')
    for item in pendencias_tipadas:
        registrar('Pendência operacional ' + item['no_id'] + ': ' + item['motivo'], item['dimensao'])
    todas = list(dict.fromkeys(pendencias['prazo'] + pendencias['custo']))
    return dict(estado='parcial' if todas else 'completo_operacional_condicional',
                nos_com_analise_operacional_valida=sorted(vistos), nos_exigidos=sorted(nos),
                obrigacoes_literais_novas_exigidas=sorted(novos), obrigacoes_reconciliadas=sorted(set(novos) & cobertas),
                pendencias=todas, pendencias_por_dimensao=pendencias,
                pendencias_tipadas=deepcopy(pendencias_tipadas), encaminhamentos=resolucoes,
                suporte_semantico='nao_auditado')
