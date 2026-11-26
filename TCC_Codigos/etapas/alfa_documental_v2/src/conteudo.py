"""Revisão do conteúdo documental: o que cada documento afirma × estado calculado.

As afirmações chegam prontas (cadastro manual, referência ou extração por IA já
validada em `extracao`). Este módulo apenas confronta cada uma com o resultado do
cálculo, atribui estado e motivo tipados e explica o porquê pelo caminho
determinante no grafo. Não altera documentos, não cria ações, riscos ou decisões
e não converte informação indeterminada em zero ou em desatualização.
"""
from copy import deepcopy
import json
import re

from . import DATA
from .vendor.interpretacao_no.contratos import hash_json

VERSAO = '1-revisao-conteudo'
PREDICADOS = ('valor', 'sem_alteracao', 'no_prazo', 'dentro_orcamento', 'critico',
              'versao', 'compromisso', 'risco', 'decisao', 'intervalo')
PREDICADOS_COMPARAVEIS = ('valor', 'no_prazo', 'dentro_orcamento', 'critico', 'versao')
ESTADOS = ('revisar', 'ja_atualizado', 'nao_verificavel', 'julgamento_humano', 'preservar')
MOTIVOS = ('valor_divergente', 'premissa_alterada', 'magnitude_sem_suporte', 'certeza_sem_suporte',
           'referencia_obsoleta', 'afirmacao_conflitante', 'confirmado', 'execucao_incompleta',
           'sem_estado_calculado', 'evento_relacionado', 'registro_historico')
CAMPOS_TEMPO = ('inicio', 'fim')
LIMITE_CAMINHOS = 8
CORPUS = DATA/'conteudo'/'documentos_prosa.json'
ESTADOS_CAMINHO = ('transmitido', 'indeterminado')
ESTADOS_ABSORCAO = ('absorvido_ou_dominado', 'dominado_na_convergencia')


# ---------------------------------------------------------------- corpus

def carregar_corpus():
    return json.loads(CORPUS.read_text())


def documento_prosa(corpus, documento_id, versao):
    for d in corpus['documentos']:
        if d['id'] == documento_id and d['versao'] == versao:
            return d
    raise KeyError(f'{documento_id}@{versao} ausente do corpus')


def documentos_do_cenario(cenario, corpus=None):
    """Versões em prosa vigentes no cenário: Status Report do registro vigente e demais artefatos."""
    corpus = corpus or carregar_corpus()
    vigente = cenario['registro_vigente']
    alvo = corpus['vinculo_cenarios']['status_report'].get(f"{vigente['id']}@{vigente['versao']}")
    if alvo is None:
        raise KeyError('Registro vigente sem versão em prosa cadastrada')
    chaves = [alvo]+list(corpus['vinculo_cenarios']['outros'])
    return [documento_prosa(corpus, *c.split('@', 1)) for c in chaves]


def extracoes_referencia(cenario):
    """Condição C: afirmações de referência dos documentos em prosa do cenário.

    Ficam em `avaliacao/` porque também são o gabarito da extração por IA; nunca
    entram no pedido do extrator.
    """
    from . import ROOT
    ref = json.loads((ROOT/'avaliacao/referencias/conteudo/afirmacoes_referencia.json').read_text())
    idx = {(e['documento_id'], e['versao']): e for e in ref['extracoes']}
    return [idx[(d['id'], d['versao'])] for d in documentos_do_cenario(cenario)]


def afirmacoes_cadastro(cenario):
    """Condição A: as afirmações estruturadas à mão no registro vigente, no formato comum."""
    s = cenario['registro_vigente']
    afs = []
    for t in s['trechos']:
        a = t.get('afirmacao')
        if not a:
            continue
        afs.append(dict(id=f"{t['id']}#1", documento_id=s['id'], versao=s['versao'], trecho_id=t['id'],
                        citacao=t['texto'], predicado='versao' if a['campo'] == 'versao' else 'valor',
                        entidades=[a['entidade']], campo=a['campo'], valor=a['valor'], unidade=a['unidade'],
                        conhecimento='exato' if a['valor'] is not None else 'indeterminado',
                        referencia_temporal='absoluta', registro=None,
                        justificativa='Afirmação cadastrada manualmente no registro vigente.'))
    return [dict(documento_id=s['id'], versao=s['versao'], afirmacoes=afs, nao_mapeados=[])]


