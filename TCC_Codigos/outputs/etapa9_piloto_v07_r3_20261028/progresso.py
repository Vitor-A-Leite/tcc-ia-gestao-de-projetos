"""Leitura compacta da coleta; sem chave, rede ou alterações no ledger."""
from pathlib import Path
from collections import Counter
import json,sqlite3
p=Path(__file__).parent.parent/'etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
with sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True) as c:
    estados=dict(c.execute('select estado,count(*) from slots_v07_r3 group by estado'))
    chamadas=c.execute('select count(*),sum(comprometido) from chamadas').fetchone()
    nova=c.execute('select id,slot,estado,contado from chamadas where id>834 order by id desc limit 1').fetchone()
    regs=[json.loads(x) for x, in c.execute('select resultado from slots_v07_r3 where resultado is not null')]
    por={}
    for cond in 'BHT':
        rs=[r['resultado']for r in regs if r['metadados']['condicao']==cond]
        por[cond]=dict(finalizados=len(rs),estados=dict(Counter(r['execucao']['estado']for r in rs)),exatos_brutos=dict(prazo=sum(r.get('delta_dias',{}).get('estado')=='exato'for r in rs),custo=sum(r.get('delta_centavos',{}).get('estado')=='exato'for r in rs)))
    print(json.dumps(dict(slots=estados,carteira=dict(tentativas=chamadas[0],comprometido_USD=chamadas[1]/1e9,saldo_USD=(5e9-chamadas[1])/1e9),ultima=nova,parada=c.execute('select motivo from parada_v07_r3').fetchall(),por_condicao=por,nota='Contagem bruta provisória; avaliação formal somente pós-coleta'),ensure_ascii=False))
