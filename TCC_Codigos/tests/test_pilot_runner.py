"""Segurança e reprodutibilidade do executor local de pilotos, sem API."""
import importlib.util
import io
import json
from contextlib import redirect_stderr
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tcc_pilot_runner', ROOT / 'scripts/run_pilots.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class PilotRunnerTests(unittest.TestCase):
    def test_real_mode_requires_explicit_authorization_before_loading_key(self):
        with patch.object(sys, 'argv', ['run_pilots.py', '--mode', 'real', '--output', '/tmp/not-created']), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                runner.main()
        self.assertEqual(caught.exception.code, 2)

    def test_existing_outputs_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / 'marker.txt'
            marker.write_text('preservar')
            with self.assertRaises(FileExistsError):
                runner.run(SimpleNamespace(output=Path(tmp), mode='simulated'), None)
            self.assertEqual(marker.read_text(), 'preservar')

    def test_api_error_does_not_expose_exception_contents(self):
        def fail(**kwargs):
            raise ValueError('Mensagem sensível que não deve aparecer na auditoria')
        audit = runner.AuditClient(SimpleNamespace(responses=SimpleNamespace(create=fail)))
        with self.assertRaises(RuntimeError) as caught:
            audit.responses.create(model='modelo-teste', input=[])
        self.assertNotIn('Mensagem sensível', str(caught.exception))
        self.assertEqual(audit.failure['type'], 'ValueError')
        self.assertEqual(audit.latest, {})

    def test_simulated_client_is_explicitly_labelled_and_offline(self):
        scenarios = json.loads((ROOT / 'data/scenarios_ground_truth.json').read_text())
        client = runner.simulated_client({s['scenario_id']: s for s in scenarios})
        with patch('socket.socket', side_effect=AssertionError('Sem rede')):
            response = client.responses.create(model='modelo-teste', input=[{}, {'content': 'ID: S001'}])
        pred = json.loads(response.output_text)
        self.assertTrue(response.id.startswith('simulated-'))
        self.assertIn('teste offline', pred['rationale'])
        self.assertEqual(pred['event_type'], scenarios[0]['expected_event_type'])

    def test_notebook_functions_load_without_creating_real_client(self):
        scenarios = json.loads((ROOT / 'data/scenarios_ground_truth.json').read_text())
        graph = json.loads((ROOT / 'data/project_graph.json').read_text())
        fake_pd = SimpleNamespace(DataFrame=lambda rows: rows)
        with patch('socket.socket', side_effect=AssertionError('Sem rede')), patch.object(runner, 'load_local_env', side_effect=AssertionError('Não carregar chave')):
            namespaces = {c: runner.load_condition(c, scenarios, graph, fake_pd) for c in runner.NOTEBOOKS}
        self.assertEqual(namespaces['baseline']['MODEL'], namespaces['hybrid']['MODEL'])
        self.assertEqual(len(namespaces['baseline']['PILOT_IDS']), 6)
        self.assertEqual(namespaces['baseline']['PILOT_IDS'], namespaces['hybrid']['PILOT_IDS'])
        for ns in namespaces.values():
            self.assertNotIn('client', ns)
            self.assertNotIn('api_key', ns)
