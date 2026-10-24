#!/usr/bin/env python3
"""Exporta entradas e avalia conclusões V2 com o mesmo contrato por condição.

Padrão: demonstração sem API. Também recebe previsões JSONL externas. As
referências dos exemplos são rascunhos autorais e não um benchmark científico.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if sys.version_info < (3, 10):
    raise SystemExit('Use Python 3.10+; neste projeto execute com .venv/bin/python.')
sys.path.insert(0, str(ROOT / "src"))
from tcc_agent.evidence_assessment import (
    EvidenceEngine, build_request, evaluate_prediction, load_case, number,
)


def load_predictions(path):
    result = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        key = (item["case_id"], item["condition"])
        if key in result:
            raise ValueError("Previsão duplicada: " + str(key))
        result[key] = item
    return result


def condition_metrics(records, condition, questions_per_record, expected_rows=()):
    selected = [r for r in records if r["condition"] == condition]
    rows = [row for r in selected if r["evaluation"] for row in r["evaluation"]["rows"]]
    total = sum(questions_per_record[r["case_id"]] for r in selected)
    supported_claims = [r for r in rows if r["predicted_status"] != "undetermined"]
    unknown_refs = [r for r in rows if r["expected_status"] == "undetermined"]
    result = {
        "n_expected_questions": total,
        "n_scored_questions": len(rows),
        "conclusion_accuracy": sum(r["conclusion_correct"] for r in rows) / total if total else 0,
        "magnitude_accuracy": sum(r["magnitude_correct"] for r in rows) / total if total else 0,
        "unjustified_precision_count": sum(r["unjustified_precision"] for r in rows),
        "visible_context_accuracy": sum(r["reference_correct"] for r in rows) / total if total else 0,
        "full_context_outcome_accuracy": sum(r["full_context_outcome_correct"] for r in rows) / total if total else 0,
        "action_accuracy": sum(r["actions_compatible"] for r in rows) / total if total else 0,
        "unsupported_assertions": sum(r["unsupported_assertion"] for r in rows),
        "unsupported_assertion_rate": sum(r["unsupported_assertion"] for r in rows) / len(supported_claims) if supported_claims else None,
        "appropriate_uncertainty_count": sum(r["appropriate_uncertainty"] for r in rows),
        "missed_conclusions": sum(r["expected_status"] != "undetermined" and r["predicted_status"] == "undetermined" for r in rows),
        "reference_rule_disagreements": sum(not r["reference_rule_agreement"] for r in rows),
    }
    # Denominadores vêm das perguntas esperadas: registros inválidos não somem.
    groups = sorted({(r['dimension'], r.get('measure', 'legacy_unspecified'), r['expected_status']) for r in expected_rows})
    result['by_dimension_measure_status'] = []
    for dimension, measure, status in groups:
        def matches(r):
            return (r['dimension'], r.get('measure', 'legacy_unspecified'), r['expected_status']) == (dimension, measure, status)
        expected_n = sum(matches(r) for r in expected_rows)
        scored = [r for r in rows if matches(r)]
        result['by_dimension_measure_status'].append({'dimension':dimension, 'measure':measure, 'expected_status':status,
            'n_expected_questions':expected_n, 'n_scored_questions':len(scored),
            'visible_context_accuracy':sum(r['reference_correct'] for r in scored)/expected_n,
            'unsupported_assertions':sum(r['unsupported_assertion'] for r in scored)})
    result['by_dimension_direction'] = []
    for dimension, direction in sorted({(r['dimension'],r['expected_direction']) for r in expected_rows}):
        expected_n = sum(r['dimension']==dimension and r['expected_direction']==direction for r in expected_rows)
        scored = [r for r in rows if r['dimension']==dimension and r.get('expected_direction')==direction]
        result['by_dimension_direction'].append({'dimension':dimension,'expected_direction':direction,
            'n_expected_questions':expected_n,'n_scored_questions':len(scored),
            'visible_context_accuracy':sum(r['reference_correct'] for r in scored)/expected_n})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "data/evidence_protocol_v2_examples.json")
    parser.add_argument("--predictions", type=Path, help="JSONL com case_id, condition e prediction; deve cobrir todos os casos/condições")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("A pasta de saída já existe; escolha uma nova.")
    dataset = json.loads(args.cases.read_text())
    if dataset['protocol_version'] not in {'2.0-draft', '2.2-draft'}:
        raise ValueError('Versão não suportada; não converter medidas automaticamente.')
    scoped = dataset['protocol_version'] == '2.2-draft'
    engine_type, make_request, evaluate, load = EvidenceEngine, build_request, evaluate_prediction, load_case
    if scoped:
        from tcc_agent import scoped_evidence
        engine_type, make_request, evaluate, load = scoped_evidence.EvidenceEngine, scoped_evidence.build_request, scoped_evidence.evaluate_prediction, scoped_evidence.load_case
    graph = dataset['graph'] if scoped else json.loads((ROOT / "data/project_graph.json").read_text())
    cases = dataset["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError('O conjunto precisa conter casos; vazio não é validação aprovada.')
    if len({c["case_id"] for c in cases}) != len(cases):
        raise ValueError("IDs de casos duplicados.")
    predictions = load_predictions(args.predictions) if args.predictions else None
    expected_keys = {(c["case_id"], condition) for c in cases for condition in ["baseline", "hybrid"]}
    if predictions is not None and set(predictions) != expected_keys:
        raise ValueError("Cobertura incompleta ou condições/casos desconhecidos nas previsões.")
    args.output.mkdir(parents=True)
    records, requests = [], []
    expected_rows = {condition: [] for condition in ['baseline', 'hybrid']}
    with patch("socket.socket", side_effect=AssertionError("Avaliação V2 não acessa rede")):
        for raw in cases:
            context, questions, references = load(raw, raw.get('graph', graph) if scoped else graph)
            for condition in ["baseline", "hybrid"]:
                if scoped:
                    ref_map = {r.question_id:r for r in references[condition]}
                    expected_rows[condition].extend({**vars(q), 'expected_status':ref_map[q.question_id].status, 'expected_direction':ref_map[q.question_id].direction} for q in questions)
                else:
                    ref_map = {(r.target,r.dimension):r for r in references[condition]}
                    expected_rows[condition].extend({**vars(q), 'expected_status':ref_map[(q.target,q.dimension)].status, 'expected_direction':ref_map[(q.target,q.dimension)].direction} for q in questions)
                visible = context.visible(condition)
                request = make_request(raw["case_id"], context, questions, condition)
                requests.append({"case_id": raw["case_id"], "condition": condition, "request": request})
                if predictions is None:
                    # Demonstração funcional, jamais rotulada como previsão de IA.
                    payload = {"assessments": [engine_type(visible).assess(q).to_dict() for q in questions]}
                else:
                    payload = predictions[(raw["case_id"], condition)].get("prediction")
                record = {"case_id": raw["case_id"], "condition": condition,
                          "mode": "rule_demonstration" if predictions is None else "external_predictions",
                          "prediction": payload, "evaluation": None, "error": None}
                try:
                    record["evaluation"] = evaluate(payload, visible, questions, references[condition])
                    # Resultado com o conhecimento completo é uma métrica
                    # separada, não um critério de evidência acessível ao baseline.
                    full_refs = {(r.question_id if scoped else (r.target, r.dimension)): r for r in references["hybrid"]}
                    claims = {(r['question_id'] if scoped else (r["target"], r["dimension"])): r for r in payload["assessments"]}
                    for row in record["evaluation"]["rows"]:
                        key = row['question_id'] if scoped else (row["target"], row["dimension"])
                        claim, ref = claims[key], full_refs[key]
                        if not scoped:
                            row['expected_direction'] = ref_map[(row['target'],row['dimension'])].direction
                            row['predicted_direction'] = claim['direction']
                        delta = number(claim["delta"]) if claim["delta"] is not None else None
                        row["full_context_outcome_correct"] = (claim["status"], claim["direction"], delta) == (ref.status, ref.direction, ref.delta)
                except (ValueError, TypeError) as exc:
                    record["error"] = type(exc).__name__ + ": " + str(exc)
                records.append(record)
                ok = record["evaluation"] is not None and record["evaluation"]["passed"]
                print(raw["case_id"], condition, "PASS" if ok else "REVISAR", flush=True)
    for name, rows in [("requests_without_references.jsonl", requests), ("evaluations.jsonl", records)]:
        (args.output / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    summary = {
        "protocol": dataset["protocol_version"], "mode": records[0]["mode"] if records else "empty",
        "n_cases": len(cases), "n_condition_records": len(records), "n_questions": sum(len(c["questions"]) * 2 for c in cases),
        "n_passed_records": sum(bool(r["evaluation"] and r["evaluation"]["passed"]) for r in records),
        "n_invalid_records": sum(r["error"] is not None for r in records),
        "unsupported_assertions": sum(r["evaluation"]["unsupported_assertions"] for r in records if r["evaluation"]),
        "dataset_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
        "graph_sha256": hashlib.sha256(json.dumps(graph,ensure_ascii=False,sort_keys=True).encode()).hexdigest() if scoped else hashlib.sha256((ROOT / "data/project_graph.json").read_bytes()).hexdigest(),
        "graph_origin": "hypothetical_dataset" if scoped else "project_graph.json",
        "api_calls": 0,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": {condition: condition_metrics(records, condition, {c["case_id"]: len(c["questions"]) for c in cases}, expected_rows[condition]) for condition in ["baseline", "hybrid"]},
        "warning": "Exemplos de desenvolvimento autorais; concordância do motor com eles não mede desempenho de IA nem valida o domínio. Revisão independente ainda necessária.",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["n_passed_records"] == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
