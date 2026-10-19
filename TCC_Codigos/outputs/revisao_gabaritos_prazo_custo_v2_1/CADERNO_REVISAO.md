# Caderno de revisão — prazo e custo

Referências autorais provisórias. Não são respostas da IA nem validação independente.
As conclusões valem condicionalmente aos relatos; cada cenário é isolado.
Nenhum exemplo hipotético foi incorporado como fato do Projeto Alfa.

Fonte versionada: `data/reference_sets/alfa_schedule_cost_v2_1_draft.json`; SHA-256 `587be6175edba243e0ac977b10cc9da9dabfd0972e28ad2d5b6268e52dae5d35`.

| Caso | Medida local de prazo | Referência local | Liberação final | Custo local / total |
|---|---|---|---|---|
| S001 | delivery | +10 dias (base não especificada) | indeterminado | indeterminado |
| S002 | finish | indeterminado | indeterminado | indeterminado |
| S003 | finish | indeterminado | indeterminado | indeterminado |
| S004 | finish | indeterminado | indeterminado | indeterminado |
| S005 | finish | indeterminado | indeterminado | indeterminado |
| S006 | start | indeterminado | indeterminado | indeterminado |
| S007 | finish | indeterminado | indeterminado | indeterminado |
| S008 | start | +4 dias (base não especificada) | indeterminado | indeterminado |
| S009 | não consultada | — | indeterminado | indeterminado |
| S010 | availability | indeterminado | indeterminado | indeterminado |
| S011 | finish | indeterminado | indeterminado | indeterminado |
| S012 | finish | indeterminado | indeterminado | indeterminado |
| S013 | finish | indeterminado | indeterminado | indeterminado |
| S014 | delivery | +7 dias (base não especificada) | indeterminado | indeterminado |
| S015 | finish | indeterminado | indeterminado | indeterminado |
| S016 | duration | indeterminado | indeterminado | indeterminado |
| S017 | finish | indeterminado | indeterminado | indeterminado |
| S018 | finish | indeterminado | indeterminado | indeterminado |
| S019 | finish | indeterminado | indeterminado | indeterminado |
| S020 | start | indeterminado | indeterminado | indeterminado |
| S021 | progress_variance | +5 dias (base não especificada) | indeterminado | indeterminado |
| S022 | não consultada | — | indeterminado | indeterminado |
| S023 | availability | indeterminado | indeterminado | indeterminado |
| S024 | finish | indeterminado | indeterminado | indeterminado |
| S025 | availability | indeterminado | indeterminado | indeterminado |
| S026 | start | indeterminado | indeterminado | indeterminado |
| S027 | não consultada | — | indeterminado | indeterminado |
| S028 | finish | indeterminado | indeterminado | indeterminado |
| S029 | start | +3 dias (base não especificada) | indeterminado | indeterminado |
| S030 | availability | indeterminado | indeterminado | indeterminado |
| S031 | finish | indeterminado | indeterminado | indeterminado |
| S032 | availability | indeterminado | indeterminado | indeterminado |
| S033 | finish | indeterminado | indeterminado | indeterminado |
| S034 | não consultada | — | indeterminado | indeterminado |
| S035 | delivery | sem variação | indeterminado | indeterminado |
| S036 | finish | indeterminado | indeterminado | indeterminado |

## Anotações para revisão

Preencher reviewer, reviewed_at, decision e notes no JSON após revisão externa. Discordâncias devem ter justificativa; não ajustar respostas apenas para concordar com o motor.

### S001

> A MotorTech informou que o motor elétrico chegará 10 dias depois do previsto.

- **S001:local:schedule** — C_MOTOR, delivery. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `supported/increase`, delta `10`. A chegada do motor foi explicitamente deslocada em dez dias; isso não determina a data da montagem.
  Providência: Conferir a previsão informada e revisar o cronograma do escopo; apurar separadamente efeitos posteriores.
- **S001:local:cost** — C_MOTOR, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A chegada do motor foi explicitamente deslocada em dez dias; isso não determina a data da montagem.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S001:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S001:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S002

