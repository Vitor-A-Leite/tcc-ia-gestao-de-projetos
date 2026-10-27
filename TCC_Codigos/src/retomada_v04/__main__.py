import argparse,json
from pathlib import Path
from . import executar
from piloto_real.chave import carregar

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--preparar',action='store_true');g.add_argument('--rodar',action='store_true');a=p.parse_args();root=Path(__file__).resolve().parents[3]
    o=root/'TCC_Codigos/outputs';proposta=json.loads((o/'etapa9_coorte_v04_20261026/opcao_retomada_73.json').read_text())
    k=carregar(root/'.env.piloto')if a.rodar else None
    print(json.dumps(executar(root/'TCC_Codigos/data/desenvolvimento',o/'etapa9_piloto_real_aprovado_20261026',o/'etapa9_retomada_v04_20261026',proposta,chave=k,coletar=a.rodar),ensure_ascii=False))
if __name__=='__main__':main()
