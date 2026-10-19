"""Protocolo V2: prazo/custo, evidência e avaliação comuns às duas condições.

Este módulo não chama LLMs, não altera o grafo legado e não transforma ausência
no grafo em prova de ausência de impacto. As regras são deliberadamente limitadas
a modelos temporais/financeiros explicitamente declarados no contexto.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json

RELATIONS = {"supplies", "precedes", "required_for", "validated_by", "belongs_to"}
TEMPORAL_RELATIONS = {"required_for", "precedes"}
NUMERIC = {"schedule_delta_days", "cost_delta_brl", "buffer_days", "delay_cost_per_day_brl"}
BOOLEAN = {"alternative_ready", "other_constraints_unchanged", "advance_allowed", "delay_cost_model_complete"}
DIRECTIONS = {"increase", "decrease", "none", "unknown"}
STATUSES = {"supported", "no_impact", "undetermined"}
ACTIONS = {"request_information", "resolve_conflict", "review_schedule", "review_budget", "update_status", "record_evidence"}


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("A magnitude deve ser numérica e não booleana.")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Magnitude inválida.") from exc
    if not result.is_finite():
        raise ValueError("A magnitude deve ser finita.")
    return result


@dataclass(frozen=True)
class Fact:
    id: str
    subject: str
    predicate: str
    value: object
    source_id: str
    quote: str


@dataclass(frozen=True)
class Question:
    target: str
    dimension: str

    def __post_init__(self):
        if self.dimension not in {"schedule", "cost"}:
            raise ValueError("Dimensão inválida; use schedule ou cost.")


@dataclass(frozen=True)
class Context:
    node_ids: frozenset[str]
    sources: dict[str, str]
    facts: tuple[Fact, ...]

    def __post_init__(self):
        if len({f.id for f in self.facts}) != len(self.facts):
            raise ValueError("IDs de evidência duplicados.")
        for f in self.facts:
            if not f.id or f.subject not in self.node_ids:
                raise ValueError("Evidência sem ID ou com entidade desconhecida.")
            if not f.quote or f.source_id not in self.sources or f.quote not in self.sources[f.source_id]:
                raise ValueError("Evidência sem trecho verificável na fonte registrada.")
            if f.predicate in NUMERIC:
                n = number(f.value)
                if f.predicate in {"buffer_days", "delay_cost_per_day_brl"} and n < 0:
                    raise ValueError("Folga e diária de custo não podem ser negativas.")
            elif f.predicate in BOOLEAN:
                if type(f.value) is not bool:
                    raise ValueError("Condição deve ser booleana.")
            elif f.predicate in RELATIONS:
                if not isinstance(f.value, str) or f.value not in self.node_ids:
                    raise ValueError("Destino de relação desconhecido.")
            elif f.predicate in {"schedule_direction", "cost_direction"}:
                if f.value not in {"increase", "decrease", "none"}:
                    raise ValueError("Direção factual inválida.")
            elif f.predicate == "schedule_model":
                if f.value != "finish_to_start_with_buffer":
                    raise ValueError("Modelo temporal não suportado nesta versão.")
            else:
                raise ValueError("Predicado não reconhecido: " + f.predicate)

    def visible(self, condition):
        if condition not in {"baseline", "hybrid"}:
            raise ValueError("Condição desconhecida.")
        facts = tuple(f for f in self.facts if condition == "hybrid" or f.source_id != "graph")
        used = {f.source_id for f in facts} | ({"event"} if "event" in self.sources else set())
        return Context(self.node_ids, {k: v for k, v in self.sources.items() if k in used}, facts)

    def cited(self, ids):
        wanted = set(ids)
        if not wanted <= {f.id for f in self.facts}:
            raise ValueError("Citação de evidência inexistente ou não disponível.")
        return Context(self.node_ids, self.sources, tuple(f for f in self.facts if f.id in wanted))


def graph_facts(raw):
    """Adapta as arestas existentes sem inventar ou modificar relações."""
    lines = [json.dumps(e, ensure_ascii=False, sort_keys=True) for e in raw["edges"]]
    facts = tuple(Fact(f"graph:{i}", e["source"], e["type"], e["target"], "graph", line)
                  for i, (e, line) in enumerate(zip(raw["edges"], lines)))
    return "\n".join(lines), facts


@dataclass(frozen=True)
class Decision:
    target: str
    dimension: str
    status: str
    direction: str
    delta: Decimal | None
    evidence_ids: tuple[str, ...]
    missing_information: tuple[str, ...]
    reason: str

    @property
    def unit(self):
        return "days" if self.dimension == "schedule" else "BRL"

    @property
    def actions(self):
        if self.status == "undetermined":
            return ("resolve_conflict",) if any(x.startswith("conflict:") for x in self.missing_information) else ("request_information",)
        if self.status == "no_impact":
            return ("record_evidence",)
        return ("review_schedule" if self.dimension == "schedule" else "review_budget", "update_status")

    def to_dict(self):
        return {"target": self.target, "dimension": self.dimension, "status": self.status,
                "direction": self.direction, "delta": str(self.delta) if self.delta is not None else None,
                "unit": self.unit, "evidence_ids": list(self.evidence_ids),
                "missing_information": list(self.missing_information), "reason": self.reason,
                "recommended_actions": list(self.actions)}


def _direction(delta):
    return "increase" if delta > 0 else "decrease" if delta < 0 else "none"


def _unknown(q, missing, evidence=(), reason="Informação insuficiente para concluir nesta entidade e dimensão."):
    return Decision(q.target, q.dimension, "undetermined", "unknown", None,
                    tuple(sorted(set(evidence))), tuple(sorted(set(missing))), reason)


def _known(q, delta, evidence, reason, direction=None):
    direction = direction or _direction(delta)
    return Decision(q.target, q.dimension, "no_impact" if direction == "none" else "supported",
                    direction, delta, tuple(sorted(set(evidence))), (), reason)


class EvidenceEngine:
    """Uma interface de consulta: assess(Question) -> Decision com certificado."""
    def __init__(self, context):
        self.context = context

    def _read(self, subject, predicate):
        facts = [f for f in self.context.facts if f.subject == subject and f.predicate == predicate]
        if not facts:
            return None, (), False
        values = [number(f.value) if predicate in NUMERIC else f.value for f in facts]
        return values[0], tuple(f.id for f in facts), any(v != values[0] for v in values)

    def _direct(self, q):
        numeric = "schedule_delta_days" if q.dimension == "schedule" else "cost_delta_brl"
        qualitative = "schedule_direction" if q.dimension == "schedule" else "cost_direction"
        value, ids, conflict = self._read(q.target, numeric)
        direction, dids, dconflict = self._read(q.target, qualitative)
        if conflict or dconflict or (value is not None and direction is not None and _direction(value) != direction):
            return _unknown(q, [f"conflict:{q.target}:{q.dimension}"], ids + dids, "As fontes disponíveis se contradizem.")
        if value is not None:
            return _known(q, value, ids, "Variação líquida explicitamente informada para o escopo consultado.")
        if direction is not None:
            return _known(q, Decimal(0) if direction == "none" else None, dids,
                          "A direção foi informada; a magnitude pode não estar disponível.", direction)
        return None

    def _has_signal(self, target, seen=frozenset()):
        if target in seen:
            return False
        if any(f.subject == target and f.predicate in {"schedule_delta_days", "schedule_direction"} for f in self.context.facts):
            return True
        return any(self._has_signal(f.subject, seen | {target}) for f in self.context.facts
                   if f.predicate in TEMPORAL_RELATIONS and f.value == target)

    def assess(self, question):
        if question.target not in self.context.node_ids:
            raise ValueError("Entidade consultada desconhecida.")
        return self._schedule(question, frozenset()) if question.dimension == "schedule" else self._cost(question)

    def _schedule(self, q, visited):
        direct = self._direct(q)
        if direct is not None:
            return direct
        if q.target in visited:
            return _unknown(q, [f"acyclic_schedule:{q.target}"], reason="Ciclo temporal sem modelo de cálculo definido.")
        incoming = [f for f in self.context.facts if f.predicate in TEMPORAL_RELATIONS and f.value == q.target
                    and self._has_signal(f.subject)]
        if not incoming:
            return _unknown(q, [f"schedule_effect:{q.target}"], reason="Sem efeito direto ou dependência temporal sustentada pelo contexto disponível.")
        params = {}
        evidence = []
        missing = []
        for predicate in ["schedule_model", "other_constraints_unchanged", "alternative_ready"]:
            value, ids, conflict = self._read(q.target, predicate)
            evidence.extend(ids)
            if conflict:
                missing.append(f"conflict:{q.target}:{predicate}")
            elif value is None or (predicate == "other_constraints_unchanged" and value is not True):
                missing.append(f"{predicate}:{q.target}")
            params[predicate] = value
        evidence.extend(f.id for f in incoming)
        # O certificado precisa incluir o sinal de origem, mesmo se uma
        # alternativa neutraliza seu efeito na entidade de destino.
        for edge in incoming:
            evidence.extend(self._schedule(Question(edge.subject, "schedule"), visited | {q.target}).evidence_ids)
        if missing:
            return _unknown(q, missing, evidence)
        if params["alternative_ready"] is True:
            return _known(q, Decimal(0), evidence, "Alternativa pronta e suficiente; demais condições permanecem inalteradas no modelo declarado.")
        buffer, bids, conflict = self._read(q.target, "buffer_days")
        evidence.extend(bids)
        if conflict or buffer is None:
            return _unknown(q, [f"conflict:{q.target}:buffer_days" if conflict else f"buffer_days:{q.target}"], evidence)
        results = []
        for edge in incoming:
            upstream = self._schedule(Question(edge.subject, "schedule"), visited | {q.target})
            evidence.extend(upstream.evidence_ids)
            if upstream.status == "undetermined":
                missing.extend(upstream.missing_information)
                continue
            if upstream.direction == "decrease":
                allowed, aids, conflict = self._read(q.target, "advance_allowed")
                evidence.extend(aids)
                if conflict or allowed is None or (allowed and buffer != 0):
                    missing.append(f"advance_model:{q.target}")
                    continue
                results.append(upstream.delta if allowed else Decimal(0))
            elif upstream.delta is None:
                # Sem magnitude não sabemos se a folga absorve o atraso.
                if buffer == 0 and upstream.direction == "increase":
                    results.append(None)
                else:
                    missing.append(f"schedule_magnitude:{edge.subject}")
            else:
                results.append(max(Decimal(0), upstream.delta - buffer))
        if missing:
            return _unknown(q, missing, evidence)
        # Sem datas-base/folgas por predecessor, nem o máximo nem a soma dos
        # deslocamentos resolve corretamente uma convergência de mudanças.
        if len(results) > 1:
            return _unknown(q, [f"multi_predecessor_schedule:{q.target}"], evidence)
        if any(v is None for v in results):
            return _known(q, None, evidence, "Atraso sustentado, mas sua magnitude não foi informada.", "increase")
        return _known(q, max(results), evidence, "Modelo explícito de término-início; a folga absorve parte ou todo o atraso.")

    def _cost(self, q):
        direct = self._direct(q)
        if direct is not None:
            return direct
        rate, ids, conflict = self._read(q.target, "delay_cost_per_day_brl")
        complete, cids, cconflict = self._read(q.target, "delay_cost_model_complete")
        if conflict or cconflict:
            return _unknown(q, [f"conflict:{q.target}:cost_model"], ids + cids)
        missing = []
        if rate is None:
            missing.append(f"delay_cost_per_day_brl:{q.target}")
        if complete is not True:
            missing.append(f"delay_cost_model_complete:{q.target}")
        if missing:
            return _unknown(q, missing, ids + cids, "Um atraso não implica aumento de custo sem um modelo financeiro explícito.")
        if rate == 0:
            return _known(q, Decimal(0), ids + cids, "Modelo líquido de custo completo com diária zero; não depende de conhecer o prazo.")
        schedule = self._schedule(Question(q.target, "schedule"), frozenset())
        evidence = ids + cids + schedule.evidence_ids
        if schedule.status == "undetermined":
            return _unknown(q, schedule.missing_information, evidence)
        if rate == 0 or schedule.direction in {"none", "decrease"}:
            return _known(q, Decimal(0), evidence, "O modelo financeiro declarado contém apenas custos de atraso, sem outras variações líquidas.")
        return _known(q, schedule.delta * rate if schedule.delta is not None else None, evidence,
                      "Custo líquido derivado de diária contratual explícita e atraso sustentado.", "increase")


# Mesmo contrato de instrução para ambas as condições; só o contexto difere.
ASSESSMENT_CONTRACT = """Avalie separadamente cada pergunta de prazo e custo. Use somente as evidências
fornecidas e as regras declaradas do protocolo. Não invente datas, folgas, preços,
relações ou alternativas. Diferencie impacto sustentado, ausência sustentada e
informação insuficiente/contraditória. Cite IDs de evidência disponíveis. Não use
confiança subjetiva como prova. A magnitude pode ser null quando a direção é
sustentada mas o valor não é conhecido. Providências são recomendações para
revisão humana. Responda um objeto JSON com assessments, uma entrada por pergunta,
contendo target, dimension, status, direction, delta, unit, evidence_ids,
missing_information, reason e recommended_actions. Status: supported, no_impact,
undetermined. Direção: increase, decrease, none, unknown. Unidades: days, BRL.
delta deve ser string decimal com ponto, sem unidade (ex.: "7", "-2", "1400.50"),
ou null. Ações: request_information, resolve_conflict, review_schedule, review_budget,
update_status, record_evidence. Não afirme atraso do projeto a partir apenas do
atraso de um componente. Não infira custo a partir apenas de prazo."""


RULES = """Uma variação líquida schedule_delta_days/cost_delta_brl explícita sustenta
somente a entidade indicada; sinal positivo significa atraso/aumento, negativo
adiantamento/redução, zero ausência sustentada. Uma direction explícita pode
sustentar o sentido sem magnitude. Valores contraditórios exigem esclarecimento.
Prazo pode atravessar required_for/precedes somente com schedule_model igual a
finish_to_start_with_buffer, other_constraints_unchanged verdadeiro,
alternative_ready conhecido e buffer_days conhecido. Alternativa pronta e
suficiente absorve o efeito; sem alternativa, atraso resultante=max(0, atraso
anterior-folga). Adiantamento exige advance_allowed explícito e folga zero;
casos mais complexos exigem outro modelo. Ausência de relação ou parâmetros não
prova ausência de impacto. supplies, validated_by e belongs_to não propagam
prazo/custo nesta versão. Custo indireto só é calculável com diária explícita
não negativa e delay_cost_model_complete verdadeiro, indicando que o custo
líquido varia somente pela diária de atraso; adiantamento não gera economia
automática. Aumento/redução sem quantia conhecida admite delta null. Para
indeterminado, pedir informação (ou resolver conflito). Para ausência sustentada,
registrar evidência. Para impacto sustentado, recomendar revisão de prazo ou
orçamento e atualização de status. Não aprovar decisões nem executar ações."""


MISSING_INFORMATION_FORMAT = {
    "syntax": "Use os códigos canônicos abaixo, substituindo ENTITY pelo ID da entidade. Pode listar mais de uma lacuna relevante.",
    "schedule_effect:ENTITY": "Falta variação direta ou relação temporal sustentada para a entidade.",
    "schedule_model:ENTITY": "Falta o modelo finish_to_start_with_buffer.",
    "other_constraints_unchanged:ENTITY": "Falta confirmação de que as demais restrições continuam inalteradas.",
    "alternative_ready:ENTITY": "Falta saber se há alternativa pronta e suficiente.",
    "buffer_days:ENTITY": "Falta folga temporal aplicável à dependência analisada.",
    "schedule_magnitude:ENTITY": "Falta magnitude de atraso na entidade de origem.",
    "advance_model:ENTITY": "Faltam condições explícitas para antecipação.",
    "multi_predecessor_schedule:ENTITY": "Convergência de mudanças requer cronograma e folgas por predecessor.",
    "acyclic_schedule:ENTITY": "Ciclo sem modelo temporal definido.",
    "delay_cost_per_day_brl:ENTITY": "Falta diária de custo de atraso.",
    "delay_cost_model_complete:ENTITY": "Falta confirmação de que a diária captura toda variação líquida de custo.",
    "conflict:ENTITY:FIELD": "Fontes divergem para schedule, cost, cost_model ou um parâmetro de contexto.",
}


def build_request(case_id, context, questions, condition):
    visible = context.visible(condition)
    if not questions or len(set(questions)) != len(questions) or any(q.target not in context.node_ids for q in questions):
        raise ValueError("Perguntas vazias, duplicadas ou com entidade desconhecida.")
    return {"contract": ASSESSMENT_CONTRACT, "rules": RULES, "input": {
        "case_id": case_id, "questions": [vars(q) for q in questions],
        "node_ids": sorted(visible.node_ids), "sources": visible.sources,
        "missing_information_format": MISSING_INFORMATION_FORMAT,
        "facts": [vars(f) for f in visible.facts]}}


def _parse_prediction(payload, questions):
    if not questions:
        raise ValueError("É necessária pelo menos uma pergunta.")
    if not isinstance(payload, dict) or set(payload) != {"assessments"} or not isinstance(payload["assessments"], list):
        raise ValueError("Use um objeto com a lista assessments.")
    expected = {(q.target, q.dimension) for q in questions}
    if len(expected) != len(questions):
        raise ValueError("Perguntas duplicadas.")
    parsed = {}
    fields = {"target", "dimension", "status", "direction", "delta", "unit", "evidence_ids", "missing_information", "reason", "recommended_actions"}
    for item in payload["assessments"]:
        if not isinstance(item, dict) or set(item) != fields:
            raise ValueError("Campos de avaliação incorretos.")
        if not isinstance(item["target"], str) or not isinstance(item["dimension"], str):
            raise ValueError("Entidade e dimensão devem ser textuais.")
        key = (item["target"], item["dimension"])
        if key not in expected or key in parsed:
            raise ValueError("Pergunta ausente, desconhecida ou duplicada.")
        if not isinstance(item["status"], str) or not isinstance(item["direction"], str) or item["status"] not in STATUSES or item["direction"] not in DIRECTIONS:
            raise ValueError("Estado ou direção inválidos.")
        for field in ["evidence_ids", "missing_information", "recommended_actions"]:
            if not isinstance(item[field], list) or any(not isinstance(v, str) or not v for v in item[field]) or len(set(item[field])) != len(item[field]):
                raise ValueError("Listas de evidência, lacunas e ações inválidas.")
        if not set(item["recommended_actions"]) <= ACTIONS:
            raise ValueError("Providência desconhecida.")
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            raise ValueError("Justificativa ausente.")
        delta = number(item["delta"]) if item["delta"] is not None else None
        unit = "days" if item["dimension"] == "schedule" else "BRL"
        if item["unit"] != unit:
            raise ValueError("Unidade incompatível com a dimensão.")
        state, direction = item["status"], item["direction"]
        if state == "undetermined" and (direction != "unknown" or delta is not None or not item["missing_information"]):
            raise ValueError("Indeterminado exige direção unknown, magnitude null e lacunas.")
        if state == "no_impact" and (direction != "none" or delta != 0):
            raise ValueError("Ausência sustentada exige magnitude zero.")
        if state == "supported" and (direction not in {"increase", "decrease"} or (delta is not None and _direction(delta) != direction)):
            raise ValueError("Magnitude e direção do impacto são incompatíveis.")
        parsed[key] = Decision(*key, state, direction, delta, tuple(item["evidence_ids"]),
                               tuple(item["missing_information"]), item["reason"])
    if set(parsed) != expected:
        raise ValueError("É obrigatório responder todas as perguntas.")
    return parsed


def evaluate_prediction(payload, context, questions, references):
    """Compara com referências autorais e audita provas usando só o contexto visível.

    references NÃO deve ser enviado ao modelo. Ausência/duplicação de questões e
    referências falha fechada. Não há juiz LLM nem média que esconda alucinações.
    """
    parsed = _parse_prediction(payload, questions)
    expected_keys = {(q.target, q.dimension) for q in questions}
    if len(references) != len(expected_keys) or {(r.target, r.dimension) for r in references} != expected_keys:
        raise ValueError("Referências incompletas ou duplicadas.")
    reference_map = {(r.target, r.dimension): r for r in references}
    rows = []
    for q in questions:
        key = (q.target, q.dimension)
        claim, reference = parsed[key], reference_map[key]
        available = EvidenceEngine(context).assess(q)
        visible_ids = {f.id for f in context.facts}
        citations_visible = set(claim.evidence_ids) <= visible_ids
        proof = EvidenceEngine(context.cited(claim.evidence_ids)).assess(q) if citations_visible else None
        assertions = claim.status != "undetermined"
        grounded = citations_visible and (not assertions or (
            proof.status == claim.status and proof.direction == claim.direction and
            (claim.delta is None or proof.delta == claim.delta)))
        if assertions:
            grounded = grounded and available.status == claim.status and available.direction == claim.direction and (claim.delta is None or available.delta == claim.delta)
        missing_correct = claim.status != "undetermined" or set(available.missing_information) <= set(claim.missing_information)
        ref_correct = (claim.status, claim.direction, claim.delta) == (reference.status, reference.direction, reference.delta)
        row = {"target": q.target, "dimension": q.dimension, "reference_correct": ref_correct,
               "expected_status": reference.status, "predicted_status": claim.status,
               "conclusion_correct": (claim.status, claim.direction) == (reference.status, reference.direction),
               "magnitude_correct": claim.delta == reference.delta,
               "unjustified_precision": claim.delta is not None and (available.delta is None or claim.delta != available.delta),
               "expected_delta": str(reference.delta) if reference.delta is not None else None,
               "citations_visible": citations_visible, "evidence_supported": grounded,
               "missing_information_complete": missing_correct,
               "actions_compatible": set(payload["assessments"][list(parsed).index(key)]["recommended_actions"]) == set(available.actions),
               "actions_consistent_with_claim": set(payload["assessments"][list(parsed).index(key)]["recommended_actions"]) == set(claim.actions),
               "unsupported_assertion": assertions and not grounded,
               "appropriate_uncertainty": claim.status == "undetermined" and available.status == "undetermined" and missing_correct,
               "reference_rule_agreement": (available.status, available.direction, available.delta) == (reference.status, reference.direction, reference.delta)}
        row["passed"] = all(row[k] for k in ["reference_correct", "citations_visible", "evidence_supported", "missing_information_complete", "actions_compatible", "reference_rule_agreement"])
        rows.append(row)
    return {"n_questions": len(rows), "passed": all(r["passed"] for r in rows),
            "unsupported_assertions": sum(r["unsupported_assertion"] for r in rows), "rows": rows}


@dataclass(frozen=True)
class Reference:
    target: str
    dimension: str
    status: str
    direction: str
    delta: Decimal | None

    def __post_init__(self):
        Question(self.target, self.dimension)
        if self.status not in STATUSES or self.direction not in DIRECTIONS:
            raise ValueError("Referência com estado inválido.")
        if self.status == "undetermined" and (self.direction != "unknown" or self.delta is not None):
            raise ValueError("Referência indeterminada incompatível.")
        if self.status == "no_impact" and (self.direction != "none" or self.delta != 0):
            raise ValueError("Referência de ausência exige zero.")
        if self.status == "supported" and (self.direction not in {"increase", "decrease"} or
                                            (self.delta is not None and _direction(self.delta) != self.direction)):
            raise ValueError("Referência de impacto incompatível.")


def load_case(raw_case, raw_graph):
    """Carrega fatos anotados e referências independentes das inferências do motor."""
    sources = dict(raw_case["sources"])
    if "graph" in sources:
        raise ValueError("A fonte graph é reservada ao adaptador do grafo.")
    source, edges = graph_facts(raw_graph)
    sources["graph"] = source
    context = Context(frozenset(n["id"] for n in raw_graph["nodes"]), sources,
                      tuple(Fact(**f) for f in raw_case["facts"]) + edges)
    questions = tuple(Question(**q) for q in raw_case["questions"])
    if not questions or len(set(questions)) != len(questions) or any(q.target not in context.node_ids for q in questions):
        raise ValueError("Perguntas vazias, duplicadas ou com entidade desconhecida.")
    references = {}
    if set(raw_case["references_by_condition"]) != {"baseline", "hybrid"}:
        raise ValueError("É necessário registrar referências para as duas condições.")
    for condition, rows in raw_case["references_by_condition"].items():
        references[condition] = tuple(Reference(r["target"], r["dimension"], r["status"], r["direction"],
                                               number(r["delta"]) if r["delta"] is not None else None) for r in rows)
        keys = [(r.target, r.dimension) for r in references[condition]]
        if len(set(keys)) != len(keys) or set(keys) != {(q.target, q.dimension) for q in questions}:
            raise ValueError("Referências incompletas ou duplicadas.")
    return context, questions, references


RESPONSE_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["assessments"],
    "properties": {"assessments": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["target", "dimension", "status", "direction", "delta", "unit", "evidence_ids",
                     "missing_information", "reason", "recommended_actions"],
        "properties": {
            "target": {"type": "string"}, "dimension": {"type": "string", "enum": ["schedule", "cost"]},
            "status": {"type": "string", "enum": sorted(STATUSES)},
            "direction": {"type": "string", "enum": sorted(DIRECTIONS)},
            "delta": {"type": ["string", "null"]}, "unit": {"type": "string", "enum": ["days", "BRL"]},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
            "missing_information": {"type": "array", "items": {"type": "string"}},
            "reason": {"type": "string"},
            "recommended_actions": {"type": "array", "items": {"type": "string", "enum": sorted(ACTIONS)}},
        }
    }}}
}


def call_model(client, model, case_id, context, questions, condition):
    """Mesmo cliente, modelo, prompt e contrato; somente o contexto varia.

    A função recebe o cliente, permitindo testes com cliente simulado. Não inclui
    referências nem sugestões produzidas pelo motor na entrada do LLM.
    """
    request = build_request(case_id, context, questions, condition)
    response = client.responses.create(
        model=model,
        input=[{"role": "system", "content": request["contract"] + "\n\n" + request["rules"]},
               {"role": "user", "content": json.dumps(request["input"], ensure_ascii=False)}],
        text={"format": {"type": "json_schema", "name": "impact_assessments_v2",
                         "schema": RESPONSE_SCHEMA, "strict": True}},
    )
    record = {"case_id": case_id, "condition": condition, "raw_output": response.output_text,
              "response_id": getattr(response, "id", None), "model": getattr(response, "model", model),
              "prediction": None, "error": None}
    usage = getattr(response, "usage", None)
    record["usage"] = usage.model_dump() if hasattr(usage, "model_dump") else None
    try:
        record["prediction"] = json.loads(record["raw_output"])
        _parse_prediction(record["prediction"], questions)
    except (ValueError, TypeError) as exc:
        record["error"] = type(exc).__name__ + ": " + str(exc)
    return record
