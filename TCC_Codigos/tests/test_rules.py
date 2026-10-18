import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc_agent.rules import artifacts_for_event


def test_delay_requires_risk_and_status():
    assert artifacts_for_event("delay") == ["risk_register", "status_report"]


def test_informational_requires_no_update():
    assert artifacts_for_event("informational") == []
