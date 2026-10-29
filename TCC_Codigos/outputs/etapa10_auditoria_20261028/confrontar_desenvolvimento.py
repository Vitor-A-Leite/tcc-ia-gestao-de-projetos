"""Confronto posterior ao selo; não modifica pareceres, fontes ou referências antigas."""
from pathlib import Path
from copy import deepcopy
import hashlib,json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def ler(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exigir(c,m):
    if not c:raise ValueError(m)


def main():
    d=OUT/'revisao_cega'
    selos={'calcular_independente.py':'1c4f833abbacbaf0e11c6804e3de725336a5096804bc8931527a4941e1c1a130',
           'derivacoes.json':'87c66fda5527eea0984c197c2b0793e1fabdcab034aa7e4d1d760eb611173180',
           'NOTAS.md':'8b3f4bf1e248af4799216f8490c5b556781a59c29aca68311f79e8e22e600ed9'}
    for p,h in selos.items():exigir(sha(d/p)==h,'Selo inicial alterado: '+p)
    fonte=ROOT/'TCC_Codigos/docs/desenvolvimento/ETAPA_01_ESPECIFICACAO.md'
    suplemento=ler(OUT/'modelo_formal_sem_gabaritos.json')
    exigir(sha(fonte)==suplemento['sha256_fonte'],'Fonte do modelo alterada')
    for trecho in suplemento['excertos']:exigir(trecho in fonte.read_text(),'Excerto não literal')
    cego=ler(d/'derivacoes.json');por={c['caso_id']:c for c in cego['casos']}
    autoral=ler(OUT.parent/'etapa9_piloto_v07_r3_20261028/referencias_avaliacao_autoral.json')
    linhas=[];resolvidas=[]
    for r in autoral:
        caso=por[r['caso_id']]
        for dim,key in [('prazo','delta_prazo_dias'),('custo','delta_custo_centavos')]:
            q=caso['H'][key];ref=r['verdade'][dim]
            concorda=(q['estado'],q['valor'])==(ref['estado'],ref['valor'])
            if not concorda:
                exigir(r['caso_id']=='k_23d8' and dim=='custo','Divergência não adjudicada')
                exigir(ref['estado']=='direcao' and ref['direcao']=='aumento' and ref['valor'] is None,'Adjudicação inesperada')
                exigir((d/'adendo_modelo.json').is_file(),'Falta adendo')
            linhas.append(dict(caso_id=r['caso_id'],versao_projeto=r['versao_projeto'],desfecho=dim,
                referencia_autoral=ref,revisao_cega=q,concorda_inicialmente=concorda,
                decisao='Confirmada sob modelo formal; magnitude permanece desconhecida' if not concorda else 'Confirmada',
                fonte_adendo='revisao_cega/ADENDO_MODELO.md' if not concorda else None))
    # Verdade do modelo, por caso. A auditoria de visibilidade continua separada.
    for cid,caso in por.items():
        verdade={}
        for dim,key in [('prazo','delta_prazo_dias'),('custo','delta_custo_centavos')]:
            q=deepcopy(caso['H'][key])
            if q['estado']=='exato':q['direcao']='aumento' if q['valor']>0 else 'reducao' if q['valor']<0 else 'zero'
            if cid=='k_23d8' and dim=='custo':
                q.update(estado='direcao',direcao='aumento',limite_inferior=20000,
                         nota='Adendo formal posterior ao selo inicial; custo de parcelas não negativo e crédito exige fonte.')
            verdade[dim]=q
        resolvidas.append(dict(caso_id=cid,verdade_no_modelo_formal=verdade,
            inferibilidade_documental=deepcopy(caso['B']),premissas=caso.get('ambiguidades',[]),
            limite='Referência B literal e B acrescido de axiomas são escopos distintos; consultar adendo. Não equivale à auditoria semântica de cada resposta.'))
    res=dict(natureza='Confronto da coordenação após derivação cega selada, mais adendo sem previsões',
             casos_unicos=15,dimensoes_unicas=30,linhas_com_versoes=len(linhas),
             divergencias_iniciais_unicas=[dict(caso_id='k_23d8',desfecho='custo',
                 causa='Premissa de custo adicional não negativo ausente no primeiro pacote cego.',
                 resolucao='Modelo formal preexistente esclarecido ao revisor sem gabaritos; direção aumento, magnitude indefinida.',
                 nao_implica='Não prova que todas as premissas eram visíveis a B/T/H no piloto.')],
             pontos_exatos_confirmados=sum(v['estado']=='exato' for c in resolvidas for v in c['verdade_no_modelo_formal'].values()),nenhum_valor_exato_corrigido=True,linhas=linhas,
             referencias_revisadas=resolvidas,parecer_humano=False,
             fonte_modelo_verificada=dict(path=str(fonte.relative_to(ROOT)),sha256=sha(fonte),excertos_literais=True),
             selos_iniciais_preservados=selos)
    (OUT/'confronto_desenvolvimento.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in res.items() if k not in ['linhas','referencias_revisadas','selos_iniciais_preservados']},ensure_ascii=False))


if __name__=='__main__':main()
