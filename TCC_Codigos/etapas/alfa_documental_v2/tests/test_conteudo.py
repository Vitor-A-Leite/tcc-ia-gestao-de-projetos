"""Revisão do conteúdo documental: avaliação, explicação e contrato de extração (offline)."""
from copy import deepcopy
import json
import tempfile
import unittest
from pathlib import Path

from TCC_Codigos.etapas.alfa_documental_v2.src import conteudo as C
from TCC_Codigos.etapas.alfa_documental_v2.src import extracao as X
from TCC_Codigos.etapas.alfa_documental_v2.src.pipeline import ler_cenario, simular
from TCC_Codigos.etapas.alfa_documental_v2.src.vendor.interpretacao_no.adaptadores import RespostaTransporte
from TCC_Codigos.etapas.alfa_documental_v2.scripts import avaliar_conteudo as AV

CENARIOS = AV.CENARIOS
_CACHE = {}


def resultado(cid):
    if cid not in _CACHE:
        _CACHE[cid] = simular(cid)
    return deepcopy(_CACHE[cid])


def revisao(cid, condicao='referencia', res=None):
    cen = ler_cenario(cid)
    ext = C.afirmacoes_cadastro(cen) if condicao == 'cadastro' else AV.extracoes_referencia(cen)
    return C.revisar_documentos(res or resultado(cid), cen, ext, condicao=condicao)


def por_id(rev):
    return {r['afirmacao']['id']: r for d in rev['documentos'] for r in d['afirmacoes']}


def referencia(doc_id, versao):
    ref = AV.ler(AV.REFERENCIAS/'afirmacoes_referencia.json')
    return next(e for e in ref['extracoes'] if e['documento_id'] == doc_id and e['versao'] == versao)


def resposta_de(ext):
    campos = ('trecho_id', 'citacao', 'predicado', 'entidades', 'campo', 'valor', 'unidade',
              'conhecimento', 'limites', 'referencia_temporal', 'registro', 'justificativa')
    return dict(versao=X.VERSAO, documento_id=ext['documento_id'], versao_documento=ext['versao'],
                afirmacoes=[{k: deepcopy(a.get(k)) for k in campos} for a in ext['afirmacoes']],
                nao_mapeados=deepcopy(ext['nao_mapeados']))


class Prescrito:
    origem = 'simulado'
    cache_identidade = 'extracao-prescrita-v1'

    def __init__(self, gerar, **envelope):
        self.gerar, self.envelope, self.pedidos = gerar, envelope, []

    def __call__(self, pedido):
        self.pedidos.append(deepcopy(pedido))
        doc = json.loads(pedido['mensagens'][1]['content'])['documento']
        return RespostaTransporte(texto=json.dumps(self.gerar(doc), ensure_ascii=False), **self.envelope)


def documento(doc_id, versao='1-prosa'):
    return C.documento_prosa(C.carregar_corpus(), doc_id, versao)


