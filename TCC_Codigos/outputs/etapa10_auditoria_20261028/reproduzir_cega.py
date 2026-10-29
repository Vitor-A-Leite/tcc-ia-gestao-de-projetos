"""Reproduz em pasta temporária: nunca sobrescreve os artefatos cegos selados."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile

OUT=Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix='tcc-etapa10-repro-') as td:
        t=Path(td)
        shutil.copytree(OUT/'pacote_cego_desenvolvimento',t/'pacote_cego_desenvolvimento')
        d=t/'revisao_cega';d.mkdir()
        shutil.copyfile(OUT/'revisao_cega/calcular_independente.py',d/'calcular_independente.py')
        subprocess.run([sys.executable,str(d/'calcular_independente.py')],check=True,capture_output=True,text=True)
        produzido=json.loads((d/'derivacoes.json').read_text())
        selado=json.loads((OUT/'revisao_cega/derivacoes.json').read_text())
        for chave in ['fontes_literais','linhas_base','casos','verificacoes']:
            if produzido[chave]!=selado[chave]:raise ValueError('Reprodução divergente: '+chave)
        resultado=dict(reproduzido=True,casos=15,partes_comparadas=['fontes_literais','linhas_base','casos','verificacoes'],
                       isolamento='Diretório temporário descartado; originais selados intocados.',
                       campos_nao_comparados='Timestamp de geração e caminhos absolutos das cópias temporárias.',
                       limite='Reprodução verifica determinismo do script independente; não é um terceiro revisor semântico.')
        (OUT/'reproducao_cega.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(resultado,ensure_ascii=False))


if __name__=='__main__':main()
