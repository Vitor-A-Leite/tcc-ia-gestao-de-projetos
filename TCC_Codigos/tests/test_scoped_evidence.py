"""Contraprovas públicas do protocolo 2.2, sem cliente de IA ou rede."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tcc_agent.scoped_evidence import (
    Context, EvidenceEngine, Fact, Question, build_request, evaluate_prediction, load_case,
)


class ScopedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset=json.loads((ROOT/'data/evidence_protocol_v2_2_cases.json').read_text())
        cls.cases={c['case_id']:c for c in cls.dataset['cases']}

    def setup_case(self,case_id,condition='hybrid',raw=None):
        raw=copy.deepcopy(raw or self.cases[case_id])
        context,questions,refs=load_case(raw,raw.get('graph',self.dataset['graph']))
        visible=context.visible(condition)
        prediction={'assessments':[EvidenceEngine(visible).assess(q).to_dict() for q in questions]}
        return visible,questions,refs[condition],prediction

    def result(self,case_id,measure,target='H_ASSEMBLY',condition='hybrid',scope='whole_entity'):
        ctx,qs,_,_=self.setup_case(case_id,condition)
        q=next(q for q in qs if (q.target,q.measure,q.scope)==(target,measure,scope))
        return EvidenceEngine(ctx).assess(q)

    def test_all_author_references_and_proofs_in_both_contexts(self):
        n=0
        for case_id in self.cases:
            for condition in ['baseline','hybrid']:
                with self.subTest(case=case_id,condition=condition):
                    ctx,qs,refs,p=self.setup_case(case_id,condition)
                    result=evaluate_prediction(p,ctx,qs,refs)
                    self.assertTrue(result['passed'],result)
                    n+=len(qs)
        self.assertEqual(n,184)

    def test_start_delivery_progress_finish_do_not_substitute_each_other(self):
        for case_id,measure,value,target in [('SC01','start','4','H_ASSEMBLY'),('SC02','delivery','10','H_MOTOR'),('SC03','progress_variance','5','H_MOTOR'),('SC04','finish','6','H_ASSEMBLY')]:
            ctx,qs,_,_=self.setup_case(case_id)
            engine=EvidenceEngine(ctx)
            for requested in ['start','delivery','progress_variance','finish']:
                q=Question('test',target,'whole_entity','schedule',requested,'calendar_days')
                decision=engine.assess(q)
                self.assertEqual(decision.delta,Decimal(value) if requested==measure else None)
                self.assertEqual(decision.status,'supported' if requested==measure else 'undetermined')

    def test_same_entity_all_four_measures_are_distinct_questions(self):
        ctx,_,_,_=self.setup_case('SC01')
        qs=tuple(Question('Q'+str(i),'H_ASSEMBLY','whole_entity','schedule',measure,'calendar_days') for i,measure in enumerate(['start','delivery','progress_variance','finish']))
        request=build_request('probe',ctx,qs,'baseline')
        self.assertEqual(len(request['input']['questions']),4)

    def test_fixed_duration_is_required_to_transfer_start_to_finish(self):
        self.assertEqual(self.result('SC05','finish').delta,Decimal('4'))
        raw=copy.deepcopy(self.cases['SC05'])
        raw['facts']=[f for f in raw['facts'] if f['kind']!='fixed_duration']
        ctx,qs,_,_=self.setup_case('SC05',raw=raw)
        finish=next(q for q in qs if q.measure=='finish')
        self.assertEqual(EvidenceEngine(ctx).assess(finish).status,'undetermined')

    def test_changed_duration_does_not_transfer_start_to_finish(self):
        raw=copy.deepcopy(self.cases['SC05'])
        f=next(f for f in raw['facts'] if f['kind']=='fixed_duration')
        f['values']['duration_unchanged']=False
        ctx,qs,_,_=self.setup_case('SC05',raw=raw)
        self.assertEqual(EvidenceEngine(ctx).assess(next(q for q in qs if q.measure=='finish')).status,'undetermined')

    def test_start_and_finish_can_have_different_supported_deltas(self):
        self.assertEqual(self.result('SC30','start').delta,4)
        self.assertEqual(self.result('SC30','finish').delta,2)

    def test_duration_delta_is_not_finish_delta(self):
        self.assertEqual(self.result('SC28','duration').delta,2)
        self.assertEqual(self.result('SC28','finish').status,'undetermined')

    def test_direct_and_computed_conflict_cannot_be_hidden_by_citations(self):
        ctx,qs,refs,p=self.setup_case('SC31')
        claim=p['assessments'][1]
        direct=next(f for f in ctx.facts if f.measure=='finish' and f.kind=='delta')
        claim.update(status='supported',direction='increase',delta='2',evidence_ids=[direct.id],missing_information=[],recommended_actions=['review_schedule','update_status'])
        result=evaluate_prediction(p,ctx,qs,refs)
        self.assertTrue(result['rows'][1]['unsupported_assertion'])
        self.assertFalse(result['passed'])

    def test_partial_buffer_full_buffer_and_alternative(self):
        for case_id,value in [('SC08',7),('SC09',0),('SC10',0)]:
            self.assertEqual(self.result(case_id,'start').delta,value)
            self.assertEqual(self.result(case_id,'finish').delta,value)
            self.assertEqual(self.result(case_id,'start',condition='baseline').status,'undetermined')

    def test_advance_allowed_and_forbidden(self):
        self.assertEqual(self.result('SC11','finish').delta,-4)
        self.assertEqual(self.result('SC12','finish').delta,0)
        self.assertEqual(self.result('SC11','net_cost').delta,0)

    def test_cost_increase_reduction_zero_and_unknown(self):
        for case_id,value in [('SC14',250),('SC15',-200),('SC16',0)]:
            self.assertEqual(self.result(case_id,'net_cost').delta,value)
        self.assertEqual(self.result('SC18','net_cost',target='H_MOTOR').status,'undetermined')

    def test_cost_uses_the_contracted_temporal_measure(self):
        raw=copy.deepcopy(self.cases['SC20'])
        f=next(f for f in raw['facts'] if f['kind']=='delay_cost')
        f['values']['net_model_complete']=True
        f['values']['time_measure']='finish'
        ctx,qs,_,_=self.setup_case('SC20',raw=raw)
        self.assertEqual(EvidenceEngine(ctx).assess(next(q for q in qs if q.dimension=='cost')).status,'undetermined')
        f['values']['time_measure']='start'
        ctx,qs,_,_=self.setup_case('SC20',raw=raw)
        self.assertEqual(EvidenceEngine(ctx).assess(next(q for q in qs if q.dimension=='cost')).delta,800)

    def test_partial_financial_model_and_zero_complete_model(self):
        self.assertEqual(self.result('SC20','net_cost').status,'undetermined')
        self.assertEqual(self.result('SC19','net_cost').delta,0)
        self.assertEqual(self.result('SC19','finish').status,'undetermined')

    def test_exact_financial_decimal(self):
        self.assertEqual(self.result('SC33','net_cost',scope='adjustment').delta,Decimal('0.20'))

    def test_component_saving_does_not_establish_project_saving(self):
        self.assertEqual(self.result('SC21','net_cost',target='H_MOTOR',scope='purchase').delta,-100)
        self.assertEqual(self.result('SC21','net_cost',target='H_RELEASE',scope='project').status,'undetermined')

    def test_lots_are_not_interchangeable_scopes(self):
        self.assertEqual(self.result('SC22','delivery',target='H_MOTOR',scope='lot_A').delta,3)
        self.assertEqual(self.result('SC22','delivery',target='H_MOTOR',scope='lot_B').status,'undetermined')

    def test_calendar_days_and_working_days_do_not_convert(self):
        ctx,qs,_,_=self.setup_case('SC23')
        by_basis={q.day_basis:EvidenceEngine(ctx).assess(q) for q in qs}
        self.assertEqual(by_basis['working_days'].delta,5)
        self.assertEqual(by_basis['calendar_days'].status,'undetermined')

    def test_progress_cannot_be_a_dependency_endpoint(self):
        raw=copy.deepcopy(self.cases['SC08'])
        next(f for f in raw['facts'] if f['kind']=='dependency_shift')['values']['source_measure']='progress_variance'
        with self.assertRaisesRegex(ValueError,'dependência temporal'):
            self.setup_case('SC08',raw=raw)

    def test_incomplete_knowledge_not_overridden_by_connected_graph(self):
        for case_id in ['SC13','SC25','SC26']:
            self.assertEqual(self.result(case_id,'start').status,'undetermined')

    def test_other_relation_types_never_transmit_days(self):
        for relation in ['supplies','validated_by','belongs_to']:
            raw=copy.deepcopy(self.cases['SC26'])
            raw['graph']['edges'][0]['type']=relation
            ctx,qs,_,_=self.setup_case('SC26',raw=raw)
            with self.subTest(relation=relation):
                self.assertEqual(EvidenceEngine(ctx).assess(qs[0]).status,'undetermined')

    def test_dependency_does_not_convert_working_to_calendar_days(self):
        raw=copy.deepcopy(self.cases['SC08'])
        raw['facts'][0]['day_basis']='working_days'
        ctx,qs,_,_=self.setup_case('SC08',raw=raw)
        self.assertEqual(EvidenceEngine(ctx).assess(next(q for q in qs if q.measure=='start')).status,'undetermined')

    def test_chain_requires_every_link_model(self):
        self.assertEqual(self.result('SC27','finish',target='H_RELEASE').delta,5)
        self.assertEqual(self.result('SC27','net_cost',target='H_RELEASE').delta,500)
        raw=copy.deepcopy(self.cases['SC27'])
        raw['facts']=[f for f in raw['facts'] if not(f['target']=='H_ASSEMBLY' and f['kind']=='fixed_duration')]
        ctx,qs,_,_=self.setup_case('SC27',raw=raw)
        self.assertEqual(EvidenceEngine(ctx).assess(next(q for q in qs if q.target=='H_RELEASE' and q.measure=='finish')).status,'undetermined')

    def test_direction_without_magnitude_is_not_numeric_precision(self):
        r=self.result('SC29','net_cost')
        self.assertEqual((r.status,r.direction,r.delta),('supported','increase',None))
        ctx,qs,refs,p=self.setup_case('SC29')
        p['assessments'][-1]['delta']='200'
        result=evaluate_prediction(p,ctx,qs,refs)
        self.assertTrue(result['rows'][-1]['unjustified_precision'])
        self.assertTrue(result['rows'][-1]['unsupported_assertion'])

    def test_same_common_instructions_no_gold_or_graph_leak(self):
        raw=self.cases['SC08']
        ctx,qs,_=load_case(raw,self.dataset['graph'])
        a=build_request('SC08',ctx,qs,'baseline'); b=build_request('SC08',ctx,qs,'hybrid')
        self.assertEqual(a['contract'],b['contract']); self.assertEqual(a['rules'],b['rules'])
        self.assertEqual(a['input']['facts'],b['input']['facts'])
        self.assertNotIn('graph',a['input']['sources']); self.assertEqual(a['input']['edges'],[])
        self.assertNotEqual(a['input']['edges'],b['input']['edges'])
        for key in ['references_by_condition','reference_rationales','expected_status','title']:
            self.assertNotIn(key,json.dumps(a))

    def test_text_relation_visible_to_both_conditions(self):
        for condition in ['baseline','hybrid']:
            self.assertEqual(self.result('SC32','start',condition=condition).delta,7)

    def test_swapping_measure_scope_or_day_basis_is_invalid(self):
        for field,value in [('measure','finish'),('scope','other_lot'),('day_basis','working_days')]:
            ctx,qs,refs,p=self.setup_case('SC01')
            p['assessments'][0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'medida/escopo/base'):
                evaluate_prediction(p,ctx,qs,refs)

    def test_existing_but_irrelevant_citation_is_not_proof(self):
        ctx,qs,refs,p=self.setup_case('SC08')
        p['assessments'][2]['evidence_ids']=[ctx.facts[0].id]
        result=evaluate_prediction(p,ctx,qs,refs)
        self.assertTrue(result['rows'][2]['unsupported_assertion'])

    def test_missing_or_duplicate_predictions_are_rejected(self):
        for duplicate in [False,True]:
            ctx,qs,refs,p=self.setup_case('SC01')
            p['assessments'].pop()
            if duplicate:p['assessments'].append(copy.deepcopy(p['assessments'][0]))
            with self.assertRaises(ValueError):evaluate_prediction(p,ctx,qs,refs)

    def test_unjustified_abstention_is_a_missed_conclusion(self):
        ctx,qs,refs,p=self.setup_case('SC14')
        p['assessments'][0].update(status='undetermined',direction='unknown',delta=None,missing_information=['price'],recommended_actions=['request_information'])
        result=evaluate_prediction(p,ctx,qs,refs)
        self.assertFalse(result['rows'][0]['reference_correct'])
        self.assertFalse(result['rows'][0]['appropriate_uncertainty'])
        self.assertFalse(result['passed'])

    def test_manual_reference_disagreement_is_reported_not_rewritten(self):
        raw=copy.deepcopy(self.cases['SC14'])
        raw['references_by_condition']['hybrid'][0]['delta']='999'
        ctx,qs,refs,p=self.setup_case('SC14',raw=raw)
        result=evaluate_prediction(p,ctx,qs,refs)
        self.assertFalse(result['rows'][0]['reference_rule_agreement'])
        self.assertEqual(refs[0].delta,999)

    def test_risk_date_price_do_not_establish_effect(self):
        for case_id in ['SC18','SC34']:
            ctx,qs,_,_=self.setup_case(case_id)
            self.assertTrue(all(EvidenceEngine(ctx).assess(q).status=='undetermined' for q in qs))

    def test_non_finite_and_negative_rates_are_rejected(self):
        for value in ['NaN','Infinity','-1',True]:
            raw=copy.deepcopy(self.cases['SC19'])
            raw['facts'][0]['values']['rate_per_day_brl']=value
            with self.subTest(value=value),self.assertRaises(ValueError):self.setup_case('SC19',raw=raw)

    def test_tampered_quote_is_rejected(self):
        raw=copy.deepcopy(self.cases['SC01']); raw['facts'][0]['quote']='Uma fonte inexistente.'
        with self.assertRaisesRegex(ValueError,'trecho'):self.setup_case('SC01',raw=raw)

    def test_temporal_cycle_is_indeterminate_without_recursion_failure(self):
        raw=copy.deepcopy(self.cases['SC27'])
        raw['graph']={'nodes':self.dataset['graph']['nodes'],'edges':[{'source':'H_RELEASE','target':'H_RELEASE','type':'precedes'}]}
        ctx,qs,_,_=self.setup_case('SC27',raw=raw)
        result=EvidenceEngine(ctx).assess(next(q for q in qs if q.target=='H_RELEASE' and q.measure=='finish'))
        self.assertEqual(result.status,'undetermined')
        self.assertTrue(any(code.startswith('acyclic_model:') for code in result.missing_information))

    def test_unavailable_evidence_and_missing_canonical_gaps_fail(self):
        ctx,qs,refs,p=self.setup_case('SC01')
        p['assessments'][0]['evidence_ids']=['hidden:fact']
        p['assessments'][1]['missing_information']=['irrelevant']
        result=evaluate_prediction(p,ctx,qs,refs)
        self.assertFalse(result['rows'][0]['citations_visible'])
        self.assertFalse(result['rows'][1]['missing_information_complete'])
        self.assertFalse(result['passed'])

    def test_cli_external_invalid_records_stay_in_denominators(self):
        # O subprocesso é o mesmo programa público, não usa cliente/chave e bloqueia sockets.
        script=ROOT/'scripts/evaluate_evidence_protocol.py'
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); d=copy.deepcopy(self.dataset); d['cases']=[self.cases['SC01']]
            cases=tmp/'cases.json'; cases.write_text(json.dumps(d))
            records=[]
            for condition in ['baseline','hybrid']:
                _,_,_,p=self.setup_case('SC01',condition)
                records.append({'case_id':'SC01','condition':condition,'prediction':p})
            records[0]['prediction']['assessments'][0]['measure']='finish'
            predictions=tmp/'predictions.jsonl'; predictions.write_text(''.join(json.dumps(r)+'\n' for r in records))
            run=subprocess.run([sys.executable,str(script),'--cases',str(cases),'--predictions',str(predictions),'--output',str(tmp/'out')],capture_output=True,text=True)
            self.assertEqual(run.returncode,1,run.stderr)
            summary=json.loads((tmp/'out/summary.json').read_text())
            self.assertEqual(summary['n_invalid_records'],1)
            self.assertEqual(summary['conditions']['baseline']['n_expected_questions'],5)
            self.assertEqual(summary['conditions']['baseline']['n_scored_questions'],0)
            self.assertEqual(summary['conditions']['baseline']['visible_context_accuracy'],0)
            self.assertEqual(sum(g['n_expected_questions'] for g in summary['conditions']['baseline']['by_dimension_measure_status']),5)
            self.assertEqual(summary['api_calls'],0)

    def test_cli_empty_dataset_and_unknown_version_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            for kind in ['empty','unknown_version']:
                d=copy.deepcopy(self.dataset)
                if kind=='empty':d['cases']=[]
                else:d['protocol_version']='2.3-unknown'
                path=tmp/(kind+'.json'); path.write_text(json.dumps(d))
                run=subprocess.run([sys.executable,str(ROOT/'scripts/evaluate_evidence_protocol.py'),'--cases',str(path),'--output',str(tmp/kind)],capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0)
                self.assertFalse((tmp/kind).exists())
