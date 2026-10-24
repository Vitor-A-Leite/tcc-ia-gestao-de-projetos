"""Protocolo 2.2: provas por entidade, escopo, medida e base de dias.

Funções puras, sem cliente de IA. Referências autorais nunca são inferidas aqui.
O protocolo 2.0 permanece separado: seus deltas genéricos não são migrados.
"""
from dataclasses import dataclass
from decimal import Decimal
import json

from .evidence_assessment import number, STATUSES, DIRECTIONS, ACTIONS, RELATIONS

TEMPORAL_MEASURES = {'start', 'delivery', 'progress_variance', 'finish', 'duration', 'availability'}
DAY_BASES = {'calendar_days', 'working_days', 'unspecified'}


@dataclass(frozen=True)
class Question:
    question_id: str
    target: str
    scope: str
    dimension: str
    measure: str
    day_basis: str

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip() for v in vars(self).values()):
            raise ValueError('Identidade da pergunta incompleta.')
        if self.dimension == 'schedule':
            if self.measure not in TEMPORAL_MEASURES or self.day_basis not in DAY_BASES:
                raise ValueError('Medida temporal ou base de dias inválida.')
        elif self.dimension != 'cost' or self.measure != 'net_cost' or self.day_basis != 'not_applicable':
            raise ValueError('Custo exige medida net_cost e base not_applicable.')

    @property
    def unit(self):
        return 'days' if self.dimension == 'schedule' else 'BRL'

    @property
    def coordinate(self):
        return (self.target, self.scope, self.dimension, self.measure, self.day_basis)

    def for_measure(self, measure, scope=None, day_basis=None):
        return Question(self.question_id, self.target, scope or self.scope, 'schedule', measure, day_basis or self.day_basis)


@dataclass(frozen=True)
class Fact:
    id: str
    source_id: str
    quote: str
    target: str
    scope: str
    dimension: str
    measure: str
    day_basis: str
    kind: str
    values: dict

    @property
    def coordinate(self):
        return (self.target, self.scope, self.dimension, self.measure, self.day_basis)

    def validate(self):
        Question(self.id, self.target, self.scope, self.dimension, self.measure, self.day_basis)
        fields = {
            'delta': {'delta'}, 'comparison': {'baseline', 'current'}, 'direction': {'direction'},
            'fixed_duration': {'duration_unchanged', 'other_constraints_unchanged'},
            'dependency_shift': {'relation', 'source_measure', 'source_scope', 'buffer_days', 'alternative_ready', 'other_constraints_unchanged', 'advance_allowed'},
            'delay_cost': {'time_measure', 'time_scope', 'time_day_basis', 'rate_per_day_brl', 'net_model_complete'},
        }
        if self.kind not in fields or not isinstance(self.values, dict) or set(self.values) != fields[self.kind]:
            raise ValueError('Tipo ou parâmetros factuais inválidos: ' + self.id)
        v = self.values
        for key in {'delta', 'baseline', 'current', 'buffer_days', 'rate_per_day_brl'} & set(v):
            n = number(v[key])
            if key in {'buffer_days', 'rate_per_day_brl'} and n < 0:
                raise ValueError('Folga/diária negativa.')
        for key in {'duration_unchanged', 'other_constraints_unchanged', 'alternative_ready', 'advance_allowed', 'net_model_complete'} & set(v):
            if type(v[key]) is not bool:
                raise ValueError('Condições devem ser booleanas.')
        if self.kind == 'direction' and v['direction'] not in {'increase', 'decrease', 'none'}:
            raise ValueError('Direção factual inválida.')
        if self.kind == 'comparison' and self.dimension == 'schedule' and self.day_basis == 'unspecified':
            raise ValueError('Comparação de posições temporais exige base de dias declarada.')
        if self.kind == 'fixed_duration' and (self.dimension != 'schedule' or self.measure != 'finish'):
            raise ValueError('Duração fixa relaciona início e término, não progresso ou entrega.')
        if self.kind == 'dependency_shift':
            if (self.dimension != 'schedule' or self.measure != 'start' or self.day_basis == 'unspecified'
                or v['relation'] not in {'required_for', 'precedes'}
                or v['source_measure'] not in {'delivery', 'availability', 'finish'}
                or not isinstance(v['source_scope'], str) or not v['source_scope']):
                raise ValueError('Modelo de dependência temporal inválido.')
        if self.kind == 'delay_cost' and (self.dimension != 'cost'
                or v['time_measure'] not in {'start', 'delivery', 'finish', 'availability'}
                or v['time_day_basis'] not in {'calendar_days', 'working_days'}
                or not isinstance(v['time_scope'], str) or not v['time_scope']):
            raise ValueError('Modelo financeiro exige medida e base temporal explícitas.')


