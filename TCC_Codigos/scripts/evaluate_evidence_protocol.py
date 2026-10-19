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


def condition_metrics(records, condition, questions_per_record):
    selected = [r for r in records if r["condition"] == condition]
    rows = [row for r in selected if r["evaluation"] for row in r["evaluation"]["rows"]]
    total = sum(questions_per_record[r["case_id"]] for r in selected)
    supported_claims = [r for r in rows if r["predicted_status"] != "undetermined"]
    unknown_refs = [r for r in rows if r["expected_status"] == "undetermined"]
    return {
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "data/evidence_protocol_v2_examples.json")
    parser.add_argument("--predictions", type=Path, help="JSONL com case_id, condition e prediction; deve cobrir todos os casos/condições")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("A pasta de saída já existe; escolha uma nova.")
    dataset = json.loads(args.cases.read_text())
    graph = json.loads((ROOT / "data/project_graph.json").read_text())
    cases = dataset["cases"]
    if len({c["case_id"] for c in cases}) != len(cases):
        raise ValueError("IDs de casos duplicados.")
    predictions = load_predictions(args.predictions) if args.predictions else None
    expected_keys = {(c["case_id"], condition) for c in cases for condition in ["baseline", "hybrid"]}
    if predictions is not None and set(predictions) != expected_keys:
        raise ValueError("Cobertura incompleta ou condições/casos desconhecidos nas previsões.")
    args.output.mkdir(parents=True)
    records, requests = [], []
    with patch("socket.socket", side_effect=AssertionError("Avaliação V2 não acessa rede")):
        for raw in cases:
            context, questions, references = load_case(raw, graph)
            for condition in ["baseline", "hybrid"]:
                visible = context.visible(condition)
                request = build_request(raw["case_id"], context, questions, condition)
                requests.append({"case_id": raw["case_id"], "condition": condition, "request": request})
                if predictions is None:
                    # Demonstração funcional, jamais rotulada como previsão de IA.
                    payload = {"assessments": [EvidenceEngine(visible).assess(q).to_dict() for q in questions]}
                else:
                    payload = predictions[(raw["case_id"], condition)].get("prediction")
                record = {"case_id": raw["case_id"], "condition": condition,
                          "mode": "rule_demonstration" if predictions is None else "external_predictions",
                          "prediction": payload, "evaluation": None, "error": None}
                try:
                    record["evaluation"] = evaluate_prediction(payload, visible, questions, references[condition])
                    # Resultado com o conhecimento completo é uma métrica
                    # separada, não um critério de evidência acessível ao baseline.
                    full_refs = {(r.target, r.dimension): r for r in references["hybrid"]}
                    claims = {(r["target"], r["dimension"]): r for r in payload["assessments"]}
                    for row in record["evaluation"]["rows"]:
                        key = (row["target"], row["dimension"])
                        claim, ref = claims[key], full_refs[key]
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
        "graph_sha256": hashlib.sha256((ROOT / "data/project_graph.json").read_bytes()).hexdigest(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": {condition: condition_metrics(records, condition, {c["case_id"]: len(c["questions"]) for c in cases}) for condition in ["baseline", "hybrid"]},
        "warning": "Exemplos de desenvolvimento autorais; concordância do motor com eles não mede desempenho de IA nem valida o domínio. Revisão independente ainda necessária.",
    }
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["n_passed_records"] == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
