import ast
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from condicoes import montar_views, auditar_equivalencia, Global, Simulado
from condicoes.baseline import validar_resposta
from condicoes.hibrido import executar_h
from interpretacao_no.contratos import hash_json
from interpretacao_no.adaptadores import RespostaTransporte, FalhaTransporte
from avaliacao import normalizar, avaliar, registrar, validar_manifesto
from avaliacao.demonstracao import montar_demo, q
from avaliacao.referencias import preparar_referencias

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'data/desenvolvimento'

def load(p): return json.loads(p.read_text())

def dados():
    b=load(D/'projeto_minimo_v1/inputs/base.json')
    e=load(D/'projeto_minimo_v1/inputs/cenarios.json')['casos'][1]
    f=load(D/'projeto_minimo_v1/inputs/fontes.json')['fontes']
    g=load(D/'projeto_minimo_grafo_v1/estado_projeto.json')
    return b,e,f,g

def views(b,e,f,g):
    return montar_views(b,e,f,g,vinculo=dict(base_hash=hash_json(b),grafo_hash=hash_json(g),versao_base=b['versao_projeto'],versao_grafo=g['versao']))

def resposta(v,eid='x'):
    c=v['comum']
    r=dict(execucao_id=eid, projeto_id=c['projeto_id'], versao=c['versao_projeto'],evento_id=c['evento']['evento_id'],view_hash=v['view_hash'],justificativa='prescrita')
    for k,val in [('fim_base',10),('fim_novo',12),('delta_dias',2),('custo_base',500000),('custo_novo',540000),('delta_centavos',40000)]:
        r[k]=q(valor=val,unidade='BRL_centavo' if k.startswith('custo') or k=='delta_centavos' else 'dia_corrido')
        r[k]['evidencias']=[dict(fonte_id=c['fontes'][0]['id'],localizador=c['fontes'][0]['localizador'])]
        if k not in ('delta_dias','delta_centavos'): r[k]['direcao']='desconhecida'
    return r

class Views(unittest.TestCase):
    def test_equivalencia_completude(self):
        vs=views(*dados()); a=auditar_equivalencia(vs)
        self.assertTrue(a['relacoes_completas'])
        self.assertEqual(len(vs['H']['relacional']['relacoes']),6)
        self.assertEqual(vs['T']['relacoes_texto'].count('relacoes: '),6)
        self.assertEqual(vs['T']['relacoes_texto'].count('transferencias: '),1)
        self.assertIn('fornece o componente',json.dumps(vs['B'],ensure_ascii=False))
        self.assertIn('Na montagem',json.dumps(vs['B'],ensure_ascii=False))
        self.assertNotIn('n_42be receber cartucho requer',json.dumps(vs['B']))
    def test_positivo_aninhado(self):
        b,e,f,g=dados(); original=views(b,e,f,g)['B']
        b['gabarito']='SEGREDO'; b['calendario']['edges']='SEGREDO'
        b['entidades'][0]['atributos']['ranking']={'expected':'SEGREDO'}
        b['atividades'][0]['duracao']['outputs']='SEGREDO'; e['familia']='SEGREDO'
        e['origem']['expected']='SEGREDO'
        for x in f: x['metadata']={'solver':'SEGREDO'}
        self.assertEqual(original,views(b,e,f,g)['B'])
    def test_nao_aceita_objeto_em_folha(self):
        b,e,f,g=dados(); b['entidades'][0]['nome']={'edges':'SEGREDO'}
        with self.assertRaises(ValueError): views(b,e,f,g)
    def test_outro_aviso_nao_visivel(self):
        b,e,f,g=dados(); v=views(b,e,f,g)['B']; ids={x['id'] for x in v['comum']['fontes']}
        for x in f:
            if x['documento_id'] not in b['documentos_comuns']+[e['documento_evento_vigente']]: self.assertNotIn(x['id'],ids)
    def test_ordem_neutra(self):
        b,e,f,g=dados(); a=views(b,e,f,g)
        for x in (b['entidades'],b['atividades'],b['parcelas_base'],f,g['relacoes'],g['regras_transferencia']): x.reverse()
        self.assertEqual(a,views(b,e,f,g))
    def test_divergencias_snapshot(self):
        for campo in ('duracao','disponibilidade','orcamento','baseline','fonte','versao','endpoint','ref'):
            with self.subTest(campo=campo):
                b,e,f,g=dados()
                if campo=='duracao': g['atividades'][0]['duracao']['valor']+=1
                if campo=='disponibilidade': next(n for n in g['entidades'] if n['tipo']=='componente')['atributos']['disponibilidade']['conhecimento']['valor']+=1
                if campo=='orcamento': g['parcelas_base'][0]['valor_centavos']+=1
                if campo=='baseline': g['linha_base']['fim']['valor']+=1
                if campo=='fonte': g['fontes'][0]['trecho']='DIVERGENTE'
                if campo=='endpoint': g['relacoes'][0]['origem_id']='inexistente'
                if campo=='ref': g['relacoes'][0]['fonte_refs'][0]['localizador']='L999'
                if campo=='versao':
                    v=dict(base_hash=hash_json(b),grafo_hash=hash_json(g),versao_base=b['versao_projeto'],versao_grafo='outra')
                    with self.assertRaises(ValueError): montar_views(b,e,f,g,vinculo=v)
                    continue
                with self.assertRaises(ValueError): views(b,e,f,g)
    def test_ids_opacos_variados(self):
        b,e,f,g=dados()
        texto=json.dumps([b,e,f,g])
        for i,n in enumerate(b['entidades']): texto=texto.replace(n['id'],'z_'+str(901+i))
        b,e,f,g=json.loads(texto)
        v=views(b,e,f,g)
        self.assertTrue(auditar_equivalencia(v)['relacoes_completas'])
        self.assertNotIn('n_42be',json.dumps(v))
    def test_view_adulterada(self):
        v=views(*dados())['B']; v['comum']['moeda']='USD'
        with self.assertRaises(ValueError): Simulado({}).prever(v,execucao_id='x')

