"""Gera manifesto e ZIP por lista positiva, sem publicar a entrega."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def package():
    files=['COMECE_AQUI.html','ABRIR_DEMONSTRACAO.command','README.md','ACEITE_ETAPA12.md','verificar_pacote.py','servir.py','verificacao_entrega.json']
    for folder,suffixes in [('demonstracao',{'.html','.css','.js','.json'}),('material_tcc',{'.docx','.md'}),('revisao_orientador',{'.docx','.md'})]:
        files.extend(str(p.relative_to(ROOT))for p in sorted((ROOT/folder).glob('*'))if p.suffix in suffixes)
    files.extend(load_path for load_path in json.loads((ROOT/'evidencias/PROVENIENCIA.json').read_text()))
    files.append('evidencias/PROVENIENCIA.json');files=sorted(set(files))
    for rel in files:
        p=ROOT/rel
        if p.is_symlink() or not p.is_file():raise ValueError('Arquivo de entrega ausente ou link: '+rel)
    manifest={'versao':'1.0-etapa12','origem':'registros congelados da etapa 11','arquivos':{p:sha(ROOT/p)for p in files},'nota':'O manifesto exclui a si próprio e o ZIP para evitar autorreferência. Não representa parecer científico.'}
    (ROOT/'MANIFESTO_ENTREGA.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    zip_path=ROOT/'Pacote_orientador.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
        for rel in files+['MANIFESTO_ENTREGA.json']:
            info=zipfile.ZipInfo('etapa12/'+rel,date_time=(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o755 if rel.endswith('.command')else 0o644)<<16;archive.writestr(info,(ROOT/rel).read_bytes())
    receipt={'arquivo':zip_path.name,'sha256':sha(zip_path),'bytes':zip_path.stat().st_size,'arquivos':len(files)+1};(ROOT/'PACOTE_SHA256.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':package()
