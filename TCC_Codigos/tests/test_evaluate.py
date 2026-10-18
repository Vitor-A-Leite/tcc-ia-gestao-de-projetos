import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc_agent.evaluate import set_metrics


def test_set_metrics_perfect_prediction():
    m = set_metrics(["a", "b"], ["a", "b"])
    assert m.precision == 1.0
    assert m.recall == 1.0
    assert m.f1 == 1.0
