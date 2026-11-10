"""Projeção reversível do pedido HTTP; contexto canônico e parser preservados."""
from collections import Counter
from copy import deepcopy
import json

VERSAO = '1-contexto-compacto'
INSTRUCOES = '''
Representação de entrada contexto-compacto v1:
Um objeto {"conjunto_evidencias_ref": ID} no lugar de uma lista referencia
exatamente a lista catalogada em conjuntos_evidencias[ID], na mesma ordem.
contrato_resposta.responsabilidades_operacionais_ref aponta para o catálogo
único em contexto.responsabilidades_operacionais. Essas referências são apenas
abreviações da entrada; na resposta continue usando pares fonte_id/localizador.
contexto.alteracoes_incorporadas registra propostas já incorporadas nesta passagem
operacional, não fatos certificados por auditoria semântica. Confira evento, alvo,
atributo, valor e evidências. Não encaminhe novamente uma operação já incorporada
para o mesmo fato. Encaminhe apenas operações ainda não resolvidas ou fatos novos;
para fato novo/conflitante, cite a evidência específica e explique a diferença no motivo.
Datas em entradas_correntes são efeitos calculados pelas dependências, não novas
restrições locais. Só proponha mudança local com evidência específica desse atributo.
'''


def compactar(dados):
    """Interna listas idênticas repetidas; não elimina evidências nem muda sua ordem."""
    d = deepcopy(dados)
    rotas = d['contrato_resposta'].get('responsabilidades_operacionais')
    if rotas == d['contexto']['responsabilidades_operacionais']:
        del d['contrato_resposta']['responsabilidades_operacionais']
        d['contrato_resposta']['responsabilidades_operacionais_ref'] = 'contexto.responsabilidades_operacionais'
    def chave(v):
        return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    def lista_refs(v):
        return isinstance(v, list) and bool(v) and all(isinstance(x, dict) and set(x) == {'fonte_id', 'localizador'} for x in v)
    contagens = Counter()
    def contar(v):
        if lista_refs(v):
            contagens[chave(v)] += 1
        elif isinstance(v, dict):
            for x in v.values(): contar(x)
        elif isinstance(v, list):
            for x in v: contar(x)
    contar(d)
    ids = {k: 'EV' + str(i) for i, k in enumerate(sorted(k for k, n in contagens.items() if n > 1), 1)}
    def substituir(v):
        if lista_refs(v) and chave(v) in ids:
            return {'conjunto_evidencias_ref': ids[chave(v)]}
        if isinstance(v, dict): return {k: substituir(x) for k, x in v.items()}
        if isinstance(v, list): return [substituir(x) for x in v]
        return v
    d = substituir(d)
    d['representacao_entrada'] = VERSAO
    d['conjuntos_evidencias'] = {ident: json.loads(k) for k, ident in ids.items()}
    return d


def expandir(dados):
    """Reconstrói integralmente o pedido lógico para auditoria offline."""
    d = deepcopy(dados)
    if d.pop('representacao_entrada') != VERSAO:
        raise ValueError('Representação desconhecida')
    catalogo = d.pop('conjuntos_evidencias')
    def restaurar(v):
        if isinstance(v, dict):
            if set(v) == {'conjunto_evidencias_ref'}:
                return deepcopy(catalogo[v['conjunto_evidencias_ref']])
            return {k: restaurar(x) for k, x in v.items()}
        if isinstance(v, list): return [restaurar(x) for x in v]
        return v
    d = restaurar(d)
    contrato = d['contrato_resposta']
    if 'responsabilidades_operacionais_ref' in contrato:
        if contrato.pop('responsabilidades_operacionais_ref') != 'contexto.responsabilidades_operacionais':
            raise ValueError('Referência de responsabilidades inválida')
        contrato['responsabilidades_operacionais'] = deepcopy(d['contexto']['responsabilidades_operacionais'])
    return d


def registrar_incorporadas(propostas, evento_id):
    """Somente propostas aceitas e aplicadas pelo orquestrador, nunca encaminhamentos."""
    return [dict(evento_id=evento_id, proposta_id=p['id'],
                 **{k: deepcopy(p[k]) for k in ('no_id', 'operacao', 'alvo_id', 'atributo', 'unidade', 'valor', 'evidencias')},
                 estado='incorporada_operacionalmente', suporte_semantico='nao_auditado')
            for p in propostas]
