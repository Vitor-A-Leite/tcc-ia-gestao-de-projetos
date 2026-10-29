# Etapa 9 — piloto v7 e comparação com v6

Coorte completa da v7, revisão 7.2, iniciada em 28/10/2026 (America/Sao_Paulo). Duas rodadas de desenvolvimento foram paradas e preservadas (seis e 15 slots); os US$ 0,269021210 dessas rodadas permanecem no total acumulado. A primeira revelou falhas de escopo; a segunda, ambiguidades entre diagnóstico local, cálculo do solver e alteração de parâmetros. Execução autorizada diretamente pelo usuário, com meta de conclusão técnica da etapa 9 e teto acumulado de US$ 5.

**H: prazo exato 16/30 → 23/30; custo exato 16/30 → 21/30.** Coleta encerrada em 90/90 slots. Comprometido acumulado: **US$ 4.480425665**; saldo interno: **US$ 0.519574335**.

## Comparação principal

| Condição | Prazo exato v6 → v7 | Custo exato v6 → v7 | Mediana por execução, s v6 → v7 | Inferência conhecida, USD v6 → v7 |
|---|---:|---:|---:|---:|
| B | 5/30 → 5/30 | 8/30 → 9/30 | 32.72 → 33.88 | 0.064011000 → 0.063695500 |
| H | 16/30 → 23/30 | 16/30 → 21/30 | 230.47 → 106.94 | 0.465194260 → 0.320810515 |
| T | 21/30 → 22/30 | 20/30 → 20/30 | 23.23 → 22.90 | 0.056827250 → 0.058258750 |

B: IA sem relações do grafo; H: grafo e interpretação por nó; T: IA com relações em texto. Mesmos 15 casos fictícios, duas repetições, inputs/views, modelo, configuração e ordem. B/T foram reexecutados com algoritmos preservados; suas variações não são atribuídas à mudança H. H passou a usar geração com JSON Schema estrito, enquanto B/T conservaram o modo JSON anterior. O ganho de validade não pode ser atribuído isoladamente ao grafo.

**Cobertura exata não é taxa de acerto.** O MAE usa apenas pares com previsão válida e referência autoral ambas exatas; ausências e indeterminações não recebem erro zero.

| Condição/desfecho | MAE v6 (n elegível) | MAE v7 (n elegível) | Ganhos / perdas de cobertura |
|---|---:|---:|---:|
| B/prazo | 0.00 (5) | 0.00 (5) | 1 / 1 |
| B/custo | 0.00 (7) | 1666.67 (9) | 4 / 3 |
| H/prazo | 0.00 (16) | 0.00 (23) | 8 / 1 |
| H/custo | 0.00 (16) | 0.00 (21) | 6 / 1 |
| T/prazo | 0.00 (21) | 0.00 (22) | 5 / 4 |
| T/custo | 0.00 (20) | 0.00 (20) | 4 / 4 |

MAE de prazo em dias; de custo em centavos.

## Calculabilidade e indeterminação H

| Desfecho | Referências exatas | Exatos corretos elegíveis v7 | Referências não exatas | Saídas não exatas válidas | Falsa precisão candidata |
|---|---:|---:|---:|---:|---:|
| prazo | 26/30 | 23 | 4 | 4 | 0 |
| custo | 24/30 | 21 | 6 | 6 | 0 |

As referências atuais permitem 26 prazos e 24 custos exatos, não 30 de cada. Preservar indeterminação requer saída indeterminada/direcional; erro de contrato não é contado como preservação. A inspeção técnica é do mesmo autor e não substitui auditoria independente.

Direções sustentadas pelas referências e não recuperadas por H: cinco na v6 e 3 na v7, em custo. Preservar ausência de magnitude não garante recuperar toda a informação direcional disponível. T/k_23d8/1 declarou aumento de prazo onde a referência mantém direção desconhecida; achado separado de MAE e falsa magnitude, registrado em comparacao_incerteza.json.

## Alterações e validação

V7 pede apenas fatos/condições/propostas locais à LLM, deixa os deltas para o motor, nomeia explicitamente a alteração de parâmetros contratuais e usa JSON Schema estrito derivado das permissões locais, mantém validador independente, atribui IDs/hashes técnicos no adaptador, deriva direções redundantes dos valores exatos, exige checklist de cláusulas, aceita manutenção de duração somente com cláusula única e provas estruturais, e fecha prazo/custo separadamente. O JSON bruto e a resposta wire são conservados e confrontados com a análise interna, inclusive no cache. Pendências exclusivamente monetárias não apagam prazo com cobertura temporal completa. Nenhuma resposta histórica foi convertida ou reparada. Detalhes em [NOTAS_IMPLEMENTACAO.md](NOTAS_IMPLEMENTACAO.md).

