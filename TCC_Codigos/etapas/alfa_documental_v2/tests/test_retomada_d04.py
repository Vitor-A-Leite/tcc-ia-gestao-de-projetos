"""Garantias da continuação autorizada, sem chamadas ou chave reais."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from ..scripts.retomar_lote_d04 import (copiar_checkpoint, restaurar_incerteza_financeira,
    BarreiraRetomada, TransporteRetomada, executar)
from ..src.ia_real import TransporteReal
from ..src.vendor.interpretacao_no.contratos import hash_json


class RetomadaTests(unittest.TestCase):
    def setUp(self):
        self.req = {'mensagens': [{}, {'conteudo': json.dumps({'contexto': {
            'no_id': 'TEST_THERMAL', 'contexto_hash': 'hash-thermal'}})}]}
        self.falha = dict(no_id='TEST_THERMAL', contexto_hash='hash-thermal', execucao=dict(
            estado='erro', erros=[{'codigo': 'rede'}], requisicao_adaptador_hash=hash_json(self.req)))
        self.original = dict(cenario_id='D04', estado='pausada', falha_real_bloqueante=True,
            pendentes=['TEST_THERMAL', 'M_VALIDATION'], cache={
                'hash-ok': {'no_id': 'TEST_SEAL', 'execucao': {'estado': 'ok'}},
                'hash-thermal': self.falha},
            consumo=dict(uso_desconhecido=True, chamadas_api=10, comprometido_api_usd=.0279946,
                         custo_api_usd=.0129946), resultado={})

    def test_copia_preserva_original_respostas_validas_e_custos(self):
        antes = deepcopy(self.original)
        s, f = copiar_checkpoint(self.original, 'Retomada autorizada')
        self.assertEqual(self.original, antes)
        self.assertEqual(s['cache'], {'hash-ok': antes['cache']['hash-ok']})
        self.assertEqual(f, self.falha)
        self.assertEqual(s['consumo']['comprometido_api_usd'], .0279946)
        self.assertEqual(s['retomada']['consumo_anterior'], antes['consumo'])
        self.assertFalse(s['consumo']['uso_desconhecido'])
        self.assertTrue(s['consumo']['uso_desconhecido_anterior'])
        restaurar_incerteza_financeira(s)
        self.assertTrue(s['consumo']['uso_desconhecido'])
        self.assertFalse(s['retomada']['novo_uso_desconhecido'])

    def test_nova_incerteza_nao_e_ocultada(self):
        s, _ = copiar_checkpoint(self.original, 'Autorizado')
        s['consumo']['uso_desconhecido'] = True
        s['resultado'] = {'execucao': {'estado': 'parcial'}}
        restaurar_incerteza_financeira(s)
        self.assertTrue(s['retomada']['novo_uso_desconhecido'])
        self.assertTrue(s['resultado']['consumo_acumulado']['uso_desconhecido'])

    def test_sem_autorizacao_ou_outra_falha_bloqueia(self):
        with self.assertRaises(ValueError): copiar_checkpoint(self.original, '')
        self.original['cache']['hash-thermal']['execucao']['erros'][0]['codigo'] = 'saida_invalida'
        with self.assertRaises(ValueError): copiar_checkpoint(self.original, 'Autorizado')
        with patch('socket.socket', side_effect=AssertionError('Sem rede')):
            with self.assertRaises(ValueError): executar('/ausente', '/ausente', 'Autorizado')

    def test_barreira_bloqueia_reenvio_e_pedido_alterado_antes_do_transporte(self):
        # Sem __init__: nenhuma carteira ou transporte é aberto neste teste.
        t = object.__new__(TransporteRetomada)
        t.configurar_barreira(self.original, self.falha)
        alterado = deepcopy(self.req); alterado['extra'] = 'alterou o pedido'
        with patch.object(TransporteReal, '__call__', return_value='resposta') as enviar:
            with self.assertRaises(ValueError): t(alterado)
            enviar.assert_not_called()
            self.assertEqual(t(self.req), 'resposta')
            with self.assertRaises(ValueError): t(self.req)
            self.assertEqual(enviar.call_count, 1)
            valido = deepcopy(self.req)
            valido['mensagens'][1]['conteudo'] = json.dumps({'contexto': {'no_id': 'TEST_SEAL'}})
            with self.assertRaises(ValueError): t(valido)
            self.assertEqual(enviar.call_count, 1)


if __name__ == '__main__': unittest.main()
