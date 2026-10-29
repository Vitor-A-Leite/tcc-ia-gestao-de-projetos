import argparse,json
from pathlib import Path
from . import executar
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rodar',action='store_true');a=p.parse_args()
    root=Path(__file__).resolve().parents[3];o=root/'TCC_Codigos/outputs';k=None
    if a.rodar:
        from piloto_real.chave import carregar
        k=carregar(root/'.env.piloto')
    print(json.dumps(executar(root/'TCC_Codigos/data/desenvolvimento',o/'etapa9_piloto_real_aprovado_20261026',o/'etapa9_piloto_v05_20261027/retomada_89',chave=k,coletar=a.rodar),ensure_ascii=False))
