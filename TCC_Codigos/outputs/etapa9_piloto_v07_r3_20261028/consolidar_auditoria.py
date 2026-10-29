"""Consolida classificação técnica documentada, preservando previsões e referências."""
from pathlib import Path
import json,hashlib
O=Path(__file__).parent

def read(n):return json.loads((O/n).read_text())
def texto(q):
 return str(q['quantidade']['valor'])if q['classe']=='exato'else(q['classe']+' / '+q.get('quantidade',{}).get('direcao','—'))

def main():
 a=read('auditoria_tecnica.json');records=[]
 for c in a['casos_H']:
  if all(q['classe']=='exato'for q in c['previsao'].values()):continue
  case=c['caso_id'];rep=c['repeticao']
  if case=='k_23d8':
   categoria='lacuna factual e confirmação operacional não fornecida';causa='Sem aceite/definição técnica. Propostas desconhecidas tiveram condição indeterminada e foram rejeitadas; direção de aumento do custo não recuperada.'
   assert c['decisoes_rejeitadas']
  elif case=='k_547a':
   categoria='encaminhamento de operação inadequada';causa='Fornecedor pediu substituir_restricao/r_08f271 para uma isenção de cobrança. Responsável alterou corretamente c_724f; pedido temporal não foi confirmado.'
   assert any('r_08f271'in s for s in c['lacunas'])
  elif case=='k_8c65':
   categoria='lacuna factual exclusivamente monetária';causa='Preço de extensão desconhecido; prazo +2 preservado. '+('Pendência tipada de custo torna a direção desconhecida.'if rep==1 else'Aumento do custo preservado sem magnitude.')
   assert c['previsao']['prazo']['quantidade']['valor']==2
  elif case=='k_d307':
   categoria='lacuna factual de duração';causa='Duração nova da usinagem desconhecida. Prazo sem magnitude/direção; custo em aumento sem magnitude.'
   assert c['previsao']['prazo']['classe']=='indeterminado'and c['previsao']['custo']['classe']=='direcao'
  elif case=='k_f04b'and rep==2:
   categoria='omissão de confirmação estruturada';causa='Justificativa diz que montagem permanece igual, mas propostas e índices da cláusula estão vazios. Política conservadora mantém duração e custo pendentes.'
   assert any('u_813c'in s for s in c['lacunas'])
  else:raise ValueError('Caso residual sem classificação técnica: '+str((case,rep)))
  f=O/(c['execucao_id']+'.json')
  records.append(dict(execucao_id=c['execucao_id'],caso=case,repeticao=rep,categoria=categoria,causa=causa,previsao=c['previsao'],referencia=c['referencia'],arquivo=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),evidencia_operacional=dict(lacunas=c['lacunas'],rejeicoes=c['decisoes_rejeitadas'],pendencias_tipadas=c['pendencias_tipadas'])))
 if len(records)!=9:raise ValueError('Quantidade residual não corresponde à inspeção documentada')
 (O/'auditoria_residual_final.json').write_text(json.dumps(dict(natureza='Inspeção técnica do mesmo autor, não independente; nenhuma previsão alterada.',casos_H=records,outras_condicoes='triagem_todas_condicoes.json; auditoria_erros_globais.json; notas_auditoria_manual.json'),ensure_ascii=False,indent=2)+'\n')
 linhas=['# Auditoria técnica dos resultados restantes','',
 'Coorte v7 revisão 7.2, 90/90 execuções. Inspeção do mesmo autor, sem independência científica. Nenhuma resposta, referência ou resultado numérico foi reparado.','',
 '## Por que H não produz 30 valores exatos','',
 'As referências autorais permitem 26 prazos e 24 custos exatos. H recuperou 23 e 21, todos coincidentes com essas referências. As quatro magnitudes de prazo e seis de custo realmente desconhecidas permaneceram não exatas. As três execuções com referências exatas ainda não quantificadas são k_547a/1, k_547a/2 e k_f04b/2.','',
 '| Caso / repetição | Prazo H | Custo H, centavos | Categoria e evidência |','|---|---|---|---|']
 for c in records:linhas.append(f'| [{c["caso"]}/{c["repeticao"]}]({c["arquivo"]}) | {texto(c["previsao"]["prazo"])} | {texto(c["previsao"]["custo"])} | {c["categoria"]}: {c["causa"]} |')
 linhas+=['',
 'k_547a: a operação contratual correta estava no contexto e no schema. O catálogo usa IDs sem descrição adicional do contrato; não houve ablação para separar efeito da apresentação e interpretação do modelo. Ambas as repetições v6 também eram parciais, por direção/hash; esses erros formais desapareceram, mas permaneceu a escolha inadequada de operação.','',
 'k_f04b/2: regressão pareada de cobertura, pois a v6 retornava -1 dia e -10000 centavos. A v7 não converte justificativa livre em confirmação operacional. A primeira repetição v7 resolveu a cláusula explicitamente e produziu os valores corretos. A exigência conservadora de resolver todas as cláusulas locais também deve ser revista quanto à aplicabilidade na etapa 10.','',
 'Perdas de direção sustentada de custo: k_23d8/1, k_23d8/2 e k_8c65/1. São três na v7, ante cinco na v6. Preservar ausência de magnitude não significa recuperar toda a informação disponível. Não houve magnitude exata indevida nem divergência numérica em H; isso é uma observação desta amostra autoral.','',
 '## Controles B/T','',
 'B/k_6d82/2 previu delta de custo zero, contra +15000 centavos na referência completa. Sua justificativa confundiu ausência de aditivo com ausência de cobrança por extensão; f_493d L01 exige aditivo para crédito por antecipação, enquanto extensão adicional já é cobrada pela regra vigente. Erro absoluto R$150; MAE de custo B R$16,67 nos nove pares elegíveis. A inferibilidade da magnitude por view B segue pendente; uma falta de relações não justifica afirmar zero.','',
 'T/k_23d8/1 previu aumento de prazo sem magnitude, embora a referência mantenha direção desconhecida devido a aceite/espera/duração não definidos. É um achado de direção excessiva frente à referência, separado do MAE e de falsa magnitude. A revisão independente permanece pendente.','',
 'Onze saídas globais foram rejeitadas: oito sem justificativa, duas com ID de fonte inexistente na entrada e uma com localizador divergente. A inspeção inclui as fontes serializadas dentro do texto relacional de T, conforme o contrato.','',
 '| Execução | Call | Rejeição observada no bruto |','|---|---:|---|']
 for e in read('auditoria_erros_globais.json'):
  sid=e['execucao_id'];label=sid.split('20261028-')[1]
  causa='Campo justificativa ausente'if e.get('campos_ausentes')else json.dumps(e['referencias_invalidas'],ensure_ascii=False)
  linhas.append(f'| [{label}]({sid}.json) | {e["call_id"]} | {causa} |')
 linhas+=['',
 'Os 25 desfechos B sem magnitude apesar de referência completa exata estão individualizados em triagem_todas_condicoes.json, com lacunas e justificativas. Eles não são automaticamente erros: B omite relações, e inferibilidade por view requer auditoria própria. As 180 combinações execução/desfecho foram classificadas; invalidade não foi tratada como acerto ou como preservação de conhecimento.','',
 '## Evidências e limite de conclusão','',
 'Fontes/trechos das lacunas: auditoria_lacunas_fontes.json. Notas com hashes de arquivos/contextos: notas_auditoria_manual.json. Matriz completa H: auditoria_tecnica.json. Comparação de magnitude/direção v6/v7: comparacao_incerteza.json. Erros globais reproduzíveis: auditar_erros_globais.py.','',
 'Os controles demonstram funcionamento do contrato e as falhas registradas. Não certificam suporte semântico de todas as respostas, validade independente dos gabaritos ou superioridade isolada do grafo. H usa schema estrito e B/T mantiveram modo JSON; diferenças de contrato influenciam a validade. Etapas 10/11 não iniciadas.','']
 (O/'AUDITORIA_RESIDUAL.md').write_text('\n'.join(linhas))
 print('Nove execuções H parciais classificadas, onze rejeições globais e achados B/T documentados.')

if __name__=='__main__':main()
