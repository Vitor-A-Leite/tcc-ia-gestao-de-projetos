"""Regras documentais usadas pela arquitetura híbrida.

As regras não tentam substituir o gerente. Elas indicam quais artefatos
merecem revisão depois que um tipo de evento foi identificado.
"""

EVENT_TO_ARTIFACTS = {
    "delay": ["risk_register", "status_report"],
    "decision": ["decision_log", "action_log"],
    "test_problem": ["risk_register", "action_log", "status_report"],
    "technical_change": ["decision_log", "risk_register", "status_report"],
    "action_commitment": ["action_log"],
    "risk_signal": ["risk_register", "status_report"],
    "supplier_change": ["decision_log", "risk_register", "status_report"],
    "informational": [],
}


def artifacts_for_event(event_type: str) -> list[str]:
    """Retorna os documentos que devem ser revisados para um tipo de evento."""
    return list(EVENT_TO_ARTIFACTS.get(event_type, []))