# ---------------------------------------------------------------- leitura do resultado

def _nos(result):
    return {n['no_id']: n for n in result.get('resultados_nos', [])}


def _quantidade(valor, estado='exato'):
    return dict(estado=estado if valor is not None else 'indeterminado', valor=valor)


def folgas_projetadas(result):
    """Folga total no cronograma projetado: fim mais tarde − fim cedo, recuando do marco final.

    Usa as datas projetadas e as relações temporais da propagação. Nó cuja folga
    depende de data indeterminada recebe None.
    """
    proj = result.get('estado_projetado_nos', {})
    suc = {}
    for e in _arestas(result):
        suc.setdefault(e['origem'], []).append(e['destino'])
    fim = {n: (d.get('fim') or {}).get('valor') for n, d in proj.items()}
    ini = {n: (d.get('inicio') or {}).get('valor') for n, d in proj.items()}
    tarde = {}
    pendentes = set(proj)
    while pendentes:
        progresso = False
        for n in list(pendentes):
            filhos = suc.get(n, [])
            if any(f in pendentes for f in filhos):
                continue
            if not filhos:
                tarde[n] = fim[n]
            else:
                inicios_tarde = []
                for f in filhos:
                    dur = None if tarde.get(f) is None or fim[f] is None or ini[f] is None else fim[f]-ini[f]
                    inicios_tarde.append(None if dur is None else tarde[f]-dur)
                tarde[n] = None if any(x is None for x in inicios_tarde) else min(inicios_tarde)
            pendentes.discard(n); progresso = True
        if not progresso:
            break
    return {n: (None if tarde.get(n) is None or fim[n] is None else tarde[n]-fim[n]) for n in proj}


def _parcela(result, pid):
    return next((p for p in result.get('livro_parcelas', []) if p['parcela_id'] == pid), None)


def _calculado(result, entidade, campo):
    """Mesma leitura de `documentos.verificar`, para que a condição A reproduza o estado atual."""
    if campo == 'custo' and entidade == 'PROJECT':
        return deepcopy(result.get('custo_novo'))
    if campo == 'custo' and _parcela(result, entidade):
        return deepcopy(_parcela(result, entidade)['novo'])
    if entidade == 'M_RELEASE' and campo == 'fim':
        return deepcopy(result.get('fim_novo'))
    if campo == 'folga':
        if entidade not in result.get('estado_projetado_nos', {}):
            return None
        return _quantidade(folgas_projetadas(result).get(entidade))
    if campo == 'duracao':
        n = _nos(result).get(entidade)
        if n is None or n.get('processamento') in ('bloqueado', 'nao_avaliado'):
            return None
        i, f = (n.get('inicio') or {}).get('valor'), (n.get('fim') or {}).get('valor')
        return _quantidade(None if i is None or f is None else f-i)
    n = _nos(result).get(entidade, {})
    q = deepcopy(n.get(campo, n.get('quantitativo', {}).get(campo)))
    if n.get('processamento') in ('bloqueado', 'nao_avaliado'):
        return None
    return q


def _base(result, entidade, campo):
    if campo == 'custo' and entidade == 'PROJECT':
        return result['custo_base'].get('valor')
    if entidade == 'M_RELEASE' and campo == 'fim':
        return result['fim_base'].get('valor')
    return result['baseline_nos'].get(entidade, {}).get(campo, {}).get('valor')


def _projetado(result, entidade, campo):
    return result.get('estado_projetado_nos', {}).get(entidade, {}).get(campo)


def _pendente(result):
    return bool(result.get('pendencias_execucao'))


def _arestas(result):
    return result.get('propagacao', [])


def _descendentes(result, no):
    filhos = {}
    for e in _arestas(result):
        filhos.setdefault(e['origem'], []).append(e['destino'])
    vistos, pilha = set(), [no]
    while pilha:
        for f in filhos.get(pilha.pop(), []):
            if f not in vistos:
                vistos.add(f); pilha.append(f)
    return vistos


def _ascendentes(result, no):
    pais = {}
    for e in _arestas(result):
        pais.setdefault(e['destino'], []).append(e['origem'])
    vistos, pilha = set(), [no]
    while pilha:
        for p in pais.get(pilha.pop(), []):
            if p not in vistos:
                vistos.add(p); pilha.append(p)
    return vistos


