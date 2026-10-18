from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Event:
    """Representa um evento extraído de uma ata, mensagem ou relatório."""

    event_type: str
    primary_entity: Optional[str] = None
    related_entities: list[str] = field(default_factory=list)
    responsible: Optional[str] = None
    due_date: Optional[str] = None
    effective_date: Optional[str] = None
    evidence: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class ImpactResult:
    """Resultado produzido pelo motor de análise de impacto."""

    event: Event
    impacted_entities: list[str]
    affected_artifacts: list[str]
    trace: dict[str, list[str]] = field(default_factory=dict)