class Baseline(unittest.TestCase):
    def setUp(self): self.v=views(*dados())['B']
    def adapter(self,t,retry=False): return Global(t,modelo='modelo-teste',configuracao={'temperatura':0},timeout_s=1,repetir_transporte=retry,origem='transporte_mock')
    def test_resultado_simulado(self):
        r=Simulado(resposta(self.v)).prever(self.v,execucao_id='x')
        self.assertEqual(r['delta_dias']['valor'],2); self.assertEqual(r['execucao']['origem'],'simulado')
        self.assertEqual(r['consumo']['chamadas'],0); self.assertEqual(r['resultados_nos'],[])
    def test_T(self):
        v=views(*dados())['T']; r=Simulado(resposta(v)).prever(v,execucao_id='x')
        self.assertEqual(r['execucao']['estado'],'ok')
    def test_sem_motor(self):
        with patch('motor_deterministico.motor.calcular',side_effect=AssertionError('motor proibido')), patch('motor_deterministico.motor.preparar',side_effect=AssertionError('motor proibido')):
            for v in views(*dados()).values():
                if v['condicao'] in ('B','T'): self.assertEqual(Simulado(resposta(v)).prever(v,execucao_id='x')['execucao']['estado'],'ok')
        for p in (ROOT/'src/condicoes').glob('*.py'):
            if p.name=='hibrido.py': continue
            self.assertNotIn('from motor_deterministico',p.read_text())
    def test_valores_invalidos(self):
        for k,val in [('fim_novo',-1),('custo_novo',-1),('delta_dias',True),('delta_centavos',1.2)]:
            r=resposta(self.v); r[k]['valor']=val
            self.assertEqual(Simulado(r).prever(self.v,execucao_id='x')['execucao']['erros'][0]['codigo'],'saida_invalida')
    def test_delta_negativo(self):
        r=resposta(self.v); r['delta_dias'].update(valor=-1,direcao='reducao')
        self.assertEqual(Simulado(r).prever(self.v,execucao_id='x')['delta_dias']['valor'],-1)
    def test_nao_corrige_aritmetica(self):
        r=resposta(self.v); r['delta_dias']['valor']=99
        self.assertEqual(Simulado(r).prever(self.v,execucao_id='x')['delta_dias']['valor'],99)
    def test_formato_identidades_unidade_evidencia(self):
        for tipo in ('unidade','identidade','evidencia','zero_lacuna','extra'):
            r=resposta(self.v)
            if tipo=='unidade':r['delta_dias']['unidade']='hora'
            if tipo=='identidade':r['evento_id']='outro'
            if tipo=='evidencia':r['delta_dias']['evidencias'][0]['fonte_id']='invisivel'
            if tipo=='zero_lacuna':r['delta_dias'].update(valor=0,direcao='zero',lacunas=['falta'])
            if tipo=='extra':r['gabarito']=0
            self.assertEqual(Simulado(r).prever(self.v,execucao_id='x')['execucao']['estado'],'erro')
    def test_recusa_truncamento_json(self):
        for estado,txt in [('recusa',None),('incompleta','{}'),('completa','{"a":1,"a":2}'),('completa','NaN')]:
            r=self.adapter(lambda _:RespostaTransporte(txt,estado=estado)).prever(self.v,execucao_id='x')
            self.assertEqual(r['execucao']['estado'],'erro');self.assertNotIn('delta_dias',r)
            self.assertEqual(r['consumo']['chamadas'],1)
    def test_timeout_retry_consumo(self):
        chamadas=[]
        def t(req):
            chamadas.append(req)
            if len(chamadas)==1:raise TimeoutError('limite')
            return RespostaTransporte(json.dumps(resposta(self.v)),modelo='observado',tokens_entrada=3,tokens_saida=4,custo_api_centavos=1)
        r=self.adapter(t,True).prever(self.v,execucao_id='x')
        self.assertEqual(r['consumo']['chamadas'],2);self.assertIsNone(r['consumo']['tokens_entrada'])
        self.assertEqual(r['consumo']['tentativas'][1]['modelo'],'observado');self.assertEqual(chamadas[0],chamadas[1])
    def test_falha_definitiva(self):
        def t(_): raise FalhaTransporte('falha','falha',transitoria=False)
        r=self.adapter(t,True).prever(self.v,execucao_id='x')
        self.assertEqual(r['consumo']['chamadas'],1)
    def test_erro_generico(self):
        r=self.adapter(lambda _:1/0).prever(self.v,execucao_id='x')
        self.assertEqual(r['execucao']['erros'][0]['codigo'],'transporte_erro')

