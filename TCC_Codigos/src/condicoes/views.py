"""Views prospectivas positivas. Sem I/O, referências, seleção causal ou solver."""
from copy import deepcopy
import json
from interpretacao_no.contratos import hash_json


def projetar(obj, schema):
    """Schema fechado também em folhas: dicionário não atravessa campo escalar."""
    if isinstance(schema, dict):
        if not isinstance(obj, dict):
            raise ValueError('Objeto esperado')
        return {k: projetar(obj[k], v) for k, v in schema.items()}
    if isinstance(schema, list):
        if not isinstance(obj, list):
            raise ValueError('Lista esperada')
        return [projetar(v, schema[0]) for v in obj]
    if type(obj) is not schema:
        raise ValueError('Tipo de folha incompatível')
    return obj


REF = {'fonte_id': str, 'localizador': str}
FONTE = dict(id=str, documento_id=str, versao=str, localizador=str, trecho=str)
QUANTIDADE = dict(estado=str, valor=int, unidade=str, fonte_refs=[str])
RELACAO = dict(id=str, origem_id=str, destino_id=str, tipo=str, fonte_refs=[REF])
TRANSFERENCIA = dict(id=str, relacao_id=str, operacao=str, origem_atributo=str,
                     restricao_destino_id=str, fonte_refs=[REF])


def conferir_snapshot(base, fontes, grafo, vinculo):
    esperado = dict(base_hash=hash_json(base), grafo_hash=hash_json(grafo),
                    versao_base=base['versao_projeto'], versao_grafo=grafo['versao'])
    if vinculo != esperado:
        raise ValueError('Vínculo de normalização ausente/obsoleto')
    def refs(ids):
        return sorted(ids)
    def valor_base(q):
        return (q['estado'], q['valor'], q['unidade'], refs(q['fonte_refs']))
    def valor_grafo(q, unidade):
        return (q['estado'], q['valor'], q.get('unidade', unidade), refs(r['fonte_id'] for r in q['evidencias']))
    for k in ('projeto_id','moeda','marco_final_id'):
        if base[k] != grafo[k]: raise ValueError('Campo comum divergente '+k)
    for k in ('id','origem_label','unidade','indice_inicial'):
        if base['calendario'][k] != grafo['calendario'][k]: raise ValueError('Calendário divergente')
    bn={n['id']:n for n in base['entidades']}; gn={n['id']:n for n in grafo['entidades']}
    if len(bn)!=len(base['entidades']) or len(gn)!=len(grafo['entidades']) or bn.keys()!=gn.keys():
        raise ValueError('Entidades divergentes/duplicadas')
    for k,n in bn.items():
        g=gn[k]
        if any(n[a]!=g[a] for a in ('tipo','nome')) or refs(n['fonte_refs'])!=refs(r['fonte_id'] for r in g['fonte_refs']):
            raise ValueError('Catálogo comum divergente')
        if 'disponibilidade' in n['atributos']:
            q=g['atributos']['disponibilidade']
            if valor_base(n['atributos']['disponibilidade'])!=valor_grafo(q['conhecimento'],q['unidade']):
                raise ValueError('Disponibilidade divergente')
    ba={a['id']:a for a in base['atividades']}; ga={a['id']:a for a in grafo['atividades']}
    if ba.keys()!=ga.keys() or len(ga)!=len(grafo['atividades']): raise ValueError('Atividades divergentes')
    for k,a in ba.items():
        if valor_base(a['duracao'])!=valor_grafo(ga[k]['duracao'],'dia_corrido'): raise ValueError('Duração divergente')
        reais={r['id']:r for r in ga[k]['restricoes_liberacao'] if r['tipo']=='nao_antes'}
        if reais.keys()!={r['id'] for r in a['restricoes_contratuais']}: raise ValueError('Restrições comuns divergentes')
        for r in a['restricoes_contratuais']:
            rr=reais[r['id']]
            if rr['valor']['valor']!=r['valor_dia'] or rr['valor']['estado']!='exato' or refs(r['fonte_refs'])!=refs(x['fonte_id'] for x in rr['fonte_refs']):
                raise ValueError('Restrição comum divergente')
    bp={p['id']:p for p in base['parcelas_base']}; gp={p['id']:p for p in grafo['parcelas_base']}
    if bp.keys()!=gp.keys() or len(gp)!=len(grafo['parcelas_base']): raise ValueError('Parcelas divergentes')
    for k,p in bp.items():
        if any(p[a]!=gp[k][a] for a in ('escopo_id','descricao','valor_centavos','moeda')) or refs(p['fonte_refs'])!=refs(x['fonte_id'] for x in gp[k]['fonte_refs']):
            raise ValueError('Orçamento divergente')
    for bk,gk in (('fim_dia','fim'),('custo_centavos','custo_centavos')):
        q=grafo['linha_base'][gk]
        if q['estado']!='exato' or q['valor']!=base['linha_base_declarada'][bk]: raise ValueError('Baseline divergente')
    fs={f['id']:projetar(f,FONTE) for f in fontes if f['documento_id'] in set(base['documentos_comuns'])|set(base['documentos_relacionais'])}
    gs={f['id']:projetar(f,FONTE) for f in grafo['fontes']}
    if fs!=gs or len(gs)!=len(grafo['fontes']): raise ValueError('Fontes de snapshot divergentes')
    rels={r['id']:r for r in grafo['relacoes']}
    if len(rels)!=len(grafo['relacoes']): raise ValueError('Relação duplicada')
    for r in rels.values():
        if r['origem_id'] not in gn or r['destino_id'] not in gn or r['tipo'] not in ('fornece','requer','precede_FS','responsavel','pertence'):
            raise ValueError('Endpoint/tipo inválido')
        if r['tipo']=='precede_FS' and (type(r['lag_dias']) is not int or r['lag_dias']!=0): raise ValueError('FS inválida')
    for t in grafo['regras_transferencia']:
        if t['relacao_id'] not in rels or rels[t['relacao_id']]['tipo']!='requer': raise ValueError('Transferência inválida')
        r=rels[t['relacao_id']]
        if t['restricao_destino_id'] not in {x['id'] for x in ga[r['origem_id']]['restricoes_liberacao']}:
            raise ValueError('Restrição transferida inexistente')
    def referencias(obj):
        if isinstance(obj,dict):
            if 'fonte_id' in obj:
                if obj['fonte_id'] not in gs or obj['localizador']!=gs[obj['fonte_id']]['localizador']: raise ValueError('Referência relacional inválida')
            for v in obj.values(): referencias(v)
        elif isinstance(obj,list):
            for v in obj: referencias(v)
    referencias([grafo['relacoes'],grafo['regras_transferencia']])