@dataclass(frozen=True)
class Edge:
    id: str
    source: str
    target: str
    type: str
    source_id: str
    quote: str


@dataclass(frozen=True)
class Context:
    nodes: tuple[dict, ...]
    sources: dict[str, str]
    facts: tuple[Fact, ...]
    edges: tuple[Edge, ...] = ()

    def __post_init__(self):
        nodes = {n['id'] for n in self.nodes}
        if len(nodes) != len(self.nodes):
            raise ValueError('Nós duplicados.')
        evidence = self.facts + self.edges
        if len({f.id for f in evidence}) != len(evidence):
            raise ValueError('IDs de evidência duplicados.')
        for e in evidence:
            if not e.id or not e.quote or e.quote not in self.sources.get(e.source_id, ''):
                raise ValueError('Evidência sem trecho verificável: ' + e.id)
            if isinstance(e, Fact):
                if e.target not in nodes or e.source_id == 'graph':
                    raise ValueError('Entidade factual inválida ou fonte graph reservada.')
                e.validate()
            elif e.source not in nodes or e.target not in nodes or e.type not in RELATIONS:
                raise ValueError('Relação inválida.')

    @property
    def ids(self):
        return {e.id for e in self.facts + self.edges}

    def visible(self, condition):
        if condition not in {'baseline', 'hybrid'}:
            raise ValueError('Condição inválida.')
        edges = tuple(e for e in self.edges if condition == 'hybrid' or e.source_id != 'graph')
        sources = {k: v for k, v in self.sources.items() if condition == 'hybrid' or k != 'graph'}
        return Context(self.nodes, sources, self.facts, edges)

    def cited(self, ids):
        if not set(ids) <= self.ids:
            raise ValueError('Evidência indisponível.')
        return Context(self.nodes, self.sources, tuple(f for f in self.facts if f.id in ids), tuple(e for e in self.edges if e.id in ids))


@dataclass(frozen=True)
class Decision:
    question: Question
    status: str
    direction: str
    delta: Decimal | None
    evidence_ids: tuple[str, ...]
    missing_information: tuple[str, ...]
    reason: str

    @property
    def actions(self):
        if self.status == 'undetermined':
            return ('resolve_conflict',) if any(s.startswith('conflict:') for s in self.missing_information) else ('request_information',)
        return ('record_evidence',) if self.status == 'no_impact' else ('review_schedule' if self.question.dimension == 'schedule' else 'review_budget', 'update_status')

    def to_dict(self):
        return {**vars(self.question), 'unit': self.question.unit, 'status': self.status, 'direction': self.direction,
                'delta': str(self.delta) if self.delta is not None else None, 'evidence_ids': list(self.evidence_ids),
                'missing_information': list(self.missing_information), 'reason': self.reason, 'recommended_actions': list(self.actions)}


def _unknown(q, missing, evidence=(), reason='Dados insuficientes para a medida, escopo e base consultados.'):
    return Decision(q, 'undetermined', 'unknown', None, tuple(sorted(set(evidence))), tuple(sorted(set(missing))), reason)


def _known(q, delta, evidence, reason, direction=None):
    direction = direction or ('increase' if delta > 0 else 'decrease' if delta < 0 else 'none')
    return Decision(q, 'no_impact' if direction == 'none' else 'supported', direction, delta, tuple(sorted(set(evidence))), (), reason)


