"""Andaime offline explícito: templates prescritos, nunca interpretação textual.

Este módulo não faz parte da política automática. A fixture deve vir de caminho
explicitamente escolhido; não há acesso a referências, outros casos ou outputs.
"""
from copy import deepcopy
from interpretacao_no import Simulado
from interpretacao_no.contratos import hash_json
from . import Politica


class InterpretadorPrescrito:
    origem = 'simulado'
    def __init__(self, fixture):
        self.templates = deepcopy(fixture['propostas_por_no'])
        self.contextos = []

    def analisar(self, c):
        self.contextos.append(deepcopy(c))
        props = deepcopy(self.templates[c['no_id']])
        # Avaliação local não é previsão final; somente confirmação de ausência exige zero.
        desconhecido = dict(estado='indeterminado', valor=None, direcao='desconhecida', evidencias=[], lacunas=['Avaliação local prescrita pelas propostas'], motivo=None)
        custo = deepcopy(desconhecido)
        if any(p['operacao'] == 'confirmar_ausencia_parcela_adicional' for p in props):
            p = next(p for p in props if p['operacao'] == 'confirmar_ausencia_parcela_adicional')
            custo = dict(estado='exato', valor=0, direcao='zero', evidencias=p['evidencias'], lacunas=[], motivo=None)
        a = {k: deepcopy(c[k]) for k in ('execucao_id', 'evento_id', 'no_id', 'revisao', 'contexto_hash', 'predecessores_versoes')}
        a.update(schema_version='1.0-proposta', analise_id='simulada-'+c['no_id'],
                 avaliacao={'prazo': desconhecido, 'custo': custo}, propostas=props,
                 justificativa='SIMULADA: transcrição autoral prescrita fora do contexto', lacunas=[])
        return Simulado(a).analisar(c)


def politica_prescrita(fixture, **limites):
    templates = deepcopy(fixture['propostas_por_no'])
    def resolver(c, a):
        # Igualdade com uma decisão externa preexistente, não hash da resposta.
        return a['propostas'] == templates[c['no_id']]
    return Politica(execucao_id=fixture['execucao_id'], alvos=fixture['alvos'],
                    plano=fixture['plano'], origem=fixture['origem'], fechamento=True,
                    resolver=resolver, dispensas=fixture.get('dispensas', {}), **limites)
