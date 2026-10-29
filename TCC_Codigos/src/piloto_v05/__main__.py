import argparse,json
from pathlib import Path
from . import executar,snapshot
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rodar',action='store_true');args=p.parse_args()
    root=Path(__file__).resolve().parents[3];o=root/'TCC_Codigos/outputs';pasta=o/'etapa9_piloto_real_aprovado_20261026';out=o/'etapa9_piloto_v05_20261027'
    snapshot(root,pasta,out);k=None
    if args.rodar:
        from piloto_real.chave import carregar
        k=carregar(root/'.env.piloto')
    print(json.dumps(executar(root/'TCC_Codigos/data/desenvolvimento',pasta,out,chave=k,coletar=args.rodar),ensure_ascii=False))
