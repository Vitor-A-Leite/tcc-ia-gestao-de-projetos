#!/usr/bin/env python3
"""Gera o explorador offline sem dependências; não modifica a fonte."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'data/project_graph.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'visualizacao/grafo_projeto.html')
    args = parser.parse_args()
    raw = args.input.read_bytes()
    graph = json.loads(raw)
    ids = [n['id'] for n in graph['nodes']]
    if len(ids) != len(set(ids)):
        raise ValueError('IDs de nós duplicados')
    for node in graph['nodes']:
        if not all(isinstance(node[k], str) and node[k] for k in ('id', 'name', 'type')):
            raise ValueError('Nó inválido')
    for edge in graph['edges']:
        if edge['source'] not in ids or edge['target'] not in ids or not edge['type']:
            raise ValueError(f'Relação inválida: {edge}')
    payload = json.dumps(graph, ensure_ascii=False).replace('<', '\\u003c')
    template = (ROOT / 'visualizacao/grafo_template.html').read_text(encoding='utf-8')
    html = template.replace('__GRAPH_JSON__', payload).replace('__SOURCE_SHA256__', hashlib.sha256(raw).hexdigest())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding='utf-8')
    linked = {e[k] for e in graph['edges'] for k in ('source', 'target')}
    isolated = [n for n in ids if n not in linked]
    print(f'{args.output.resolve()}\n{len(ids)} nós · {len(graph["edges"])} relações direcionadas · {len(isolated)} nós isolados')
    print(f'SHA-256 da fonte: {hashlib.sha256(raw).hexdigest()}')


if __name__ == '__main__':
    main()
