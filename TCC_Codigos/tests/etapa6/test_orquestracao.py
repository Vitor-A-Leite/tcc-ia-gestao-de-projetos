import json
from copy import deepcopy
from pathlib import Path
import unittest
from orquestracao import avaliar, Politica, projecao
from orquestracao.simulacao import InterpretadorPrescrito, politica_prescrita

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/desenvolvimento'

class Orquestracao(unittest.TestCase):
    def setUp(self):
        self.e=json.loads((DATA/'projeto_minimo_grafo_v1/estado_projeto.json').read_text())
    def fixture(self, caso='k_09c2'):
        return json.loads((DATA/'orquestracao_simulada_v1'/ (caso+'.json')).read_text())
    def rodar(self, caso='k_09c2', **limites):
        f=self.fixture(caso);i=InterpretadorPrescrito(f);p=politica_prescrita(f,**limites)
        return avaliar(self.e,f['evento'],i,p),i,p
    def test_oito_fluxos(self):
        for c,d,v in [('k_b731',0,0),('k_09c2',2,40000),('k_e168',0,30000),('k_547a',2,0),('k_a92f',0,15000),('k_f04b',-1,-10000),('k_23d8',None,None),('k_8c65',2,None)]:
            with self.subTest(c=c):
                r,_,_=self.rodar(c)
                self.assertEqual(r['delta_dias']['valor'],d,r)
                self.assertEqual(r['delta_centavos']['valor'],v,r)
                if v is None:
                    self.assertEqual(r['delta_centavos']['direcao'],'aumento')
                    self.assertEqual(r['delta_centavos']['limites']['inferior'],20000)
    def test_contexto_convergencia_corrente(self):
        r,i,_=self.rodar()
        c=next(c for c in i.contextos if c['no_id']=='n_a367')
        q={p['no_id']:p for p in c['entradas_correntes']}
        self.assertEqual(q['n_42be']['quantitativo']['fim']['valor'],7)
        self.assertEqual(q['n_915c']['quantitativo']['fim']['valor'],5)
        self.assertTrue(all(p['execucao_id']==c['execucao_id'] for p in q.values()))
        self.assertEqual(len(i.contextos),3)
        self.assertEqual(r['consumo']['chamadas'],0)
    def test_custo_sem_atraso_nao_para_montagem(self):
        r,i,_=self.rodar('k_e168')
        self.assertIn('n_a367',[c['no_id'] for c in i.contextos])
        self.assertEqual(len({p['parcela_id'] for p in r['livro_parcelas']}),len(r['livro_parcelas']))
    def test_imutabilidade_sem_vazamento(self):
        f=self.fixture();antes=deepcopy((self.e,f));i=InterpretadorPrescrito(f)
        avaliar(self.e,f['evento'],i,politica_prescrita(f))
        self.assertEqual((self.e,f),antes)
        for c in i.contextos:
            texto=json.dumps(c)
            for proibido in ('delta_centavos','livro_parcelas','expected_','referencias/','propostas_por_no','autorizacoes'):
                self.assertNotIn(proibido,texto)
        self.assertGreater(len({tuple(c['fontes'][j]['id'] for j in range(len(c['fontes']))) for c in i.contextos}),1)
    def test_sem_politica_nao_aplica(self):
        f=self.fixture();p=politica_prescrita(f);p.resolver=None
        r=avaliar(self.e,f['evento'],InterpretadorPrescrito(f),p)
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertIsNone(r['delta_centavos']['valor'])
    def test_limites(self):
        for limites in ({'max_analises':0},{'max_tempo_s':1e-9}):
            with self.subTest(limites=limites):
                r,i,_=self.rodar(**limites)
                self.assertEqual(r['execucao']['estado'],'parcial')
                self.assertEqual(len(i.contextos),0)
    def test_cache_revalidado_e_invalidado(self):
        f=self.fixture();i=InterpretadorPrescrito(f);p=politica_prescrita(f)
        avaliar(self.e,f['evento'],i,p);n=len(i.contextos)
        r=avaliar(self.e,f['evento'],i,p)
        self.assertEqual(len(i.contextos),n)
        self.assertTrue(any(t['processamento']=='reuso_cache' for t in r['rastro_orquestracao']))
        f['evento']['relato']+=' Revisão documental.'
        avaliar(self.e,f['evento'],i,p)
        self.assertGreater(len(i.contextos),n)
        self.assertTrue(any(c['revisao']>1 for c in i.contextos[n:]))
    def test_cache_adulterado_rejeitado(self):
        f=self.fixture();i=InterpretadorPrescrito(f);p=politica_prescrita(f)
        avaliar(self.e,f['evento'],i,p)
        next(iter(p.cache.values()))['revisao']=9
        r=avaliar(self.e,f['evento'],i,p)
        self.assertEqual(r['execucao']['estado'],'erro')
    def test_resposta_obsoleta(self):
        f=self.fixture();i=InterpretadorPrescrito(f)
        class Obsoleto:
            def analisar(_,c):
                a=i.analisar(c);a['contexto_hash']='antigo';return a
        r=avaliar(self.e,f['evento'],Obsoleto(),politica_prescrita(f))
        self.assertEqual(r['execucao']['estado'],'erro')
    def test_falha_interpretacao(self):
        f=self.fixture();f['propostas_por_no']['n_c820'][0]['valor']['valor']=-1
        r=avaliar(self.e,f['evento'],InterpretadorPrescrito(f),politica_prescrita(f))
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertIsNone(r['delta_dias']['valor'])
    def test_alvo_ambiguo(self):
        f=self.fixture();p=politica_prescrita(f);p.alvos=[]
        self.assertEqual(avaliar(self.e,f['evento'],InterpretadorPrescrito(f),p)['execucao']['estado'],'erro')
    def test_regra_pendente(self):
        f=self.fixture();p=politica_prescrita(f);del p.plano['n_a367']
        r=avaliar(self.e,f['evento'],InterpretadorPrescrito(f),p)
        self.assertEqual(r['execucao']['estado'],'parcial')
    def test_deterministico_sem_llm(self):
        f=self.fixture('k_f04b');e=deepcopy(self.e);e['regras_locais']=[]
        f['evento']['relato']='Evento sintético: nenhuma alteração no projeto; condições e valores preservados.'
        f['evento']['evidencias'][0]['trecho']=f['evento']['relato']
        # Evento normalizado sem alterações quantitativas: fechamento é externo explícito.
        class Nunca:
            def analisar(_,c):raise AssertionError('Chamada indevida')
        p=Politica(execucao_id='det',alvos=['n_915c'],plano={},origem='teste determinístico',fechamento=True)
        r=avaliar(e,f['evento'],Nunca(),p)
        self.assertEqual(r['execucao']['estado'],'ok')
    def test_ids_trocados(self):
        f=self.fixture();mapping={n['id']:'opaco_'+str(i) for i,n in enumerate(self.e['entidades'])}
        def trocar(x):
            if isinstance(x,str):return mapping.get(x,x)
            if isinstance(x,list):return [trocar(v) for v in x]
            if isinstance(x,dict):return {mapping.get(k,k):trocar(v) for k,v in x.items()}
            return x
        e,f=trocar(self.e),trocar(f)
        from interpretacao_no.contratos import hash_json
        for ps in f['propostas_por_no'].values():
            for p in ps:
                for o in p['origens_causais']:o['efeito_id']=hash_json([f['evento']['evento_id'],p['alvo_id']])
        r=avaliar(e,f['evento'],InterpretadorPrescrito(f),politica_prescrita(f))
        self.assertEqual(r['delta_dias']['valor'],2)
        self.assertEqual(r['delta_centavos']['valor'],40000)

    def test_lacunas_legitimas_preservam_conclusoes(self):
        for caso in ('k_23d8','k_8c65'):
            f=self.fixture(caso);i=InterpretadorPrescrito(f)
            class ComLacunas:
                origem='simulado'
                def analisar(_,c):
                    a=i.analisar(c);a['lacunas']=[l for p in a['propostas'] if isinstance(p['valor'],dict) for l in p['valor'].get('lacunas',[])];return a
            r=avaliar(self.e,f['evento'],ComLacunas(),politica_prescrita(f))
            self.assertEqual(r['delta_centavos']['direcao'],'aumento')
            self.assertEqual(r['delta_centavos']['limites']['inferior'],20000)
            if caso=='k_8c65':self.assertEqual(r['delta_dias']['valor'],2)
    def test_predecessor_pendente_nao_vira_baseline_vigente(self):
        f=self.fixture();i=InterpretadorPrescrito(f);p=politica_prescrita(f)
        resolver=p.resolver
        p.resolver=lambda c,a:c['no_id']!='n_c820' and resolver(c,a)
        r=avaliar(self.e,f['evento'],i,p)
        self.assertEqual([c['no_id'] for c in i.contextos],['n_c820'])
        registros={x['no_id']:x for x in r['registros_correntes']}
        self.assertEqual(registros['n_a367']['quantitativo'],{})
        self.assertEqual(registros['n_915c']['quantitativo']['fim']['valor'],5)
    def test_zero_api_simulado_e_cache_consumo_real(self):
        r,_,_=self.rodar(max_chamadas=0)
        self.assertEqual(r['execucao']['estado'],'ok')
        f=self.fixture();i=InterpretadorPrescrito(f);p=politica_prescrita(f)
        from interpretacao_no.adaptadores import LLM,RespostaTransporte
        def transporte(req):
            c=json.loads(req['mensagens'][1]['conteudo'])['contexto']
            a=i.analisar(c)
            a={k:v for k,v in a.items() if k not in ('execucao','decisoes')}
            return RespostaTransporte(json.dumps(a),tokens_entrada=10,tokens_saida=20,custo_api_centavos=1)
        llm=LLM(transporte,modelo='offline-injetado',configuracao={},timeout_s=1)
        r=avaliar(self.e,f['evento'],llm,p)
        self.assertEqual(r['consumo']['chamadas'],3)
        self.assertEqual(r['consumo']['tokens_entrada'],30)
        r=avaliar(self.e,f['evento'],llm,p)
        self.assertEqual(r['consumo']['chamadas'],0)
        self.assertEqual(r['consumo']['tokens_entrada'],0)
        self.assertEqual(r['consumo']['custo_api_centavos'],0)
    def test_mesma_obrigacao_duas_origens_uma_vez(self):
        f=self.fixture();p=deepcopy(f['propostas_por_no']['n_42be'][0])
        p.update(id='segunda_origem',no_id='n_c820')
        f['propostas_por_no']['n_c820'].append(p)
        f['plano']['n_c820']['obrigacoes'].append(p['alvo_id'])
        r=avaliar(self.e,f['evento'],InterpretadorPrescrito(f),politica_prescrita(f))
        self.assertEqual(r['delta_centavos']['valor'],40000)
        self.assertEqual(sum(x['parcela_id']==p['alvo_id'] for x in r['livro_parcelas']),1)
    def test_conteudo_falso_nao_autoriza_por_hash(self):
        f=self.fixture();p=politica_prescrita(f)
        f['propostas_por_no']['n_c820'][0]['valor']['valor']=200
        r=avaliar(self.e,f['evento'],InterpretadorPrescrito(f),p)
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertIsNone(r['delta_dias']['valor'])

    def test_excecao_tardia_preserva_identidade_rastro_consumo(self):
        f=self.fixture();i=InterpretadorPrescrito(f)
        class Falho:
            origem='simulado'
            def analisar(_,c):
                if c['no_id']=='n_a367':raise RuntimeError('falha externa')
                return i.analisar(c)
        r=avaliar(self.e,f['evento'],Falho(),politica_prescrita(f))
        self.assertEqual(r['execucao']['estado'],'erro')
        self.assertIsNone(r['consumo']['chamadas'])
        self.assertEqual(r['evento_id'],f['evento']['evento_id'])
        self.assertEqual(r['fim_base']['valor'],10)
        self.assertGreater(len(r['rastro_orquestracao']),1)
    def test_limite_real_reserva_tentativas(self):
        f=self.fixture();p=politica_prescrita(f,max_chamadas=1)
        from interpretacao_no.adaptadores import LLM,RespostaTransporte
        chamadas=[]
        def transporte(req):
            chamadas.append(req);return RespostaTransporte('{}')
        i=LLM(transporte,modelo='offline',configuracao={},timeout_s=1,repetir_transporte=True)
        r=avaliar(self.e,f['evento'],i,p)
        self.assertEqual(chamadas,[])
        self.assertEqual(r['execucao']['estado'],'parcial')

    def test_regra_sem_plano_bloqueia_interpretacao_descendente(self):
        f=self.fixture('k_8c65');p=politica_prescrita(f);del p.plano['n_a367'];i=InterpretadorPrescrito(f)
        r=avaliar(self.e,f['evento'],i,p)
        self.assertNotIn('n_e659',[c['no_id'] for c in i.contextos])
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertTrue(all(n['processamento'] in ('calculado','inalterado_verificado','nao_avaliado','bloqueado') for n in r['resultados_nos']))
    def test_lacuna_residual_nao_finge_completude(self):
        f=self.fixture();i=InterpretadorPrescrito(f)
        class Residual:
            origem='simulado'
            def analisar(_,c):
                a=i.analisar(c);a['lacunas']=['Efeito adicional ainda não representado'];return a
        r=avaliar(self.e,f['evento'],Residual(),politica_prescrita(f))
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertIsNone(r['delta_centavos']['valor'])
    def test_cache_vinculado_a_configuracao_e_validador(self):
        f=self.fixture();i=InterpretadorPrescrito(f);p=politica_prescrita(f)
        avaliar(self.e,f['evento'],i,p);q=len(i.contextos)
        i.configuracao={'revisao':2}
        avaliar(self.e,f['evento'],i,p)
        self.assertGreater(len(i.contextos),q);q=len(i.contextos)
        resolver=p.resolver;p.resolver=lambda c,a:resolver(c,a)
        avaliar(self.e,f['evento'],i,p)
        self.assertGreater(len(i.contextos),q)

if __name__=='__main__':unittest.main()
