"""Exemplo prescrito: um nó, fonte fictícia explícita, zero rede."""
import argparse
import json
from pathlib import Path
from . import montar_contexto, hash_json, Simulado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('estado', type=Path)
    args = parser.parse_args()
    estado = json.loads(args.estado.read_text(encoding='utf-8'))
    fonte = dict(id='fonte_demo', documento_id='documento_demo', versao='1', localizador='L01',
                 trecho='O cartucho n_c820 estará disponível em D4; demais efeitos não definidos neste aviso ilustrativo.')
    evento = dict(evento_id='evento_demo', projeto_id=estado['projeto_id'], versao_projeto=estado['versao'],
                  instante_observacao=0, relato=fonte['trecho'], escopo=estado['escopo'], lacunas=[],
                  origem=dict(autor='Exemplo fictício offline', documento_id='documento_demo', data_registro='D0'), evidencias=[fonte])
    c = montar_contexto(estado, evento, execucao_id='demo_offline', no_id='n_c820', revisao=1,
                       fonte_ids=[f['id'] for f in estado['fontes']] + ['fonte_demo'])
    ref = dict(fonte_id='fonte_demo', localizador='L01')
    desconhecido = dict(estado='indeterminado', valor=None, direcao='desconhecida', evidencias=[ref],
                       lacunas=['Não há conclusão quantitativa local neste exemplo'], motivo=None)
    # Resposta prescrita somente no adapter simulado, nunca incorporada ao contexto.
    a = dict(schema_version='1.0-proposta', analise_id='analise_demo',
             **{k: c[k] for k in ('execucao_id','evento_id','no_id','revisao','contexto_hash','predecessores_versoes')},
             avaliacao=dict(prazo=desconhecido, custo=desconhecido),
             justificativa='Demonstração prescrita de contrato; não é interpretação real validada.', lacunas=[],
             propostas=[dict(id='proposta_demo', no_id='n_c820', operacao='substituir_disponibilidade',
                             alvo_id='n_c820', atributo='disponibilidade', unidade='dia_corrido',
                             valor=dict(estado='exato', valor=4, direcao='desconhecida', evidencias=[ref], lacunas=[], motivo=None),
                             evidencias=[ref], relacao_refs=[], regra_refs=[], condicoes=[],
                             origens_causais=[dict(evento_id='evento_demo', fato_ref=ref, efeito_id=hash_json(['evento_demo','n_c820']))])])
    print(json.dumps(dict(contexto=c, analise=Simulado(a).analisar(c)), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
