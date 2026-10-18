#!/usr/bin/env python3
"""Executa todos os testes locais sem dependências extras e com rede bloqueada."""
import importlib
import inspect
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Os testes do projeto requerem Python 3.10 ou superior.")
    root = Path(__file__).resolve().parents[1]
    test_dir = root / "tests"
    sys.path.insert(0, str(test_dir))
    # Impede acesso à API inclusive se uma regressão introduzir conexão de rede.
    with patch("socket.socket", side_effect=AssertionError("Rede proibida nos testes offline")):
        suite = unittest.defaultTestLoader.discover(str(test_dir))
        # Inclui os testes originais escritos como funções para pytest.
        for path in sorted(test_dir.glob("test_*.py")):
            module = importlib.import_module(path.stem)
            for name, fn in inspect.getmembers(module, inspect.isfunction):
                if name.startswith("test_") and fn.__module__ == module.__name__:
                    suite.addTest(unittest.FunctionTestCase(fn, description=f"{module.__name__}.{name}"))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
