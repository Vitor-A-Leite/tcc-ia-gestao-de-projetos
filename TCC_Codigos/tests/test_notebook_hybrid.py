"""Regressões do notebook 3 sem executar setup Colab, ler chaves ou acessar rede.

Execute com Python 3.10+: python3 TCC_Codigos/scripts/test_offline.py
As funções são extraídas via AST do notebook original, sem cópias de implementação.
"""
import ast
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tcc_agent.graph import ProjectGraph
from tcc_agent.models import Event
from tcc_agent.pipeline import HybridImpactPipeline

NOTEBOOK = ROOT.parent / "TCC 03_Arquitetura_Hibrida_com_API.ipynb"


class NotebookHybridTests(unittest.TestCase):
    def setUp(self):
        # Falha imediatamente se qualquer teste tentar abrir conexão de rede.
        network = patch("socket.socket", side_effect=AssertionError("Rede proibida nos testes"))
        network.start()
        self.addCleanup(network.stop)
        self.scenarios = json.loads((ROOT / "data/scenarios_ground_truth.json").read_text())
        raw = json.loads((ROOT / "data/project_graph.json").read_text())
        self.graph = ProjectGraph(raw["nodes"], raw["edges"])
        self.ns = {
            "json": json, "re": re, "time": time, "hashlib": hashlib,
            "datetime": datetime, "timezone": timezone, "Event": Event,
            "entity_catalog": raw["nodes"], "graph": self.graph,
            "pipeline": HybridImpactPipeline(self.graph, max_depth=4),
            # DataFrame é apenas a camada de apresentação; métricas são reais.
            "pd": SimpleNamespace(DataFrame=lambda rows: rows),
        }
        self.notebook = json.loads(NOTEBOOK.read_text())
        for cell in self.notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            source = "\n".join(line for line in source.splitlines() if not line.startswith("!"))
            tree = ast.parse(source)
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    exec(compile(ast.Module(body=[node], type_ignores=[]), str(NOTEBOOK), "exec"), self.ns)
                elif isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id in {
                        "MODEL", "ALLOWED_EVENT_TYPES", "HYBRID_INTERPRETER_PROMPT_V1", "hybrid_prompt_hash"
                    } for t in node.targets
                ):
                    exec(compile(ast.Module(body=[node], type_ignores=[]), str(NOTEBOOK), "exec"), self.ns)
        self.client = SimpleNamespace(responses=SimpleNamespace(create=Mock()))
        self.ns["client"] = self.client

    def prediction(self, scenario=None):
        s = scenario or self.scenarios[0]
        return {
            "event_type": s["expected_event_type"],
            "primary_entity": s["expected_primary_entity"],
            "related_entities": s["expected_related_entities"],
            "responsible": s.get("expected_responsible"),
            "due_date": s.get("expected_due_date"),
            "effective_date": s.get("expected_effective_date"),
            "confidence": 1.0, "rationale": "Resposta simulada para teste offline.",
        }

    def respond(self, text):
        self.client.responses.create.return_value = SimpleNamespace(output_text=text, id="offline-response")
        return self.ns["run_hybrid_scenario"](self.scenarios[0])

    def perfect_records(self):
        return [
            {
                "scenario_id": s["scenario_id"], "llm_prediction": self.prediction(s),
                "impacted_entities": s["expected_impacted_entities"],
                "affected_artifacts": s["expected_artifacts"],
                "interpretation_ok": True, "pipeline_ok": True, "error": None,
            } for s in self.scenarios
        ]

    def test_all_36_reference_interpretations_run_without_api(self):
        records = []
        for s in self.scenarios:
            self.client.responses.create.return_value = SimpleNamespace(
                output_text=json.dumps(self.prediction(s)), id="offline-response"
            )
            record = self.ns["run_hybrid_scenario"](s)
            self.assertTrue(record["pipeline_ok"], (s["scenario_id"], record["error"]))
            records.append(record)
        self.assertEqual(len(records), 36)
        self.assertEqual(self.ns["evaluate_hybrid"](records, self.scenarios)[0]["n_scenarios"], 36)
        for s, r in zip(self.scenarios, records):
            if s["expected_event_type"] == "informational":
                self.assertEqual(r["impacted_entities"], [])
                self.assertEqual(r["affected_artifacts"], [])
                self.assertEqual(r["trace"], {})

    def test_invalid_payload_types_are_rejected_before_pipeline(self):
        invalid_fields = [
            ("related_entities", None), ("related_entities", "C_MOTOR"),
            ("related_entities", [None]), ("related_entities", ["NO_SUCH_ID"]),
            ("primary_entity", []), ("event_type", []), ("event_type", "unknown"),
            ("responsible", "C_MOTOR"), ("responsible", "UNKNOWN"),
            ("due_date", "2026-02-30"), ("due_date", "20261018"),
            ("effective_date", "18/10/2026"), ("effective_date", 123),
            ("confidence", None), ("confidence", True), ("confidence", "0.8"),
            ("confidence", float("nan")), ("confidence", float("inf")),
            ("confidence", -0.1), ("confidence", 1.1),
            ("rationale", None), ("rationale", "  "),
        ]
        for field, value in invalid_fields:
            with self.subTest(field=field, value=value):
                pred = self.prediction()
                pred[field] = value
                with self.assertRaises(ValueError):
                    self.ns["validate_interpretation"](pred)
        for value in [[], None, "text", {}]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.ns["validate_interpretation"](value)

    def test_valid_dates_responsible_and_confidence_boundaries(self):
        for confidence in [0, 0.5, 1]:
            pred = self.prediction()
            pred.update(responsible="P_ANA", due_date="2028-02-29", confidence=confidence)
            self.assertTrue(self.ns["validate_interpretation"](pred))

    def test_converter_cannot_bypass_validation(self):
        pred = self.prediction()
        pred["related_entities"] = None
        with self.assertRaises(ValueError):
            self.ns["prediction_to_event"](pred, "evidência")

    def test_success_preserves_audit_and_expected_fields_are_not_in_prompt(self):
        text = json.dumps(self.prediction())
        record = self.respond(text)
        self.assertTrue(record["interpretation_ok"])
        self.assertTrue(record["pipeline_ok"])
        self.assertEqual(record["raw_output"], text)
        self.assertEqual(record["response_id"], "offline-response")
        self.assertIsNotNone(record["llm_elapsed_seconds"])
        self.assertIsNone(record["error"])
        prompt = self.client.responses.create.call_args.kwargs["input"][1]["content"]
        self.assertNotIn("expected_", prompt)
        self.assertNotIn(self.scenarios[0]["ground_truth_rationale"], prompt)

    def test_invalid_json_preserves_original_response(self):
        record = self.respond("resposta inválida sem JSON")
        self.assertEqual(record["raw_output"], "resposta inválida sem JSON")
        self.assertEqual(record["response_id"], "offline-response")
        self.assertEqual(record["error_stage"], "parse")
        self.assertEqual(record["error_type"], "JSONDecodeError")
        self.assertFalse(record["interpretation_ok"])
        self.assertFalse(record["pipeline_ok"])

    def test_invalid_schema_preserves_original_and_does_not_run_pipeline(self):
        pred = self.prediction()
        pred["related_entities"] = None
        text = json.dumps(pred)
        self.ns["pipeline"] = Mock()
        record = self.respond(text)
        self.assertEqual(record["raw_output"], text)
        self.assertEqual(record["response_id"], "offline-response")
        self.assertEqual(record["error_stage"], "validation")
        self.assertFalse(record["interpretation_ok"])
        self.assertFalse(record["pipeline_ok"])
        self.ns["pipeline"].analyze.assert_not_called()

    def test_api_exception_is_simulated_and_identified(self):
        self.client.responses.create.side_effect = RuntimeError("Falha simulada, sem rede")
        record = self.ns["run_hybrid_scenario"](self.scenarios[0])
        self.assertEqual(record["error_stage"], "api")
        self.assertIsNone(record["raw_output"])
        self.assertFalse(record["pipeline_ok"])

    def test_pipeline_error_keeps_interpretation_and_raw(self):
        self.ns["pipeline"] = Mock()
        self.ns["pipeline"].analyze.side_effect = RuntimeError("Falha simulada do pipeline")
        text = json.dumps(self.prediction())
        record = self.respond(text)
        self.assertEqual(record["raw_output"], text)
        self.assertEqual(record["response_id"], "offline-response")
        self.assertEqual(record["error_stage"], "pipeline")
        self.assertTrue(record["interpretation_ok"])
        self.assertFalse(record["pipeline_ok"])

    def test_coverage_rejects_empty_partial_duplicate_unknown_and_invalid_ids(self):
        records = self.perfect_records()
        unknown = copy.deepcopy(records)
        unknown[-1]["scenario_id"] = "S999"
        invalid = copy.deepcopy(records)
        del invalid[-1]["scenario_id"]
        for batch in [[], records[:1], records[:-1], records + [records[0]], unknown, invalid]:
            with self.subTest(length=len(batch)), self.assertRaises(ValueError):
                self.ns["evaluate_hybrid"](batch, self.scenarios)

    def test_ground_truth_requires_unique_nonempty_scenarios(self):
        with self.assertRaises(ValueError):
            self.ns["evaluate_hybrid"]([], [])
        with self.assertRaises(ValueError):
            self.ns["evaluate_hybrid"](self.perfect_records(), self.scenarios + [self.scenarios[0]])

    def test_complete_perfect_predictions_have_perfect_metrics(self):
        summary, rows = self.ns["evaluate_hybrid"](self.perfect_records(), self.scenarios)
        self.assertEqual(summary["n_scenarios"], 36)
        self.assertEqual(summary["n_expected_scenarios"], 36)
        self.assertEqual(summary["n_pipeline_failures"], 0)
        self.assertEqual(len(rows), 36)
        for key in ["event_type_accuracy", "artifact_f1_micro", "entity_f1_micro"]:
            self.assertEqual(summary[key], 1.0)

    def test_failed_attempts_are_counted_and_not_removed(self):
        records = self.perfect_records()
        records[0].update(llm_prediction=None, interpretation_ok=False, pipeline_ok=False,
                          impacted_entities=[], affected_artifacts=[], error="Falha simulada")
        summary, rows = self.ns["evaluate_hybrid"](records, self.scenarios)
        self.assertEqual(len(rows), 36)
        self.assertEqual(summary["n_interpretation_failures"], 1)
        self.assertEqual(summary["n_pipeline_failures"], 1)
        self.assertEqual(summary["event_type_accuracy"], 35 / 36)
        self.assertLess(summary["artifact_recall_micro"], 1)
        self.assertLess(summary["entity_recall_micro"], 1)


if __name__ == "__main__":
    unittest.main()
