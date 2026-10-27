"""Regressões diferenciais do legado; log RED original preservado; fixtures sintéticas, zero API."""
import unittest
from copy import deepcopy
from cenarios import projeto,analise
from piloto_real.politica import construir
from interpretacao_no.adaptadores import Simulado
from orquestracao import avaliar
from motor_deterministico.motor import preparar
class Contraprovas(unittest.TestCase):
    def test_ausencia_especifica_com_duas_obrigacoes_distintas(self):
        e,ev=projeto();preparar(e);p=construir(e,ev,execucao_id='mock_escopo')
        class Mock:
            origem='simulado'
            def analisar(self,c):return Simulado(analise(c,custo=1000)).analisar(c)
        r=avaliar(e,ev,Mock(),p)
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertIsNone(r['delta_dias']['valor'])
    def test_nota_global_nao_bloqueia_motor_completo(self):
        e,ev=projeto();p=construir(e,ev,execucao_id='mock_solver')
        class Mock:
            origem='simulado'
            def analisar(self,c):return Simulado(analise(c,custo=0,notas=True)).analisar(c)
        r=avaliar(e,ev,Mock(),p)
        self.assertEqual(r['registro_operacional']['fechamento_final']['estado'],'completo_operacional_condicional')
        self.assertIsNone(r['delta_dias']['valor'])
        self.assertIsNone(r['delta_centavos']['valor'])
if __name__=='__main__':unittest.main()
