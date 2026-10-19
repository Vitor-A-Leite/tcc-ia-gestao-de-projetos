#!/usr/bin/env python3
"""Executa seis casos por condição, isolando saídas e reutilizando as funções dos notebooks."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "TCC_Codigos/src"))
from tcc_agent.evaluate import set_metrics
from tcc_agent.graph import ProjectGraph
from tcc_agent.models import Event
from tcc_agent.local_runtime import load_local_env
from tcc_agent.pipeline import HybridImpactPipeline

NOTEBOOKS = {"baseline": "TCC_Baseline_LLM.ipynb", "hybrid": "TCC 03_Arquitetura_Hibrida_com_API.ipynb"}
CONFIG = {"MODEL", "PILOT_IDS", "ALLOWED_EVENT_TYPES", "ALLOWED_ARTIFACTS", "SYSTEM_PROMPT_V2", "HYBRID_INTERPRETER_PROMPT_V1", "prompt_hash", "hybrid_prompt_hash"}


def load_condition(condition, scenarios, raw_graph, pd):
    """Importa funções e configurações, sem executar células de setup ou chamadas."""
    graph = ProjectGraph(raw_graph["nodes"], raw_graph["edges"])
    ns = dict(json=json, re=re, time=time, hashlib=hashlib, datetime=datetime,
              timezone=timezone, pd=pd, Event=Event, graph=graph,
              pipeline=HybridImpactPipeline(graph, max_depth=4),
              entity_catalog=raw_graph["nodes"])
    nb = json.loads((ROOT / NOTEBOOKS[condition]).read_text())
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.FunctionDef) or (
                isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in CONFIG for t in node.targets)
            ):
                exec(compile(ast.Module(body=[node], type_ignores=[]), NOTEBOOKS[condition], "exec"), ns)
    return ns


def simulated_client(by_id):
    def create(**kwargs):
        text = kwargs["input"][1]["content"]
        sid = re.search(r"ID: (S\d+)", text).group(1)
        s = by_id[sid]
        pred = dict(event_type=s["expected_event_type"], primary_entity=s["expected_primary_entity"],
                    related_entities=s["expected_related_entities"], responsible=s.get("expected_responsible"),
                    due_date=s.get("expected_due_date"), effective_date=s.get("expected_effective_date"),
                    rationale="Referência injetada para teste offline; não é resposta de LLM.", confidence=1.0,
                    impacted_entities=s["expected_impacted_entities"], impacted_artifacts=s["expected_artifacts"])
        return SimpleNamespace(output_text=json.dumps(pred, ensure_ascii=False), id="simulated-" + sid,
                               model=kwargs["model"], usage=None)
    return SimpleNamespace(responses=SimpleNamespace(create=create))


class AuditClient:
    def __init__(self, client):
        self.client = client
        self.responses = SimpleNamespace(create=self.create)
        self.latest = {}
        self.failure = None

    def create(self, **kwargs):
        self.latest = {}
        self.failure = None
        started = time.monotonic()
        try:
            response = self.client.responses.create(**kwargs)
        except Exception as exc:
            self.failure = {"type": type(exc).__name__, "http_status": getattr(exc, "status_code", None),
                            "code": getattr(exc, "code", None)}
            # Nunca propaga texto de autenticação que possa conter fragmentos da chave.
            raise RuntimeError("Falha de API: " + json.dumps(self.failure)) from None
        usage = getattr(response, "usage", None)
        self.latest = {"response_model": getattr(response, "model", None),
                       "usage": usage.model_dump() if hasattr(usage, "model_dump") else None,
                       "request_id": getattr(response, "_request_id", None),
                       "request_elapsed_seconds": round(time.monotonic() - started, 3)}
        return response


def pilot_metrics(condition, records, scenarios, ns, folder):
    expected_ids = {s["scenario_id"] for s in scenarios}
    if len(records) != len(scenarios) or {r["scenario_id"] for r in records} != expected_ids:
        return None
    if condition == "hybrid":
        summary, details = ns["evaluate_hybrid"](records, scenarios)
    else:
        summary, details = ns["evaluate_baseline"](records, scenarios)
    summary["scope"] = "piloto; não é avaliação do experimento completo"
    summary["n_execution_errors"] = sum(bool(r.get("error")) for r in records)
    (folder / "metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    details.to_csv(folder / "details.csv", index=False)
    return summary


def run(args, pd):
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError("A pasta de saída já existe; escolha uma nova para preservar resultados.")
    output.mkdir(parents=True)
    scenarios = json.loads((ROOT / "TCC_Codigos/data/scenarios_ground_truth.json").read_text())
    raw_graph = json.loads((ROOT / "TCC_Codigos/data/project_graph.json").read_text())
    by_id = {s["scenario_id"]: s for s in scenarios}
    namespaces = {c: load_condition(c, scenarios, raw_graph, pd) for c in NOTEBOOKS}
    if len({ns["MODEL"] for ns in namespaces.values()}) != 1:
        raise ValueError("Os modelos do baseline e híbrido precisam ser iguais.")
    if namespaces["baseline"]["PILOT_IDS"] != namespaces["hybrid"]["PILOT_IDS"]:
        raise ValueError("Os pilotos das duas condições precisam ter os mesmos IDs.")
    client = None
    if args.mode == "real":
        from openai import OpenAI
        load_local_env(ROOT)
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY ausente no ambiente local.")
        client = OpenAI(api_key=key, max_retries=0, timeout=60.0)
    manifest = {"mode": args.mode, "started_at_utc": datetime.now(timezone.utc).isoformat(),
                "python": sys.version.split()[0], "models": {c: ns["MODEL"] for c, ns in namespaces.items()},
                "pilot_ids": namespaces["baseline"]["PILOT_IDS"], "max_depth_hybrid": 4,
                "sdk_retries": 0, "timeout_seconds": 60,
                "files_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                    [*NOTEBOOKS.values(), "TCC_Codigos/data/project_graph.json", "TCC_Codigos/data/scenarios_ground_truth.json",
                     "TCC_Codigos/src/tcc_agent/pipeline.py", "TCC_Codigos/src/tcc_agent/graph.py", "TCC_Codigos/src/tcc_agent/rules.py"]},
                "packages": {name: importlib.metadata.version(name) for name in ["openai", "pandas"]}}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    summaries = {}
    stopped = None
    for condition, ns in namespaces.items():
        folder = output / condition
        folder.mkdir()
        prompt = ns["SYSTEM_PROMPT_V2"] if condition == "baseline" else ns["HYBRID_INTERPRETER_PROMPT_V1"]
        (folder / "prompt.txt").write_text(prompt)
        audit = AuditClient(client if args.mode == "real" else simulated_client(by_id))
        ns["client"] = audit
        analyze = ns["run_scenario"] if condition == "baseline" else ns["run_hybrid_scenario"]
        records = []
        print(f'\n{condition.upper()} — {args.mode} — {len(ns["PILOT_IDS"])} cenários', flush=True)
        for index, sid in enumerate(ns["PILOT_IDS"], 1):
            print(f'[{index}/6] {sid}: iniciando', flush=True)
            try:
                record = analyze(by_id[sid])
            except Exception as exc:
                record = {"scenario_id": sid, "model": ns["MODEL"], "prediction": None,
                          "parse_ok": False, "validation_ok": False, "raw_output": None,
                          "error": str(exc), "error_stage": "api"}
            record["mode"] = args.mode
            record["api_audit"] = audit.latest
            if audit.failure:
                record["api_failure"] = audit.failure
            records.append(record)
            with (folder / "records.jsonl").open("a") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            pred = record.get("prediction") or record.get("llm_prediction") or {}
            print(f'[{index}/6] {sid}: {"ERRO" if record.get("error") else "OK"}; '
                  f'tipo={pred.get("event_type")}; esperado={by_id[sid]["expected_event_type"]}', flush=True)
            if audit.failure:
                stopped = {"condition": condition, "scenario_id": sid, **audit.failure}
                print("Interrompido após falha da API; sem repetição automática.", flush=True)
                break
        selected = [by_id[sid] for sid in ns["PILOT_IDS"]]
        summaries[condition] = pilot_metrics(condition, records, selected, ns, folder)
        if stopped:
            break
    result = {"mode": args.mode, "summaries": summaries, "stopped": stopped,
              "finished_at_utc": datetime.now(timezone.utc).isoformat()}
    (output / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print('\nResumo salvo em:', output, flush=True)
    return 1 if stopped else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["simulated", "real"], default="simulated")
    parser.add_argument("--allow-api", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "real" and not args.allow_api:
        parser.error("A execução real precisa de --allow-api.")
    import pandas as pd
    if args.mode == "simulated":
        with patch("socket.socket", side_effect=AssertionError("Rede bloqueada na simulação")):
            return run(args, pd)
    return run(args, pd)


if __name__ == "__main__":
    raise SystemExit(main())
