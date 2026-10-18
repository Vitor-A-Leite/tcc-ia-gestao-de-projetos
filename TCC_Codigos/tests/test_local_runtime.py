"""Execução portátil pelo repositório, sem serviços de notebook na nuvem."""
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tcc_agent.local_runtime import repository_root, load_local_env


class LocalRuntimeTests(unittest.TestCase):
    def test_repository_found_from_root_and_nested_folder(self):
        self.assertEqual(repository_root(ROOT.parent), ROOT.parent)
        self.assertEqual(repository_root(ROOT / "data"), ROOT.parent)

    def test_missing_repository_reports_local_path_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                repository_root(tmp)

    def test_env_is_loaded_without_output_or_overriding_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, '.env').write_text('# teste\nTCC_TEST_SECRET="dummy-value"\nTCC_TEST_EXPORTED=file-value\n')
            with patch.dict(os.environ, {'TCC_TEST_EXPORTED': 'already-exported'}):
                os.environ.pop('TCC_TEST_SECRET', None)
                output = io.StringIO()
                with redirect_stdout(output):
                    load_local_env(tmp)
                self.assertEqual(os.environ['TCC_TEST_SECRET'], 'dummy-value')
                self.assertEqual(os.environ['TCC_TEST_EXPORTED'], 'already-exported')
                self.assertEqual(output.getvalue(), '')

    def test_env_does_not_execute_shell_and_handles_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            load_local_env(tmp)
            Path(tmp, '.env').write_text('TCC_TEST_LITERAL=$(echo no-execution)\n')
            with patch.dict(os.environ, {}, clear=True):
                load_local_env(tmp)
                self.assertEqual(os.environ['TCC_TEST_LITERAL'], '$(echo no-execution)')

    def test_bad_env_line_does_not_expose_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, '.env').write_text('BAD LINE WITH SECRET\n')
            with self.assertRaisesRegex(ValueError, 'linha 1') as caught:
                load_local_env(tmp)
            self.assertNotIn('SECRET', str(caught.exception))

    def test_all_notebooks_are_local_python_and_portable(self):
        import ast
        paths = [ROOT.parent / name for name in [
            'ProjetoTCCv01.ipynb', 'TCC_Baseline_LLM.ipynb',
            'TCC 03_Arquitetura_Hibrida_com_API.ipynb',
        ]]
        for path in paths:
            with self.subTest(notebook=path.name):
                nb = json.loads(path.read_text())
                for cell in nb['cells']:
                    if cell['cell_type'] != 'code':
                        continue
                    code = ''.join(cell['source'])
                    ast.parse(code)
                    for forbidden in ['google.colab', '/content/', 'drive.mount', '!pip', '%cd']:
                        self.assertNotIn(forbidden, code)
                bootstrap = next(''.join(c['source']) for c in nb['cells']
                                 if c['cell_type'] == 'code' and 'REPO_ROOT = next(' in ''.join(c['source']))
                # Verifica portabilidade com caminho diferente do computador do autor.
                with tempfile.TemporaryDirectory() as tmp:
                    clone = Path(tmp)
                    (clone / 'TCC_Codigos/data').mkdir(parents=True)
                    (clone / 'TCC_Codigos/data/project_graph.json').write_text('{}')
                    with patch('pathlib.Path.cwd', return_value=clone), patch.object(sys, 'path', list(sys.path)), redirect_stdout(io.StringIO()):
                        ns = {}
                        exec(bootstrap, ns)
                    self.assertEqual(ns['PROJECT_DIR'], clone / 'TCC_Codigos')

    def test_terminal_runner_refuses_api_without_explicit_flag(self):
        path = ROOT / 'scripts/run_local.py'
        spec = importlib.util.spec_from_file_location('tcc_local_runner', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for condition in ['baseline', 'hybrid']:
            with patch.object(sys, 'argv', [str(path), condition]), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    module.main()
                self.assertEqual(caught.exception.code, 2)
