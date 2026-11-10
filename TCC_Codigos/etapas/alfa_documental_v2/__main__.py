"""Entrada única: python -m alfa_documental_v2 ou caminho da pasta."""
if not __package__:
    import sys
    import runpy
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
    runpy.run_module(Path(__file__).resolve().parent.name,run_name='__main__')
    raise SystemExit

import argparse
import json
from .src.sessoes import Sessoes


def main():
    p=argparse.ArgumentParser(description='Alfa documental v2 — somente simulação offline')
    sub=p.add_subparsers(dest='comando',required=True)
    s=sub.add_parser('servir');s.add_argument('--porta',type=int,default=8767)
    sub.add_parser('testar');sub.add_parser('comparar');sub.add_parser('integridade')
    s=sub.add_parser('auditar');s.add_argument('resultado');s.add_argument('--saida',required=True)
    s=sub.add_parser('simular');s.add_argument('cenario');s.add_argument('--entradas',nargs='+',required=True);s.add_argument('--limite',default='todos');s.add_argument('--max-solicitacoes',type=int,default=32)
    s=sub.add_parser('continuar');s.add_argument('id');s.add_argument('--nos',nargs='+',required=True);s.add_argument('--limite',required=True);s.add_argument('--max-solicitacoes',type=int,default=32)
    s=sub.add_parser('cancelar');s.add_argument('id')
    a=p.parse_args()
    if a.comando=='servir':
        from .src.demo import servir
        servir(a.porta);return
    if a.comando=='testar':
        import unittest
        from pathlib import Path
        root=Path(__file__).resolve().parent
        suite=unittest.defaultTestLoader.discover(str(root/'tests'), top_level_dir=str(root.parent))
        raise SystemExit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
    if a.comando=='auditar':
        from .src.auditoria import auditar_arquivo
        r=auditar_arquivo(a.resultado,a.saida)
        print(json.dumps({'estado':r['estado'],'registros':len(r['registros']),'saida':a.saida},ensure_ascii=False));return
    if a.comando=='comparar':
        from .src.avaliacao import comparar
        print(json.dumps(comparar(),ensure_ascii=False,indent=2));return
    if a.comando=='integridade':
        from .src.avaliacao import integridade
        r=integridade();print(json.dumps(r,indent=2));raise SystemExit(0 if r['ok'] else 1)
    m=Sessoes()
    if a.comando=='simular':
        r=m.preparar(a.cenario,a.entradas,a.limite,limites={'max_solicitacoes':a.max_solicitacoes});r=m.executar(r['id'])
    elif a.comando=='continuar':r=m.executar(a.id,selecionados=a.nos,max_nos=a.limite,limites={'max_solicitacoes':a.max_solicitacoes})
    else:r=m.cancelar(a.id)
    from .src.demo import publico
    print(json.dumps(publico(r),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
