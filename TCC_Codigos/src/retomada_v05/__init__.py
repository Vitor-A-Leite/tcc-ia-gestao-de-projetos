"""Continuação dos89pendentes após DNS de ambiente; não repete tentativa273."""
from pathlib import Path
import json,hashlib
from piloto_v05 import CarteiraV05,preparar_coorte,historico
from piloto_real.ledger import Bloqueio
from piloto_real.runner import gravar_novo
from interpretacao_no.contratos import hash_json
ID='etapa9-v05-retomada89-rede-20261027'
def codigo():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(Path(__file__).parent.glob('*.py'))}
class CarteiraRetomada(CarteiraV05):
    def __init__(self,pasta,plano,a):
        self.ativa=False;super().__init__(pasta,plano,a)
        try:
            self.permitidos=tuple(s for s,e,_ in self.resultados()if e=='pendente')
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS retomada_v05(id TEXT PRIMARY KEY,adendo TEXT,hash TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS parada_retomada_v05(id INTEGER PRIMARY KEY,motivo TEXT)')
                old=self.db.execute('SELECT adendo,hash FROM retomada_v05 WHERE id=?',(ID,)).fetchone()
                if old:
                    self.adendo_retomada=json.loads(old[0]);self.permitidos=tuple(self.adendo_retomada['slots'])
                    if old[1]!=hash_json(self.adendo_retomada)or self.adendo_retomada['codigo']!=codigo():raise Bloqueio('Retomada/código divergentes')
                else:
                    n,t=self.db.execute('SELECT count(*),sum(comprometido)FROM chamadas').fetchone()
                    final=[(s,r)for s,e,r in self.resultados()if e=='terminado']
                    if(n,t)!=(273,1223050975)or len(self.permitidos)!=89 or len(final)!=1 or self.db.execute('SELECT motivo FROM parada_v05').fetchone()!=('Falha transporte/protocolo: http_indisponivel',):raise Bloqueio('Estado não corresponde à parada DNS')
                    self.adendo_retomada=dict(id=ID,autorizacao='Continuação dos90slots v05 já autorizados;89pendentes, sem replay doB1/tentativa273',motivo='FalhaDNS no sandbox;getaddrinfo fora do sandbox verificado pela coordenação semAPI',acesso='execução com rede escalada sujeita à revisão automática',slots=list(self.permitidos),primeiro_resultado_hash=hash_json(final),chamada273_hash=hash_json(self.db.execute('SELECT *FROM chamadas WHERE id=273').fetchone()),parada_original_preservada=True,adendo_original_hash=hash_json(a),historico=self.hist,codigo=codigo(),base_tentativas=273,base_comprometido_nanoUSD=t,max_global=572,max_novas_restantes=299,teto_nanoUSD=5000000000,configuracao='mesmos modelo/High/stream/180s total/25k saída/16k entrada/8H/1500sH;sem retries/fallback',codigo_original=a['codigo'])
                    self.db.execute('INSERT INTO retomada_v05 VALUES(?,?,?)',(ID,json.dumps(self.adendo_retomada,ensure_ascii=False),hash_json(self.adendo_retomada)))
                self.ativa=True
        except BaseException:self.close();raise
    def parada(self):
        if not self.ativa:return super().parada()
        return self.db.execute('SELECT motivo FROM parada_retomada_v05').fetchone()
    def parar(self,m):
        if not self.ativa:return super().parar(m)
        with self.db:self.db.execute('INSERT OR IGNORE INTO parada_retomada_v05 VALUES(1,?)',(m,))
    def conferir(self):
        super().conferir()
        if self.ativa:
            a=self.adendo_retomada
            if a['codigo']!=codigo()or a['chamada273_hash']!=hash_json(self.db.execute('SELECT *FROM chamadas WHERE id=273').fetchone()):raise Bloqueio('Código/tentativa273 alterados')
            final=[(s,r)for s,e,r in self.resultados()if s not in self.permitidos]
            if hash_json(final)!=a['primeiro_resultado_hash']:raise Bloqueio('Primeiro resultado alterado')
    def iniciar(self,s):
        if s not in self.permitidos:raise Bloqueio('Não repetir primeiro slot')
        return super().iniciar(s)
    def reservar(self,s,h):
        if s not in self.permitidos:raise Bloqueio('Não repetir primeiro slot')
        return super().reservar(s,h)
    def salvar(self,s,r):
        if s not in self.permitidos:raise Bloqueio('Não editar primeiro resultado')
        return super().salvar(s,r)

from copy import deepcopy
from piloto_real.runner import indisponivel
from piloto_real import MODELO,CONFIG
from hibrido_v05.contratos import VERSAO
from hibrido_v05.avaliacao import registrar
from piloto_real.ledger import RESERVA,NANO_USD
def executar(dados,pasta,out,*,chave=None,http=None,coletar=False):
    from time import monotonic
    from piloto_real.transporte import sanitizar
    from condicoes.baseline import Global
    from hibrido_v05 import construir,LocalV05,executar_h
    from piloto_v05.transporte import ResponsesSSE,LocalSSE
    from retomada_v04_sse.http import HTTPStreaming
    plano,a,casos=preparar_coorte(dados);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    gravar_novo(out/'adendo_aprovado.json',a);gravar_novo(out/'manifesto.json',a['manifesto'])
    if coletar and http is None and not chave:raise Bloqueio('Credencial local ausente')
    with CarteiraRetomada(pasta,plano,a)as l:
        gravar_novo(out/'adendo_retomada.json',l.adendo_retomada)
        if not coletar:return dict(estado='preparado_offline',slots=89,adendo_hash=hash_json(l.adendo_retomada))
        api=http or HTTPStreaming(chave);redact=lambda x:sanitizar(x,chave)
        for s in a['manifesto']['execucoes']:
            eid=s['execucao_id'];st=l.estado(eid)
            if st=='terminado':continue
            if st=='iniciado':
                r=indisponivel(s,'INTERROMPIDO_SEM_REPLAY');reg=registrar(s,r);l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg);l.parar('Slot iniciado anteriormente; sem replay');break
            if l.parada():break
            n,t=l.db.execute('SELECT count(*),sum(comprometido) FROM chamadas').fetchone()
            if n>=572 or t+RESERVA>5*NANO_USD:l.parar('Teto acumulado impede próximo slot');break
            l.iniciar(eid);inicio=monotonic()
            try:
                c=casos[s['caso_id']]
                if s['condicao']=='H':
                    t=LocalSSE(l,eid,api,redator=redact,timeout_s=180)
                    p=construir(c['estado'],c['evento'],execucao_id=eid)
                    i=LocalV05(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180)
                    r=executar_h(c['base'],c['evento_comum'],c['fontes'],c['estado'],c['evento'],c['views']['H'],i,p,vinculo=c['vinculo'],origem='llm_transporte_injetado')
                    r.update(registro_operacional=deepcopy(p.registro_operacional),versao_formato_local=VERSAO,natureza_previsao='condicional_original_v05')
                else:
                    t=ResponsesSSE(l,eid,api,redator=redact,timeout_s=180)
                    r=Global(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180,repetir_transporte=False,origem='llm_transporte_injetado').prever(c['views'][s['condicao']],execucao_id=eid)
                    r['natureza_previsao']='original_global_nao_corrigida'
                r.update(suporte_semantico='nao_auditado',tempo_slot_s=monotonic()-inicio,orcamento_apos_slot=l.resumo(),adendo_v05_hash=hash_json(a))
            except Exception:
                l.parar('Falha integração v05; sem retry');r=indisponivel(s,'FALHA_INTEGRACAO_V05_SANITIZADA')
            reg=redact(registrar(s,r));l.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg)
            print(json.dumps(dict(slot=eid,estado=r['execucao']['estado'],tempo_s=round(monotonic()-inicio,2),orcamento=l.resumo(),parada=l.parada()),ensure_ascii=False),flush=True)
        l.conferir();res=dict(coorte=ID,estados={e:sum(st==e for _,st,_ in l.resultados())for e in ('pendente','iniciado','terminado')},parada=l.parada(),orcamento=l.resumo(),historico_preservado=True)
        gravar_novo(out/('resumo-'+hash_json(res)[:12]+'.json'),res);return res
