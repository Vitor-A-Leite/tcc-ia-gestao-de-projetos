# Correções de escopo e conhecimento no revisor v3

## Implementação

O contrato `3-revisao-observacional` acrescenta referências de cadastro para o escopo, extração estruturada das afirmações de valor e comparações determinísticas. O cadastro explicita as equivalências entre “Alfa v1”, `ALFA-AMPLIADO` e a versão `1.0.0`, além da vigência prospectiva desde D0 já usada pelo normalizador. O instante de observação tem campo próprio. Cada pacote registra a origem, o snapshot e o hash do cadastro.

O revisor usa `CONTEXTO.ESCOPO` para os metadados e IDs documentais para as afirmações extraídas. O código compara `restricoes_escopo` com o cadastro e `fundamentos_valor` com os valores propostos. A combinação de fonte indeterminada e proposta exata exige suporte insuficiente. Afirmações de outro objeto ou vigência também são insuficientes para sustentar a magnitude no contexto avaliado. Valores exatos incompatíveis, com aplicabilidade alinhada, permitem identificar contradição.

A suíte completa passou com 123 testes. Inclui releitura integral dos 23 pareceres v2, as quatro regressões de escopo, desconhecimento em D04/D09, N03, aliases, projeto/versão/vigência divergentes, parâmetros monetários compostos, orçamento, retomada e a rejeição observada no controle N06.

## Avaliação com IA

A rodada de 11/11/2026 utilizou `gpt-6-luna` com esforço `high`, em 19 propostas históricas e nove controles. Na primeira execução, 26 dos 28 casos produziram pareceres válidos. N01 apresentou falha de rede e N06 foi rejeitado por incoerência entre campos. Uma retomada técnica de N01, com o mesmo pacote, prompt, modelo e configuração, produziu um parecer válido de suporte insuficiente. A consolidação contém 27 casos válidos e um caso retido para revisão, em 29 tentativas. [Comparação da primeira execução](../outputs/avaliacao_revisor_v3_20261111/comparacao.json), [consolidação após retomada técnica](../outputs/avaliacao_revisor_v3_retomada_N01_20261111/consolidacao.json)

## As 19 propostas históricas

| Medida | v2 | v3 |
|---|---:|---:|
| Respostas válidas no contrato | 19/19 | 19/19 |
| Pareceres sustentados | 15 | 19 |
| Pareceres de suporte insuficiente | 3 | 0 |
| Pareceres ambíguos | 1 | 0 |
| Tokens de entrada | 148.073 | 184.181 |
| Tokens de saída | 50.434 | 71.656 |
| Custo estimado em USD | 0,0400243 | 0,0542461 |

D03-01, D05-01, D09-01 e D09-02 receberam pareceres sustentados. As extrações documentais e as referências ao cadastro permitiram conferir a ausência de restrição conflitante de escopo. D04 e D09 conservaram os valores indeterminados na representação examinada. [Resultados das regressões](../outputs/avaliacao_revisor_v3_20261111/comparacao.json)

## Controles e limitação remanescente

| Caso | Situação | Referência autoral | Resultado validado |
|---|---|---|---|
| N01 | Restrição própria de M_PROTO_READY em D25, citando fornecedor e precedência | `suporte_insuficiente` | `suporte_insuficiente`, após retomada técnica |
| N02 | Proposta D26 diante de aviso D25 | `contradita` | `contradita` |
| N03 | Proposta D25 diante de disponibilidade desconhecida | `suporte_insuficiente` | `suporte_insuficiente` |
| N04 | Proposta D25 diante de alternativas D25/D27 | `ambigua` | `ambigua` |
| N05 | Documento exclusivo de outro projeto | `contradita` | `contradita` |
| N06 | Documento exclusivo de outra versão | `contradita` | `requer_revisao`, por incoerência |
| N07 | Início de vigência D10, com aplicação desde D0 expressamente excluída | `contradita` | `contradita` |
| N08 | Aliases cadastrados e vigência compatível | `sustentada` | `sustentada` |
| N09 | Data anterior D18 e nova magnitude pendente diante de proposta D25 | `suporte_insuficiente` | `suporte_insuficiente` |

Oito dos nove controles tiveram pareceres válidos coincidentes com a referência. Em N03, a IA extraiu o conhecimento indeterminado e o código conferiu a insuficiência de suporte para fixar D25. N05 e N07 exercitaram restrições genuínas de projeto e vigência. N08 exercitou a correspondência dos aliases cadastrados.

Em N06, a IA extraiu corretamente a exclusão da versão `1.0.0` e a aplicação exclusiva à versão `2.0.0`. Indicou `aplicabilidade=outro_objeto_ou_vigencia` para o valor D25 e marcou o aspecto `valor` como `contradito`. O comparador exige `insuficiente` para uma afirmação fora do contexto aplicável. O parser registrou `classificacao_valor_inconsistente` e reteve o parecer. A conclusão global bruta era `contradita`. O caso demonstra a utilidade da conferência de consistência e uma incoerência remanescente na resposta da IA. [Registro N06](../outputs/avaliacao_revisor_v3_20261111/casos/N06.json)

## Retomada técnica e orçamento

A primeira tentativa de N01 terminou com erro de rede após aproximadamente 180 segundos. Seu uso permaneceu desconhecido e a reserva de US$0,015 foi conservada. A retomada recebeu manifesto e diretório próprios, com vínculo ao registro original e identidade do pacote conferida. [Manifesto da retomada](../outputs/avaliacao_revisor_v3_retomada_N01_20261111/manifesto.json)

As 29 tentativas tiveram 28 chamadas conciliadas e uma com uso desconhecido. O consumo conhecido foi de 237.190 tokens de entrada e 114.790 de saída. O custo estimado conciliado foi US$0,08018826. Com a reserva de US$0,015, a rodada comprometeu US$0,09518826. O comprometimento histórico acumulado passou de US$4,859951475 para US$4,955139735, dentro do teto autorizado de US$20. [Consolidação financeira](../outputs/avaliacao_revisor_v3_retomada_N01_20261111/consolidacao.json)

## Integridade e alcance

Os arquivos da avaliação v2 foram preservados e conferidos por hash. A carteira conserva as linhas e reservas anteriores, com 29 novas tentativas identificadas. A primeira rodada v3 e sua falha técnica têm registros próprios. Os identificadores operacionais dos controles adicionais são neutros quanto à classificação esperada.

A comparação usa casos de desenvolvimento e referências autorais. A extração de afirmações e sua aplicabilidade continua sendo uma interpretação da IA. O código verifica vínculos e consistência das informações extraídas. A avaliação registra a correção dos problemas observados e a incoerência remanescente de N06.
