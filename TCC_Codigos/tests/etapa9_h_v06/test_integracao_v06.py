"""Fronteira/avaliação e catálogos dos inputs vigentes, sem inferência real."""
from copy import deepcopy
from pathlib import Path
import unittest

from avaliacao.demonstracao import montar_demo
from hibrido_v05.avaliacao import normalizar as normalizar_v05
from hibrido_v06 import construir, executar_h, SimuladoV06, montar_contexto, VERSAO
from hibrido_v06.avaliacao import normalizar, registrar, hash_implementacao, conferir_proveniencia_h
from hibrido_v06.metricas import avaliar
from interpretacao_no.contratos import hash_json
from piloto_real.inputs import carregar
from test_encaminhamentos import analise, projeto, encaminhar

DADOS = Path(__file__).resolve().parents[2] / 'data/desenvolvimento'


def pipeline():
    caso = next(c for c in carregar(DADOS) if c['caso_id'] == 'k_09c2')
    p = construir(caso['estado'], caso['evento'], execucao_id='mock_fronteira_v06')
    def resposta(c):
        a = analise(c)
        a['propostas'] = []
        for q in a['avaliacao'].values():
            q.update(estado='indeterminado', valor=None, direcao='desconhecida',
                     evidencias=[], lacunas=['MOCK sem interpretação factual'])
        a['pendencias_operacionais'] = ['MOCK sem interpretação semântica deste cenário']
        return a
    r = executar_h(caso['base'], caso['evento_comum'], caso['fontes'], caso['estado'],
                   caso['evento'], caso['views']['H'], SimuladoV06(resposta), p,
                   vinculo=caso['vinculo'], origem='simulado')
    m, registros, referencias, _ = montar_demo()
    m['execucoes'] = m['execucoes'][:3]
    registros = registros[:3]
    m['schema_version'] = '3.0-manifesto-h06'
    s = m['execucoes'][1]
    s.update(projeto_id=caso['estado']['projeto_id'], evento_id=caso['evento']['evento_id'],
             execucao_id=p.execucao_id, versao_projeto=caso['estado']['versao'],
             view_hash=caso['views']['H']['view_hash'], snapshot_hash=hash_json(caso['estado']),
             evento_hash=hash_json(caso['evento']), codigo_hash=hash_implementacao(),
             versao_protocolo=p.versao, origem='simulado', modelo=None, config_hash=hash_json({}))
    registros[1] = registrar(s, r)
    ref = deepcopy(referencias[0])
    ref.update(caso_id=s['caso_id'], versao_projeto=s['versao_projeto'])
    for d in ('prazo', 'custo'):
        ref['por_view']['H'][d].update(estado='pendente', view_hash=s['view_hash'])
    refs = {(x['caso_id'], x['versao_projeto']): x for x in referencias + [ref]}
    return m, registros, list(refs.values()), r


