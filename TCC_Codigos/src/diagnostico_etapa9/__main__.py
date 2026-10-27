import argparse,json
from pathlib import Path
from . import executar
from piloto_real.chave import carregar


def main():
    p=argparse.ArgumentParser(description='Adendo único180s aprovado;mesmo ledger;sem retomada dos90slots')
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--preparar',action='store_true');g.add_argument('--rodar',action='store_true')
    a=p.parse_args();r=Path(__file__).resolve().parents[3]
    pasta=r/'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026'
    saida=r/'TCC_Codigos/outputs/etapa9_diagnostico_180s_20261026/execucao'
    k=carregar(r/'.env.piloto')if a.rodar else None
    x=executar(pasta,saida,chave=k,coletar=a.rodar)
    if 'resultados'in x:x={**x,'resultados':[dict(slot=r['slot_diagnostico'],estado=r['estado'],tempos_ms=r.get('tempos_ms'))for r in x['resultados']]}
    print(json.dumps(x,ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError):raise SystemExit('Adendo/configuração inválida; confira estado e ledger;sem segredos nos logs')from None
