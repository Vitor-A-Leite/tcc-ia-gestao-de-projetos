"""Reprodução dos sintomas históricos, offline; não corrige respostas."""
import json,sqlite3
from pathlib import Path
from collections import Counter
from interpretacao_no.adaptadores import _json
from interpretacao_no.contratos import validar,hash_json
ROOT=Path(__file__).resolve().parents[2]
W=ROOT/'outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
db=sqlite3.connect('file:'+str(W.resolve())+'?mode=ro',uri=True)
counts=Counter();reproduzidos=[];fechamentos=Counter()
for (raw,) in db.execute('SELECT resultado FROM slots_v04 ORDER BY rowid'):
 reg=json.loads(raw)
 if reg['metadados']['condicao']!='H':continue
 r=reg['resultado'];fechamentos[(r['registro_operacional']['fechamento_final']['estado'],r['delta_dias']['estado'],r['delta_centavos']['estado'])]+=1
 for step in r['rastro_orquestracao']:
  ex=step.get('analise',{}).get('execucao',{})
  if not ex:continue
  for att in ex.get('tentativas',[]):
   text=att.get('resposta_bruta')
   if not text:continue
   try:validar(_json(text),step['contexto'])
   except (ValueError,KeyError,TypeError)as err:
    counts[str(err)]+=1;reproduzidos.append(dict(execucao_id=reg['metadados']['execucao_id'],no_id=step['no_id'],erro=str(err),resposta_bruta_hash=hash_json(text),contexto_hash=step['contexto']['contexto_hash']))
result=dict(rotulo='REPRODUCAO_LEGADA_OFFLINE_SEM_RECLASSIFICACAO',rejeicoes=dict(counts),fechamentos=[dict(estado=k[0],prazo=k[1],custo=k[2],n=v)for k,v in fechamentos.items()],analises=reproduzidos)
Path(__file__).with_name('reproducao_legada.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items()if k!='analises'},ensure_ascii=False))
assert counts['Texto obrigatório']==15 and counts['Ausência exige zero local sustentado']==3
assert fechamentos[('completo_operacional_condicional','indeterminado','indeterminado')]==8
print('SINAL VERMELHO REPRODUZIDO: interface e oito fechamentos sem previsão quantitativa; legado permanece intacto.')
