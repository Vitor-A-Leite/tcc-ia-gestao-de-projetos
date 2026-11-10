"""Contratos locais v1. Sem I/O, cálculo global ou leitura de referências."""
from copy import deepcopy
import hashlib
import json


class ContratoInvalido(ValueError):
    pass


def exigir(ok, mensagem):
    if not ok:
        raise ContratoInvalido(mensagem)


def hash_json(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def campos(obj, nomes):
    exigir(isinstance(obj, dict) and set(obj) == set(nomes.split()), 'Campos incompatíveis: ' + nomes)


def texto(v):
    exigir(isinstance(v, str) and bool(v.strip()), 'Texto obrigatório')


def numero(v, minimo=None):
    exigir(type(v) is int and (minimo is None or v >= minimo), 'Inteiro fora do domínio')


def lista(v):
    exigir(isinstance(v, list), 'Lista obrigatória')


def strings(v):
    lista(v)
    for x in v:
        texto(x)
    exigir(len(set(v)) == len(v), 'Identidades repetidas')


def selecionar(obj, nomes):
    return {k: deepcopy(obj[k]) for k in nomes.split()}


def fonte(f):
    return selecionar(f, 'id documento_id versao localizador trecho')


def refs(v, c, obrigatoria=True):
    lista(v)
    exigir(bool(v) or not obrigatoria, 'Evidência obrigatória')
    fontes = {f['id']: f for f in c['fontes']}
    for r in v:
        campos(r, 'fonte_id localizador')
        exigir(r['fonte_id'] in fontes and r['localizador'] == fontes[r['fonte_id']]['localizador'], 'Fonte invisível/localizador divergente')


def conhecimento(v, c, absoluto=False, minimo=None):
    campos(v, 'estado valor direcao evidencias lacunas motivo')
    strings(v['lacunas'])
    refs(v['evidencias'], c, False)
    exigir(v['motivo'] is None or isinstance(v['motivo'], str), 'Motivo inválido')
    estado = v['estado']
    if estado == 'exato':
        numero(v['valor'], minimo)
        exigir(not v['lacunas'] and v['evidencias'], 'Exato exige suporte sem lacuna')
        esperado = 'desconhecida' if absoluto else ('aumento' if v['valor'] > 0 else 'reducao' if v['valor'] < 0 else 'zero')
        exigir(v['direcao'] == esperado, 'Direção incompatível')
    else:
        exigir(v['valor'] is None, 'Desconhecimento não admite magnitude')
        if estado == 'direcao':
            exigir(v['direcao'] in ('aumento', 'reducao') and v['evidencias'] and v['lacunas'], 'Direção sem suporte/lacuna')
        elif estado == 'indeterminado':
            exigir(v['direcao'] == 'desconhecida' and v['lacunas'], 'Indeterminação exige lacuna')
        elif estado == 'inaplicavel':
            exigir(v['direcao'] == 'desconhecida' and not v['lacunas'] and v['motivo'], 'Inaplicabilidade exige motivo')
        else:
            raise ContratoInvalido('Estado inválido')


# Os únicos descritores habilitados nesta versão; ampliar requer revisão de contrato.
OPS = {
    'substituir_disponibilidade': ('disponibilidade', 'dia_corrido'),
    'substituir_duracao': ('duracao', 'dia_corrido'),
    'substituir_restricao': ('valor', 'dia_corrido'),
    'adicionar_parcela': ('valor_centavos', 'BRL_centavo'),
    'substituir_parcela': ('valor_centavos', 'BRL_centavo'),
    'registrar_lacuna_custo': ('valor_centavos', 'BRL_centavo'),
    'aplicar_regra_catalogada': ('parametros_contratuais', 'contrato_temporal'),
    'confirmar_manutencao_atributo': ('duracao', 'dia_corrido'),
    'confirmar_ausencia_parcela_adicional': ('readequacao', 'BRL_centavo'),
}


def montar_contexto(estado, evento, *, execucao_id, no_id, revisao,
                    fonte_ids, relacao_ids=(), regra_ids=(), predecessores=(),
                    obrigacoes=(), predicados=(), parcela_ids=()):
    """Projeção positiva explícita. Predecessores são fatos locais já selecionados.

    obrigacoes: IDs novos resolvidos externamente, nunca criados pela resposta LLM.
    Não agenda nós nem importa política manual/saídas do motor.
    """
    texto(execucao_id)
    numero(revisao, 1)
    exigir(evento['projeto_id'] == estado['projeto_id'] and evento['versao_projeto'] == estado['versao'], 'Snapshot/evento divergentes')
    exigir(evento['instante_observacao'] == 0, 'Somente evento prospectivo D0')
    entidades = {n['id']: n for n in estado['entidades']}
    exigir(no_id in entidades, 'Nó desconhecido')
    for seq in (fonte_ids, relacao_ids, regra_ids, obrigacoes, predicados, parcela_ids):
        strings(list(seq))
    fontes = {}
    for f in estado['fontes'] + evento['evidencias']:
        novo = fonte(f)
        exigir(f['id'] not in fontes or fontes[f['id']] == novo, 'Colisão de fonte')
        fontes[f['id']] = novo
    exigir(set(fonte_ids) <= fontes.keys(), 'Fonte selecionada inexistente')
    rels = {r['id']: r for r in estado['relacoes']}
    regras = {r['id']: r for grupo in ('regras_locais', 'regras_transferencia', 'regras_custo') for r in estado[grupo]}
    exigir(set(relacao_ids) <= rels.keys() and set(regra_ids) <= regras.keys(), 'Catálogo inexistente')
    # Fontes são copiadas como dados literais; nunca concatenadas ao papel de sistema.
    n = entidades[no_id]
    atributos = {}
    if 'disponibilidade' in n['atributos']:
        d = n['atributos']['disponibilidade']
        atributos['disponibilidade'] = selecionar(d, 'tipo unidade')
        exigir(d['tipo'] == 'inteiro' and d['unidade'] == 'dia_corrido', 'Tipo/unidade de disponibilidade inválidos')
        atributos['disponibilidade']['conhecimento'] = selecionar(d['conhecimento'], 'estado valor direcao evidencias lacunas motivo')
    atividade = next((a for a in estado['atividades'] if a['id'] == no_id), None)
    if atividade:
        atributos['duracao'] = selecionar(atividade['duracao'], 'estado valor direcao evidencias lacunas motivo')
    c = dict(schema_version='1.0-contexto-no', execucao_id=execucao_id,
             projeto_id=estado['projeto_id'], versao_projeto=estado['versao'],
             snapshot_hash=hash_json(estado), evento_id=evento['evento_id'], no_id=no_id,
             revisao=revisao, moeda='BRL', unidade_temporal='dia_corrido',
             no=dict(id=no_id, tipo=n['tipo'], nome=n['nome'], atributos=atributos),
             evento=selecionar(evento, 'evento_id relato origem instante_observacao escopo lacunas'),
             fontes=[fontes[k] for k in sorted(fonte_ids)],
             relacoes=[selecionar(rels[k], 'id origem_id destino_id tipo fonte_refs') for k in sorted(relacao_ids)],
             regras=[], predecessores=[], predecessores_versoes={},
             predicados=list(predicados), obrigacoes=list(obrigacoes), permissoes=[])
    for k in sorted(regra_ids):
        r = regras[k]
        if k in {x['id'] for x in estado['regras_locais']}:
            exigir(r['no_id'] == no_id, 'Regra local de outro nó')
            c['regras'].append(selecionar(r, 'id no_id clausula fonte_refs condicao_textual operacoes_permitidas atributos_alvo'))
        elif k in {x['id'] for x in estado['regras_transferencia']}:
            exigir(r['relacao_id'] in relacao_ids and rels[r['relacao_id']]['destino_id'] == no_id, 'Transferência fora do nó')
            c['regras'].append(selecionar(r, 'id relacao_id operacao origem_atributo restricao_destino_id fonte_refs'))
        else:
            fim = r['intervalo']['fim_ref']
            exigir(isinstance(fim, dict) and fim.get('atividade_id') == no_id, 'Contrato fora do nó proprietário')
            c['regras'].append(selecionar(r, 'id parcela_id taxa_centavos_dia unidade_taxa intervalo base_contratada_dias politica_reducao condicao fonte_refs'))
    for p in predecessores:
        campos(p, 'no_id revisao fatos fonte_refs')
        exigir(p['no_id'] in entidades and p['no_id'] != no_id, 'Predecessor inválido')
        numero(p['revisao'], 1)
        exigir(p['no_id'] not in c['predecessores_versoes'], 'Predecessor duplicado')
        # Fatos são passagens, não resultados calculados/analises/políticas serializadas.
        texto(p['fatos'])
        exigir(p['fatos'] in {f['trecho'] for f in c['fontes']}, 'Fato predecessor deve ser passagem visível literal')
        refs(p['fonte_refs'], c)
        c['predecessores'].append(deepcopy(p))
        c['predecessores_versoes'][p['no_id']] = p['revisao']
    c['evento']['origem'] = selecionar(evento['origem'], 'autor documento_id data_registro')
    def permitir(op, alvo, atributo, unidade):
        c['permissoes'].append(dict(operacao=op, alvo_id=alvo, atributo=atributo, unidade=unidade))
    if 'disponibilidade' in atributos:
        permitir('substituir_disponibilidade', no_id, 'disponibilidade', 'dia_corrido')
    c['restricoes'] = []
    c['proprietarios'] = {}
    if atividade and n['tipo'] == 'atividade':
        permitir('substituir_duracao', no_id, 'duracao', 'dia_corrido')
    for r in c['regras']:
        for op in r.get('operacoes_permitidas', []):
            if op in OPS:
                at, un = OPS[op]
                if at in r['atributos_alvo']:
                    permitir(op, no_id, at, un)
    if atividade:
        for r in atividade['restricoes_liberacao']:
            if r['tipo'] == 'nao_antes':
                rr = selecionar(r, 'id atividade_id tipo fonte_refs')
                rr['valor'] = selecionar(r['valor'], 'estado valor direcao evidencias lacunas motivo')
                c['restricoes'].append(rr)
                c['proprietarios'][r['id']] = no_id
                permitir('substituir_restricao', r['id'], 'valor', 'dia_corrido')
    parcelas = {p['id']: p for p in estado['parcelas_base']}
    exigir(set(parcela_ids) <= parcelas.keys(), 'Parcela inexistente')
    c['parcelas'] = [selecionar(parcelas[k], 'id escopo_id descricao valor_centavos moeda fonte_refs') for k in sorted(parcela_ids)]
    for k in parcela_ids:
        c['proprietarios'][k] = no_id
        exigir(k not in {r['parcela_id'] for r in estado['regras_custo']}, 'Parcela temporal exige regra catalogada')
        permitir('substituir_parcela', k, 'valor_centavos', 'BRL_centavo')
    for r in c['regras']:
        if 'parcela_id' in r:
            c['proprietarios'][r['id']] = no_id
            r['intervalo'] = {k: selecionar(v, 'atividade_id atributo') if isinstance(v, dict) else v for k, v in selecionar(r['intervalo'], 'inicio_ref fim_ref').items()}
            for v in r['intervalo'].values():
                exigir(v == 'D0' or (isinstance(v, dict) and v['atividade_id'] in entidades and v['atributo'] in ('inicio', 'fim')), 'Referência temporal inválida')
            permitir('aplicar_regra_catalogada', r['id'], 'parametros_contratuais', 'contrato_temporal')
    for ob in obrigacoes:
        exigir(ob not in entidades and ob not in {p['id'] for p in estado['parcelas_base']}, 'Colisão de obrigação')
        for op in ('adicionar_parcela', 'registrar_lacuna_custo'):
            permitir(op, ob, 'valor_centavos', 'BRL_centavo')
    for chave in ('evento_id', 'relato', 'escopo'):
        texto(c['evento'][chave])
    strings(c['evento']['lacunas'])
    for v in c['evento']['origem'].values():
        texto(v)
    for v in (c['no']['id'], c['no']['tipo'], c['no']['nome']):
        texto(v)
    for f in c['fontes']:
        for v in f.values():
            texto(v)
    for r in c['relacoes']:
        for k in ('id', 'origem_id', 'destino_id', 'tipo'):
            texto(r[k])
    for r in c['regras']:
        if 'parcela_id' in r:
            texto(r['condicao'])
            numero(r['base_contratada_dias'], 0)
            if r['taxa_centavos_dia'] is not None:
                numero(r['taxa_centavos_dia'], 0)
            exigir(r['unidade_taxa'] == 'BRL_centavo/dia_corrido' and r['politica_reducao'] in ('sem_credito', 'recalculavel_com_credito'), 'Contrato temporal inválido')
        if 'condicao_textual' in r:
            texto(r['condicao_textual'])
            strings(r['operacoes_permitidas'])
            strings(r['atributos_alvo'])
    for atributo, v in atributos.items():
        conhecimento(v['conhecimento'] if atributo == 'disponibilidade' else v, c, absoluto=True, minimo=0)
    for r in c['restricoes']:
        conhecimento(r['valor'], c, absoluto=True, minimo=0)
    # Valida todas as referências estruturadas selecionadas, sem interpretar texto.
    def conferir(v):
        if isinstance(v, dict):
            if 'fonte_id' in v:
                refs([v], c)
            for x in v.values():
                conferir(x)
        elif isinstance(v, list):
            for x in v:
                conferir(x)
    conferir(c)
    c['contexto_hash'] = hash_json(c)
    return c


def validar(a, c):
    """Estrutura/proveniência apenas. Todas as propostas requerem revisão semântica."""
    exigir(c['contexto_hash'] == hash_json({k: v for k, v in c.items() if k != 'contexto_hash'}), 'Contexto adulterado')
    campos(a, 'schema_version analise_id execucao_id evento_id no_id revisao contexto_hash predecessores_versoes avaliacao propostas justificativa lacunas')
    exigir(a['schema_version'] == '1.0-proposta', 'Versão de análise inválida')
    texto(a['analise_id'])
    for k in ('execucao_id', 'evento_id', 'no_id', 'revisao', 'contexto_hash', 'predecessores_versoes'):
        exigir(a[k] == c[k] and type(a[k]) is type(c[k]), 'Identidade/revisão divergente: ' + k)
    exigir(isinstance(a['predecessores_versoes'], dict), 'Mapa de revisões obrigatório')
    for revisao in a['predecessores_versoes'].values():
        numero(revisao, 1)
    campos(a['avaliacao'], 'prazo custo')
    for v in a['avaliacao'].values():
        conhecimento(v, c)
    texto(a['justificativa'])
    strings(a['lacunas'])
    lista(a['propostas'])
    ids, escritas, decisoes = set(), set(), []
    for p in a['propostas']:
        campos(p, 'id operacao alvo_id atributo valor unidade evidencias relacao_refs regra_refs condicoes origens_causais no_id')
        texto(p['id'])
        exigir(p['id'] not in ids, 'Proposta duplicada')
        ids.add(p['id'])
        exigir(p['no_id'] == c['no_id'], 'Proposta de outro nó')
        d = selecionar(p, 'operacao alvo_id atributo unidade')
        exigir(d in c['permissoes'], 'Operação/alvo/unidade fora de catálogo: requer_revisao')
        chave = (p['alvo_id'], p['atributo'])
        exigir(chave not in escritas, 'Escritas conflitantes')
        escritas.add(chave)
        refs(p['evidencias'], c)
        for k, catalogo in (('regra_refs', c['regras']), ('relacao_refs', c['relacoes'])):
            strings(p[k])
            exigir(set(p[k]) <= {x['id'] for x in catalogo}, 'Referência de catálogo invisível')
        lista(p['condicoes'])
        for cond in p['condicoes']:
            campos(cond, 'predicado estado evidencias')
            exigir(cond['predicado'] in c['predicados'] and cond['estado'] in ('confirmada', 'nao_confirmada', 'indeterminada'), 'Condição fora de catálogo')
            refs(cond['evidencias'], c)
        lista(p['origens_causais'])
        exigir(p['origens_causais'], 'Origem obrigatória')
        canonico = hash_json([c['evento_id'], p['alvo_id']])
        for o in p['origens_causais']:
            campos(o, 'evento_id fato_ref efeito_id')
            exigir(o['evento_id'] == c['evento_id'] and o['efeito_id'] == canonico, 'Origem/efeito não canônico')
            refs([o['fato_ref']], c)
            exigir(o['fato_ref'] in p['evidencias'], 'Origem sem evidência da proposta')
        op = p['operacao']
        if op.startswith('confirmar_'):
            regras = [r for r in c['regras'] if r['id'] in p['regra_refs'] and r.get('no_id') == c['no_id'] and op in r.get('operacoes_permitidas', []) and p['atributo'] in r.get('atributos_alvo', [])]
            exigir(regras and p['condicoes'] and all(x['estado'] == 'confirmada' for x in p['condicoes']), 'Confirmação sem condição/regra resolvida')
            numero(p['valor'], 0)
            esperado = 0 if op == 'confirmar_ausencia_parcela_adicional' else c['no']['atributos']['duracao']['valor']
            exigir(p['valor'] == esperado, 'Confirmação divergente')
            if op == 'confirmar_ausencia_parcela_adicional':
                exigir(a['avaliacao']['custo']['estado'] == 'exato' and a['avaliacao']['custo']['valor'] == 0, 'Ausência exige zero local sustentado')
        elif op == 'aplicar_regra_catalogada':
            exigir(p['alvo_id'] in p['regra_refs'], 'Aditivo sem regra')
            v = p['valor']
            exigir(isinstance(v, dict) and v and set(v) <= {'taxa_centavos_dia', 'base_contratada_dias', 'politica_reducao'}, 'Aditivo fora de catálogo')
            for k, x in v.items():
                if k == 'politica_reducao':
                    exigir(x in ('sem_credito', 'recalculavel_com_credito'), 'Política inválida')
                elif k != 'taxa_centavos_dia' or x is not None:
                    numero(x, 0)
        else:
            conhecimento(p['valor'], c, absoluto=True, minimo=0)
            exigir(p['valor']['estado'] != 'inaplicavel', 'Atributo quantitativo obrigatório')
            if op == 'registrar_lacuna_custo':
                exigir(p['valor']['estado'] != 'exato', 'Lacuna não é preço exato')
        decisoes.append(dict(proposta_id=p['id'], status='requer_revisao',
                             efeito_id=canonico, estrutura='valida', suporte_semantico='nao_auditado',
                             motivos=['Citação visível não prova suporte semântico; nenhuma aplicação autorizada']))
    return deepcopy(decisoes)
