"""Fecho conservador por relações temporais e responsabilidades financeiras."""
import re
from .vendor.orquestracao import ordem


def construir(estado, evento, grafo, sementes):
    seq, pred = ordem(estado)
    regiao = set(sementes)
    if not regiao or not regiao <= set(seq): raise ValueError('Sementes inválidas.')
    motivos = {n: ['Ponto de entrada confirmado pelo engenheiro'] for n in sementes}
    owners = {p['id']: p['proprietario'] for p in grafo['parcelas']}
    literais = set(re.findall(r'\bp_[0-9a-f]+\b', evento['relato']))
    if not literais <= owners.keys(): raise ValueError('Obrigação sem responsável cadastrado.')
    for p in literais:
        n = owners[p]; regiao.add(n); motivos.setdefault(n, []).append('Responsável pela obrigação citada: '+p)
    mudou = True
    while mudou:
        antes = set(regiao)
        for n in seq:
            causas = pred[n] & regiao
            if causas:
                regiao.add(n); motivos.setdefault(n, []).append('Dependência temporal de '+', '.join(sorted(causas)))
        for r in estado['regras_custo']:
            ends = {v['atividade_id'] for v in r['intervalo'].values() if isinstance(v, dict)}
            if ends & regiao:
                owner = owners[r['parcela_id']]; regiao.add(owner)
                motivos.setdefault(owner, []).append('Responsabilidade contratual '+r['id'])
        mudou = antes != regiao
    return dict(nos=[n for n in seq if n in regiao],
                motivos={n: list(dict.fromkeys(motivos[n])) for n in sorted(regiao)},
                predecessores_externos={n: sorted(pred[n]-regiao) for n in sorted(regiao) if pred[n]-regiao},
                excluidos={n: 'Fora do alcance cadastrado das entradas; cálculo mantém estado e fontes. Sem interpretação semântica.' for n in seq if n not in regiao},
                premissa='Cobertura condicionada às relações e menções cadastradas; não certifica completude do mundo real.')
