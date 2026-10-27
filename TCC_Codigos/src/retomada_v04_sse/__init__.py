"""R2 SSE: preparação offline. Ativação futura exige revisão do coordenador."""
from copy import deepcopy
from pathlib import Path
import fcntl,hashlib,json,sqlite3
from piloto_real.ledger import Bloqueio,RESERVA,NANO_USD
from piloto_real.runner import gravar_novo
from coorte_v04 import CarteiraV04,preparar_coorte
from interpretacao_no.contratos import hash_json
ID='etapa9-v04-sse-r2-70-20261026'
TRANSPORTE='responses-sse-r2'
TABELAS=('meta','slots','parada','adendos','diagnosticos','coorte_v04','parada_v04','retomadas_v04','paradas_retomada_v04')
def codigo():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(Path(__file__).parent.glob('*.py'))}
def ancora(db,permitidos):
    return hash_json({t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall()for t in TABELAS}|dict(chamadas1a71=db.execute('SELECT * FROM chamadas WHERE id<=71 ORDER BY id').fetchall(),terminados20=[r for r in db.execute('SELECT * FROM slots_v04 ORDER BY rowid')if r[0]not in permitidos]))
def preparar_offline(dados,pasta,out):
    plano,a,casos=preparar_coorte(dados);pasta=Path(pasta);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if not(pasta/'ledger.sqlite').is_file():raise Bloqueio('Carteira ausente')
    with(pasta/'lote.lock').open()as lock:
        try:fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
        except BlockingIOError:raise Bloqueio('Coletor ativo')from None
        db=sqlite3.connect('file:'+str((pasta/'ledger.sqlite').resolve())+'?mode=ro',uri=True)
        try:
            rows=db.execute('SELECT id,estado FROM slots_v04 ORDER BY rowid').fetchall();pending=[s for s,e in rows if e=='pendente']
            if len(pending)!=70 or sum(e=='terminado'for _,e in rows)!=20 or any(e=='iniciado'for _,e in rows):raise Bloqueio('Estado não corresponde a20/90parados')
            if db.execute('SELECT count(*) FROM chamadas').fetchone()[0]!=71:raise Bloqueio('Contagem anterior mudou')
            slots={s['execucao_id']:s for s in a['manifesto']['execucoes']};n=sum(a['nos_por_caso'][slots[s]['caso_id']]if slots[s]['condicao']=='H'else 1 for s in pending)
            total=db.execute('SELECT sum(comprometido) FROM chamadas').fetchone()[0]
            if (n,total)!=(219,430331335)or 71+n>300 or total+n*RESERVA>5*NANO_USD:raise Bloqueio('Limites revisados incompatíveis')
            proposta=dict(id=ID,estado='PREPARADO_OFFLINE_NAO_ATIVADO',origem='Solicitação técnica do coordenador para revisão; não é nova aprovação humana',codigo=codigo(),coorte_original_hash=hash_json(a),transporte=TRANSPORTE,slots=pending,slots_hash=hash_json(pending),ancora=ancora(db,pending),deadline_total_s=180,retries=0,geracao_diff={'stream':True},contagem='JSON inalterado; mesmos model/input/reasoning/text',max_chamadas_novas=n,max_agregado=71+n,comprometido_anterior_nanoUSD=total,reserva_adicional_max_nanoUSD=n*RESERVA,comprometido_max_nanoUSD=total+n*RESERVA,teto_nanoUSD=5*NANO_USD,guardas='mesmas guardas;failed/incomplete/SSEerro também interrompem sem retry',fontes_oficiais=['https://developers.openai.com/api/docs/guides/streaming-responses','https://developers.openai.com/api/reference/resources/responses/streaming-events'])
            gravar_novo(out/'adendo_r2_offline.json',proposta)
            return proposta
        finally:db.close()

