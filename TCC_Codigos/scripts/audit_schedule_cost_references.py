#!/usr/bin/env python3
"""Prepara pacote de revisão offline; não executa modelos nem avalia desempenho."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

if sys.version_info < (3, 10):
    raise SystemExit('Use Python 3.10+; neste projeto execute com .venv/bin/python.')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tcc_agent.reference_review import audit_reference_set, build_review_request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    path = ROOT / 'data/reference_sets/alfa_schedule_cost_v2_1_draft.json'
    with patch('socket.socket', side_effect=AssertionError('Rede proibida nesta auditoria')):
        bundle = json.loads(path.read_text())
        graph = json.loads((ROOT / 'data/project_graph.json').read_text())
        summary = audit_reference_set(bundle, ROOT / 'data')
        summary['reference_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        summary['source_hashes'] = bundle['source_hashes']
        summary['api_calls'] = 0
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'audit.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
        with (args.output / 'inputs_without_answers.jsonl').open('w') as stream:
            for case in bundle['cases']:
                for condition in ['baseline', 'hybrid']:
                    stream.write(json.dumps(build_review_request(bundle, case, graph, condition), ensure_ascii=False) + '\n')
        lines = ['# Caderno de revisão — prazo e custo', '',
                 'Referências autorais provisórias. Não são respostas da IA nem validação independente.',
                 'As conclusões valem condicionalmente aos relatos; cada cenário é isolado.',
                 'Nenhum exemplo hipotético foi incorporado como fato do Projeto Alfa.', '',
                 f'Fonte versionada: `{path.relative_to(ROOT)}`; SHA-256 `{summary["reference_sha256"]}`.', '',
                 '| Caso | Medida local de prazo | Referência local | Liberação final | Custo local / total |',
                 '|---|---|---|---|---|']
        for case in bundle['cases']:
            qs = case['questions']
            local = next((q for q in qs if q['scope']=='local' and q['dimension']=='schedule'), None)
            label = '—'
            if local:
                r = local['reference_by_condition']['baseline']
                label = 'indeterminado' if r['delta'] is None else 'sem variação' if r['delta']=='0' else '+'+r['delta']+' dias (base não especificada)'
            lines.append(f'| {case["case_id"]} | {local["measure"] if local else "não consultada"} | {label} | indeterminado | indeterminado |')
        lines += ['', '## Anotações para revisão', '',
                  'Preencher reviewer, reviewed_at, decision e notes no JSON após revisão externa. Discordâncias devem ter justificativa; não ajustar respostas apenas para concordar com o motor.', '']
        for case in bundle['cases']:
            lines += [f'### {case["case_id"]}', '', '> '+case['sources']['event'], '']
            for q in case['questions']:
                r = q['reference_by_condition']['baseline']
                lines += [f'- **{q["question_id"]}** — {q["target"]}, {q["measure"]}. Escopo: {q["scope_description"]}',
                          f'  Referência em ambas as condições: `{r["status"]}/{r["direction"]}`, delta `{r["delta"]}`. {q["rationale"]}',
                          '  Providência: '+q['action_detail']]
                if q['missing_information']:
                    lines.append('  Faltam: '+'; '.join(q['missing_information']))
            lines += ['', 'Revisor: ______ | Concordância/correção e justificativa: ______', '']
        (args.output / 'CADERNO_REVISAO.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'output':str(args.output),'cases':summary['cases'],'questions_per_condition':summary['questions_per_condition'],'counts':summary['counts'],'api_calls':0,'approved_for_real_runs':False},ensure_ascii=False))


if __name__ == '__main__':
    main()
