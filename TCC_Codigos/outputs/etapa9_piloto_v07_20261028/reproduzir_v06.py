"""Controles vermelhos preservados: quatro bloqueios v06, sem rede/credenciais."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'TCC_Codigos/tests/etapa9_h_v06'))
from test_encaminhamentos import projeto, analise, encaminhar
from hibrido_v06 import avaliar, construir, SimuladoV06, LocalV06, VERSAO
from interpretacao_no.adaptadores import RespostaTransporte

OLD = Path(__file__).parent.parent / 'etapa9_piloto_v06_20261027'

class BloqueiosV06(unittest.TestCase):
    def replay_local(self, caso, no):
        f = OLD / ('etapa9-v06-90-BHT-R2-20261027-' + caso + '-H-1.json')
        r = json.loads(f.read_text())['resultado']
        passo = next(x for x in r['rastro_orquestracao'] if x['no_id'] == no)
        raw = passo['analise']['execucao']['tentativas'][0]['resposta_bruta']
        class Transporte:
            versao_formato_local = VERSAO
            def __call__(self, request):
                return RespostaTransporte(raw)
        return LocalV06(Transporte(), modelo='mock', configuracao={}, timeout_s=1).analisar(passo['contexto'])

    def test_identidade_tecnica_nao_deveria_depender_de_copia_llm(self):
        r = self.replay_local('k_a064', 'n_21dc')
        self.assertEqual(r['execucao']['estado'], 'ok', r['execucao']['erros'])

    def test_direcao_exata_redundante_nao_deveria_invalidar_valor(self):
        r = self.replay_local('k_09c2', 'n_e659')
        self.assertEqual(r['execucao']['estado'], 'ok', r['execucao']['erros'])

    def test_manutencao_por_clausula_resolve_objetivo_de_duracao(self):
        e, ev = projeto()
        def resposta(c):
            a = analise(c)
            if c['no_id'] == 'n_alpha':
                a['encaminhamentos'] = [encaminhar(c, 'substituir_duracao', 'n_join')]
            return a
        r = avaliar(e, ev, SimuladoV06(resposta), construir(e, ev, execucao_id='repro_manutencao'))
        self.assertEqual(r['execucao']['estado'], 'ok', r.get('lacunas'))

    def test_pendencia_de_custo_nao_deveria_apagar_prazo_representado(self):
        e, ev = projeto()
        def resposta(c):
            a = analise(c)
            if c['no_id'] == 'n_alpha':
                a['pendencias_operacionais'] = ['MOCK: um preço adicional permanece desconhecido.']
            return a
        r = avaliar(e, ev, SimuladoV06(resposta), construir(e, ev, execucao_id='repro_dimensoes'))
        self.assertEqual(r['delta_dias']['estado'], 'exato', r.get('lacunas'))
        self.assertEqual(r['delta_centavos']['estado'], 'indeterminado')

if __name__ == '__main__':
    unittest.main()
