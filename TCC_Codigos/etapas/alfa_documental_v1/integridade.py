"""Confere hashes sem escrever na carteira ou nas etapas históricas."""
import hashlib
import json
from . import ROOT, REPO


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def verificar_selo():
    m=json.loads((ROOT/'inputs/SELO.json').read_text())
    errors=[path for path,digest in m['arquivos'].items() if not (ROOT/'inputs'/path).is_file() or sha(ROOT/'inputs'/path)!=digest]
    if errors: raise ValueError('Inputs/referências alterados: '+', '.join(errors))
    return len(m['arquivos'])

def conferir_historico():
    old=json.loads((ROOT/'integridade_antes.json').read_text())
    changes=[path for path,digest in old.items() if not (REPO/path).is_file() or sha(REPO/path)!=digest]
    return dict(arquivos_conferidos=len(old),alterados=changes,carteira_inalterada=sha(REPO/json.loads((ROOT/'orcamento_antes.json').read_text())['ledger'])==json.loads((ROOT/'orcamento_antes.json').read_text())['sha256'],inputs_selados=verificar_selo())
