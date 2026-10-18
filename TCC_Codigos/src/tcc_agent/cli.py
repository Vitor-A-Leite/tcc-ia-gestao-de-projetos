import argparse
import json
from pathlib import Path

from .graph import ProjectGraph
from .models import Event
from .pipeline import HybridImpactPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Protótipo de análise de impacto do TCC")
    parser.add_argument("--graph", default="data/project_graph.json")
    parser.add_argument("--event-type", required=True)
    parser.add_argument("--primary-entity", required=False)
    parser.add_argument("--related", nargs="*", default=[])
    args = parser.parse_args()

    graph = ProjectGraph.from_json(args.graph)
    pipeline = HybridImpactPipeline(graph)
    result = pipeline.analyze(
        Event(
            event_type=args.event_type,
            primary_entity=args.primary_entity,
            related_entities=args.related,
        )
    )

    print(json.dumps({
        "event_type": result.event.event_type,
        "impacted_entities": result.impacted_entities,
        "affected_artifacts": result.affected_artifacts,
        "trace": result.trace,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