class Avaliador(unittest.TestCase):
    def setUp(self): self.m,self.r,self.refs,self.a=montar_demo()
    def test_metricas_denominadores(self):
        out=avaliar(self.m,self.r,self.refs,self.a)
        for c in ('B','H','T'):
            p=out['metricas'][c+':prazo'];co=out['metricas'][c+':custo']
            self.assertEqual(p['N'],8);self.assertEqual(p['cobertura_numerica']['n'],3)
            self.assertEqual(p['erro_numerico']['n'],2);self.assertEqual(p['erro_numerico']['MAE'],1.5)
            self.assertEqual(co['erro_numerico']['MAE_BRL'],1.5)
            self.assertEqual(p['zero_sustentado']['n'],1);self.assertEqual(p['falsa_certeza']['n'],1)
            self.assertEqual(p['indeterminacao_adequada']['n'],1);self.assertEqual(p['acerto_direcao']['n'],3)
        self.assertTrue(all(p['n_intersecao']==2 for p in out['pareadas']))
    def test_ausente(self):
        out=avaliar(self.m,self.r[1:],self.refs)
        self.assertEqual(out['metricas']['B:prazo']['N'],8);self.assertEqual(out['metricas']['B:prazo']['estados']['erro'],2)
        self.assertEqual(out['anomalias'][0]['tipo'],'ausente')
    def test_duplicada(self):
        out=avaliar(self.m,self.r+[self.r[0]],self.refs)
        self.assertEqual(out['metricas']['B:prazo']['N'],8);self.assertEqual(out['anomalias'][0]['tipo'],'duplicada')
    def test_extra(self):
        r=deepcopy(self.r[0]);r['metadados']['execucao_id']='extra'
        self.assertEqual(normalizar(self.m,self.r+[r])['anomalias'][0]['tipo'],'execucao_extra')
    def test_versao_hash_origem(self):
        for campo in ('versao_projeto','origem','view_hash'):
            rs=deepcopy(self.r);rs[0]['metadados'][campo]='outra'
            self.assertEqual(normalizar(self.m,rs)['linhas'][0]['desfechos']['prazo']['classe'],'invalido')
        rs=deepcopy(self.r);rs[0]['resultado']['versao']='outra';rs[0]['resultado_hash']=hash_json(rs[0]['resultado'])
        self.assertEqual(normalizar(self.m,rs)['anomalias'][0]['tipo'],'identidade_versao_divergente')
    def test_manifesto_pareado(self):
        for m in (dict(self.m,execucoes=self.m['execucoes'][1:]),dict(self.m,execucoes=self.m['execucoes']+[self.m['execucoes'][0]])):
            with self.assertRaises(ValueError):validar_manifesto(m)
    def test_referencia_ausente_duplicada_errada(self):
        for refs in (self.refs[1:],self.refs+[self.refs[0]], [dict(self.refs[0],versao_projeto='outra')]+self.refs[1:]):
            with self.assertRaises(ValueError):avaliar(self.m,self.r,refs)
    def test_suporte_nao_automatico(self):
        out=avaliar(self.m,self.r,self.refs)
        self.assertEqual(out['metricas']['B:prazo']['zero_sustentado']['n'],0)
        self.assertEqual(out['metricas']['B:prazo']['suporte'],{'nao_auditado':8})
    def test_pendente_nao_inventa_falsa_certeza(self):
        refs=deepcopy(self.refs)
        for ref in refs:
            for c in ('B','H','T'):
                for d in ('prazo','custo'):ref['por_view'][c][d]['estado']='pendente'
        out=avaliar(self.m,self.r,refs)
        self.assertEqual(out['metricas']['B:prazo']['falsa_certeza']['auditaveis'],0)
    def test_auditoria_obsoleta(self):
        a=deepcopy(self.a);a[0]['resultado_hash']='outra'
        self.assertEqual(avaliar(self.m,self.r,self.refs,a)['auditorias_nao_vinculadas'],1)
    def test_reducao_zero_sem_imputacao(self):
        for ref in self.refs:
            for d in ('prazo','custo'):
                if ref['verdade'][d]['estado']=='exato': ref['verdade'][d].update(valor=-1,direcao='reducao')
        out=avaliar(self.m,self.r,self.refs)
        self.assertEqual(out['metricas']['B:prazo']['erro_numerico']['MAE'],3.5)
        self.assertEqual(out['metricas']['B:prazo']['erro_numerico']['n'],2)
    def test_unidade_ausente_invalida(self):
        self.r[0]['resultado']['delta_dias'].pop('unidade')
        self.r[0]['resultado_hash']=hash_json(self.r[0]['resultado'])
        self.assertEqual(normalizar(self.m,self.r)['linhas'][0]['desfechos']['prazo']['classe'],'invalido')
    def test_inconsistencia_aritmetica_avaliador(self):
        r=self.r[0]['resultado'];r.update(fim_base=q(valor=10),fim_novo=q(valor=12))
        self.r[0]['resultado_hash']=hash_json(r)
        self.assertEqual(avaliar(self.m,self.r,self.refs)['metricas']['B:prazo']['inconsistencia_aritmetica']['n'],1)
        self.assertEqual(r['delta_dias']['valor'],0)
    def test_referencia_view_obsoleta(self):
        self.refs[0]['por_view']['B']['prazo']['view_hash']='outra'
        with self.assertRaises(ValueError):avaliar(self.m,self.r,self.refs)

