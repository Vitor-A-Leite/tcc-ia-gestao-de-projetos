"""Coorte aprovada v04; ledger global histórico preservado; importação sem rede."""
from copy import deepcopy
import hashlib,json
from pathlib import Path
from time import monotonic
from piloto_real.runner import preparar,gravar_novo,indisponivel
from piloto_real.ledger import Ledger,Bloqueio,RESERVA,NANO_USD
from piloto_real import MODELO,CONFIG
from piloto_real.transporte import Responses,HTTP,sanitizar
from piloto_real.politica import construir
from formato_local_v04 import LocalV04,ResponsesV04
from formato_local_v04.contrato import VERSAO
from interpretacao_no.contratos import hash_json
from condicoes.baseline import Global
from condicoes.hibrido import executar_h
from avaliacao.execucoes import registrar,validar_manifesto

ID='etapa9-coorte-v04-180s-20261026'
DEADLINE=180

def codigo():
    src=Path(__file__).resolve().parents[1]
    return {str(p.relative_to(src)):hashlib.sha256(p.read_bytes()).hexdigest()for d in ('coorte_v04','formato_local_v04')for p in sorted((src/d).glob('*.py'))}

def historico(db):
    return hash_json({t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall()for t in ('meta','parada','slots','adendos','diagnosticos')}|{'chamadas':db.execute('SELECT * FROM chamadas WHERE id<=15 ORDER BY id').fetchall()})

def preparar_coorte(dados):
    plano,m,casos=preparar(dados);slots=deepcopy(m['execucoes'])
    for s in slots:
        s['execucao_id']=ID+'-'+s['caso_id']+'-'+s['condicao']+'-'+str(s['repeticao'])
        s['versao_protocolo']=ID;s['codigo_hash']=hash_json(dict(historico=plano['codigo'],novo=codigo()))
    m={**m,'execucoes':slots};validar_manifesto(m)
    nos={k:len(c['estado']['entidades'])for k,c in casos.items()}
    limite_passagem=sum(2*n+4 for n in nos.values())
    adendo=dict(id=ID,autorizacao_usuario='Retomar piloto v04, deadline180s, teto acumuladoUS$5;90slots novos;sem etapas10/11',versao_formato_local=VERSAO,slots=[s['execucao_id']for s in slots],manifesto=m,plano_original_hash=hash_json(plano),codigo=codigo(),deadline_chamada_s=180,max_analises_H=8,max_chamadas_H=8,max_tempo_H_s=8*180+60,derivacao_tempo_H='8 chamadas lógicas ×180s +60s processamento local; não amplia nós/chamadas',max_tentativas_agregado=300,teto_nanoUSD=5*NANO_USD,guarda='parar após5timeouts consecutivos na coorte; parar em HTTP/protocolo/integração',nos_por_caso=nos,estimativa_passagem_completa=limite_passagem,estimativa_agregada=15+limite_passagem,ordem=plano['ordem'])
    return plano,adendo,casos

