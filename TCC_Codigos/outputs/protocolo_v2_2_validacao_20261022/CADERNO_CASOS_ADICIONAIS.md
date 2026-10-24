# Caderno dos casos adicionais — V2.2

**34 hipóteses autorais de desenvolvimento. Nenhuma resposta abaixo foi produzida por IA.**

92 perguntas por condição; 184 no total. Revisão independente pendente. Os valores não pertencem ao Projeto Alfa.
A = baseline; H = híbrido. Indeterminado não significa zero. Cada relato e plano são um contexto isolado.

As respostas foram registradas pelo autor no JSON antes de executar o motor. A concordância verificada é teste de software, não revisão independente do domínio.

Grafo padrão hipotético: H_MOTOR required_for H_ASSEMBLY; H_ASSEMBLY precedes H_RELEASE.

Convenções: start=início; delivery=entrega; progress_variance=desvio de progresso; finish=término; duration=duração; net_cost=custo líquido.

## SC01 — Atraso de início sem informação do término

Hipótese: o início da montagem atrasou quatro dias; sua duração e a entrega não foram informadas.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: delta = {"delta": "4"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | increase / 4 | increase / 4 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |
| Q3 | H_ASSEMBLY / whole_entity | delivery / calendar_days | indeterminado | indeterminado |
| Q4 | H_ASSEMBLY / whole_entity | progress_variance / calendar_days | indeterminado | indeterminado |
| Q5 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: A mudança de início não determina esta medida sem um modelo adicional.
- Q3: A mudança de início não determina esta medida sem um modelo adicional.
- Q4: A mudança de início não determina esta medida sem um modelo adicional.
- Q5: A mudança de início não determina esta medida sem um modelo adicional.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC02 — Entrega não é início nem término

Hipótese: a entrega do motor atrasou dez dias. Não há parâmetros de montagem.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | increase / 10 | increase / 10 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: O atraso da entrega do motor é direto, mas faltam modelo temporal, folga e condições da montagem para concluir sobre seu início.
- Q3: Faltam efeito no início, duração e restrições da montagem; entrega do motor não é término da montagem.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC03 — Progresso atrasado não é previsão de entrega

Hipótese: a usinagem está cinco dias atrás no progresso; não há nova previsão de término.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida progress_variance, base calendar_days: delta = {"delta": "5"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | progress_variance / calendar_days | increase / 5 | increase / 5 |
| Q2 | H_MOTOR / whole_entity | finish / calendar_days | indeterminado | indeterminado |
| Q3 | H_MOTOR / whole_entity | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Desvio de progresso não estabelece previsão de término sem plano de recuperação e trabalho restante.
- Q3: Desvio de progresso não estabelece data de entrega; faltam previsão de término e condições logísticas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC04 — Término informado não revela início ou entrega

Hipótese: a previsão de término da montagem mudou seis dias; início e transporte são desconhecidos.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: delta = {"delta": "6"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | finish / calendar_days | increase / 6 | increase / 6 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |
| Q3 | H_ASSEMBLY / whole_entity | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Conhecer apenas o deslocamento do término não determina quando a montagem começou.
- Q3: A entrega pode ter transporte e outras restrições; nenhum modelo a relaciona ao término.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC05 — Duração constante: término acompanha início

Hipótese: as posições são índices de dias corridos desde a mesma origem; duração e demais restrições permanecem constantes.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: comparison = {"baseline": "20", "current": "24"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | increase / 4 | increase / 4 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | increase / 4 | increase / 4 |
| Q3 | H_ASSEMBLY / whole_entity | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Índice atual menos índice da linha de base, em dias corridos.
- Q2: A duração fixa e as demais restrições constantes permitem o mesmo deslocamento no término.
- Q3: Não existe modelo entre término e entrega.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC06 — Antecipação com duração constante

Hipótese: as posições são índices de dias corridos desde a mesma origem; duração e demais restrições permanecem constantes.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: comparison = {"baseline": "20", "current": "17"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | decrease / -3 | decrease / -3 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | decrease / -3 | decrease / -3 |
| Q3 | H_ASSEMBLY / whole_entity | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Índice atual menos índice da linha de base, em dias corridos.
- Q2: A duração fixa e as demais restrições constantes permitem o mesmo deslocamento no término.
- Q3: Não existe modelo entre término e entrega.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC07 — Início mantido com duração constante

Hipótese: as posições são índices de dias corridos desde a mesma origem; duração e demais restrições permanecem constantes.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: comparison = {"baseline": "20", "current": "20"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | zero sustentado | zero sustentado |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | zero sustentado | zero sustentado |
| Q3 | H_ASSEMBLY / whole_entity | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Índice atual menos índice da linha de base, em dias corridos.
- Q2: A duração fixa e as demais restrições constantes permitem o mesmo deslocamento no término.
- Q3: Não existe modelo entre término e entrega.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC08 — Folga absorve parte do atraso

Hipótese: modelo temporal condicional explicitado; o grafo informa qual fornecimento condiciona a montagem. O modelo financeiro cobre toda a variação líquida no escopo.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "3", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "200", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | increase / 10 | increase / 10 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | increase / 7 |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | increase / 7 |
| Q4 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | increase / 1400 |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Sem a relação não há como selecionar predecessor. Com vínculo e parâmetros completos, aplicar folga/alternativa/permissão de antecipação.
- Q3: Mesmo deslocamento do início somente sob duração e demais restrições constantes.
- Q4: Diária de R$ 200 por dia corrido de atraso no término; sem economia automática por antecipação, e sem outras variações líquidas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC09 — Folga absorve todo o atraso

Hipótese: modelo temporal condicional explicitado; o grafo informa qual fornecimento condiciona a montagem. O modelo financeiro cobre toda a variação líquida no escopo.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "12", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "200", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | increase / 10 | increase / 10 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | zero sustentado |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | zero sustentado |
| Q4 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | zero sustentado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Sem a relação não há como selecionar predecessor. Com vínculo e parâmetros completos, aplicar folga/alternativa/permissão de antecipação.
- Q3: Mesmo deslocamento do início somente sob duração e demais restrições constantes.
- Q4: Diária de R$ 200 por dia corrido de atraso no término; sem economia automática por antecipação, e sem outras variações líquidas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC10 — Alternativa pronta absorve atraso

Hipótese: modelo temporal condicional explicitado; o grafo informa qual fornecimento condiciona a montagem. O modelo financeiro cobre toda a variação líquida no escopo.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": true, "buffer_days": "3", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "200", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | increase / 10 | increase / 10 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | zero sustentado |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | zero sustentado |
| Q4 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | zero sustentado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Sem a relação não há como selecionar predecessor. Com vínculo e parâmetros completos, aplicar folga/alternativa/permissão de antecipação.
- Q3: Mesmo deslocamento do início somente sob duração e demais restrições constantes.
- Q4: Diária de R$ 200 por dia corrido de atraso no término; sem economia automática por antecipação, e sem outras variações líquidas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC11 — Antecipação permitida

Hipótese: modelo temporal condicional explicitado; o grafo informa qual fornecimento condiciona a montagem. O modelo financeiro cobre toda a variação líquida no escopo.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "-4"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": true, "alternative_ready": false, "buffer_days": "0", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "200", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | decrease / -4 | decrease / -4 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | decrease / -4 |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | decrease / -4 |
| Q4 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | zero sustentado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Sem a relação não há como selecionar predecessor. Com vínculo e parâmetros completos, aplicar folga/alternativa/permissão de antecipação.
- Q3: Mesmo deslocamento do início somente sob duração e demais restrições constantes.
- Q4: Diária de R$ 200 por dia corrido de atraso no término; sem economia automática por antecipação, e sem outras variações líquidas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC12 — Antecipação impedida

Hipótese: modelo temporal condicional explicitado; o grafo informa qual fornecimento condiciona a montagem. O modelo financeiro cobre toda a variação líquida no escopo.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "-4"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "0", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "200", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | decrease / -4 | decrease / -4 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | zero sustentado |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | zero sustentado |
| Q4 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | zero sustentado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Sem a relação não há como selecionar predecessor. Com vínculo e parâmetros completos, aplicar folga/alternativa/permissão de antecipação.
- Q3: Mesmo deslocamento do início somente sob duração e demais restrições constantes.
- Q4: Diária de R$ 200 por dia corrido de atraso no término; sem economia automática por antecipação, e sem outras variações líquidas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC13 — Outras restrições mudaram

Hipótese: o motor atrasa dez dias, mas também há mudanças não quantificadas de recursos da montagem.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "3", "other_constraints_unchanged": false, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Mudanças não quantificadas de recursos violam a hipótese de outras restrições constantes.
- Q2: Duração fixa não resolve a ausência de conclusão sobre o início e as restrições alteradas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC14 — Aumento líquido de custo

Hipótese: os valores são custos totais líquidos comparáveis da montagem, em BRL, incluindo materiais, mão de obra, frete, retrabalho e efeitos de prazo; não existem outras parcelas variáveis nesse escopo.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: comparison = {"baseline": "1000", "current": "1250"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | increase / 250 | increase / 250 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Custo total atual menos custo total anterior, no mesmo escopo e moeda.
- Q2: Não há variação direta nem modelo suficiente para concluir sobre esta medida temporal neste escopo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC15 — Redução líquida de custo

Hipótese: os valores são custos totais líquidos comparáveis da montagem, em BRL, incluindo materiais, mão de obra, frete, retrabalho e efeitos de prazo; não existem outras parcelas variáveis nesse escopo.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: comparison = {"baseline": "1000", "current": "800"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | decrease / -200 | decrease / -200 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Custo total atual menos custo total anterior, no mesmo escopo e moeda.
- Q2: Não há variação direta nem modelo suficiente para concluir sobre esta medida temporal neste escopo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC16 — Custo líquido mantido

Hipótese: os valores são custos totais líquidos comparáveis da montagem, em BRL, incluindo materiais, mão de obra, frete, retrabalho e efeitos de prazo; não existem outras parcelas variáveis nesse escopo.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: comparison = {"baseline": "1000", "current": "1000"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | zero sustentado | zero sustentado |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Custo total atual menos custo total anterior, no mesmo escopo e moeda.
- Q2: Não há variação direta nem modelo suficiente para concluir sobre esta medida temporal neste escopo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC17 — Direção de custo conhecida, magnitude ausente

Hipótese: está confirmado aumento líquido no custo total da montagem, mas o valor ainda não foi consolidado.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: direction = {"direction": "increase"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | increase / magnitude desconhecida | increase / magnitude desconhecida |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: A direção é explícita, sem autorizar uma quantia.
- Q2: Não há variação direta nem modelo suficiente para concluir sobre esta medida temporal neste escopo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC18 — Preço unitário não é custo líquido

Hipótese: o preço unitário do motor caiu R$ 50; quantidade, frete, substituição e retrabalho não foram informados.

**Plano hipotético anotado:**

```text
Nenhum parâmetro adicional informado.
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | net_cost / not_applicable | indeterminado | indeterminado |
| Q2 | H_RELEASE / project | net_cost / not_applicable | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Preço unitário não informa variação líquida no escopo.
- Q2: Não há composição do custo total do projeto.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC19 — Modelo líquido completo com diária zero

Hipótese: contratualmente nenhuma parcela líquida de custo da montagem varia, e a diária aplicável é zero; o prazo está em aberto.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "0", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | zero sustentado | zero sustentado |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Modelo líquido completo e diária zero provam ausência de efeito financeiro.
- Q2: Não há variação direta nem modelo suficiente para concluir sobre esta medida temporal neste escopo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC20 — Custo parcial não prova custo líquido

Hipótese: há quatro dias de atraso do início, e diária de R$ 200, mas existem custos de retrabalho ainda não consolidados.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: delta = {"delta": "4"}
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": false, "rate_per_day_brl": "200", "time_day_basis": "calendar_days", "time_measure": "start", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | increase / 4 | increase / 4 |
| Q2 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Modelo parcial de diária não representa o custo líquido completo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC21 — Economia de componente não é economia do projeto

Hipótese: a compra do motor tem economia líquida de R$ 100. Os demais custos do projeto não foram apurados.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo purchase, medida net_cost, base not_applicable: delta = {"delta": "-100"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / purchase | net_cost / not_applicable | decrease / -100 | decrease / -100 |
| Q2 | H_RELEASE / project | net_cost / not_applicable | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Economia da compra do motor não determina a variação líquida de todas as parcelas do projeto.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC22 — Lotes distintos no mesmo nó

Hipótese: apenas a entrega do lote A do motor atrasa três dias; não há informação sobre o lote B.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo lot_A, medida delivery, base calendar_days: delta = {"delta": "3"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / lot_A | delivery / calendar_days | increase / 3 | increase / 3 |
| Q2 | H_MOTOR / lot_B | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: O fato cita apenas o lote A; não existe variação direta nem modelo aplicável ao lote B.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC23 — Dias úteis não se convertem em corridos sem calendário

Hipótese: a entrega do motor atrasou cinco dias úteis. Não há calendário com finais de semana e feriados.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base working_days: delta = {"delta": "5"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / working_days | increase / 5 | increase / 5 |
| Q2 | H_MOTOR / whole_entity | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Cinco dias úteis não estabelecem desvio em dias corridos sem calendário compatível.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC24 — Fontes conflitantes

Hipótese: duas fontes de mesma data e escopo divergem: entrega do motor com dois ou cinco dias de atraso; nenhuma tem precedência definida.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "2"}
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "5"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "0", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | indeterminado | indeterminado |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: As duas fontes informam valores incompatíveis para a mesma entrega, escopo e base, sem precedência definida.
- Q2: No híbrido, a origem contraditória impede cálculo; no baseline falta também a relação temporal visível.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC25 — Mais de um predecessor sem calendário individual

Hipótese: motor e sensor atrasam; falta cronograma por predecessor. Não somar nem escolher arbitrariamente o maior atraso.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "5"}
H_SENSOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "8"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "0", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
```

Grafo específico: `[{"source": "H_MOTOR", "target": "H_ASSEMBLY", "type": "required_for"}, {"source": "H_SENSOR", "target": "H_ASSEMBLY", "type": "required_for"}]`.

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: O híbrido conhece dois predecessores e precisa de restrições por predecessor; o baseline não recebe as relações.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC26 — Validação não é propagação de quantidade

Hipótese: existe apenas uma relação de validação entre motor e montagem. Não há vínculo temporal declarado entre eles.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "3", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
```

Grafo específico: `[{"source": "H_MOTOR", "target": "H_ASSEMBLY", "type": "validated_by"}]`.

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: A única relação é de validação; ela não satisfaz o vínculo temporal required_for necessário ao modelo declarado.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC27 — Cadeia explicitamente parametrizada

Hipótese: motor condiciona montagem; término da montagem precede liberação; os dois vínculos têm folgas próprias, duração fixa e demais restrições constantes. O custo líquido da liberação varia somente pela diária de atraso.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "3", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_RELEASE, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "2", "other_constraints_unchanged": true, "relation": "precedes", "source_measure": "finish", "source_scope": "whole_entity"}
H_RELEASE, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_RELEASE, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "100", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | increase / 7 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | increase / 7 |
| Q3 | H_RELEASE / whole_entity | start / calendar_days | indeterminado | increase / 5 |
| Q4 | H_RELEASE / whole_entity | finish / calendar_days | indeterminado | increase / 5 |
| Q5 | H_RELEASE / whole_entity | net_cost / not_applicable | indeterminado | increase / 500 |

**Justificativas autorais:**

- Q1: 10 dias na entrega menos 3 de folga = 7 no início da montagem.
- Q2: Duração da montagem constante.
- Q3: 7 dias no término da montagem menos 2 de folga = 5 no início da liberação.
- Q4: Duração da liberação constante.
- Q5: 5 dias de atraso no término × R$ 100 por dia, modelo líquido completo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC28 — Duração adicional não determina término isoladamente

Hipótese: a duração prevista da montagem aumentou dois dias, sem informação de início nem de outras restrições.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida duration, base calendar_days: delta = {"delta": "2"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | duration / calendar_days | increase / 2 | increase / 2 |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Alteração de duração não determina deslocamento do início.
- Q3: Faltam início e restrições para converter duração adicional em deslocamento de término.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC29 — Atraso sem magnitude

Hipótese: motor chegará atrasado, sem número de dias; folga zero, duração constante e modelo líquido de custo de atraso completo.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: direction = {"direction": "increase"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "0", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_ASSEMBLY, escopo whole_entity, medida net_cost, base not_applicable: delay_cost = {"net_model_complete": true, "rate_per_day_brl": "200", "time_day_basis": "calendar_days", "time_measure": "finish", "time_scope": "whole_entity"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_MOTOR / whole_entity | delivery / calendar_days | increase / magnitude desconhecida | increase / magnitude desconhecida |
| Q2 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | increase / magnitude desconhecida |
| Q3 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | increase / magnitude desconhecida |
| Q4 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | increase / magnitude desconhecida |

**Justificativas autorais:**

- Q1: A entrega está explicitamente atrasada, mas a magnitude não foi informada.
- Q2: O híbrido tem vínculo e folga zero, sustentando atraso sem magnitude; o baseline não conhece o vínculo.
- Q3: No híbrido, duração constante transmite a direção do atraso do início; a magnitude segue desconhecida.
- Q4: Direção positiva sustentada; sem magnitude temporal não se calcula quantia em BRL.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC30 — Início e término com desvios diferentes

Hipótese: a montagem começou quatro dias depois, mas a previsão de término mudou apenas dois dias. Não foi declarada duração constante.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: delta = {"delta": "4"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: delta = {"delta": "2"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | increase / 4 | increase / 4 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | increase / 2 | increase / 2 |
| Q3 | H_ASSEMBLY / whole_entity | delivery / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q3: Os deslocamentos de início e término não definem a entrega, cuja logística não foi informada.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC31 — Conflito entre conclusão direta e modelo

Hipótese: início quatro dias depois e duração supostamente constante contradizem uma fonte que declara término apenas dois dias depois, no mesmo escopo e base.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: delta = {"delta": "4"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: delta = {"delta": "2"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | increase / 4 | increase / 4 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.
- Q2: Confrontar fonte direta e modelo: não selecionar a conclusão conveniente.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC32 — Dependência explícita no texto também vale no baseline

Hipótese: a montagem necessita da entrega do motor (H_MOTOR required_for H_ASSEMBLY), com folga de três dias e demais condições explícitas.

**Plano hipotético anotado:**

```text
H_MOTOR, escopo whole_entity, medida delivery, base calendar_days: delta = {"delta": "10"}
H_ASSEMBLY, escopo whole_entity, medida start, base calendar_days: dependency_shift = {"advance_allowed": false, "alternative_ready": false, "buffer_days": "3", "other_constraints_unchanged": true, "relation": "required_for", "source_measure": "delivery", "source_scope": "whole_entity"}
H_ASSEMBLY, escopo whole_entity, medida finish, base calendar_days: fixed_duration = {"duration_unchanged": true, "other_constraints_unchanged": true}
```

Grafo específico: `[]`.

A relação do texto está acessível nas duas condições.

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | increase / 7 | increase / 7 |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | increase / 7 | increase / 7 |

**Justificativas autorais:**

- Q1: Relação textual fornecida nas duas condições: ambas podem usar o vínculo.
- Q2: Variação direta na medida e no escopo indicados; não extrapolar a outras medidas.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC33 — Aritmética financeira decimal

Hipótese: o custo líquido completo no escopo de um ajuste passou de R$ 0,10 para R$ 0,30, sem outras parcelas variáveis.

**Plano hipotético anotado:**

```text
H_ASSEMBLY, escopo adjustment, medida net_cost, base not_applicable: comparison = {"baseline": "0.10", "current": "0.30"}
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / adjustment | net_cost / not_applicable | increase / 0.20 | increase / 0.20 |

**Justificativas autorais:**

- Q1: Subtração decimal exata; não usar aproximação binária.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

## SC34 — Data e risco não são variação confirmada

Hipótese: foi autorizado reteste para 06/10 e existe risco de consumir três dias extras; não há data anterior, efeito confirmado nem orçamento.

**Plano hipotético anotado:**

```text
Nenhum parâmetro adicional informado.
```

| Pergunta | Entidade / escopo | Medida / base | A | H |
|---|---|---|---|---|
| Q1 | H_ASSEMBLY / whole_entity | start / calendar_days | indeterminado | indeterminado |
| Q2 | H_ASSEMBLY / whole_entity | finish / calendar_days | indeterminado | indeterminado |
| Q3 | H_ASSEMBLY / whole_entity | net_cost / not_applicable | indeterminado | indeterminado |

**Justificativas autorais:**

- Q1: Data absoluta de reteste e autorização não informam diferença contra linha de base comparável.
- Q2: Risco de três dias extras não é alteração confirmada do término e não há cronograma suficiente.
- Q3: O relato não informa custo líquido nem modelo financeiro completo.

Revisor independente: ______ | Concordância/correção, fonte e justificativa: ______

