import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from observatorio import Observatorio, quantidade, ROOT


class ObservatorioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.obs=Observatorio()

    def test_oito_eventos_pelo_contrato_h_sem_api(self):
        for caso in self.obs.casos:
            with self.subTest(caso=caso):
                d=self.obs.executar(caso)
                r=d['resultado']
                self.assertEqual(r['condicao'],'H')
                self.assertEqual(r['evento_id'],self.obs.casos[caso]['evento_id'])
                self.assertEqual(r['execucao']['origem'],'simulado')
                self.assertEqual(r['consumo']['chamadas'],0)
                self.assertIn(r['execucao']['estado'],('ok','parcial'))
                self.assertEqual(len(d['nos']),7)
                self.assertEqual(len(d['grafo']['arcos_causais']),5)
                self.assertEqual(len({p['original']['parcela_id'] for p in d['parcelas']}),len(d['parcelas']))
                json.dumps(d,allow_nan=False)

    def test_prazo_convergencia_custo_e_evidencia(self):
        d=self.obs.executar('k_09c2');r=d['resultado']
        self.assertEqual(r['delta_dias']['valor'],2)
        self.assertEqual(r['delta_centavos']['valor'],40000)
        self.assertEqual(d['resumo'][1]['depois'],'R$ 5.400,00')
        montagem=next(n for n in d['nos'] if n['nome']=='Montar bancada')
        self.assertEqual(len(montagem['passo']['contexto']['entradas_correntes']),2)
        self.assertIn('SIMULADA',montagem['passo']['analise']['justificativa'])
        self.assertTrue(montagem['passo']['contexto']['fontes'])

    def test_parcial_operacional_nao_zero(self):
        d=self.obs.executar('k_09c2','parcial');r=d['resultado']
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertIsNone(r['delta_dias']['valor'])
        self.assertEqual(d['resumo'][0]['delta'],'Indeterminado')
        self.assertEqual(d['politica']['limite_analises'],1)
        self.assertTrue(any(n['estado']=='bloqueado' for n in d['nos']))

    def test_erro_operacional_nao_zero(self):
        d=self.obs.executar('k_09c2','erro');r=d['resultado']
        self.assertEqual(r['execucao']['estado'],'erro')
        self.assertTrue(r['execucao']['erros'])
        self.assertNotIn('delta_dias',r)
        self.assertEqual(d['resumo'][0]['delta'],'Não disponível')
        self.assertEqual(d['parcelas'],[])
        self.assertIn('inexistente',d['politica']['alvos'][0])

    def test_indeterminacao_limite_e_reducao(self):
        for c in ('k_23d8','k_8c65'):
            d=self.obs.executar(c)
            self.assertIn('≥ +R$ 200,00',d['resumo'][1]['delta'])
            self.assertIsNone(d['resultado']['delta_centavos']['valor'])
        d=self.obs.executar('k_f04b')
        self.assertEqual(d['resultado']['delta_dias']['valor'],-1)
        self.assertEqual(d['resumo'][1]['delta'],'−R$ 100,00')

    def test_formatacao_sem_imputacao(self):
        self.assertEqual(quantidade(None),'Não disponível')
        self.assertEqual(quantidade({'estado':'exato','valor':0},True),'R$ 0,00')
        self.assertEqual(quantidade({'estado':'inaplicavel'}),'Inaplicável')
        with self.assertRaises(ValueError): quantidade({'estado':'exato','valor':True})

    def test_identidade_rejeitada(self):
        from orquestracao.simulacao import politica_prescrita
        from observatorio import ler
        d=self.obs.executar('k_09c2');f=ler(self.obs.fixtures/'k_09c2.json')
        for campo in ('evento_id','projeto_id','versao','snapshot_hash','view_hash','condicao'):
            r=deepcopy(d['resultado']);r[campo]='divergente'
            with self.subTest(campo=campo),self.assertRaises(ValueError):
                self.obs.apresentar(r,f,d['views'],'normal',politica_prescrita(f))

    def test_nao_abre_referencias_no_caminho_predicao(self):
        import observatorio
        original=observatorio.ler
        def isolado(p):
            self.assertNotIn('referencias',str(p));self.assertNotIn('outputs',str(p))
            return original(p)
        with patch.object(observatorio,'ler',side_effect=isolado):
            obs=Observatorio();d=obs.executar('k_09c2')
        self.assertNotIn('referencias',d)
        self.assertIn('Sem execução',d['condicoes']['B'])
        self.assertEqual(set(d['views']),{'B','H','T'})

    def test_selecao_invalida_e_isolamento(self):
        before=deepcopy(self.obs.estado)
        for c,m in [('../referencias/gabaritos','normal'),('k_09c2','real'),('k_09c2','')]:
            with self.assertRaises(ValueError): self.obs.executar(c,m)
        a=self.obs.executar('k_b731');b=self.obs.executar('k_09c2')
        self.assertNotEqual(a['resultado']['execucao_id'],b['resultado']['execucao_id'])
        self.assertEqual(self.obs.estado,before)
        self.assertEqual(a['resultado']['delta_centavos']['valor'],0)

    def test_avaliacao_dataset_separado_preserva_denominadores(self):
        d=self.obs.avaliacao()
        self.assertIn('sintéticos',d['aviso'])
        self.assertEqual(d['arquivos']['manifesto']['uso'],'teste_prescrito')
        for m in d['arquivos']['metricas']['metricas'].values():
            self.assertEqual(m['N'],8)
            self.assertEqual(m['estados']['erro'],1)
            self.assertEqual(m['estados']['invalido'],1)
        self.assertIn('referencias_sinteticas',d['arquivos'])

    def test_apresentacao_legivel_preserva_resultado_original(self):
        from interpretacao_no.contratos import hash_json
        d=self.obs.executar('k_09c2')
        self.assertEqual(hash_json(d['resultado']),d['identidades']['resultado_hash'])
        n=next(n for n in d['nos'] if n['nome']=='Montar bancada')
        self.assertEqual(n['campos'][0]['depois'],'7 (dia corrido)')
        self.assertEqual(len(n['predecessores']),2)
        self.assertEqual(n['propostas_apresentacao'][n['passo']['analise']['propostas'][0]['id']],'3 (dia corrido)')
        self.assertNotIn('apresentacao_valor',next(t for t in d['resultado']['rastro_orquestracao'] if t['no_id']==n['id'])['analise']['propostas'][0])
        self.assertIn('Oficina',self.obs.catalogo()['casos'][0]['resumo'])
        fornecedor=next(n for n in d['nos'] if n['tipo']=='fornecedor')
        self.assertIn('Não se aplica',fornecedor['campos'][0]['depois'])

    def test_regra_base_distinta_dos_termos_do_evento(self):
        for caso,esperado in [('k_547a','Base contratada: 12 dias'),('k_8c65','Taxa: desconhecida')]:
            d=self.obs.executar(caso)
            self.assertEqual(d['regras']['regras_custo'][0]['base_contratada_dias'],10)
            self.assertEqual(d['regras']['regras_custo'][0]['taxa_centavos_dia'],10000)
            self.assertIn(esperado,d['alteracoes_contratuais'][0]['parametros'])
            self.assertEqual(d['alteracoes_contratuais'][0]['decisao'],'aceita')
            self.assertTrue(d['alteracoes_contratuais'][0]['fontes'])
        self.assertEqual(self.obs.executar('k_547a')['resultado']['delta_centavos']['valor'],0)

    def test_ui_sem_html_injetado_ou_aritmetica_cientifica(self):
        js=(ROOT/'visualizacao/observatorio_quantitativo/app.js').read_text()
        self.assertNotIn('innerHTML',js)
        self.assertNotIn('eval(',js)
        self.assertIn('textContent',js)
        self.assertNotIn('Math.max',js)


if __name__=='__main__':unittest.main()
