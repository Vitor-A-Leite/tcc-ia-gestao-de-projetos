#!/bin/zsh
cd "${0:A:h}/../../.."
if [[ -x .venv/bin/python ]]; then
  alfa_python=.venv/bin/python
else
  alfa_python=python3
fi
(sleep 1; open 'http://127.0.0.1:8766') &
"$alfa_python" -m TCC_Codigos.etapas.alfa_documental_v1 servir --porta 8766
