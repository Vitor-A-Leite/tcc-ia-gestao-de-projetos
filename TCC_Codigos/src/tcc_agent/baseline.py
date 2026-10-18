import json
from pathlib import Path


ALLOWED_EVENT_TYPES = {
    "delay",
    "decision",
    "test_problem",
    "technical_change",
    "action_commitment",
    "risk_signal",
    "supplier_change",
    "informational",
}

ALLOWED_ARTIFACTS = {
    "action_log",
    "risk_register",
    "decision_log",
    "status_report",
}


def build_entity_dictionary(project_graph_path: str | Path) -> str:
    data = json.loads(Path(project_graph_path).read_text(encoding="utf-8"))
    lines = [f'- {node["id"]}: {node["name"]} ({node["type"]})' for node in data["nodes"]]
    return "\n".join(lines)


def build_baseline_prompt(source_text: str, entity_dictionary: str) -> str:
    """Monta o prompt do baseline LLM-only.

    O modelo recebe apenas o evento e o dicionário de entidades. Ele NÃO
    recebe o grafo nem as regras documentais da arquitetura proposta.
    """
    return f"""Você é um analisador de eventos de gestão de projetos.

Tarefa:
1. Classifique o evento.
2. Identifique a entidade principal e entidades relacionadas.
3. Indique quais artefatos gerenciais podem precisar de revisão.
4. Indique as entidades do projeto que podem ter sido impactadas.

Tipos permitidos:
{', '.join(sorted(ALLOWED_EVENT_TYPES))}

Artefatos permitidos:
{', '.join(sorted(ALLOWED_ARTIFACTS))}

Dicionário de entidades:
{entity_dictionary}

Evento:
{source_text}

Responda SOMENTE em JSON no formato:
{{
  "event_type": "...",
  "primary_entity": "ID ou null",
  "related_entities": ["ID"],
  "affected_artifacts": ["nome"],
  "impacted_entities": ["ID"],
  "responsible": "ID ou null",
  "due_date": "AAAA-MM-DD ou null",
  "effective_date": "AAAA-MM-DD ou null"
}}
"""


def validate_prediction(payload: dict) -> dict:
    """Valida e normaliza a resposta JSON do LLM."""
    required = {
        "event_type",
        "primary_entity",
        "related_entities",
        "affected_artifacts",
        "impacted_entities",
        "responsible",
        "due_date",
        "effective_date",
    }
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Campos ausentes: {sorted(missing)}")

    if payload["event_type"] not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"Tipo de evento inválido: {payload['event_type']}")

    invalid_artifacts = set(payload["affected_artifacts"]) - ALLOWED_ARTIFACTS
    if invalid_artifacts:
        raise ValueError(f"Artefatos inválidos: {sorted(invalid_artifacts)}")

    for field in ["related_entities", "affected_artifacts", "impacted_entities"]:
        if not isinstance(payload[field], list):
            raise ValueError(f"O campo {field} precisa ser uma lista.")

    return payload
