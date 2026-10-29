"""Audita projeção e imutabilidade contra o repositório original, sem API."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,runpy,socket
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hjson(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()
def check(x,msg):
    if not x:raise ValueError(msg)
def blocked(*a,**kw):raise RuntimeError('Rede proibida nesta auditoria')
socket.socket=blocked;socket.create_connection=blocked
baseline=load(HERE/'integridade_antes.json')
check(sha(ROOT/baseline['carteira'])==baseline['carteira_sha256'],'Carteira alterada')
immutable={p:h for p,h in baseline['artefatos11'].items() if not p.endswith(('/STATUS.md','/PLANO_MESTRE.md'))}
for p,h in immutable.items():check(sha(ROOT/p)==h,'Etapa 11 alterada: '+p)
freeze=load(ROOT/'TCC_Codigos/outputs/etapa10_auditoria_20261028/congelamento.json')['artefatos']
for p,h in freeze.items():check(sha(ROOT/p)==h,'Congelamento alterado: '+p)
before={p:sha(HERE/p) for p in ['demonstracao/dados.js','demonstracao/dados.json','evidencias/PROVENIENCIA.json']}
runpy.run_path(str(HERE/'construir.py'),run_name='__main__')
check(before=={p:sha(HERE/p)for p in before},'Construção não determinística')
D=load(HERE/'demonstracao/dados.json');records=load(HERE/'evidencias/etapa11/registros.json')
check(len(D['cases'])==3 and len(records)==9,'Pareamento incorreto')
original={r['metadados']['execucao_id']:r for r in records}
local=0
for c in D['cases']:
    check(set(c['records'])=={'B','H','T'},'Condições ausentes')
    for r in c['records'].values():
        check(r==original[r['metadados']['execucao_id']],'Resultado substituído')
        check(hjson(r['resultado'])==r['resultado_hash'],'Hash de resultado divergente')
    h=c['records']['H']['resultado'];trace=h['rastro_orquestracao'];local+=len(trace)
    check(len(trace)==6 and len(h['livro_parcelas'])==6,'Rastro ou livro incompleto')
    check(len({p['parcela_id']for p in h['livro_parcelas']})==6,'Parcela duplicada')
check(local==18,'Número de análises H incorreto')
unknown=D['cases'][1]['records'];check(unknown['H']['resultado']['delta_centavos']['valor'] is None,'Indeterminação imputada')
check(unknown['H']['resultado']['delta_centavos']['limites']=={'inferior':0,'superior':None},'Limites alterados')
check(all(unknown[x]['resultado']['execucao']['estado']=='erro'for x in ['B','T']),'Falha recuperada')
for key,file in [('metrics','metricas_auditadas.json'),('budget','auditoria_uso.json'),('operational','operacional.json'),('audits','auditoria_semantica.json'),('failures','falhas_formato.json')]:check(D[key]==load(HERE/'evidencias/etapa11'/file),'Projeção alterada: '+key)
check(D['budget']['acumulado_nanoUSD']==4567653865 and D['paid_calls_in_stage12']==0,'Orçamento divergente')
js=(HERE/'demonstracao/dados.js').read_text();check(json.loads(js.removeprefix('window.EXPERIMENTO = ').rstrip(';\n'))==D,'JSON e JS divergem')
origins=load(HERE/'evidencias/PROVENIENCIA.json')
for p,ref in origins.items():check(sha(HERE/p)==ref['sha256']==sha(ROOT/ref['origem']),'Cópia divergente: '+p)
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ['src','href']and value and not value.startswith('#'):self.links.append(value)
links=0
for p in [HERE/'COMECE_AQUI.html',HERE/'demonstracao/index.html']:
    parser=Links();parser.feed(p.read_text())
    for ref in parser.links:
        check('://' not in ref and not ref.startswith('//'),'Dependência remota: '+ref)
        target=(p.parent/ref).resolve();check(HERE in target.parents and target.is_file(),'Link quebrado: '+ref);links+=1
check(sha(ROOT/baseline['carteira'])==baseline['carteira_sha256'],'Carteira alterada após auditoria')
report={'ok':True,'casos':3,'execucoes_originais':9,'analises_H':local,'copias_identicas':len(origins),'congelamento_etapa10':len(freeze),'artefatos_etapa11_preservados':len(immutable),'carteira_bytes_identicos':True,'carteira_sha256':baseline['carteira_sha256'],'construcao_deterministica_sem_rede':True,'links_locais_validos':links,'chamadas_pagas_etapa12':0,'compromisso_acumulado_nanoUSD':4567653865,'saldo_nanoUSD':432346135,'revisao_humana':'pendente'}
(HERE/'verificacao_entrega.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
