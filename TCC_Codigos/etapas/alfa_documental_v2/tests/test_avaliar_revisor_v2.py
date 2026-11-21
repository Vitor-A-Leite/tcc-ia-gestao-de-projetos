"""Comparação e retomada com HTTP prescrito e carteiras temporárias."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from ..scripts import avaliar_revisor_v2 as avaliacao
from ..src import lote_ia as lote
from ..src.ia_real import MODELO
from ..src.vendor.interpretacao_no.adaptadores import FalhaTransporte
from .test_revisao import resposta_prescrita


class AvaliacaoRevisorTests(unittest.TestCase):
    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.root = Path(temporario.name)
        self.pasta = self.root/'avaliacao'
        for nome in ('HISTORICO', 'LEDGER'):
            caminho = self.root/(nome+'.sqlite')
            with sqlite3.connect(caminho) as db:
                db.execute('CREATE TABLE chamadas(id TEXT PRIMARY KEY, rodada TEXT, estado TEXT, comprometido INTEGER, entrada INTEGER, saida INTEGER, segundos REAL, arquivo TEXT)')
            alteracao = patch.object(lote, nome, caminho)
            alteracao.start()
            self.addCleanup(alteracao.stop)
        for alteracao in (
            patch('socket.socket', side_effect=AssertionError('Rede proibida no teste')),
            patch.object(lote, 'ler_chave', side_effect=AssertionError('Credencial proibida no teste')),
        ):
            alteracao.start()
            self.addCleanup(alteracao.stop)
        self.pedidos = []
        self.manifesto = avaliacao.preparar(self.pasta)

    def http(self, path, pedido):
        self.pedidos.append((path, deepcopy(pedido)))
        if path:
            return {'input_tokens': 100}
        pacote = json.loads(pedido['input'][1]['content'])
        self.assertNotIn('referencia_autoral', pacote)
        self.assertNotIn('anterior', pacote)
        self.assertNotIn('esperado', pacote)
        self.assertNotIn('Variante sintética', json.dumps(pedido))
        resposta = resposta_prescrita(pacote)
        return dict(status='completed', model=MODELO, id='http-falso',
                    output=[dict(content=[dict(type='output_text', text=json.dumps(resposta))])],
                    usage=dict(input_tokens=100, output_tokens=20))

    def executar(self, http=None):
        return avaliacao.executar(self.pasta, autorizacao='Teste offline autorizado', http=http or self.http)

    def test_comparacao_completa_retoma_sem_novo_consumo(self):
        historico = lote.HISTORICO.read_bytes()
        self.assertEqual(len(self.manifesto['entradas']), 23)
        self.assertEqual(self.manifesto['teto_rodada_nano'], 345_000_000)
        resultado = self.executar()
        self.assertEqual(resultado['estado'], 'concluido')
        resumo = avaliacao.ler(self.pasta/'comparacao.json')
        self.assertEqual(resumo['anterior']['validos'], 10)
        self.assertEqual(resumo['resultados']['coleta']['validos'], 19)
        self.assertEqual(resumo['resultados']['controle']['validos'], 4)
        # Todas as respostas prescritas são favoráveis, inclusive os controles negativos.
        self.assertEqual(resumo['controles_concordantes'], 0)
        self.assertTrue(resumo['originais_preservados'])
        for caso in resumo['casos']:
            self.assertEqual(caso['cobertura']['aspectos_avaliados'], 7)
            self.assertEqual(caso['cobertura']['fontes_citadas'], caso['cobertura']['fontes_citadas_examinadas'])
        registros = {p: p.read_bytes() for p in (self.pasta/'casos').glob('*.json')}
        carteira = lote.LEDGER.read_bytes()
        self.executar()
        self.assertEqual(len(self.pedidos), 46)
        self.assertEqual(lote.LEDGER.read_bytes(), carteira)
        self.assertEqual(lote.HISTORICO.read_bytes(), historico)
        self.assertEqual(registros, {p: p.read_bytes() for p in registros})

    def test_interrupcao_retoma_casos_pendentes_preservando_reserva(self):
        def interromper(path, pedido):
            if not path:
                raise KeyboardInterrupt('Interrupção prescrita')
            return self.http(path, pedido)

        with self.assertRaises(KeyboardInterrupt):
            self.executar(interromper)
        primeiro = self.pasta/'casos/D01-01.json'
        antes = primeiro.read_bytes()
        self.assertIsNone(avaliacao.ler(primeiro)['revisao'])
        self.assertEqual(lote.comprometido(lote.LEDGER), 15_000_000)
        resultado = self.executar()
        self.assertEqual(resultado['estado'], 'concluido_com_falhas')
        self.assertEqual(primeiro.read_bytes(), antes)
        with sqlite3.connect(lote.LEDGER) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM chamadas').fetchone()[0], 23)
            self.assertEqual(db.execute("SELECT count(*) FROM chamadas WHERE estado='reservada'").fetchone()[0], 1)
        self.assertAlmostEqual(avaliacao.ler(self.pasta/'comparacao.json')['consumo']['comprometido_api_usd'],
                               lote.comprometido(lote.LEDGER)/1e9)

    def test_falha_de_um_caso_fica_registrada_sem_repeticao(self):
        def falhar_primeiro(path, pedido):
            if not self.pedidos:
                self.pedidos.append((path, deepcopy(pedido)))
                raise FalhaTransporte('rede', 'Falha prescrita')
            return self.http(path, pedido)

        resultado = self.executar(falhar_primeiro)
        self.assertEqual(resultado['estado'], 'concluido_com_falhas')
        resumo = avaliacao.ler(self.pasta/'comparacao.json')
        self.assertEqual(resumo['resultados']['coleta']['invalidos'], 1)
        self.assertEqual(resumo['resultados']['coleta']['validos'], 18)
        self.assertEqual(resumo['erros'], {'rede': 1})
        antes = len(self.pedidos)
        self.executar()
        self.assertEqual(len(self.pedidos), antes)

    def test_manifesto_entrada_e_codigo_obsoletos_bloqueiam(self):
        with patch.object(avaliacao, 'hashes_codigo', return_value={}):
            with self.assertRaisesRegex(ValueError, 'Implementação mudou'):
                self.executar()
        entrada = self.pasta/self.manifesto['entradas'][0]['arquivo']
        entrada.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Entrada mudou'):
            self.executar()
        self.assertEqual(self.pedidos, [])
        self.assertEqual(lote.comprometido(lote.LEDGER), 0)

    def test_teto_global_confere_carteira_atual_antes_da_api(self):
        caso = avaliacao.ler(self.pasta/self.manifesto['entradas'][0]['arquivo'])
        with sqlite3.connect(lote.LEDGER) as db:
            db.execute('INSERT INTO chamadas VALUES(?,?,?,?,?,?,?,?)',
                       ('antiga', 'antiga', 'reservada', 19_999_000_000, None, None, 0, 'antiga.json'))
        registro = avaliacao.avaliar_caso(self.pasta, caso, self.manifesto, 'ficticia', http=self.http)
        self.assertEqual(registro['revisao']['erros'][0]['codigo'], 'orcamento')
        self.assertEqual(self.pedidos, [])
        self.assertEqual(lote.comprometido(lote.LEDGER), 19_999_000_000)
        with self.assertRaisesRegex(ValueError, 'Saldo insuficiente'):
            avaliacao.preparar(self.root/'sem_saldo')