def montar_views(base, evento, fontes, grafo, *, vinculo):
    """base pré-normalizada e grafo explicitamente vinculados, um único aviso.

    Aceita catálogo de fontes em memória; só documentos comuns + aviso corrente
    passam. Não usa metadados caso/família, seleções do H ou hashes de outputs.
    H é envelope de informação, NÃO substitui ContextoNo/Politica da etapa 6.
    """
    conferir_snapshot(base, fontes, grafo, vinculo)
    if (evento['projeto_id'] != base['projeto_id'] or evento['versao_projeto'] != base['versao_projeto']
            or grafo['projeto_id'] != base['projeto_id'] or evento['instante_observacao'] != 0
            or type(evento['instante_observacao']) is not int):
        raise ValueError('Identidade/instante incompatível')
    # Equivalência do snapshot é explícita, não assumida por semelhança de IDs.
    if {n['id'] for n in base['entidades']} != {n['id'] for n in grafo['entidades']}:
        raise ValueError('Catálogos divergentes')
    docs = set(base['documentos_comuns'])
    if set(evento['documentos_comuns_vigentes']) != docs or set(evento['documentos_relacionais_vigentes']) != set(base['documentos_relacionais']):
        raise ValueError('Vigência divergente')
    if evento['documento_evento_vigente'] in docs | set(base['documentos_relacionais']):
        raise ValueError('Aviso não isolado')
    fs = [projetar(f, FONTE) for f in fontes if f['documento_id'] in docs | {evento['documento_evento_vigente']}]
    if len({f['id'] for f in fs}) != len(fs) or {f['documento_id'] for f in fs} != docs | {evento['documento_evento_vigente']}:
        raise ValueError('Fontes ausentes/duplicadas')
    if {f['id'] for f in fs if f['documento_id'] == evento['documento_evento_vigente']} != set(evento['evidencia_ids']):
        raise ValueError('Aviso/evidência divergentes')
    comum = projetar(base, dict(projeto_id=str, versao_projeto=str, nome=str,
        calendario=dict(id=str, origem_label=str, unidade=str, indice_inicial=int, fonte_refs=[str]),
        moeda=str, unidade_monetaria=str, marco_final_id=str,
        linha_base_declarada=dict(fim_dia=int, custo_centavos=int, fonte_refs=[str]),
        parcelas_base=[dict(id=str, escopo_id=str, descricao=str, valor_centavos=int, moeda=str, fonte_refs=[str])]))
    comum['entidades'] = []
    for n in sorted(base['entidades'], key=lambda x: x['id']):
        novo = projetar(n, dict(id=str, tipo=str, nome=str, fonte_refs=[str]))
        novo['atributos'] = {k: projetar(n['atributos'][k], QUANTIDADE)
                             for k in ('disponibilidade',) if k in n['atributos']}
        comum['entidades'].append(novo)
    comum['atividades'] = [projetar(a, dict(id=str, entidade_id=str, duracao=QUANTIDADE,
        restricoes_contratuais=[dict(id=str, tipo=str, valor_dia=int, fonte_refs=[str])]))
        for a in sorted(base['atividades'], key=lambda x: x['id'])]
    comum['parcelas_base'].sort(key=lambda x: x['id'])
    comum['fontes'] = sorted(fs, key=lambda x: x['id'])
    comum['evento'] = projetar(evento, dict(evento_id=str, relato=str,
        origem=dict(autor=str, documento_id=str, data_registro=str), instante_observacao=int, escopo=str, lacunas=[str]))
    relacionais = sorted([projetar(f, FONTE) for f in fontes if f['documento_id'] in base['documentos_relacionais']], key=lambda x: x['id'])
    if {f['documento_id'] for f in relacionais} != set(base['documentos_relacionais']):
        raise ValueError('Fontes relacionais ausentes')
    rels = []
    for r in sorted(grafo['relacoes'], key=lambda x: x['id']):
        v = projetar(r, RELACAO)
        if r['tipo'] == 'precede_FS':
            v['lag_dias'] = projetar(r['lag_dias'], int)
        rels.append(v)
    exclusivos = dict(relacoes=rels,
        transferencias=[projetar(t, TRANSFERENCIA) for t in sorted(grafo['regras_transferencia'], key=lambda x: x['id'])],
        fontes=relacionais)
    # Texto neutro completo por registro, sem caminho crítico, relevância ou interpretação do aviso.
    texto = '\n'.join(f'{grupo}: '+json.dumps(v, sort_keys=True, ensure_ascii=False)
                      for grupo in ('relacoes', 'transferencias', 'fontes') for v in exclusivos[grupo])
    views = {}
    for condicao in ('B', 'H', 'T'):
        v = dict(schema_version='1.0-view', condicao=condicao, comum=deepcopy(comum))
        if condicao == 'H':
            v['relacional'] = deepcopy(exclusivos)
        elif condicao == 'T':
            v['relacoes_texto'] = texto
        v['view_hash'] = hash_json(v)
        views[condicao] = v
    return views


def auditar_equivalencia(views):
    hashes = {k: hash_json(v['comum']) for k, v in views.items()}
    esperado = '\n'.join(f'{g}: '+json.dumps(v, sort_keys=True, ensure_ascii=False)
                         for g in ('relacoes', 'transferencias', 'fontes') for v in views['H']['relacional'][g])
    if len(set(hashes.values())) != 1 or views['T']['relacoes_texto'] != esperado:
        raise ValueError('Fatos comuns ou relações divergentes')
    return dict(fatos_comuns_hash=hashes['B'], relacoes_completas=True,
                assimetrias=['B sem ficha relacional; fatos relacionais comuns preservados',
                'H: agenda local, política externa e motor; B/T: uma chamada global sem motor',
                'T tem relações em texto; H/T diferem também em decomposição e cálculo'])
