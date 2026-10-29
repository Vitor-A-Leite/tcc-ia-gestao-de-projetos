"""Conferência final dos artefatos e critérios; sem API ou alteração de previsões."""
from pathlib import Path
import json,hashlib,re,sqlite3
from piloto_v07_r3 import codigo
O=Path(__file__).parent;ROOT=O.parents[2]

def read(n):return json.loads((O/n).read_text())
def check(ok,mensagem):
 if not ok:raise ValueError(mensagem)

def main():
 i=read('integridade_final.json');r=read('resumo_descritivo.json');a=read('auditoria_tecnica.json');n=read('normalizacao.json');inc=read('comparacao_incerteza.json');tri=read('triagem_todas_condicoes.json')
 check(i['slots']=={'terminado':90}and len(n['linhas'])==90,'Coorte incompleta')
 check(len({l['slot']['execucao_id']for l in n['linhas']})==90,'Slots duplicados')
 check(all(r['por_condicao'][c]['registros']==30 for c in 'BHT'),'Denominadores por condição')
 check(i['estados_chamadas']=={'conciliado':280}and not i['parada'],'Coleta não conciliada/parada')
 check(not i['alteracoes_indevidas']and i['chamadas_1_a_834_preservadas'],'Preservação histórica')
 check(codigo()==read('adendo_aprovado.json')['codigo'],'Código congelado divergente')
 check(r['analises_H']=={'total':220,'ok':220},'Validade local H divergente')
 for d,refn in [('prazo',4),('custo',6)]:
  x=a['resumo_H'][d];check(x['referencias_nao_exatas']==refn and x['nao_exatos_preservados']==refn and x['falsa_precisao']==0,'Magnitude indevida H '+d)
  check(x['divergencias_numericas']==0,'Divergência numérica H '+d)
  check(inc['v7']['resumo']['H'][d]['direcao_excessiva_ou_contraditoria']==0,'Direção excessiva H')
 check(len(a['matriz_H'])==60 and tri['N_desfechos']==180,'Triagem incompleta')
 parciais={l['slot']['execucao_id']for l in n['linhas']if l['slot']['condicao']=='H'and any(q['classe']!='exato'for q in l['desfechos'].values())}
 check(parciais=={x['execucao_id']for x in read('auditoria_residual_final.json')['casos_H']},'Residual H não classificado')
 check(len(read('auditoria_erros_globais.json'))==11,'Erros globais não auditados')
 for log,numero in [('testes_h07_r3.log',23),('testes_carteira.log',6)]:
  s=(O/log).read_text();check(re.search(r'Ran '+str(numero)+r' tests\b',s)and s.rstrip().endswith('OK'),'Testes sem aprovação: '+log)
 for nota in read('notas_auditoria_manual.json')['notas']:
  f=O/nota['arquivo'];check(hashlib.sha256(f.read_bytes()).hexdigest()==nota['arquivo_sha256'],'Nota sem vínculo bruto')
  rr=json.loads(f.read_text());check(rr['metadados']['execucao_id']==nota['execucao_id'],'Nota/execução divergente')
  if 'contexto_hash'in nota:check(any(t.get('contexto',{}).get('contexto_hash')==nota['contexto_hash'] for t in rr['resultado']['rastro_orquestracao']),'Nota/contexto divergente')
  else:check(rr['resultado']['view_hash']==nota['view_hash'],'Nota/view divergente')
 with sqlite3.connect((O/'ledger_final.sqlite').resolve().as_uri()+'?mode=ro',uri=True)as db:
  nn,cc,ci=db.execute('select count(*),sum(comprometido),sum(custo_inferencia)from chamadas').fetchone()
  check((nn,cc,ci)==(1114,4480425665,2063925665),'Snapshot/carteira divergente')
  check(cc<=5000000000 and cc==r['carteira']['comprometido_nanoUSD'],'Teto/relatório financeiro')
  for sid,raw in db.execute('select id,resultado from slots_v07_r3'):
   check(json.loads(raw)==json.loads((O/(sid+'.json')).read_text()),'Bruto/snapshot divergente')
 documentos=[O/x for x in ['RELATORIO.md','DIAGNOSTICO.md','AUDITORIA_RESIDUAL.md','VALIDACAO.md']]+[ROOT/'TCC_Codigos/docs/desenvolvimento'/x for x in ['ETAPA_09_ACEITE_TECNICO.md','ETAPA_09_PILOTO_V07.md']]
 hashes={}
 for p in documentos:
  s=p.read_text();hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
  for target in re.findall(r'\]\(([^)]+)\)',s):
   if target.startswith(('https://','http://','#')):continue
   check((p.parent/target.split('#')[0]).exists(),'Link local inexistente: '+str(p)+' -> '+target)
 res=dict(criterios_tecnicos_atendidos=True,coorte_slots=90,testes_H=23,testes_carteira=6,analises_H_validas=220,referencias_nao_exatas_H_preservadas=dict(prazo=4,custo=6),H_exatos_corretos=dict(prazo=23,custo=21),residuais_H_classificados=len(parciais),rejeicoes_globais_auditadas=11,notas_manuais_vinculadas=9,comprometido_nanoUSD=cc,saldo_nanoUSD=5000000000-cc,codigo_congelado_preservado=True,links_locais_verificados=True,documentos_sha256=hashes,independencia_cientifica=False,etapas_10_11='não iniciadas')
 (O/'verificacao_entrega.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res,ensure_ascii=False))

if __name__=='__main__':main()