class AvaliacaoTest(unittest.TestCase):
    def test_condicao_a_reproduz_verificacao_atual(self):
        for cid in CENARIOS:
            res = resultado(cid)
            antigo = {x['trecho_id']: x['estado'] for x in res['verificacao_documental']['afirmacoes']}
            novo = {r['afirmacao']['trecho_id']: r['estado'] for r in revisao(cid, 'cadastro', res)['documentos'][0]['afirmacoes']}
            self.assertEqual(antigo, novo, cid)

    def test_condicao_c_coincide_com_estados_esperados(self):
        esperado = AV.ler(AV.REFERENCIAS/'dev/estados_esperados.json')['cenarios']
        for cid in CENARIOS:
            obtido = {k: dict(estado=r['estado'], motivo=r['motivo']) for k, r in por_id(revisao(cid)).items()}
            self.assertEqual(obtido, esperado[cid], cid)

    def test_d02_caminho_determinante_e_criticidade(self):
        r = por_id(revisao('D02'))
        nos = [n['no'] for n in r['SRP.RESUMO#2']['explicacao']['caminhos'][0]['nos']]
        self.assertEqual(nos, ['SUP_MOTOR', 'C_MOTOR', 'T_ASSEMBLY', 'M_PROTO_READY', 'TEST_LIFE',
                               'M_VALIDATION', 'T_DOC', 'T_RELEASE', 'M_RELEASE'])
        self.assertEqual(r['SRP.SUPRIMENTOS#2']['motivo'], 'premissa_alterada')
        self.assertTrue(r['SRP.SUPRIMENTOS#2']['calculado']['critico'])
        self.assertIn('dia 45', r['SRP.RESUMO#1']['sugestao'])
        # Evidências restritas ao caminho, não a todas as fontes ancestrais.
        self.assertLess(len(r['SRP.RESUMO#2']['explicacao']['evidencias']), 15)

    def test_d05_convergencia_ramo_dominado_e_mudanca_de_outro_fornecedor(self):
        r = por_id(revisao('D05'))
        self.assertEqual(r['SRP.SUPRIMENTOS#2']['estado'], 'ja_atualizado')
        self.assertFalse(r['SRP.SUPRIMENTOS#2']['calculado']['critico'])
        self.assertEqual(r['SRP.SUPRIMENTOS#3']['calculado']['mudadas'], ['SUP_HOUSING'])
        self.assertIn('ramo(s) paralelo(s)', r['SRP.RESUMO#2']['explicacao']['texto'])

    def test_d01_folga_absorve_e_explica(self):
        r = por_id(revisao('D01'))
        self.assertEqual(r['SRP.RESUMO#2']['estado'], 'ja_atualizado')
        self.assertTrue(r['SRP.RESUMO#2']['explicacao']['absorcoes'])
        self.assertEqual(r['SRP.SUPRIMENTOS#1']['estado'], 'revisar')

    def test_d04_indeterminado_nao_vira_zero(self):
        r = por_id(revisao('D04'))
        self.assertEqual(r['SRP.RESUMO#2']['motivo'], 'magnitude_sem_suporte')
        self.assertEqual(r['SRP.RESUMO#1']['motivo'], 'certeza_sem_suporte')
        self.assertIsNone(r['SRP.RESUMO#2']['calculado']['valor'])
        self.assertIn('a confirmar', r['SRP.RESUMO#2']['sugestao'])

    def test_execucao_incompleta_e_sem_estado(self):
        res = resultado('D04')
        res['pendencias_execucao'] = [{'no_id': 'X'}]
        r = por_id(revisao('D04', res=res))
        self.assertEqual((r['SRP.RESUMO#2']['estado'], r['SRP.RESUMO#2']['motivo']), ('nao_verificavel', 'execucao_incompleta'))
        res = resultado('D02')
        res['resultados_nos'] = [n for n in res['resultados_nos'] if n['no_id'] != 'M_VALIDATION']
        r = por_id(revisao('D02', res=res))
        self.assertEqual((r['SRP.TESTES#1']['estado'], r['SRP.TESTES#1']['motivo']), ('nao_verificavel', 'sem_estado_calculado'))

    def test_afirmacoes_conflitantes(self):
        cen = ler_cenario('D08')
        ext = deepcopy(AV.extracoes_referencia(cen))
        extra = deepcopy(ext[0]['afirmacoes'][1]); extra.update(id='SRP.RESUMO#9', valor=42, citacao='dia 40')
        ext[0]['afirmacoes'].append(extra)
        r = por_id(C.revisar_documentos(resultado('D08'), cen, ext, condicao='teste'))
        self.assertEqual(r['SRP.RESUMO#2']['motivo'], 'afirmacao_conflitante')
        self.assertEqual(r['SRP.RESUMO#9']['motivo'], 'afirmacao_conflitante')

    def test_nao_altera_entradas_nem_documentos(self):
        res, cen = resultado('D02'), ler_cenario('D02')
        ext = AV.extracoes_referencia(cen)
        copia = deepcopy((res, cen, ext))
        rev = C.revisar_documentos(res, cen, ext, condicao='referencia')
        self.assertEqual((res, cen, ext), copia)
        self.assertFalse(rev['atualizacao_executada'])
        self.assertIsNone(rev['aprovacao_humana'])
        self.assertEqual(rev['suporte_semantico'], 'nao_auditado')

    def test_executor_recusa_destino_existente_e_reproduz(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileExistsError):
                AV.executar(d)
            r = AV.executar(Path(d)/'nova')
            self.assertTrue(all(x['reproduz_verificacao_atual'] for x in r['linha_base_A'].values()))
            self.assertEqual(r['condicao_C']['divergencias'], [])
            self.assertEqual(r['chamadas_ia'], 0)


