"""Rodada de extração com HTTP prescrito, carteiras temporárias e rede bloqueada."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from ..scripts import avaliar_extracao as AX
from ..src import lote_ia as lote
from ..src.ia_real import MODELO
from .test_conteudo import referencia, resposta_de


class AvaliarExtracaoTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.pasta = self.root/'extracao'
        for nome in ('HISTORICO', 'LEDGER'):
            caminho = self.root/(nome+'.sqlite')
            with sqlite3.connect(caminho) as db:
                db.execute('CREATE TABLE chamadas(id TEXT PRIMARY KEY, rodada TEXT, estado TEXT, comprometido INTEGER, entrada INTEGER, saida INTEGER, segundos REAL, arquivo TEXT)')
            p = patch.object(lote, nome, caminho); p.start(); self.addCleanup(p.stop)
        for p in (patch('socket.socket', side_effect=AssertionError('Rede proibida no teste')),
                  patch.object(lote, 'ler_chave', side_effect=AssertionError('Credencial proibida no teste'))):
            p.start(); self.addCleanup(p.stop)
        self.pedidos = []
        self.alterar = None
        self.manifesto = AX.preparar(self.pasta)

    def http(self, path, pedido):
        self.pedidos.append((path, deepcopy(pedido)))
        if path:
            return {'input_tokens': 3000}
        bruto = pedido['input'][1]['content']
        for proibido in ('estados_esperados', 'revisar', 'premissa_alterada', 'fim_novo', 'Referência de desenvolvimento'):
            self.assertNotIn(proibido, bruto)
        doc = json.loads(bruto)['documento']
        resposta = resposta_de(referencia(doc['id'], doc['versao']))
        if self.alterar:
            self.alterar(doc, resposta)
        return dict(status='completed', model=MODELO, id='http-falso',
                    output=[dict(content=[dict(type='output_text', text=json.dumps(resposta, ensure_ascii=False))])],
                    usage=dict(input_tokens=3000, output_tokens=900))

    def executar(self):
        return AX.executar(self.pasta, autorizacao='Teste offline autorizado', http=self.http)

    def test_rodada_completa_reproduz_referencia_e_retoma_sem_gasto(self):
        self.assertEqual(len(self.manifesto['entradas']), 6)
        self.assertEqual(self.manifesto['teto_rodada_nano'], 6*15_000_000)
        r = self.executar()
        self.assertEqual(r['estado'], 'concluido')
        resumo = AX.ler(self.pasta/'comparacao.json')
        self.assertEqual((resumo['extracao']['falsos_positivos'], resumo['extracao']['falsos_negativos']), (0, 0))
        self.assertEqual(resumo['condicao_B']['estado_e_motivo_iguais'], resumo['condicao_B']['afirmacoes'])
        self.assertEqual(resumo['condicao_B']['afirmacoes'], 117)
        self.assertEqual(resumo['consumo']['chamadas_api'], 6)
        carteira = lote.LEDGER.read_bytes()
        self.executar()
        self.assertEqual(len(self.pedidos), 12)  # contagem + geração por documento, sem repetição
        self.assertEqual(lote.LEDGER.read_bytes(), carteira)

    def test_extracao_errada_aparece_na_condicao_b(self):
        def alterar(doc, resposta):
            if doc['id'] == 'STATUS' and doc['versao'] == '1-prosa':
                # IA perde a frase qualitativa e erra o valor do lançamento.
                resposta['afirmacoes'] = [a for a in resposta['afirmacoes'] if a['predicado'] != 'no_prazo']
                next(a for a in resposta['afirmacoes'] if a['citacao'] == 'lançamento previsto para o dia 40')['valor'] = 45
                resposta['nao_mapeados'] = resposta['nao_mapeados']
        self.alterar = alterar
        self.executar()
        b = AX.ler(self.pasta/'comparacao.json')['condicao_B']
        omitidas = [d for d in b['divergencias'] if d['obtido']['estado'] == 'omitida']
        self.assertEqual({d['afirmacao'] for d in omitidas}, {'SRP.RESUMO#1'})
        self.assertEqual(len(omitidas), 8)  # todos os cenários com STATUS@1-prosa
        d02 = next(d for d in b['divergencias'] if d['cenario'] == 'D02' and d['afirmacao'] == 'SRP.RESUMO#2')
        self.assertEqual(d02['obtido']['estado'], 'ja_atualizado')  # valor errado mascara a desatualização
        self.assertGreater(b['revisar_fn'], 0)

    def test_resposta_invalida_e_falha_registrada_sem_repetir(self):
        def alterar(doc, resposta):
            if doc['id'] == 'RISK':
                resposta['afirmacoes'][0]['citacao'] = 'texto inventado'
        self.alterar = alterar
        r = self.executar()
        self.assertEqual(r['estado'], 'concluido_com_falhas')
        resumo = AX.ler(self.pasta/'comparacao.json')
        self.assertEqual(resumo['extracao']['erros'], {'citacao_nao_literal': 1})
        self.assertTrue(any(d['obtido']['estado'] == 'extracao_invalida' for d in resumo['condicao_B']['divergencias']))

    def test_manifesto_recusa_codigo_ou_referencia_alterados(self):
        m = AX.ler(self.pasta/'manifesto.json')
        m['origens'] = {k: '0'*64 for k in m['origens']}
        from ..src.vendor.interpretacao_no.contratos import hash_json
        m['hash'] = hash_json({k: v for k, v in m.items() if k != 'hash'})
        (self.pasta/'manifesto.json').write_text(json.dumps(m))
        with self.assertRaises(Exception):
            self.executar()
        self.assertEqual(self.pedidos, [])

    def test_autorizacao_obrigatoria(self):
        with self.assertRaises(Exception):
            AX.executar(self.pasta, autorizacao='  ', http=self.http)
        self.assertEqual(self.pedidos, [])


if __name__ == '__main__':
    unittest.main()
