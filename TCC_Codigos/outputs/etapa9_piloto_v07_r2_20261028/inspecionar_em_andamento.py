"""Inspeção somente leitura das respostas H já conciliadas; não mede acurácia."""
from pathlib import Path
import sys,json,sqlite3
sys.path.insert(0,str(Path(__file__).parents[2]/'src'))
from hibrido_v07_r2.wire import incorporar
from interpretacao_no.adaptadores import _json
p=Path(__file__).parent.parent/'etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
validas=0;erros=[];contagens=[]
with sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True) as db:
    for i,s,raw in db.execute("select id,slot,registro from chamadas where id>790 and slot like '%-H-%' and estado='conciliado'"):
        x=json.loads(raw);d=json.loads(x['payload']['input'][1]['content'])
        txt=''.join(c['text']for o in x['response'].get('output',[])if o.get('type')=='message'for c in o.get('content',[])if c.get('type')=='output_text')
        contagens.append(x['contagem_oficial'])
        try:incorporar(_json(txt),d['contexto']);validas+=1
        except Exception as exc:erros.append(dict(call=i,slot=s,no=d['contexto']['no_id'],erro=str(exc)))
print(json.dumps(dict(analises_H_validas=validas,rejeicoes=erros,max_entrada_H=max(contagens)if contagens else None,nota='Validação de contrato; não é auditoria de suporte semântico'),ensure_ascii=False))