def afirmacao(trecho='T.X', predicado='valor', entidades=('SUP_MOTOR',), campo='fim', valor=18, unidade='dia_corrido',
              conhecimento='exato', limites=None, n=1):
    return dict(id=f'{trecho}#{n}', documento_id='DOC', versao='1', trecho_id=trecho, citacao='x', predicado=predicado,
                entidades=list(entidades), campo=campo, valor=valor, unidade=unidade, conhecimento=conhecimento,
                limites=limites, referencia_temporal='absoluta', registro=None, justificativa='teste')


def avaliar(cid, a):
    r = C.revisar_documentos(resultado(cid), ler_cenario(cid), [dict(documento_id='DOC', versao='1', afirmacoes=[a], nao_mapeados=[])], condicao='teste')
    x = r['documentos'][0]['afirmacoes'][0]
    return x['estado'], x['motivo'], x['calculado']


class PredicadosV3Test(unittest.TestCase):
    """Folga, duração, custo por parcela e faixas, exercitados só em D01–D09."""

    def test_folga_projetada(self):
        a = afirmacao(campo='folga', valor=2)
        self.assertEqual(avaliar('D08', a)[:2], ('ja_atualizado', 'confirmado'))
        self.assertEqual(avaliar('D01', a)[2]['valor'], 1)  # D19: folga cai para 1
        self.assertEqual(avaliar('D02', a)[:2], ('revisar', 'valor_divergente'))  # D25: crítico, folga 0
        self.assertEqual(avaliar('D02', a)[2]['valor'], 0)
        self.assertEqual(avaliar('D04', a)[:2], ('revisar', 'magnitude_sem_suporte'))

    def test_duracao(self):
        self.assertEqual(avaliar('D06', afirmacao(entidades=['TEST_LOAD'], campo='duracao', valor=4))[:2], ('revisar', 'valor_divergente'))
        self.assertEqual(avaliar('D02', afirmacao(entidades=['TEST_LIFE'], campo='duracao', valor=10))[:2], ('ja_atualizado', 'confirmado'))

    def test_custo_por_parcela_e_sem_alteracao(self):
        p10 = afirmacao(entidades=['p_10'], campo='custo', valor=3000000, unidade='BRL_centavo')
        self.assertEqual(avaliar('D03', p10)[:2], ('revisar', 'valor_divergente'))
        self.assertEqual(avaliar('D08', p10)[:2], ('ja_atualizado', 'confirmado'))
        lab = afirmacao(predicado='sem_alteracao', entidades=['p_17'], campo='custo', valor=None, unidade=None)
        self.assertEqual(avaliar('D06', lab)[:2], ('revisar', 'premissa_alterada'))
        self.assertEqual(avaliar('D02', lab)[:2], ('ja_atualizado', 'confirmado'))

    def test_faixa_de_semana(self):
        a = afirmacao(entidades=['M_RELEASE'], valor=None, conhecimento='faixa', limites=dict(minimo=38, maximo=41))
        self.assertEqual(avaliar('D08', a)[:2], ('ja_atualizado', 'confirmado'))
        self.assertEqual(avaliar('D02', a)[:2], ('revisar', 'valor_divergente'))
        self.assertEqual(avaliar('D04', a)[:2], ('revisar', 'magnitude_sem_suporte'))

    def test_contrato_v3(self):
        cat = X.catalogo_entidades()
        doc = dict(id='DOC', versao='1', trechos=[dict(id='T.X', texto='entrega na terceira semana; parcela R$ 30.000')])
        base = dict(trecho_id='T.X', citacao='entrega na terceira semana', predicado='valor', entidades=['SUP_MOTOR'], campo='fim',
                    valor=None, unidade='dia_corrido', conhecimento='faixa', limites=dict(minimo=14, maximo=20),
                    referencia_temporal='relativa', registro=None, justificativa='j')
        resp = lambda a: dict(versao=X.VERSAO, documento_id='DOC', versao_documento='1', afirmacoes=[a], nao_mapeados=[])
        self.assertEqual(X.validar_extracao(resp(base), doc, cat)['afirmacoes'][0]['limites'], dict(minimo=14, maximo=20))
        casos = [(dict(limites=None), 'conhecimento_inconsistente'),
                 (dict(limites=dict(minimo=20, maximo=14)), 'conhecimento_inconsistente'),
                 (dict(conhecimento='exato', valor=18), 'conhecimento_inconsistente'),
                 (dict(entidades=['p_10'], campo='fim'), 'campo_invalido')]
        for mud, codigo in casos:
            with self.assertRaises(X.ErroExtracao) as e:
                X.validar_extracao(resp({**base, **mud}), doc, cat)
            self.assertEqual(e.exception.codigo, codigo, mud)
        self.assertIn('p_10', {e['id'] for e in cat})


