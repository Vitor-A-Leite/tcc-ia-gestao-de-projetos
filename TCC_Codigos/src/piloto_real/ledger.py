"""Ledger SQLite ACID e lock exclusivo por lote; valores monetários nanoUSD."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import sqlite3
from interpretacao_no.contratos import hash_json

NANO_USD=10**9
RESERVA_INFERENCIA=14_500_000 #16000×125 +25000×500 nanoUSD
PROVISAO_CONTAGEM=2_000_000 #hipótese de reserva, não preço publicado
RESERVA=RESERVA_INFERENCIA+PROVISAO_CONTAGEM


class Bloqueio(ValueError):pass


class Ledger:
    def __init__(self,pasta,plano):
        self.pasta=Path(pasta);self.pasta.mkdir(parents=True,exist_ok=True)
        self.lock=open(self.pasta/'lote.lock','a+')
        try:fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:self.lock.close();raise Bloqueio('Lote já está em uso por outro processo')
        self.db=sqlite3.connect(str(self.pasta/'ledger.sqlite'))
        self.db.execute('PRAGMA journal_mode=DELETE');self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY, plano TEXT NOT NULL, hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS parada (id INTEGER PRIMARY KEY, motivo TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS slots (id TEXT PRIMARY KEY, estado TEXT NOT NULL, plano TEXT NOT NULL, resultado TEXT);
        CREATE TABLE IF NOT EXISTS chamadas (id INTEGER PRIMARY KEY AUTOINCREMENT,slot TEXT NOT NULL, request_hash TEXT NOT NULL, estado TEXT NOT NULL, comprometido INTEGER NOT NULL, contado INTEGER, custo_inferencia INTEGER, uso TEXT, registro TEXT,contagem_iniciada INTEGER NOT NULL DEFAULT 0,inferencia_iniciada INTEGER NOT NULL DEFAULT 0);''')
        m=self.db.execute('SELECT hash FROM meta WHERE id=1').fetchone()
        if m and m[0]!=hash_json(plano):self.close();raise Bloqueio('Plano/código/inputs divergem do lote persistido; não criar lote substituto')
        with self.db:
            if not m:
                self.db.execute('INSERT INTO meta VALUES(1,?,?)',(json.dumps(plano,ensure_ascii=False),hash_json(plano)))
                for s in plano['slots']:self.db.execute('INSERT INTO slots VALUES(?,?,?,NULL)',(s['execucao_id'],'pendente',json.dumps(s,ensure_ascii=False)))
        self.plano=plano

    def close(self):
        if getattr(self,'db',None):self.db.close();self.db=None
        if getattr(self,'lock',None):fcntl.flock(self.lock,fcntl.LOCK_UN);self.lock.close();self.lock=None
    def __enter__(self):return self
    def __exit__(self,*a):self.close()

    def estado(self,slot):return self.db.execute('SELECT estado FROM slots WHERE id=?',(slot,)).fetchone()[0]
    def iniciar(self,slot):
        with self.db:
            r=self.db.execute("UPDATE slots SET estado='iniciado' WHERE id=? AND estado='pendente'",(slot,))
            if r.rowcount!=1:raise Bloqueio('Slot já iniciado; não repetir inferência')
    def salvar(self,slot,r):
        with self.db:
            x=self.db.execute("UPDATE slots SET estado='terminado',resultado=? WHERE id=? AND estado='iniciado'",(json.dumps(r,ensure_ascii=False,allow_nan=False),slot))
            if x.rowcount!=1:raise Bloqueio('Resultado de slot já persistido ou slot não iniciado')
    def reservar(self,slot,reqhash):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            n,total=self.db.execute('SELECT COUNT(*),COALESCE(SUM(comprometido),0) FROM chamadas').fetchone()
            por_slot=self.db.execute('SELECT COUNT(*) FROM chamadas WHERE slot=?',(slot,)).fetchone()[0]
            s=next(x for x in self.plano['slots'] if x['execucao_id']==slot)
            if self.db.execute('SELECT COUNT(*) FROM parada').fetchone()[0] or self.estado(slot)!='iniciado' or n>=300 or por_slot >= (8 if s['condicao']=='H' else 1) or total+RESERVA>5*NANO_USD:
                raise Bloqueio('Limite agregado/per-slot de chamadas ou USD excedido')
            cur=self.db.execute('INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES(?,?,?,?)',(slot,reqhash,'reservado',RESERVA))
            return cur.lastrowid
    def iniciar_contagem(self,id):
        with self.db:
            x=self.db.execute("UPDATE chamadas SET contagem_iniciada=1 WHERE id=? AND estado='reservado' AND contagem_iniciada=0",(id,))
            if x.rowcount!=1:raise Bloqueio('Contagem já marcada; não repetir')
    def contar(self,id,n):
        if type(n)is not int or n<0:raise ValueError('Contagem oficial inválida')
        with self.db:self.db.execute("UPDATE chamadas SET estado='contado',contado=? WHERE id=? AND estado='reservado'",(n,id))
    def enviar(self,id):
        with self.db:
            x=self.db.execute("UPDATE chamadas SET estado='enviado',inferencia_iniciada=1 WHERE id=? AND estado='contado' AND contado<=16000",(id,))
            if x.rowcount!=1:raise Bloqueio('Entrada não contada/verificada ou envio já marcado')
    def concluir(self,id,custo,uso,registro):
        # Somente usage completo confiável libera a parte de inferência; provisão de count é mantida.
        if type(custo)is not int or not 0<=custo<=RESERVA_INFERENCIA:raise Bloqueio('Uso fora da reserva aprovada')
        with self.db:
            x=self.db.execute("UPDATE chamadas SET estado='conciliado',comprometido=?,custo_inferencia=?,uso=?,registro=? WHERE id=? AND estado='enviado'",(PROVISAO_CONTAGEM+custo,custo,json.dumps(uso),json.dumps(registro,ensure_ascii=False),id))
            if x.rowcount!=1:raise Bloqueio('Conciliação duplicada/inválida')
    def desconhecido(self,id,registro):
        with self.db:self.db.execute("UPDATE chamadas SET estado='custo_desconhecido',registro=? WHERE id=? AND estado!='conciliado'",(json.dumps(registro,ensure_ascii=False),id))
    def nao_enviado(self,id,registro):
        # Contagem retornou >limite: nenhuma inferência enviada; conserva reserva inteira por cautela.
        self.desconhecido(id,registro)
    def parar(self,motivo):
        with self.db:self.db.execute("INSERT OR IGNORE INTO parada VALUES(1,?)",(motivo,))
    def resumo(self):
        n,t,c=self.db.execute('SELECT COUNT(*),COALESCE(SUM(comprometido),0),COALESCE(SUM(custo_inferencia),0) FROM chamadas').fetchone()
        contagens,inferencias=self.db.execute('SELECT COALESCE(SUM(contagem_iniciada),0),COALESCE(SUM(inferencia_iniciada),0) FROM chamadas').fetchone()
        return dict(tentativas_reservadas=n,HTTP_contagem_marcadas=contagens,HTTP_inferencia_marcadas=inferencias,comprometido_nanoUSD=t,inferencia_conciliada_nanoUSD=c,teto_nanoUSD=5*NANO_USD,
                    provisao_contagem_nanoUSD=n*PROVISAO_CONTAGEM,
                    custos_desconhecidos=self.db.execute("SELECT COUNT(*) FROM chamadas WHERE estado!='conciliado'").fetchone()[0])
    def resultados(self):
        return [(s,e,json.loads(r) if r else None) for s,e,r in self.db.execute('SELECT id,estado,resultado FROM slots ORDER BY rowid')]