def criticos(result):
    """Nós do caminho crítico projetado: fecho para trás a partir do marco final
    pelas relações em que o fim da origem determina o início do destino."""
    pais = {}
    for e in _arestas(result):
        fo, idd = e['fim_origem'], e['inicio_destino']
        if fo.get('estado') == 'exato' and idd.get('estado') == 'exato' and fo['valor'] == idd['valor']:
            pais.setdefault(e['destino'], []).append(e['origem'])
    vistos, pilha = {'M_RELEASE'}, ['M_RELEASE']
    while pilha:
        for p in pais.get(pilha.pop(), []):
            if p not in vistos:
                vistos.add(p); pilha.append(p)
    return vistos


# ---------------------------------------------------------------- explicação rastreável

def caminhos(result, alvo, origens):
    """Caminhos determinantes da mudança até `alvo`, da origem para o alvo."""
    if alvo not in result.get('nos_com_mudanca_prazo', []):
        return []
    entrantes = {}
    for e in _arestas(result):
        if e['estado'] not in ESTADOS_CAMINHO:
            continue
        if e['estado'] == 'transmitido' and e['fim_origem'].get('valor') != e['inicio_destino'].get('valor'):
            continue
        entrantes.setdefault(e['destino'], []).append(e)
    achados = []

    def andar(no, trilha, arestas):
        if len(achados) >= LIMITE_CAMINHOS:
            return
        if no in origens or not entrantes.get(no):
            achados.append((list(reversed(trilha)), list(reversed(arestas))))
            return
        for e in entrantes[no]:
            if e['origem'] not in trilha:
                andar(e['origem'], trilha+[e['origem']], arestas+[e])

    andar(alvo, [alvo], [])
    saida = []
    for nos, arestas in achados:
        if nos[0] not in origens:
            continue
        saida.append(dict(
            nos=[dict(no=n, fim_base=_base_no(result, n), fim_novo=(_projetado(result, n, 'fim') or {}).get('valor'),
                      conhecimento=(_projetado(result, n, 'fim') or {}).get('estado')) for n in nos],
            relacoes=[e['relacao_id'] for e in arestas],
            fonte_refs=[r for e in arestas for r in e.get('fonte_refs', [])]))
    return saida


def _base_no(result, n):
    return result['baseline_nos'].get(n, {}).get('fim', {}).get('valor')


def absorcoes(result, alvo):
    """Relações em que uma mudança deixou de se propagar em direção ao alvo."""
    relevantes = _ascendentes(result, alvo) | {alvo}
    mudados = set(result.get('nos_com_mudanca_prazo', []))
    return [dict(relacao_id=e['relacao_id'], origem=e['origem'], destino=e['destino'], estado=e['estado'],
                 fonte_refs=deepcopy(e.get('fonte_refs', [])))
            for e in _arestas(result)
            if e['estado'] in ESTADOS_ABSORCAO and e['origem'] in mudados and e['destino'] in relevantes]


def efeitos_custo(result):
    return [dict(parcela_id=p['parcela_id'], proprietario=p['proprietario'], regra_id=p.get('regra_id'),
                 delta=p['delta'].get('valor'), conhecimento=p['delta'].get('estado'),
                 fonte_refs=deepcopy(p.get('fonte_refs', [])))
            for p in result.get('efeitos_financeiros', [])]


def _texto_caminho(c):
    def rot(n):
        if n['conhecimento'] != 'exato':
            return f"{n['no']} ({n['fim_base']} → indeterminado)"
        return f"{n['no']} ({n['fim_base']} → {n['fim_novo']})"
    nos = c['nos']
    if len(nos) == 1:
        return rot(nos[0])
    meio = [n['no'] for n in nos[1:-1]]
    return ' → '.join([rot(nos[0])]+meio+[rot(nos[-1])])


