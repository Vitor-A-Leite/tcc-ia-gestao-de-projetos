"""Avaliação final: material, regra de agregação por trecho e métricas.

A regra de agregação e as métricas são fixadas antes da rodada e registradas no
manifesto. O gabarito só é lido na comparação, depois de todas as respostas.
"""
from collections import Counter
from copy import deepcopy
import json

from . import DATA

PASTA = DATA/'final'
MATERIAL = PASTA/'material_gerado.json'
GABARITO = PASTA/'gabarito_final.json'
EVENTOS = tuple(f'F{i:02}' for i in range(1, 16))
GRUPOS_D = (('STATUS_A', 'STATUS_B'), ('STATUS_C', 'STATUS_D'), ('ACTION_LOG', 'RISK_REGISTER', 'DECISION_LOG'))
VERSAO_DOCUMENTO = '1-final'

REGRA_AGREGACAO = (
    'Por trecho e evento. Decision Log: sempre PRESERVAR. Demais documentos: sem afirmação extraída → SEM_AFIRMACAO; '
    'alguma afirmação "revisar" → REVISAR; senão alguma "julgamento_humano" → DECISAO_HUMANA; senão CORRETO '
    '(inclui ja_atualizado, nao_verificavel e preservar). Documento sem extração válida ou grupo sem anotação válida → FALHA, '
    'que conta como "não revisar" e como erro nas métricas de classe.')


def carregar_material():
    return json.loads(MATERIAL.read_text())


def documentos_finais(material=None):
    """Documentos do material no formato do corpus de conteúdo (localizador por seção)."""
    material = material or carregar_material()
    docs = []
    for d in material['documentos']:
        docs.append(dict(id=d['id'], versao=VERSAO_DOCUMENTO, artefato=d['artefato'], nome=d['nome'],
                         trechos=[dict(id=t['id'], localizador='§'+t['id'].split('.', 1)[1], texto=t['texto']) for t in d['trechos']]))
    return docs


def eventos(material=None):
    material = material or carregar_material()
    return {e['id']: deepcopy(e) for e in material['eventos']}


def agregar_b(revisao, documentos):
    """Rótulo por trecho a partir das afirmações avaliadas (condição B)."""
    por_doc = {(d['documento_id'], d['versao']): d for d in revisao['documentos']}
    rotulos = {}
    for d in documentos:
        aval = por_doc.get((d['id'], d['versao']))
        for t in d['trechos']:
            if d['artefato'] == 'decision_log':
                rotulos[t['id']] = 'PRESERVAR' if aval is not None else 'FALHA'
                continue
            if aval is None:
                rotulos[t['id']] = 'FALHA'
                continue
            estados = [a['estado'] for a in aval['afirmacoes'] if a['afirmacao']['trecho_id'] == t['id']]
            if not estados:
                rotulos[t['id']] = 'SEM_AFIRMACAO'
            elif 'revisar' in estados:
                rotulos[t['id']] = 'REVISAR'
            elif 'julgamento_humano' in estados:
                rotulos[t['id']] = 'DECISAO_HUMANA'
            else:
                rotulos[t['id']] = 'CORRETO'
    return rotulos


def motivos_b(revisao):
    m = {}
    for d in revisao['documentos']:
        for a in d['afirmacoes']:
            if a['estado'] == 'revisar':
                m.setdefault(a['afirmacao']['trecho_id'], set()).add(a['motivo'])
    return m


def _classe4(r):
    return 'NAO_REVISAR' if r in ('CORRETO', 'SEM_AFIRMACAO', 'FALHA') else r


def metricas(predito, gabarito, motivos_preditos=None):
    """predito/gabarito: {(evento, trecho): rotulo}; gabarito também traz motivos."""
    vp = fp = fn = vn = 0
    ac5 = ac4 = falhas = 0
    motivo_ok = motivo_total = 0
    fp_em_corretos = corretos = 0
    por_doc = Counter()
    for k, g in gabarito.items():
        p = predito.get(k, 'FALHA')
        falhas += p == 'FALHA'
        gr, pr = g['rotulo'] == 'REVISAR', p == 'REVISAR'
        vp += gr and pr; fp += (not gr) and pr; fn += gr and not pr; vn += (not gr) and not pr
        ac5 += p == g['rotulo']; ac4 += _classe4(p) == _classe4(g['rotulo'])
        if g['rotulo'] in ('CORRETO', 'SEM_AFIRMACAO'):
            corretos += 1; fp_em_corretos += pr
        if gr and pr and motivos_preditos is not None:
            motivo_total += 1
            motivo_ok += bool(set(motivos_preditos.get(k, ())) & set(g['motivos']))
        if gr != pr:
            por_doc[k[1].split('.')[0]] += 1
    prec = vp/(vp+fp) if vp+fp else None
    rev = vp/(vp+fn) if vp+fn else None
    f1 = 2*prec*rev/(prec+rev) if prec and rev else None
    n = len(gabarito)
    return dict(pares=n, falhas=falhas, revisar=dict(vp=vp, fp=fp, fn=fn, vn=vn, precisao=prec, revocacao=rev, f1=f1),
                acuracia_5_rotulos=ac5/n, acuracia_4_classes=ac4/n,
                falsos_alertas_em_trechos_corretos=dict(fp=fp_em_corretos, de=corretos),
                motivo_compativel=dict(ok=motivo_ok, de=motivo_total) if motivos_preditos is not None else None,
                erros_revisar_por_documento=dict(por_doc))


def resumo_repeticoes(lista):
    """Média, mínimo e máximo das métricas principais entre repetições."""
    def serie(f):
        v = [f(m) for m in lista if f(m) is not None]
        return dict(media=sum(v)/len(v), minimo=min(v), maximo=max(v), n=len(v)) if v else None
    return dict(repeticoes=len(lista),
                precisao=serie(lambda m: m['revisar']['precisao']), revocacao=serie(lambda m: m['revisar']['revocacao']),
                f1=serie(lambda m: m['revisar']['f1']), acuracia_4_classes=serie(lambda m: m['acuracia_4_classes']),
                acuracia_5_rotulos=serie(lambda m: m['acuracia_5_rotulos']), falhas=serie(lambda m: m['falhas']))


def carregar_gabarito():
    g = json.loads(GABARITO.read_text())
    return g, {(a['evento'], a['trecho_id']): dict(rotulo=a['rotulo'], motivos=a['motivos']) for a in g['anotacoes']}