> A equipe decidiu solicitar uma proposta alternativa para o redutor à GearWorks; Carla fará o contato até 25/09.

- **S002:local:schedule** — T_PROC, finish. Escopo: Conclusão da solicitação/cotação do redutor; não toda a tarefa de compras.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Solicitar proposta e estabelecer prazo de contato não informa variação da conclusão da compra.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S002:local:cost** — T_PROC, net_cost. Escopo: Conclusão da solicitação/cotação do redutor; não toda a tarefa de compras.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Solicitar proposta e estabelecer prazo de contato não informa variação da conclusão da compra.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S002:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S002:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S003

> No ensaio preliminar de carga, o protótipo apresentou folga excessiva no redutor.

- **S003:local:schedule** — TEST_LOAD, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A folga excessiva é uma não conformidade; duração de correção e reteste não foram informadas.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S003:local:cost** — TEST_LOAD, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A folga excessiva é uma não conformidade; duração de correção e reteste não foram informadas.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S003:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S003:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S004

> A espessura da parede da carcaça foi alterada de 3,0 mm para 3,5 mm após revisão estrutural.

- **S004:local:schedule** — T_CAD, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A espessura mudou; esforço, duração e situação do detalhamento não foram informados.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S004:local:cost** — T_CAD, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A espessura mudou; esforço, duração e situação do detalhamento não foram informados.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S004:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S004:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S005

> Bruno ficou responsável por atualizar o desenho da carcaça até amanhã.

- **S005:local:schedule** — T_CAD, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Uma data de compromisso para atualizar desenho não fornece comparação com a linha de base.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S005:local:cost** — T_CAD, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Uma data de compromisso para atualizar desenho não fornece comparação com a linha de base.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S005:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S005:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S006

> Existe risco de a câmara térmica não estar disponível na semana prevista para os ensaios.

- **S006:local:schedule** — TEST_THERMAL, start. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Indisponibilidade da câmara é uma possibilidade, sem confirmação ou janela alternativa.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S006:local:cost** — TEST_THERMAL, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Indisponibilidade da câmara é uma possibilidade, sem confirmação ou janela alternativa.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S006:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S006:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S007

> Foi aprovada a troca do fornecedor do sensor: a SensePro será substituída pela NovaSense.

- **S007:local:schedule** — T_PROC, finish. Escopo: Fornecimento do sensor com o fornecedor aprovado.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A troca aprovada não informa disponibilidade, prazo contratado ou diferença para a linha de base.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S007:local:cost** — T_PROC, net_cost. Escopo: Fornecimento do sensor com o fornecedor aprovado.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A troca aprovada não informa disponibilidade, prazo contratado ou diferença para a linha de base.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S007:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S007:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S008

> O laboratório confirmou que o teste térmico só poderá começar quatro dias depois do planejado.

- **S008:local:schedule** — TEST_THERMAL, start. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `supported/increase`, delta `4`. O início do teste mudou quatro dias; sua conclusão exige duração e restrições posteriores.
  Providência: Conferir a previsão informada e revisar o cronograma do escopo; apurar separadamente efeitos posteriores.
- **S008:local:cost** — TEST_THERMAL, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. O início do teste mudou quatro dias; sua conclusão exige duração e restrições posteriores.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S008:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S008:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S009

> A reunião de sexta-feira foi transferida da sala 2 para a sala 4.

- **S009:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S009:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S010

> A engenharia especificou rolamento com classe de folga C3 no lugar do modelo inicialmente selecionado.

- **S010:local:schedule** — C_BEARING, availability. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A classe de folga foi alterada, sem informação sobre disponibilidade do novo rolamento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S010:local:cost** — C_BEARING, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A classe de folga foi alterada, sem informação sobre disponibilidade do novo rolamento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S010:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S010:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S011

> A equipe aprovou o Design Freeze para 02/10 sem alterações adicionais de geometria.

- **S011:local:schedule** — M_DESIGN_FREEZE, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A data aprovada é um valor absoluto, sem data anterior comparável; geometria inalterada não significa prazo inalterado.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S011:local:cost** — M_DESIGN_FREEZE, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A data aprovada é um valor absoluto, sem data anterior comparável; geometria inalterada não significa prazo inalterado.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S011:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S011:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S012

