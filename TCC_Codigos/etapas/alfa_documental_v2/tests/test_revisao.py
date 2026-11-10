"""Contratos observacionais; toda resposta de IA é prescrita e nenhuma rede é usada."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from .. import ROOT
from ..src.pipeline import simular
from ..src.revisao import (VERSAO, Observador, RevisorIA, analisar_propostas,
                          montar_pacote, validar_parecer, formato_parecer, _ref_ids)
from ..src.auditoria import auditar_resultado, auditar_arquivo, TransporteRevisaoReal
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.apresentacao import registrar_incorporadas
from ..src.vendor.hibrido_v07_r3.contratos import hash_json
from ..src.vendor.interpretacao_no.adaptadores import RespostaTransporte, FalhaTransporte


def resposta_prescrita(pacote, parecer='sustentada'):
    p = pacote['proposta']
    ids = {r['fonte_id'] for r in _ref_ids(p)}
    return dict(versao=VERSAO, pacote_hash=pacote['pacote_hash'], proposta_hash=pacote['proposta_hash'],
                contexto_hash=pacote['referencia']['contexto_hash'], parecer=parecer, tipo_efeito='fato_local',
                entidade_sustentada=p['no_id'], alvo_sustentado=p['alvo_id'], atributo_sustentado=p['atributo'],
                unidade_sustentada=p['unidade'], valor_sustentado=deepcopy(pacote['proposto']),
                fontes_examinadas=[dict(fonte_id=f['id'], documento_id=f['documento_id'], versao=f['versao'],
                    localizador=f['localizador'], trecho_citado=f['trecho'][:100]) for f in pacote['fontes'] if f['id'] in ids],
                justificativa='Resposta prescrita exclusivamente para testar o contrato; não é auditoria humana.',
                suporte_ausente=[] if parecer in ('sustentada', 'contradita') else ['Evidência do atributo local não estabelecida nesta resposta prescrita.'])


class TransporteTeste:
    origem = 'simulado'
    cache_identidade = 'resposta-prescrita-v1'

    def __init__(self, responder=None):
        self.responder = responder or resposta_prescrita
        self.pedidos = []

    def __call__(self, pedido):
        self.pedidos.append(deepcopy(pedido))
        pacote = json.loads(pedido['mensagens'][1]['content'])
        r = self.responder(pacote)
        return r if isinstance(r, RespostaTransporte) else RespostaTransporte(json.dumps(r), modelo='teste-offline')


def revisor_teste(responder=None):
    return RevisorIA(TransporteTeste(responder), modelo='teste-offline', configuracao={'fixture': 'contrato'})


def sincronizar(c, a):
    c['contexto_hash'] = hash_json({k: v for k, v in c.items() if k != 'contexto_hash'})
    a['contexto_hash'] = c['contexto_hash']
    return c, a


class RevisaoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultado = simular('D02')

    def passo(self, no='SUP_MOTOR'):
        s = next(s for s in self.resultado['rastro_orquestracao'] if s['no_id'] == no)
        return deepcopy(s['contexto']), deepcopy(s['analise'])

    def pacote(self):
        c, a = self.passo()
        d = analisar_propostas(c, a)[0]
        return montar_pacote(c, a, a['propostas'][0], d)

    def test_candidata_vinculada_sem_certificar_suporte(self):
        c, a = self.passo()
        d = analisar_propostas(c, a)[0]
        self.assertEqual(d['decisao'], 'candidata')
        self.assertEqual(d['vigente']['comparavel'], 18)
        self.assertEqual(d['proposto'], 25)
        self.assertEqual(d['suporte_semantico'], 'nao_auditado')
        self.assertFalse(d['autorizacao'])

    def test_entidade_atributo_unidade_e_custo_invalidos(self):
        for campo, valor in [('no_id', 'M_RELEASE'), ('alvo_id', 'inexistente'),
                             ('atributo', 'duracao'), ('unidade', 'BRL_centavo')]:
            c, a = self.passo()
            a['propostas'][0][campo] = valor
            with self.subTest(campo=campo):
                self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'incompativel')
        c, a = self.passo()
        a['propostas'][0]['valor']['valor'] = -10
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'incompativel')

    def test_fonte_contexto_evento_versao_invalidos(self):
        for mutacao in ('hash', 'fonte', 'evento', 'versao_duplicada'):
            c, a = self.passo()
            if mutacao == 'hash':
                c['fontes'][0]['trecho'] += ' adulterado'
            elif mutacao == 'fonte':
                a['propostas'][0]['evidencias'][0]['localizador'] = 'inventado'
            elif mutacao == 'evento':
                a['evento_id'] = 'outro'
            else:
                f = deepcopy(c['fontes'][0]); f['versao'] = 'outra'
                c['fontes'].append(f); sincronizar(c, a)
            with self.subTest(mutacao=mutacao):
                self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'incompativel')

    def test_igualdade_zero_e_desconhecimento(self):
        c, a = self.passo()
        a['propostas'][0]['valor']['valor'] = 18
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'ja_atualizado')
        c['restricoes'][0]['valor'].update(estado='indeterminado', valor=None, lacunas=['Valor ausente'])
        sincronizar(c, a)
        a['propostas'][0]['valor']['valor'] = 0
        d = analisar_propostas(c, a)[0]
        self.assertEqual(d['decisao'], 'requer_revisao')
        self.assertIsNone(d['vigente']['valor']['valor'])
        self.assertFalse(d['vigente']['conhecido'])
        c, a = self.passo()
        a['propostas'][0]['valor'].update(estado='indeterminado', valor=None, lacunas=['Magnitude não informada'])
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'requer_revisao')

    def test_repeticao_exige_mesmo_fato_e_nao_so_citacao(self):
        c, a = self.passo()
        p = a['propostas'][0]
        c['alteracoes_incorporadas'] = registrar_incorporadas([p], c['evento_id'])
        sincronizar(c, a)
        self.assertNotEqual(analisar_propostas(c, a)[0]['decisao'], 'ja_incorporado')
        c['alteracoes_incorporadas'][0]['origens_causais'] = deepcopy(p['origens_causais'])
        sincronizar(c, a)
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'ja_incorporado')
        c['alteracoes_incorporadas'][0]['evento_id'] = 'evento_anterior'
        sincronizar(c, a)
        self.assertNotEqual(analisar_propostas(c, a)[0]['decisao'], 'ja_incorporado')

    def test_conflito_concorrente_e_com_incorporada(self):
        c, a = self.passo()
        p = deepcopy(a['propostas'][0]); p['id'] = 'outra'; p['valor']['valor'] = 30
        a['propostas'].append(p)
        self.assertEqual([d['decisao'] for d in analisar_propostas(c, a)], ['conflito', 'conflito'])
        c, a = self.passo()
        c['alteracoes_incorporadas'] = registrar_incorporadas([p], c['evento_id'])
        sincronizar(c, a)
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'conflito')

    def test_confirmacao_valida_sem_alteracao_numerica(self):
        c, a = self.passo('T_ASSEMBLY')
        d = analisar_propostas(c, a)[0]
        self.assertEqual(d['estrutura'], 'valida')
        self.assertEqual(d['decisao'], 'ja_atualizado')
        self.assertEqual(d['proposto'], 5)
        self.assertEqual(d['suporte_semantico'], 'nao_auditado')

    def test_valor_financeiro_vigente_vem_da_operacao_incorporada(self):
        c, a = self.passo()
        p = a['propostas'][0]
        p.update(operacao='substituir_parcela', alvo_id='p_10', atributo='valor_centavos', unidade='BRL_centavo')
        p['origens_causais'][0]['efeito_id'] = hash_json([c['evento_id'], 'p_10'])
        p['valor']['valor'] = 3100000
        c['alteracoes_incorporadas'] = registrar_incorporadas([p], c['evento_id'])
        sincronizar(c, a)
        d = analisar_propostas(c, a)[0]
        self.assertEqual(c['parcelas'][0]['valor_centavos'], 3000000)
        self.assertEqual(d['vigente']['comparavel'], 3100000)
        self.assertEqual(d['decisao'], 'ja_atualizado')
        p['valor']['valor'] = -1
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'incompativel')
        p['valor']['valor'] = 3100000; p['unidade'] = 'dia_corrido'
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'incompativel')

    def test_aditivos_distintos_e_sobreposicao_conflitante(self):
        c, a = self.passo('M_RELEASE')
        _, origem = self.passo()
        p = deepcopy(origem['propostas'][0])
        p.update(id='aditivo', no_id=c['no_id'], operacao='alterar_parametros_contratuais', alvo_id='OVERHEAD',
                 atributo='parametros_contratuais', unidade='contrato_temporal', valor={'base_contratada_dias': 50}, regra_refs=['OVERHEAD'])
        p['origens_causais'][0]['efeito_id'] = hash_json([c['evento_id'], p['alvo_id']])
        a['propostas'] = [p]
        anterior = deepcopy(p); anterior.update(id='taxa', valor={'taxa_centavos_dia': 45000})
        c['alteracoes_incorporadas'] = registrar_incorporadas([anterior], c['evento_id'])
        sincronizar(c, a)
        d = analisar_propostas(c, a)[0]
        self.assertEqual(d['decisao'], 'candidata')
        self.assertEqual(d['conflitos_refs'], [])
        p['valor'] = {'taxa_centavos_dia': 45000}
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'ja_atualizado')
        p['valor'] = {'taxa_centavos_dia': 60000}
        self.assertEqual(analisar_propostas(c, a)[0]['decisao'], 'conflito')

    def test_repeticao_e_troca_de_revisor_nao_reusam_parecer(self):
        primeiro = revisor_teste()
        segundo = revisor_teste(lambda p: resposta_prescrita(p, 'ambigua'))
        segundo.configuracao = {'fixture': 'outra'}
        a1 = auditar_resultado(self.resultado, revisor=primeiro)
        a2 = auditar_resultado(self.resultado, revisor=primeiro)
        a3 = auditar_resultado(self.resultado, revisor=segundo)
        self.assertEqual(len(primeiro.transporte.pedidos), 4)
        self.assertEqual(len(segundo.transporte.pedidos), 2)
        self.assertNotEqual(a1['identidade_revisor'], a3['identidade_revisor'])
        self.assertEqual(a2['registros'][0]['revisao_semantica']['tentativas'], 1)
        self.assertEqual(a3['registros'][0]['revisao_semantica']['parecer']['parecer'], 'ambigua')

    def test_pacote_fontes_originais_sem_gabarito_resultado_ou_justificativa(self):
        c, a = self.passo()
        a['justificativa'] = 'O proponente inventa esta razão.'
        d = analisar_propostas(c, a)[0]
        p = montar_pacote(c, a, a['propostas'][0], d)
        self.assertEqual(p['fontes'], c['fontes'])
        self.assertEqual(p['referencia']['contexto_hash'], c['contexto_hash'])
        self.assertNotIn('fim_novo', p)
        self.assertNotIn('justificativa', p)
        self.assertNotIn('gabarito', p)
        self.assertTrue(all(f['versao'] and f['trecho'] for f in p['fontes']))

    def test_parecer_estrito_vinculos_fontes_unidade(self):
        p = self.pacote()
        bom = resposta_prescrita(p)
        self.assertEqual(validar_parecer(bom, p), bom)
        for campo, valor in [('interpretacao_validada', True), ('pacote_hash', 'outro'),
                             ('entidade_sustentada', 'OUTRO'), ('alvo_sustentado', 'OUTRO'),
                             ('atributo_sustentado', 'duracao'), ('unidade_sustentada', 'BRL_centavo'),
                             ('valor_sustentado', True), ('tipo_efeito', 'propagacao'),
                             ('suporte_ausente', ['Falta suporte'])]:
            ruim = deepcopy(bom); ruim[campo] = valor
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                validar_parecer(ruim, p)
        for campo in ('fonte_id', 'localizador', 'documento_id', 'versao', 'trecho_citado'):
            ruim = deepcopy(bom); ruim['fontes_examinadas'][0][campo] = 'inventado'
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                validar_parecer(ruim, p)
        ruim = deepcopy(bom); ruim['fontes_examinadas'] = []
        with self.assertRaises(ValueError): validar_parecer(ruim, p)
        p['fontes'][0]['trecho'] += 'tamper'
        with self.assertRaises(ValueError): validar_parecer(bom, p)

    def test_contradita_ambigua_e_insuficiente_sao_pareceres_nao_verdade(self):
        p = self.pacote()
        for parecer in ('contradita', 'ambigua', 'suporte_insuficiente'):
            r = revisor_teste(lambda pacote: resposta_prescrita(pacote, parecer)).revisar(p)
            self.assertEqual(r['parecer']['parecer'], parecer)
            self.assertEqual(r['natureza'], 'simulacao_nao_mede_ia')
            self.assertEqual(r['chamadas_api'], 0)
            self.assertIsNone(r['tokens_entrada'])
            self.assertNotIn('aprovacao_humana', r['parecer'])

    def test_recusa_incompleta_parser_e_transporte_falhos(self):
        p = self.pacote()
        respostas = [RespostaTransporte('{}', estado='recusa'), RespostaTransporte('{}', estado='incompleta'),
                     RespostaTransporte('não JSON'), RespostaTransporte('{"x":1,"x":2}'),
                     RespostaTransporte('{"x":NaN}'), RespostaTransporte('{}', tokens_entrada=100)]
        for resposta in respostas:
            r = revisor_teste(lambda p: resposta).revisar(p)
            self.assertEqual(r['estado'], 'requer_revisao')
            self.assertIsNone(r['parecer'])
            self.assertEqual(r['resposta_bruta'], resposta.texto)
        def falhar(p): raise RuntimeError('falha prescrita')
        r = revisor_teste(falhar).revisar(p)
        self.assertEqual(r['tentativas'], 1)
        self.assertIsNone(r['parecer'])
        self.assertEqual(r['erros'][0]['mensagem'], 'falha prescrita')

    def test_observacao_nao_altera_aceite_calculo_ou_suporte(self):
        revisor = revisor_teste(lambda p: resposta_prescrita(p, 'suporte_insuficiente'))
        observado = simular('D02', observador=Observador(revisor))
        for k in ('fim_novo', 'delta_dias', 'custo_novo', 'delta_centavos', 'completude', 'pendencias_execucao', 'execucao'):
            self.assertEqual(observado[k], self.resultado[k], k)
        self.assertEqual(observado['suporte_semantico'], 'nao_auditado')
        self.assertIsNone(observado['aprovacao_humana'])
        self.assertNotIn('revisao_observacional', self.resultado)
        self.assertEqual(len(observado['revisao_observacional']['registros']), 2)
        self.assertTrue(all(r['revisao_semantica']['parecer']['parecer'] == 'suporte_insuficiente'
                            for r in observado['revisao_observacional']['registros']))
        s0 = next(s for s in self.resultado['rastro_orquestracao'] if s['no_id'] == 'SUP_MOTOR')
        s1 = next(s for s in observado['rastro_orquestracao'] if s['no_id'] == 'SUP_MOTOR')
        self.assertEqual(s0['contexto'], s1['contexto'])
        self.assertEqual([s.get('contexto') for s in observado['rastro_orquestracao']],
                         [s.get('contexto') for s in self.resultado['rastro_orquestracao']])

    def test_falha_do_observador_nao_vira_falha_do_calculo(self):
        class Ruim(Observador):
            def analisar(self, *args): raise RuntimeError('bug observacional')
        r = simular('D02', observador=Ruim())
        self.assertEqual(r['fim_novo'], self.resultado['fim_novo'])
        self.assertEqual(r['execucao'], self.resultado['execucao'])
        self.assertEqual(r['revisao_observacional']['registros'][0]['estado'], 'erro_observacao')

    def test_auditoria_preserva_coleta_e_recusa_sobrescrita(self):
        antes = deepcopy(self.resultado)
        audit = auditar_resultado(self.resultado, revisor=revisor_teste())
        self.assertEqual(self.resultado, antes)
        self.assertEqual(audit['resultado_original_hash'], hash_json(antes))
        self.assertTrue(audit['verificacao_documental_cadastrada'])
        with tempfile.TemporaryDirectory() as tmp:
            origem, destino = Path(tmp)/'original.json', Path(tmp)/'audit.json'
            origem.write_text(json.dumps(antes)); bruto = origem.read_bytes()
            auditar_arquivo(origem, destino)
            with self.assertRaises(FileExistsError): auditar_arquivo(origem, destino)
            with self.assertRaises(ValueError): auditar_arquivo(origem, origem)
            self.assertEqual(origem.read_bytes(), bruto)
        adulterado = deepcopy(antes)
        passo = next(s for s in adulterado['rastro_orquestracao'] if s['no_id'] == 'SUP_MOTOR')
        passo['analise']['propostas'][0]['valor']['valor'] = 99
        audit = auditar_resultado(adulterado, revisor=revisor_teste())
        self.assertEqual(audit['registros'][0]['estado'], 'vinculo_invalido')

    def test_piloto_marco_sem_suporte_continua_numericamente_igual(self):
        original = json.loads((ROOT/'outputs/ia_real_20261110T050151Z/resultado.json').read_text())
        def falso(p):
            r = resposta_prescrita(p, 'suporte_insuficiente')
            if p['proposta']['alvo_id'] == 'release_M_PROTO_READY':
                r.update(tipo_efeito='propagacao', entidade_sustentada=None, alvo_sustentado=None,
                         atributo_sustentado=None, unidade_sustentada=None, valor_sustentado=None,
                         justificativa='Resposta manual: CHANGE.D02 fala do motor; E026 registra precedência. Não afirma restrição local do marco.',
                         suporte_ausente=['Evidência explícita de nao_antes=25 para M_PROTO_READY.'])
            return r
        antes = hash_json(original)
        audit = auditar_resultado(original, revisor=revisor_teste(falso))
        registro = next(r for r in audit['registros'] if r.get('pacote', {}).get('proposta', {}).get('alvo_id') == 'release_M_PROTO_READY')
        self.assertEqual(registro['deterministica']['decisao'], 'candidata')
        self.assertEqual(registro['revisao_semantica']['parecer']['parecer'], 'suporte_insuficiente')
        self.assertEqual(registro['revisao_semantica']['natureza'], 'simulacao_nao_mede_ia')
        self.assertEqual(hash_json(original), antes)
        self.assertEqual(original['fim_novo']['valor'], 45)
        self.assertEqual(original['suporte_semantico'], 'nao_auditado')


class OrcamentoRevisaoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.resultado = simular('D02')
        self.origem = self.root/'original.json'; self.origem.write_text(json.dumps(self.resultado))
        self.calls = []

    def transporte(self, falha=None):
        def http(path, payload):
            self.calls.append((path, deepcopy(payload)))
            if falha: raise FalhaTransporte('rede', 'Falha HTTP prescrita, nenhuma rede')
            if path: return {'input_tokens': 100}
            pacote = json.loads(payload['input'][1]['content'])
            return dict(status='completed', model=MODELO, service_tier='default', id='teste_http',
                        output=[{'content': [{'type': 'output_text', 'text': json.dumps(resposta_prescrita(pacote))}]}],
                        usage={'input_tokens': 100, 'output_tokens': 20})
        t = TransporteReal(self.root/'carteira'/'run', 'chave-ficticia-nao-usada', 0, http=http)
        self.addCleanup(t.db.close)
        return TransporteRevisaoReal(t)

    def revisor(self, falha=None):
        return RevisorIA(self.transporte(falha), modelo=MODELO, configuracao=CONFIG, modo='ia_real')

    def limites(self, **kw):
        return dict(max_solicitacoes=2, max_tokens_entrada=128000, max_tokens_saida=32000,
                    max_segundos=1000, max_custo_centavos=3, **kw)

    def test_real_exige_identidade_sessao_destino_e_orcamento(self):
        with self.assertRaises(ValueError): RevisorIA(TransporteTeste(), modelo=MODELO, configuracao=CONFIG, modo='ia_real')
        with self.assertRaises(ValueError): RevisorIA(lambda p: None, modelo='x', configuracao={})
        r = self.revisor()
        with self.assertRaises(ValueError): Observador(r)
        with self.assertRaises(ValueError): auditar_resultado(self.resultado, revisor=r)
        with self.assertRaises(ValueError): auditar_arquivo(self.origem, self.root/'sem-teto.json', revisor=r)
        self.assertEqual(self.calls, [])
        c = next(s for s in self.resultado['rastro_orquestracao'] if s['no_id'] == 'SUP_MOTOR')
        d = analisar_propostas(c['contexto'], c['analise'])[0]
        p = montar_pacote(c['contexto'], c['analise'], c['analise']['propostas'][0], d)
        self.assertEqual(r.revisar(p)['tentativas'], 0)
        self.assertEqual(self.calls, [])

    def test_reservas_de_tokens_dinheiro_tempo_e_solicitacoes(self):
        for i, (campo, valor) in enumerate([('max_tokens_entrada', 63999), ('max_tokens_saida', 15999),
                                           ('max_custo_centavos', 1.49), ('max_segundos', 359), ('max_solicitacoes', 0)]):
            r = self.revisor(); b = self.limites(); b[campo] = valor
            audit = auditar_arquivo(self.origem, self.root/f'limite{i}.json', revisor=r, limites=b)
            self.assertEqual(self.calls, [], campo)
            self.assertEqual(audit['sessao_revisao']['consumo']['solicitacoes_reais'], 0)
            self.assertTrue(all(x['revisao_semantica']['parecer'] is None for x in audit['registros']))

    def test_transporte_com_reserva_contabilizado_e_repeticao_nao_gasta(self):
        r = self.revisor(); b = self.limites(); b['max_solicitacoes'] = 1
        with patch('socket.socket', side_effect=AssertionError('Rede proibida')):
            audit = auditar_arquivo(self.origem, self.root/'real-mock.json', revisor=r, limites=b)
        u = audit['sessao_revisao']['consumo']
        self.assertEqual(u['chamadas_api'], 1)
        self.assertEqual(u['solicitacoes_reais'], 1)
        self.assertEqual(u['tokens_entrada'], 100)
        self.assertEqual(u['tokens_saida'], 20)
        self.assertGreater(u['custo_api_usd'], 0)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(audit['registros'][0]['revisao_semantica']['tentativas'], 1)
        self.assertEqual(audit['registros'][1]['revisao_semantica']['tentativas'], 0)
        with self.assertRaises(FileExistsError):
            auditar_arquivo(self.origem, self.root/'real-mock.json', revisor=r, limites=b)
        self.assertEqual(len(self.calls), 2)

    def test_uso_desconhecido_preserva_reserva_e_bloqueia_seguinte(self):
        audit = auditar_arquivo(self.origem, self.root/'falha.json', revisor=self.revisor(falha=True), limites=self.limites())
        u = audit['sessao_revisao']['consumo']
        self.assertTrue(u['uso_desconhecido'])
        self.assertEqual(u['chamadas_api'], 1)
        self.assertEqual(u['comprometido_api_usd'], .015)
        self.assertEqual(len(self.calls), 1)
        r = audit['registros'][0]['revisao_semantica']
        self.assertEqual(r['tentativas'], 1)
        self.assertTrue(r['uso_desconhecido'])
        self.assertIsNone(r['tokens_entrada'])
        self.assertIsNone(r['parecer'])
        self.assertEqual(audit['registros'][1]['revisao_semantica']['tentativas'], 0)
