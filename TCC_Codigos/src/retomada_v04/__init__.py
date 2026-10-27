"""Retomada operacional append-only: somente73slots pendentes aprovados."""
from copy import deepcopy
from pathlib import Path
import hashlib,json
from time import monotonic
from coorte_v04 import (CarteiraV04,preparar_coorte,historico,TransporteGuardado,TransporteLocalGuardado,
                        gravar_novo,indisponivel,MODELO,CONFIG,construir,LocalV04,executar_h,Global,registrar,VERSAO)
from piloto_real.ledger import Bloqueio,RESERVA,NANO_USD
from piloto_real.transporte import sanitizar
from interpretacao_no.contratos import hash_json
from .http import HTTPSeguro
ID='etapa9-retomada-v04-73-20261026-r1'

def codigo():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(Path(__file__).parent.glob('*.py'))}
def ancora(db,permitidos):
    return hash_json(dict(chamadas=db.execute('SELECT * FROM chamadas WHERE id<=61 ORDER BY id').fetchall(),terminados=[r for r in db.execute('SELECT * FROM slots_v04 ORDER BY rowid')if r[0]not in permitidos],coorte=db.execute('SELECT * FROM coorte_v04').fetchall(),parada=db.execute('SELECT * FROM parada_v04').fetchall()))

