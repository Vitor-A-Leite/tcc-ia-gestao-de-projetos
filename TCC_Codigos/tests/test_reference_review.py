"""Contraprovas da preparação das referências; não são testes de desempenho da IA."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tcc_agent.reference_review import audit_reference_set, build_review_request


class ReferenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads((ROOT/'data/reference_sets/alfa_schedule_cost_v2_1_draft.json').read_text())
        cls.graph = json.loads((ROOT/'data/project_graph.json').read_text())
        cls.cases = {c['case_id']: c for c in cls.bundle['cases']}

    def question(self, sid, scope='local', dimension='schedule'):
        return next(q for q in self.cases[sid]['questions'] if q['scope']==scope and q['dimension']==dimension)

    def test_all_sources_and_cases_are_covered_but_not_promoted(self):
        result = audit_reference_set(self.bundle, ROOT/'data')
        self.assertEqual(result['cases'],36)
        self.assertEqual(len(result['review_issues']),36)
        self.assertFalse(result['approved_for_real_runs'])
        self.assertFalse(result['independent_benchmark'])

    def test_start_delay_is_not_a_finish_delay(self):
        for sid,delta in [('S008','4'),('S029','3')]:
            q=self.question(sid)
            self.assertEqual(q['measure'],'start')
            self.assertEqual(q['reference_by_condition']['baseline']['delta'],delta)
            self.assertEqual(self.question(sid,'project')['reference_by_condition']['hybrid']['status'],'undetermined')

    def test_risk_three_days_is_not_confirmed_duration(self):
        case=self.cases['S016']
        self.assertEqual(case['observation_kind'],'risk')
        self.assertEqual(self.question('S016')['reference_by_condition']['hybrid']['status'],'undetermined')

    def test_no_supply_change_does_not_prove_project_or_cost_zero(self):
        self.assertEqual(self.question('S035')['reference_by_condition']['baseline']['status'],'no_impact')
        for scope,dim in [('project','schedule'),('project','cost'),('local','cost')]:
            self.assertEqual(self.question('S035',scope,dim)['reference_by_condition']['hybrid']['status'],'undetermined')

    def test_no_cost_values_in_sources_does_not_mean_zero(self):
        for case in self.bundle['cases']:
            for q in case['questions']:
                if q['dimension']=='cost':
                    for ref in q['reference_by_condition'].values():
                        self.assertEqual(ref['status'],'undetermined')
                        self.assertIsNone(ref['delta'])

    def test_progress_does_not_become_delivery(self):
        q=self.question('S021')
        self.assertEqual(q['measure'],'progress_variance')
        self.assertEqual(q['reference_by_condition']['baseline']['delta'],'5')
        self.assertEqual(self.question('S021','project')['reference_by_condition']['baseline']['status'],'undetermined')

    def test_no_gold_leak_and_only_graph_differs(self):
        for case in self.bundle['cases']:
            a=build_review_request(self.bundle,case,self.graph,'baseline')
            b=build_review_request(self.bundle,case,self.graph,'hybrid')
            self.assertNotIn('graph_edges',a)
            self.assertEqual(b.pop('graph_edges'),self.graph['edges'])
            a.pop('condition'); b.pop('condition')
            self.assertEqual(a,b)
            for forbidden in ['reference_by_condition','expected_impacted_entities','ground_truth_rationale','review_status']:
                self.assertNotIn(forbidden,json.dumps(a))
            self.assertEqual(set(a['sources']),{'event'})

    def test_changed_source_hash_is_rejected(self):
        bundle=copy.deepcopy(self.bundle)
        bundle['source_hashes']['project_graph.json']='bad'
        with self.assertRaisesRegex(ValueError,'Fonte alterada'):
            audit_reference_set(bundle,ROOT/'data')

    def test_node_metadata_cannot_leak_hidden_relations(self):
        graph=copy.deepcopy(self.graph)
        graph['nodes'][0]['hidden_dependency']='T_ASSEMBLY'
        request=build_review_request(self.bundle,self.cases['S001'],graph,'baseline')
        self.assertNotIn('hidden_dependency',json.dumps(request))

    def test_modified_event_cannot_borrow_hidden_gold(self):
        bundle=copy.deepcopy(self.bundle)
        bundle['cases'][0]['sources']['event']+=' O projeto atrasará dez dias.'
        with self.assertRaisesRegex(ValueError,'Texto/data'):
            audit_reference_set(bundle,ROOT/'data')

    def test_missing_case_is_not_silently_dropped(self):
        bundle=copy.deepcopy(self.bundle)
        bundle['cases'].pop()
        with self.assertRaisesRegex(ValueError,'Cobertura'):
            audit_reference_set(bundle,ROOT/'data')

    def test_unsupported_zero_without_explanation_is_rejected(self):
        bundle=copy.deepcopy(self.bundle)
        q=bundle['cases'][0]['questions'][1]
        q['reference_by_condition']['baseline']={'status':'no_impact','direction':'none','delta':'0'}
        with self.assertRaisesRegex(ValueError,'Conclusão incoerente'):
            audit_reference_set(bundle,ROOT/'data')

    def test_wrong_action_is_rejected(self):
        bundle=copy.deepcopy(self.bundle)
        bundle['cases'][0]['questions'][1]['recommended_actions']=['review_budget']
        with self.assertRaisesRegex(ValueError,'Providência'):
            audit_reference_set(bundle,ROOT/'data')
