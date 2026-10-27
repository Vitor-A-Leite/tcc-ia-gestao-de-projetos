"""Contratos/contraprovas offline: nenhum oráculo ou resposta de IA real fabricada."""
import json,unittest
from copy import deepcopy
from cenarios import projeto,analise,proposta,exato,desconhecido,REF,CLAUSULA
from hibrido_v05 import avaliar,construir,SimuladoV05,SCHEMA,LocalV05,montar_contexto,validar
from hibrido_v05.contratos import VERSAO,hash_json
from hibrido_v05.motor import calcular
from motor_deterministico.motor import resumo
from interpretacao_no.adaptadores import RespostaTransporte

class ContratosEscopados(unittest.TestCase):
    def contexto(self,duas=False):
        e,ev=projeto()
        if duas:
            regra=deepcopy(e['regras_locais'][0]);regra.update(id='r_extra',atributos_alvo=['readequacao'],operacoes_permitidas=['confirmar_ausencia_parcela_adicional']);e['regras_locais'].append(regra)
        p=construir(e,ev,execucao_id='mock_contrato')
        c=montar_contexto(e,ev,execucao_id=p.execucao_id,no_id='n_join',revisao=1,**p.plano['n_join'])
        return e,ev,p,c
    def test_justificativa_string_nunca_array_convertido(self):
        _,_,_,c=self.contexto();a=analise(c,versao=SCHEMA);validar(a,c)
        for value in (['Representação em lista'],[],{},None,'   '):
            bad=deepcopy(a);bad['justificativa']=value
            with self.assertRaisesRegex(ValueError,'justificativa'):validar(bad,c)
    def test_hash_direcao_refs_booleano_e_duplicata_seguem_rejeitados(self):
        _,_,_,c=self.contexto();a=analise(c,versao=SCHEMA)
        for modo in ('hash','direcao','fonte','bool','duplicata','clausula_sem_citacao','predicado_de_outra_regra'):
            bad=deepcopy(a)
            if modo=='hash':bad['contexto_hash']='inventado'
            if modo=='direcao':bad['avaliacao']['custo']['direcao']='zero'
            if modo=='fonte':bad['propostas'][0]['evidencias'][0]['localizador']='invisivel'
            if modo=='bool':bad['propostas'][1]['valor']=False
            if modo=='duplicata':bad['propostas'].append(deepcopy(bad['propostas'][0]))
            if modo=='clausula_sem_citacao':bad['propostas'][1]['evidencias']=[REF]
            if modo=='predicado_de_outra_regra':bad['propostas'][1]['condicoes'][0]['predicado']='outro'
            with self.subTest(modo=modo):
                with self.assertRaises(ValueError):validar(bad,c)
    def test_ausencia_e_lacuna_mesma_clausula_contradicao(self):
        _,_,_,c=self.contexto();a=analise(c,versao=SCHEMA)
        ob=c['escopos_regras'][0]['obrigacao_lacuna_id']
        a['propostas'].append(proposta(c,'registrar_lacuna_custo',ob,desconhecido(),'r_equiv'))
        with self.assertRaisesRegex(ValueError,'contraditórios'):validar(a,c)
    def test_ausencia_e_custo_positivo_vinculado_mesma_clausula_rejeitados(self):
        _,_,_,c=self.contexto();a=analise(c,versao=SCHEMA)
        a['propostas'][-1]['regra_refs']=['r_equiv']
        with self.assertRaisesRegex(ValueError,'contraditórios'):validar(a,c)
    def test_ausencia_uma_regra_nao_fecha_outra(self):
        e,ev,_,_=self.contexto(duas=True);p=construir(e,ev,execucao_id='mock_duas_clausulas')
        r=avaliar(e,ev,SimuladoV05(lambda c:analise(c,versao=SCHEMA)),p)
        self.assertEqual(r['execucao']['estado'],'parcial');self.assertTrue(any('r_extra'in x for x in r['lacunas']))
    def test_ausencia_uma_e_custo_desconhecido_outra_nao_viram_zero(self):
        e,ev,_,_=self.contexto(duas=True);p=construir(e,ev,execucao_id='mock_custos_distintos')
        def a(c):
            r=analise(c,versao=SCHEMA)
            if c['no_id']=='n_join':
                scope=next(x for x in c['escopos_regras']if x['regra_id']=='r_extra')
                r['propostas'].append(proposta(c,'registrar_lacuna_custo',scope['obrigacao_lacuna_id'],desconhecido('Preço da outra cláusula não informado'),'r_extra'))
            return r
        r=avaliar(e,ev,SimuladoV05(a),p)
        self.assertEqual(r['registro_operacional']['fechamento_final']['estado'],'completo_operacional_condicional')
        self.assertEqual(r['delta_dias']['valor'],2);self.assertIsNone(r['delta_centavos']['valor'])
        self.assertGreaterEqual(r['delta_centavos']['limites']['inferior'],11000)
    def test_confirmacoes_de_duas_regras_têm_escopos_distintos(self):
        e,ev,_,c=self.contexto(duas=True);a=analise(c,versao=SCHEMA)
        a['propostas'].append(proposta(c,'confirmar_ausencia_parcela_adicional','n_join',0,'r_extra'))
        validar(a,c)
        pm=dict(autorizacoes={p['id']:resumo(p)for p in a['propostas']},predicados=c['predicados'],requisitos_locais=[dict(no_id='n_join',regra_id=r['id'])for r in e['regras_locais']])
        r=calcular(e,ev,a['propostas'],pm,'mock_motor_escopado');self.assertEqual(r['execucao']['estado'],'ok',r)
    def test_pendencia_factual_fora_da_representacao_impede_fallback_baseline(self):
        e,ev=projeto();p=construir(e,ev,execucao_id='mock_pendencia_real')
        def a(c):
            r=analise(c,versao=SCHEMA)
            if c['no_id']=='n_alpha':r['pendencias_operacionais']=['Fato pertinente depende de relação não representada pelo catálogo']
            return r
        r=avaliar(e,ev,SimuladoV05(a),p)
        self.assertEqual(r['execucao']['estado'],'parcial');self.assertIsNone(r['delta_dias']['valor']);self.assertTrue(any('Pendência operacional'in x for x in r['lacunas']))
    def test_manutencao_e_substituicao_concorrentes_rejeitadas(self):
        _,_,_,c=self.contexto();a=analise(c,versao=SCHEMA)
        a['propostas'].append(proposta(c,'substituir_duracao','n_join',exato(9),'r_equiv'))
        with self.assertRaisesRegex(ValueError,'concorrentes'):validar(a,c)

