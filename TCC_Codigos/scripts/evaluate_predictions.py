import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc_agent.baseline import validate_prediction
from tcc_agent.evaluate import aggregate_artifact_metrics, event_type_accuracy


def main() -> None:
    gt = json.loads((ROOT / "data/scenarios_ground_truth.json").read_text(encoding="utf-8"))
    gt_by_id = {x["scenario_id"]: x for x in gt}
    pred_dir = ROOT / "outputs/predictions"

    records = []
    parse_errors = []

    for path in sorted(pred_dir.glob("*.json")):
        sid = path.stem
        if sid not in gt_by_id:
            continue
        try:
            payload = validate_prediction(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            parse_errors.append({"scenario_id": sid, "error": str(exc)})
            continue

        expected = gt_by_id[sid]
        records.append({
            "scenario_id": sid,
            "expected_event_type": expected["expected_event_type"],
            "predicted_event_type": payload["event_type"],
            "expected_artifacts": expected["expected_artifacts"],
            "predicted_artifacts": payload["affected_artifacts"],
        })

    metrics = aggregate_artifact_metrics(records)
    result = {
        "evaluated_scenarios": len(records),
        "parse_errors": parse_errors,
        "event_type_accuracy": event_type_accuracy(records),
        "artifact_precision": metrics.precision,
        "artifact_recall": metrics.recall,
        "artifact_f1": metrics.f1,
        "true_positive": metrics.true_positive,
        "false_positive": metrics.false_positive,
        "false_negative": metrics.false_negative,
    }

    out = ROOT / "outputs/evaluation.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