class CarteiraRetomada(CarteiraV04):
    def __init__(self,pasta,plano,adendo,proposta):
        self.ativa=False
        super().__init__(pasta,plano,adendo)
        try:
            self.permitidos=tuple(proposta['slots_pendentes'])
            if len(self.permitidos)!=73 or len(set(self.permitidos))!=73 or hash_json(list(self.permitidos))!=proposta['slots_pendentes_hash']:raise Bloqueio('Lista73incompatível')
            self.retomada=dict(id=ID,coorte=adendo['id'],codigo=codigo(),proposta_hash=hash_json(proposta),slots=list(self.permitidos),decisao='Decisão operacional do coordenador: ativar73pendentes após revisão de uma falha http_indisponivel indeterminada; não é nova fala/aprovação do usuário',autorizacao_humana_origem='Autorização existente para90slotsv04,180s,teto acumuladoUS$5;sem etapas10/11',sem_retry=True,deadline_s=180,mesmos_prompts_e_parametros=True,max_novas_chamadas_passagem=229,max_agregado_estimado=290,max_comprometido_nanoUSD=4159002675,telemetria='somente fase enum,classe allowlisted e errno inteiro; nenhum conteúdo/headers/mensagem de exceção')
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS retomadas_v04 (id TEXT PRIMARY KEY,adendo TEXT,hash TEXT,ancora TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS paradas_retomada_v04 (seq INTEGER PRIMARY KEY AUTOINCREMENT,retomada TEXT,motivo TEXT)')
                old=self.db.execute('SELECT hash,ancora FROM retomadas_v04 WHERE id=?',(ID,)).fetchone()
                atual=ancora(self.db,self.permitidos)
                if old:
                    if old!=(hash_json(self.retomada),atual):raise Bloqueio('Retomada/código/originais divergentes')
                else:
                    for t,h in proposta['tabelas_congeladas_hash'].items():
                        if hash_json(self.db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall())!=h:raise Bloqueio('Estado revisado mudou')
                    pending=[s for s,e in self.db.execute('SELECT id,estado FROM slots_v04 ORDER BY rowid')if e=='pendente']
                    if pending!=list(self.permitidos):raise Bloqueio('Conjunto/ordem pendentes mudou')
                    n,total=self.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
                    estimativa=sum(adendo['nos_por_caso'][self.novos[s]['caso_id']]if self.novos[s]['condicao']=='H'else 1 for s in self.permitidos)
                    if (n,total,estimativa)!=(61,380502675,229)or n+estimativa!=290 or total+estimativa*RESERVA!=4159002675:raise Bloqueio('Limites revisados mudaram')
                    self.db.execute('INSERT INTO retomadas_v04 VALUES(?,?,?,?)',(ID,json.dumps(self.retomada,ensure_ascii=False),hash_json(self.retomada),atual))
                self.ancora=atual;self.ativa=True
        except BaseException:self.close();raise
    def parada(self):
        if not self.ativa:return super().parada()
        return self.db.execute('SELECT motivo FROM paradas_retomada_v04 WHERE retomada=? ORDER BY seq LIMIT 1',(ID,)).fetchone()
    def parar(self,m):
        if not self.ativa:return super().parar(m)
        with self.db:
            if not self.parada():self.db.execute('INSERT INTO paradas_retomada_v04(retomada,motivo) VALUES(?,?)',(ID,m))
    def conferir(self):
        if ancora(self.db,self.permitidos)!=self.ancora:raise Bloqueio('Chamadas1–61/17terminados/parada alterados')
    def iniciar(self,s):
        if s not in self.permitidos:raise Bloqueio('Fora dos73pendentes autorizados')
        self.conferir();return super().iniciar(s)
    def reservar(self,s,h):
        if s not in self.permitidos:raise Bloqueio('Fora da lista73')
        self.conferir();return super().reservar(s,h)
    def salvar(self,s,r):
        if s not in self.permitidos:raise Bloqueio('Não editar17terminados')
        self.conferir();return super().salvar(s,r)

def executar(dados,pasta,out,proposta,*,chave=None,http=None,coletar=False):
    plano,a,casos=preparar_coorte(dados);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with CarteiraRetomada(pasta,plano,a,proposta)as l:
        gravar_novo(out/'adendo_retomada.json',l.retomada);gravar_novo(out/'manifesto.json',a['manifesto'])
        if not coletar:return dict(estado='preparado_sem_rede',orcamento=l.resumo(),estimativa=l.retomada['max_agregado_estimado'])
        if http is None and not chave:raise Bloqueio('Credencial local ausente')
        api=http or HTTPSeguro(chave);redact=lambda x:sanitizar(x,chave)
        for s in a['manifesto']['execucoes']:
            eid=s['execucao_id']
            if eid not in l.permitidos:continue
            st=l.estado(eid)
            if st=='terminado':continue
            if st=='iniciado':
                r=indisponivel(s,'INTERROMPIDO_SEM_REPLAY');r['adendo_retomada']=dict(id=ID,hash=hash_json(l.retomada),codigo=codigo());l.salvar(eid,registrar(s,r));l.parar('Slot anterior interrompido; revisar');break
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
                r.update(adendo_retomada=dict(id=ID,hash=hash_json(l.retomada),codigo=codigo()),suporte_semantico='nao_auditado',tempo_slot_s=monotonic()-inicio,orcamento_apos_slot=l.resumo())
                reg=redact(registrar(s,r))
            except Exception as exc:
                l.parar('Falha de integração no slot; revisar sem replay')
                reg=registrar(s,indisponivel(s,'FALHA_INTEGRACAO_SANITIZADA'))
            reg['resultado'].setdefault('adendo_retomada',dict(id=ID,hash=hash_json(l.retomada),codigo=codigo()))
            reg=registrar(s,reg['resultado'])
            l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg)
            print(json.dumps(dict(slot=eid,estado=reg['resultado']['execucao']['estado'],tempo_s=round(monotonic()-inicio,2),orcamento=l.resumo(),parada=l.parada()),ensure_ascii=False),flush=True)
        l.conferir()
        if historico(l.db)!=l.hist:raise Bloqueio('Histórico não preservado')
        resumo=dict(coorte=a['id'],retomada=ID,planejado=90,estados={e:sum(st==e for _,st,_ in l.resultados())for e in ('pendente','iniciado','terminado')},parada=l.parada(),orcamento=l.resumo(),historico_preservado=True)
        gravar_novo(out/('resumo-'+hash_json(resumo)[:12]+'.json'),resumo);return resumo
