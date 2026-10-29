"""Executor final aditivo. Preditor, inputs e manifesto da etapa 10 intocados.

Uma carteira canônica, 9 slots, até 30 novas tentativas, sem replay/retry.
Importar este módulo nunca lê chave, toca carteira ou envia rede.
"""
from copy import deepcopy
from pathlib import Path
import argparse,fcntl,hashlib,importlib.util,json,socket,sqlite3,sys
from time import monotonic

ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'TCC_Codigos/src'
sys.path.insert(0,str(SRC))
ET10=ROOT/'TCC_Codigos/outputs/etapa10_auditoria_20261028'
OUT=ROOT/'TCC_Codigos/outputs/etapa11_final_20261028'
CARTEIRA=ROOT/'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026'
ID='etapa11-final-v2-3-BHT-R1'
BASE_N=1114
BASE_USD=4480425665
from piloto_real.ledger import Ledger,Bloqueio,RESERVA,NANO_USD
from piloto_real.runner import gravar_novo,indisponivel
from piloto_real.transporte import sanitizar
from piloto_real import MODELO,CONFIG
from piloto_v07_r3.transporte import ResponsesSSE,LocalSSE
from hibrido_v07_r3 import construir,LocalV07R3,executar_h
from hibrido_v07_r3.contratos import VERSAO
from hibrido_v07_r3.avaliacao import validar_manifesto,registrar
from interpretacao_no.contratos import hash_json
from condicoes.baseline import Global


