"""Contrato V2, isolamento piloto/teste e execução offline do baseline real."""
import ast
from contextlib import redirect_stdout
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'TCC_Codigos/data'
NOTEBOOK = ROOT / 'TCC_Baseline_LLM.ipynb'


def digest(value):
    return hashlib.sha256(value).hexdigest()


class BaselineV2Tests(unittest.TestCase):
    def setUp(self):
        blocker = patch('socket.socket', side_effect=AssertionError('Rede proibida nos testes'))
        blocker.start()
        self.addCleanup(blocker.stop)
        self.nb = json.loads(NOTEBOOK.read_text())
        self.test = json.loads((DATA / 'scenarios_ground_truth.json').read_text())
        self.pilot = json.loads((DATA / 'scenarios_development_pilot.json').read_text())
        self.snapshot = json.loads((ROOT / 'TCC_Codigos/docs/baseline_v2_snapshot.json').read_text())
        self.ns = {'json': json, 're': re, 'time': time, 'hashlib': hashlib,
                   'datetime': datetime, 'timezone': timezone,
                   'entity_catalog': json.loads((DATA / 'project_graph.json').read_text())['nodes'],
                   'pd': SimpleNamespace(DataFrame=lambda rows: rows)}
        for cell in self.nb['cells']:
            if cell['cell_type'] != 'code':
                continue
            for node in ast.parse(''.join(cell['source'])).body:
                selected = isinstance(node, ast.FunctionDef) or (
                    isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {
                        'MODEL', 'ALLOWED_EVENT_TYPES', 'ALLOWED_ARTIFACTS', 'SYSTEM_PROMPT_V2', 'prompt_hash'
                    } for t in node.targets))
                if selected:
                    exec(compile(ast.Module(body=[node], type_ignores=[]), str(NOTEBOOK), 'exec'), self.ns)
        self.create = Mock()
        self.ns['client'] = SimpleNamespace(responses=SimpleNamespace(create=self.create))

    def prediction(self, scenario):
        return {'event_type': scenario['expected_event_type'],
                'primary_entity': scenario['expected_primary_entity'],
                'related_entities': scenario['expected_related_entities'],
                'impacted_entities': scenario['expected_impacted_entities'],
                'impacted_artifacts': scenario['expected_artifacts'],
                'responsible': scenario['expected_responsible'],
                'due_date': scenario['expected_due_date'],
                'effective_date': scenario['expected_effective_date'],
                'rationale': 'Resposta simulada; não é resultado científico.'}

    def test_six_development_events_are_disjoint_from_36_official_events(self):
        self.assertEqual([s['scenario_id'] for s in self.test], [f'S{i:03d}' for i in range(1, 37)])
        self.assertEqual([s['scenario_id'] for s in self.pilot], [f'DEV{i:03d}' for i in range(1, 7)])
        for key in ['scenario_id', 'source_text']:
            self.assertTrue({s[key] for s in self.test}.isdisjoint(s[key] for s in self.pilot))
        self.assertEqual({s['expected_event_type'] for s in self.pilot}, {
            'delay', 'decision', 'test_problem', 'technical_change', 'action_commitment', 'informational'})
        inputs = [{k: s[k] for k in ['scenario_id', 'occurred_at', 'source_type', 'source_text']} for s in self.test]
        self.assertEqual(digest(json.dumps(inputs, ensure_ascii=False, sort_keys=True).encode()),
                         self.snapshot['official_input_sha256'])

    def test_all_reviewed_labels_use_catalog_and_explicit_participant_roles(self):
        valid_ids = {n['id'] for n in self.ns['entity_catalog']}
        for s in self.test + self.pilot:
            with self.subTest(scenario=s['scenario_id']):
                self.assertTrue(self.ns['validate_prediction'](self.prediction(s)))
                self.assertNotIn(s['expected_primary_entity'], s['expected_related_entities'])
                self.assertTrue(set(s['expected_impacted_entities']) <= valid_ids)
                if s['expected_event_type'] == 'informational':
                    self.assertEqual(s['expected_impacted_entities'], [])
                    self.assertEqual(s['expected_artifacts'], [])
        audit = json.loads((DATA / 'ground_truth_review_baseline_v2.json').read_text())
        self.assertEqual([s['scenario_id'] for s in audit['entries']], [s['scenario_id'] for s in self.test])
        for entry, current in zip(audit['entries'], self.test):
            self.assertEqual(len(entry['reviewed_fields']), 4)
            self.assertTrue(entry['rationale'])
            for key, change in entry['changes'].items():
                self.assertEqual(change['after'], current[key])

    def test_snapshot_and_original_functions_have_not_drifted(self):
        for path, expected in self.snapshot['file_sha256'].items():
            self.assertEqual(digest((ROOT / path).read_bytes()), expected, path)
        for path, expected in self.snapshot['protected_function_ast_sha256'].items():
            nb = json.loads((ROOT / path).read_text())
            actual = {}
            for c in nb['cells']:
                if c['cell_type'] == 'code':
                    for node in ast.parse(''.join(c['source'])).body:
                        if isinstance(node, ast.FunctionDef):
                            actual[node.name] = digest(ast.dump(node, include_attributes=False).encode())
            self.assertEqual(actual, expected, path)

    def test_v2_prompt_has_general_definitions_without_scenario_answers(self):
        prompt = self.ns['SYSTEM_PROMPT_V2']
        self.assertIn('primary_entity: entidade sobre a qual o evento incide diretamente.', prompt)
        self.assertIn('outras entidades explicitamente envolvidas no evento, mas que não são o objeto principal.', prompt)
        for artifact in ['risk_register', 'status_report', 'decision_log', 'action_log']:
            self.assertIn(artifact + ':\nUse quando', prompt)
        self.assertNotRegex(prompt, r'\b(?:S|DEV)\d{3}\b|expected_')
        self.assertEqual(digest(prompt.encode()), self.snapshot['prompt_sha256'])
        self.assertEqual(self.ns['MODEL'], self.snapshot['model'])
        self.assertEqual((ROOT / 'TCC_Codigos/docs/baseline_v2_system_prompt.txt').read_text(), prompt + '\n')

    def test_ground_truth_cannot_leak_into_user_input(self):
        for s in self.test + self.pilot:
            changed = copy.deepcopy(s)
            for key in changed:
                if key.startswith('expected_') or key == 'ground_truth_rationale':
                    changed[key] = 'DO_NOT_SEND_THIS'
            before = self.ns['build_user_input'](s)
            after = self.ns['build_user_input'](changed)
            self.assertEqual(before, after)
            self.assertNotIn('DO_NOT_SEND_THIS', after)
            self.assertNotIn('expected_', after)

    def test_notebook_example_and_pilot_send_only_dev_ids(self):
        self.ns.update(pilot_scenarios=self.pilot, scenarios=self.test, pprint=lambda obj: None)
        self.create.return_value = SimpleNamespace(output_text=json.dumps(self.prediction(self.pilot[0])), id='offline')
        with redirect_stdout(io.StringIO()):
            for i in [17, 19]:
                exec(''.join(self.nb['cells'][i]['source']), self.ns)
        self.assertEqual(len(self.ns['pilot_records']), 6)
        self.assertEqual([r['scenario_id'] for r in self.ns['pilot_records']], [s['scenario_id'] for s in self.pilot])
        self.assertTrue(all(r['validation_ok'] for r in self.ns['pilot_records']))
        self.assertEqual(self.create.call_count, 7)
        for call in self.create.call_args_list:
            self.assertIn('ID: DEV', call.kwargs['input'][1]['content'])
            self.assertEqual(call.kwargs['model'], self.snapshot['model'])
            self.assertEqual(call.kwargs['input'][0]['content'], self.ns['SYSTEM_PROMPT_V2'])

    def test_hybrid_example_and_pilot_also_keep_official_cases_out(self):
        path = ROOT / 'TCC 03_Arquitetura_Hibrida_com_API.ipynb'
        nb = json.loads(path.read_text())
        selected = []
        run = Mock(side_effect=lambda s: {'scenario_id': s['scenario_id'],
                   'interpretation_ok': True, 'pipeline_ok': True, 'error': None})
        ns = {'pilot_scenarios': self.pilot, 'scenarios': self.test,
              'run_hybrid_scenario': run, 'pprint': lambda obj: None}
        with redirect_stdout(io.StringIO()):
            for c in nb['cells']:
                source = ''.join(c.get('source', []))
                if c['cell_type'] == 'code' and ('pilot_example = next(' in source or 'PILOT_IDS =' in source):
                    exec(source, ns)
                    selected.append(source)
        self.assertEqual(len(selected), 2)
        self.assertEqual([call.args[0]['scenario_id'] for call in run.call_args_list],
                         ['DEV001', 'DEV001', 'DEV002', 'DEV003', 'DEV004', 'DEV005', 'DEV006'])

    def test_full_batch_is_off_by_default_and_uses_only_official_test_set(self):
        self.ns.update(scenarios=self.test)
        self.create.side_effect = [SimpleNamespace(output_text=json.dumps(self.prediction(s)), id='offline') for s in self.test]
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            self.ns['OUTPUT_DIR'] = Path(tmp)
            exec(''.join(self.nb['cells'][24]['source']), self.ns)
            self.assertIs(self.ns['RUN_FULL_EXPERIMENT'], False)
            exec(''.join(self.nb['cells'][26]['source']), self.ns)
            self.create.assert_not_called()
            self.assertFalse((Path(tmp) / 'full_results_v2.jsonl').exists())
            self.ns['RUN_FULL_EXPERIMENT'] = True
            with patch.object(time, 'sleep'):
                exec(''.join(self.nb['cells'][26]['source']), self.ns)
            self.assertEqual([r['scenario_id'] for r in self.ns['full_records']], [s['scenario_id'] for s in self.test])
            self.assertEqual(len((Path(tmp) / 'full_results_v2.jsonl').read_text().splitlines()), 36)
            summary, rows = self.ns['evaluate_baseline'](self.ns['full_records'], self.test)
            self.assertEqual(summary['n_scenarios'], 36)
            self.assertEqual(summary['event_type_accuracy'], 1.0)
            self.assertEqual(summary['artifact_f1_micro'], 1.0)
            self.assertEqual(len(rows), 36)

    def test_parser_and_failed_prediction_still_preserve_audit(self):
        s = self.pilot[0]
        payload = self.prediction(s)
        self.assertEqual(self.ns['extract_json']('```json\n' + json.dumps(payload) + '\n```'), payload)
        self.create.return_value = SimpleNamespace(output_text='invalid JSON', id='failed-offline')
        record = self.ns['run_scenario'](s)
        self.assertFalse(record['parse_ok'])
        self.assertFalse(record['validation_ok'])
        self.assertEqual(record['raw_output'], 'invalid JSON')
        self.assertEqual(record['response_id'], 'failed-offline')
        self.assertIsNotNone(record['error'])
        summary, _ = self.ns['evaluate_baseline']([record], [s])
        self.assertEqual(summary['event_type_accuracy'], 0.0)
        self.assertEqual(summary['artifact_fn'], len(s['expected_artifacts']))

    def test_zip_matches_current_notebook(self):
        with ZipFile(ROOT / 'TCC_Secao_2_Baseline_LLM.zip') as z:
            self.assertEqual(z.read('Secao_2_Baseline_LLM.ipynb'), NOTEBOOK.read_bytes())


if __name__ == '__main__':
    unittest.main()
