import argparse,json
from pathlib import Path
from . import executar
from piloto_real.chave import carregar

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--preparar',action='store_true');g.add_argument('--rodar',action='store_true');a=p.parse_args()
    root=Path(__file__).resolve().parents[3]
    k=carregar(root/'.env.piloto')if a.rodar else None
    print(json.dumps(executar(root/'TCC_Codigos/data/desenvolvimento',root/'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026',root/'TCC_Codigos/outputs/etapa9_coorte_v04_20261026',chave=k,coletar=a.rodar),ensure_ascii=False))
if __name__=='__main__':main()
