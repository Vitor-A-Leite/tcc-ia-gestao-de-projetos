"""Entradas explícitas. Nenhum comando deste CLI executa chamadas pagas."""
import argparse
import json
from pathlib import Path
from . import ROOT
from .dados import gravar
from .integridade import verificar_selo,conferir_historico


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    run=sub.add_parser('simular');run.add_argument('cenario');run.add_argument('--saida',type=Path,required=True)
    val=sub.add_parser('avaliar');val.add_argument('--saida',type=Path,required=True);val.add_argument('--particao',choices=['dev','final'],default='dev')
    sub.add_parser('testar');sub.add_parser('integridade')
    demo=sub.add_parser('construir-demo');demo.add_argument('--resultados',type=Path,required=True)
    srv=sub.add_parser('servir');srv.add_argument('--porta',type=int,default=8766)
    sub.add_parser('protocolo-pago')
    reg=sub.add_parser('cadastrar-documento');reg.add_argument('arquivo',type=Path);reg.add_argument('--destino',type=Path,required=True)
    args=p.parse_args();verificar_selo()
    if args.cmd=='simular':
        from .pipeline import simular
        if args.saida.exists(): raise ValueError('Saída existe; preserve a tentativa anterior')
        r=simular(args.cenario);gravar(args.saida,r);print(json.dumps(r['execucao']))
    elif args.cmd=='avaliar':
        from .avaliacao import executar_avaliacao
        print(json.dumps(executar_avaliacao(args.saida,args.particao),ensure_ascii=False,indent=2))
    elif args.cmd=='testar':
        from .testes import run
        raise SystemExit(0 if run().wasSuccessful() else 1)
    elif args.cmd=='integridade': print(json.dumps(conferir_historico(),ensure_ascii=False,indent=2))
    elif args.cmd=='construir-demo':
        from .demo import construir_demo
        construir_demo(args.resultados);print(ROOT/'web/index.html')
    elif args.cmd=='servir':
        from .demo import servir
        servir(args.porta)
    elif args.cmd=='protocolo-pago': print((ROOT/'PROTOCOLO_PAGO.md').read_text())
    elif args.cmd=='cadastrar-documento':
        from .cadastro import cadastrar
        from .modelo import carregar
        g,d=carregar()
        print(json.dumps(cadastrar(args.arquivo,args.destino,[n['id'] for n in g['nodes']]+[x['id'] for x in d]+['PROJECT']),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
