"""Serializa entradas comuns e relações, sem abrir referências nem outputs."""
import argparse
import json
from pathlib import Path
from .views import montar_views, auditar_equivalencia
from interpretacao_no.contratos import hash_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('inputs',type=Path);p.add_argument('grafo',type=Path);p.add_argument('destino',type=Path)
    a=p.parse_args()
    def read(p):return json.loads(p.read_text())
    base=read(a.inputs/'base.json');g=read(a.grafo);fs=read(a.inputs/'fontes.json')['fontes']
    vinculo=dict(base_hash=hash_json(base),grafo_hash=hash_json(g),versao_base=base['versao_projeto'],versao_grafo=g['versao'])
    # Vinculação declarada pelo normalizador e conferida por campos; hashes não provam autoria.
    a.destino.mkdir(parents=True,exist_ok=True)
    auditoria={}
    for e in read(a.inputs/'cenarios.json')['casos']:
        vs=montar_views(base,e,fs,g,vinculo=vinculo)
        for c,v in vs.items():
            (a.destino/(e['evento_id']+'_'+c+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
        auditoria[e['evento_id']]=auditar_equivalencia(vs)
    (a.destino/'auditoria_views.json').write_text(json.dumps(dict(vinculo=vinculo,eventos=auditoria),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
