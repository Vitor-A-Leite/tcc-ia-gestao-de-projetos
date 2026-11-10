"""Documento cadastrado -> análise H real/injetada -> solver -> verificação documental."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from . import ROOT, VERSION
from .integridade import sha
from .modelo import carregar,projetar,normalizar,grafo_documental
from .politica import construir
from .simulacao import interpretador
from .orquestracao import avaliar
from hibrido_v07_r3.adaptador import LocalV07R3
from interpretacao_no.contratos import hash_json
from motor_deterministico.motor import cronograma
from orquestracao import _corrente


def ler_cenario(id, particao='dev'):
    if particao not in ('dev','final') or not id.isalnum(): raise ValueError('Cenário inválido')
    return json.loads((ROOT/'inputs/cenarios'/particao/(id+'.json')).read_text())


def executar(cenario, *, adapter=None, fixture=None, max_analises=None):
    g,docs=carregar();state=projetar(g,docs);ev=normalizar(cenario,state)
    if adapter is None:
        if fixture is None: raise ValueError('Simulação exige interpretação manual explícita')
        adapter=interpretador(fixture,g);mode='simulacao_offline'
    else:
        if not isinstance(adapter,LocalV07R3): raise ValueError('Use o adaptador real H7.2; mocks exigem modo simulado')
        # Esta função aceita a fronteira real existente; runner pago Alfa não está autorizado.
        mode='transporte_injetado_origem_a_auditar'
    policy=construir(state,ev,g,'ALFA-'+cenario['id'],max_analises)
    result=avaliar(state,ev,adapter,policy)
    result.update(pacote_versao=VERSION,modo=mode,simulacao_nao_mede_ia=mode=='simulacao_offline',data_execucao=datetime.now(timezone.utc).isoformat(),
                  documento_origem=deepcopy(cenario['documento']),cenario_id=cenario['id'],particao=cenario['particao'],inputs_hash=hash_json([g,docs,cenario]),
                  aprovacao_humana=None,atualizacoes_oficiais_executadas=[])
    result['runtime_hashes']={p.name:sha(p) for p in ROOT.glob('*.py')}
    result['grafo']=grafo_documental(g,docs,cenario)
    base=cronograma(state)
    result['baseline_nos']={k:{v:q.saida() for v,q in dates.items()} for k,dates in base.items()}
    accepted=[p for step in result.get('rastro_orquestracao',[]) for p in step.get('analise',{}).get('propostas',[]) if any(d['no_id']==step['no_id'] and d['operacao_estrutural']=='permitida_condicional' for d in policy.registro_operacional['decisoes'])]
    # Evidência auxiliar, nunca completar previsão parcial com baseline.
    current=_corrente(state,accepted,ev)
    result['estado_projetado_nos']={k:{v:q.saida() for v,q in dates.items()} for k,dates in cronograma(current).items()}
    result['projecao_auxiliar_condicional']=True
    preds={n['id']:[] for n in state['entidades']}
    for r in state['relacoes']: preds[r['destino_id']].append(r['origem_id'])
    successors={n:[] for n in preds}
    for n,ps in preds.items():
        for p in ps: successors[p].append(n)
    # Folga total por recuo da baseline; convergências usam mínimo dos sucessores.
    from motor_deterministico.motor import ordenar
    latest={};slack={};dur={a['id']:a['duracao']['valor'] for a in state['atividades']}
    for n in reversed(ordenar(preds)):
        lf=min(latest[s] for s in successors[n]) if successors[n] else state['linha_base']['fim']['valor']
        latest[n]=lf-dur[n];slack[n]=latest[n]-base[n]['inicio'].inferior
    result['folgas_base_dias']=slack
    result['propagacao']=[]
    for r in state['relacoes']:
        a,b=r['origem_id'],r['destino_id']
        na=result['estado_projetado_nos'][a]['fim'];ba=result['baseline_nos'][a]['fim']
        nb=result['estado_projetado_nos'][b]['inicio'];bb=result['baseline_nos'][b]['inicio']
        changed=na['valor']!=ba['valor'] or na['estado']!=ba['estado']
        result['propagacao'].append(dict(relacao_id=r['id'],origem=a,destino=b,regra='inicio=max(restrições, fins dos predecessores)',
            fim_origem=na,inicio_destino=nb,fonte_refs=r['fonte_refs'],
            estado='sem_alteracao' if not changed else 'indeterminado' if na['valor'] is None or nb['valor'] is None else 'absorvido_ou_dominado' if nb['valor']==bb['valor'] else 'dominado_na_convergencia' if na['valor']<nb['valor'] else 'transmitido',
            projecao_condicional=True))
    result['nos_com_mudanca_prazo']=[n for n in preds if any(result['estado_projetado_nos'][n][k]['valor']!=result['baseline_nos'][n][k]['valor'] or result['estado_projetado_nos'][n][k]['estado']!=result['baseline_nos'][n][k]['estado'] for k in ('inicio','fim'))]
    owners={p['id']:p['proprietario'] for p in g['parcelas']}
    result['efeitos_financeiros']=[dict(proprietario=owners[p['parcela_id']],**deepcopy(p)) for p in result.get('livro_parcelas',[]) if p['delta']['valor']!=0]
    result['nos_com_mudanca_custo']=sorted({p['proprietario'] for p in result['efeitos_financeiros']})
    result['nos_com_mudanca_quantitativa']=sorted(set(result['nos_com_mudanca_prazo'])|set(result['nos_com_mudanca_custo']))
    consulted={t['no_id'] for t in result.get('rastro_orquestracao',[]) if t['processamento'] in ('interpretado','reuso_cache')}
    result['cobertura']=dict(nos_grafo=len(g['nodes']),nos_executaveis=len(preds),nos_consultados=len(consulted),nos_nao_consultados=sorted(set(preds)-consulted),arestas_temporais=len(state['relacoes']),truncamento=False)
    from .documentos import verificar
    result['verificacao_documental']=verificar(result,cenario,docs)
    return result


def simular(id,particao='dev',**kwargs):
    c=ler_cenario(id,particao)
    f=json.loads((ROOT/'inputs/simulacoes'/particao/(id+'.json')).read_text())
    return executar(c,fixture=f,**kwargs)