class EvidenceEngine:
    def __init__(self, context):
        self.context = context

    def assess(self, q):
        if q.target not in {n['id'] for n in self.context.nodes}:
            raise ValueError('Entidade desconhecida.')
        return self._assess(q, frozenset())

    def _assess(self, q, visited):
        token = ':'.join(q.coordinate)
        if q.coordinate in visited:
            return _unknown(q, ['acyclic_model:' + token])
        facts = [f for f in self.context.facts if f.coordinate == q.coordinate]
        candidates = []
        for f in facts:
            v, ev = f.values, [f.id]
            if f.kind == 'delta':
                result = _known(q, number(v['delta']), ev, 'Variação explicitamente anotada na medida e escopo consultados.')
            elif f.kind == 'comparison':
                result = _known(q, number(v['current']) - number(v['baseline']), ev, 'Valor atual menos base comparável, na mesma medida e unidade.')
            elif f.kind == 'direction':
                result = _known(q, Decimal(0) if v['direction'] == 'none' else None, ev, 'Direção explicitamente informada.', v['direction'])
            else:
                result = self._model(q, f, visited | {q.coordinate})
            candidates.append(result)
        known = [r for r in candidates if r.status != 'undetermined']
        # Uma fonte explícita pode resolver um modelo incompleto, mas nunca apagar um conflito.
        conflicts = [r for r in candidates if any(m.startswith('conflict:') for m in r.missing_information)]
        directions = {r.direction for r in known}
        magnitudes = {r.delta for r in known if r.delta is not None}
        evidence = [e for r in candidates for e in r.evidence_ids]
        if conflicts or len(directions) > 1 or len(magnitudes) > 1:
            return _unknown(q, ['conflict:' + token], evidence, 'Fontes ou modelos disponíveis divergem nesta medida e escopo.')
        if known:
            # Se uma conclusão possui prova numérica completa, preservar esse certificado.
            return next((r for r in known if r.delta is not None), known[0])
        if candidates:
            return _unknown(q, [m for r in candidates for m in r.missing_information], evidence)
        return _unknown(q, ['evidence:' + token])

    def _model(self, q, f, visited):
        v, evidence = f.values, [f.id]
        if f.kind == 'fixed_duration':
            if not v['duration_unchanged'] or not v['other_constraints_unchanged']:
                return _unknown(q, ['fixed_duration_conditions:' + q.target], evidence)
            upstream = self._assess(q.for_measure('start'), visited)
        elif f.kind == 'delay_cost':
            if not v['net_model_complete']:
                return _unknown(q, ['net_cost_model_complete:' + q.target], evidence)
            rate = number(v['rate_per_day_brl'])
            if rate == 0:
                return _known(q, Decimal(0), evidence, 'Modelo líquido completo com diária zero.')
            upstream = self._assess(q.for_measure(v['time_measure'], v['time_scope'], v['time_day_basis']), visited)
        elif f.kind == 'dependency_shift':
            if not v['other_constraints_unchanged']:
                return _unknown(q, ['other_constraints_unchanged:' + q.target], evidence)
            edges = [e for e in self.context.edges if e.target == q.target and e.type == v['relation']]
            if not edges:
                return _unknown(q, ['dependency:' + q.target + ':' + v['relation']], evidence)
            evidence += [e.id for e in edges]
            # Não escolher um predecessor conveniente entre vários sem cronograma por predecessor.
            predecessors = {e.source for e in edges}
            if len(predecessors) != 1:
                return _unknown(q, ['per_predecessor_schedule:' + q.target], evidence)
            source = next(iter(predecessors))
            source_q = Question(q.question_id, source, v['source_scope'], 'schedule', v['source_measure'], q.day_basis)
            upstream = self._assess(source_q, visited)
        else:
            raise ValueError('Modelo não implementado.')
        evidence += list(upstream.evidence_ids)
        if any(m.startswith('conflict:') for m in upstream.missing_information):
            return _unknown(q, upstream.missing_information, evidence)
        if f.kind == 'dependency_shift' and v['alternative_ready']:
            return _known(q, Decimal(0), evidence, 'Alternativa pronta e suficiente no modelo explicitamente declarado.')
        if upstream.status == 'undetermined':
            return _unknown(q, upstream.missing_information, evidence)
        if f.kind == 'fixed_duration':
            return _known(q, upstream.delta, evidence, 'Deslocamento do término igual ao do início apenas com duração e outras restrições constantes.', upstream.direction)
        if f.kind == 'delay_cost':
            if upstream.direction in {'none', 'decrease'}:
                return _known(q, Decimal(0), evidence, 'Modelo líquido limitado a custo de atraso; antecipação não produz economia automática.')
            return _known(q, upstream.delta * rate if upstream.delta is not None else None, evidence, 'Diária explícita × atraso da medida contratada.', 'increase')
        buffer = number(v['buffer_days'])
        if upstream.direction == 'decrease':
            if not v['advance_allowed']:
                return _known(q, Decimal(0), evidence, 'Antecipação do destino explicitamente impedida no modelo.')
            if buffer != 0:
                return _unknown(q, ['advance_with_buffer:' + q.target], evidence)
            return _known(q, upstream.delta, evidence, 'Antecipação permitida, sem folga e sem outras restrições.', 'decrease')
        if upstream.direction == 'none':
            return _known(q, Decimal(0), evidence, 'Origem não mudou, demais restrições constantes.')
        if upstream.delta is None:
            return (_known(q, None, evidence, 'Atraso sem magnitude atravessa vínculo com folga zero.', 'increase')
                    if buffer == 0 else _unknown(q, ['magnitude:' + source], evidence))
        return _known(q, max(Decimal(0), upstream.delta - buffer), evidence, 'Vínculo temporal declarado: atraso absorvido pela folga aplicável.')


