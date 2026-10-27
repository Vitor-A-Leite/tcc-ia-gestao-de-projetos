"""MOCKS de integração matemática/contrato, não teste de desempenho do LLM."""
import unittest
from copy import deepcopy
from cenarios import projeto,analise
from hibrido_v05 import avaliar,construir,SimuladoV05,SCHEMA
class IntegracaoV05(unittest.TestCase):
    def rodar(self,notas=False,desconhecer=False,taxa=False):
        e,ev=projeto();p=construir(e,ev,execucao_id='mock_v05')
        i=SimuladoV05(lambda c:analise(c,versao=SCHEMA,custo=1000,notas=notas,desconhecer=desconhecer,taxas_desconhecidas=taxa))
        return avaliar(e,ev,i,p)
    def test_ausencia_de_clausula_com_duas_obrigacoes_e_custo_temporal(self):
        r=self.rodar();self.assertEqual(r['execucao']['estado'],'ok',r)
        self.assertEqual(r['delta_dias']['valor'],2);self.assertEqual(r['delta_centavos']['valor'],11000)
        self.assertEqual(r['fim_novo']['valor'],max(6,5)+3)
        self.assertEqual(len({p['parcela_id']for p in r['livro_parcelas']}),4)
    def test_nota_local_sobre_marco_nao_substitui_solver(self):
        r=self.rodar(notas=True);self.assertEqual(r['execucao']['estado'],'ok',r)
        self.assertEqual(r['delta_dias']['valor'],2);self.assertEqual(r['delta_centavos']['valor'],11000)
        self.assertTrue(r['notas_diagnosticas_locais']);self.assertFalse(r['lacunas'])
    def test_falta_real_duracao_e_readequacao_continua_desconhecida(self):
        r=self.rodar(desconhecer=True);self.assertEqual(r['execucao']['estado'],'parcial',r)
        self.assertIsNone(r['delta_dias']['valor']);self.assertIsNone(r['delta_centavos']['valor'])
        self.assertNotEqual(r['delta_centavos']['estado'],'exato')
    def test_taxa_realmente_ausente_nao_vira_zero(self):
        r=self.rodar(taxa=True);self.assertEqual(r['delta_dias']['valor'],2,r)
        self.assertIsNone(r['delta_centavos']['valor']);self.assertNotEqual(r['delta_centavos']['estado'],'exato')
if __name__=='__main__':unittest.main()
