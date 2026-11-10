"""Avaliador independente: lê referências só depois de persistir resultados.

Erros/falhas integram denominadores. Nenhuma recuperação de JSON ou reparo de
previsões. As métricas deste pacote caracterizam simulação, não desempenho LLM.
"""
import hashlib
import json
from . import ROOT
from .dados import gravar


def avaliar_resultados(results, particao):
    counts=dict(TP=0,FP=0,FN=0,TN=0)
    timeline=money=0;nt=nc=0;et=ec=0;failures=[];structural=0;recommendations=0;units=0
    for result in results:
        ref=json.loads((ROOT/'inputs/referencias'/particao/(result['cenario_id']+'.json')).read_text())
        valid=result['execucao']['estado'] in ('ok','parcial') and not result.get('pendencias_execucao')
        def correct(key,truth):
            q=result.get(key)
            return bool(valid and q and ((truth is None and q['estado']!='exato' and q['valor'] is None) or (truth is not None and q['estado']=='exato' and q['valor']==truth)))
        tc=correct('fim_novo',ref['fim']);cc=correct('custo_novo',ref['custo'])
        timeline+=tc;money+=cc
        if ref['fim'] is not None:
            nt+=1;q=result.get('fim_novo',{})
            if q.get('estado')=='exato': et+=abs(q['valor']-ref['fim'])
        if ref['custo'] is not None:
            nc+=1;q=result.get('custo_novo',{})
            if q.get('estado')=='exato': ec+=abs(q['valor']-ref['custo'])
        truth=set(ref['revisar']);neg=set(ref['nao_revisar'])
        recs=result['verificacao_documental']['recomendacoes'];pred={r['trecho_id'] for r in recs}
        # Unidade: (cenário, documento@versão, trecho, campo). Fixtures têm um
        # campo por trecho; IDs válidos fora do universo são falsos positivos.
        counts['TP']+=len(pred&truth);counts['FP']+=len(pred-truth)
        counts['FN']+=len(truth-pred);counts['TN']+=len(neg-pred);units+=len(truth|neg)
        recommendations+=len(recs)
        for r in recs:
            # Este indicador verifica vínculos, não prova entailment semântico.
            structural+=bool(r['evidencias'] and r['calculo_ref']['inputs_hash']==result['inputs_hash'] and r['calculo_ref']['quantidade'] and any(e['documento_id']==result['documento_origem']['id'] for e in r['evidencias']))
        if not tc or not cc or pred!=truth:
            failures.append(dict(cenario=result['cenario_id'],prazo_correto=tc,custo_correto=cc,FP=sorted(pred-truth),FN=sorted(truth-pred),execucao=result['execucao']))
    tp,fp,fn=counts['TP'],counts['FP'],counts['FN']
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    return dict(natureza='simulacao_offline_nao_avalia_IA',particao=particao,execucoes=len(results),
                prazo=dict(acertos_estado_e_valor=timeline,total=len(results),referencias_numericas=nt,soma_erros_absolutos_pares_exatos=et),
                custo=dict(acertos_estado_e_valor=money,total=len(results),referencias_numericas=nc,soma_erros_absolutos_pares_exatos=ec),
                documental=dict(unidade='cenario+documento@versao+trecho+campo',unidades=units,**counts,precision=precision,recall=recall,F1=f1,
                    recomendacoes=recommendations,rastreabilidade_estrutural=dict(sustentadas=structural,total=recommendations,taxa=structural/recommendations if recommendations else None),
                    suporte_semantico='requer auditoria humana/independente; conferência manual representativa em QA_MANUAL.md'),falhas=failures)


def executar_avaliacao(saida,particao='dev'):
    if saida.exists(): raise ValueError('Saída já existe; não sobrescrever resultados')
    from .pipeline import simular
    saida.mkdir(parents=True)
    # Persistência bruta antes de abrir a referência, inclusive falhas.
    results=[]
    for file in sorted((ROOT/'inputs/cenarios'/particao).glob('*.json')):
        r=simular(file.stem,particao);gravar(saida/(file.stem+'.json'),r);results.append(r)
    report=avaliar_resultados(results,particao);gravar(saida/'metricas.json',report)
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in saida.glob('*.json')}
    gravar(saida/'MANIFESTO.json',manifest)
    return report
