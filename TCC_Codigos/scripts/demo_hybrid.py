from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc_agent import Event, HybridImpactPipeline, ProjectGraph


def main() -> None:
    graph = ProjectGraph.from_json(ROOT / "data/project_graph.json")
    pipeline = HybridImpactPipeline(graph)

    event = Event(
        event_type="delay",
        primary_entity="SUP_MOTOR",
        related_entities=["C_MOTOR"],
        evidence="A MotorTech informou que o motor chegará 10 dias depois do previsto.",
    )

    result = pipeline.analyze(event)
    print("Artefatos a revisar:", result.affected_artifacts)
    print("Entidades impactadas:", result.impacted_entities)
    print("Rastreabilidade:")
    for target, path in result.trace.items():
        print("  ", " -> ".join(path))


if __name__ == "__main__":
    main()
