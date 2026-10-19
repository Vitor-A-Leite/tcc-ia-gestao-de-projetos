# Resultados da validação local do TCC

## Escopo e execução

- 34 testes automatizados passaram com rede bloqueada.
- Integridade: 40 nós, 65 arestas válidas e 36 cenários com IDs únicos.
- Os três notebooks têm sintaxe Python válida e caminhos locais portáveis.
- A preparação local foi executada pelo terminal, sem API.
- Baseline e híbrido foram executados integralmente em simulação, incluindo os 36 casos por condição. Respostas de referência foram injetadas; isso não mede o LLM.
- Piloto real: 6 cenários por condição, 12 respostas distintas da API, sem falhas de API, parsing ou validação.
- Mesmo modelo configurado nas duas condições: `gpt-6-luna`. Prompt baseline V2 e interpretador híbrido V1 preservados.
- Nenhum experimento real de 36 casos foi executado. Os pilotos não foram repetidos para escolher uma resposta melhor.

## Comparação do piloto real

As métricas de entidades e artefatos abaixo usam microagregação sobre pares cenário/elemento. O mesmo conjunto de seis referências foi usado em ambas as condições. Quando os conjuntos são vazios por cenário, precision e recall são 1, seguindo `set_metrics`; casos vazios não acrescentam verdadeiros positivos à microagregação. O tipo de evento usa acurácia por cenário.

| Métrica | Baseline | Híbrido |
|---|---:|---:|
| Acurácia do tipo de evento | 100,0% | 83,3% |
| Precisão de documentos | 100,0% | 78,6% |
| Recall de documentos | 72,7% | 100,0% |
| F1 de documentos | 84,2% | 88,0% |
| Precisão de entidades | 85,7% | 22,7% |
| Recall de entidades | 33,3% | 83,3% |
| F1 de entidades | 48,0% | 35,7% |

## Casos, sem ocultar erros

| Cenário | Referência | Tipo baseline | Tipo híbrido | F1 entidades baseline | F1 entidades híbrido |
|---|---|---|---|---:|---:|
| S001 | delay | delay | delay | 25,0% | 60,0% |
| S003 | test_problem | test_problem | test_problem | 80,0% | 26,7% |
| S007 | supplier_change | supplier_change | supplier_change | 33,3% | 47,1% |
| S009 | informational | informational | informational | 100,0% | 100,0% |
| S024 | test_problem | test_problem | test_problem | 66,7% | 35,3% |
| S035 | informational | informational | supplier_change | 100,0% | 0,0% |

## O que precisa ser revisado antes de congelar

1. **Interpretação do S035:** o baseline respeitou a ausência explícita de mudança de peça, prazo ou inspeção. O híbrido classificou o texto como `supplier_change`, com confiança declarada de 0,94, e gerou 15 entidades extras e 3 documentos extras. A confiança é declarada pelo modelo, sem calibração demonstrada. O bloqueio de propagação para `informational` continua funcionando, mas não se aplica quando o interpretador escolhe outro tipo.
2. **Propagação muito ampla:** nos seis casos, o híbrido teve 51 falsos positivos e 3 falsos negativos de entidades; o baseline teve 1 falso positivo e 12 falsos negativos. O percurso atual segue todas as relações direcionadas, inclusive `belongs_to` e relações de validação, sem política específica por evento. Devemos definir os critérios de impacto antes de alterar o algoritmo ou as referências.
3. **Entidade principal ausente:** no híbrido, `C_MOTOR` no S001, `TEST_LOAD` no S003 e `C_SENSOR` no S024 foram identificados como entidades principais, mas não entraram na lista final de impactados, embora estejam nas referências. O pipeline adiciona as entidades relacionadas e os descendentes, mas não a principal. Como fornecedores de origem nem sempre devem contar como impactados, simplesmente incluir toda entidade principal também pode aumentar falsos positivos; a regra precisa ser explicitada por papel/tipo.
4. **Comparação ainda exploratória:** o híbrido teve melhor recall de entidades e F1 de documentos neste piloto, mas pior precisão e F1 de entidades. Seis cenários, uma execução por condição e prompts diferentes não permitem confirmar a hipótese geral do TCC.

Nenhum prompt, referência ou regra científica foi ajustado depois de observar este piloto. Os erros foram preservados para revisão. O próximo passo é acordar e documentar as regras de propagação e a distinção entre entidade de origem e entidade afetada; depois revisar o prompt usando somente os casos de desenvolvimento, versionar as alterações e repetir o piloto em uma nova pasta. Só então congelar o protocolo para os 36 casos.

## Evidências e reprodução

- `01_testes_automatizados.log`: suíte completa sem rede.
- `02_preparacao_local.log`: preparação local pelo terminal.
- `requirements_instalados.txt`: versões instaladas nesta rodada.
- `00_integridade.json`: conferência estrutural dos dados.
- `03_pilotos_simulados/`: piloto com respostas de referência injetadas.
- `04_simulacao_completa/`: saídas simuladas dos 36 casos, rotuladas como simulação.
- `05_pilotos_reais/manifest.json`: hashes, versões, modelo, IDs do piloto e parâmetros de execução.
- `05_pilotos_reais/baseline/records.jsonl` e `hybrid/records.jsonl`: respostas brutas, previsões, tempos, IDs e uso de tokens; cada resposta foi salva incrementalmente.
- `COMPARACAO_PILOTO.json` e `.csv`: comparação uniforme das duas condições, incluindo listas de entidades extras e faltantes.

Uso registrado: 13484 tokens de entrada e 3643 de saída. Isso não é uma fatura nem uma estimativa monetária.
