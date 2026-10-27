import argparse
import json
from pathlib import Path
from .chave import configurar,presente,carregar
from .runner import executar


def main():
    p=argparse.ArgumentParser(description='Etapa9: lote único aprovado gpt-6-luna High; não envia rede sem --rodar')
    g=p.add_mutually_exclusive_group(required=True)
    for nome in ('configurar-chave','checar-chave','preparar','rodar'):g.add_argument('--'+nome,action='store_true')
    a=p.parse_args();root=Path(__file__).resolve().parents[3]
    chave=root/'.env.piloto'
    if a.configurar_chave:
        import subprocess
        ignorado=subprocess.run(['git','check-ignore','-q',str(chave)],cwd=root,capture_output=True).returncode==0
        if not ignorado:raise ValueError('Caminho da chave não está ignorado ou está rastreado pelo Git')
        configurar(chave);return
    if a.checar_chave:print('configurada localmente (sem teste de API)' if presente(chave) else 'ausente');return
    dados=root/'TCC_Codigos/data/desenvolvimento';pasta=root/'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026'
    k=carregar(chave) if a.rodar else None
    r=executar(dados,pasta,chave=k,coletar=a.rodar)
    print(json.dumps(r,ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError):
        raise SystemExit('Configuração/estado inválido; confira permissões, plano e ledger. Nenhum segredo é exibido.') from None
