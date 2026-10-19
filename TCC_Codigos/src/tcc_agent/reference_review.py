"""Auditoria offline das referências autorais, sem gerar ou ajustar suas respostas."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json

CRITERIA = {
    'version': '2.1-draft',
    'statuses': {
        'supported': 'A evidência sustenta a direção da variação no escopo e medida consultados; magnitude pode ser desconhecida.',
        'no_impact': 'Há evidência explícita ou cálculo completo de variação zero nesse escopo e medida.',
        'undetermined': 'Faltam dados ou há conflito; não substituir por zero.',
    },
    'scope': 'Responder separadamente cada entidade, atividade e medida. Início, duração, progresso, entrega e término são diferentes.',
    'time': 'Datas absolutas e prazos de compromisso não estabelecem desvio sem base comparável. Risco não é efeito confirmado. Não converter dias não qualificados em úteis ou corridos.',
    'cost': 'Somente variação líquida no escopo, na moeda solicitada. Atraso, qualidade, maior capacidade e embalagem diferente não estabelecem variação de custo.',
    'propagation': 'Arestas indicam relações estruturais; exigem mecanismo causal e dados temporais/financeiros aplicáveis. Não propagar a mesma quantidade indiscriminadamente nem tratar ausência de caminho como ausência de impacto.',
    'evidence': 'Citar os trechos disponíveis e declarar condições e lacunas. Relato de fonte é tratado condicionalmente, sem certificação externa. Não importar outros cenários.',
    'actions': 'Recomendar revisão de cronograma/orçamento quando sustentada; registrar ausência sustentada; solicitar dados ou resolver conflito quando indeterminado. Não executar alterações.',
}


def audit_reference_set(bundle, data_dir):
    """Falha em fonte alterada ou anotação incoerente; retorna cobertura, não acurácia."""
    for filename, expected in bundle['source_hashes'].items():
        if filename not in {'scenarios_ground_truth.json', 'project_graph.json'}:
            raise ValueError('Fonte não permitida.')
        if hashlib.sha256((data_dir / filename).read_bytes()).hexdigest() != expected:
            raise ValueError('Fonte alterada: ' + filename)
    originals = json.loads((data_dir / 'scenarios_ground_truth.json').read_text())
    graph = json.loads((data_dir / 'project_graph.json').read_text())
    nodes = {n['id'] for n in graph['nodes']}
    source_by_id = {s['scenario_id']: s for s in originals}
    cases = bundle['cases']
    if len(cases) != len(source_by_id) or {c['case_id'] for c in cases} != set(source_by_id):
        raise ValueError('Cobertura de cenários incompleta ou duplicada.')
    question_ids = set()
    counts = Counter()
    issues = []
    for case in cases:
        sid = case['case_id']
        original = source_by_id[sid]
        if case['sources'] != {'event': original['source_text']} or case['occurred_at'] != original['occurred_at']:
            raise ValueError('Texto/data do evento alterados: ' + sid)
        evidence_ids = set()
        for e in case['evidence']:
            if e['id'] in evidence_ids or not e['quote'] or e['quote'] not in case['sources'].get(e['source_id'], ''):
                raise ValueError('Citação inválida: ' + sid)
            evidence_ids.add(e['id'])
        coverage = set()
        for q in case['questions']:
            qid = q['question_id']
            key = (q['scope'], q['dimension'])
            if qid in question_ids or key in coverage or q['target'] not in nodes or not q['scope_description']:
                raise ValueError('Pergunta duplicada ou escopo inválido: ' + qid)
            if q['scope'] not in {'local', 'project'} or q['dimension'] not in {'schedule', 'cost'}:
                raise ValueError('Escopo ou dimensão inválidos: ' + qid)
            allowed = {'start', 'finish', 'duration', 'delivery', 'availability', 'progress_variance'} if q['dimension'] == 'schedule' else {'net_cost'}
            if q['measure'] not in allowed or q['unit'] != ('days' if q['dimension'] == 'schedule' else 'BRL'):
                raise ValueError('Medida/unidade inválida: ' + qid)
            if not q['evidence_ids'] or not set(q['evidence_ids']) <= evidence_ids or not q['rationale']:
                raise ValueError('Referência sem justificativa/citação: ' + qid)
            question_ids.add(qid)
            coverage.add(key)
            if set(q['reference_by_condition']) != {'baseline', 'hybrid'}:
                raise ValueError('Referências por condição incompletas: ' + qid)
            for condition, ref in q['reference_by_condition'].items():
                status, direction, delta = ref['status'], ref['direction'], ref['delta']
                if status == 'undetermined':
                    valid = direction == 'unknown' and delta is None and bool(q['missing_information'])
                elif status == 'no_impact':
                    valid = direction == 'none' and delta == '0' and not q['missing_information']
                elif status == 'supported':
                    try:
                        n = None if delta is None else Decimal(delta)
                        valid = (delta is None or isinstance(delta, str)) and direction in {'increase', 'decrease'} and not q['missing_information'] and (n is None or (n.is_finite() and (n > 0 if direction == 'increase' else n < 0)))
                    except (InvalidOperation, TypeError, ValueError):
                        valid = False
                else:
                    valid = False
                if not valid:
                    raise ValueError('Conclusão incoerente: ' + qid)
                expected_actions = ['request_information'] if status == 'undetermined' else ['record_evidence'] if status == 'no_impact' else ['review_schedule' if q['dimension'] == 'schedule' else 'review_budget', 'update_status']
                if q['recommended_actions'] != expected_actions:
                    raise ValueError('Providência incompatível: ' + qid)
                counts[f'{condition}:{q["dimension"]}:{status}'] += 1
        if not {('project', 'schedule'), ('project', 'cost')} <= coverage:
            raise ValueError('Faltam perguntas de projeto: ' + sid)
        if any(case['review'].get(k) is None for k in ['reviewer', 'reviewed_at', 'decision']) or case['review_status'] != 'independently_reviewed':
            issues.append(sid + ': aguarda revisão independente')
    return {'reference_set_id': bundle['reference_set_id'], 'cases': len(cases), 'questions_per_condition': len(question_ids),
            'counts': dict(sorted(counts.items())), 'structurally_valid': True,
            'semantic_validation': 'pending_independent_review', 'independent_benchmark': False,
            'approved_for_real_runs': False, 'review_issues': issues,
            'limitations': ['Inspeção de citações não valida semanticamente a anotação.',
                           'Todos os custos são indeterminados nestas fontes; não mede detecção de aumento, redução ou custo zero.',
                           'O conjunto já foi inspecionado no desenvolvimento; não é avaliação independente.',
                           'O avaliador V2.0 não distingue as medidas temporais V2.1; não usar adaptação automática.']}


def build_review_request(bundle, case, graph, condition):
    """Entrada revisável sem respostas, justificativas do gabarito ou impactos esperados."""
    if condition not in {'baseline', 'hybrid'}:
        raise ValueError('Condição desconhecida.')
    fields = ['question_id', 'scope', 'target', 'scope_description', 'dimension', 'measure', 'unit', 'day_basis']
    result = {'reference_set_id': bundle['reference_set_id'], 'case_id': case['case_id'], 'condition': condition,
              'criteria': CRITERIA, 'occurred_at': case['occurred_at'], 'sources': case['sources'],
              'node_catalog': [{k: n[k] for k in ('id', 'type', 'name')} for n in graph['nodes']], 'questions': [{k: q[k] for k in fields} for q in case['questions']],
              'response_contract': {'per_question': ['question_id', 'status', 'direction', 'delta', 'unit', 'evidence_quotes', 'missing_information', 'rationale', 'recommended_actions'],
                                    'delta': 'String numérica com sinal ou null; zero exige evidência; não omitir perguntas.'}}
    if condition == 'hybrid':
        result['graph_edges'] = graph['edges']
    return result