@dataclass(frozen=True)
class Reference:
    question_id: str
    status: str
    direction: str
    delta: Decimal | None

    def __post_init__(self):
        _validate_label(self.status, self.direction, self.delta)


def _validate_label(status, direction, delta):
    if status not in STATUSES or direction not in DIRECTIONS:
        raise ValueError('Estado/direção inválidos.')
    if status == 'undetermined' and (direction != 'unknown' or delta is not None):
        raise ValueError('Indeterminado não é zero.')
    if status == 'no_impact' and (direction != 'none' or delta != 0):
        raise ValueError('Ausência sustentada exige zero.')
    if status == 'supported' and (direction not in {'increase', 'decrease'} or (delta is not None and ((delta <= 0 if direction == 'increase' else delta >= 0)))):
        raise ValueError('Sinal incompatível com direção.')


def _check_questions(questions, context):
    if not questions or len({q.question_id for q in questions}) != len(questions) or len({q.coordinate for q in questions}) != len(questions):
        raise ValueError('Perguntas vazias ou duplicadas.')
    if any(q.target not in {n['id'] for n in context.nodes} for q in questions):
        raise ValueError('Entidade desconhecida.')


def load_case(raw, graph):
    sources = dict(raw['sources'])
    if 'graph' in sources:
        raise ValueError('Fonte graph reservada.')
    lines = [json.dumps(e, ensure_ascii=False, sort_keys=True) for e in graph['edges']]
    sources['graph'] = '\n'.join(lines)
    edges = tuple(Edge(f'graph:{i}', e['source'], e['target'], e['type'], 'graph', line) for i, (e, line) in enumerate(zip(graph['edges'], lines)))
    edges += tuple(Edge(**e) for e in raw.get('text_edges', []))
    context = Context(tuple({k:n[k] for k in ('id','name','type')} for n in graph['nodes']), sources, tuple(Fact(**f) for f in raw['facts']), edges)
    questions = tuple(Question(**q) for q in raw['questions'])
    _check_questions(questions, context)
    if set(raw['references_by_condition']) != {'baseline', 'hybrid'}:
        raise ValueError('Referências por condição incompletas.')
    references = {}
    for condition, rows in raw['references_by_condition'].items():
        references[condition] = tuple(Reference(r['question_id'], r['status'], r['direction'], number(r['delta']) if r['delta'] is not None else None) for r in rows)
        if len(rows) != len(questions) or {r.question_id for r in references[condition]} != {q.question_id for q in questions}:
            raise ValueError('Referências incompletas ou duplicadas.')
    return context, questions, references


CONTRACT = '''Protocolo 2.2. Responda cada pergunta com sua identidade completa, sem trocar entidade,
escopo, medida ou base de dias. Início, entrega, progresso, duração e término são distintos.
Use somente fatos e relações visíveis. Datas absolutas e compromissos não estabelecem desvio.
Risco não é mudança confirmada. Ausência de dados não é zero. Confiança não é evidência.
Relatos e fatos anotados são condicionais; não foram certificados externamente.
A saída é {"assessments": [...]}, com uma resposta por pergunta, todos os campos da pergunta
mais unit, status, direction, delta, evidence_ids, missing_information, reason e recommended_actions.
status: supported/no_impact/undetermined; direction: increase/decrease/none/unknown.
delta: string decimal ou null; units days/BRL. Positivo = atraso/aumento; negativo = adiantamento/redução.
Cite IDs de provas, incluindo modelos e arestas usados. Indeterminado exige lacunas.
Ações: request_information, resolve_conflict, review_schedule, review_budget, update_status, record_evidence.
As providências são recomendações para revisão humana, não ações executadas.'''

