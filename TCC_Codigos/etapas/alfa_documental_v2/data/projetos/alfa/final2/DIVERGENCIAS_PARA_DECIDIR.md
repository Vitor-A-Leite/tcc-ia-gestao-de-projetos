# Rodada 2: divergências entre as anotadoras (para os autores decidirem)

Data: 24/11/2026. Arquivos comparados (SHA-256):

- `anotacoes1.json` (IA 1, modelo a confirmar pelos autores): `1478c1f34f8eb479f07fc2f48875aa320ef38434c9869a08186e589bef119bae`
- `anotacoes2.json` (IA 2, ChatGPT): `4339b8104bd158486ef1b0e640df676b5a5246efcabef20274032caa03682d2c`
- `material_gerado.json`: `850a17bd226402daab9572818d44a3227083994c8d0d6676052cd3ca2f799bc8`

## Resumo

| Medida | Valor |
|---|---|
| Pares anotados (15 eventos × 44 trechos) | 660 |
| Mesmo rótulo | 620 (93,9%) |
| Kappa de Cohen | **0,896** |
| Mesma decisão "revisar × não revisar" | 649 (98,3%) |

As 40 divergências caem em **7 padrões**. Cada padrão vale para todos os eventos listados. Para cada um, escrevam **IA1**, **IA2** ou **outro**. Decidam pelas regras do prompt, sem consultar o sistema.

## P1. `STATUS_A.OBSERVACOES`, todos os eventos (15 casos)

> "Responsáveis: Ana (gerente do projeto), Bruno (engenharia mecânica), Carla (suprimentos) e Diego (validação). A equipe considera o plano realista. O próximo status será emitido após o design freeze."

- **IA1: SEM_AFIRMACAO.** Papéis, opinião e próximo status não são verificáveis no estado.
- **IA2: CORRETO.** Os responsáveis e o design freeze não mudaram.

Nos dois casos, o trecho não precisa de revisão.

**Decisão:** ______

## P2. `ACTION_LOG.A05`, em G01–G07, G09, G10 e G13 (10 casos)

> "Validar com o cliente a franquia de 40 dias da parcela de gestão e instalação e o custo de R$ 300 por dia excedente. […] Situação: concluída."

- **IA1: CORRETO.** A regra da franquia não mudou; a ação concluída continua certa.
- **IA2: DECISAO_HUMANA.** A ação trata da parcela de gestão, que passou a ter dias excedentes; cabe avaliar se é preciso validar de novo.

**Decisão:** ______

## P3. `ACTION_LOG.A06`, em G01–G05, G10, G13 e G14 (8 casos)

> "Negociar uma janela de frete consolidado para as peças que chegam entre D16 e D20 […]"

- **IA1: REVISAR.** Com as novas entregas, a janela D16–D20 não cobre mais todas as chegadas (no G01, por exemplo, seria D17–D24).
- **IA2: DECISAO_HUMANA.** A janela é uma proposta administrativa e não afirma cobrir todas as peças; uma pessoa decide se amplia.

**Decisão:** ______

## P4. `ACTION_LOG.A06`, só no G12 (1 caso)

No G12, a ElecBoard passa para D20, ainda dentro da janela.

- **IA1: CORRETO.**
- **IA2: DECISAO_HUMANA.** Uma entrega abrangida pela negociação mudou.

**Decisão:** ______

## P5. `STATUS_A.RESUMO`, em G11 e G12 (2 casos)

> "[…] O orçamento aprovado é de R$ 152.000,00."

- **IA1: REVISAR.** Trata a frase como o custo atual: indeterminado no G11 e R$ 152.800 no G12.
- **IA2: CORRETO.** "Orçamento aprovado" é o registro da aprovação inicial, não o custo atual.

**Decisão:** ______

## P6. `RISK_REGISTER` R01, R02 e R06, só no G08 (3 casos)

No G08, a montagem fica mais curta (D20→D23), mas o início em D20 e o fim em D40 não mudam.

- **IA1: CORRETO.** As datas de referência dos riscos continuam valendo.
- **IA2: DECISAO_HUMANA.** A montagem mudou; cabe avaliar se o risco continua adequado.

**Decisão:** ______

## P7. `RISK_REGISTER.R03`, só no G08 (1 caso)

> "Extensão do teste de vida. Se o teste exceder 10 dias, a validação passaria de D35, e cada dia extra custaria R$ 500 de laboratório e R$ 300 de gestão."

No G08, o teste de vida termina em D33 e quem define a validação é o térmico (D35); o laboratório já passou da franquia.

- **IA1: DECISAO_HUMANA.** A data D35 continua correta, mas o risco precisa ser reavaliado.
- **IA2: REVISAR** (`premissa_alterada`). Exceder 10 dias não moveria mais a validação nem acrescentaria custo.

**Decisão:** ______

## Conferência das concordâncias

O arquivo `amostra_concordancias.csv` traz 50 pares em que as duas IAs concordaram (semente 20261124). Marquem **sim** ou **não** em "CONFERE?"; se for "não", escrevam o rótulo correto.

## Próximo passo

Com as 7 decisões e a amostra conferida, eu gero `gabarito_final.json`, congelo o manifesto da rodada 2 (B, D e E; validação parcial; instruções v4) e peço o OK para rodar.
