"""Regressões dos registros reais e contrato v2 com respostas prescritas offline."""
from collections import Counter
from copy import deepcopy
from functools import partial
import json
from pathlib import Path
import tempfile
import unittest

from ..src import ROOT
from ..src.auditoria import auditar_arquivo, auditar_resultado
from ..src.pipeline import simular
from ..src.revisao import (ASPECTOS, ErroRevisao, RevisorIA, VERSAO_V2 as VERSAO, VERSAO_LEGADA,
                          conferir_pacote, formato_parecer as formato_atual, validar_parecer)
from ..src.vendor.interpretacao_no.contratos import hash_json
from .test_revisao import TransporteTeste, resposta_prescrita as resposta_atual, revisor_teste as revisor_atual

resposta_prescrita = partial(resposta_atual, versao=VERSAO)
revisor_teste = partial(revisor_atual, versao=VERSAO)
formato_parecer = partial(formato_atual, versao=VERSAO)


class RevisaoV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origem = ROOT/'outputs/lote_desenvolvimento_revisoes_finais_20261110'
        cls.historicos = [registro for path in sorted(cls.origem.glob('D*/auditoria.json'))
                          for registro in json.loads(path.read_text())['registros']]
        cls.pacote = deepcopy(cls.historicos[0]['pacote'])

    def conferir_erro(self, resposta, codigo, caminho=None, pacote=None):
        with self.assertRaises(ErroRevisao) as capturada:
            validar_parecer(resposta, pacote or self.pacote)
        self.assertEqual(capturada.exception.codigo, codigo)
        if caminho:
            self.assertEqual(capturada.exception.caminho, caminho)

    def test_releitura_v1_reproduz_dez_validos_e_nove_rejeitados(self):
        contagem = Counter()
        for registro in self.historicos:
            pacote = registro['pacote']
            resposta = json.loads(registro['revisao_semantica']['resposta_bruta'])
            try:
                validado = validar_parecer(resposta, pacote)
                self.assertEqual(validado, resposta)
                contagem['valido'] += 1
            except ValueError as exc:
                contagem[str(exc)] += 1
        self.assertEqual(contagem, Counter({
            'valido': 10, 'Entidade/alvo/atributo sustentado divergente': 6,
            'Citação não literal da fonte original': 3}))

    def test_dezenove_pacotes_recuperam_identidade_e_citacoes_exatas(self):
        for historico in self.historicos:
            pacote = historico['pacote']
            antes = deepcopy(pacote)
            bruto = resposta_prescrita(pacote)
            validado = validar_parecer(bruto, pacote)
            self.assertEqual(validado['entidade_sustentada'], pacote['proposta']['no_id'])
            self.assertEqual(validado['alvo_sustentado'], pacote['proposta']['alvo_id'])
            self.assertEqual(validado['valor_sustentado'], pacote['proposto'])
            fontes = {fonte['id']: fonte for fonte in pacote['fontes']}
            for fonte in validado['fontes_examinadas']:
                original = fontes[fonte['fonte_id']]
                self.assertEqual(fonte['trecho_citado'], original['trecho'])
                for campo in ('documento_id', 'versao', 'localizador'):
                    self.assertEqual(fonte[campo], original[campo])
            self.assertEqual(pacote, antes)
            self.assertNotIn('entidade_sustentada', bruto)
            self.assertNotIn('trecho_citado', json.dumps(bruto))

    def test_esquema_restringe_referencias_e_aspectos(self):
        esquema = formato_parecer(self.pacote)['schema']['properties']
        self.assertEqual(set(esquema['aspectos']['properties']), set(ASPECTOS))
        ids = [fonte['id'] for fonte in self.pacote['fontes']]
        self.assertEqual(esquema['fontes_examinadas']['items']['enum'], ids)
        for aspecto in esquema['aspectos']['properties'].values():
            self.assertEqual(aspecto['properties']['fonte_ids']['items']['enum'], ids)

    def test_fonte_inventada_duplicada_ou_nao_examinada(self):
        resposta = resposta_prescrita(self.pacote)
        resposta['fontes_examinadas'] = ['INVENTADA']
        self.conferir_erro(resposta, 'fonte_invalida', 'fontes_examinadas[0]')
        resposta = resposta_prescrita(self.pacote)
        resposta['fontes_examinadas'] *= 2
        self.conferir_erro(resposta, 'fonte_duplicada', 'fontes_examinadas')
        resposta = resposta_prescrita(self.pacote)
        outra = next(f['id'] for f in self.pacote['fontes'] if f['id'] not in resposta['fontes_examinadas'])
        resposta['aspectos']['atributo']['fonte_ids'] = [outra]
        self.conferir_erro(resposta, 'fonte_nao_examinada', 'aspectos.atributo')

    def test_favoravel_exige_suporte_em_todos_aspectos_e_cobertura(self):
        for nome in ASPECTOS:
            resposta = resposta_prescrita(self.pacote)
            resposta['aspectos'][nome]['estado'] = 'insuficiente'
            self.conferir_erro(resposta, 'parecer_inconsistente', 'aspectos')
        resposta = resposta_prescrita(self.pacote)
        resposta['aspectos']['valor']['fonte_ids'] = []
        self.conferir_erro(resposta, 'evidencia_ausente', 'aspectos.valor')
        resposta = resposta_prescrita(self.pacote)
        resposta['suporte_ausente'] = ['Magnitude ausente']
        self.conferir_erro(resposta, 'parecer_inconsistente', 'suporte_ausente')
        resposta = resposta_prescrita(self.pacote)
        outra = next(f['id'] for f in self.pacote['fontes'] if f['id'] not in resposta['fontes_examinadas'])
        resposta['fontes_examinadas'] = [outra]
        for aspecto in resposta['aspectos'].values():
            aspecto['fonte_ids'] = [outra]
        self.conferir_erro(resposta, 'cobertura_incompleta', 'fontes_examinadas')

    def test_propagacao_e_nao_aplicabilidade_nao_sustentam_alteracao_local(self):
        resposta = resposta_prescrita(self.pacote)
        resposta['tipo_efeito'] = 'propagacao'
        self.conferir_erro(resposta, 'efeito_incompativel', 'tipo_efeito')
        resposta = resposta_prescrita(self.pacote)
        resposta['aspectos']['atributo']['estado'] = 'nao_aplicavel'
        self.conferir_erro(resposta, 'aspecto_inconsistente', 'aspectos.atributo')
        montagem = self.historicos[1]['pacote']
        resposta = resposta_prescrita(montagem)
        resposta['aspectos']['condicoes']['estado'] = 'nao_aplicavel'
        self.conferir_erro(resposta, 'aspecto_inconsistente', 'aspectos.condicoes', pacote=montagem)

    def test_conclusoes_negativas_exigem_aspecto_compativel(self):
        for parecer in ('contradita', 'ambigua', 'suporte_insuficiente'):
            resposta = resposta_prescrita(self.pacote, parecer)
            validado = validar_parecer(resposta, self.pacote)
            self.assertEqual(validado['parecer'], parecer)
            self.assertIsNone(validado['atributo_sustentado'])
            resposta['aspectos']['atributo']['estado'] = 'sustentado'
            self.conferir_erro(resposta, 'parecer_inconsistente', 'parecer')

    def test_vinculo_schema_e_localizacao_dos_erros(self):
        resposta = resposta_prescrita(self.pacote)
        resposta['contexto_hash'] = 'outro'
        self.conferir_erro(resposta, 'vinculo_invalido', 'contexto_hash')
        resposta = resposta_prescrita(self.pacote)
        resposta['aspectos']['valor']['estado'] = 'talvez'
        self.conferir_erro(resposta, 'schema_invalido', '$.aspectos.valor.estado')
        resposta = resposta_prescrita(self.pacote)
        resposta['aspectos']['entidade']['fonte_ids'] = ['INVENTADA']
        self.conferir_erro(resposta, 'fonte_invalida', 'aspectos.entidade.fonte_ids[0]')

    def test_objeto_adulterado_e_downgrade_bloqueados_antes_de_aceite(self):
        resultado = auditar_resultado(simular('D02'))
        pacote = resultado['registros'][0]['pacote']
        pacote['objeto_avaliado']['entidade'] = 'OUTRO'
        pacote['pacote_hash'] = hash_json({k: v for k, v in pacote.items() if k != 'pacote_hash'})
        revisor = revisor_teste()
        erro = revisor.revisar(pacote)
        self.assertEqual(erro['erros'][0]['codigo'], 'vinculo_invalido')
        self.assertEqual(revisor.transporte.pedidos, [])
        revisor = revisor_teste(lambda p: resposta_prescrita(p, versao=VERSAO_LEGADA))
        erro = revisor.revisar(self.pacote)
        self.assertEqual(erro['erros'][0]['codigo'], 'versao_invalida')
        self.assertIsNone(erro['parecer'])

    def test_api_legada_explicita_e_api_atual(self):
        transporte = TransporteTeste(lambda p: resposta_prescrita(p, versao=VERSAO_LEGADA))
        antigo = RevisorIA(transporte, modelo='teste', configuracao={}, versao=VERSAO_LEGADA)
        self.assertEqual(antigo.revisar(self.pacote)['estado'], 'parecer_recebido')
        atual = revisor_teste().revisar(self.pacote)
        self.assertEqual(atual['versao'], VERSAO)
        self.assertEqual(atual['estado'], 'parecer_recebido')
        self.assertEqual(atual['schema_hash'], hash_json(atual['pedido']['formato_resposta']))

    def test_auditoria_arquivo_documento_atualizado_e_incerteza(self):
        for cid in ('D04', 'D07', 'D09'):
            original = simular(cid)
            antes = hash_json(original)
            with tempfile.TemporaryDirectory() as tmp:
                origem = Path(tmp)/'original.json'
                origem.write_text(json.dumps(original))
                auditoria = auditar_arquivo(origem, Path(tmp)/'auditoria.json', revisor=revisor_teste())
            self.assertTrue(all(r['revisao_semantica']['estado'] == 'parecer_recebido'
                                for r in auditoria['registros']))
            self.assertEqual(hash_json(original), antes)
            if cid == 'D07':
                self.assertEqual(original['verificacao_documental']['recomendacoes'], [])
            else:
                valor = auditoria['registros'][0]['revisao_semantica']['parecer']['objeto_avaliado']['valor']
                self.assertEqual(valor['estado'], 'indeterminado')
                self.assertIsNone(valor['valor'])
