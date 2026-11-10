"""Contrato do modo real com transporte inteiramente falso e sockets bloqueados.

Estes testes não são resultados de IA; validam identidade, orçamento e estados.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..src import DATA
from ..src.sessoes import Sessoes
from ..src.pipeline import ler_cenario
from ..src.modelo import carregar
from ..src.simulacao import interpretador
from ..src.vendor.hibrido_v07_r3.adaptador import LocalV07R3
from ..src.vendor.hibrido_v07_r3.contratos import VERSAO
from ..src.vendor.interpretacao_no.adaptadores import RespostaTransporte, FalhaTransporte


class TransporteFalso:
    origem='openai_real';versao_formato_local=VERSAO
    def __init__(self):
        g,_=carregar();fixture=json.loads((DATA/'simulacoes/dev/D02.json').read_text())
        self.responder=interpretador(fixture,g).resposta
        self.n=0;self.parado=False;self.falhar=False;self.uso_desconhecido=False
    def snapshot(self):
        return dict(chamadas_api=self.n,tokens_entrada=self.n*10,tokens_saida=self.n*5,
                    custo_api_usd=0 if self.uso_desconhecido else self.n*.0001,
                    comprometido_usd=self.n*.01 if self.uso_desconhecido else self.n*.0001,
                    segundos=self.n*.001,uso_desconhecido=self.uso_desconhecido)
    def __call__(self,pedido):
        self.n+=1
        if self.falhar:
            self.parado=True;self.uso_desconhecido=True
            raise FalhaTransporte('rede_teste','Falha preparada, sem rede')
        c=json.loads(pedido['mensagens'][1]['conteudo'])['contexto']
        return RespostaTransporte(texto=json.dumps(self.responder(c)),modelo='gpt-6-luna',
                                 request_id='falso-'+str(self.n),tokens_entrada=10,tokens_saida=5,
                                 custo_api_centavos=None,metadados={'custo_api_usd':.0001,'moeda':'USD'})


class SugestorFalso:
    origem='openai_real'
    def __init__(self,t):self.transporte=t
    def snapshot(self):return self.transporte.snapshot()
    def __call__(self,pedido):
        self.transporte.n+=1
        return dict(sugestoes=[dict(no_id='SUP_MOTOR',justificativa='Resposta falsa de teste vinculada ao relato.')],ambiguidades=[])


class SessaoRealContrato(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.m=Sessoes(self.tmp.name);self.t=TransporteFalso();self.a=LocalV07R3(self.t,modelo='gpt-6-luna',configuracao={'reasoning':{'effort':'high'}},timeout_s=180)
        self.rede=patch('socket.socket',side_effect=AssertionError('Rede proibida no teste de contrato'))
        self.rede.start();self.addCleanup(self.rede.stop)
    def preparar(self,**kwargs):
        return self.m.preparar('D02',['SUP_MOTOR'],32,modo='ia_real',limites={'max_solicitacoes':33,'max_custo_centavos':40,'max_segundos':7200},**kwargs)
    def test_json_real_sem_leitura_fixture(self):
        c=ler_cenario('D02');c['id']='EVENTO_JSON_REAL';c['particao']='piloto_real'
        original=Path.read_text
        def ler(p,*a,**kw):
            if 'simulacoes' in p.parts:raise AssertionError('Modo real leu fixture')
            return original(p,*a,**kw)
        with patch.object(Path,'read_text',ler):
            s=self.m.preparar(c['id'],['SUP_MOTOR'],32,modo='ia_real',cenario=c,limites={'max_solicitacoes':33,'max_custo_centavos':40})
            s=self.m.executar(s['id'],adaptador_real=self.a)
        self.assertEqual(s['resultado']['modo'],'ia_real');self.assertFalse(s['resultado']['simulacao_nao_mede_ia'])
        self.assertEqual(s['resultado']['delta_dias']['valor'],5);self.assertEqual(s['consumo']['solicitacoes_simuladas'],0)
    def test_sugestao_e_locais_compartilham_snapshot(self):
        s=self.preparar();t=SugestorFalso(self.t)
        self.m.sugestao(s['id'],'uma',t);self.m.sugestao(s['id'],'uma',t)
        with self.assertRaisesRegex(ValueError,'Confirme'):self.m.executar(s['id'],adaptador_real=self.a)
        self.m.selecionar(s['id'],['SUP_MOTOR'],32,origem='ia_autorizada_pelo_usuario')
        s=self.m.executar(s['id'],adaptador_real=self.a)
        self.assertEqual(self.t.n,14);self.assertEqual(s['consumo']['chamadas_api'],14)
        self.assertEqual(s['consumo']['solicitacoes_reais'],14);self.assertEqual(s['consumo']['tokens_entrada'],140)
        self.assertAlmostEqual(s['consumo']['custo_api_usd'],.0014)
        self.assertEqual(s['historico_selecoes'][-1]['origem'],'ia_autorizada_pelo_usuario')
    def test_teto_real_acumulado_e_retomada(self):
        s=self.preparar();self.m.sugestao(s['id'],'uma',SugestorFalso(self.t));self.m.selecionar(s['id'],['SUP_MOTOR'],32)
        s=self.m.executar(s['id'],adaptador_real=self.a,limites={'max_solicitacoes':2})
        self.assertEqual(self.t.n,2);self.assertEqual(s['visitados'],['SUP_MOTOR']);self.assertEqual(s['estado'],'pausada')
        s=self.m.executar(s['id'],adaptador_real=self.a,selecionados=['C_MOTOR'],limites={'max_solicitacoes':3})
        self.assertEqual(self.t.n,3);self.assertEqual(s['consumo']['chamadas_api'],3)
    def test_falha_desconhecida_interrompe_sem_tentativas_falsas(self):
        s=self.preparar();self.t.falhar=True;s=self.m.executar(s['id'],adaptador_real=self.a)
        self.assertEqual(self.t.n,1);self.assertEqual(s['consumo']['solicitacoes_reais'],1)
        self.assertTrue(s['consumo']['uso_desconhecido']);self.assertEqual(s['consumo']['comprometido_api_usd'],.01)
        self.assertIsNone(s['resultado']['fim_novo']['valor'])
    def test_modo_real_explicito_orcamento_e_adaptador(self):
        with self.assertRaisesRegex(ValueError,'financeiro'):self.m.preparar('D02',['SUP_MOTOR'],32,modo='ia_real')
        s=self.preparar()
        with self.assertRaisesRegex(ValueError,'adaptador_real'):self.m.executar(s['id'])
        offline=self.m.preparar('D02',['SUP_MOTOR'],32)
        with self.assertRaisesRegex(ValueError,'offline'):self.m.executar(offline['id'],adaptador_real=self.a)
        self.assertEqual(self.t.n,0)


if __name__=='__main__':unittest.main()
