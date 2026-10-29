"""Empacota evidências salvas. Biblioteca padrão; sem transporte, chaves ou inferência."""
from pathlib import Path
import argparse,hashlib,json,shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FINAL=ROOT/'TCC_Codigos/outputs/etapa11_final_20261028'
INPUT=ROOT/'TCC_Codigos/data/final/etapa10_v2/inputs'
ET10=ROOT/'TCC_Codigos/outputs/etapa10_auditoria_20261028'

def load(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hjson(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()

def build():
    seal=load(FINAL/'selo_final.json')
    for p,h in seal['artefatos'].items():
        if p.endswith(('/STATUS.md','/PLANO_MESTRE.md')):continue
        if digest(ROOT/p)!=h:raise ValueError('Evidência final alterada: '+p)
    for p,h in load(ET10/'congelamento.json')['artefatos'].items():
        if digest(ROOT/p)!=h:raise ValueError('Congelamento alterado: '+p)
    records=load(FINAL/'registros.json');views=load(ET10/'preparacao_final_v2/views.json')
    state=load(INPUT/'estado_projeto.json');scenarios=load(INPUT/'cenarios.json')['casos']
    if len(records)!=9:raise ValueError('Nove execuções obrigatórias')
    for r in records:
        if hjson(r['resultado'])!=r['resultado_hash']:raise ValueError('Resultado divergente')
    labels={'k_1671298a5a':'Duas atividades mais longas','k_c23705f4ea':'Prazo conhecido e taxa desconhecida','k_ec2826cc2a':'Crédito sem mudança de prazo'}
    cases=[]
    for event in sorted(scenarios,key=lambda x:x['caso_id']):
        cid=event['caso_id'];rr={r['metadados']['condicao']:r for r in records if r['metadados']['caso_id']==cid}
        if set(rr)!={'B','H','T'}:raise ValueError('Pareamento incompleto')
        cases.append(dict(id=cid,title=labels[cid],event=event,records=rr,views=views[cid]))
    bundle=dict(version='1.0-etapa12-replay-salvo',project=state,cases=cases,
        metrics=load(FINAL/'metricas_auditadas.json'),operational=load(FINAL/'operacional.json'),
        budget=load(FINAL/'auditoria_uso.json'),audits=load(FINAL/'auditoria_semantica.json'),
        failures=load(FINAL/'falhas_formato.json'),references=load(ROOT/'TCC_Codigos/data/final/etapa10_v2/referencias/referencias_avaliacao.json'),
        source_seal_sha256=digest(FINAL/'selo_final.json'),paid_calls_in_stage12=0)
    sources={}
    names=['RELATORIO.md','manifesto.json','adendo_aprovado.json','registros.json','metricas_auditadas.json','normalizacao.json','operacional.json','auditoria_uso.json','auditoria_semantica.json','auditoria_local_H.json','falhas_formato.json','integridade_depois.json','recontagem_metricas.json','selo_final.json','verificacao_final.json']
    for name in names:
        src=FINAL/name;dst=HERE/'evidencias/etapa11'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);sources[str(dst.relative_to(HERE))]=dict(origem=str(src.relative_to(ROOT)),sha256=digest(src))
    for src in sorted(INPUT.rglob('*')):
        if not src.is_file():continue
        dst=HERE/'evidencias/inputs'/src.relative_to(INPUT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);sources[str(dst.relative_to(HERE))]=dict(origem=str(src.relative_to(ROOT)),sha256=digest(src))
    for src,dst in [(ET10/'preparacao_final_v2/views.json',HERE/'evidencias/views.json'),(ROOT/'TCC_Codigos/data/final/etapa10_v2/referencias/referencias_avaliacao.json',HERE/'evidencias/referencias.json'),(ROOT/'TCC_Codigos/docs/desenvolvimento/ETAPA_10_PROTOCOLO_FINAL.md',HERE/'evidencias/protocolo_final.md')]:
        shutil.copyfile(src,dst);sources[str(dst.relative_to(HERE))]=dict(origem=str(src.relative_to(ROOT)),sha256=digest(src))
    for name in ['NOTAS.md','derivacoes.json','calcular.py','selo.json']:
        src=ET10/'revisao_final_v2_cega'/name;dst=HERE/'evidencias/revisao_cega'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);sources[str(dst.relative_to(HERE))]=dict(origem=str(src.relative_to(ROOT)),sha256=digest(src))
    (HERE/'demonstracao').mkdir(exist_ok=True)
    serialized=json.dumps(bundle,ensure_ascii=False,allow_nan=False,separators=(',',':'))
    (HERE/'demonstracao/dados.js').write_text('window.EXPERIMENTO = '+serialized.replace('<','\\u003c')+';\n')
    (HERE/'demonstracao/dados.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    (HERE/'evidencias/PROVENIENCIA.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(casos=3,execucoes=9,analises_H=sum(len(c['records']['H']['resultado']['rastro_orquestracao'])for c in cases),copias_verificaveis=len(sources),chamadas_pagas=0)))

if __name__=='__main__':build()
