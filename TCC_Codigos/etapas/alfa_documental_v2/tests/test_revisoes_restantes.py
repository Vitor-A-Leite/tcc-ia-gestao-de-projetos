from copy import deepcopy
import unittest
from unittest.mock import patch
from ..scripts.concluir_revisoes_lote import RevisorComRespostasPreservadas
from ..src.revisao import RevisorIA


class ReusoRevisoesTests(unittest.TestCase):
    def test_preserva_parecer_invalido_e_so_envia_pacote_novo(self):
        pacote={'pacote_hash':'h','valor':25}
        ruim={'estado':'requer_revisao','parecer':None,'resposta_bruta':'original'}
        a={'registros':[{'pacote':pacote,'revisao_semantica':ruim}]};antes=deepcopy(a)
        revisor=object.__new__(RevisorComRespostasPreservadas);revisor.carregar_anteriores(a)
        with patch.object(RevisorIA,'revisar',return_value='novo') as enviar:
            self.assertEqual(revisor.revisar(pacote),ruim);enviar.assert_not_called()
            with self.assertRaises(ValueError):revisor.revisar({'pacote_hash':'h','valor':26})
            enviar.assert_not_called()
            self.assertEqual(revisor.revisar({'pacote_hash':'outro'}),'novo')
            self.assertEqual(enviar.call_count,1)
        self.assertEqual(a,antes)
        self.assertEqual(revisor.reutilizados,['h'])