class Integracao(unittest.TestCase):
    def test_fronteira_normalizador_metricas_sem_reclassificar(self):
        m, registros, refs, resultado = pipeline()
        n = normalizar(m, registros)
        self.assertFalse(n['anomalias'], n['anomalias'])
        self.assertEqual(resultado['contrato_h'], '3.0-h')
        self.assertEqual(n['linhas'][1]['resultado_original'], resultado)
        self.assertEqual(n['linhas'][1]['desfechos']['prazo']['classe'], 'indeterminado')
        metricas = avaliar(m, registros, refs)
        self.assertEqual(metricas['metricas']['H:prazo']['cobertura_numerica']['n'], 0)
        with self.assertRaises(ValueError):
            normalizar_v05(m, registros)

    def test_versoes_misturadas_rejeitadas(self):
        for alvo in ('envelope', 'analise', 'contexto', 'formato', 'protocolo'):
            with self.subTest(alvo=alvo):
                m, registros, _, r = pipeline()
                if alvo == 'protocolo':
                    m['execucoes'][1]['versao_protocolo'] = '5.0-politica-h-escopada'
                    with self.assertRaises(ValueError):
                        normalizar(m, registros)
                    continue
                passo = next(t for t in r['rastro_orquestracao'] if 'analise' in t)
                if alvo == 'envelope':
                    r['contrato_h'] = '2.0-h'
                elif alvo == 'analise':
                    passo['analise']['schema_version'] = '2.0-analise-local'
                elif alvo == 'contexto':
                    passo['contexto']['schema_version'] = '2.0-contexto-no-local'
                else:
                    passo['analise']['execucao']['versao_formato_local'] = '5.0-h-local-escopado'
                registros[1] = registrar(m['execucoes'][1], r)
                self.assertTrue(normalizar(m, registros)['anomalias'])

    def test_reconciliacao_preservada_e_conferida_contra_rastro(self):
        from hibrido_v06 import avaliar as executar
        e, ev = projeto()
        p = construir(e, ev, execucao_id='mock_proveniencia')
        r = executar(e, ev, SimuladoV06(analise), p)
        r.update(contrato_h='3.0-h', condicao_orquestracao='orquestracao_v06', politica_versao=p.versao)
        r['execucao'].update(origem='simulado', modelo=None, configuracao={}, config_hash=hash_json({}))
        slot = dict(modelo=None, config_hash=hash_json({}), origem='simulado', execucao_id=p.execucao_id,
                    evento_id=ev['evento_id'], snapshot_hash=hash_json(e), projeto_id=e['projeto_id'],
                    versao_projeto=e['versao'], versao_protocolo=p.versao)
        conferir_proveniencia_h(r, slot, uso='teste_prescrito')
        for alvo in ('proposta', 'estado', 'catalogo', 'politica'):
            with self.subTest(alvo=alvo):
                alterado = deepcopy(r)
                fechamento = alterado['registro_operacional']['fechamento_final']
                if alvo == 'proposta':
                    fechamento['encaminhamentos'][0]['propostas_refs'] = ['proposta_inexistente']
                elif alvo == 'estado':
                    fechamento['encaminhamentos'][0]['estado'] = 'pendente'
                elif alvo == 'catalogo':
                    alterado['registro_operacional']['responsabilidades_operacionais'] = []
                else:
                    alterado['politica_versao'] = '5.0-politica-h-escopada'
                with self.assertRaises(ValueError):
                    conferir_proveniencia_h(alterado, slot, uso='teste_prescrito')

    def test_pendencia_nao_pode_ser_reclassificada_como_execucao_completa(self):
        from hibrido_v06 import avaliar as executar
        e, ev = projeto()
        p = construir(e, ev, execucao_id='mock_pendencia_proveniencia')
        def resposta(c):
            a = analise(c)
            if c['no_id'] == 'n_alpha':
                a['encaminhamentos'] = [encaminhar(c, 'substituir_duracao', 'n_beta')]
            if c['no_id'] == 'n_beta':
                a['propostas'] = []
            return a
        r = executar(e, ev, SimuladoV06(resposta), p)
        r.update(contrato_h='3.0-h', condicao_orquestracao='orquestracao_v06', politica_versao=p.versao)
        r['execucao'].update(origem='simulado', modelo=None, configuracao={}, config_hash=hash_json({}))
        slot = dict(modelo=None, config_hash=hash_json({}), origem='simulado', execucao_id=p.execucao_id,
                    evento_id=ev['evento_id'], snapshot_hash=hash_json(e), projeto_id=e['projeto_id'],
                    versao_projeto=e['versao'], versao_protocolo=p.versao)
        conferir_proveniencia_h(r, slot, uso='teste_prescrito')
        r['execucao']['estado'] = 'ok'
        with self.assertRaisesRegex(ValueError, 'pendente com resultado completo'):
            conferir_proveniencia_h(r, slot, uso='teste_prescrito')

    def test_catalogos_dos_15_casos_sao_derivados_das_permissoes(self):
        casos = carregar(DADOS)
        self.assertEqual(len(casos), 15)
        for caso in casos:
            with self.subTest(caso=caso['caso_id']):
                e, ev = caso['estado'], caso['evento']
                p = construir(e, ev, execucao_id='mock_catalogo_' + caso['caso_id'])
                for n, selecao in p.plano.items():
                    c = montar_contexto(e, ev, no_id=n, revisao=1, execucao_id=p.execucao_id,
                                        responsabilidades_operacionais=p.responsabilidades_operacionais,
                                        **selecao)
                    locais = [{k: v for k, v in rota.items() if k != 'no_id'}
                              for rota in p.responsabilidades_operacionais if rota['no_id'] == n]
                    self.assertCountEqual(locais, c['permissoes'])
                if caso['caso_id'] == 'k_09c2':
                    dono = next(rota['no_id'] for rota in p.responsabilidades_operacionais
                                if rota['operacao'] == 'adicionar_parcela' and rota['alvo_id'] == 'p_07a4')
                    self.assertEqual(dono, 'n_c820')
                    self.assertFalse(any(rota['no_id'] == 'n_73fa' for rota in p.responsabilidades_operacionais))

    def test_carteira_v05_rejeita_transporte_v06_antes_de_reservar(self):
        from piloto_v05.transporte import LocalSSE
        class Carteira:
            manifesto_formato = dict(versao_formato_local='5.0-h-local-escopado', slots=['nao_autorizado'])
            def reservar(self, *args):
                raise AssertionError('Tentou reservar chamada paga')
        class HTTP:
            def post(self, *args):
                raise AssertionError('Tentou acessar rede')
        t = LocalSSE(Carteira(), 'nao_autorizado', HTTP(), timeout_s=1)
        with self.assertRaises(ValueError):
            t(dict(versao_formato_local=VERSAO))


if __name__ == '__main__':
    unittest.main()