class InterfaceTest(unittest.TestCase):
    def test_endpoint_parcial_concluida_e_antes_da_execucao(self):
        from TCC_Codigos.etapas.alfa_documental_v2.src.sessoes import Sessoes
        from TCC_Codigos.etapas.alfa_documental_v2.src.demo import conteudo
        with tempfile.TemporaryDirectory() as d:
            m = Sessoes(d)
            s = m.preparar('D02', ['SUP_MOTOR'], '1')
            with self.assertRaises(ValueError):
                conteudo(m.ler(s['id']))
            s = m.executar(s['id'])
            parcial = conteudo(m.ler(s['id']))
            st = {a['id']: a['estado'] for a in parcial['documentos'][0]['afirmacoes']}
            self.assertEqual(st['SRP.RESUMO#2'], 'nao_verificavel')
            s = m.executar(s['id'], selecionados=s['pendentes'], max_nos='todos')
            final = conteudo(m.ler(s['id']))
            self.assertEqual(final['resumo'], {'revisar': 7, 'ja_atualizado': 3, 'julgamento_humano': 2, 'preservar': 1})
            self.assertFalse(final['atualizacao_executada'])
            doc = final['documentos'][0]
            self.assertTrue(all(a['citacao'] in next(t['texto'] for t in doc['trechos'] if t['id'] == a['trecho_id']) for a in doc['afirmacoes']))
            ia = conteudo(m.ler(s['id']), 'ia')
            self.assertEqual(ia['origem_ia']['versao_contrato'], '2-extracao-afirmacoes')
            st = {a['citacao']: a['estado'] for a in ia['documentos'][0]['afirmacoes']}
            self.assertEqual(st['o projeto segue dentro do cronograma'], 'revisar')
            self.assertEqual(st['essa entrega não está no caminho crítico'], 'revisar')
            cad = conteudo(m.ler(s['id']), 'cadastro')
            self.assertEqual(cad['resumo'], {'revisar': 3, 'ja_atualizado': 2})
            with self.assertRaises(ValueError):
                conteudo(m.ler(s['id']), 'gabarito')


    def test_rodada_ia_com_documento_invalido_mostra_erro(self):
        from TCC_Codigos.etapas.alfa_documental_v2.src.demo import extracoes_ia, RODADA_IA
        docs = C.documentos_do_cenario(ler_cenario('D02'))
        validas, falhas, _ = extracoes_ia(docs, RODADA_IA.parent/'extracao_ia_20261121')
        self.assertEqual({(e['documento_id'], e['versao']) for e in validas}, {('ACTION', '1-prosa'), ('DECISION', '1-prosa')})
        self.assertEqual(falhas[('STATUS', '1-prosa')][0]['codigo'], 'campo_invalido')