def explicar(result, cenario, alvos, *, custo=False, contendo=None):
    origens = set(cenario['entidades_mencionadas'])
    doc = cenario['documento']
    mudanca = [dict(documento_id=doc['id'], versao=doc['versao'], trecho_id=t['id'],
                    localizador=t['localizador'], texto=t['texto']) for t in doc['trechos']]
    cams, abs_ = [], []
    for a in alvos:
        cams += caminhos(result, a, origens)
        abs_ += absorcoes(result, a)
    efs = efeitos_custo(result) if custo else []
    if custo:
        for ef in efs:
            if ef['proprietario'] not in alvos:
                cams += caminhos(result, ef['proprietario'], origens)
    vistos, unicos = set(), []
    for c in cams:
        k = tuple(c['relacoes']) + tuple(n['no'] for n in c['nos'])
        if k not in vistos and (contendo is None or any(n['no'] == contendo for n in c['nos'])):
            vistos.add(k); unicos.append(c)
    partes = [f"{m['documento_id']} {m['localizador']}" for m in mudanca]
    # Ramos paralelos com mesma origem e mesmo alvo: mostrar um e resumir os demais.
    grupos = {}
    for c in unicos:
        grupos.setdefault((c['nos'][0]['no'], c['nos'][-1]['no']), []).append(c)
    linhas = []
    for g in grupos.values():
        linha = f"{' e '.join(partes)}: " + _texto_caminho(g[0])
        if len(g) > 1:
            primeiro = {n['no'] for n in g[0]['nos']}
            via = sorted({n['no'] for c in g[1:] for n in c['nos']} - primeiro)
            linha += f" (mais {len(g)-1} ramo(s) paralelo(s)" + (f" via {', '.join(via)})" if via else ')')
        linhas.append(linha+'.')
    for ef in efs:
        delta = 'indeterminado' if ef['conhecimento'] != 'exato' else ('+' if ef['delta'] >= 0 else '−')+_brl(abs(ef['delta']))
        linhas.append(f"Parcela {ef['parcela_id']} ({ef['proprietario']}): {delta}.")
    if not unicos and abs_:
        linhas.append('Mudança absorvida antes de chegar ao alvo: ' +
                      ', '.join(f"{x['relacao_id']} {x['origem']}→{x['destino']} ({x['estado']})" for x in abs_[:4]) + '.')
    refs = [dict(fonte_id=m['trecho_id'], localizador=m['localizador']) for m in mudanca]
    refs += [r for c in unicos for r in c['fonte_refs']] + [r for ef in efs for r in ef['fonte_refs']]
    if not unicos:
        refs += [r for x in abs_ for r in x['fonte_refs']]
    refs = list({(r['fonte_id'], r['localizador']): r for r in refs}.values())
    return dict(mudanca=mudanca, caminhos=unicos, absorcoes=abs_, efeitos_custo=efs,
                texto=' '.join(linhas) if linhas else 'Nenhuma alteração calculada alcança as entidades afirmadas.',
                evidencias=refs)


# ---------------------------------------------------------------- avaliação por predicado

def _veredito_booleano(afirmado, verdade, result):
    if verdade == 'nv':
        return 'nao_verificavel', 'sem_estado_calculado'
    if verdade is None:
        return ('nao_verificavel', 'execucao_incompleta') if _pendente(result) else ('revisar', 'certeza_sem_suporte')
    return ('ja_atualizado', 'confirmado') if verdade == afirmado else ('revisar', 'premissa_alterada')


def _comparar_limite(q, base):
    """True/False quando o estado (ou seus limites) decide `q <= base`; None se não decide."""
    if q is None or base is None:
        return 'nv'
    if q.get('estado') == 'exato':
        return q['valor'] <= base
    lim = q.get('limites') or {}
    if lim.get('inferior') is not None and lim['inferior'] > base:
        return False
    if lim.get('superior') is not None and lim['superior'] <= base:
        return True
    return None


def _avaliar_valor(a, result):
    e, campo = a['entidades'][0], a['campo']
    q = _calculado(result, e, campo)
    if q is None:
        return 'nao_verificavel', 'sem_estado_calculado', None
    faixa = a.get('conhecimento') == 'faixa' and a.get('limites')
    if q['estado'] == 'exato':
        if faixa:
            dentro = a['limites']['minimo'] <= q['valor'] <= a['limites']['maximo']
            return ('ja_atualizado', 'confirmado', q) if dentro else ('revisar', 'valor_divergente', q)
        igual = a['conhecimento'] == 'exato' and q['valor'] == a['valor']
        return ('ja_atualizado', 'confirmado', q) if igual else ('revisar', 'valor_divergente', q)
    if _pendente(result):
        return 'nao_verificavel', 'execucao_incompleta', q
    if a['valor'] is None and not faixa:
        return 'ja_atualizado', 'confirmado', q
    return 'revisar', 'magnitude_sem_suporte', q


