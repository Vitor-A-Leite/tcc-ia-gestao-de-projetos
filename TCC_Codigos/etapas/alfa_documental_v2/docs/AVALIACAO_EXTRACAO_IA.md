# Extração de afirmações por IA: rodadas reais de 21/11/2026

## O que foi medido

A IA (`gpt-6-luna`, esforço `high`) leu os seis documentos em prosa do corpus de conteúdo e devolveu, para cada trecho, as afirmações verificáveis com citação literal, entidade e predicado. O pedido continha só o documento, o catálogo de entidades e o catálogo de predicados. A IA não recebeu o cálculo, o cenário, as afirmações de referência nem os estados esperados.

Depois das respostas, o código:

1. validou cada extração no contrato (`src/extracao.py`);
2. comparou o que foi extraído com as 29 afirmações de referência;
3. aplicou a revisão de conteúdo nos nove cenários D01–D09 usando as afirmações extraídas (condição B) e comparou com os 117 estados esperados.

Autorização do usuário em 21/11/2026, registrada em `execucao.json` de cada rodada: rodar, com gasto de até US$5.

## Rodada 1 — contrato `1-extracao-afirmacoes`

Pasta: `outputs/extracao_ia_20261121/`.

| Medida | Resultado |
|---|---|
| Respostas válidas no contrato | 2 de 6 |
| Rejeições | `campo_invalido` (2), `conhecimento_inconsistente` (1), `predicado_incompativel` (1) |
| Condição B | 9 de 117 estados iguais; 0 de 31 "revisar" encontrados |
| Custo | US$0,0074486 (6 chamadas conciliadas; 14.391 tokens de entrada, 12.019 de saída) |

As rejeições vieram principalmente de ambiguidades do contrato:

- **Fornecedor × componente.** Para "a entrega do motor", a IA listou `SUP_MOTOR` e `C_MOTOR` juntos; o predicado `valor` exige uma entidade. O catálogo não explicava a diferença.
- **Campos fora de `valor`.** As instruções não diziam qual `campo` e qual `conhecimento` usar em `sem_alteracao` e `risco`; a IA deixou `campo` nulo ou marcou `indeterminado`.
- **Frases compostas.** No Status Report original, "dentro do cronograma, dia 40, R$ 152.000" virou uma única afirmação, e a data do motor foi tratada como compromisso.

Também se constatou uma falha do protocolo: o exemplo de data relativa das instruções ("três semanas após o início" = 21) coincidia com a resposta do controle C1, que ficou contaminado nessa rodada.

As falhas foram preservadas; nenhuma resposta foi repetida para substituí-las.

## Rodada 2 — contrato `2-extracao-afirmacoes`

Pasta: `outputs/extracao_ia_v2_20261121/`. As instruções da v1 estão preservadas em `SISTEMA_V1`.

Mudanças, todas nas instruções e no catálogo de predicados, sem alterar o validador nem as referências:

- extrair separadamente cada afirmação de uma frase composta;
- datas comunicadas por fornecedor referem-se a `SUP_*`; `valor`, `no_prazo` e `critico` levam uma entidade;
- `campo` obrigatório em `valor`, `sem_alteracao` e `risco`; `conhecimento=indeterminado` só em `valor` pendente;
- `compromisso` só para ações registradas;
- exemplo de data relativa trocado por um que não coincide com nenhum controle.

| Medida | Resultado |
|---|---|
| Respostas válidas no contrato | **6 de 6** |
| Extração (casamento estrito por trecho, predicado, entidades e campo) | 26 verdadeiros positivos, 10 falsos positivos, 3 falsos negativos; 26 valores corretos |
| Controles | C1–C7 corretos, inclusive data relativa (21), paráfrase, valor pendente, outro projeto, frase sem afirmação e conflito no mesmo trecho (detectado) |
| Condição B, casamento estrito | 99 de 117 estados e motivos iguais; "revisar": 30 encontrados, 1 falso alerta, 1 omissão |
| Condição B, leituras equivalentes | 117 de 117; "revisar": 31 de 31, nenhum falso alerta |
| Custo | US$0,0080004 (6 chamadas conciliadas; 15.849 tokens de entrada, 12.831 de saída) |

As 18 divergências estritas têm duas causas, ambas leituras equivalentes:

- **Granularidade.** "Os demais fornecedores seguem conforme o previsto" foi extraída como quatro afirmações `sem_alteracao` (uma por fornecedor), e não como uma afirmação agrupada. No D05, a de `SUP_HOUSING` saiu corretamente como "revisar"; o casamento estrito conta isso como um falso alerta mais uma omissão.
- **Entidade da decisão.** DEC-01 foi associada a `PROJECT`, e a referência usa `T_CAD`. O catálogo não tem entidade para "arquitetura mecânica"; o estado é "preservar" nos dois casos.

Os demais falsos positivos da extração são leituras adicionais defensáveis (por exemplo, "manteve a entrega" como `sem_alteracao` em C2).

## Consumo acumulado

| | USD |
|---|---|
| Rodada 1 | 0,0074486 |
| Rodada 2 | 0,0080004 |
| Total das duas rodadas | 0,0154490 |
| Comprometido histórico após as rodadas | 4,970588735 (teto de US$20) |

Todas as 12 chamadas foram conciliadas no ledger `outputs/consumo_ia_real.sqlite`, sem reserva pendente.

## Limites

- **Desenvolvimento, não avaliação final.** Os documentos e as respostas esperadas foram redigidos pelo agente que implementou o sistema, e os cenários D01–D09 já eram conhecidos.
- **Ajuste após ver resultados.** A v2 foi escrita depois de ver as falhas da v1 nos mesmos documentos. O ganho mostra que as ambiguidades eram a causa principal, mas não estima o desempenho em documentos novos.
- **Uma tentativa por documento**, sem repetições: a estabilidade entre execuções é desconhecida.
- **Casamento.** A leitura "equivalente" foi verificada para as duas causas acima; não há regra geral de equivalência no código.
- **Próximo passo para valer como resultado do TCC:** documentos novos, respostas anotadas de forma independente pela dupla antes da execução e contrato congelado.
