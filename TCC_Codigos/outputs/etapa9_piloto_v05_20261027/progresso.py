"""Snapshot compacto read-only; não consulta chave/API."""
import sqlite3,json
from pathlib import Path
p=Path(__file__).parent.parent/'etapa9_piloto_real_aprovado_20261026/ledger.sqlite';c=sqlite3.connect('file:'+str(p.resolve())+'?mode=ro',uri=True)
x=dict(slots=dict(c.execute('SELECT estado,count(*)FROM slots_v05 GROUP BY estado').fetchall()),carteira=c.execute('SELECT count(*),sum(comprometido)FROM chamadas').fetchone(),ultimas=c.execute('SELECT id,estado FROM chamadas ORDER BY id DESC LIMIT 2').fetchall(),parada=c.execute('SELECT motivo FROM parada_retomada_v05').fetchone())
print(json.dumps(x));c.close()