def _avaliar_sem_alteracao(a, result):
    mudadas, incertas, sem_estado = [], [], []
    for e in a['entidades']:
        if a['campo'] in CAMPOS_TEMPO:
            p = _projetado(result, e, a['campo'])
            if p is None:
                sem_estado.append(e); continue
            if e in result.get('nos_com_mudanca_prazo', []):
                (mudadas if p.get('estado') == 'exato' else incertas).append(e)
        elif _parcela(result, e):
            delta = _parcela(result, e)['delta']
            if delta.get('estado') != 'exato':
                incertas.append(e)
            elif delta['valor'] != 0:
                mudadas.append(e)
        elif e == 'PROJECT':
            q = result.get('custo_novo') or {}
            if q.get('estado') != 'exato':
                incertas.append(e)
            elif q['valor'] != result['custo_base'].get('valor'):
                mudadas.append(e)
        else:
            efs = [x for x in result.get('efeitos_financeiros', []) if x['proprietario'] == e]
            if any(x['delta'].get('estado') != 'exato' for x in efs):
                incertas.append(e)
            elif efs:
                mudadas.append(e)
    verdade = 'nv' if sem_estado else False if mudadas else None if incertas else True
    estado, motivo = _veredito_booleano(True, verdade, result)
    return estado, motivo, dict(mudadas=mudadas, incertas=incertas, sem_estado=sem_estado)


def _avaliar_critico(a, result):
    e = a['entidades'][0]
    q = _calculado(result, e, 'fim')
    if q is None:
        return 'nao_verificavel', 'sem_estado_calculado', None
    jusante = _descendentes(result, e) | {e}
    if q.get('estado') != 'exato' or any((_projetado(result, n, 'fim') or {}).get('estado') != 'exato' for n in jusante):
        verdade = None
    else:
        verdade = e in criticos(result)
    estado, motivo = _veredito_booleano(a['valor'], verdade, result)
    return estado, motivo, dict(critico=verdade)


def _avaliar_artefato(a, result):
    if a['predicado'] == 'decisao':
        return 'preservar', 'registro_historico', None
    if a['predicado'] == 'compromisso':
        mudados = set(result.get('nos_com_mudanca_quantitativa', []))
    else:
        mudados = set(result.get('nos_com_mudanca_prazo' if a['campo'] in CAMPOS_TEMPO else 'nos_com_mudanca_custo', []))
    afetadas = [e for e in a['entidades'] if e in mudados]
    if afetadas:
        return 'julgamento_humano', 'evento_relacionado', dict(entidades_alteradas=afetadas)
    return 'ja_atualizado', 'confirmado', dict(entidades_alteradas=[])


def _versao_normal(v):
    """'revisão 1', 'rev. 1' e '1' designam a mesma versão; sem dígitos, compara o texto."""
    digitos = re.findall(r'\d+', str(v))
    return '.'.join(digitos) if digitos else str(v).strip().casefold()


def _avaliar_intervalo(a, result):
    """Dias entre o fim da primeira entidade e o início da segunda (B − A).

    valor booleano: true = existe intervalo (> 0), false = não existe; valor inteiro: dias exatos.
    """
    ea, eb = a['entidades']
    qa, qb = _calculado(result, ea, 'fim'), _calculado(result, eb, 'inicio')
    if qa is None or qb is None:
        return 'nao_verificavel', 'sem_estado_calculado', None
    if qa.get('estado') != 'exato' or qb.get('estado') != 'exato':
        if _pendente(result):
            return 'nao_verificavel', 'execucao_incompleta', None
        return 'revisar', 'certeza_sem_suporte' if type(a['valor']) is bool else 'magnitude_sem_suporte', None
    dias = qb['valor']-qa['valor']
    calc = dict(estado='exato', valor=dias, fim_a=qa['valor'], inicio_b=qb['valor'])
    if type(a['valor']) is bool:
        estado, motivo = _veredito_booleano(a['valor'], dias > 0, result)
        return estado, motivo, calc
    return (('ja_atualizado', 'confirmado') if dias == a['valor'] else ('revisar', 'valor_divergente')) + (calc,)


