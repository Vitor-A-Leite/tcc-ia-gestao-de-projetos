import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc_agent import Event, HybridImpactPipeline, ProjectGraph


def test_delay_pipeline_marks_documents():
    graph = ProjectGraph.from_json(ROOT / "data/project_graph.json")
    result = HybridImpactPipeline(graph).analyze(
        Event("delay", primary_entity="SUP_MOTOR", related_entities=["C_MOTOR"])
    )
    assert "risk_register" in result.affected_artifacts
    assert "status_report" in result.affected_artifacts
    assert "C_MOTOR" in result.impacted_entities


def test_informational_event_marks_no_documents():
    graph = ProjectGraph.from_json(ROOT / "data/project_graph.json")
    result = HybridImpactPipeline(graph).analyze(Event("informational"))
    assert result.affected_artifacts == []
