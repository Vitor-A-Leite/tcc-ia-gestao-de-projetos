"""Telemetria preserva resultados e a separação entre IA e referência."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'src'))
from serve_graph3d import execute
from tcc_agent import Event, HybridImpactPipeline, ProjectGraph

class ObservatoryTests(unittest.TestCase):
    def test_all_reference_cases_preserve_pipeline(self):
        graph = json.loads((ROOT / 'data/project_graph.json').read_text())
        cases = json.loads((ROOT / 'data/scenarios_ground_truth.json').read_text())
        for scenario in cases:
            with self.subTest(scenario=scenario['scenario_id']):
                events=[]
                execute(scenario, graph, 'reference', lambda kind,data:events.append((kind,data)))
                result=events[-1][1]
                expected=HybridImpactPipeline(ProjectGraph(graph['nodes'],graph['edges'])).analyze(Event(**result['event']))
                self.assertEqual(result['trace'], expected.trace)
                self.assertEqual(result['impacted_entities'],expected.impacted_entities)
                transfers=[data for kind,data in events if kind=='transfer']
                self.assertEqual(len(transfers),len(expected.trace))
                for step in transfers:
                    self.assertEqual(step['path'],expected.trace[step['target']])
                    self.assertIn({'source':step['source'],'target':step['target'],'type':step['relation']},graph['edges'])
                if scenario['expected_event_type']=='informational':self.assertEqual(transfers,[])

    def test_real_adapter_with_simulated_api(self):
        from run_pilots import load_condition, simulated_client
        graph=json.loads((ROOT / 'data/project_graph.json').read_text())
        scenario=json.loads((ROOT / 'data/scenarios_ground_truth.json').read_text())[0]
        events=[]
        client=simulated_client({scenario['scenario_id']:scenario})
        with patch('openai.OpenAI',return_value=client),patch('tcc_agent.local_runtime.load_local_env'):
            execute(scenario,graph,'real',lambda kind,data:events.append((kind,data)))
        self.assertEqual(events[-1][0],'result')
        self.assertEqual(events[2][1]['response_id'],'simulated-S001')
