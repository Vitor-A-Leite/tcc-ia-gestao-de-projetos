"""Relatório descritivo derivado dos artefatos pós-coleta, sem API."""
from pathlib import Path
import json
O=Path(__file__).parent

def ler(n):return json.loads((O/n).read_text())
def usd(n):return f'{n/1e9:.9f}'
def numero(n):return '—' if n is None else f'{n:.2f}'
def quantidade(q):return str(q['quantidade']['valor']) if q['classe']=='exato' else q['classe']+(' ('+q.get('quantidade',{}).get('direcao','')+')' if q['classe']=='direcao' else '')

def main():
 c=ler('comparacao_v06_v07.json');r=ler('resumo_descritivo.json');a=ler('contabilidade_e_erros.json');i=ler('integridade_final.json');audit=ler('auditoria_tecnica.json');w=r['carteira'];h=c['comparacao']['H']
 normal=ler('normalizacao.json');old=json.loads((O.parent/'etapa9_piloto_v06_20261027/normalizacao.json').read_text());oldmap={(l['slot']['caso_id'],l['slot']['repeticao'],l['slot']['condicao']):l for l in old['linhas']}
 p=h['desfechos']['prazo'];k=h['desfechos']['custo']
 linhas=['# Etapa 9 — piloto v7 e comparação com v6','',
 'Coorte completa da v7, revisão 7.2, iniciada em 28/10/2026 (America/Sao_Paulo). Duas rodadas de desenvolvimento foram paradas e preservadas (seis e 15 slots); os US$ 0,269021210 dessas rodadas permanecem no total acumulado. A primeira revelou falhas de escopo; a segunda, ambiguidades entre diagnóstico local, cálculo do solver e alteração de parâmetros. Execução autorizada diretamente pelo usuário, com meta de conclusão técnica da etapa 9 e teto acumulado de US$ 5.','',
 f'**H: prazo exato {p["cobertura_v06"]["n"]}/30 → {p["cobertura_v07"]["n"]}/30; custo exato {k["cobertura_v06"]["n"]}/30 → {k["cobertura_v07"]["n"]}/30.** Coleta encerrada em {i["slots"].get("terminado",0)}/90 slots. Comprometido acumulado: **US$ {usd(w["comprometido_nanoUSD"])}**; saldo interno: **US$ {usd(w["saldo_nanoUSD"])}**.','',
 '## Comparação principal','',
 '| Condição | Prazo exato v6 → v7 | Custo exato v6 → v7 | Mediana por execução, s v6 → v7 | Inferência conhecida, USD v6 → v7 |','|---|---:|---:|---:|---:|']
 for cond in 'BHT':
  x=c['comparacao'][cond];dp=x['desfechos']['prazo'];dc=x['desfechos']['custo']
  linhas.append(f'| {cond} | {dp["cobertura_v06"]["n"]}/30 → {dp["cobertura_v07"]["n"]}/30 | {dc["cobertura_v06"]["n"]}/30 → {dc["cobertura_v07"]["n"]}/30 | {numero(x["latencia_mediana_slot_v06_s"])} → {numero(x["latencia_mediana_slot_v07_s"])} | {usd(x["inferencia_v06_nanoUSD"])} → {usd(x["inferencia_v07_nanoUSD"])} |')
 linhas+=['','B: IA sem relações do grafo; H: grafo e interpretação por nó; T: IA com relações em texto. Mesmos 15 casos fictícios, duas repetições, inputs/views, modelo, configuração e ordem. B/T foram reexecutados com algoritmos preservados; suas variações não são atribuídas à mudança H. H passou a usar geração com JSON Schema estrito, enquanto B/T conservaram o modo JSON anterior. O ganho de validade não pode ser atribuído isoladamente ao grafo.','',
 '**Cobertura exata não é taxa de acerto.** O MAE usa apenas pares com previsão válida e referência autoral ambas exatas; ausências e indeterminações não recebem erro zero.','',
 '| Condição/desfecho | MAE v6 (n elegível) | MAE v7 (n elegível) | Ganhos / perdas de cobertura |','|---|---:|---:|---:|']
 for cond in 'BHT':
  for d in ('prazo','custo'):
   x=c['comparacao'][cond]['desfechos'][d]
   linhas.append(f'| {cond}/{d} | {numero(x["erro_v06"]["MAE"])} ({x["erro_v06"]["n"]}) | {numero(x["erro_v07"]["MAE"])} ({x["erro_v07"]["n"]}) | {x["ganharam"]} / {x["perderam"]} |')
 linhas+=['','MAE de prazo em dias; de custo em centavos.','',
 '## Calculabilidade e indeterminação H','',
 '| Desfecho | Referências exatas | Exatos corretos elegíveis v7 | Referências não exatas | Saídas não exatas válidas | Falsa precisão candidata |','|---|---:|---:|---:|---:|---:|']
 for d,x in audit['resumo_H'].items():
  linhas.append(f'| {d} | {x["referencias_exatas"]}/30 | {x["exatos_corretos_elegiveis"]} | {x["referencias_nao_exatas"]} | {x["nao_exatos_preservados"]} | {x["falsa_precisao"]} |')
 linhas+=['','As referências atuais permitem 26 prazos e 24 custos exatos, não 30 de cada. Preservar indeterminação requer saída indeterminada/direcional; erro de contrato não é contado como preservação. A inspeção técnica é do mesmo autor e não substitui auditoria independente.','',
 f'Direções sustentadas pelas referências e não recuperadas por H: cinco na v6 e {audit["resumo_H"]["custo"]["direcoes_sustentadas_nao_recuperadas"]} na v7, em custo. Preservar ausência de magnitude não garante recuperar toda a informação direcional disponível. T/k_23d8/1 declarou aumento de prazo onde a referência mantém direção desconhecida; achado separado de MAE e falsa magnitude, registrado em comparacao_incerteza.json.','',
 '## Alterações e validação','',
 'V7 pede apenas fatos/condições/propostas locais à LLM, deixa os deltas para o motor, nomeia explicitamente a alteração de parâmetros contratuais e usa JSON Schema estrito derivado das permissões locais, mantém validador independente, atribui IDs/hashes técnicos no adaptador, deriva direções redundantes dos valores exatos, exige checklist de cláusulas, aceita manutenção de duração somente com cláusula única e provas estruturais, e fecha prazo/custo separadamente. O JSON bruto e a resposta wire são conservados e confrontados com a análise interna, inclusive no cache. Pendências exclusivamente monetárias não apagam prazo com cobertura temporal completa. Nenhuma resposta histórica foi convertida ou reparada. Detalhes em [NOTAS_IMPLEMENTACAO.md](NOTAS_IMPLEMENTACAO.md).','',
 'V7 inicial: 126 testes aprovados. Revisão 7.1: 20 testes H, incluindo cinco de schema independente, e seis de carteira/integração; o envio do schema idêntico à contagem e à geração foi conferido em teste adicional. Revisão 7.2: 23 testes H e seis de carteira/integração, incluindo ausência de diagnóstico local, tradução de operação, crédito contratual e deltas negativos. Os controles vermelhos v6 permanecem preservados. Testes sintéticos não medem desempenho empírico.','',
 '## Falhas e encaminhamentos','',
 f'Análises locais H v6: `{json.dumps(c["analises_H_v06"],ensure_ascii=False)}`. H v7: `{json.dumps(c["analises_H_v07"],ensure_ascii=False)}`.','',
 f'Fechamentos H v7: `{json.dumps(c["fechamentos_H_v07"],ensure_ascii=False)}`. Encaminhamentos v7: `{json.dumps(c["estados_encaminhamentos"],ensure_ascii=False)}`. São ocorrências, não operações únicas. Proposta indeterminada pode resolver a responsabilidade sem fornecer número exato.','',
 f'Candidatos a divergência numérica/falsa precisão em todas as condições: {len(c["suspeitas_v06"])} na v6 e {len(c["suspeitas_v07"])} na v7. A lista completa está em `resumo_descritivo.json`; nenhuma saída é corrigida para coincidir com a referência.','',
 'As três execuções H com referências exatas ainda sem magnitude são k_547a/1, k_547a/2 (encaminhamento inadequado) e k_f04b/2 (omissão de confirmação estruturada). A última é uma perda pareada frente à v6. Houve oito ganhos/uma perda em prazo e seis ganhos/uma perda em custo. B/k_6d82/2 previu custo zero contra +15000 centavos, explicando seu MAE de R$16,67 nos nove pares elegíveis.','',
 'Inspeção por caso e causas remanescentes: [AUDITORIA_RESIDUAL.md](AUDITORIA_RESIDUAL.md), [DIAGNOSTICO.md](DIAGNOSTICO.md), `auditoria_tecnica.json`, `triagem_todas_condicoes.json` e `notas_auditoria_manual.json`. A triagem usa referências completas; uma falta de magnitude em B não é automaticamente erro, pois sua view omite relações e a inferibilidade ainda requer auditoria.','',
 '## Custo e preservação','',
 '| Parcela | USD |','|---|---:|',
 '| Comprometido antes desta revisão | 3.477660900 |',
 f'| Incremento comprometido v7 revisão 7.2 | {usd(a["comprometido_nanoUSD"])} |',
 f'| Inferência conhecida v7 | {a["uso_conciliado"]["custo_inferencia_USD"]} |',
 f'| Provisão de contagem v7 | {usd(a["provisao_contagem_hipotetica_nanoUSD"])} |',
 f'| Inferência conhecida acumulada | {usd(w["inferencia_conhecida_nanoUSD"])} |',
 f'| Reserva de inferência desconhecida acumulada | {usd(w["reserva_inferencia_desconhecida_nanoUSD"])} |',
 f'| Provisão de contagem acumulada | {usd(w["provisao_contagem_nanoUSD"])} |',
 f'| **Comprometido acumulado** | **{usd(w["comprometido_nanoUSD"])}** |',
 f'| **Saldo sob teto US$ 5** | **{usd(w["saldo_nanoUSD"])}** |','',
 f'{i["tentativas_novas"]} chamadas novas; {w["tentativas"]} tentativas acumuladas. Custos desconhecidos históricos preservados: {w["custos_desconhecidos"]}. Comprometimento inclui reservas/provisões e não equivale à fatura. Provisão de US$ 0,002 por contagem é hipótese conservadora, não tarifa comprovada.','',
 'Modelo gpt-6-luna/High, Standard, cache 30 min, streaming; entrada oficial ≤16 mil e saída total ≤25 mil tokens, 180 s por chamada, H ≤8 chamadas/1.500 s. Sem retries/fallback. Preços por milhão de tokens: entrada 0,10; cache lido 0,01; cache escrito 30 min 0,125; saída 0,50 USD. Custo reconciliado também por aritmética racional independente. Fontes oficiais consultadas antes da coleta: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [cache](https://developers.openai.com/api/docs/guides/prompt-caching).','',
 f'Código congelado, tabelas históricas, chamadas 1–834 e {i["arquivos_inventariados"]} arquivos preexistentes conferidos. Maior entrada oficial: {i["max_contagem_oficial"]} tokens. Paradas: `{json.dumps(i["parada"],ensure_ascii=False)}`. Snapshots antes/depois separados. Apenas carteira e resumos STATUS/PLANO admitem alterações previstas.','',
 '## Limites e conclusão da etapa','',
 'Comparação descritiva de desenvolvimento. Prompt, contrato e coordenação H mudaram juntos; não há isolamento causal nem prova de superioridade. Referências autorais, inferibilidade por view e suporte semântico seguem sem revisão independente. Etapas 10/11 não iniciadas. O [critério](../../docs/desenvolvimento/ETAPA_09_CRITERIO_CONCLUSAO.md) e o [aceite técnico](../../docs/desenvolvimento/ETAPA_09_ACEITE_TECNICO.md) registram a conclusão da etapa 9 e as limitações remanescentes. Reprodução offline em [VALIDACAO.md](VALIDACAO.md).','']
 (O/'RELATORIO.md').write_text('\n'.join(linhas))
 diag=['# Diagnóstico v6 → v7 por caso','', 'Previsões originais; prazo em dias e custo em centavos. Referências autorais, sem independência científica.','', '| Caso / repetição | Prazo v6 | Prazo v7 | Custo v6 | Custo v7 |','|---|---:|---:|---:|---:|']
 for l in normal['linhas']:
  s=l['slot']
  if s['condicao']!='H':continue
  prev=oldmap[(s['caso_id'],s['repeticao'],'H')]
  diag.append('| '+s['caso_id']+' / '+str(s['repeticao'])+' | '+' | '.join(quantidade(x) for x in (prev['desfechos']['prazo'],l['desfechos']['prazo'],prev['desfechos']['custo'],l['desfechos']['custo']))+' |')
 diag+=['','## Casos sem dois valores exatos','']
 for caso in audit['casos_H']:
  if all(q['classe']=='exato' for q in caso['previsao'].values()):continue
  diag+=['### '+caso['caso_id']+' / '+str(caso['repeticao']),'',f'Estado: {caso["estado"]}. Referência: prazo {caso["referencia"]["prazo"]["estado"]}; custo {caso["referencia"]["custo"]["estado"]}.','', 'Lacunas finais: '+json.dumps(caso['lacunas'],ensure_ascii=False)+'.','', 'Rejeições locais: '+json.dumps(caso['erros_locais'],ensure_ascii=False)+'.','', 'Rejeições operacionais: '+json.dumps(caso['decisoes_rejeitadas'],ensure_ascii=False)+'.','', 'Pendências tipadas: '+json.dumps(caso['pendencias_tipadas'],ensure_ascii=False)+'.','']
 (O/'DIAGNOSTICO.md').write_text('\n'.join(diag))
 print('Relatório e diagnóstico derivados salvos')

if __name__=='__main__':main()
