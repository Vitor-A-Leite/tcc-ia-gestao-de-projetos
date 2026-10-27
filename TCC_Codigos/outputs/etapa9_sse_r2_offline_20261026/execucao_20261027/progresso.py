import sqlite3,json
from pathlib import Path
p=Path(__file__).parent.parent.parent/'etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
d=sqlite3.connect('file:'+str(p.resolve())+'?mode=ro',uri=True)
print(json.dumps(dict(slots=d.execute('SELECT estado,count(*) FROM slots_v04 GROUP BY estado').fetchall(),chamadas=d.execute('SELECT count(*),sum(comprometido),sum(custo_inferencia) FROM chamadas').fetchone(),recentes=d.execute('SELECT id,slot,estado FROM chamadas WHERE id>15 ORDER BY id DESC LIMIT 2').fetchall(),parada=d.execute('SELECT * FROM paradas_sse_r2').fetchall()),ensure_ascii=False))