class ExtracaoTest(unittest.TestCase):
    def setUp(self):
        self.cat = X.catalogo_entidades()

    def extrator(self, gerar, **envelope):
        return X.ExtratorIA(Prescrito(gerar, **envelope), modelo='teste-offline', configuracao={'fixture': 'contrato'})

    def test_referencias_validam_no_contrato(self):
        for d in C.carregar_corpus()['documentos']:
            ext = referencia(d['id'], d['versao'])
            r = self.extrator(lambda _doc, ext=ext: resposta_de(ext)).extrair(d)
            self.assertEqual(r['estado'], 'extracao_recebida', (d['id'], d['versao'], r['erros']))
            m = X.comparar_extracoes(ext, r['extracao'])
            self.assertEqual((m['falsos_positivos'], m['falsos_negativos']), (0, 0))
            self.assertEqual(r['natureza'], 'simulacao_nao_mede_ia')

    def test_pedido_nao_leva_calculo_cenario_nem_referencia(self):
        t = Prescrito(lambda _doc: resposta_de(referencia('STATUS', '1-prosa')))
        X.ExtratorIA(t, modelo='teste-offline', configuracao={}).extrair(documento('STATUS'))
        conteudo = json.loads(t.pedidos[0]['mensagens'][1]['content'])
        self.assertEqual(set(conteudo), {'versao', 'documento', 'entidades', 'predicados'})
        bruto = t.pedidos[0]['mensagens'][1]['content']
        for proibido in ('fim_novo', 'CHANGE-D', 'estados_esperados', 'revisar', 'premissa_alterada'):
            self.assertNotIn(proibido, bruto)

    def test_controle_conflitante_e_nao_mapeados(self):
        d = documento('CONTROLES')
        r = self.extrator(lambda _doc: resposta_de(referencia('CONTROLES', '1-prosa'))).extrair(d)
        self.assertEqual(r['extracao']['conflitos'], ['CTL.C7#1', 'CTL.C7#2'])
        self.assertEqual({x['trecho_id'] for x in r['extracao']['nao_mapeados']}, {'CTL.C4', 'CTL.C6'})

    def erro(self, mutar, doc_id='STATUS', versao='1-prosa'):
        base = resposta_de(referencia(doc_id, versao))
        mutar(base)
        r = self.extrator(lambda _doc: base).extrair(documento(doc_id, versao))
        self.assertEqual(r['estado'], 'requer_revisao')
        return r['erros'][0]['codigo']

    def test_diagnosticos_do_contrato(self):
        def citacao(b): b['afirmacoes'][1]['citacao'] = 'lançamento no dia 40'
        def entidade(b): b['afirmacoes'][1]['entidades'] = ['INEXISTENTE']
        def pessoa(b): b['afirmacoes'][1]['entidades'] = ['P_CARLA']
        def prazo_nao_marco(b): b['afirmacoes'][0]['entidades'] = ['SUP_MOTOR']
        def conhecimento(b): b['afirmacoes'][1]['conhecimento'] = 'indeterminado'
        def cobertura(b): b['nao_mapeados'] = []
        def contradicao(b): b['nao_mapeados'].append(dict(trecho_id='SRP.TESTES', razao='fora_do_catalogo'))
        def booleano(b): b['afirmacoes'][0]['valor'] = 'sim'
        casos = dict(citacao='citacao_nao_literal', entidade='schema_invalido', pessoa='predicado_incompativel',
                     prazo_nao_marco='predicado_incompativel', conhecimento='conhecimento_inconsistente',
                     cobertura='cobertura_incompleta', contradicao='cobertura_contraditoria', booleano='conhecimento_inconsistente')
        for nome, codigo in casos.items():
            self.assertEqual(self.erro(locals()[nome]), codigo, nome)
        def sem_registro(b): b['afirmacoes'][0]['registro'] = None
        self.assertEqual(self.erro(sem_registro, 'RISK'), 'registro_ausente')

    def test_falhas_de_transporte_e_modo_real(self):
        r = self.extrator(lambda _doc: resposta_de(referencia('RISK', '1-prosa')), tokens_entrada=10).extrair(documento('RISK'))
        self.assertEqual(r['estado'], 'requer_revisao')
        r = self.extrator(lambda _doc: {}, estado='recusa').extrair(documento('RISK'))
        self.assertEqual(r['erros'][0]['codigo'], 'resposta_incompleta')
        # Modo real recusa transporte que não passa pelas reservas do ledger.
        with self.assertRaises(Exception):
            X.ExtratorIA(Prescrito(lambda d: {}), modelo='m', configuracao={}, modo='ia_real')
        with self.assertRaises(X.ErroExtracao) as e:
            X.ExtratorIA(Prescrito(lambda d: {}), modelo='m', configuracao={}, modo='outro')
        self.assertEqual(e.exception.codigo, 'modo_indisponivel')

    def test_metricas_contam_erros_de_extracao(self):
        ref = referencia('STATUS', '1-prosa')
        obtida = deepcopy(ref)
        obtida['afirmacoes'] = obtida['afirmacoes'][:-1]
        obtida['afirmacoes'][1] = dict(obtida['afirmacoes'][1], valor=41)
        m = X.comparar_extracoes(ref, obtida)
        self.assertEqual((m['verdadeiros_positivos'], m['falsos_negativos'], m['valor_correto']), (9, 1, 8))


if __name__ == '__main__':
    unittest.main()
