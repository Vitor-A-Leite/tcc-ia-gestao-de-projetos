"""Demonstração somente SIMULADA; arquivo escolhido explicitamente."""
import argparse
import json
from pathlib import Path
from . import avaliar
from .simulacao import InterpretadorPrescrito, politica_prescrita
p=argparse.ArgumentParser()
p.add_argument('estado')
p.add_argument('fixture', help='Transcrição prescrita SIMULADA de um único evento')
a=p.parse_args()
e=json.loads(Path(a.estado).read_text())
f=json.loads(Path(a.fixture).read_text())
print(json.dumps(avaliar(e, f['evento'], InterpretadorPrescrito(f), politica_prescrita(f)), ensure_ascii=False, indent=2))
