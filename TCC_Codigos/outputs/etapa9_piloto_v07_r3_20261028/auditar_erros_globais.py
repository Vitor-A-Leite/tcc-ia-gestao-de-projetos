"""Inspeção dos campos/referências brutos rejeitados, sem corrigir saídas."""
from pathlib import Path
import json,sqlite3
from interpretacao_no.adaptadores import _json
O=Path(__file__).parent

def referencias(x):
 r=set()
 if isinstance(x,dict):
  if isinstance(x.get('fonte_id'),str)and isinstance(x.get('localizador'),str):r.add((x['fonte_id'],x['localizador']))
  for v in x.values():r|=referencias(v)
 elif isinstance(x,list):
  for v in x:r|=referencias(v)
 return r

def main():
 erros=json.loads((O/'contabilidade_e_erros.json').read_text())['erros'];ids={r['execucao_id']:r for r in erros};out=[]
 with sqlite3.connect((O/'ledger_final.sqlite').resolve().as_uri()+'?mode=ro',uri=True)as db:
  for cid,s,raw in db.execute('select id,slot,registro from chamadas where id>834'):
   if s not in ids:continue
   r=json.loads(raw);txt=''.join(c['text']for o in r['response']['output']if o.get('type')=='message'for c in o['content']if c.get('type')=='output_text');a=_json(txt);entrada=json.loads(r['payload']['input'][1]['content']);msg=ids[s]['erros'][0]['mensagem'];item=dict(execucao_id=s,call_id=cid,erro=msg)
   if msg.startswith('Campos incompatíveis:'):
    esperado=set(msg.split(': ',1)[1].split());item.update(campos_ausentes=sorted(esperado-set(a)),campos_extras=sorted(set(a)-esperado))
   else:
    view=entrada['view'];fontes=view['comum']['fontes']
    if view['condicao']=='T':fontes=fontes+[json.loads(l.split(': ',1)[1])for l in view['relacoes_texto'].splitlines()if l.startswith('fontes: ')]
    mapa={f['id']:f['localizador']for f in fontes};permitidos=set(mapa.items());invalidas=referencias(a)-permitidos
    item['referencias_invalidas']=[dict(fonte_id=f,localizador_retornado=l,localizador_visivel=mapa.get(f))for f,l in sorted(invalidas)]
    if not invalidas:raise ValueError('Rejeição de fonte não reproduzida: '+s)
   out.append(item)
 (O/'auditoria_erros_globais.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(out,ensure_ascii=False))

if __name__=='__main__':main()
