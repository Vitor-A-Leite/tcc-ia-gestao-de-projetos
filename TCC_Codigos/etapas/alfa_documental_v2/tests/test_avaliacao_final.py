"""Rodada final com HTTP prescrito, carteiras temporárias e rede bloqueada."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from ..scripts import avaliacao_final as AV
from ..src import avaliacao_final as AF
from ..src import ia_sozinha as D
from ..src import extracao as X
from ..src import lote_ia as lote
from ..src.ia_real import MODELO
from ..src.vendor.interpretacao_no.contratos import hash_json


class AvaliacaoFinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.gab = AF.carregar_gabarito()
        cls.textos = {t['id']: t['texto'] for d in AF.documentos_finais() for t in d['trechos']}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.pasta = self.root/'final'
        for nome in ('HISTORICO', 'LEDGER'):
            caminho = self.root/(nome+'.sqlite')
            with sqlite3.connect(caminho) as db:
                db.execute('CREATE TABLE chamadas(id TEXT PRIMARY KEY, rodada TEXT, estado TEXT, comprometido INTEGER, entrada INTEGER, saida INTEGER, segundos REAL, arquivo TEXT)')
            p = patch.object(lote, nome, caminho); p.start(); self.addCleanup(p.stop)
        for p in (patch('socket.socket', side_effect=AssertionError('Rede proibida no teste')),
                  patch.object(lote, 'ler_chave', side_effect=AssertionError('Credencial proibida no teste'))):
            p.start(); self.addCleanup(p.stop)
        self.pedidos = []
        self.falhar = set()
        self.m = AV.preparar(self.pasta, repeticoes=2)

    def http(self, path, pedido):
        self.pedidos.append((path, deepcopy(pedido)))
        if path:
            return {'input_tokens': 4000}
        nome = pedido['text']['format']['name']
        bruto = pedido['input'][1]['content']
        for proibido in ('gabarito', 'informacoes_ia1', 'estado_projetado', 'fim_novo', 'folgas_base', 'livro_parcelas'):
            self.assertNotIn(proibido, bruto)
        dados = json.loads(bruto)
        if nome == 'extracao_afirmacoes':
            doc = dados['documento']
            resp = dict(versao=X.VERSAO, documento_id=doc['id'], versao_documento=doc['versao'], afirmacoes=[],
                        nao_mapeados=[dict(trecho_id=t['id'], razao='sem_afirmacao_verificavel') for t in doc['trechos']])
            if doc['id'] in self.falhar:
                resp['documento_id'] = 'OUTRO'
        else:
            ev = dados['evento']['id']
            anot = []
            for d in dados['documentos']:
                for t in d['trechos']:
                    g = self.gab[(ev, t['id'])]
                    infos = [dict(citacao=self.textos[t['id']][:12], motivo=(g['motivos'] or ['valor_divergente'])[0], correto_seria='x')] if g['rotulo'] == 'REVISAR' else []
                    anot.append(dict(trecho_id=t['id'], rotulo=g['rotulo'], informacoes=infos, observacao=''))
            resp = dict(versao=D.VERSAO, anotacoes=anot)
        return dict(status='completed', model=MODELO, id='http-falso',
                    output=[dict(content=[dict(type='output_text', text=json.dumps(resp, ensure_ascii=False))])],
                    usage=dict(input_tokens=4000, output_tokens=1500))

    def executar(self, **kw):
        return AV.executar(self.pasta, autorizacao='Teste offline autorizado', http=self.http, **kw)

    def test_rodada_completa_metricas_e_retomada(self):
        self.assertEqual(self.m['chamadas_previstas'], 2*(7+45))
        r = self.executar()
        self.assertEqual(r['estado'], 'concluido')
        c = AV.ler(self.pasta/'comparacao.json')
        # D prescrita com o gabarito: acerto total. B sem afirmações: nada a revisar.
        self.assertEqual(c['repeticoes']['1']['D']['revisar']['f1'], 1.0)
        self.assertEqual(c['repeticoes']['1']['B']['revisar']['vp'], 0)
        self.assertEqual(c['repeticoes']['1']['B']['falhas'], 0)
        self.assertEqual(c['consumo']['B']['chamadas_api'], 14)
        self.assertEqual(c['consumo']['D']['chamadas_api'], 90)
        # E: B sem afirmações não contradiz D, então E herda os acertos de D.
        self.assertEqual(c['repeticoes']['1']['E']['revisar']['f1'], 1.0)
        self.assertEqual(c['B_voto']['revisar']['vp'], 0)
        self.assertEqual(c['modo_validacao'], 'parcial')
        carteira = lote.LEDGER.read_bytes()
        n = len(self.pedidos)
        self.executar()
        self.assertEqual(len(self.pedidos), n)
        self.assertEqual(lote.LEDGER.read_bytes(), carteira)

    def test_repeticoes_separadas_e_falha_contabilizada(self):
        self.falhar = {'RISK_REGISTER'}
        r1 = self.executar(repeticoes=[1])
        self.assertEqual(r1['estado'], 'parcial_aguardando_outras_repeticoes')
        self.assertFalse((self.pasta/'comparacao.json').exists())
        self.executar(repeticoes=[2])
        c = AV.ler(self.pasta/'comparacao.json')
        self.assertEqual(c['repeticoes']['1']['B']['falhas'], 4*15)
        self.assertEqual(c['erros']['B'], {'schema_invalido': 2})
        self.assertEqual(c['repeticoes']['1']['E']['falhas'], 0)  # D cobre o documento que B perdeu

    def test_manifesto_recusa_alteracao_e_exige_autorizacao(self):
        with self.assertRaises(Exception):
            AV.executar(self.pasta, autorizacao=' ', http=self.http)
        m = AV.ler(self.pasta/'manifesto.json')
        m['origens'] = {k: '0'*64 for k in m['origens']}
        m['hash'] = hash_json({k: v for k, v in m.items() if k != 'hash'})
        (self.pasta/'manifesto.json').write_text(json.dumps(m))
        with self.assertRaises(Exception):
            self.executar()
        self.assertEqual(self.pedidos, [])

    def test_retomada_tecnica_refaz_so_falhas_de_rede(self):
        from ..scripts import retomada_tecnica as RT
        from ..src.vendor.interpretacao_no.adaptadores import FalhaTransporte
        cair = {'D_F01_G1', 'D_F02_G2'}
        original = self.http
        def http(path, pedido):
            if not path:
                dados = json.loads(pedido['input'][1]['content'])
                if 'evento' in dados and f"D_{dados['evento']['id']}_G{1 if dados['documentos'][0]['id']=='STATUS_A' else 2 if dados['documentos'][0]['id']=='STATUS_C' else 3}" in cair:
                    cair.discard(f"D_{dados['evento']['id']}_G{1 if dados['documentos'][0]['id']=='STATUS_A' else 2 if dados['documentos'][0]['id']=='STATUS_C' else 3}")
                    raise FalhaTransporte('rede', 'queda simulada')
            return original(path, pedido)
        AV.executar(self.pasta, autorizacao='Teste', http=http, repeticoes=[1])
        self.assertEqual(AV.ler(self.pasta/'casos'/'r1_D_F01_G1.json')['estado'], 'falha')
        n = len(self.pedidos)
        r = RT.executar(self.pasta, autorizacao='Teste retomada', http=self.http)
        self.assertEqual(r['refeitas'], {'r1_D_F01_G1': 'concluido', 'r1_D_F02_G2': 'concluido'})
        self.assertEqual(len(r['pendentes']), 52)  # repetição 2 inteira
        self.assertTrue((self.pasta/'casos'/'_tentativas_originais'/'r1_D_F01_G1.json').exists())
        self.assertTrue((self.pasta/'comparacao.json').exists())
        n2 = len(self.pedidos)
        r = RT.executar(self.pasta, autorizacao='Teste retomada', http=self.http)  # nada a refazer
        self.assertEqual((r['refeitas'], r['pendentes']), ({}, {}))
        self.assertEqual(len(self.pedidos), n2)
        self.assertGreater(n2, n)

    def test_agregacao_b(self):
        docs = AF.documentos_finais()
        rev = dict(documentos=[dict(documento_id='STATUS_A', versao='1-final', afirmacoes=[
            dict(afirmacao=dict(trecho_id='STATUS_A.RESUMO'), estado='ja_atualizado'),
            dict(afirmacao=dict(trecho_id='STATUS_A.RESUMO'), estado='revisar'),
            dict(afirmacao=dict(trecho_id='STATUS_A.CUSTOS'), estado='nao_verificavel')]),
            dict(documento_id='RISK_REGISTER', versao='1-final', afirmacoes=[
            dict(afirmacao=dict(trecho_id='RISK_REGISTER.R1'), estado='julgamento_humano')]),
            dict(documento_id='DECISION_LOG', versao='1-final', afirmacoes=[])])
        r = AF.agregar_b(rev, docs)
        self.assertEqual(r['STATUS_A.RESUMO'], 'REVISAR')
        self.assertEqual(r['STATUS_A.CUSTOS'], 'CORRETO')
        self.assertEqual(r['STATUS_A.OBSERVACOES'], 'SEM_AFIRMACAO')
        self.assertEqual(r['RISK_REGISTER.R1'], 'DECISAO_HUMANA')
        self.assertEqual(r['DECISION_LOG.D1'], 'PRESERVAR')
        self.assertEqual(r['STATUS_B.RESUMO'], 'FALHA')


if __name__ == '__main__':
    unittest.main()
