import unittest
from copy import deepcopy
from ..scripts.concluir_lote_d09 import inspecionar, AVISO_INSPECIONADO, RELATO_INSPECIONADO, executar


class ConclusaoTests(unittest.TestCase):
    def setUp(self):
        self.s=dict(sugestoes=[dict(no_id='SUP_MOTOR')],ambiguidades=[AVISO_INSPECIONADO])
        self.c=dict(id='D09',entidades_mencionadas=['SUP_MOTOR'],
                    documento=dict(trechos=[dict(texto=RELATO_INSPECIONADO)]))

    def test_decisao_preserva_aviso_original_e_declara_intervencao(self):
        antes=deepcopy(self.s);d=inspecionar(self.s,self.c)
        self.assertEqual(self.s,antes)
        self.assertEqual(d['selecao'],['SUP_MOTOR'])
        self.assertEqual(d['natureza'],'inspecao_do_assistente_nao_aprovacao_humana')
        self.assertFalse(d['nova_sugestao_solicitada'])

    def test_outra_ambiguidade_ou_entidade_bloqueia(self):
        self.s['ambiguidades']=['Fornecedor desconhecido']
        with self.assertRaises(ValueError):inspecionar(self.s,self.c)
        self.s['ambiguidades']=[AVISO_INSPECIONADO];self.s['sugestoes'][0]['no_id']='SUP_GEAR'
        with self.assertRaises(ValueError):inspecionar(self.s,self.c)

    def test_fonte_alterada_ou_sem_autorizacao_bloqueia(self):
        self.c['documento']['trechos'][0]['texto']='Preço conhecido'
        with self.assertRaises(ValueError):inspecionar(self.s,self.c)
        with self.assertRaises(ValueError):executar('/ausente','/ausente','/ausente','Autorizado')
