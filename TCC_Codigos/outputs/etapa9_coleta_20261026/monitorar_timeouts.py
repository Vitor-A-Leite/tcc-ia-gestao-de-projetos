"""Guarda diagnóstica autorizada após início; não chama API nem altera protocolo."""
import sqlite3,json,subprocess,os,signal,time
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'outputs/etapa9_piloto_real_aprovado_20261026';OUT=Path(__file__).parent
anterior=None
while True:
    c=sqlite3.connect('file:'+str((P/'ledger.sqlite').resolve())+'?mode=ro',uri=True)
    slots=c.execute('SELECT estado,count(*) FROM slots GROUP BY estado').fetchall()
    rows=c.execute('SELECT id,estado,registro FROM chamadas WHERE inferencia_iniciada=1 ORDER BY id').fetchall();c.close()
    finalizadas=[(i,e,json.loads(r) if r else{}) for i,e,r in rows if e in ('conciliado','custo_desconhecido')]
    consecutivas=[]
    for i,e,r in reversed(finalizadas):
        if r.get('erro')!='timeout':break
        consecutivas.append(i)
    foto=dict(slots=dict(slots),inferencias_marcadas=len(rows),inferencias_finalizadas=len(finalizadas),timeouts_consecutivos=len(consecutivas))
    if foto!=anterior:
        with (OUT/'acompanhamento.jsonl').open('a') as f:f.write(json.dumps(foto)+'\n')
        anterior=foto
    if len(consecutivas)>=5:
        # Confere processo dono do lock, sem enumerar ambiente ou credenciais.
        ps=subprocess.run(['lsof','-t',str(P/'lote.lock')],capture_output=True,text=True,check=True)
        ids={int(p) for p in ps.stdout.split()}
        alvos=[]
        for pid in ids:
            cmd=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,check=True).stdout.strip()
            if cmd.endswith('-m piloto_real --rodar'):alvos.append(pid)
        if len(alvos)!=1:raise RuntimeError('Não foi possível identificar o coletor inequivocamente; não enviar sinal')
        os.kill(alvos[0],signal.SIGINT)
        evento=dict(tipo='parada_antecipada_diagnostica',origem='instrução explícita do coordenador durante coleta',data_usuario='2026-10-26',regra='cinco inferências consecutivas sem resposta por timeout;sem ampliar deadline ou repetir slots',inferencias_timeout_ids=sorted(consecutivas),PID_interrompido=alvos[0],snapshot=foto)
        # Aguarda a liberação segura pelo context manager; nunca zera/reseta estado.
        time.sleep(2)
        c=sqlite3.connect(str(P/'ledger.sqlite'),timeout=10)
        with c:c.execute('INSERT OR IGNORE INTO parada VALUES(1,?)',('Parada antecipada diagnóstica autorizada: cinco inferências consecutivas com timeout; revisão antes de retomar',))
        c.close()
        (OUT/'parada_diagnostica.json').write_text(json.dumps(evento,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(evento,ensure_ascii=False));break
    if not any(e in ('pendente','iniciado') for e,n in slots):
        print(json.dumps(dict(estado='lote_terminado',snapshot=foto)));break
    time.sleep(5)
