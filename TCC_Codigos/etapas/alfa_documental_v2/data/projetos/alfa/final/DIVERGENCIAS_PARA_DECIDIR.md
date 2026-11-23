# Divergências entre as duas IAs anotadoras

Data: 23/11/2026. Arquivos comparados (SHA-256):

- `anotacoes1.json`: `11a5efb3fca6e0fd7aea1431f0a34ed3a9c96b8296650d42740b806889746ccb`
- `anotacoes2.json`: `0e8ecdb0cf5f6ecb74a73da6158949c70e5360fc54a9abee8573202ef9eb0159`
- `material_gerado.json`: `74efadaa25cca3fa359f516ebcad9bea291e0fe49b486d47472d314be14d99dc`

## Resumo

| Medida | Valor |
|---|---|
| Pares anotados (15 eventos × 34 trechos) | 510 |
| Mesmo rótulo | 463 (90,8%) |
| Kappa de Cohen (5 rótulos) | 0,850 |
| Mesma decisão "revisar × não revisar" | 482 (94,5%) |
| Quando as duas marcaram REVISAR, mesmos motivos | 206 de 245 |

As 47 divergências se concentram em **7 padrões**. Cada padrão se repete em vários eventos pelo mesmo motivo, então basta decidir uma vez por padrão.

## Como decidir

Marque **IA1**, **IA2** ou **outro** na coluna "Decisão" de cada padrão. A regra escolhida será aplicada a todos os eventos listados. Decidam juntos, sem consultar como o sistema se comporta.

## Os 7 padrões

### P1. `STATUS_A.OBSERVACOES`, em todos os eventos (15 casos)

> "A equipe está motivada, e a comunicação entre engenharia e suprimentos tem sido muito boa. Ana fará a próxima revisão do cronograma ao fim do detalhamento CAD."

- **IA1: CORRETO.** Considera "revisão ao fim do detalhamento CAD" uma informação que continua válida.
- **IA2: SEM_AFIRMACAO.** Considera tudo opinião ou intenção sem data verificável.
- Observação: o fim do CAD é D10 e não muda em nenhum evento, então os dois rótulos significam "não precisa revisar".

**Decisão:** IA2 (SEM_AFIRMACAO), decidida pelo agente aplicando as regras do prompt de anotação (ver `gabarito_final.json`).

### P2. `STATUS_C.OBSERVACOES`, em F02, F03, F04, F06, F07 e F09 a F14 (11 casos)

> "Bruno vai aproveitar o intervalo antes da montagem para revisar o procedimento de torque. A equipe recebeu bem a reprogramação."

- **IA1: CORRETO.** O "intervalo" não tem data; nada verificável é contradito.
- **IA2: REVISAR** (`premissa_alterada`). A frase pressupõe uma folga entre compras e montagem, que só existe no cenário F01. Nos outros eventos, a montagem começa logo depois das compras.

**Decisão:** IA2 (REVISAR), decidida pelo agente aplicando as regras do prompt de anotação (ver `gabarito_final.json`).

### P3. `STATUS_B.ENGENHARIA`, em F01 a F03, F07 e F09 a F14 (10 casos)

> "[…] A montagem do protótipo ocorre ao longo da quarta semana."

- **IA1: REVISAR.** A montagem vai de D20 a D25, e D20 pertence à terceira semana (D14 a D20). O texto não diz que começa na terceira.
- **IA2: CORRETO.** 5 dos 6 dias estão na quarta semana; aceita como aproximação.
- Observação: é um efeito direto da convenção de semanas. No F05, F06 e F15 a montagem vai de D22 a D27, toda dentro da quarta semana.

**Decisão:** IA1 (REVISAR), decidida pelo agente aplicando as regras do prompt de anotação (ver `gabarito_final.json`).

### P4. `STATUS_B.ENGENHARIA`, só em F06 (1 caso)

> "O detalhamento CAD termina na segunda semana, e a análise estrutural fecha logo depois, sem pendências previstas."

- **IA1: CORRETO.** As datas continuam compatíveis com as semanas.
- **IA2: REVISAR** (`premissa_alterada`). O evento F06 é justamente a análise estrutural estendida por pendência de refinamento, o que contradiz "sem pendências previstas".

**Decisão:** IA2 (REVISAR), decidida pelo agente aplicando as regras do prompt de anotação (ver `gabarito_final.json`).

### P5. `RISK_REGISTER.R2`, em F01, F04, F05, F06, F08 e F15 (6 casos)

> "O teste de vida pode ultrapassar os 10 dias previstos, levando a validação para depois de D35 […]"

- **IA1: DECISAO_HUMANA.** A frase é condicional e continua verdadeira; uma pessoa decide se o risco precisa ser atualizado.
- **IA2: REVISAR** (`valor_divergente`). A data de referência D35 mudou (por exemplo, D38 no F01).

**Decisão:** IA2 (REVISAR), decidida pelo agente aplicando as regras do prompt de anotação (ver `gabarito_final.json`).

### P6. `ACTION_LOG.A3`, em F03, F06 e F15 (3 casos)

> "Enviar ao fornecedor das peças usinadas o desenho CAD revisão 1 […] Prazo: D10. Situação: concluída."

- **IA1: DECISAO_HUMANA.** Está ligada à MetalForm (F03, F15) ou à engenharia (F06), que mudaram.
- **IA2: CORRETO.** A ação já está concluída e nenhuma informação dela ficou errada.

**Decisão:** IA1 (DECISAO_HUMANA), decidida pelo agente aplicando as regras do prompt de anotação (ver `gabarito_final.json`).

### P7. `ACTION_LOG.A1`, só em F07 (1 caso)

> "Obter da GearWorks a confirmação formal da entrega do redutor em D20 […] Situação: em andamento."

- **IA1: DECISAO_HUMANA.** O F07 é exatamente a confirmação pedida; alguém precisa decidir se encerra a ação.
- **IA2: CORRETO.** Pela regra, DECISAO_HUMANA exige que algo tenha mudado, e no F07 nada mudou.

**Decisão:** IA2 (CORRETO), decidida pelo agente aplicando as regras do prompt de anotação (ver `gabarito_final.json`).

## Conferência das concordâncias

O arquivo `amostra_concordancias.csv` traz 50 pares em que as duas IAs concordaram, sorteados com semente fixa (20261123). Para cada um, marquem **sim** ou **não** em "CONFERE?". Se for "não", escrevam o rótulo correto. A taxa de acerto dessa amostra entra na metodologia como estimativa da qualidade das concordâncias.

## Próximo passo

Com as 7 decisões e a amostra conferida, eu gero o gabarito consolidado (`gabarito_final.json`) e registro seu hash e data. A partir daí ele fica congelado, e só então rodamos as condições com IA.
