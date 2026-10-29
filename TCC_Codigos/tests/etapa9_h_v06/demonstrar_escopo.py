"""Exporta a contraprova sintética. Nunca lê/rescreve saídas de inferência real."""
import argparse
import json
from pathlib import Path

from hibrido_v05 import avaliar as avaliar_v05, construir as construir_v05, SimuladoV05, SCHEMA as SCHEMA_V05
from hibrido_v06 import avaliar, construir, SimuladoV06
from test_encaminhamentos import analise, encaminhar, projeto, fixtures


def demonstrar():
    e, ev = projeto()
    def resposta_v05(c):
        a = fixtures.analise(c, versao=SCHEMA_V05)
        if c['no_id'] == 'n_alpha':
            a['pendencias_operacionais'] = ['Sem permissão local para lançar p_aa11']
        return a

    def sem_resolucao(c):
        a = analise(c)
        if c['no_id'] == 'n_alpha':
            a['encaminhamentos'] = [encaminhar(c, 'substituir_duracao', 'n_beta')]
        if c['no_id'] == 'n_beta':
            a['propostas'] = []
        return a

    def falta_factual(c):
        a = analise(c)
        if c['no_id'] == 'n_alpha':
            a['pendencias_operacionais'] = ['Falta factual local não representada']
        return a

    resultados = {'v05_bloqueio_original_mock': avaliar_v05(
        e, ev, SimuladoV05(resposta_v05), construir_v05(e, ev, execucao_id='demo_v05_mock'))}
    for nome, resposta in [('v06_encaminhamento_resolvido', analise),
                           ('v06_encaminhamento_nao_resolvido', sem_resolucao),
                           ('v06_falta_factual_preservada', falta_factual)]:
        resultados[nome] = avaliar(e, ev, SimuladoV06(resposta), construir(e, ev, execucao_id=nome))
    return dict(
        natureza='MOCK sintético prescrito, sem LLM ou avaliação de acurácia',
        ressalva='As respostas simuladas usam contratos diferentes; não são reparos nem replay de respostas reais.',
        chamadas_reais=0,
        resumo={nome: dict(estado=r['execucao']['estado'], delta_dias=r['delta_dias']['valor'],
                           delta_centavos=r['delta_centavos']['valor'],
                           encaminhamentos=r['registro_operacional']['fechamento_final'].get('encaminhamentos', []))
                for nome, r in resultados.items()},
        resultados=resultados,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, required=True)
    args = parser.parse_args()
    dados = demonstrar()
    # Artefatos são novos: uma segunda execução deve escolher outro destino.
    with args.saida.open('x') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps(dados['resumo'], ensure_ascii=False, indent=2))