def _versao_vigente(documentos, entidade):
    for d in documentos:
        if d['id'] == entidade:
            return d['versao']
    return None


def avaliar_afirmacao(a, result, cenario, documentos):
    p = a['predicado']
    if p == 'valor':
        estado, motivo, calc = _avaliar_valor(a, result)
        expl = explicar(result, cenario, a['entidades'], custo=a['campo'] == 'custo')
    elif p == 'versao':
        vigente = _versao_vigente(documentos, a['entidades'][0])
        calc = dict(estado='exato' if vigente is not None else 'indeterminado', valor=vigente)
        if vigente is None:
            estado, motivo = 'nao_verificavel', 'sem_estado_calculado'
        else:
            estado, motivo = ('ja_atualizado', 'confirmado') if _versao_normal(a['valor']) == _versao_normal(vigente) else ('revisar', 'referencia_obsoleta')
        expl = explicar(result, cenario, [])
    elif p == 'no_prazo':
        e = a['entidades'][0]
        q = _calculado(result, e, 'fim')
        base = _base(result, e, 'fim')
        estado, motivo = _veredito_booleano(a['valor'], _comparar_limite(q, base), result)
        calc = dict(fim=q, fim_planejado=base)
        expl = explicar(result, cenario, [e])
    elif p == 'dentro_orcamento':
        q = _calculado(result, 'PROJECT', 'custo')
        base = _base(result, 'PROJECT', 'custo')
        estado, motivo = _veredito_booleano(a['valor'], _comparar_limite(q, base), result)
        calc = dict(custo=q, orcamento=base)
        expl = explicar(result, cenario, [], custo=True)
    elif p == 'sem_alteracao':
        estado, motivo, calc = _avaliar_sem_alteracao(a, result)
        expl = explicar(result, cenario, calc['mudadas']+calc['incertas'], custo=a['campo'] == 'custo')
    elif p == 'intervalo':
        estado, motivo, calc = _avaliar_intervalo(a, result)
        expl = explicar(result, cenario, a['entidades'])
    elif p == 'critico':
        estado, motivo, calc = _avaliar_critico(a, result)
        e = a['entidades'][0]
        expl = None
        if calc and calc.get('critico'):
            # Criticidade: mostrar a cadeia da entidade até o marco final.
            expl = explicar(result, cenario, ['M_RELEASE'], contendo=e)
            if expl['caminhos']:
                expl['texto'] = f'{e} determina o marco final. ' + expl['texto']
            else:
                expl = None
        if expl is None:
            expl = explicar(result, cenario, a['entidades'])
    elif p in ('compromisso', 'risco', 'decisao'):
        estado, motivo, calc = _avaliar_artefato(a, result)
        expl = explicar(result, cenario, (calc or {}).get('entidades_alteradas', []))
        if p == 'decisao':
            expl['texto'] = 'Decisão histórica: a mudança não autoriza reescrevê-la; uma nova decisão seria um registro novo.'
    else:
        raise ValueError(f'Predicado fora do catálogo: {p}')
    return dict(afirmacao=deepcopy(a), estado=estado, motivo=motivo, calculado=deepcopy(calc),
                explicacao=expl, sugestao=_sugestao(a, estado, motivo, calc))


def _brl(centavos):
    s = f'{centavos/100:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    return f'R$ {s}'


