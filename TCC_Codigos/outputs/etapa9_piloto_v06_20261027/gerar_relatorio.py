"""Relatório descritivo somente após avaliação e verificação de integridade."""
from pathlib import Path
from collections import Counter
import json
O=Path(__file__).parent

def ler(nome):return json.loads((O/nome).read_text())
def usd(n):return f'{n/1e9:.9f}'
def num(x):return '—'if x is None else str(round(x,3))
def main():
 c=ler('comparacao_v05_v06.json');d=ler('resumo_descritivo.json');a=ler('contabilidade_e_erros.json');i=ler('integridade_final.json')
 carteira=d['carteira'];terminados=i['slots'].get('terminado',0)
 linhas=['# Etapa 9 — piloto v06 e comparação com v05','',
 '27/10/2026, America/Sao_Paulo. Nova coorte autorizada pelo usuário: “Pode integrar a v6 e rodar um novo piloto, mantendo o limite acumulado de US$ 5. Depois me mostre a comparação com a v5.”','',
 f'**{terminados}/90 execuções encerradas.** Paradas registradas: `{json.dumps(i["parada"],ensure_ascii=False)}`. Nenhum resultado v04/v05 foi substituído; nenhuma resposta desta coorte foi reparada ou reenviada. Etapas 10/11 não iniciadas.','',
 '## Escopo e versões','',
 '15 casos fictícios (Bancada Íris e Estação Nácar), B/H/T, duas repetições, mesma ordem e mesmos inputs/views, modelo e parâmetros da v05. B = IA sem relações do grafo; H = grafo com interpretação por nó; T = IA com relações em texto. H muda para formato 6.0, contexto/resposta 3.0, política 6.0 e fronteira 3.0-h. O novo catálogo informa responsáveis e o fechamento confere encaminhamentos contra propostas aceitas. A avaliação usa manifesto 3.0-manifesto-h06.','',
 'Modelo gpt-6-luna, raciocínio High, streaming, Standard/cache 30 min, 180 s totais por chamada contando contagem e inferência, entrada oficial ≤16.000 tokens, saída total ≤25.000 tokens, H ≤8 chamadas/análises e 1.500 s. Sem retries ou fallback. Até 300 tentativas novas; teto monetário acumulado prevalece sobre o teto de 810 tentativas globais.','',
 '## Cobertura exata e erro numérico','',
 '| Condição/desfecho | Cobertura exata v05 | Cobertura exata v06 | MAE v05 (n) | MAE v06 (n) |',
 '|---|---:|---:|---:|---:|']
 for cond in 'BHT':
  for des,unidade in (('prazo','dias'),('custo','centavos')):
   q=c['comparacao'][cond]['desfechos'][des];a5,a6=q['erro_v05'],q['erro_v06']
   linhas.append(f'| {cond}/{des} ({unidade}) | {q["cobertura_v05"]["n"]}/30 | {q["cobertura_v06"]["n"]}/30 | {num(a5["MAE"])} ({a5["n"]}) | {num(a6["MAE"])} ({a6["n"]}) |')
 linhas+=['','N=30 planejados por condição. Cobertura exata é o número de previsões válidas com quantidade exata; não é taxa de suporte semântico. MAE inclui somente previsão exata válida e referência autoral exata. Os demais resultados permanecem nos denominadores, com classe própria; nunca recebem erro zero por ausência.','',
 '## Transições por caso e repetição','',
 '| Condição/desfecho | Ganhou cobertura exata | Perdeu cobertura exata | Exato nas duas |','|---|---:|---:|---:|']
 for cond in 'BHT':
  for des in ('prazo','custo'):
   q=c['comparacao'][cond]['desfechos'][des]
   linhas.append(f'| {cond}/{des} | {q["ganharam"]} | {q["perderam"]} | {q["exatos_nas_duas"]} |')
 linhas+=['','Todos os 90 pares foram conferidos em caso, repetição, condição, hashes de view/snapshot/evento, versão, modelo e configuração. A tabela completa está em `comparacao_por_caso.csv`; o JSON inclui hashes dos resultados originais. Ganho/perda significa disponibilidade de valor exato, não adjudicação científica.','',
 '## Operação, latência e custo','',
 '| Condição | Estados v05 | Estados v06 | Tentativas v05 → v06 | Mediana por execução, s v05 → v06 | Inferência conhecida USD v05 → v06 |','|---|---|---|---:|---:|---:|']
 for cond in 'BHT':
  q=c['comparacao'][cond]
  linhas.append(f'| {cond} | `{json.dumps(q["estados_v05"],ensure_ascii=False)}` | `{json.dumps(q["estados_v06"],ensure_ascii=False)}` | {q["tentativas_v05"]} → {q["tentativas_v06"]} | {num(q["latencia_mediana_slot_v05_s"])} → {num(q["latencia_mediana_slot_v06_s"])} | {usd(q["inferencia_v05_nanoUSD"])} → {usd(q["inferencia_v06_nanoUSD"])} |')
 linhas+=['','Latência por execução inclui contagem oficial, inferência, adaptação e coordenação. H contém várias chamadas. A v05 conserva uma falha DNS inicial B sem inferência, e as coletas ocorreram em momentos diferentes. B/T foram reexecutados com algoritmos preservados; suas diferenças não são atribuídas à alteração H.','',
 '## Encaminhamentos e falhas H','',
 f'Análises H v05: `{json.dumps(c["analises_H_v05"],ensure_ascii=False)}`. Análises H v06: `{json.dumps(c["analises_H_v06"],ensure_ascii=False)}`.','',
 f'Fechamentos v05: `{json.dumps(c["fechamentos_H_v05"],ensure_ascii=False)}`. Fechamentos v06: `{json.dumps(c["fechamentos_H_v06"],ensure_ascii=False)}`. Encaminhamentos aceitos para conferência: `{json.dumps(c["estados_encaminhamentos"],ensure_ascii=False)}`.','',
 'Esses totais contam ocorrências de encaminhamentos nas análises aceitas e incorporadas ao fechamento, não operações únicas: vários nós podem encaminhar a mesma operação ao mesmo responsável. Respostas localmente rejeitadas permanecem no rastro e não contam como encaminhamentos resolvidos. Uma resolução operacional não prova que a evidência sustenta a interpretação; uma proposta indeterminada pode resolver a rota sem tornar o valor exato.','',
 f'Candidatas a divergência numérica ou falsa precisão: {len(c["suspeitas_v05"])} na v05 e {len(c["suspeitas_v06"])} na v06. São sinais para revisão contra referências autorais, não auditoria semântica automática. Ausência de sinal não prova suporte.','',
 '## Carteira única acumulada','',
 '| Parcela | USD |','|---|---:|',
 '| Comprometido antes da v06 | 2.096607180 |',
 f'| Comprometimento incremental v06 | {usd(a["comprometido_nanoUSD"])} |',
 f'| Inferência incremental conhecida v06 | {a["uso_conciliado"]["custo_inferencia_USD"]} |',
 f'| Inferência conhecida acumulada | {usd(carteira["inferencia_conhecida_nanoUSD"])} |',
 f'| Reserva de inferência desconhecida acumulada | {usd(carteira["reserva_inferencia_desconhecida_nanoUSD"])} |',
 f'| Provisão hipotética de contagem acumulada | {usd(carteira["provisao_contagem_nanoUSD"])} |',
 f'| **Comprometido acumulado** | **{usd(carteira["comprometido_nanoUSD"])}** |',
 f'| **Saldo interno sob US$ 5** | **{usd(carteira["saldo_nanoUSD"])}** |','',
 f'{carteira["tentativas"]} tentativas acumuladas, {i["tentativas_novas"]} novas. Custos não conciliados: {carteira["custos_desconhecidos"]}. Reservas históricas preservadas. Comprometimento inclui reservas/provisões, não equivale à fatura. A provisão de contagem de US$ 0,002 por tentativa é hipótese operacional conservadora, não tarifa confirmada.','',
 'Preços Standard verificados antes da coleta: US$ 0,10/M entrada, US$ 0,01/M leitura de cache, US$ 0,125/M escrita 30 min, US$ 0,50/M saída. Reserva máxima de inferência US$ 0,0145 por chamada, mais a provisão. O custo conhecido foi recalculado com aritmética racional a partir do usage, sem duplicar escrita de cache. Fontes: [modelo GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) e [contabilidade de cache](https://developers.openai.com/api/docs/guides/prompt-caching).','',
 '## Verificações e preservação','',
 f'55 testes offline antes da coleta: 6 integração/carteira, 27 H v06 e 22 SSE. Snapshots antes/depois separados. Verificados {i["arquivos_inventariados"]} arquivos preexistentes; somente ledger e resumos de status/plano admitem alterações. Tabelas históricas e chamadas 1–510 preservadas; código congelado e JSONs por slot conferidos. Maior entrada oficial observada: {i["max_contagem_oficial"]} tokens.','',
 'A revisão automática inicialmente rejeitou a execução por suspeita de dados sensíveis sem autorização específica. A verificação documentou que os inputs são dois projetos inteiramente fictícios, com loader restrito a oito JSONs; nenhum documento pessoal entra nos prompts. O mesmo comando foi reapresentado com essas evidências e aprovado. A rejeição ocorreu antes de criar a coorte ou reservar chamada. `escopo_dados_verificado.json` conserva a evidência.','',
 '## Limitações e próximo passo','',
 'Comparação descritiva entre rodadas. Mudaram prompt/contrato/coordenação H; não há isolamento causal do efeito dessas mudanças nem prova de superioridade. Referências autorais, inferibilidade por view e suporte semântico continuam sem auditoria independente. Rejeições de contrato, indeterminação, encaminhamentos e valores exatos devem ser revisados separadamente. Não houve ajuste seletivo de respostas ou prompts durante a coleta.','',
 'Revisar os achados e as limitações antes de congelar o protocolo e iniciar as etapas 10/11. Arquivos centrais: `comparacao_v05_v06.json`, `comparacao_por_caso.csv`, `normalizacao.json`, `avaliacao_autoral.json`, `contabilidade_e_erros.json`, `resumo_descritivo.json`, `integridade_final.json` e os JSONs originais por execução.','']
 linhas[6:6]=['**Achado principal:** H passou de 9/30 para 16/30 previsões exatas de prazo e custo (30% → 53,3%). São oito ganhos e uma perda nos pares correspondentes. MAE zero apenas nos 16 pares exatos elegíveis de cada desfecho. A mediana de latência H passou de 108,95 s para 230,47 s; a inferência H conhecida aumentou 66,2%. Rejeições locais passaram de 2/178 para 8/203 análises.','',
 'Há um candidato a falsa precisão em B/k_d307/1: aumento exato de 2.500 centavos frente a referência autoral apenas direcional com limite inferior. Por isso B tem oito custos exatos retornados, mas sete pares elegíveis ao MAE. A revisão de casos e próximos pontos está em [DIAGNOSTICO.md](DIAGNOSTICO.md), com extrações e hashes em [diagnosticos_comparativos.json](diagnosticos_comparativos.json).','']
 (O/'RELATORIO.md').write_text('\n'.join(linhas))
 print('Relatório salvo:',O/'RELATORIO.md')
if __name__=='__main__':main()
