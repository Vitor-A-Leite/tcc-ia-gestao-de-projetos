"""Regressões sintéticas: resoluções operacionais, nunca desempenho do modelo."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

from hibrido_v06 import avaliar, construir, SimuladoV06, LocalV06, SCHEMA
from hibrido_v06.contratos import montar_contexto, validar, VERSAO
from hibrido_v06.formato import SISTEMA
from interpretacao_no.adaptadores import RespostaTransporte
from interpretacao_no.contratos import hash_json

spec = importlib.util.spec_from_file_location(
    'fixtures_h05_escopo', Path(__file__).parents[1] / 'etapa9_h_v05/cenarios.py')
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
projeto, REF = fixtures.projeto, fixtures.REF


def encaminhar(c, operacao='adicionar_parcela', alvo='p_aa11'):
    rota = next(r for r in c['responsabilidades_operacionais']
                if r['operacao'] == operacao and r['alvo_id'] == alvo)
    return dict(deepcopy(rota), motivo='MOCK: alteração a cargo do responsável catalogado',
                evidencias=[deepcopy(REF)])


def analise(c, **kwargs):
    a = fixtures.analise(c, versao=SCHEMA, **kwargs)
    a['encaminhamentos'] = [encaminhar(c)] if c['no_id'] == 'n_alpha' else []
    return a


class Encaminhamentos(unittest.TestCase):
    def rodar(self, alterar=None, **kwargs):
        e, ev = projeto()
        def resposta(c):
            a = analise(c, **kwargs)
            if alterar:
                alterar(c, a)
            return a
        return avaliar(e, ev, SimuladoV06(resposta), construir(e, ev, execucao_id='mock_v06'))

    def assert_parcial(self, r):
        self.assertEqual(r['execucao']['estado'], 'parcial', r.get('execucao'))
        self.assertIsNone(r['delta_centavos']['valor'])

    def test_encaminhamento_anterior_ao_responsavel_resolve_sem_bloquear_sucessores(self):
        r = self.rodar()
        self.assertEqual(r['execucao']['estado'], 'ok', r.get('lacunas'))
        self.assertEqual(r['delta_dias']['valor'], 2)
        self.assertEqual(r['delta_centavos']['valor'], 11000)
        fechamento = r['registro_operacional']['fechamento_final']
        pedido, = fechamento['encaminhamentos']
        self.assertEqual(pedido['estado'], 'resolvido_operacional_condicional')
        self.assertEqual(pedido['propostas_refs'], ['n_join:adicionar_parcela:p_aa11'])
        self.assertEqual(r['consumo']['analises'], 4)
        self.assertEqual(r['consumo']['chamadas'], 0)
        self.assertEqual(len({p['parcela_id'] for p in r['livro_parcelas']}), 4)
        self.assertEqual(r['suporte_semantico'], 'nao_auditado')

    def test_v05_reproduz_bloqueio_e_nao_reinterpreta_pendencia_textual(self):
        from hibrido_v05 import avaliar as antigo, construir as politica, SimuladoV05, SCHEMA as V5
        e, ev = projeto()
        def resposta(c):
            a = fixtures.analise(c, versao=V5)
            if c['no_id'] == 'n_alpha':
                a['pendencias_operacionais'] = ['Sem permissão local para p_aa11']
            return a
        r = antigo(e, ev, SimuladoV05(resposta), politica(e, ev, execucao_id='repro_v05'))
        self.assert_parcial(r)
        self.assertTrue(any('Pendência operacional n_alpha' in x for x in r['lacunas']))

    def test_responsavel_existe_mas_nao_propoe_alteracao_exigida(self):
        def alterar(c, a):
            if c['no_id'] == 'n_alpha':
                a['encaminhamentos'] = [encaminhar(c, 'substituir_duracao', 'n_beta')]
            if c['no_id'] == 'n_beta':
                a['propostas'] = []
        r = self.rodar(alterar)
        self.assert_parcial(r)
        self.assertTrue(any('Encaminhamento não resolvido' in x for x in r['lacunas']))

    def test_outro_encaminhamento_nao_substitui_proposta(self):
        def alterar(c, a):
            if c['no_id'] in ('n_alpha', 'n_join'):
                a['encaminhamentos'] = [encaminhar(c, 'substituir_duracao', 'n_beta')]
            if c['no_id'] == 'n_beta':
                a['propostas'] = []
        r = self.rodar(alterar)
        self.assert_parcial(r)
        self.assertEqual([x['estado'] for x in r['registro_operacional']['fechamento_final']['encaminhamentos']],
                         ['pendente', 'pendente'])

    def test_encaminhamento_depois_do_responsavel(self):
        def alterar(c, a):
            if c['no_id'] == 'n_marco':
                a['encaminhamentos'] = [encaminhar(c)]
        r = self.rodar(alterar)
        self.assertEqual(r['execucao']['estado'], 'ok')
        self.assertEqual(len(r['registro_operacional']['fechamento_final']['encaminhamentos']), 2)
        self.assertEqual(r['delta_centavos']['valor'], 11000)

    def test_lacuna_factual_nunca_e_apagada_por_encaminhamento(self):
        def alterar(c, a):
            if c['no_id'] == 'n_alpha':
                a['pendencias_operacionais'] = ['Falta definição factual local não representável']
        r = self.rodar(alterar)
        self.assert_parcial(r)
        self.assertTrue(any('Falta definição factual local' in x for x in r['lacunas']))

    def test_resolucao_tipadamente_desconhecida_nao_vira_exata(self):
        def alterar(c, a):
            if c['no_id'] == 'n_alpha':
                a['encaminhamentos'] = [encaminhar(c, 'registrar_lacuna_custo')]
            if c['no_id'] == 'n_join':
                p = next(p for p in a['propostas'] if p['alvo_id'] == 'p_aa11')
                p['operacao'] = 'registrar_lacuna_custo'
                p['valor'] = fixtures.desconhecido()
        r = self.rodar(alterar)
        self.assert_parcial(r)
        self.assertEqual(r['delta_dias']['valor'], 2)
        self.assertEqual(r['registro_operacional']['fechamento_final']['encaminhamentos'][0]['estado'],
                         'resolvido_operacional_condicional')

    def test_operacao_diferente_nao_resolve_encaminhamento(self):
        def alterar(c, a):
            if c['no_id'] == 'n_join':
                p = next(p for p in a['propostas'] if p['alvo_id'] == 'p_aa11')
                p['operacao'] = 'registrar_lacuna_custo'
                p['valor'] = fixtures.desconhecido()
        r = self.rodar(alterar)
        self.assert_parcial(r)
        self.assertEqual(r['registro_operacional']['fechamento_final']['encaminhamentos'][0]['estado'], 'pendente')

    def test_responsavel_rejeitado_nao_resolve(self):
        def alterar(c, a):
            if c['no_id'] == 'n_join':
                a['contexto_hash'] = 'hash_invalido'
        self.assert_parcial(self.rodar(alterar))

    def test_lacunas_duracao_e_taxa_continuam_parciais(self):
        for kwargs in ({'desconhecer': True}, {'taxas_desconhecidas': True}):
            with self.subTest(kwargs=kwargs):
                self.assert_parcial(self.rodar(**kwargs))

    def test_reuso_da_politica_nao_herda_resolucao_de_outra_passagem(self):
        e, ev = projeto()
        politica = construir(e, ev, execucao_id='mock_reuso')
        i = SimuladoV06(analise)
        primeiro = avaliar(e, ev, i, politica)
        segundo = avaliar(e, ev, i, politica)
        self.assertEqual(segundo['execucao']['estado'], 'ok')
        self.assertTrue(all(t['processamento'] == 'reuso_cache' for t in segundo['rastro_orquestracao']))
        self.assertEqual(len(segundo['registro_operacional']['fechamento_final']['encaminhamentos']), 1)
        def omitir(c):
            a = analise(c)
            if c['no_id'] == 'n_join':
                a['pendencias_operacionais'] = ['Cobrança ainda sem definição nesta passagem']
            return a
        terceiro = avaliar(e, ev, SimuladoV06(omitir), politica)
        self.assert_parcial(terceiro)
        self.assertEqual(terceiro['registro_operacional']['fechamento_final']['encaminhamentos'][0]['estado'], 'pendente')
        self.assertEqual(primeiro['execucao']['estado'], 'ok')

    def contexto(self):
        e, ev = projeto()
        politica = construir(e, ev, execucao_id='mock_contrato')
        return montar_contexto(e, ev, execucao_id=politica.execucao_id, no_id='n_alpha', revisao=1,
                              responsabilidades_operacionais=politica.responsabilidades_operacionais,
                              **politica.plano['n_alpha'])

    def test_rotas_invalidas_nao_alargam_permissoes(self):
        c = self.contexto()
        for campo, valor in [('no_id', 'n_inexistente'), ('alvo_id', 'p_falsa'), ('unidade', 'BRL'),
                             ('operacao', 'substituir_parcela'), ('atributo', 'duracao'),
                             ('motivo', ''), ('evidencias', [])]:
            with self.subTest(campo=campo):
                a = analise(c)
                a['encaminhamentos'][0][campo] = valor
                with self.assertRaises(ValueError):
                    validar(a, c)
        a = analise(c)
        a['encaminhamentos'] = [encaminhar(c, 'substituir_duracao', 'n_alpha')]
        with self.assertRaisesRegex(ValueError, 'Obrigação local'):
            validar(a, c)
        a = analise(c)
        a['encaminhamentos'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicado'):
            validar(a, c)

    def test_proposta_externa_continua_proibida(self):
        c = self.contexto()
        a = analise(c)
        a['propostas'][0].update(operacao='adicionar_parcela', alvo_id='p_aa11',
                                atributo='valor_centavos', unidade='BRL_centavo')
        with self.assertRaisesRegex(ValueError, 'fora de catálogo'):
            validar(a, c)

    def test_schema_antigo_e_encaminhamento_ausente_sao_rejeitados(self):
        c = self.contexto()
        a = analise(c)
        del a['encaminhamentos']
        with self.assertRaises(ValueError):
            validar(a, c)
        a = analise(c)
        a['schema_version'] = '2.0-analise-local'
        with self.assertRaises(ValueError):
            validar(a, c)

    def test_confirmacao_de_clausula_nao_e_resolvida_por_rota_sem_escopo(self):
        c = self.contexto()
        a = analise(c)
        a['encaminhamentos'] = [encaminhar(c, 'confirmar_ausencia_parcela_adicional', 'n_join')]
        with self.assertRaisesRegex(ValueError, 'Confirmação por cláusula'):
            validar(a, c)

    def test_encaminhamentos_ciclicos_sem_propostas_continuam_pendentes(self):
        def alterar(c, a):
            if c['no_id'] in ('n_alpha', 'n_beta'):
                alvo = 'n_beta' if c['no_id'] == 'n_alpha' else 'n_alpha'
                a['encaminhamentos'] = [encaminhar(c, 'substituir_duracao', alvo)]
                a['propostas'] = []
        r = self.rodar(alterar)
        self.assert_parcial(r)
        self.assertEqual([x['estado'] for x in r['registro_operacional']['fechamento_final']['encaminhamentos']],
                         ['pendente', 'pendente'])

    def test_limite_impede_responsavel_e_nao_libera_encaminhamento(self):
        e, ev = projeto()
        p = construir(e, ev, execucao_id='mock_limite')
        p.max_analises = 2
        r = avaliar(e, ev, SimuladoV06(analise), p)
        self.assert_parcial(r)
        self.assertEqual(r['consumo']['analises'], 2)
        self.assertEqual(r['registro_operacional']['fechamento_final']['encaminhamentos'][0]['estado'], 'pendente')

    def test_alteracao_de_plano_catalogo_ou_snapshot_exige_nova_politica(self):
        for alvo in ('catalogo', 'plano', 'evento', 'estado'):
            with self.subTest(alvo=alvo):
                e, ev = projeto()
                politica = construir(e, ev, execucao_id='mock_tamper')
                if alvo == 'catalogo':
                    politica.responsabilidades_operacionais[0]['no_id'] = 'n_beta'
                elif alvo == 'plano':
                    politica.plano['n_alpha']['obrigacoes'] = ['p_falsa']
                elif alvo == 'evento':
                    ev['relato'] += ' Nova observação'
                else:
                    e['entidades'][0]['nome'] = 'Outro nome'
                i = SimuladoV06(lambda c: self.fail('Não deve chamar interpretador'))
                r = avaliar(e, ev, i, politica)
                self.assertEqual(r['execucao']['estado'], 'erro')
                self.assertEqual(r['consumo']['analises'], 0)

    def test_requisicao_real_do_adaptador_contem_contrato_e_preserva_resposta_bruta(self):
        c = self.contexto()
        a = analise(c)
        bruto = json.dumps(a)
        pedidos = []
        class Transporte:
            versao_formato_local = VERSAO
            def __call__(self, pedido):
                pedidos.append(pedido)
                return RespostaTransporte(bruto)
        r = LocalV06(Transporte(), modelo='mock', configuracao={}, timeout_s=1).analisar(c)
        self.assertEqual(r['execucao']['estado'], 'ok')
        self.assertEqual(r['execucao']['tentativas'][0]['resposta_bruta'], bruto)
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(pedidos[0]['mensagens'][0]['conteudo'], SISTEMA)
        payload = json.loads(pedidos[0]['mensagens'][1]['conteudo'])
        self.assertEqual(payload['contexto'], c)
        self.assertIn('encaminhamentos', payload['contrato_resposta']['campos_analise'])
        self.assertEqual(r['contexto_hash'], c['contexto_hash'])
        self.assertFalse(r['execucao']['repetir_transporte'])

    def test_catalogo_nao_contem_fatos_valores_nem_altera_inputs(self):
        e, ev = projeto()
        antes = deepcopy((e, ev))
        p = construir(e, ev, execucao_id='mock_ids')
        for rota in p.responsabilidades_operacionais:
            self.assertEqual(set(rota), {'no_id', 'operacao', 'alvo_id', 'atributo', 'unidade'})
        avaliar(e, ev, SimuladoV06(analise), p)
        self.assertEqual((e, ev), antes)

    def test_timeout_sem_retry(self):
        chamadas = []
        class Transporte:
            versao_formato_local = VERSAO
            def __call__(self, req):
                chamadas.append(req)
                raise TimeoutError('timeout mock')
        r = LocalV06(Transporte(), modelo='mock', configuracao={}, timeout_s=1).analisar(self.contexto())
        self.assertEqual(r['execucao']['estado'], 'erro')
        self.assertEqual(r['execucao']['chamadas'], 1)
        self.assertEqual(len(chamadas), 1)


if __name__ == '__main__':
    unittest.main()
