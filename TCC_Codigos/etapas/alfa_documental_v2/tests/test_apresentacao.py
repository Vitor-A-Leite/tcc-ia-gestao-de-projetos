"""Compactação sem perda e incorporação operacional; nenhuma inferência real."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import ROOT
from ..src.apresentacao import compactar, expandir, registrar_incorporadas, INSTRUCOES
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.pipeline import simular
from ..src.vendor.hibrido_v07_r3.schema import formato


class ApresentacaoTests(unittest.TestCase):
    def registros(self):
        for p in sorted((ROOT/'outputs/ia_real_20261110T050151Z').glob('*.json')):
            d = json.loads(p.read_text())
            if 'pedido' in d and d['etiqueta'] != 'sugestao_entrada':
                yield d

    def test_reconstrucao_exata_todas_chamadas_historicas(self):
        registros = list(self.registros())
        self.assertEqual(len(registros), 13)
        for r in registros:
            with self.subTest(no=r['etiqueta']):
                dados = json.loads(r['pedido']['input'][1]['content'])
                original = deepcopy(dados)
                compacto = compactar(dados)
                self.assertEqual(expandir(compacto), original)
                self.assertEqual(dados, original)
                self.assertEqual(compacto, compactar(dados))
                self.assertNotIn('responsabilidades_operacionais', compacto['contrato_resposta'])
                self.assertLess(len(json.dumps(compacto)), len(json.dumps(dados)))

    def test_refs_mantem_ordem_e_rejeitam_catalogo_incompleto(self):
        a = {'fonte_id': 'A', 'localizador': '1'}
        b = {'fonte_id': 'B', 'localizador': '2'}
        d = dict(contexto={'responsabilidades_operacionais': []}, contrato_resposta={'responsabilidades_operacionais': []},
                 valores=[[a,b],[a,b],[b,a],[]])
        c = compactar(d)
        self.assertEqual(expandir(c), d)
        c['conjuntos_evidencias'] = {}
        with self.assertRaises(KeyError): expandir(c)

    def test_estado_incorporado_so_depois_da_aplicacao(self):
        r = simular('D02')
        passos = {p['no_id']: p for p in r['rastro_orquestracao'] if 'contexto' in p}
        self.assertEqual(passos['SUP_MOTOR']['contexto']['alteracoes_incorporadas'], [])
        for no in ('C_MOTOR', 'T_ASSEMBLY', 'M_VALIDATION', 'T_DOC', 'M_RELEASE'):
            c = passos[no]['contexto']
            propostas = c['alteracoes_incorporadas']
            p = next(p for p in propostas if p['alvo_id'] == 'release_SUP_MOTOR')
            self.assertEqual(p['valor']['valor'],25)
            self.assertEqual(p['evento_id'],'D02')
            self.assertEqual(p['suporte_semantico'],'nao_auditado')
            fontes = {(f['id'],f['localizador']) for f in c['fontes']}
            self.assertTrue(all((e['fonte_id'],e['localizador']) in fontes for e in p['evidencias']))
        self.assertEqual(registrar_incorporadas([], 'novo_evento'), [])
        self.assertEqual(r['fim_novo']['valor'],45)

    def test_transporte_envia_compacto_schema_e_parser_preservados(self):
        r = next(self.registros())
        dados = json.loads(r['pedido']['input'][1]['content'])
        req = dict(modelo=MODELO, configuracao=CONFIG, mensagens=[
            {'papel':'sistema','conteudo':r['pedido']['input'][0]['content']},
            {'papel':'usuario','conteudo':json.dumps(dados)}])
        calls=[]
        def http(path, payload):
            calls.append((path, deepcopy(payload)))
            if path: return {'input_tokens':100}
            return dict(status='completed', model=MODELO, id='teste', output=[], usage={'input_tokens':100,'output_tokens':0})
        with tempfile.TemporaryDirectory() as tmp, patch('socket.socket', side_effect=AssertionError('Rede proibida')):
            t=TransporteReal(Path(tmp)/'run','segredo_teste',0,http=http)
            self.addCleanup(t.db.close)
            t(req)
            payload=calls[1][1]
            self.assertEqual(expandir(json.loads(payload['input'][1]['content'])),dados)
            self.assertEqual(payload['text']['format'],formato(dados['contexto']))
            self.assertTrue(payload['input'][0]['content'].endswith(INSTRUCOES))
            self.assertEqual(calls[0][1]['input'], payload['input'])
            self.assertIn('fatos novos',payload['input'][0]['content'])
            salvo=json.loads(next((Path(tmp)/'run').glob('*.json')).read_text())
            self.assertEqual(salvo['pedido'],payload)