class IntegracaoH(unittest.TestCase):
    def test_H_real_contrato_simulado(self):
        from orquestracao.simulacao import InterpretadorPrescrito,politica_prescrita
        b,e,f,g=dados();v=views(b,e,f,g)['H'];fixture=load(D/'orquestracao_simulada_v1/k_09c2.json')
        p=politica_prescrita(fixture)
        vinculo=dict(base_hash=hash_json(b),grafo_hash=hash_json(g),versao_base=b['versao_projeto'],versao_grafo=g['versao'])
        r=executar_h(b,e,f,g,fixture['evento'],v,InterpretadorPrescrito(fixture),p,vinculo=vinculo,origem='simulado')
        self.assertEqual(r['delta_dias']['valor'],2);self.assertEqual(r['execucao']['origem'],'simulado')
        self.assertTrue(r['rastro_orquestracao']);self.assertEqual(r['consumo']['chamadas'],0)
        m,rs,refs,a=montar_demo();m['execucoes']=m['execucoes'][:3]
        slot=m['execucoes'][1]
        slot.update(projeto_id=b['projeto_id'],evento_id=e['evento_id'],execucao_id=p.execucao_id,versao_projeto=g['versao'],
                    view_hash=v['view_hash'],snapshot_hash=hash_json(g),evento_hash=hash_json(fixture['evento']))
        rs=rs[:3];rs[1]=registrar(slot,r)
        self.assertEqual(normalizar(m,rs)['linhas'][1]['desfechos']['prazo']['classe'],'exato')
        with self.assertRaises(ValueError):executar_h(b,e,f,g,fixture['evento'],v,InterpretadorPrescrito(fixture),p,vinculo=vinculo,origem='llm_transporte_injetado')
        fixture['evento']['relato']='outro'
        with self.assertRaises(ValueError):executar_h(b,e,f,g,fixture['evento'],v,InterpretadorPrescrito(fixture),p,vinculo=vinculo,origem='simulado')
    def test_referencias_autorais(self):
        b,e,f,g=dados();casos=load(D/'projeto_minimo_v1/inputs/cenarios.json')['casos']
        vs={ev['caso_id']:views(b,ev,f,g) for ev in casos}
        refs=preparar_referencias(load(D/'projeto_minimo_v1/referencias/gabaritos.json'),vs,dict(B=b['versao_projeto'],H=g['versao'],T=b['versao_projeto']))
        self.assertEqual(len(refs),16)
        self.assertEqual(refs[0]['por_view']['B']['prazo']['estado'],'pendente')
        self.assertEqual(refs[0]['por_view']['H']['prazo']['estado'],'exato')
        self.assertTrue(all(r['revisores']==[] for r in refs))

if __name__=='__main__':unittest.main()
