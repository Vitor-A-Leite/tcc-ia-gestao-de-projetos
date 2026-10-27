"""Preparo offline; --rodar exige liberação técnica explícita após revisão."""
import argparse,json
from pathlib import Path
from . import executar
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--preparar',action='store_true');g.add_argument('--rodar',action='store_true');p.add_argument('--revisao-coordenador-registrada',action='store_true');a=p.parse_args()
    if a.rodar and not a.revisao_coordenador_registrada:p.error('R2aguarda revisão do coordenador; nenhuma chave será carregada')
    root=Path(__file__).resolve().parents[3];o=root/'TCC_Codigos/outputs';k=None
    if a.rodar:
        from piloto_real.chave import carregar
        k=carregar(root/'.env.piloto')
    x=executar(root/'TCC_Codigos/data/desenvolvimento',o/'etapa9_piloto_real_aprovado_20261026',o/'etapa9_sse_r2_offline_20261026',chave=k,coletar=a.rodar,liberacao_coordenador=a.revisao_coordenador_registrada)
    print(json.dumps({k:v for k,v in x.items()if k not in ('slots','codigo','ancora')},ensure_ascii=False))
