# Etapa 9 — piloto v06 e comparação com v05

27/10/2026, America/Sao_Paulo. Nova coorte autorizada pelo usuário: “Pode integrar a v6 e rodar um novo piloto, mantendo o limite acumulado de US$ 5. Depois me mostre a comparação com a v5.”

**90/90 execuções encerradas.** Paradas registradas: `[]`. Nenhum resultado v04/v05 foi substituído; nenhuma resposta desta coorte foi reparada ou reenviada. Etapas 10/11 não iniciadas.

**Achado principal:** H passou de 9/30 para 16/30 previsões exatas de prazo e custo (30% → 53,3%). São oito ganhos e uma perda nos pares correspondentes. MAE zero apenas nos 16 pares exatos elegíveis de cada desfecho. A mediana de latência H passou de 108,95 s para 230,47 s; a inferência H conhecida aumentou 66,2%. Rejeições locais passaram de 2/178 para 8/203 análises.

Há um candidato a falsa precisão em B/k_d307/1: aumento exato de 2.500 centavos frente a referência autoral apenas direcional com limite inferior. Por isso B tem oito custos exatos retornados, mas sete pares elegíveis ao MAE. A revisão de casos e próximos pontos está em [DIAGNOSTICO.md](DIAGNOSTICO.md), com extrações e hashes em [diagnosticos_comparativos.json](diagnosticos_comparativos.json).

## Escopo e versões

15 casos fictícios (Bancada Íris e Estação Nácar), B/H/T, duas repetições, mesma ordem e mesmos inputs/views, modelo e parâmetros da v05. B = IA sem relações do grafo; H = grafo com interpretação por nó; T = IA com relações em texto. H muda para formato 6.0, contexto/resposta 3.0, política 6.0 e fronteira 3.0-h. O novo catálogo informa responsáveis e o fechamento confere encaminhamentos contra propostas aceitas. A avaliação usa manifesto 3.0-manifesto-h06.

Modelo gpt-6-luna, raciocínio High, streaming, Standard/cache 30 min, 180 s totais por chamada contando contagem e inferência, entrada oficial ≤16.000 tokens, saída total ≤25.000 tokens, H ≤8 chamadas/análises e 1.500 s. Sem retries ou fallback. Até 300 tentativas novas; teto monetário acumulado prevalece sobre o teto de 810 tentativas globais.

## Cobertura exata e erro numérico

| Condição/desfecho | Cobertura exata v05 | Cobertura exata v06 | MAE v05 (n) | MAE v06 (n) |
|---|---:|---:|---:|---:|
| B/prazo (dias) | 4/30 | 5/30 | 0 (4) | 0 (5) |
| B/custo (centavos) | 8/30 | 8/30 | 0 (8) | 0 (7) |
| H/prazo (dias) | 9/30 | 16/30 | 0 (9) | 0 (16) |
| H/custo (centavos) | 9/30 | 16/30 | 0 (9) | 0 (16) |
| T/prazo (dias) | 23/30 | 21/30 | 0 (23) | 0 (21) |
| T/custo (centavos) | 21/30 | 20/30 | 0 (21) | 0 (20) |

N=30 planejados por condição. Cobertura exata é o número de previsões válidas com quantidade exata; não é taxa de suporte semântico. MAE inclui somente previsão exata válida e referência autoral exata. Os demais resultados permanecem nos denominadores, com classe própria; nunca recebem erro zero por ausência.

## Transições por caso e repetição

| Condição/desfecho | Ganhou cobertura exata | Perdeu cobertura exata | Exato nas duas |
|---|---:|---:|---:|
| B/prazo | 1 | 0 | 4 |
| B/custo | 2 | 2 | 6 |
| H/prazo | 8 | 1 | 8 |
| H/custo | 8 | 1 | 8 |
| T/prazo | 3 | 5 | 18 |
| T/custo | 3 | 4 | 17 |

Todos os 90 pares foram conferidos em caso, repetição, condição, hashes de view/snapshot/evento, versão, modelo e configuração. A tabela completa está em `comparacao_por_caso.csv`; o JSON inclui hashes dos resultados originais. Ganho/perda significa disponibilidade de valor exato, não adjudicação científica.

## Operação, latência e custo

| Condição | Estados v05 | Estados v06 | Tentativas v05 → v06 | Mediana por execução, s v05 → v06 | Inferência conhecida USD v05 → v06 |
|---|---|---|---:|---:|---:|
| B | `{"erro": 8, "parcial": 18, "ok": 4}` | `{"erro": 6, "parcial": 19, "ok": 5}` | 30 → 30 | 39.024 → 32.72 | 0.062462700 → 0.064011000 |
| H | `{"parcial": 21, "ok": 9}` | `{"parcial": 14, "ok": 16}` | 178 → 203 | 108.952 → 230.467 | 0.279920255 → 0.465194260 |
| T | `{"ok": 21, "parcial": 6, "erro": 3}` | `{"ok": 20, "erro": 6, "parcial": 4}` | 30 → 30 | 25.681 → 23.234 | 0.057173250 → 0.056827250 |

