"""Verificação local pós-parada; sem rede e sem chaves."""
from pathlib import Path
import hashlib,json,sqlite3
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
antes=json.loads((OUT/'integridade_antes.json').read_text())
permitidos=['TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite','TCC_Codigos/docs/desenvolvimento/STATUS.md','TCC_Codigos/docs/desenvolvimento/PLANO_MESTRE.md']
alterados=[p for p,h in antes.items()if not(ROOT/p).exists()or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
a=sqlite3.connect('file:'+str(OUT/'ledger_antes.sqlite')+'?mode=ro',uri=True)
b=sqlite3.connect('file:'+str(ROOT/permitidos[0])+'?mode=ro',uri=True)
tabelas=[r[0]for r in a.execute("SELECT name FROM sqlite_master WHERE type='table'AND name NOT LIKE 'sqlite_%'")]
diff=[]
for t in tabelas:
    q='SELECT * FROM '+t+(' WHERE id<=272'if t=='chamadas'else'')+' ORDER BY rowid'
    if a.execute(q).fetchall()!=b.execute(q).fetchall():diff.append(t)
r=dict(arquivos_antes=len(antes),alterados=alterados,alteracoes_permitidas=permitidos,alteracoes_nao_permitidas=[p for p in alterados if p not in permitidos],tabelas_anteriores_alteradas=diff,chamadas1a272_preservadas='chamadas'not in diff,novas_chamadas=b.execute('SELECT count(*) FROM chamadas WHERE id>272').fetchone()[0],estado_slots_v05=dict(b.execute('SELECT estado,count(*) FROM slots_v05 GROUP BY estado').fetchall()),codigo_congelado_igual=json.loads(b.execute('SELECT adendo FROM coorte_v05').fetchone()[0])['codigo'])
from piloto_v05 import codigo
r['codigo_congelado_igual']=r['codigo_congelado_igual']==codigo()
r['schemas_anteriores_preservados']=all(a.execute('SELECT sql FROM sqlite_master WHERE name=?',(t,)).fetchone()==b.execute('SELECT sql FROM sqlite_master WHERE name=?',(t,)).fetchone()for t in tabelas)
assert not r['alteracoes_nao_permitidas']and not diff and r['codigo_congelado_igual']and r['schemas_anteriores_preservados']
(OUT/'integridade_final.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
target=OUT/'ledger_apos.sqlite'
if not target.exists():
    dst=sqlite3.connect(str(target));b.backup(dst);dst.close()
a.close();b.close();print(json.dumps(r,ensure_ascii=False))