RULES = '''Fatos delta, comparison (current-baseline) e direction aplicam-se apenas à coordenada
(target, scope, dimension, measure, day_basis). Não converter bases de dias nem propagar progresso.
fixed_duration permite start -> finish no mesmo escopo somente com duration_unchanged e
other_constraints_unchanged verdadeiros. Nenhuma outra conversão de medida é automática.
dependency_shift é um modelo condicional, não uma aresta: exige uma relação visível required_for/precedes,
um único predecessor, sua medida de origem especificada, mesma base de dias, e outras restrições constantes.
Com alternativa pronta e suficiente: zero. Sem alternativa: max(0, atraso da origem - buffer_days).
Adiantamento exige advance_allowed e folga zero; se explicitamente proibido, zero; outros casos indeterminados.
Múltiplos predecessores requerem cronograma por predecessor. supplies, validated_by e belongs_to não transmitem
quantidades. Ausência de caminho não demonstra zero. Conflitos acessíveis impedem escolher uma única fonte.
delay_cost exige net_model_complete: toda variação líquida nesse escopo deve ser apenas diária × atraso
positivo da medida e base contratadas. Diária zero prova zero; antecipação não implica economia nesse modelo.
Preço unitário não é custo líquido. Nenhum modelo parcial prova custo total. Informações qualitativas podem
sustentar direção com delta null. Solicitar dados se indeterminado, resolver conflito se houver contradição,
registrar evidência se zero sustentado, revisar cronograma/orçamento e status se alteração sustentada.
Lacunas são códigos: evidence:TARGET:SCOPE:DIMENSION:MEASURE:BASIS; dependency:TARGET:RELATION;
fixed_duration_conditions:TARGET; net_cost_model_complete:TARGET; other_constraints_unchanged:TARGET;
per_predecessor_schedule:TARGET; advance_with_buffer:TARGET; magnitude:TARGET;
acyclic_model:TARGET:SCOPE:DIMENSION:MEASURE:BASIS; conflict:TARGET:SCOPE:DIMENSION:MEASURE:BASIS.'''


RESPONSE_SCHEMA = {
    'type':'object', 'additionalProperties':False, 'required':['assessments'],
    'properties':{'assessments':{'type':'array','items':{
        'type':'object', 'additionalProperties':False,
        'required':list(Question.__dataclass_fields__) + ['unit','status','direction','delta','evidence_ids','missing_information','reason','recommended_actions'],
        'properties':{
            'question_id':{'type':'string'},'target':{'type':'string'},'scope':{'type':'string'},
            'dimension':{'type':'string','enum':['schedule','cost']},
            'measure':{'type':'string','enum':sorted(TEMPORAL_MEASURES|{'net_cost'})},
            'day_basis':{'type':'string','enum':sorted(DAY_BASES|{'not_applicable'})},
            'unit':{'type':'string','enum':['days','BRL']},
            'status':{'type':'string','enum':sorted(STATUSES)},
            'direction':{'type':'string','enum':sorted(DIRECTIONS)},
            'delta':{'type':['string','null']},
            'evidence_ids':{'type':'array','items':{'type':'string'}},
            'missing_information':{'type':'array','items':{'type':'string'}},
            'reason':{'type':'string'},
            'recommended_actions':{'type':'array','items':{'type':'string','enum':sorted(ACTIONS)}},
        }
    }}}
}


def build_request(case_id, context, questions, condition):
    _check_questions(questions, context)
    visible = context.visible(condition)
    return {'contract': CONTRACT, 'rules': RULES, 'response_schema': RESPONSE_SCHEMA, 'input': {'case_id': case_id,
            'questions': [vars(q) for q in questions], 'node_catalog': list(visible.nodes),
            'sources': visible.sources, 'facts': [vars(f) for f in visible.facts], 'edges': [vars(e) for e in visible.edges]}}


