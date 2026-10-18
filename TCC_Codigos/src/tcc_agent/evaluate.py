from dataclasses import dataclass


@dataclass
class SetMetrics:
    precision: float
    recall: float
    f1: float
    true_positive: int
    false_positive: int
    false_negative: int


def set_metrics(expected: list[str], predicted: list[str]) -> SetMetrics:
    expected_set = set(expected)
    predicted_set = set(predicted)

    tp = len(expected_set & predicted_set)
    fp = len(predicted_set - expected_set)
    fn = len(expected_set - predicted_set)

    precision = tp / (tp + fp) if (tp + fp) else (1.0 if not expected_set else 0.0)
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return SetMetrics(precision, recall, f1, tp, fp, fn)


def event_type_accuracy(records: list[dict]) -> float:
    if not records:
        return 0.0
    correct = sum(r["expected_event_type"] == r["predicted_event_type"] for r in records)
    return correct / len(records)


def aggregate_artifact_metrics(records: list[dict]) -> SetMetrics:
    expected = []
    predicted = []
    # Micro-average: cada par cenário/artefato é tratado como uma decisão.
    for record in records:
        sid = record["scenario_id"]
        expected.extend(f"{sid}:{x}" for x in record["expected_artifacts"])
        predicted.extend(f"{sid}:{x}" for x in record["predicted_artifacts"])
    return set_metrics(expected, predicted)
