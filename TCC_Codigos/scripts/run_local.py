#!/usr/bin/env python3
"""Executa notebooks locais como Python, sem Jupyter, Drive ou Colab."""
import argparse
import ast
import json
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = {
    "setup": "ProjetoTCCv01.ipynb",
    "baseline": "TCC_Baseline_LLM.ipynb",
    "hybrid": "TCC 03_Arquitetura_Hibrida_com_API.ipynb",
}


def display(value):
    print(value.to_string(index=False) if hasattr(value, "to_string") else value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition", choices=NOTEBOOKS)
    parser.add_argument("--allow-api", action="store_true", help="Autoriza as chamadas pagas do piloto")
    parser.add_argument("--full", action="store_true", help="Executa também os 36 casos após o piloto; use após congelar o protocolo")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error("Use Python 3.10 ou superior.")
    if args.condition != "setup" and not args.allow_api:
        parser.error("Baseline e híbrido chamam a API. Use --allow-api para autorizar; para testar sem API use scripts/test_offline.py.")
    notebook_path = ROOT / NOTEBOOKS[args.condition]
    nb = json.loads(notebook_path.read_text(encoding="utf-8"))
    ns = {"__name__": "__main__", "__file__": str(notebook_path), "display": display}
    original_cwd = Path.cwd()
    try:
        os.chdir(ROOT)
        for index, cell in enumerate(nb["cells"], 1):
            if cell["cell_type"] != "code":
                continue
            tree = ast.parse("".join(cell["source"]), filename=f"{notebook_path.name}:célula {index}")
            for node in tree.body:
                if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id in {"RUN_FULL_EXPERIMENT", "RUN_FULL_HYBRID"}
                    for t in node.targets
                ):
                    node.value = ast.Constant(value=args.full)
            # Exibe expressões finais, como tabelas, também no terminal.
            if tree.body and isinstance(tree.body[-1], ast.Expr):
                last = tree.body.pop()
                exec(compile(ast.fix_missing_locations(tree), str(notebook_path), "exec"), ns)
                value = eval(compile(ast.Expression(last.value), str(notebook_path), "eval"), ns)
                if value is not None:
                    display(value)
            else:
                exec(compile(ast.fix_missing_locations(tree), str(notebook_path), "exec"), ns)
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()