> Carla vai cotar um segundo fornecedor para a carcaça até 29/09.

- **S012:local:schedule** — T_PROC, finish. Escopo: Conclusão da cotação da carcaça; não toda a tarefa de compras.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Prazo para cotação não é prazo de conclusão da compra nem variação deste prazo.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S012:local:cost** — T_PROC, net_cost. Escopo: Conclusão da cotação da carcaça; não toda a tarefa de compras.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Prazo para cotação não é prazo de conclusão da compra nem variação deste prazo.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S012:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S012:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S013

> O teste de vedação apresentou vazamento acima do limite no conjunto da carcaça.

- **S013:local:schedule** — TEST_SEAL, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Falha de vedação não informa tempo de reparo ou reteste.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S013:local:cost** — TEST_SEAL, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Falha de vedação não informa tempo de reparo ou reteste.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S013:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S013:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S014

> A ElecBoard informou atraso de sete dias na entrega da placa de controle.

- **S014:local:schedule** — C_PCB, delivery. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `supported/increase`, delta `7`. O atraso de sete dias na entrega da placa é explícito; efeitos posteriores dependem do cronograma.
  Providência: Conferir a previsão informada e revisar o cronograma do escopo; apurar separadamente efeitos posteriores.
- **S014:local:cost** — C_PCB, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. O atraso de sete dias na entrega da placa é explícito; efeitos posteriores dependem do cronograma.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S014:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S014:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S015

> A equipe decidiu substituir a MetalForm por outro fornecedor para fabricar a carcaça do protótipo.

- **S015:local:schedule** — T_PROC, finish. Escopo: Fornecimento da carcaça após a substituição.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A substituição do fornecedor não informa o novo prazo de fornecimento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S015:local:cost** — T_PROC, net_cost. Escopo: Fornecimento da carcaça após a substituição.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A substituição do fornecedor não informa o novo prazo de fornecimento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S015:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S015:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S016

> O teste de vida pode consumir três dias extras e colocar a data de validação em risco.

- **S016:local:schedule** — TEST_LIFE, duration. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Três dias extras são uma possibilidade; não são duração adicional confirmada.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S016:local:cost** — TEST_LIFE, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Três dias extras são uma possibilidade; não são duração adicional confirmada.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S016:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S016:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S017

> O limite de corrente do motor foi reduzido no software de controle para diminuir aquecimento.

- **S017:local:schedule** — TEST_THERMAL, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A mudança do limite de corrente não quantifica efeito na duração ou conclusão dos ensaios.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S017:local:cost** — TEST_THERMAL, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A mudança do limite de corrente não quantifica efeito na duração ou conclusão dos ensaios.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S017:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S017:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S018

> Durante o teste térmico, a temperatura do motor ultrapassou o limite especificado.

- **S018:local:schedule** — TEST_THERMAL, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Temperatura fora do limite não quantifica duração de correção nem novo prazo.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S018:local:cost** — TEST_THERMAL, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Temperatura fora do limite não quantifica duração de correção nem novo prazo.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S018:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S018:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S019

> Foi decidido repetir o teste térmico após a alteração do limite de corrente; Diego agenda o reteste até 01/10.

- **S019:local:schedule** — TEST_THERMAL, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Repetir e agendar o teste não informa sua conclusão; prazo de agendamento não é término do reteste.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S019:local:cost** — TEST_THERMAL, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Repetir e agendar o teste não informa sua conclusão; prazo de agendamento não é término do reteste.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S019:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S019:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S020

> Diego ficou responsável por reservar a câmara térmica para o reteste de 06/10.

- **S020:local:schedule** — TEST_THERMAL, start. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O reteste em 06/10 é uma data absoluta; não existe data anterior comparável no evento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S020:local:cost** — TEST_THERMAL, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. O reteste em 06/10 é uma data absoluta; não existe data anterior comparável no evento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S020:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S020:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S021

> A usinagem do eixo de saída acumulou atraso de cinco dias por retrabalho.

