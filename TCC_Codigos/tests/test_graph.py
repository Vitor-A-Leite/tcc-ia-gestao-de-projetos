import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc_agent.graph import ProjectGraph


def test_graph_loads_40_nodes_and_65_edges():
    graph = ProjectGraph.from_json(ROOT / "data/project_graph.json")
    assert len(graph.nodes) == 40
    assert len(graph.edges) == 65


def test_motor_supplier_reaches_motor_component():
    graph = ProjectGraph.from_json(ROOT / "data/project_graph.json")
    impacted, _ = graph.downstream(["SUP_MOTOR"], max_depth=1)
    assert "C_MOTOR" in impacted


def test_unknown_entity_is_ignored():
    graph = ProjectGraph.from_json(ROOT / "data/project_graph.json")
    impacted, trace = graph.downstream(["DOES_NOT_EXIST"], max_depth=3)
    assert impacted == []
    assert trace == {}