def ler(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exigir(c,m):
    if not c:raise Bloqueio(m)


def carregar_modulo(nome,path):
    spec=importlib.util.spec_from_file_location(nome,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def historico(db):
    """Hash em fluxo das tabelas antigas e chamadas 1–1114; sem JSON de resultados."""
    h=hashlib.sha256()
    tables=db.execute("select name,sql from sqlite_master where type='table' and name not like 'sqlite_%' and name not like '%etapa11%' order by name").fetchall()
    for t,ddl in tables:
        h.update(json.dumps([t,ddl],ensure_ascii=False).encode())
        query='select * from "'+t.replace('"','""')+'"'+(' where id<=1114' if t=='chamadas' else '')+' order by rowid'
        for row in db.execute(query):h.update(json.dumps(row,ensure_ascii=False,separators=(',',':')).encode())
    return h.hexdigest()


def preparar():
    freeze=ler(ET10/'congelamento.json')
    for p,h in freeze['artefatos'].items():exigir(sha(ROOT/p)==h,'Congelamento etapa10 divergente: '+p)
    prep=carregar_modulo('preparacao_final_congelada',ET10/'preparar_final.py')
    casos,inputs=prep.carregar(ROOT/'TCC_Codigos/data/final/etapa10_v2/inputs')
    m=ler(ET10/'preparacao_final_v2/manifesto.json');validar_manifesto(m)
    exigir(len(m['execucoes'])==9 and m['uso']=='final','Manifesto final inválido')
    views=ler(ET10/'preparacao_final_v2/views.json')
    cs={c['caso_id']:c for c in casos}
    for s in m['execucoes']:
        c=cs[s['caso_id']]
        exigir(c['views']==views[c['caso_id']],'View reconstruída divergente')
        exigir(s['snapshot_hash']==hash_json(c['estado']) and s['evento_hash']==hash_json(c['evento']),'Snapshot/evento divergente')
    runtime={p:h for p,h in freeze['artefatos'].items() if p.startswith('TCC_Codigos/src/')}
    runtime.update(inputs)
    for p in [ET10/'preparar_final.py',ET10/'preparacao_final_v2/manifesto.json',ET10/'preparacao_final_v2/views.json',ET10/'congelamento.json',Path(__file__).resolve(),ROOT/'TCC_Codigos/tests/etapa11/test_executor.py',OUT/'precos_verificados.json']:
        runtime[str(p.relative_to(ROOT))]=sha(p)
    precos=ler(OUT/'precos_verificados.json')
    exigir(precos['nanoUSD_por_token']==dict(input=100,cached_input=10,cache_write_30m=125,output=500),'Tarifário incompatível')
    with sqlite3.connect((OUT/'ledger_antes.sqlite').as_uri()+'?mode=ro',uri=True)as db:hist=historico(db)
    adendo=dict(id=ID,autorizacao_usuario='Pode iniciar a etapa 11 com os três casos inéditos. Crie uma meta para concluir o experimento final e continue até atendê-la, mantendo o limite acumulado de US$ 5.',
        data_local='2026-10-28 America/Sao_Paulo',manifesto=m,slots=[s['execucao_id'] for s in m['execucoes']],
        congelamento_etapa10_sha256=sha(ET10/'congelamento.json'),runtime=runtime,
        versao_formato_local=VERSAO,modelo=MODELO,configuracao=CONFIG,precos=precos,
        base_tentativas=BASE_N,base_comprometido_nanoUSD=BASE_USD,historico_sha256=hist,
        teto_nanoUSD=5*NANO_USD,max_tentativas_novas=30,max_tentativas_acumuladas=1144,reserva_nanoUSD=RESERVA,
        max_chamadas_H=8,max_tempo_H_s=1500,max_entrada_oficial=16000,max_saida_total=25000,
        timeout_chamada_s=180,retries=0,fallback=False,parecer_humano=False,
        limite='Experimento exploratório: três casos sintéticos, uma repetição; autorização de execução não é parecer científico humano.')
    return adendo,cs


class CarteiraFinal(Ledger):
    def __init__(self,pasta,adendo):
        self.pasta=Path(pasta)
        exigir((self.pasta/'ledger.sqlite').is_file(),'Carteira prévia obrigatória; não criar/resetar')
        self.lock=open(self.pasta/'lote.lock','a+')
        try:fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:self.lock.close();self.lock=None;raise Bloqueio('Carteira em uso') from None
        try:
            self.db=sqlite3.connect(self.pasta/'ledger.sqlite')
            self.db.execute('PRAGMA synchronous=FULL')
            self.manifesto_formato=deepcopy(adendo);self.novos={s['execucao_id']:s for s in adendo['manifesto']['execucoes']}
            exigir(historico(self.db)==adendo['historico_sha256'],'Histórico anterior divergente')
            self.conferir()
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS coorte_etapa11(id TEXT PRIMARY KEY,adendo TEXT NOT NULL,hash TEXT NOT NULL)')
                self.db.execute('CREATE TABLE IF NOT EXISTS slots_etapa11(id TEXT PRIMARY KEY,estado TEXT NOT NULL,resultado TEXT)')
                self.db.execute('CREATE TABLE IF NOT EXISTS parada_etapa11(id INTEGER PRIMARY KEY,motivo TEXT NOT NULL)')
                old=self.db.execute('select hash from coorte_etapa11 where id=?',(ID,)).fetchone()
                if old:exigir(old[0]==hash_json(adendo),'Adendo persistido divergente')
                else:
                    exigir(self.db.execute('select count(*),sum(comprometido) from chamadas').fetchone()==(BASE_N,BASE_USD),'Base financeira divergente')
                    self.db.execute('insert into coorte_etapa11 values(?,?,?)',(ID,json.dumps(adendo,ensure_ascii=False),hash_json(adendo)))
                    self.db.executemany('insert into slots_etapa11 values(?,?,NULL)',[(s,'pendente') for s in self.novos])
        except BaseException:self.close();raise

    def conferir(self):
        for p,h in self.manifesto_formato['runtime'].items():exigir(sha(ROOT/p)==h,'Runtime congelado alterado: '+p)
    def conferir_historico(self):exigir(historico(self.db)==self.manifesto_formato['historico_sha256'],'Histórico modificado')
    def estado(self,s):
        exigir(s in self.novos,'Slot fora do manifesto')
        return self.db.execute('select estado from slots_etapa11 where id=?',(s,)).fetchone()[0]
    def parada(self):return self.db.execute('select motivo from parada_etapa11').fetchone()
    def parar(self,m):
        with self.db:self.db.execute('insert or ignore into parada_etapa11 values(1,?)',(m,))
    def iniciar(self,s):
        self.conferir()
        with self.db:
            exigir(not self.parada(),'Coorte parada')
            primeiro=self.db.execute("select id from slots_etapa11 where estado!='terminado' order by rowid limit 1").fetchone()
            exigir(primeiro==(s,),'Ordem/replay inválido')
            q=self.db.execute("update slots_etapa11 set estado='iniciado' where id=? and estado='pendente'",(s,))
            exigir(q.rowcount==1,'Slot já iniciado; não repetir')
    def salvar(self,s,r):
        self.conferir()
        with self.db:
            q=self.db.execute("update slots_etapa11 set estado='terminado',resultado=? where id=? and estado='iniciado'",(json.dumps(r,ensure_ascii=False,allow_nan=False),s))
            exigir(q.rowcount==1,'Resultado já salvo/slot não iniciado')
    def reservar(self,s,h):
        self.conferir()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            n,t=self.db.execute('select count(*),sum(comprometido) from chamadas').fetchone()
            por=self.db.execute('select count(*) from chamadas where slot=?',(s,)).fetchone()[0]
            exigir(s in self.novos and not self.parada() and self.estado(s)=='iniciado','Slot indisponível')
            exigir(n<1144 and n-BASE_N<30 and t+RESERVA<=5*NANO_USD and por<(8 if self.novos[s]['condicao']=='H' else 1),'Teto de chamadas/custo')
            return self.db.execute("insert into chamadas(slot,request_hash,estado,comprometido) values(?,?,'reservado',?)",(s,h,RESERVA)).lastrowid
    def _nova(self,i):
        r=self.db.execute('select slot from chamadas where id=?',(i,)).fetchone()
        exigir(i>BASE_N and r and r[0] in self.novos,'Mutação de chamada histórica/estranha bloqueada')
    def iniciar_contagem(self,i):self._nova(i);return super().iniciar_contagem(i)
    def contar(self,i,n):self._nova(i);return super().contar(i,n)
    def enviar(self,i):self._nova(i);return super().enviar(i)
    def concluir(self,i,*args):self._nova(i);return super().concluir(i,*args)
    def desconhecido(self,i,r):
        self._nova(i);super().desconhecido(i,r)
        if r.get('erro')!='timeout':self.parar('Falha transporte/protocolo/usage: '+str(r.get('erro','usage incompleto')))
        ult=self.db.execute('select registro from chamadas where id>1114 order by id desc limit 5').fetchall()
        if len(ult)==5 and all(raw and json.loads(raw).get('erro')=='timeout' for raw, in ult):self.parar('Cinco timeouts consecutivos')
    def resultados(self):return [(s,e,json.loads(r)if r else None) for s,e,r in self.db.execute('select * from slots_etapa11 order by rowid')]


def executar(adendo,casos,*,pasta=CARTEIRA,out=OUT,chave=None,http=None):
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    exigir(http is None or Path(pasta).resolve()!=CARTEIRA.resolve(),'Mock nunca pode usar carteira real')
    exigir(http is not None or chave,'Credencial ausente')
    gravar_novo(out/'adendo_aprovado.json',adendo);gravar_novo(out/'manifesto.json',adendo['manifesto'])
    from retomada_v04_sse.http import HTTPStreaming
    api=http if http is not None else HTTPStreaming(chave)
    redact=lambda x:sanitizar(x,chave)
    with CarteiraFinal(pasta,adendo) as ledger:
        for s in adendo['manifesto']['execucoes']:
            eid=s['execucao_id'];st=ledger.estado(eid)
            if st=='terminado':continue
            if st=='iniciado':
                r=indisponivel(s,'INTERROMPIDO_SEM_REPLAY');reg=registrar(s,r)
                ledger.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg);ledger.parar('Slot encontrado iniciado; sem replay');break
            if ledger.parada():break
            n,t=ledger.db.execute('select count(*),sum(comprometido) from chamadas').fetchone()
            if n>=1144 or t+RESERVA>5*NANO_USD:ledger.parar('Teto acumulado impede próximo slot');break
            ledger.iniciar(eid);inicio=monotonic()
            try:
                c=casos[s['caso_id']]
                if s['condicao']=='H':
                    transporte=LocalSSE(ledger,eid,api,redator=redact,timeout_s=180)
                    politica=construir(c['estado'],c['evento'],execucao_id=eid)
                    interpretador=LocalV07R3(transporte,modelo=MODELO,configuracao=CONFIG,timeout_s=180)
                    r=executar_h(c['base'],c['evento_comum'],c['fontes'],c['estado'],c['evento'],c['views']['H'],interpretador,politica,vinculo=c['vinculo'],origem='llm_transporte_injetado')
                    r.update(registro_operacional=deepcopy(politica.registro_operacional),versao_formato_local=VERSAO,natureza_previsao='condicional_original_v07')
                else:
                    transporte=ResponsesSSE(ledger,eid,api,redator=redact,timeout_s=180)
                    r=Global(transporte,modelo=MODELO,configuracao=CONFIG,timeout_s=180,repetir_transporte=False,origem='llm_transporte_injetado').prever(c['views'][s['condicao']],execucao_id=eid)
                    r['natureza_previsao']='original_global_nao_corrigida'
                r.update(suporte_semantico='nao_auditado',tempo_slot_s=monotonic()-inicio,orcamento_apos_slot=ledger.resumo(),adendo_etapa11_hash=hash_json(adendo))
            except Exception:
                ledger.parar('Falha integração final; sem retry');r=indisponivel(s,'FALHA_INTEGRACAO_FINAL_SANITIZADA')
            reg=redact(registrar(s,r));ledger.salvar(eid,reg);gravar_novo(out/(eid+'.json'),reg)
            print(json.dumps(dict(slot=eid,estado=r['execucao']['estado'],tempo_s=round(monotonic()-inicio,2),orcamento=ledger.resumo(),parada=ledger.parada()),ensure_ascii=False),flush=True)
        ledger.conferir();ledger.conferir_historico()
        res=dict(coorte=ID,estados={e:sum(st==e for _,st,_ in ledger.resultados()) for e in ('pendente','iniciado','terminado')},parada=ledger.parada(),orcamento=ledger.resumo(),historico_preservado=True)
        gravar_novo(out/('resumo-'+hash_json(res)[:12]+'.json'),res)
        with sqlite3.connect(out/('ledger_final.sqlite' if res['estados']['terminado']==9 else 'ledger_parada.sqlite'))as final:ledger.db.backup(final)
        return res


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--rodar',action='store_true');args=parser.parse_args()
    a,cs=preparar()
    if not args.rodar:
        gravar_novo(OUT/'adendo_aprovado.json',a);gravar_novo(OUT/'manifesto.json',a['manifesto'])
        print(json.dumps(dict(estado='preparado_offline',slots=9,reserva_maxima_nanoUSD=30*RESERVA,adendo_sha256=hash_json(a))))
    else:
        socket.getaddrinfo('api.openai.com',443) # antes de chave/carteira/reserva
        from piloto_real.chave import carregar
        chave=carregar(ROOT/'.env.piloto')
        print(json.dumps(executar(a,cs,chave=chave),ensure_ascii=False))