- **S021:local:schedule** — C_SHAFT, progress_variance. Escopo: Desvio de progresso acumulado na usinagem do eixo; não previsão de entrega.
  Referência em ambas as condições: `supported/increase`, delta `5`. Há cinco dias de atraso acumulado na usinagem; não se afirma igual atraso de entrega ou término.
  Providência: Conferir a previsão informada e revisar o cronograma do escopo; apurar separadamente efeitos posteriores.
- **S021:local:cost** — C_SHAFT, net_cost. Escopo: Desvio de progresso acumulado na usinagem do eixo; não previsão de entrega.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Há cinco dias de atraso acumulado na usinagem; não se afirma igual atraso de entrega ou término.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S021:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S021:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S022

> O café da reunião de validação será servido às 14h.

- **S022:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S022:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S023

> A tolerância do diâmetro do eixo foi alterada de h7 para h6 para reduzir folga.

- **S023:local:schedule** — C_SHAFT, availability. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. A tolerância mudou, mas esforço, estoque e prazo do eixo não foram informados.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S023:local:cost** — C_SHAFT, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A tolerância mudou, mas esforço, estoque e prazo do eixo não foram informados.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S023:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S023:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S024

> O ensaio de EMC indicou ruído intermitente no sensor de posição quando o motor opera em alta carga.

- **S024:local:schedule** — TEST_EMC, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Ruído intermitente exige análise técnica; duração da solução não foi informada.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S024:local:cost** — TEST_EMC, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Ruído intermitente exige análise técnica; duração da solução não foi informada.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S024:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S024:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S025

> A equipe aprovou um segundo fornecedor para a placa de controle devido à instabilidade de prazo da ElecBoard.

- **S025:local:schedule** — C_PCB, availability. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Aprovar segundo fornecedor não equivale a ter placa alternativa pronta e suficiente.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S025:local:cost** — C_PCB, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Aprovar segundo fornecedor não equivale a ter placa alternativa pronta e suficiente.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S025:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S025:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S026

> Mesmo com o ensaio de vedação pendente, foi autorizado iniciar a montagem do segundo protótipo para não perder a janela de testes.

- **S026:local:schedule** — T_ASSEMBLY, start. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Autorizar o início não comprova início realizado nem desvio em relação ao planejado.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S026:local:cost** — T_ASSEMBLY, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Autorizar o início não comprova início realizado nem desvio em relação ao planejado.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S026:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S026:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S027

> Ana atualizará o cronograma e o status do projeto após consolidar os novos prazos até o fim do dia.

- **S027:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S027:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S028

> Com os atrasos do motor e do eixo, o milestone de protótipo disponível passou a ter risco alto de escorregar.

- **S028:local:schedule** — M_PROTO_READY, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Risco alto não é adiamento confirmado; atrasos de outros cenários não podem ser importados.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S028:local:cost** — M_PROTO_READY, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Risco alto não é adiamento confirmado; atrasos de outros cenários não podem ser importados.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S028:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S028:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S029

> A revisão do relatório final de validação só começará três dias depois do previsto.

- **S029:local:schedule** — T_DOC, start. Escopo: Início da revisão do relatório final de validação.
  Referência em ambas as condições: `supported/increase`, delta `3`. A revisão do relatório começará três dias depois; isso não determina seu término.
  Providência: Conferir a previsão informada e revisar o cronograma do escopo; apurar separadamente efeitos posteriores.
- **S029:local:cost** — T_DOC, net_cost. Escopo: Início da revisão do relatório final de validação.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. A revisão do relatório começará três dias depois; isso não determina seu término.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S029:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S029:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S030

> O conector do chicote será reposicionado para evitar interferência com a carcaça.

- **S030:local:schedule** — C_HARNESS, availability. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Reposicionar conector não informa esforço nem nova disponibilidade do chicote.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S030:local:cost** — C_HARNESS, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Reposicionar conector não informa esforço nem nova disponibilidade do chicote.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S030:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S030:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S031

> No teste de vida, o rolamento apresentou desgaste visível antes do número previsto de ciclos.

