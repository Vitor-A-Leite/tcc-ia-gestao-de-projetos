"""Verifica integridade de uma entrega extraída, somente com biblioteca padrão."""
from pathlib import Path
import hashlib,json,sys

ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    manifest=json.loads((ROOT/'MANIFESTO_ENTREGA.json').read_text())
    errors=[]
    for rel,expected in manifest['arquivos'].items():
        p=(ROOT/rel).resolve()
        if ROOT not in p.parents or not p.is_file():errors.append('Ausente ou fora da entrega: '+rel)
        elif sha(p)!=expected:errors.append('Hash diferente: '+rel)
    for rel,origin in json.loads((ROOT/'evidencias/PROVENIENCIA.json').read_text()).items():
        p=ROOT/rel
        if not p.is_file() or sha(p)!=origin['sha256']:errors.append('Cópia de evidência diferente: '+rel)
    result={'ok':not errors,'arquivos_verificados':len(manifest['arquivos']),'erros':errors,
            'nota':'Hashes confirmam integridade, não correção científica ou aprovação humana.'}
    print(json.dumps(result,ensure_ascii=False,indent=2));return not errors
if __name__=='__main__':sys.exit(0 if verify() else 1)
