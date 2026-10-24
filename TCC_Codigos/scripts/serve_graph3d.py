#!/usr/bin/env python3
"""Servidor local do observatório 3D. API paga exige --allow-api e seleção na UI."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from tcc_agent import Event, HybridImpactPipeline, ProjectGraph


def execute(scenario, raw_graph, mode, emit):
    emit('input', {'text': scenario['source_text'], 'scenario_id': scenario['scenario_id']})
    emit('processing', {'mode': mode, 'message': 'Interpretando com IA' if mode == 'real' else 'Carregando interpretação de referência; sem IA'})
    if mode == 'real':
        from run_pilots import load_condition, AuditClient
        from tcc_agent.local_runtime import load_local_env
        from openai import OpenAI
        load_local_env(ROOT.parent)
        ns = load_condition('hybrid', [scenario], raw_graph, None)
        ns['client'] = AuditClient(OpenAI(max_retries=0, timeout=90))
        result = ns['call_interpreter_llm'](scenario)
        if result['error']:
            raise RuntimeError('A interpretação da IA falhou ou não passou na validação.')
        event = ns['prediction_to_event'](result['prediction'], evidence=scenario['source_text'])
        detail = dict(result['prediction'], response_id=result['response_id'], model=ns['MODEL'])
    else:
        event = Event(event_type=scenario['expected_event_type'],
                      primary_entity=scenario['expected_primary_entity'],
                      related_entities=scenario['expected_related_entities'],
                      responsible=scenario.get('expected_responsible'),
                      due_date=scenario.get('expected_due_date'),
                      effective_date=scenario.get('expected_effective_date'), evidence=scenario['source_text'])
        detail = dict(asdict(event), rationale='Interpretação de referência injetada; não é uma resposta de IA.')
    emit('interpretation', detail)
    pipeline = HybridImpactPipeline(ProjectGraph(raw_graph['nodes'], raw_graph['edges']))
    result = pipeline.analyze(event, on_step=lambda step: emit('transfer', step))
    emit('result', asdict(result))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send_json(self, value, status=200):
        data = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == '/api/data':
            return self.send_json({'graph': self.server.graph, 'scenarios': [
                {k: s[k] for k in ('scenario_id', 'source_text')} for s in self.server.scenarios],
                'allow_api': self.server.allow_api})
        if self.path == '/api/runs':
            return self.send_json([json.loads(p.read_text()) for p in sorted(self.server.output.glob('*.json'))])
        files = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
        if self.path not in files:
            return self.send_json({'error': 'Não encontrado'}, 404)
        name, mime = files[self.path]
        data = (ROOT / 'visualizacao/observatorio3d' / name).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        # Somente a própria interface local pode disparar uma execução.
        origin = self.headers.get('Origin')
        expected = 'http://' + self.headers.get('Host', '')
        if origin and origin != expected:
            return self.send_json({'error': 'Origem inválida'}, 403)
        if self.path != '/api/run' or self.headers.get('Content-Type') != 'application/json':
            return self.send_json({'error': 'Pedido inválido'}, 400)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length < 4096:
                raise ValueError()
            body = json.loads(self.rfile.read(length))
            scenario = next(s for s in self.server.scenarios if s['scenario_id'] == body['scenario_id'])
            mode = body['mode']
            if mode not in ('reference', 'real') or (mode == 'real' and not self.server.allow_api):
                raise ValueError()
        except (ValueError, KeyError, StopIteration, TypeError):
            return self.send_json({'error': 'Cenário ou modo inválido; API requer --allow-api.'}, 400)
        run = {'id': uuid.uuid4().hex, 'created_at': datetime.now(timezone.utc).isoformat(),
               'scenario_id': scenario['scenario_id'], 'mode': mode, 'events': []}
        self.send_response(200)
        self.send_header('Content-Type', 'application/x-ndjson; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        started = time.monotonic()
        disconnected = False
        def emit(kind, data):
            nonlocal disconnected
            item = {'type': kind, 'data': data, 'elapsed_ms': round((time.monotonic()-started)*1000, 2)}
            run['events'].append(item)
            if not disconnected:
                try:
                    self.wfile.write((json.dumps(item, ensure_ascii=False)+'\n').encode())
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    disconnected = True
        try:
            execute(scenario, self.server.graph, mode, emit)
        except Exception as exc:
            emit('error', {'message': 'Execução interrompida. Verifique configuração e disponibilidade da API.', 'type': type(exc).__name__})
        finally:
            self.server.output.mkdir(parents=True, exist_ok=True)
            (self.server.output / (run['id'] + '.json')).write_text(json.dumps(run, ensure_ascii=False, indent=2))
            emit('saved', {'id': run['id']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--allow-api', action='store_true')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.graph = json.loads((ROOT / 'data/project_graph.json').read_text())
    server.scenarios = json.loads((ROOT / 'data/scenarios_ground_truth.json').read_text())
    server.allow_api = args.allow_api
    server.output = ROOT / 'outputs/observatorio3d'
    print(f'Observatório 3D: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    main()