class CarteiraV04(Ledger):
    def __init__(self,pasta,plano,adendo):
        if not (Path(pasta)/'ledger.sqlite').is_file():raise Bloqueio('Carteira original ausente')
        super().__init__(pasta,plano)
        try:
            src=Path(__file__).resolve().parents[1]
            for p,h in plano['codigo'].items():
                if hashlib.sha256((src/p).read_bytes()).hexdigest()!=h:raise Bloqueio('Código histórico alterado')
            self.manifesto_formato=adendo;self.novos={s['execucao_id']:s for s in adendo['manifesto']['execucoes']}
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS coorte_v04 (id TEXT PRIMARY KEY, manifesto TEXT, hash TEXT, historico_hash TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS slots_v04 (id TEXT PRIMARY KEY, estado TEXT, resultado TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS parada_v04 (id INTEGER PRIMARY KEY, motivo TEXT)')
                r=self.db.execute('SELECT hash,historico_hash FROM coorte_v04 WHERE id=?',(ID,)).fetchone()
                if r:
                    if r!=(hash_json(adendo),historico(self.db)):raise Bloqueio('Adendo/código/histórico divergente')
                    self.hist=r[1]
                else:
                    n,total=self.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
                    if (n,total)!=(15,172820515):raise Bloqueio('Estado inicial não revisado')
                    self.hist=historico(self.db)
                    self.db.execute('INSERT INTO coorte_v04 VALUES(?,?,?,?)',(ID,json.dumps(adendo,ensure_ascii=False),hash_json(adendo),self.hist))
                    for s in self.novos:self.db.execute('INSERT INTO slots_v04 VALUES(?,?,NULL)',(s,'pendente'))
        except BaseException:self.close();raise
    def estado(self,s):return self.db.execute('SELECT estado FROM slots_v04 WHERE id=?',(s,)).fetchone()[0]
    def iniciar(self,s):
        with self.db:
            if self.parada():raise Bloqueio('Coorte parada')
            q=self.db.execute("UPDATE slots_v04 SET estado='iniciado' WHERE id=? AND estado='pendente'",(s,))
            if q.rowcount!=1:raise Bloqueio('Sem replay de slot iniciado')
    def salvar(self,s,r):
        with self.db:
            q=self.db.execute("UPDATE slots_v04 SET estado='terminado',resultado=? WHERE id=? AND estado='iniciado'",(json.dumps(r,ensure_ascii=False,allow_nan=False),s))
            if q.rowcount!=1:raise Bloqueio('Resultado já persistido')
    def parada(self):return self.db.execute('SELECT motivo FROM parada_v04').fetchone()
    def parar(self,m):
        with self.db:self.db.execute('INSERT OR IGNORE INTO parada_v04 VALUES(1,?)',(m,))
    def reservar(self,s,h):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if historico(self.db)!=self.hist:raise Bloqueio('Histórico alterado')
            n,total=self.db.execute('SELECT count(*),coalesce(sum(comprometido),0) FROM chamadas').fetchone()
            count=self.db.execute('SELECT count(*) FROM chamadas WHERE slot=?',(s,)).fetchone()[0]
            if s not in self.novos or self.parada() or self.estado(s)!='iniciado':raise Bloqueio('Slot/coorte indisponível')
            if n>=300 or total+RESERVA>5*NANO_USD or count>=(8 if self.novos[s]['condicao']=='H'else 1):raise Bloqueio('Limite agregado/per-slot atingido')
            return self.db.execute('INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES(?,?,?,?)',(s,h,'reservado',RESERVA)).lastrowid
    def desconhecido(self,id,registro):
        super().desconhecido(id,registro)
        erro=registro.get('erro');falha=registro.get('falha_transporte')or{}
        if erro is None:self.parar('Usage/protocolo incompleto; reserva mantida')
        if erro not in (None,'timeout'):self.parar('Falha transporte/integração: '+str(erro)+' '+str(falha))
        self.guarda()
    def guarda(self):
        rows=self.db.execute('SELECT registro FROM chamadas WHERE id>15 ORDER BY id DESC LIMIT 5').fetchall()
        if len(rows)==5 and all(r and json.loads(r).get('erro')=='timeout'for r, in rows):self.parar('Cinco timeouts consecutivos na coorte')
    def resultados(self):return [(s,e,json.loads(r)if r else None)for s,e,r in self.db.execute('SELECT * FROM slots_v04 ORDER BY rowid')]

class TransporteGuardado(Responses):
    def __call__(self,req):
        r=super().__call__(req)
        if r.metadados.get('protocolo_provider')=='divergente':self.ledger.parar('Protocolo divergente')
        return r

class TransporteLocalGuardado(ResponsesV04):
    def __call__(self,req):
        r=super().__call__(req)
        if r.metadados.get('protocolo_provider')=='divergente':self.ledger.parar('Protocolo divergente')
        return r

def executar(dados,pasta,out,*,chave=None,http=None,coletar=False):
    plano,a,casos=preparar_coorte(dados);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with CarteiraV04(pasta,plano,a)as l:
        gravar_novo(out/'adendo.json',a);gravar_novo(out/'manifesto.json',a['manifesto'])
        if not coletar:return dict(estado='preparado_sem_rede',orcamento=l.resumo(),estimativa=a['estimativa_agregada'])
        if http is None and not chave:raise Bloqueio('Credencial local ausente')
        api=http or HTTP(chave);redact=lambda x:sanitizar(x,chave)
        for s in a['manifesto']['execucoes']:
            eid=s['execucao_id'];st=l.estado(eid)
            if st=='terminado':continue
            if st=='iniciado':
                l.salvar(eid,registrar(s,indisponivel(s,'INTERROMPIDO_SEM_REPLAY')));l.parar('Slot anterior interrompido; revisar');break
            n,total=l.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
            if l.parada():break
            if n>=300 or total+RESERVA>5*NANO_USD:l.parar('Limite global impede próximo slot');break
            l.iniciar(eid);inicio=monotonic()
            try:
                c=casos[s['caso_id']]
                if s['condicao']=='H':
                    t=TransporteLocalGuardado(l,eid,api,redator=redact,timeout_s=180)
                    p=construir(c['estado'],c['evento'],execucao_id=eid);p.max_tempo_s=1500
                    i=LocalV04(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180)
                    r=executar_h(c['base'],c['evento_comum'],c['fontes'],c['estado'],c['evento'],c['views']['H'],i,p,vinculo=c['vinculo'],origem='llm_transporte_injetado')
                    r.update(natureza_previsao='condicional_original',registro_operacional=deepcopy(p.registro_operacional),versao_formato_local=VERSAO)
                else:
                    t=TransporteGuardado(l,eid,api,redator=redact,timeout_s=180)
                    r=Global(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180,repetir_transporte=False,origem='llm_transporte_injetado').prever(c['views'][s['condicao']],execucao_id=eid)
                    r['natureza_previsao']='original_global_nao_corrigida'
                r.update(suporte_semantico='nao_auditado',tempo_slot_s=monotonic()-inicio,orcamento_apos_slot=l.resumo())
                reg=redact(registrar(s,r))
            except Exception as exc:
                l.parar('Falha de integração no slot; revisar sem replay')
                reg=registrar(s,indisponivel(s,'FALHA_INTEGRACAO_SANITIZADA'))
            l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg)
            print(json.dumps(dict(slot=eid,estado=reg['resultado']['execucao']['estado'],tempo_s=round(monotonic()-inicio,2),orcamento=l.resumo(),parada=l.parada()),ensure_ascii=False),flush=True)
        if historico(l.db)!=l.hist:raise Bloqueio('Histórico não preservado')
        resumo=dict(coorte=ID,planejado=90,estados={e:sum(st==e for _,st,_ in l.resultados())for e in ('pendente','iniciado','terminado')},parada=l.parada(),orcamento=l.resumo(),historico_preservado=True)
        gravar_novo(out/('resumo-'+hash_json(resumo)[:12]+'.json'),resumo);return resumo