- **S031:local:schedule** — TEST_LIFE, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Desgaste antes dos ciclos previstos é falha de desempenho, não adiantamento do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S031:local:cost** — TEST_LIFE, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Desgaste antes dos ciclos previstos é falha de desempenho, não adiantamento do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S031:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S031:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S032

> Foi decidido substituir o rolamento por uma versão de maior capacidade dinâmica antes de repetir o teste de vida.

- **S032:local:schedule** — C_BEARING, availability. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Maior capacidade dinâmica não estabelece novo prazo ou preço; reteste precisa de planejamento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S032:local:cost** — C_BEARING, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Maior capacidade dinâmica não estabelece novo prazo ou preço; reteste precisa de planejamento.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S032:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S032:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S033

> Bruno atualizará a BOM e o desenho do conjunto com o novo rolamento até segunda-feira.

- **S033:local:schedule** — T_CAD, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Prazo para atualizar BOM e desenho não fornece variação de conclusão em relação à linha de base.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S033:local:cost** — T_CAD, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Prazo para atualizar BOM e desenho não fornece variação de conclusão em relação à linha de base.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S033:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S033:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S034

> A liberação de engenharia está em risco porque os relatórios de validação ainda não foram consolidados.

- **S034:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S034:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S035

> A MetalForm informou que passará a enviar as peças em caixas retornáveis, sem mudança de peça, prazo ou inspeção.

- **S035:local:schedule** — SUP_HOUSING, delivery. Escopo: Prazo do fornecimento de peças mencionado pela MetalForm; não entrega final do projeto.
  Referência em ambas as condições: `no_impact/none`, delta `0`. O prazo do fornecimento mencionado é explicitamente mantido; a afirmação não cobre custo ou todo o projeto.
  Providência: Registrar manutenção do prazo apenas no fornecimento mencionado; verificar custo separadamente.
- **S035:local:cost** — SUP_HOUSING, net_cost. Escopo: Prazo do fornecimento de peças mencionado pela MetalForm; não entrega final do projeto.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. O prazo do fornecimento mencionado é explicitamente mantido; a afirmação não cobre custo ou todo o projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S035:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S035:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

### S036

> Após a conclusão satisfatória dos cinco ensaios, a equipe aprovou a validação do protótipo e autorizou a preparação da liberação de engenharia.

- **S036:local:schedule** — M_VALIDATION, finish. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. Validação concluída e aprovada não informa desvio em relação à data prevista; preparar liberação não é concluí-la.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Valor anterior e valor atual comparáveis para a medida consultada, ou direção explicitamente confirmada.; Confirmação do efeito realizado ou previsto, distinguindo risco e compromisso de variação confirmada.
- **S036:local:cost** — M_VALIDATION, net_cost. Escopo: Somente a entidade e a atividade descritas no evento, na medida temporal indicada.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O relato não informa variação líquida de custo neste escopo. Validação concluída e aprovada não informa desvio em relação à data prevista; preparar liberação não é concluí-la.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.
- **S036:project:schedule** — M_RELEASE, finish. Escopo: Data da liberação final de engenharia do Projeto Alfa.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não determina o desvio da liberação final: uma conexão estrutural não fornece folgas, calendário e restrições suficientes.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Cronograma vigente e linha de base comparável, com calendário.; Datas de necessidade, folgas, durações e restrições de cada etapa afetada.; Situação de execução, alternativas e confirmação de quais restrições permanecem iguais.
- **S036:project:cost** — M_RELEASE, net_cost. Escopo: Custo líquido total do Projeto Alfa associado ao evento; não somente custo de um componente.
  Referência em ambas as condições: `undetermined/unknown`, delta `None`. O evento não informa variação líquida do custo total do projeto.
  Providência: Solicitar os dados faltantes antes de concluir ou alterar prazo e orçamento.
  Faltam: Variação líquida de custo no escopo, moeda e base de comparação.; Quantidades, preços, retrabalho, reteste, frete e custos indiretos aplicáveis, ou declaração explícita de que não variam.

Revisor: ______ | Concordância/correção e justificativa: ______

