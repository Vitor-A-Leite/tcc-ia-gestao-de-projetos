from .graph import ProjectGraph
from .models import Event, ImpactResult
from .rules import artifacts_for_event


class HybridImpactPipeline:
    """Combina evento estruturado + grafo + regras documentais."""

    def __init__(self, graph: ProjectGraph, max_depth: int = 4):
        self.graph = graph
        self.max_depth = max_depth

    def analyze(self, event: Event) -> ImpactResult:
        seeds = []
        if event.primary_entity:
            seeds.append(event.primary_entity)
        seeds.extend(event.related_entities)

        # Remove duplicatas preservando a ordem.
        seeds = list(dict.fromkeys(seed for seed in seeds if self.graph.has_entity(seed)))

        impacted, trace = self.graph.downstream(seeds, max_depth=self.max_depth)

        # As entidades diretamente citadas também fazem parte da análise.
        all_impacted = list(dict.fromkeys(event.related_entities + impacted))

        return ImpactResult(
            event=event,
            impacted_entities=all_impacted,
            affected_artifacts=artifacts_for_event(event.event_type),
            trace=trace,
        )