V7 inicial: 126 testes aprovados. Revisão 7.1: 20 testes H, incluindo cinco de schema independente, e seis de carteira/integração; o envio do schema idêntico à contagem e à geração foi conferido em teste adicional. Revisão 7.2: 23 testes H e seis de carteira/integração, incluindo ausência de diagnóstico local, tradução de operação, crédito contratual e deltas negativos. Os controles vermelhos v6 permanecem preservados. Testes sintéticos não medem desempenho empírico.

## Falhas e encaminhamentos

Análises locais H v6: `{"total": 203, "ok": 195, "erro": 8, "erro:Direção incompatível": 5, "erro:Identidade/revisão divergente: contexto_hash": 3}`. H v7: `{"total": 220, "ok": 220}`.

Fechamentos H v7: `{"completo_operacional_condicional": 24, "parcial": 6}`. Encaminhamentos v7: `{"resolvido_operacional_condicional": 224, "pendente": 14}`. São ocorrências, não operações únicas. Proposta indeterminada pode resolver a responsabilidade sem fornecer número exato.

Candidatos a divergência numérica/falsa precisão em todas as condições: 1 na v6 e 1 na v7. A lista completa está em `resumo_descritivo.json`; nenhuma saída é corrigida para coincidir com a referência.

As três execuções H com referências exatas ainda sem magnitude são k_547a/1, k_547a/2 (encaminhamento inadequado) e k_f04b/2 (omissão de confirmação estruturada). A última é uma perda pareada frente à v6. Houve oito ganhos/uma perda em prazo e seis ganhos/uma perda em custo. B/k_6d82/2 previu custo zero contra +15000 centavos, explicando seu MAE de R$16,67 nos nove pares elegíveis.

Inspeção por caso e causas remanescentes: [AUDITORIA_RESIDUAL.md](AUDITORIA_RESIDUAL.md), [DIAGNOSTICO.md](DIAGNOSTICO.md), `auditoria_tecnica.json`, `triagem_todas_condicoes.json` e `notas_auditoria_manual.json`. A triagem usa referências completas; uma falta de magnitude em B não é automaticamente erro, pois sua view omite relações e a inferibilidade ainda requer auditoria.

## Custo e preservação

| Parcela | USD |
|---|---:|
| Comprometido antes desta revisão | 3.477660900 |
| Incremento comprometido v7 revisão 7.2 | 1.002764765 |
| Inferência conhecida v7 | 0.442764765 |
| Provisão de contagem v7 | 0.560000000 |
| Inferência conhecida acumulada | 2.063925665 |
| Reserva de inferência desconhecida acumulada | 0.188500000 |
| Provisão de contagem acumulada | 2.228000000 |
| **Comprometido acumulado** | **4.480425665** |
| **Saldo sob teto US$ 5** | **0.519574335** |

280 chamadas novas; 1114 tentativas acumuladas. Custos desconhecidos históricos preservados: 13. Comprometimento inclui reservas/provisões e não equivale à fatura. Provisão de US$ 0,002 por contagem é hipótese conservadora, não tarifa comprovada.

Modelo gpt-6-luna/High, Standard, cache 30 min, streaming; entrada oficial ≤16 mil e saída total ≤25 mil tokens, 180 s por chamada, H ≤8 chamadas/1.500 s. Sem retries/fallback. Preços por milhão de tokens: entrada 0,10; cache lido 0,01; cache escrito 30 min 0,125; saída 0,50 USD. Custo reconciliado também por aritmética racional independente. Fontes oficiais consultadas antes da coleta: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [cache](https://developers.openai.com/api/docs/guides/prompt-caching).

Código congelado, tabelas históricas, chamadas 1–834 e 1497 arquivos preexistentes conferidos. Maior entrada oficial: 11796 tokens. Paradas: `[]`. Snapshots antes/depois separados. Apenas carteira e resumos STATUS/PLANO admitem alterações previstas.

## Limites e conclusão da etapa

Comparação descritiva de desenvolvimento. Prompt, contrato e coordenação H mudaram juntos; não há isolamento causal nem prova de superioridade. Referências autorais, inferibilidade por view e suporte semântico seguem sem revisão independente. Etapas 10/11 não iniciadas. O [critério](../../docs/desenvolvimento/ETAPA_09_CRITERIO_CONCLUSAO.md) e o [aceite técnico](../../docs/desenvolvimento/ETAPA_09_ACEITE_TECNICO.md) registram a conclusão da etapa 9 e as limitações remanescentes. Reprodução offline em [VALIDACAO.md](VALIDACAO.md).
