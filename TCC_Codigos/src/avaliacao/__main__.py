"""Única CLI com acesso às referências autorais, sempre pós-predição."""
import argparse
import json
from pathlib import Path
from condicoes.views import montar_views
from interpretacao_no.contratos import hash_json
from .referencias import preparar_referencias
from .metricas import avaliar


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='acao',required=True)
    r=sub.add_parser('referencias');r.add_argument('pacote',type=Path);r.add_argument('grafo',type=Path);r.add_argument('destino',type=Path)
    r=sub.add_parser('avaliar');r.add_argument('manifesto',type=Path);r.add_argument('registros',type=Path);r.add_argument('referencias',type=Path);r.add_argument('destino',type=Path);r.add_argument('--auditorias',type=Path)
    a=p.parse_args()
    def read(p):return json.loads(p.read_text())
    if a.acao=='referencias':
        b=read(a.pacote/'inputs/base.json');fs=read(a.pacote/'inputs/fontes.json')['fontes'];g=read(a.grafo)
        vs={e['caso_id']:montar_views(b,e,fs,g,vinculo=dict(base_hash=hash_json(b),grafo_hash=hash_json(g),versao_base=b['versao_projeto'],versao_grafo=g['versao'])) for e in read(a.pacote/'inputs/cenarios.json')['casos']}
        out=preparar_referencias(read(a.pacote/'referencias/gabaritos.json'),vs,dict(B=b['versao_projeto'],T=b['versao_projeto'],H=g['versao']))
    else:
        out=avaliar(read(a.manifesto),read(a.registros),read(a.referencias),read(a.auditorias) if a.auditorias else [])
    a.destino.parent.mkdir(parents=True,exist_ok=True)
    a.destino.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
