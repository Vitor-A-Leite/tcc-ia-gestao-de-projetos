"""Fechamento read-only contra faseDNS e hashes antes da rede; snapshot final novo."""
from pathlib import Path
import sqlite3,json,hashlib
O=Path(__file__).parent;R=O.parent;W=R.parent/'etapa9_piloto_real_aprovado_20261026/ledger.sqlite';ROOT=R.parents[2]
a=sqlite3.connect('file:'+str(R/'ledger_apos.sqlite')+'?mode=ro',uri=True);b=sqlite3.connect('file:'+str(W)+'?mode=ro',uri=True)
assert not b.execute("SELECT count(*)FROM slots_v05 WHERE estado='iniciado'").fetchone()[0]
x=a.execute('SELECT *FROM chamadas WHERE id<=273 ORDER BY id').fetchall();y=b.execute('SELECT *FROM chamadas WHERE id<=273 ORDER BY id').fetchall()
primeiros=a.execute("SELECT *FROM slots_v05 WHERE estado='terminado'").fetchall()
first=all(b.execute('SELECT *FROM slots_v05 WHERE id=?',(v[0],)).fetchone()==v for v in primeiros)
parada=a.execute('SELECT *FROM parada_v05').fetchall()==b.execute('SELECT *FROM parada_v05').fetchall()
coorte=a.execute('SELECT *FROM coorte_v05').fetchall()==b.execute('SELECT *FROM coorte_v05').fetchall()
files=json.loads((O/'codigo_antes_rede.json').read_text());diff=[p for p,h in files.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
r=dict(chamadas1a273_identicas=x==y,primeiro_resultado_identico=first,paradaDNS_identica=parada,adendo_original_identico=coorte,codigos_modificados=diff,snapshotDNS_preservado='ledger_apos.sqlite;273tentativas',snapshot_final='retomada_89/ledger_final.sqlite',contagens=b.execute('SELECT count(*),sum(comprometido)FROM chamadas').fetchone(),slots=b.execute('SELECT estado,count(*)FROM slots_v05 GROUP BY estado').fetchall())
assert x==y and first and parada and coorte and not diff
p=O/'ledger_final.sqlite'
if not p.exists():
 dst=sqlite3.connect(str(p));b.backup(dst);dst.close()
else:
 dst=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True);assert list(dst.iterdump())==list(b.iterdump());dst.close()
(O/'integridade_final_fases.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');a.close();b.close();print(json.dumps(r))
