"""Nova coorte v06 autorizada em 27/10; mesma carteira acumulada, sem replay."""
from copy import deepcopy
from pathlib import Path
import hashlib,json,sqlite3,subprocess
from piloto_real.runner import preparar,gravar_novo,indisponivel
from piloto_real.ledger import Ledger,Bloqueio,RESERVA,NANO_USD
from piloto_real import MODELO,CONFIG
from interpretacao_no.contratos import hash_json
from hibrido_v06.contratos import VERSAO
from hibrido_v06.politica import POLITICA
from hibrido_v06.avaliacao import validar_manifesto,registrar
ID='etapa9-v06-90-BHT-R2-20261027'
AUTORIZACAO='Pode integrar a v6 e rodar um novo piloto, mantendo o limite acumulado de US$ 5. Depois me mostre a comparação com a v5.'

def codigo():
    src=Path(__file__).resolve().parents[1]
    return {str(p.relative_to(src)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(src.rglob('*.py'))}

def historico(db):
    tabelas=[r[0]for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%v06%'")]
    return hash_json({t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() if t!='chamadas' else db.execute('SELECT * FROM chamadas WHERE id<=510 ORDER BY id').fetchall()for t in tabelas})

def preparar_coorte(dados):
    plano,m,casos=preparar(dados);m=deepcopy(m);m['schema_version']='3.0-manifesto-h06'
    for s in m['execucoes']:
        s['execucao_id']=ID+'-'+s['caso_id']+'-'+s['condicao']+'-'+str(s['repeticao'])
        s['codigo_hash']=hash_json(dict(antigo=plano['codigo'],novo=codigo()))
        s['versao_protocolo']=POLITICA if s['condicao']=='H'else ID
    validar_manifesto(m)
    a=dict(id=ID,autorizacao_usuario=AUTORIZACAO,data_local='2026-10-27 America/Sao_Paulo',origem_autorizacao='mensagem direta do usuário nesta conversa',versao_formato_local=VERSAO,manifesto=m,slots=[s['execucao_id']for s in m['execucoes']],codigo=codigo(),modelo=MODELO,configuracao=CONFIG,stream=True,deadline_total_chamada_s=180,max_entrada_oficial=16000,max_saida_total=25000,max_analises_H=8,max_chamadas_H=8,max_tempo_H_s=1500,retries=0,fallback=False,max_chamadas_novas=300,max_tentativas_agregado=810,teto_nanoUSD=5*NANO_USD,base_tentativas=510,base_comprometido_nanoUSD=2096607180,carteira='etapa9_piloto_real_aprovado_20261026/ledger.sqlite',guarda='USD acumulado prevalece; reservas desconhecidas preservadas; erro HTTP/protocolo/incomplete interrompe;5timeouts consecutivos interrompem',ordem=plano['ordem'],alteracao_cientifica='H v06 aprovado; B/T preservados; coorte nova sem reclassificação v04')
    return plano,a,casos

class CarteiraV06(Ledger):
    def __init__(self,pasta,plano,a):
        if not(Path(pasta)/'ledger.sqlite').is_file():raise Bloqueio('Carteira acumulada original obrigatória')
        super().__init__(pasta,plano)
        try:
            if a['codigo']!=codigo() or a['id']!=ID:raise Bloqueio('Código/adendo v06 divergentes')
            validar_manifesto(a['manifesto'])
            self.manifesto_formato=a;self.novos={s['execucao_id']:s for s in a['manifesto']['execucoes']}
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS coorte_v06(id TEXT PRIMARY KEY,adendo TEXT,hash TEXT,historico_hash TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS slots_v06(id TEXT PRIMARY KEY,estado TEXT,resultado TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS parada_v06(id INTEGER PRIMARY KEY,motivo TEXT)')
                antigo=self.db.execute('SELECT hash,historico_hash FROM coorte_v06 WHERE id=?',(ID,)).fetchone()
                self.hist=historico(self.db)
                if antigo:
                    if antigo!=(hash_json(a),self.hist):raise Bloqueio('Histórico/adendo alterados')
                else:
                    n,t=self.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
                    if(n,t)!=(510,2096607180):raise Bloqueio('Estado anterior não corresponde ao aprovado')
                    if self.db.execute("SELECT count(*) FROM slots_v05 WHERE estado='terminado'").fetchone()[0] != 90:
                        raise Bloqueio('Piloto v05 ainda não está encerrado')
                    self.db.execute('INSERT INTO coorte_v06 VALUES(?,?,?,?)',(ID,json.dumps(a,ensure_ascii=False),hash_json(a),self.hist))
                    self.db.executemany('INSERT INTO slots_v06 VALUES(?,?,NULL)',[(s,'pendente')for s in self.novos])
        except BaseException:self.close();raise
    def conferir(self):
        if historico(self.db)!=self.hist:raise Bloqueio('Histórico anterior alterado')
        if codigo()!=self.manifesto_formato['codigo']:raise Bloqueio('Código v06 alterado durante coleta')
    def estado(self,s):return self.db.execute('SELECT estado FROM slots_v06 WHERE id=?',(s,)).fetchone()[0]
    def iniciar(self,s):
        self.conferir()
        with self.db:
            if self.parada():raise Bloqueio('Coorte v06 parada')
            q=self.db.execute("UPDATE slots_v06 SET estado='iniciado' WHERE id=? AND estado='pendente'",(s,))
            if q.rowcount!=1:raise Bloqueio('Sem replay de slot')
    def salvar(self,s,r):
        self.conferir()
        with self.db:
            q=self.db.execute("UPDATE slots_v06 SET estado='terminado',resultado=? WHERE id=? AND estado='iniciado'",(json.dumps(r,ensure_ascii=False,allow_nan=False),s))
            if q.rowcount!=1:raise Bloqueio('Resultado já persistido')
    def parada(self):return self.db.execute('SELECT motivo FROM parada_v06').fetchone()
    def parar(self,m):
        with self.db:self.db.execute('INSERT OR IGNORE INTO parada_v06 VALUES(1,?)',(m,))
    def reservar(self,s,h):
        self.conferir()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            n,t=self.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
            por=self.db.execute('SELECT count(*) FROM chamadas WHERE slot=?',(s,)).fetchone()[0]
            if s not in self.novos or self.parada() or self.estado(s)!='iniciado':raise Bloqueio('Slot indisponível')
            if n>=810 or n-510>=300 or t+RESERVA>5*NANO_USD or por>=(8 if self.novos[s]['condicao']=='H'else 1):raise Bloqueio('Teto global/per-slot atingido')
            return self.db.execute('INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES(?,?,?,?)',(s,h,'reservado',RESERVA)).lastrowid
    def desconhecido(self,id,r):
        super().desconhecido(id,r)
        if r.get('erro') not in ('timeout',):self.parar('Falha transporte/protocolo: '+str(r.get('erro','usage incompleto')))
        ult=self.db.execute('SELECT registro FROM chamadas WHERE id>510 ORDER BY id DESC LIMIT 5').fetchall()
        if len(ult)==5 and all(v and json.loads(v).get('erro')=='timeout'for v, in ult):self.parar('Cinco timeouts consecutivos v06')
    def resultados(self):return[(s,e,json.loads(r)if r else None)for s,e,r in self.db.execute('SELECT * FROM slots_v06 ORDER BY rowid')]

def snapshot(root,pasta,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if(out/'integridade_antes.json').exists():return
    root=Path(root)
    paths=[p for d in ('src','data','tests','docs','outputs')
           for p in (root/'TCC_Codigos'/d).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts
           and p.suffix not in ('.pyc',) and out not in p.parents]
    gravar_novo(out/'integridade_antes.json',{
        str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths})
    src=sqlite3.connect('file:'+str((Path(pasta)/'ledger.sqlite').resolve())+'?mode=ro',uri=True)
    target=sqlite3.connect(str(out/'ledger_antes.sqlite'));src.backup(target);target.close();src.close()

def executar(dados,pasta,out,*,chave=None,http=None,coletar=False):
    from time import monotonic
    from piloto_real.transporte import sanitizar
    from condicoes.baseline import Global
    from hibrido_v06 import construir,LocalV06,executar_h
    from .transporte import ResponsesSSE,LocalSSE
    from retomada_v04_sse.http import HTTPStreaming
    plano,a,casos=preparar_coorte(dados);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    gravar_novo(out/'adendo_aprovado.json',a);gravar_novo(out/'manifesto.json',a['manifesto'])
    if not coletar:return dict(estado='preparado_offline',slots=90,adendo_hash=hash_json(a))
    if http is None and not chave:raise Bloqueio('Credencial local ausente')
    with CarteiraV06(pasta,plano,a)as l:
        api=http or HTTPStreaming(chave);redact=lambda x:sanitizar(x,chave)
        for s in a['manifesto']['execucoes']:
            eid=s['execucao_id'];st=l.estado(eid)
            if st=='terminado':continue
            if st=='iniciado':
                r=indisponivel(s,'INTERROMPIDO_SEM_REPLAY');reg=registrar(s,r);l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg);l.parar('Slot iniciado anteriormente; sem replay');break
            if l.parada():break
            n,t=l.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
            if n>=810 or t+RESERVA>5*NANO_USD:l.parar('Teto acumulado impede próximo slot');break
            l.iniciar(eid);inicio=monotonic()
            try:
                c=casos[s['caso_id']]
                if s['condicao']=='H':
                    t=LocalSSE(l,eid,api,redator=redact,timeout_s=180)
                    p=construir(c['estado'],c['evento'],execucao_id=eid)
                    i=LocalV06(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180)
                    r=executar_h(c['base'],c['evento_comum'],c['fontes'],c['estado'],c['evento'],c['views']['H'],i,p,vinculo=c['vinculo'],origem='llm_transporte_injetado')
                    r.update(registro_operacional=deepcopy(p.registro_operacional),versao_formato_local=VERSAO,natureza_previsao='condicional_original_v06')
                else:
                    t=ResponsesSSE(l,eid,api,redator=redact,timeout_s=180)
                    r=Global(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180,repetir_transporte=False,origem='llm_transporte_injetado').prever(c['views'][s['condicao']],execucao_id=eid)
                    r['natureza_previsao']='original_global_nao_corrigida'
                r.update(suporte_semantico='nao_auditado',tempo_slot_s=monotonic()-inicio,orcamento_apos_slot=l.resumo(),adendo_v06_hash=hash_json(a))
            except Exception:
                l.parar('Falha integração v06; sem retry');r=indisponivel(s,'FALHA_INTEGRACAO_V06_SANITIZADA')
            reg=redact(registrar(s,r));l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg)
            print(json.dumps(dict(slot=eid,estado=r['execucao']['estado'],tempo_s=round(monotonic()-inicio,2),orcamento=l.resumo(),parada=l.parada()),ensure_ascii=False),flush=True)
        l.conferir();res=dict(coorte=ID,estados={e:sum(st==e for _,st,_ in l.resultados())for e in ('pendente','iniciado','terminado')},parada=l.parada(),orcamento=l.resumo(),historico_preservado=True)
        gravar_novo(out/('resumo-'+hash_json(res)[:12]+'.json'),res);return res
