"""Verificações offline de comportamento, fronteiras e preservação."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from . import ROOT
from .pipeline import simular,executar,ler_cenario
from .modelo import carregar,projetar,normalizar,grafo_documental
from .politica import construir
from .documentos import registrar_decisao
from hibrido_v07_r3.adaptador import SimuladoV07R3
from hibrido_v07_r3.orquestracao import avaliar
from hibrido_v07_r3.politica import construir as politica_legada
from motor_deterministico.motor import preparar
from interpretacao_no.contratos import hash_json


class Alfa(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results={f'D{i:02}':simular(f'D{i:02}') for i in range(1,10)}
    def test_folga(self):
        r=self.results['D01'];self.assertEqual(r['delta_dias']['valor'],0)
        self.assertEqual(r['folgas_base_dias']['SUP_MOTOR'],2)
        self.assertIn('absorvido_ou_dominado',{e['estado'] for e in r['propagacao']})
    def test_caminho_critico(self):
        r=self.results['D02'];self.assertEqual(r['delta_dias']['valor'],5);self.assertEqual(r['delta_centavos']['valor'],150000)
        self.assertEqual(len(r['rastro_orquestracao']),32)
    def test_preco_sem_atraso(self):
        r=self.results['D03'];self.assertEqual(r['delta_dias']['valor'],0);self.assertEqual(r['delta_centavos']['valor'],300000)
    def test_ignorancia_nao_vira_zero(self):
        r=self.results['D04'];self.assertIsNone(r['fim_novo']['valor']);self.assertIsNone(r['custo_novo']['valor'])
        self.assertEqual(r['fim_novo']['limites']['inferior'],40)
    def test_custo_desconhecido_nao_bloqueia_prazo(self):
        r=self.results['D09'];self.assertEqual(r['fim_novo']['valor'],40);self.assertIsNone(r['custo_novo']['valor'])
    def test_convergencia_maximo(self):
        r=self.results['D05'];self.assertEqual(r['delta_dias']['valor'],4)
        for n in ('C_HOUSING','C_SHAFT','C_BEARING','C_SEAL'): self.assertIn(n,r['nos_com_mudanca_quantitativa'])
        self.assertEqual(r['delta_centavos']['valor'],120000)
    def test_custo_compartilhado(self):
        r=self.results['D06'];self.assertEqual(r['delta_centavos']['valor'],320000)
        # Dois testes se alongam; só 4 dias de laboratório excedente (não 2+4).
        book=r['livro_parcelas'];self.assertEqual(len({x['parcela_id'] for x in book}),len(book))
        self.assertEqual(next(x for x in book if x['parcela_id']=='p_17')['delta']['valor'],200000)
    def test_documento_desatualizado(self):
        rs=self.results['D02']['verificacao_documental']['recomendacoes']
        self.assertEqual({x['trecho_id'] for x in rs},{'SR.FINISH','SR.COST','SR.MOTOR'})
        self.assertTrue(all(x['atualizacao_executada'] is False and x['aprovacao_humana'] is None for x in rs))
    def test_ja_atualizado(self):
        r=self.results['D07']['verificacao_documental'];self.assertFalse(r['recomendacoes']);self.assertEqual(len(r['afirmacoes']),5)
    def test_sem_efeito(self):
        r=self.results['D08'];self.assertFalse(r['nos_com_mudanca_quantitativa']);self.assertFalse(r['verificacao_documental']['recomendacoes'])
    def test_relacao_nao_e_impacto(self):
        r=self.results['D02'];self.assertNotIn('T_CAD',r['nos_com_mudanca_quantitativa'])
        for n in r['grafo']['nodes']:
            if n['type'] in ('Document','Person','ProjectArea'): self.assertNotIn(n['id'],r['nos_com_mudanca_quantitativa'])
    def test_documentos_versoes_e_cad(self):
        r=self.results['D07'];ns={n['id']:n for n in r['grafo']['nodes']}
        self.assertEqual(ns['T_CAD']['type'],'Task');self.assertEqual(ns['DOC_CAD@1']['type'],'Document')
        self.assertTrue({'STATUS@0','STATUS@1','STATUS@2'}<=ns.keys())
    def test_encaminhamento_tem_resolucao(self):
        r=self.results['D02']['registro_operacional']['fechamento_final']['encaminhamentos']
        self.assertEqual(len(r),1);self.assertEqual(r[0]['criterio'],'manutencao_escopada_clausula_unica')
    def test_limite_explicitamente_parcial(self):
        r=simular('D02',max_analises=8)
        self.assertEqual(r['execucao']['estado'],'parcial');self.assertIsNone(r['fim_novo']['valor'])
        self.assertTrue(any('Limite' in x for x in r['lacunas']))
        # A disponibilidade local já validada pode ser revisada; os totais não.
        self.assertEqual({x['trecho_id'] for x in r['verificacao_documental']['recomendacoes']},{'SR.MOTOR'})
    def test_legacy_preserva_limite(self):
        g,d=carregar();e=projetar(g,d);ev=normalizar(ler_cenario('D02'),e)
        with self.assertRaisesRegex(ValueError,'limite'): politica_legada(e,ev,execucao_id='test')
    def test_ciclo_rejeitado(self):
        g,d=carregar();e=projetar(g,d)
        e['relacoes'].append(dict(id='cycle',origem_id='M_RELEASE',destino_id='T_REQ',tipo='precede_FS',lag_dias=0,fonte_refs=e['relacoes'][0]['fonte_refs']))
        with self.assertRaisesRegex(ValueError,'Ciclo'): preparar(e)
    def test_baseline_inconsistente_rejeitada(self):
        g,d=carregar();g['fim_base']=41
        with self.assertRaisesRegex(ValueError,'Baseline'): projetar(g,d)
    def test_fonte_inventada_rejeitada(self):
        # Mantém bruto inválido; não é convertido em ausência de efeito.
        original=self.results['D02']['rastro_orquestracao'][0]
        c=original['contexto'];w=deepcopy(original['analise']['execucao']['resposta_wire'])
        w['propostas']=[dict(operacao='substituir_restricao',alvo_id='release_C_COUPLING',atributo='valor',unidade='dia_corrido',valor=dict(estado='exato',valor=99,evidencias=[dict(fonte_id='INVENTADA',localizador='x')],lacunas=[],motivo=None),evidencias=[dict(fonte_id='INVENTADA',localizador='x')],relacao_refs=[],regra_refs=[],condicoes=[],origem_ref=dict(fonte_id='INVENTADA',localizador='x'))]
        a=SimuladoV07R3(w).analisar(c);self.assertEqual(a['execucao']['estado'],'erro')
    def test_entrada_imutavel(self):
        g,d=carregar();e=projetar(g,d);before=hash_json([g,d,e]);simular('D02');self.assertEqual(before,hash_json([g,d,e]))
    def test_aprovacao_nao_edita_oficial(self):
        r=self.results['D02']['verificacao_documental']['recomendacoes'][0];d=ler_cenario('D02')['registro_vigente'];h=hash_json(d)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'decisao.json';entry=registrar_decisao(r,'aprovar','Revisor fictício do teste','Somente teste',d,p)
            self.assertFalse(entry['atualizacao_executada']);self.assertEqual(h,hash_json(d))
            with self.assertRaises(FileExistsError): registrar_decisao(r,'aprovar','Teste','Teste',d,p)
            d['versao']='outra'
            with self.assertRaisesRegex(ValueError,'mudou'): registrar_decisao(r,'aprovar','Teste','Teste',d,Path(tmp)/'outra.json')
    def test_logs_sem_criacao_automatica(self):
        for r in self.results.values():
            for item in r['verificacao_documental']['triagem_outros_artefatos']: self.assertEqual(item['recomendacoes'],[])
    def test_simulacao_zero_chamadas(self):
        for r in self.results.values(): self.assertEqual(r['consumo']['chamadas'],0);self.assertTrue(r['simulacao_nao_mede_ia'])
    def test_cadastro_versionado_sem_sobrescrita(self):
        from .cadastro import cadastrar
        c=ler_cenario('D01')['documento']
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'entrada.json';p.write_text(json.dumps(c));out=Path(tmp)/'registro'
            cadastrar(p,out,['SUP_MOTOR'])
            with self.assertRaises(ValueError): cadastrar(p,out,['SUP_MOTOR'])
            c.update(versao='2',anterior=c['id']+'@1');p.write_text(json.dumps(c));cadastrar(p,out,['SUP_MOTOR'])
            self.assertEqual(len(list(out.glob('*.json'))),2)
    def test_documento_vinculo_falso_e_pdf_recusados(self):
        from .cadastro import validar_documento,cadastrar
        c=ler_cenario('D01')['documento']
        with self.assertRaises(ValueError): validar_documento(c,[])
        with self.assertRaisesRegex(ValueError,'Word/PDF'): cadastrar(Path('qualquer.pdf'),Path('nao_criar'),[])
    def test_custo_destaca_proprietario_sem_atraso(self):
        r=self.results['D03'];self.assertEqual(r['nos_com_mudanca_prazo'],[])
        self.assertIn('SUP_MOTOR',r['nos_com_mudanca_custo'])
    def test_ramo_menor_nao_e_causa_da_convergencia(self):
        r=self.results['D02']
        e=next(e for e in r['propagacao'] if e['origem']=='TEST_LOAD' and e['destino']=='M_VALIDATION')
        self.assertEqual(e['estado'],'dominado_na_convergencia')
    def test_avaliador_conta_falsos_e_falhas(self):
        from .avaliacao import avaliar_resultados
        r=deepcopy(self.results['D02']);recs=r['verificacao_documental']['recomendacoes']
        recs[0]['trecho_id']='SR.FREEZE'  # um positivo removido e um negativo marcado
        r['execucao']['estado']='erro'
        m=avaliar_resultados([r],'dev');self.assertEqual(m['documental']['FP'],1);self.assertEqual(m['documental']['FN'],1)
        self.assertEqual(m['prazo']['acertos_estado_e_valor'],0);self.assertEqual(m['prazo']['total'],1)


def run():
    with patch('socket.socket',side_effect=AssertionError('Rede proibida nos testes offline')):
        return unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Alfa))
if __name__=='__main__':
    raise SystemExit(0 if run().wasSuccessful() else 1)
