"""Leitura para inspeção técnica; resultados brutos, sem avaliação ou alteração."""
from pathlib import Path
import json,sqlite3
p=Path(__file__).parent.parent/'etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
with sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True)as db:
    for raw, in db.execute("select resultado from slots_v07_r3 where resultado is not null and id like '%-H-%'"):
        x=json.loads(raw);s=x['metadados'];r=x['resultado']
        if all(r.get(k,{}).get('estado')=='exato'for k in ('delta_dias','delta_centavos')):continue
        print(json.dumps(dict(caso=s['caso_id'],repeticao=s['repeticao'],prazo={k:r.get('delta_dias',{}).get(k)for k in ('estado','valor','direcao')},custo={k:r.get('delta_centavos',{}).get(k)for k in ('estado','valor','direcao')},erros=r['execucao'].get('erros'),rejeicoes=[d for d in r.get('registro_operacional',{}).get('decisoes',[])if d['operacao_estrutural']!='permitida_condicional'],pendencias_tipadas=r.get('registro_operacional',{}).get('fechamento_final',{}).get('pendencias_tipadas'),lacunas=r.get('lacunas')),ensure_ascii=False))
