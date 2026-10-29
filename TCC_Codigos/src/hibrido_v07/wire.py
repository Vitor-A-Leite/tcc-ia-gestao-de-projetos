"""Resposta sem identidade repetida: o adaptador vincula conteúdo ao pedido atual.

Nenhuma resposta histórica é reparada. O novo contrato recusa campos técnicos e
direções redundantes; a representação interna mantém a validação estrita.
"""
from copy import deepcopy
from .contratos import SCHEMA, validar, campos, exigir, numero, hash_json

WIRE = '1.0-resposta-h07'
IDENTIDADES = ('execucao_id', 'evento_id', 'no_id', 'revisao', 'contexto_hash', 'predecessores_versoes')
CAMPOS = 'schema_version avaliacao propostas justificativa lacunas pendencias_operacionais encaminhamentos resolucoes_regras'


def quantidade(q, *, absoluto=False):
    exigir(isinstance(q, dict), 'Conhecimento deve ser objeto')
    campos(q, 'estado valor evidencias lacunas motivo' + (' direcao' if q.get('estado') == 'direcao' else ''))
    v = deepcopy(q)
    if q['estado'] == 'exato':
        numero(q['valor'], 0 if absoluto else None)
        v['direcao'] = 'desconhecida' if absoluto else ('aumento' if q['valor'] > 0 else 'reducao' if q['valor'] < 0 else 'zero')
    elif q['estado'] != 'direcao':
        v['direcao'] = 'desconhecida'
    return v


def incorporar(w, c):
    campos(w, CAMPOS)
    exigir(w['schema_version'] == WIRE, 'Resposta wire H07 obrigatória')
    exigir(c['contexto_hash'] == hash_json({k: v for k, v in c.items() if k != 'contexto_hash'}), 'Contexto adulterado')
    a = {k: deepcopy(c[k]) for k in IDENTIDADES}
    a.update(schema_version=SCHEMA, analise_id=c['no_id'] + ':r' + str(c['revisao']) + ':' + c['contexto_hash'][:16])
    for k in ('justificativa', 'lacunas', 'pendencias_operacionais', 'encaminhamentos', 'resolucoes_regras'):
        a[k] = deepcopy(w[k])
    campos(w['avaliacao'], 'prazo custo')
    a['avaliacao'] = {k: quantidade(v) for k, v in w['avaliacao'].items()}
    exigir(isinstance(w['propostas'], list), 'Propostas devem ser lista')
    a['propostas'] = []
    for i, p in enumerate(w['propostas'], 1):
        campos(p, 'operacao alvo_id atributo valor unidade evidencias relacao_refs regra_refs condicoes origem_ref')
        q = {k: deepcopy(v) for k, v in p.items() if k != 'origem_ref'}
        q.update(id=c['no_id'] + ':r' + str(c['revisao']) + ':p' + str(i), no_id=c['no_id'],
                 origens_causais=[dict(evento_id=c['evento_id'], fato_ref=deepcopy(p['origem_ref']), efeito_id=hash_json([c['evento_id'], p['alvo_id']]))])
        if not p['operacao'].startswith('confirmar_') and p['operacao'] != 'aplicar_regra_catalogada':
            q['valor'] = quantidade(p['valor'], absoluto=True)
        a['propostas'].append(q)
    validar(a, c)
    return a


def conferir_vinculo(a, c):
    e = a['execucao']
    exigir(e.get('wire_schema') == WIRE and e.get('vinculo_contexto_hash') == c['contexto_hash'], 'Vínculo do adaptador divergente')
    exigir(hash_json(e['resposta_wire']) == e.get('resposta_wire_hash'), 'Resposta wire adulterada')
    if e.get('origem') != 'simulado':
        from interpretacao_no.adaptadores import _json
        exigir(len(e['tentativas']) == 1 and _json(e['tentativas'][0]['resposta_bruta']) == e['resposta_wire'], 'Resposta wire não corresponde ao conteúdo bruto')
    exigir(incorporar(e['resposta_wire'], c) == {k: v for k, v in a.items() if k not in ('execucao', 'decisoes')}, 'Conteúdo não corresponde à resposta wire vinculada')