Latência por execução inclui contagem oficial, inferência, adaptação e coordenação. H contém várias chamadas. A v05 conserva uma falha DNS inicial B sem inferência, e as coletas ocorreram em momentos diferentes. B/T foram reexecutados com algoritmos preservados; suas diferenças não são atribuídas à alteração H.

## Encaminhamentos e falhas H

Análises H v05: `{"total": 178, "ok": 176, "erro": 2, "erro:Identidade/revisão divergente: contexto_hash": 1, "erro:Direção incompatível": 1}`. Análises H v06: `{"total": 203, "ok": 195, "erro": 8, "erro:Direção incompatível": 5, "erro:Identidade/revisão divergente: contexto_hash": 3}`.

Fechamentos v05: `{"parcial": 20, "completo_operacional_condicional": 10}`. Fechamentos v06: `{"parcial": 13, "completo_operacional_condicional": 17}`. Encaminhamentos aceitos para conferência: `{"resolvido_operacional_condicional": 249, "pendente": 25}`.

Esses totais contam ocorrências de encaminhamentos nas análises aceitas e incorporadas ao fechamento, não operações únicas: vários nós podem encaminhar a mesma operação ao mesmo responsável. Respostas localmente rejeitadas permanecem no rastro e não contam como encaminhamentos resolvidos. Uma resolução operacional não prova que a evidência sustenta a interpretação; uma proposta indeterminada pode resolver a rota sem tornar o valor exato.

Candidatas a divergência numérica ou falsa precisão: 0 na v05 e 1 na v06. São sinais para revisão contra referências autorais, não auditoria semântica automática. Ausência de sinal não prova suporte.

## Carteira única acumulada

| Parcela | USD |
|---|---:|
| Comprometido antes da v06 | 2.096607180 |
| Comprometimento incremental v06 | 1.112032510 |
| Inferência incremental conhecida v06 | 0.58603251 |
| Inferência conhecida acumulada | 1.474139690 |
| Reserva de inferência desconhecida acumulada | 0.188500000 |
| Provisão hipotética de contagem acumulada | 1.546000000 |
| **Comprometido acumulado** | **3.208639690** |
| **Saldo interno sob US$ 5** | **1.791360310** |

773 tentativas acumuladas, 263 novas. Custos não conciliados: 13. Reservas históricas preservadas. Comprometimento inclui reservas/provisões, não equivale à fatura. A provisão de contagem de US$ 0,002 por tentativa é hipótese operacional conservadora, não tarifa confirmada.

Preços Standard verificados antes da coleta: US$ 0,10/M entrada, US$ 0,01/M leitura de cache, US$ 0,125/M escrita 30 min, US$ 0,50/M saída. Reserva máxima de inferência US$ 0,0145 por chamada, mais a provisão. O custo conhecido foi recalculado com aritmética racional a partir do usage, sem duplicar escrita de cache. Fontes: [modelo GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) e [contabilidade de cache](https://developers.openai.com/api/docs/guides/prompt-caching).

## Verificações e preservação

55 testes offline antes da coleta: 6 integração/carteira, 27 H v06 e 22 SSE. Snapshots antes/depois separados. Verificados 1208 arquivos preexistentes; somente ledger e resumos de status/plano admitem alterações. Tabelas históricas e chamadas 1–510 preservadas; código congelado e JSONs por slot conferidos. Maior entrada oficial observada: 10243 tokens.

A revisão automática inicialmente rejeitou a execução por suspeita de dados sensíveis sem autorização específica. A verificação documentou que os inputs são dois projetos inteiramente fictícios, com loader restrito a oito JSONs; nenhum documento pessoal entra nos prompts. O mesmo comando foi reapresentado com essas evidências e aprovado. A rejeição ocorreu antes de criar a coorte ou reservar chamada. `escopo_dados_verificado.json` conserva a evidência.

## Limitações e próximo passo

Comparação descritiva entre rodadas. Mudaram prompt/contrato/coordenação H; não há isolamento causal do efeito dessas mudanças nem prova de superioridade. Referências autorais, inferibilidade por view e suporte semântico continuam sem auditoria independente. Rejeições de contrato, indeterminação, encaminhamentos e valores exatos devem ser revisados separadamente. Não houve ajuste seletivo de respostas ou prompts durante a coleta.

Revisar os achados e as limitações antes de congelar o protocolo e iniciar as etapas 10/11. Arquivos centrais: `comparacao_v05_v06.json`, `comparacao_por_caso.csv`, `normalizacao.json`, `avaliacao_autoral.json`, `contabilidade_e_erros.json`, `resumo_descritivo.json`, `integridade_final.json` e os JSONs originais por execução.
