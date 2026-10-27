"""Gera lote offline em diretório novo; não sobrescreve artefatos anteriores."""
import argparse
import json
from pathlib import Path
from . import ROTULO
from .lote import executar_lote


def main():
    parser=argparse.ArgumentParser(description=ROTULO)
    parser.add_argument('--dados',type=Path,required=True)
    parser.add_argument('--saida',type=Path,required=True)
    a=parser.parse_args()
    r=executar_lote(a.dados,a.saida)
    print(json.dumps(dict(rotulo=r['rotulo'],normais={k:v for k,v in r['normais'].items() if k!='registros'},
        contraprovas=r['contraprovas'],chamadas_api_reais=r['chamadas_api_reais']),ensure_ascii=False))


if __name__=='__main__':main()
