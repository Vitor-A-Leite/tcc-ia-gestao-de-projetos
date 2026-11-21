# Avaliação do revisor v2

## Implementação e execução

O contrato v2 atribui a identificação do objeto avaliado e a recuperação literal das fontes ao código. A IA fornece a avaliação de sete aspectos e seleciona referências do catálogo. O parser verifica vínculos, cobertura de fontes e coerência entre os aspectos e a conclusão. Os registros v1 continuam legíveis. A suíte completa passou com 105 testes, incluindo 16 novas regressões.

Em 11/11/2026 foram executadas 23 avaliações com `gpt-6-luna` e esforço `high`. A rodada usou as 19 propostas históricas e quatro controles. Cada caso recebeu uma tentativa. Todos os pedidos, respostas, usos e hashes estão registrados. O manifesto identifica o código e as entradas utilizados. [Manifesto da avaliação](../outputs/avaliacao_revisor_v2_20261111/manifesto.json)

## Comparação das 19 propostas históricas

| Medida | v1 | v2 |
|---|---:|---:|
| Respostas válidas no contrato | 10/19 | 19/19 |
| Erros de identificadores | 6 | 0 |
| Erros de citação literal | 3 | 0 |
| Pareceres válidos `sustentada` | 10 | 15 |
| Pareceres válidos `suporte_insuficiente` | 0 | 3 |
| Pareceres válidos `ambigua` | 0 | 1 |
| Tokens de entrada | 122.391 | 148.073 |
| Tokens de saída | 26.222 | 50.434 |
| Custo estimado em USD | 0,0253501 | 0,0400243 |

As 19 respostas v2 avaliaram os sete aspectos e declararam todas as fontes citadas pelas propostas. O código recuperou os trechos originais a partir dos IDs. Entre os dez pareceres v1 válidos, sete conservaram a classificação global. A comparação inclui o consumo das 19 tentativas de cada versão. [Comparação detalhada](../outputs/avaliacao_revisor_v2_20261111/comparacao.json)

## Controles

| Caso | Proposta e evidência | Referência autoral | Resultado v2 |
|---|---|---|---|
| N01 | Restrição local do marco em D25, citando disponibilidade do fornecedor e precedência | `suporte_insuficiente` | `suporte_insuficiente` |
| N02 | D26 diante de aviso explícito de D25 | `contradita` | `contradita` |
| N03 | D25 diante de disponibilidade desconhecida | `suporte_insuficiente` | `contradita` |
| N04 | D25 diante de alternativas D25 ou D27 sem confirmação | `ambigua` | `ambigua` |

N01 reapresenta a proposta histórica de `release_M_PROTO_READY`. O revisor reconheceu que a disponibilidade se refere a `SUP_MOTOR` e que a relação de precedência oferece suporte à propagação. Identificou a ausência de evidência específica para mudar a restrição própria do marco. [Parecer N01](../outputs/avaliacao_revisor_v2_20261111/casos/N01.json)

Houve concordância exata em três dos quatro controles, e os quatro receberam pareceres desfavoráveis. Em N03, o revisor tratou a declaração de disponibilidade desconhecida como contradição da magnitude exata D25. A referência autoral trata essa situação como ausência de suporte para a magnitude. Essa diferença evidencia uma fronteira de classificação que ainda requer avaliação. [Parecer N03](../outputs/avaliacao_revisor_v2_20261111/casos/N03.json)

## Limitações semânticas observadas

Quatro propostas históricas receberam pareceres desfavoráveis por questões de escopo, em D03-01, D05-01, D09-01 e D09-02. Os pacotes contêm `evento.escopo`, `evento.instante_observacao` e identificação de projeto/versão. O revisor exigiu confirmação desses dados no texto de uma fonte ou uma correspondência explícita entre “Alfa v1” e `ALFA-AMPLIADO` versão `1.0.0`. Nos quatro casos, os demais aspectos aplicáveis foram classificados como sustentados. Isso indica uma exigência documental adicional introduzida pela interpretação do revisor. [D03-01](../outputs/avaliacao_revisor_v2_20261111/casos/D03-01.json), [D05-01](../outputs/avaliacao_revisor_v2_20261111/casos/D05-01.json), [D09-01](../outputs/avaliacao_revisor_v2_20261111/casos/D09-01.json), [D09-02](../outputs/avaliacao_revisor_v2_20261111/casos/D09-02.json)

A cobertura de fontes mede referências declaradas. O acerto semântico exige inspeção própria. As propostas históricas pertencem ao conjunto de desenvolvimento e os controles usam referência autoral. O ensaio permite observar o funcionamento do contrato e esses comportamentos específicos. Sua amostra é limitada para estimar desempenho em novos documentos.

## Consumo e integridade

As 23 chamadas consumiram 167.068 tokens de entrada e 61.174 de saída. O custo estimado a partir do uso informado e dos preços configurados foi US$0,0472938. O comprometimento histórico acumulado passou de US$4,812657675 para US$4,859951475, dentro do teto autorizado de US$20. Todas as chamadas desta rodada foram conciliadas. As reservas históricas foram preservadas.

Os hashes dos arquivos históricos conferiram ao final da avaliação. A comparação das linhas da carteira com a versão anterior do Git também confirmou a preservação dos registros financeiros anteriores. O executor mantém os checkpoints por caso e dispõe de testes de retomada, interrupção e teto financeiro. [Registro da execução](../outputs/avaliacao_revisor_v2_20261111/execucao.json)
