"""Regressões de escopo cadastrado e estado de conhecimento, sem API real."""
from copy import deepcopy
import json
import unittest

from ..src import ROOT
from ..src.evidencias_revisao import (ID_ESCOPO, carregar_cadastro, montar_escopo,
                                    comparar_afirmacao, valores_avaliados)
from ..src.revisao import (ErroRevisao, VERSAO, atualizar_pacote, conferir_pacote,
                          validar_parecer, analisar_propostas, montar_pacote)
from ..src.pipeline import simular
from ..src.vendor.interpretacao_no.contratos import hash_json
from .test_revisao import resposta_prescrita, revisor_teste, sincronizar


class RevisaoV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = ROOT/'outputs/avaliacao_revisor_v2_20261111'

    def pacote(self, cid='D02-01'):
        return atualizar_pacote(json.loads((self.base/'entradas'/f'{cid}.json').read_text())['pacote'])

    def erro(self, resposta, pacote, codigo):
        with self.assertRaises(ErroRevisao) as erro:
            validar_parecer(resposta, pacote)
        self.assertEqual(erro.exception.codigo, codigo)

    def restricao(self, pacote, campo, valores):
        fonte = next(f['id'] for f in pacote['fontes'] if f['id'].startswith('CHANGE.'))
        return dict(campo=campo, conhecimento='exato', valores=valores,
                    fonte_ids=[fonte], justificativa='Restrição prescrita para teste.')

    def test_releitura_dos_23_resultados_v2_permanece_identica(self):
        arquivos = list((self.base/'casos').glob('*.json'))
        self.assertEqual(len(arquivos), 23)
        for path in arquivos:
            registro = json.loads(path.read_text())
            revisao = registro['revisao']
            self.assertEqual(validar_parecer(json.loads(revisao['resposta_bruta']), registro['pacote']), revisao['parecer'])

    def test_migracao_conserva_proposta_contexto_e_pacote_original(self):
        original = json.loads((self.base/'entradas/D03-01.json').read_text())['pacote']
        antes = deepcopy(original)
        pacote = atualizar_pacote(original)
        self.assertEqual(original, antes)
        self.assertEqual(pacote['versao'], VERSAO)
        self.assertEqual(pacote['proposta_hash'], original['proposta_hash'])
        self.assertEqual(pacote['referencia'], original['referencia'])
        self.assertNotEqual(pacote['pacote_hash'], original['pacote_hash'])
        self.assertEqual(pacote['metadados_escopo']['cadastro_hash'], hash_json(carregar_cadastro()))

    def test_quatro_escopos_usam_metadados_com_proveniencia(self):
        for cid in ('D03-01', 'D05-01', 'D09-01', 'D09-02'):
            pacote = self.pacote(cid)
            resposta = resposta_prescrita(pacote)
            resposta['aspectos']['escopo']['fonte_ids'] = []
            resultado = revisor_teste(lambda p: resposta).revisar(pacote)
            self.assertEqual(resultado['estado'], 'parecer_recebido', resultado['erros'])
            parecer = resultado['parecer']
            self.assertEqual(parecer['comparacoes_codigo']['escopo'], 'sustentado')
            self.assertEqual(parecer['contextos_resolvidos'][0]['id'], ID_ESCOPO)
            self.assertEqual(parecer['objeto_avaliado']['escopo']['vigencia']['inicio_dia'], 0)

    def test_silencio_documental_nao_sustenta_rejeicao_de_escopo_verificado(self):
        pacote = self.pacote()
        for estado, global_ in (('insuficiente', 'suporte_insuficiente'), ('ambiguo', 'ambigua')):
            resposta = resposta_prescrita(pacote, global_)
            resposta['aspectos']['escopo']['estado'] = estado
            self.erro(resposta, pacote, 'classificacao_escopo_inconsistente')

    def test_restricoes_explicitas_de_projeto_versao_e_vigencia(self):
        pacote = self.pacote()
        for campo, valor in (('projeto_id', 'PROJETO-B'), ('versao_projeto', '2.0.0'), ('inicio_dia', 10)):
            resposta = resposta_prescrita(pacote, 'contradita')
            resposta['aspectos']['escopo']['estado'] = 'contradito'
            resposta['restricoes_escopo'] = [self.restricao(pacote, campo, [valor])]
            resultado = validar_parecer(resposta, pacote)
            self.assertEqual(resultado['comparacoes_codigo']['escopo'], 'contradito')
            resposta['aspectos']['escopo']['estado'] = 'sustentado'
            self.erro(resposta, pacote, 'classificacao_escopo_inconsistente')

    def test_aliases_exigem_equivalencia_cadastrada(self):
        pacote = self.pacote()
        resposta = resposta_prescrita(pacote)
        resposta['restricoes_escopo'] = [self.restricao(pacote, 'projeto_id', ['Alfa v1']),
                                       self.restricao(pacote, 'versao_projeto', ['v1'])]
        self.assertEqual(validar_parecer(resposta, pacote)['comparacoes_codigo']['escopo'], 'sustentado')
        resposta['restricoes_escopo'][1]['valores'] = ['v2']
        self.erro(resposta, pacote, 'classificacao_escopo_inconsistente')

    def test_observacao_nao_e_origem_automatica_da_vigencia(self):
        pacote = self.pacote()
        evento = deepcopy(pacote['evento'])
        evento['instante_observacao'] = 12
        escopo = montar_escopo(pacote['referencia'], evento, pacote['fontes'], carregar_cadastro())
        self.assertEqual(escopo['vigencia']['inicio_dia'], 0)
        evento['escopo'] = 'Vigência a confirmar'
        escopo = montar_escopo(pacote['referencia'], evento, pacote['fontes'], carregar_cadastro())
        self.assertIsNone(escopo['vigencia'])
        self.assertEqual(escopo['estado'], 'indisponivel')

    def test_vinculos_de_cadastro_divergentes_e_metadados_adulterados(self):
        pacote = self.pacote()
        for campo, valor in (('projeto_id', 'OUTRO'), ('versao_projeto', '2.0.0')):
            referencia = {**pacote['referencia'], campo: valor}
            escopo = montar_escopo(referencia, pacote['evento'], pacote['fontes'], carregar_cadastro())
            self.assertEqual(escopo['estado'], 'divergente')
            self.assertIn(campo, escopo['divergencias'])
        pacote['metadados_escopo']['estado'] = 'divergente'
        pacote['pacote_hash'] = hash_json({k: v for k, v in pacote.items() if k != 'pacote_hash'})
        with self.assertRaises(ErroRevisao):
            conferir_pacote(pacote)

    def test_n03_indeterminado_com_magnitude_exata_e_insuficiente(self):
        pacote = self.pacote('N03')
        resposta = resposta_prescrita(pacote, 'suporte_insuficiente')
        resposta['fundamentos_valor']['valor'].update(conhecimento='indeterminado', valores=[])
        resposta['aspectos']['valor']['estado'] = 'insuficiente'
        self.assertEqual(validar_parecer(resposta, pacote)['comparacoes_codigo']['valores']['valor'], 'insuficiente')
        resposta['parecer'] = 'contradita'
        resposta['aspectos']['valor']['estado'] = 'contradito'
        self.erro(resposta, pacote, 'classificacao_valor_inconsistente')

    def test_valores_desconhecidos_d04_d09_podem_ser_sustentados(self):
        for cid in ('D04-01', 'D09-01'):
            pacote = self.pacote(cid)
            resultado = validar_parecer(resposta_prescrita(pacote), pacote)
            self.assertEqual(resultado['parecer'], 'sustentada')
            self.assertIsNone(resultado['objeto_avaliado']['valor']['valor'])

    def test_exato_alternativas_ausencia_e_valor_anterior(self):
        base = dict(conhecimento='exato', valores=[25], aplicabilidade='mesmo_objeto_e_vigencia')
        for proposto, fundamento, esperado in (
            (26, base, 'contradito'), (25, base, 'sustentado'),
            (25, dict(base, conhecimento='alternativas', valores=[25, 27]), 'ambiguo'),
            (26, dict(base, conhecimento='alternativas', valores=[25, 27]), 'contradito'),
            (25, dict(base, conhecimento='ausente', valores=[]), 'insuficiente'),
            (25, dict(base, valores=[18], aplicabilidade='outro_objeto_ou_vigencia'), 'insuficiente'),
        ):
            self.assertEqual(comparar_afirmacao(proposto, fundamento), esperado)

    def test_fontes_e_cardinalidade_dos_fundamentos(self):
        pacote = self.pacote()
        resposta = resposta_prescrita(pacote)
        resposta['fundamentos_valor']['valor']['fonte_ids'] = ['INVENTADA']
        self.erro(resposta, pacote, 'fonte_invalida')
        for estado, valores in (('exato', []), ('indeterminado', [25]), ('alternativas', [25, 25])):
            resposta = resposta_prescrita(pacote)
            resposta['fundamentos_valor']['valor'].update(conhecimento=estado, valores=valores)
            self.erro(resposta, pacote, 'fundamento_inconsistente')

    def test_cadastro_so_sustenta_escopo_e_precisa_ser_examinado(self):
        pacote = self.pacote()
        resposta = resposta_prescrita(pacote)
        resposta['contextos_examinados'] = []
        self.erro(resposta, pacote, 'cobertura_incompleta')
        resposta = resposta_prescrita(pacote)
        resposta['aspectos']['valor']['contexto_ids'] = [ID_ESCOPO]
        self.erro(resposta, pacote, 'contexto_incompativel')

    def test_n06_real_conserva_rejeicao_por_incoerencia(self):
        arquivo = ROOT/'outputs/avaliacao_revisor_v3_20261111/casos/N06.json'
        registro = json.loads(arquivo.read_text())
        bruto = json.loads(registro['revisao']['resposta_bruta'])
        self.assertEqual(bruto['fundamentos_valor']['valor']['aplicabilidade'], 'outro_objeto_ou_vigencia')
        self.assertEqual(bruto['aspectos']['valor']['estado'], 'contradito')
        self.erro(bruto, registro['pacote'], 'classificacao_valor_inconsistente')

    def test_campos_compostos_conservam_unidades_e_comparacoes_individuais(self):
        pacote = self.pacote()
        pacote['proposta']['operacao'] = 'alterar_parametros_contratuais'
        pacote['proposto'] = dict(taxa_centavos_dia=50000, base_contratada_dias=10, politica_reducao='sem_credito')
        campos = valores_avaliados(pacote)
        self.assertEqual(campos['taxa_centavos_dia']['unidade'], 'BRL_centavo/dia_corrido')
        self.assertEqual(campos['base_contratada_dias']['unidade'], 'dia_corrido')
        self.assertEqual(campos['politica_reducao']['valor'], 'sem_credito')

    def test_aditivo_composto_passando_pelo_revisor(self):
        resultado = simular('D02')
        passo = next(p for p in resultado['rastro_orquestracao'] if p['no_id'] == 'M_RELEASE')
        c, a = deepcopy(passo['contexto']), deepcopy(passo['analise'])
        p = deepcopy(self.pacote()['proposta'])
        p.update(id='aditivo', no_id='M_RELEASE', operacao='alterar_parametros_contratuais',
                 alvo_id='OVERHEAD', atributo='parametros_contratuais', unidade='contrato_temporal',
                 valor=dict(taxa_centavos_dia=45000, base_contratada_dias=50, politica_reducao='sem_credito'),
                 regra_refs=['OVERHEAD'])
        p['origens_causais'][0]['efeito_id'] = hash_json([c['evento_id'], p['alvo_id']])
        a['propostas'] = [p]
        a['resolucoes_regras'] = [dict(regra_id=r['regra_id'], propostas_indices=[1] if r['regra_id'] == 'OVERHEAD' else [])
                                  for r in c['escopos_regras']]
        sincronizar(c, a)
        d = analisar_propostas(c, a)[0]
        self.assertIsNone(d['erro_analise'])
        pacote = montar_pacote(c, a, p, d)
        revisao = revisor_teste().revisar(pacote)
        self.assertEqual(revisao['estado'], 'parecer_recebido', revisao['erros'])
        self.assertEqual(set(revisao['parecer']['comparacoes_codigo']['valores']), set(p['valor']))