class CarteiraSSE(CarteiraV04):
    """Só instanciar em cópia nos testes ou após revisão explícita para ativação."""
    def __init__(self,pasta,plano,a,proposta,*,liberacao_coordenador=False):
        if not liberacao_coordenador:raise Bloqueio('R2aguarda revisão do coordenador; não ativar')
        self.ativa=False;super().__init__(pasta,plano,a)
        try:
            self.permitidos=tuple(proposta['slots']);self.proposta=deepcopy(proposta)
            if len(set(self.permitidos))!=70 or len(self.permitidos)!=70 or hash_json(list(self.permitidos))!=proposta['slots_hash']or proposta['codigo']!=codigo()or proposta['id']!=ID or proposta['coorte_original_hash']!=hash_json(a):raise Bloqueio('Lista/código/adendo divergentes')
            limites=dict(max_chamadas_novas=219,max_agregado=290,comprometido_anterior_nanoUSD=430331335,reserva_adicional_max_nanoUSD=3613500000,comprometido_max_nanoUSD=4043831335,teto_nanoUSD=5000000000,deadline_total_s=180,retries=0,geracao_diff={'stream':True},transporte=TRANSPORTE)
            if any(proposta.get(k)!=v for k,v in limites.items()):raise Bloqueio('Parâmetros/limites do adendo divergentes')
            self.retomada=dict(proposta_hash=hash_json(proposta),id=ID,codigo=codigo(),transporte=TRANSPORTE,decisao='Ativação técnica após revisão do coordenador, dentro da autorização humana original dos90slots/180s/US$5')
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS retomadas_sse_r2 (id TEXT PRIMARY KEY,adendo TEXT,hash TEXT,ancora TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS paradas_sse_r2 (seq INTEGER PRIMARY KEY AUTOINCREMENT,retomada TEXT,motivo TEXT)')
                atual=ancora(self.db,self.permitidos)
                if atual!=proposta['ancora']:raise Bloqueio('Chamadas1–71/20terminados/paradas alterados')
                old=self.db.execute('SELECT hash,ancora FROM retomadas_sse_r2 WHERE id=?',(ID,)).fetchone()
                if old:
                    if old!=(hash_json(self.retomada),atual):raise Bloqueio('Retomada SSE divergente')
                else:
                    pending=[s for s,e in self.db.execute('SELECT id,estado FROM slots_v04 ORDER BY rowid')if e=='pendente']
                    n,total=self.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
                    if pending!=list(self.permitidos)or(n,total)!=(71,430331335):raise Bloqueio('Estado inicial mudou')
                    self.db.execute('INSERT INTO retomadas_sse_r2 VALUES(?,?,?,?)',(ID,json.dumps(self.retomada,ensure_ascii=False),hash_json(self.retomada),atual))
                self.ativa=True
        except BaseException:self.close();raise
    def parada(self):
        if not self.ativa:return super().parada()
        return self.db.execute('SELECT motivo FROM paradas_sse_r2 WHERE retomada=? ORDER BY seq LIMIT 1',(ID,)).fetchone()
    def parar(self,m):
        if not self.ativa:return super().parar(m)
        with self.db:
            if not self.parada():self.db.execute('INSERT INTO paradas_sse_r2(retomada,motivo) VALUES(?,?)',(ID,m))
    def conferir(self):
        if ancora(self.db,self.permitidos)!=self.proposta['ancora']:raise Bloqueio('Âncoras históricas alteradas')
    def iniciar(self,s):
        if s not in self.permitidos:raise Bloqueio('Não repetir20slots')
        self.conferir();return super().iniciar(s)
    def reservar(self,s,h):
        if s not in self.permitidos:raise Bloqueio('Fora dos70IDs')
        self.conferir();return super().reservar(s,h)
    def salvar(self,s,r):
        if s not in self.permitidos:raise Bloqueio('Não editar20terminados')
        self.conferir();return super().salvar(s,r)

def vincular_resultado(r,carteira):
    novo=deepcopy(r);novo['adendo_transporte_sse']=dict(id=ID,hash=hash_json(carteira.retomada),codigo=codigo(),transporte=TRANSPORTE);return novo

def executar(dados,pasta,out,proposta=None,*,chave=None,http=None,coletar=False,liberacao_coordenador=False):
    """Sem ativação/rede no preparo; coleta somente após liberação explícita."""
    from time import monotonic
    from piloto_real.transporte import sanitizar
    from piloto_real.runner import indisponivel
    from piloto_real import MODELO,CONFIG
    from piloto_real.politica import construir
    from formato_local_v04 import LocalV04
    from condicoes.baseline import Global
    from condicoes.hibrido import executar_h
    from avaliacao.execucoes import registrar
    from .transporte import ResponsesSSE,LocalSSE
    from .http import HTTPStreaming
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if not coletar:return preparar_offline(dados,pasta,out)
    if not liberacao_coordenador:raise Bloqueio('Não ativar R2antes da revisão do coordenador')
    if http is None and not chave:raise Bloqueio('Credencial local ausente')
    proposta=proposta or json.loads((out/'adendo_r2_offline.json').read_text())
    plano,a,casos=preparar_coorte(dados)
    with CarteiraSSE(pasta,plano,a,proposta,liberacao_coordenador=True)as l:
        gravar_novo(out/'ativacao_r2.json',l.retomada);gravar_novo(out/'manifesto.json',a['manifesto'])
        api=http or HTTPStreaming(chave);redact=lambda x:sanitizar(x,chave)
        for eid in l.permitidos:
            s=l.novos[eid];st=l.estado(eid)
            if st=='terminado':continue
            if st=='iniciado':
                reg=registrar(s,vincular_resultado(indisponivel(s,'INTERROMPIDO_SEM_REPLAY'),l));l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg)
                l.parar('Slot SSE anterior iniciado; não repetir');break
            if l.parada():break
            n,total=l.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
            if n>=300 or total+RESERVA>5*NANO_USD:l.parar('Limite global impede próximo slot SSE');break
            l.iniciar(eid);inicio=monotonic()
            try:
                c=casos[s['caso_id']]
                if s['condicao']=='H':
                    t=LocalSSE(l,eid,api,redator=redact,timeout_s=180)
                    p=construir(c['estado'],c['evento'],execucao_id=eid);p.max_tempo_s=1500
                    i=LocalV04(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180)
                    r=executar_h(c['base'],c['evento_comum'],c['fontes'],c['estado'],c['evento'],c['views']['H'],i,p,vinculo=c['vinculo'],origem='llm_transporte_injetado')
                    r.update(natureza_previsao='condicional_original',registro_operacional=deepcopy(p.registro_operacional),versao_formato_local='4.0-formato-local')
                else:
                    t=ResponsesSSE(l,eid,api,redator=redact,timeout_s=180)
                    r=Global(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180,repetir_transporte=False,origem='llm_transporte_injetado').prever(c['views'][s['condicao']],execucao_id=eid)
                    r['natureza_previsao']='original_global_nao_corrigida'
                r.update(suporte_semantico='nao_auditado',tempo_slot_s=monotonic()-inicio,orcamento_apos_slot=l.resumo())
            except Exception:
                l.parar('Falha de integração SSE no slot; revisar sem retry');r=indisponivel(s,'FALHA_INTEGRACAO_SSE_SANITIZADA')
            reg=redact(registrar(s,vincular_resultado(r,l)));l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg)
            print(json.dumps(dict(slot=eid,estado=r['execucao']['estado'],transporte=TRANSPORTE,tempo_s=round(monotonic()-inicio,2),orcamento=l.resumo(),parada=l.parada()),ensure_ascii=False),flush=True)
        l.conferir()
        resumo=dict(coorte=a['id'],retomada=ID,transporte=TRANSPORTE,planejado=90,estados={e:sum(st==e for _,st,_ in l.resultados())for e in ('pendente','iniciado','terminado')},parada=l.parada(),orcamento=l.resumo(),ancoras_preservadas=True)
        gravar_novo(out/('resumo-'+hash_json(resumo)[:12]+'.json'),resumo);return resumo