class InterfaceV05(unittest.TestCase):
    def test_pedido_tipado_sem_conversao_sem_dados_de_referencia(self):
        e,ev=projeto();p=construir(e,ev,execucao_id='mock_prompt');c=montar_contexto(e,ev,execucao_id=p.execucao_id,no_id='n_join',revisao=1,**p.plano['n_join'])
        class T:
            versao_formato_local=VERSAO
            def __init__(self):self.requests=[]
            def __call__(self,req):
                self.requests.append(deepcopy(req));return RespostaTransporte(json.dumps(analise(c,versao=SCHEMA)),modelo='mock')
        t=T();r=LocalV05(t,modelo='mock',configuracao={},timeout_s=1).analisar(c);self.assertEqual(r['execucao']['estado'],'ok')
        req=t.requests[0];data=json.loads(req['mensagens'][1]['conteudo']);con=data['contrato_resposta']
        self.assertEqual(con['schema_version_resposta'],SCHEMA);self.assertIn('string não vazia',con['tipos_campos']['justificativa']);self.assertIn('pendencias_operacionais',con['campos_analise'])
        self.assertNotIn('avaliacao.custo deve',req['mensagens'][0]['conteudo'])
        self.assertEqual(r['execucao']['requisicao_adaptador_hash'],hash_json(req))
        for x in ('gabarito','delta_final','referencia_esperada'):self.assertNotIn(x,json.dumps(data))
        # Mesmo conteúdo científico em array continua rejeitado; jamais há join implícito.
        t.__class__.__call__=lambda self,req:RespostaTransporte(json.dumps({**analise(c,versao=SCHEMA),'justificativa':['texto em lista']}))
        rr=LocalV05(t,modelo='mock',configuracao={},timeout_s=1).analisar(c);self.assertEqual(rr['execucao']['estado'],'erro')
    def test_transportes_antigos_e_schema_antigo_nao_misturam_versoes(self):
        class T:versao_formato_local='4.0-formato-local'
        with self.assertRaises(ValueError):LocalV05(T(),modelo='mock',configuracao={},timeout_s=1)
        e,ev=projeto();p=construir(e,ev,execucao_id='mock_schema');c=montar_contexto(e,ev,execucao_id=p.execucao_id,no_id='n_join',revisao=1,**p.plano['n_join'])
        with self.assertRaises(ValueError):validar(analise(c),c)
