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
                    forbidden_patterns = ['/content/', 'drive.mount', '!pip', '%cd']
                    if path.name != 'TCC_Baseline_LLM.ipynb':
                        forbidden_patterns.append('google.colab')
                    for forbidden in forbidden_patterns:
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

    def test_baseline_colab_bootstrap_clones_and_reuses_checkout(self):
        from types import ModuleType
        notebook = json.loads((ROOT.parent / 'TCC_Baseline_LLM.ipynb').read_text())
        bootstrap = next(''.join(c['source']) for c in notebook['cells']
                         if c['cell_type'] == 'code' and 'REPO_ROOT = next(' in ''.join(c['source']))
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            clone = cwd / 'tcc-ia-gestao-de-projetos'
            commands = []

            def run(command, **kwargs):
                self.assertTrue(kwargs['check'])
                commands.append(command)
                if command[:2] == ['git', 'clone']:
                    (clone / 'TCC_Codigos/data').mkdir(parents=True)
                    (clone / 'TCC_Codigos/data/project_graph.json').write_text('{}')

            with patch('pathlib.Path.cwd', return_value=cwd), patch('subprocess.run', side_effect=run), patch.dict(sys.modules, {'pandas': ModuleType('pandas'), 'google.colab': ModuleType('google.colab')}), patch.object(sys, 'path', list(sys.path)), redirect_stdout(io.StringIO()):
                first = {}
                exec(bootstrap, first)
                second = {}
                exec(bootstrap, second)
            self.assertEqual(first['PROJECT_DIR'], clone / 'TCC_Codigos')
            self.assertEqual(second['PROJECT_DIR'], first['PROJECT_DIR'])
            self.assertEqual(sum(command[:2] == ['git', 'clone'] for command in commands), 1)
            self.assertEqual(sum('pip' in command for command in commands), 2)

    def test_baseline_reads_colab_secret_without_printing_it(self):
        from types import ModuleType, SimpleNamespace
        notebook = json.loads((ROOT.parent / 'TCC_Baseline_LLM.ipynb').read_text())
        cell = ''.join(notebook['cells'][5]['source'])
        fake_openai = ModuleType('openai')
        fake_openai.OpenAI = lambda **kwargs: kwargs
        ns = {'REPO_ROOT': ROOT.parent, 'colab': object(), 'os': os,
              'importlib': __import__('importlib')}
        output = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), patch.dict(sys.modules, {'openai': fake_openai}), patch('tcc_agent.local_runtime.load_local_env'), patch('importlib.import_module', return_value=SimpleNamespace(get=lambda name: 'test-secret')), redirect_stdout(output):
            exec(cell, ns)
        self.assertEqual(ns['client']['api_key'], 'test-secret')
        self.assertNotIn('test-secret', output.getvalue())

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