def evaluate_prediction(payload, context, questions, references):
    _check_questions(questions, context)
    expected = {q.question_id:q for q in questions}
    if len(references) != len(questions) or {r.question_id for r in references} != set(expected):
        raise ValueError('Referências incompletas ou duplicadas.')
    if not isinstance(payload, dict) or set(payload) != {'assessments'} or not isinstance(payload['assessments'], list):
        raise ValueError('Use objeto assessments.')
    parsed = {}
    for item in payload['assessments']:
        fields = set(Question.__dataclass_fields__) | {'unit','status','direction','delta','evidence_ids','missing_information','reason','recommended_actions'}
        if not isinstance(item, dict) or set(item) != fields:
            raise ValueError('Campos inválidos.')
        q = Question(**{k:item[k] for k in Question.__dataclass_fields__})
        if q.question_id not in expected or q != expected[q.question_id] or q.question_id in parsed:
            raise ValueError('Pergunta duplicada, desconhecida ou medida/escopo/base trocados.')
        for key in ['evidence_ids','missing_information','recommended_actions']:
            values = item[key]
            if not isinstance(values,list) or any(not isinstance(v,str) or not v for v in values) or len(values)!=len(set(values)):
                raise ValueError('Lista inválida.')
        if item['unit'] != q.unit or not isinstance(item['reason'], str) or not item['reason'].strip() or not set(item['recommended_actions']) <= ACTIONS:
            raise ValueError('Unidade, justificativa ou providência inválida.')
        if item['delta'] is not None and not isinstance(item['delta'],str):
            raise ValueError('Delta deve ser string ou null.')
        delta = number(item['delta']) if item['delta'] is not None else None
        _validate_label(item['status'],item['direction'],delta)
        if item['status']=='undetermined' and not item['missing_information']:
            raise ValueError('Indeterminado exige lacunas.')
        if item['status']!='undetermined' and item['missing_information']:
            raise ValueError('Conclusão sustentada não pode ocultar lacunas essenciais.')
        parsed[q.question_id] = (Decision(q,item['status'],item['direction'],delta,tuple(item['evidence_ids']),tuple(item['missing_information']),item['reason']),item)
    if set(parsed)!=set(expected):
        raise ValueError('Todas as perguntas são obrigatórias.')
    refs = {r.question_id:r for r in references}
    rows=[]
    for qid,q in expected.items():
        claim,item=parsed[qid]; ref=refs[qid]
        available=EvidenceEngine(context).assess(q)
        citations_visible=set(claim.evidence_ids)<=context.ids
        proof=EvidenceEngine(context.cited(claim.evidence_ids)).assess(q) if citations_visible else None
        asserted=claim.status!='undetermined'
        def supports(result):
            return result.status==claim.status and result.direction==claim.direction and (claim.delta is None or result.delta==claim.delta)
        grounded=citations_visible and (not asserted or (supports(proof) and supports(available)))
        label=lambda r:(r.status,r.direction,r.delta)
        missing=not (claim.status=='undetermined') or set(available.missing_information)<=set(claim.missing_information)
        row={**vars(q),'expected_status':ref.status,'predicted_status':claim.status,
             'expected_direction':ref.direction,'predicted_direction':claim.direction,
             'conclusion_correct':(claim.status,claim.direction)==(ref.status,ref.direction),
             'magnitude_correct':claim.delta==ref.delta,'reference_correct':label(claim)==label(ref),
             'expected_delta':str(ref.delta) if ref.delta is not None else None,
             'unjustified_precision':claim.delta is not None and (available.delta is None or available.delta!=claim.delta),
             'citations_visible':citations_visible,'evidence_supported':grounded,'missing_information_complete':missing,
             'actions_compatible':set(item['recommended_actions'])==set(available.actions),
             'actions_consistent_with_claim':set(item['recommended_actions'])==set(claim.actions),
             'unsupported_assertion':asserted and not grounded,
             'appropriate_uncertainty':claim.status=='undetermined' and available.status=='undetermined' and missing,
             'reference_rule_agreement':label(available)==label(ref)}
        row['passed']=all(row[k] for k in ['reference_correct','citations_visible','evidence_supported','missing_information_complete','actions_compatible','reference_rule_agreement'])
        rows.append(row)
    return {'n_questions':len(rows),'passed':all(r['passed'] for r in rows),'unsupported_assertions':sum(r['unsupported_assertion'] for r in rows),'rows':rows}
