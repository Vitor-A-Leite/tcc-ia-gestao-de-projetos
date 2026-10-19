"""Contrato comum V2; referências autorais não são geradas pelo motor testado."""
import copy
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tcc_agent.evidence_assessment import (
    Context, Decision, EvidenceEngine, Fact, Question, Reference, build_request,
    call_model, evaluate_prediction, graph_facts, load_case, number,
)


class EvidenceAssessmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads((ROOT / 'data/project_graph.json').read_text())
        cls.cases = {r['case_id']: r for r in json.loads((ROOT / 'data/evidence_protocol_v2_examples.json').read_text())['cases']}

    def setup_case(self, case_id, condition='hybrid'):
        context, questions, references = load_case(self.cases[case_id], self.graph)
        visible = context.visible(condition)
        payload = {'assessments': [EvidenceEngine(visible).assess(q).to_dict() for q in questions]}
        return visible, questions, references[condition], payload

    def test_all_fifteen_manual_examples_match_both_visible_contexts(self):
        for case_id in self.cases:
            for condition in ['baseline', 'hybrid']:
                with self.subTest(case=case_id, condition=condition):
                    context, questions, references, payload = self.setup_case(case_id, condition)
                    evaluation = evaluate_prediction(payload, context, questions, references)
                    self.assertTrue(evaluation['passed'], evaluation)
                    self.assertEqual(evaluation['unsupported_assertions'], 0)

    def test_same_prompt_and_rules_but_no_graph_leak_in_baseline(self):
        context, questions, _ = load_case(self.cases['V2_02'], self.graph)
        baseline = build_request('V2_02', context, questions, 'baseline')
        hybrid = build_request('V2_02', context, questions, 'hybrid')
        self.assertEqual(baseline['contract'], hybrid['contract'])
        self.assertEqual(baseline['rules'], hybrid['rules'])
        self.assertEqual(baseline['input']['questions'], hybrid['input']['questions'])
        self.assertNotIn('graph', baseline['input']['sources'])
        self.assertFalse(any(f['source_id'] == 'graph' for f in baseline['input']['facts']))
        self.assertEqual(sum(f['source_id'] == 'graph' for f in hybrid['input']['facts']), 65)
        self.assertNotIn('references', baseline['input'])

    def test_graph_adapter_preserves_every_edge_and_direction(self):
        source, facts = graph_facts(self.graph)
        self.assertEqual(len(facts), 65)
        for edge, fact in zip(self.graph['edges'], facts):
            self.assertEqual((fact.subject, fact.predicate, fact.value), (edge['source'], edge['type'], edge['target']))
            self.assertIn(fact.quote, source)

    def test_motor_delay_alone_does_not_confirm_assembly_delay_or_cost(self):
        for condition in ['baseline', 'hybrid']:
            _, _, _, payload = self.setup_case('V2_01', condition)
            self.assertTrue(all(r['status'] == 'undetermined' for r in payload['assessments']))

    def test_partial_buffer_has_seven_day_effect_without_automatic_cost(self):
        _, _, _, payload = self.setup_case('V2_02')
        schedule, cost = payload['assessments']
        self.assertEqual(schedule['delta'], '7')
        self.assertEqual(schedule['recommended_actions'], ['review_schedule', 'update_status'])
        self.assertEqual(cost['status'], 'undetermined')
        self.assertEqual(cost['recommended_actions'], ['request_information'])

    def test_full_buffer_proves_no_schedule_effect(self):
        _, _, _, payload = self.setup_case('V2_03')
        schedule = payload['assessments'][0]
        self.assertEqual((schedule['status'], schedule['delta']), ('no_impact', '0'))
        self.assertEqual(schedule['recommended_actions'], ['record_evidence'])

    def test_alternative_certificate_includes_its_origin_signal(self):
        context, questions, refs, payload = self.setup_case('V2_04')
        schedule = payload['assessments'][0]
        self.assertIn('V2_04:event:0', schedule['evidence_ids'])
        self.assertTrue(evaluate_prediction(payload, context, questions, refs)['passed'])

    def test_delay_cost_requires_explicit_complete_financial_model(self):
        context, questions, _, payload = self.setup_case('V2_05')
        self.assertEqual(payload['assessments'][1]['delta'], '1400')
        without_complete = replace(context, facts=tuple(f for f in context.facts if f.predicate != 'delay_cost_model_complete'))
        self.assertEqual(EvidenceEngine(without_complete).assess(questions[1]).status, 'undetermined')

    def test_zero_delay_cost_model_does_not_require_schedule_knowledge(self):
        _, _, _, payload = self.setup_case('V2_14')
        self.assertEqual(payload['assessments'][0]['status'], 'undetermined')
        self.assertEqual(payload['assessments'][1]['status'], 'no_impact')

    def test_direct_advance_and_cost_reduction_are_distinct_dimensions(self):
        _, _, _, payload = self.setup_case('V2_06')
        self.assertEqual([r['delta'] for r in payload['assessments']], ['-2', '-500'])
        self.assertEqual([r['direction'] for r in payload['assessments']], ['decrease', 'decrease'])

    def test_conclusive_direction_can_have_unknown_magnitude(self):
        _, _, _, payload = self.setup_case('V2_07')
        self.assertEqual(payload['assessments'][0]['status'], 'supported')
        self.assertEqual(payload['assessments'][0]['direction'], 'increase')
        self.assertIsNone(payload['assessments'][0]['delta'])

    def test_cannot_invent_magnitude_for_known_direction(self):
        context, questions, refs, payload = self.setup_case('V2_07')
        payload['assessments'][0]['delta'] = '10'
        result = evaluate_prediction(payload, context, questions, refs)
        self.assertFalse(result['passed'])
        self.assertEqual(result['unsupported_assertions'], 1)

    def test_contradictions_require_resolution_not_confident_choice(self):
        _, _, _, payload = self.setup_case('V2_08')
        self.assertEqual(payload['assessments'][0]['status'], 'undetermined')
        self.assertEqual(payload['assessments'][0]['recommended_actions'], ['resolve_conflict'])

    def test_cherry_picking_one_side_of_conflict_is_rejected(self):
        context, questions, refs, payload = self.setup_case('V2_08')
        claim = Decision(questions[0].target, 'schedule', 'supported', 'increase', Decimal(10), ('V2_08:event:0',), (), 'Escolha de uma única fonte.')
        payload['assessments'][0] = claim.to_dict()
        result = evaluate_prediction(payload, context, questions, refs)
        self.assertEqual(result['unsupported_assertions'], 1)
        self.assertFalse(result['rows'][0]['actions_compatible'])

    def test_unknown_is_not_no_impact_and_false_absence_is_rejected(self):
        context, questions, refs, payload = self.setup_case('V2_01')
        payload['assessments'][0] = Decision(questions[0].target, 'schedule', 'no_impact', 'none', Decimal(0), (), (), 'Sem dados.').to_dict()
        result = evaluate_prediction(payload, context, questions, refs)
        self.assertFalse(result['passed'])
        self.assertEqual(result['unsupported_assertions'], 1)

    def test_unnecessary_abstention_is_not_rewarded(self):
        context, questions, refs, payload = self.setup_case('V2_02')
        payload['assessments'][0] = Decision(questions[0].target, 'schedule', 'undetermined', 'unknown', None, (), ('arbitrary',), 'Não sei.').to_dict()
        result = evaluate_prediction(payload, context, questions, refs)
        self.assertFalse(result['rows'][0]['reference_correct'])
        self.assertFalse(result['rows'][0]['appropriate_uncertainty'])

    def test_hidden_graph_citation_is_rejected_for_baseline(self):
        context, questions, refs, payload = self.setup_case('V2_02', 'baseline')
        payload['assessments'][0]['evidence_ids'] = ['graph:15']
        self.assertFalse(evaluate_prediction(payload, context, questions, refs)['rows'][0]['citations_visible'])

    def test_existing_evidence_id_without_sufficient_proof_is_rejected(self):
        context, questions, refs, payload = self.setup_case('V2_02')
        payload['assessments'][0]['evidence_ids'] = ['V2_02:event:0']
        self.assertEqual(evaluate_prediction(payload, context, questions, refs)['unsupported_assertions'], 1)

    def test_belongs_to_and_validation_do_not_propagate_time(self):
        for name in ['V2_10', 'V2_11']:
            _, _, _, payload = self.setup_case(name)
            self.assertEqual(payload['assessments'][0]['status'], 'undetermined')

    def test_advance_requires_explicit_permission(self):
        context, questions, _, payload = self.setup_case('V2_12')
        self.assertEqual(payload['assessments'][0]['delta'], '-2')
        context = replace(context, facts=tuple(f for f in context.facts if f.predicate != 'advance_allowed'))
        self.assertEqual(EvidenceEngine(context).assess(questions[0]).status, 'undetermined')

    def test_explicit_two_step_chain_does_not_reach_project_release(self):
        context, _, _, payload = self.setup_case('V2_13')
        self.assertEqual(payload['assessments'][0]['delta'], '5')
        self.assertEqual(EvidenceEngine(context).assess(Question('M_RELEASE','schedule')).status, 'undetermined')

    def test_incomplete_or_duplicate_assessments_are_rejected(self):
        context, questions, refs, payload = self.setup_case('V2_02')
        for claims in [[], payload['assessments'][:1], payload['assessments'] * 2]:
            with self.subTest(claims=claims), self.assertRaises(ValueError):
                evaluate_prediction({'assessments': claims}, context, questions, refs)
        with self.assertRaises(ValueError):
            evaluate_prediction(payload, context, questions, refs[:1])
        with self.assertRaises(ValueError):
            evaluate_prediction(payload, context, questions, (refs[0], refs[0]))

    def test_schema_rejects_bad_units_numbers_shapes_and_actions(self):
        context, questions, refs, original = self.setup_case('V2_02')
        invalid = [('unit', 'hours'), ('delta', True), ('delta', 'NaN'), ('delta', '-7'),
                   ('status', []), ('target', []), ('dimension', 'quality'),
                   ('recommended_actions', ['execute_purchase']), ('evidence_ids', None)]
        for key, value in invalid:
            with self.subTest(field=key):
                payload = copy.deepcopy(original);payload['assessments'][0][key] = value
                with self.assertRaises(ValueError):
                    evaluate_prediction(payload, context, questions, refs)

    def test_invalid_or_duplicate_facts_are_rejected(self):
        context, _, _, _ = self.setup_case('V2_02')
        first = context.facts[0]
        for bad in [replace(first, quote='Trecho inexistente.'), replace(first, subject='UNKNOWN'),
                    replace(first, value=True), replace(first, value='Infinity')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                replace(context, facts=(bad,))
        with self.assertRaises(ValueError):
            replace(context, facts=(first, first))

    def test_qualitative_and_numeric_contradiction_is_indeterminate(self):
        context, questions, _, _ = self.setup_case('V2_06')
        source='O prazo não se altera.'
        fact=Fact('contradiction','C_MOTOR','schedule_direction','none','extra',source)
        context=replace(context,sources={**context.sources,'extra':source},facts=context.facts+(fact,))
        self.assertEqual(EvidenceEngine(context).assess(questions[0]).status,'undetermined')

    def test_money_uses_decimal_arithmetic(self):
        self.assertEqual(number('0.10') * number('3'), Decimal('0.30'))
        for value in [True, float('nan'), 'Infinity', [], None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                number(value)

    def test_model_adapter_does_not_send_references_or_call_engine(self):
        context, questions, _, payload = self.setup_case('V2_02')
        create=Mock(return_value=SimpleNamespace(output_text=json.dumps(payload),id='offline',model='test-model',usage=None))
        client=SimpleNamespace(responses=SimpleNamespace(create=create))
        record=call_model(client,'test-model','V2_02',context,questions,'baseline')
        self.assertIsNone(record['error'])
        sent=json.loads(create.call_args.kwargs['input'][1]['content'])
        self.assertNotIn('graph',sent['sources'])
        self.assertNotIn('references',sent)
        self.assertEqual(create.call_args.kwargs['text']['format']['type'],'json_schema')

    def test_model_adapter_preserves_invalid_raw_output(self):
        context, questions, _, _=self.setup_case('V2_02')
        client=SimpleNamespace(responses=SimpleNamespace(create=Mock(return_value=SimpleNamespace(output_text='invalid JSON',id='offline'))))
        record=call_model(client,'test-model','V2_02',context,questions,'hybrid')
        self.assertEqual(record['raw_output'],'invalid JSON')
        self.assertIsNotNone(record['error'])

    def test_multiple_changed_predecessors_require_schedule_not_naive_max(self):
        context, questions, _, _ = self.setup_case('V2_02')
        quote='O redutor terá um dia de atraso.'
        fact=Fact('gear-delay','C_GEARBOX','schedule_delta_days',1,'extra',quote)
        context=replace(context,sources={**context.sources,'extra':quote},facts=context.facts+(fact,))
        result=EvidenceEngine(context).assess(questions[0])
        self.assertEqual(result.status,'undetermined')
        self.assertIn('multi_predecessor_schedule:T_ASSEMBLY',result.missing_information)

    def test_explicit_relation_in_event_can_support_baseline_without_graph(self):
        context, questions, refs, payload=self.setup_case('V2_02','baseline')
        quote='O motor é necessário para a montagem.'
        fact=Fact('event-dependency','C_MOTOR','required_for','T_ASSEMBLY','explicit',quote)
        context=replace(context,sources={**context.sources,'explicit':quote},facts=context.facts+(fact,))
        self.assertEqual(EvidenceEngine(context).assess(questions[0]).delta,Decimal(7))

    def test_same_meaning_citations_do_not_require_duplicate_sources(self):
        context, questions, refs, payload=self.setup_case('V2_06')
        f=next(f for f in context.facts if f.predicate=='schedule_delta_days')
        context=replace(context,facts=context.facts+(replace(f,id='duplicate-supported-fact'),))
        self.assertTrue(evaluate_prediction(payload,context,questions,refs)['passed'])

    def test_canonical_missing_information_is_documented_in_requests(self):
        context, questions, _=load_case(self.cases['V2_02'],self.graph)
        req=build_request('V2_02',context,questions,'baseline')
        self.assertIn('schedule_effect:ENTITY',req['input']['missing_information_format'])

    def test_empty_or_unknown_questions_cannot_be_sent_to_model(self):
        context, questions, refs, payload=self.setup_case('V2_02')
        client=SimpleNamespace(responses=SimpleNamespace(create=Mock()))
        for bad in [(), (questions[0],questions[0]), (Question('UNKNOWN','schedule'),)]:
            with self.subTest(questions=bad), self.assertRaises(ValueError):
                call_model(client,'test-model','V2_02',context,bad,'hybrid')
        client.responses.create.assert_not_called()
        with self.assertRaises(ValueError):
            evaluate_prediction({'assessments':[]},context,(),())

    def test_correct_direction_with_omitted_known_magnitude_is_not_called_hallucination(self):
        context,questions,refs,payload=self.setup_case('V2_02')
        payload['assessments'][0]['delta']=None
        row=evaluate_prediction(payload,context,questions,refs)['rows'][0]
        self.assertTrue(row['conclusion_correct'])
        self.assertFalse(row['magnitude_correct'])
        self.assertFalse(row['unjustified_precision'])
        self.assertTrue(row['evidence_supported'])
        self.assertFalse(row['passed'])
