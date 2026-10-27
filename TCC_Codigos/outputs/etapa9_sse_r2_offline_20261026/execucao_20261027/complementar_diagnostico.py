"""Complemento descritivo offline; não modifica respostas nem faz chamadas."""
import json
import sqlite3
from pathlib import Path
from collections import Counter
from statistics import mean, median
O = Path(__file__).parent
W = O.parent.parent / 'etapa9_piloto_real_aprovado_20261026'
db = sqlite3.connect('file:' + str((W / 'ledger.sqlite').resolve()) + '?mode=ro', uri=True)
regs = [json.loads(row[0]) for row in db.execute('SELECT resultado FROM slots_v04')]
proof_path = O / 'texto_obrigatorio_revalidacao_offline.json'
proof = json.loads(proof_path.read_text())
counts = Counter()
for item in proof:
    reg = next(r for r in regs if r['metadados']['execucao_id'] == item['execucao_id'])
    step = next(t for t in reg['resultado']['rastro_orquestracao'] if t['no_id'] == item['no_id'])
    raw = step['analise']['execucao']['tentativas'][0]['resposta_bruta']
    value = json.loads(raw)['justificativa']
    item['justificativa_tipo'] = type(value).__name__
    item['justificativa_comprimento'] = len(value)
    item['justificativa_vazia_apos_strip'] = None
    item['contrato_exige'] = 'string não vazia; lista não satisfaz texto()'
    item['tipos_itens'] = sorted({type(v).__name__ for v in value})
    counts[(type(value).__name__, len(value))] += 1
assert len(proof) == 15 and all(item['justificativa_tipo'] == 'list' for item in proof)
proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2))
p = O / 'diagnostico_descritivo.json'
diag = json.loads(p.read_text())
lat = diag['latencias_preservadas_por_call_id']
for reg in regs:
    if reg['metadados']['condicao'] == 'H':
        continue
    result = reg['resultado']
    phase = 'R2 SSE' if 'adendo_transporte_sse' in result else 'R1' if 'adendo_retomada' in result else 'Primeira'
    for attempt in result.get('consumo', {}).get('tentativas', []):
        cid = (attempt.get('metadados') or {}).get('call_id')
        if cid and type(attempt.get('latencia_ms')) in (float, int):
            lat[str(cid)] = dict(fase=phase, condicao=reg['metadados']['condicao'], latencia_ms=attempt['latencia_ms'])
for phase, total, expected in [('Primeira', 46, 44), ('R1', 10, 9), ('R2 SSE', 201, 201)]:
    values = [value['latencia_ms'] / 1000 for value in lat.values() if value['fase'] == phase]
    assert len(values) == expected
    diag['latencia_por_fase'][phase] = dict(n_medidas=len(values), N_chamadas=total, media_s=mean(values), mediana_s=median(values), min_s=min(values), max_s=max(values), escopo='contagem+inferência+adaptação local; somente IDs/tempos preservados, sem imputar ausentes')
diag['justificativas_tipo_incompativel'] = dict(total=15, tipo='list', comprimentos={str(k): v for k, v in counts.items()}, exigencia='string não vazia')
p.write_text(json.dumps(diag, ensure_ascii=False, indent=2))
db.close()
print(json.dumps(dict(justificativas=dict(diag['justificativas_tipo_incompativel']), latencias=diag['latencia_por_fase']), ensure_ascii=False))
