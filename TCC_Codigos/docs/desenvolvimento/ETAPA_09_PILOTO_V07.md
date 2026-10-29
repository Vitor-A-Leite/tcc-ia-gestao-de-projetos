# Etapa 9 — v7, correções e piloto comparável à v6

**Etapa 9 tecnicamente concluída em 28/10/2026, para revisão.** Revisão 7.2 encerrada em 90/90 execuções, dentro do teto acumulado de US$ 5. O [critério definido antes da coleta](ETAPA_09_CRITERIO_CONCLUSAO.md) foi atendido conforme o [aceite técnico e suas limitações](ETAPA_09_ACEITE_TECNICO.md). Etapas 10/11 não iniciadas.

## Correções prospectivas

O contrato local passou a solicitar fatos, condições, propostas, encaminhamentos e pendências. IDs técnicos, hashes de contexto e direções redundantes de valores exatos são atribuídos pelo adaptador determinístico. JSON bruto, resposta de transporte e análise incorporada permanecem vinculados e são revalidados. Isso elimina a necessidade de a LLM copiar identificadores que o executor já conhece, sem fornecer valores factuais ausentes.

Cada cláusula local exige resolução explícita por índices de propostas que a referenciem. Uma manutenção de duração pode resolver um pedido de substituição somente para o mesmo responsável, alvo, atributo e unidade, com cláusula única e condição confirmada. Omissões e propostas sem suporte estrutural continuam bloqueadas.

Pendências são tipadas por prazo, custo ou ambos. Uma pendência exclusivamente monetária permite calcular prazo se a cobertura temporal estiver completa; pendência temporal continua afetando custo quando a duração interfere na incidência. O caminho de prazo isolado conserva as validações temporais e não publica custo.

A revisão 7.1 acrescentou geração com JSON Schema estrito derivado das permissões, fontes, predicados e cláusulas do contexto. Nó sem permissão não pode emitir proposta local. O mesmo schema é enviado à contagem oficial e à geração. A validação posterior permanece necessária; schema válido não garante interpretação correta.

A revisão 7.2 retirou da resposta solicitada à LLM o diagnóstico de deltas locais e renomeou a operação contratual para `alterar_parametros_contratuais`. Calcular a incidência de uma regra já existente é responsabilidade do motor; alterar taxa, base contratada ou crédito exige mudança expressa. A tradução para o nome legado no motor é registrada e conferida, preservando valores, condições, evidências e IDs.

## Rodadas de desenvolvimento preservadas

| Rodada | Slots encerrados | Chamadas conciliadas | Incremento comprometido, USD | Motivo da parada |
|---|---:|---:|---:|---|
| V7 inicial | 6 | 17 | 0,073249855 | Propostas externas em nó sem permissão; motivou schema restrito. |
| Revisão 7.1 | 15 | 44 | 0,195771355 | Pendência de baseline local e encaminhamento de cálculo contratual sem alteração factual; motivou revisão 7.2. |

Nenhuma resposta foi reparada ou reexecutada no mesmo slot. As duas rodadas permanecem fora da comparação principal, mas seus US$ 0,269021210 estão incluídos no teto acumulado. [Relatório inicial](../../outputs/etapa9_piloto_v07_20261028/RELATORIO_PARCIAL.md) e [relatório 7.1](../../outputs/etapa9_piloto_v07_r2_20261028/RELATORIO_PARCIAL.md).

## Protocolo da revisão 7.2

90 slots: 15 casos fictícios, condições B/H/T, duas repetições. Mesmos casos, versões, views, snapshots, eventos, modelo, configuração e ordem da v6. B/T conservam seus algoritmos. H mudou contrato, prompt, schema e coordenação em conjunto; não há isolamento causal entre esses componentes.

Carteira única iniciou em 834 tentativas e US$ 3,477660900 comprometidos. Teto absoluto US$ 5, sem reset, retry ou fallback. As 13 reservas desconhecidas anteriores permanecem. A provisão de US$ 0,002 por contagem é hipótese conservadora e não tarifa comprovada; compromisso interno não equivale à fatura.

Código congelado no adendo antes da coleta; 112 contextos passaram pela preparação offline. Revisão 7.2: 23 testes H e seis de carteira/integração aprovados, incluindo preservação de desconhecidos, fechamento por dimensão, créditos, deltas negativos e tradução de operações. Versão inicial: 126 testes aprovados. Testes prescritos verificam implementação, não desempenho empírico.

## Resultados e aceite técnico

H passou de 16/30 para **23/30 prazos exatos** e de 16/30 para **21/30 custos exatos**. MAE zero nos pares H elegíveis, sem falsa magnitude nos casos de referência não exata. As 220 análises locais foram válidas; na v6 eram 195/203. Mediana H: 230,47 → 106,94 s; inferência conhecida H: US$ 0,465194260 → US$ 0,320810515.

As quatro magnitudes de prazo e seis de custo realmente desconhecidas permaneceram não exatas. Três execuções com referências exatas continuam parciais: k_547a/1, k_547a/2 e k_f04b/2. A última é perda pareada frente à v6; o saldo é de oito ganhos/uma perda em prazo e seis ganhos/uma perda em custo. Há três perdas de direção sustentada de custo, ante cinco na v6.

B ficou em 5/30 prazos e 9/30 custos exatos; um custo errou R$150, com MAE R$16,67 nos nove pares elegíveis. T ficou em 22/30 e 20/30, com uma direção de prazo excessiva frente à referência. Sete saídas B e quatro T foram rejeitadas por contrato. Todos os resultados permanecem no denominador; H usa schema estrito e B/T mantiveram modo JSON, impedindo atribuir o ganho isoladamente ao grafo.

Carteira final: **US$ 4,480425665 comprometidos**, saldo **US$ 0,519574335**. Incremento desta coorte US$ 1,002764765, mais US$ 0,269021210 das rodadas de desenvolvimento, todos incluídos no acumulado. As 280 chamadas novas foram conciliadas; 13 reservas históricas desconhecidas preservadas. Sem parada, retry ou fallback. Código congelado, tabelas anteriores, chamadas 1–834 e inventário de 1.497 arquivos conferidos, sem alteração indevida.

[Relatório comparativo](../../outputs/etapa9_piloto_v07_r3_20261028/RELATORIO.md), [auditoria residual](../../outputs/etapa9_piloto_v07_r3_20261028/AUDITORIA_RESIDUAL.md), [diagnóstico por caso](../../outputs/etapa9_piloto_v07_r3_20261028/DIAGNOSTICO.md), [reprodução offline](../../outputs/etapa9_piloto_v07_r3_20261028/VALIDACAO.md) e [integridade final](../../outputs/etapa9_piloto_v07_r3_20261028/integridade_final.json).

As referências autorais permitem 26/30 prazos e 24/30 custos exatos. Não se exige 30 números: fatos ausentes não podem virar zero. MAE usa somente pares válidos exatos e é separado da cobertura. Auditoria de desenvolvimento pelo mesmo autor não substitui revisão independente das referências, inferibilidade por view e suporte semântico na etapa 10.
