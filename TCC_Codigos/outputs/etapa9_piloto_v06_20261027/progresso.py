"""Leitura compacta da coleta; sem chave, rede ou alterações no ledger."""
from pathlib import Path
import json,sqlite3
p=Path(__file__).parent.parent/'etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
with sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True) as c:
    estados=dict(c.execute('select estado,count(*) from slots_v06 group by estado'))
    chamadas=c.execute('select count(*),sum(comprometido) from chamadas').fetchone()
    nova=c.execute('select id,slot,estado,contado from chamadas where id>510 order by id desc limit 1').fetchone()
    print(json.dumps(dict(slots=estados,carteira=dict(tentativas=chamadas[0],comprometido_USD=chamadas[1]/1e9,saldo_USD=(5e9-chamadas[1])/1e9),ultima=nova,parada=c.execute('select motivo from parada_v06').fetchall()),ensure_ascii=False))