def _sugestao(a, estado, motivo, calc):
    if estado == 'ja_atualizado':
        return None
    if estado == 'preservar':
        return 'Preservar o registro histórico; a mudança não autoriza alterá-lo.'
    if estado == 'julgamento_humano':
        ents = ', '.join((calc or {}).get('entidades_alteradas', []))
        return f'Um responsável deve avaliar se o registro continua adequado; mudou: {ents}.'
    if estado == 'nao_verificavel':
        return 'Não afirmar desatualização sem estado calculado validado.'
    if motivo == 'afirmacao_conflitante':
        return 'O documento traz valores incompatíveis para a mesma informação; unificar após conferir a fonte.'
    if motivo == 'valor_divergente' and isinstance(calc, dict) and calc.get('estado') == 'exato':
        if a['unidade'] == 'BRL_centavo':
            return f"Atualizar {a['entidades'][0]}.{a['campo']} para {_brl(calc['valor'])}."
        if a['unidade'] == 'dia_corrido':
            return f"Atualizar {a['entidades'][0]}.{a['campo']} para o dia {calc['valor']}."
        return f"Atualizar {a['entidades'][0]}.{a['campo']} para {calc['valor']}."
    if motivo == 'magnitude_sem_suporte':
        return 'Substituir o valor exato por "a confirmar" até obter a informação faltante.'
    if motivo == 'certeza_sem_suporte':
        return f"Rever \"{a['citacao']}\": a situação calculada ainda é indeterminada."
    if motivo == 'referencia_obsoleta':
        return f"Atualizar a referência para a versão vigente {calc.get('valor')}."
    detalhe = 'a premissa deixou de valer no cálculo'
    p, calc = a['predicado'], calc or {}
    if p == 'no_prazo' and (calc.get('fim') or {}).get('estado') == 'exato':
        detalhe = f"fim calculado no dia {calc['fim']['valor']}, planejado no dia {calc['fim_planejado']}"
    elif p == 'dentro_orcamento' and (calc.get('custo') or {}).get('estado') == 'exato':
        detalhe = f"custo calculado {_brl(calc['custo']['valor'])}, orçamento {_brl(calc['orcamento'])}"
    elif p == 'critico':
        detalhe = 'a entidade passou a determinar o prazo final' if calc.get('critico') else 'a entidade deixou de determinar o prazo final'
    elif p == 'sem_alteracao' and calc.get('mudadas'):
        detalhe = 'mudaram: ' + ', '.join(calc['mudadas'])
    return f"Rever \"{a['citacao']}\": {detalhe}."


def _conflitos(afirmacoes):
    grupos = {}
    for a in afirmacoes:
        if a['predicado'] in PREDICADOS_COMPARAVEIS and a['conhecimento'] == 'exato':
            # Mesmo trecho: seções diferentes podem tratar de momentos diferentes.
            grupos.setdefault((a['trecho_id'], a['predicado'], tuple(a['entidades']), a['campo']), []).append(a)
    ids = set()
    for g in grupos.values():
        if len({json.dumps(x['valor']) for x in g}) > 1:
            ids |= {x['id'] for x in g}
    return ids


def revisar_documentos(result, cenario, extracoes, *, condicao, documentos=None):
    """Avalia afirmações já estruturadas, por documento. Nada é escrito no oficial."""
    if documentos is None:
        from .modelo import carregar
        documentos = carregar()[1]
    saida = []
    for ext in extracoes:
        conflitantes = _conflitos(ext['afirmacoes'])
        avaliadas = []
        for a in ext['afirmacoes']:
            r = avaliar_afirmacao(a, result, cenario, documentos)
            if a['id'] in conflitantes:
                r.update(estado='revisar', motivo='afirmacao_conflitante')
                r['sugestao'] = _sugestao(a, 'revisar', 'afirmacao_conflitante', r['calculado'])
            avaliadas.append(r)
        resumo = {}
        for r in avaliadas:
            resumo[r['estado']] = resumo.get(r['estado'], 0)+1
        saida.append(dict(documento_id=ext['documento_id'], versao=ext['versao'], afirmacoes=avaliadas,
                          nao_mapeados=deepcopy(ext.get('nao_mapeados', [])), resumo=resumo))
    return dict(versao=VERSAO, condicao=condicao, cenario_id=cenario['id'],
                execucao_id=result.get('execucao_id'), inputs_hash=result.get('inputs_hash'),
                extracoes_hash=hash_json(extracoes), execucao_global=result.get('execucao', {}).get('estado'),
                documentos=saida, atualizacao_executada=False, aprovacao_humana=None,
                suporte_semantico='nao_auditado',
                natureza='recomendacao_pendente_validacao_humana')


def tabela(revisao):
    """Linhas legíveis: documento, trecho, citação, estado, motivo, por quê."""
    linhas = []
    for d in revisao['documentos']:
        for r in d['afirmacoes']:
            a = r['afirmacao']
            linhas.append(dict(documento=f"{d['documento_id']}@{d['versao']}", afirmacao=a['id'], citacao=a['citacao'],
                               estado=r['estado'], motivo=r['motivo'], sugestao=r['sugestao'],
                               por_que=r['explicacao']['texto'] if r['estado'] != 'ja_atualizado' or r['explicacao']['absorcoes'] else None))
    return linhas
