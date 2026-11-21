"""Novo lote v3 com transporte simulado e carteiras isoladas."""
import unittest

from ..scripts import avaliar_revisor_v3 as avaliacao
from ..src import lote_ia as lote
from . import test_avaliar_revisor_v2 as testes_executor


class AvaliacaoRevisorV3Tests(unittest.TestCase):
    def setUp(self):
        testes_executor.AvaliacaoRevisorTests.setUp(self)
        self.pasta = self.root/'avaliacao_v3'
        self.manifesto = avaliacao.preparar(self.pasta)

    def http(self, path, pedido):
        return testes_executor.AvaliacaoRevisorTests.http(self, path, pedido)

    def test_28_casos_comparacao_e_retomada_preservam_historicos(self):
        anterior = {p: lote.sha(p) for p in avaliacao.ANTERIOR.rglob('*.json')}
        self.assertEqual(len(self.manifesto['entradas']), 28)
        self.assertEqual(self.manifesto['teto_rodada_nano'], 420_000_000)
        resultado = avaliacao.executar(self.pasta, autorizacao='Teste offline', http=self.http)
        self.assertEqual(resultado['estado'], 'concluido')
        resumo = avaliacao.executor.ler(self.pasta/'comparacao.json')
        self.assertEqual(resumo['anterior']['validos'], 19)
        self.assertEqual(resumo['resultados']['coleta']['validos'], 19)
        self.assertEqual(resumo['resultados']['controle']['validos'], 9)
        self.assertEqual(len(resumo['regressoes_escopo']), 4)
        self.assertTrue(all(r['concordante'] for r in resumo['regressoes_escopo']))
        avaliacao.executar(self.pasta, autorizacao='Teste de retomada offline', http=self.http)
        self.assertEqual(len(self.pedidos), 56)
        self.assertEqual(anterior, {p: lote.sha(p) for p in anterior})

    def test_controles_tem_ids_neutros_e_cadastro_congelado(self):
        for entrada in self.manifesto['entradas']:
            if entrada['grupo'] == 'controle' and entrada['id'] != 'N01':
                pacote = avaliacao.executor.ler(self.pasta/entrada['arquivo'])['pacote']
                self.assertEqual(pacote['proposta']['id'], 'controle_'+entrada['id']+'_proposta')
        self.assertIn('data/projetos/alfa/escopo_revisao.json', self.manifesto['codigo'])
        self.assertIn('scripts/avaliar_revisor_v3.py', self.manifesto['codigo'])
