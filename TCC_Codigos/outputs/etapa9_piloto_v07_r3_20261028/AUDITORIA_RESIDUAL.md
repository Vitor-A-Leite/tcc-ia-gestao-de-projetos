# Auditoria técnica dos resultados restantes

Coorte v7 revisão 7.2, 90/90 execuções. Inspeção do mesmo autor, sem independência científica. Nenhuma resposta, referência ou resultado numérico foi reparado.

## Por que H não produz 30 valores exatos

As referências autorais permitem 26 prazos e 24 custos exatos. H recuperou 23 e 21, todos coincidentes com essas referências. As quatro magnitudes de prazo e seis de custo realmente desconhecidas permaneceram não exatas. As três execuções com referências exatas ainda não quantificadas são k_547a/1, k_547a/2 e k_f04b/2.

| Caso / repetição | Prazo H | Custo H, centavos | Categoria e evidência |
|---|---|---|---|
| [k_23d8/1](etapa9-v07-r3-90-BHT-R2-20261028-k_23d8-H-1.json) | indeterminado / desconhecida | indeterminado / desconhecida | lacuna factual e confirmação operacional não fornecida: Sem aceite/definição técnica. Propostas desconhecidas tiveram condição indeterminada e foram rejeitadas; direção de aumento do custo não recuperada. |
| [k_23d8/2](etapa9-v07-r3-90-BHT-R2-20261028-k_23d8-H-2.json) | indeterminado / desconhecida | indeterminado / desconhecida | lacuna factual e confirmação operacional não fornecida: Sem aceite/definição técnica. Propostas desconhecidas tiveram condição indeterminada e foram rejeitadas; direção de aumento do custo não recuperada. |
| [k_547a/1](etapa9-v07-r3-90-BHT-R2-20261028-k_547a-H-1.json) | indeterminado / desconhecida | indeterminado / desconhecida | encaminhamento de operação inadequada: Fornecedor pediu substituir_restricao/r_08f271 para uma isenção de cobrança. Responsável alterou corretamente c_724f; pedido temporal não foi confirmado. |
| [k_547a/2](etapa9-v07-r3-90-BHT-R2-20261028-k_547a-H-2.json) | indeterminado / desconhecida | indeterminado / desconhecida | encaminhamento de operação inadequada: Fornecedor pediu substituir_restricao/r_08f271 para uma isenção de cobrança. Responsável alterou corretamente c_724f; pedido temporal não foi confirmado. |
| [k_8c65/1](etapa9-v07-r3-90-BHT-R2-20261028-k_8c65-H-1.json) | 2 | indeterminado / desconhecida | lacuna factual exclusivamente monetária: Preço de extensão desconhecido; prazo +2 preservado. Pendência tipada de custo torna a direção desconhecida. |
| [k_8c65/2](etapa9-v07-r3-90-BHT-R2-20261028-k_8c65-H-2.json) | 2 | direcao / aumento | lacuna factual exclusivamente monetária: Preço de extensão desconhecido; prazo +2 preservado. Aumento do custo preservado sem magnitude. |
| [k_d307/1](etapa9-v07-r3-90-BHT-R2-20261028-k_d307-H-1.json) | indeterminado / desconhecida | direcao / aumento | lacuna factual de duração: Duração nova da usinagem desconhecida. Prazo sem magnitude/direção; custo em aumento sem magnitude. |
| [k_d307/2](etapa9-v07-r3-90-BHT-R2-20261028-k_d307-H-2.json) | indeterminado / desconhecida | direcao / aumento | lacuna factual de duração: Duração nova da usinagem desconhecida. Prazo sem magnitude/direção; custo em aumento sem magnitude. |
| [k_f04b/2](etapa9-v07-r3-90-BHT-R2-20261028-k_f04b-H-2.json) | indeterminado / desconhecida | indeterminado / desconhecida | omissão de confirmação estruturada: Justificativa diz que montagem permanece igual, mas propostas e índices da cláusula estão vazios. Política conservadora mantém duração e custo pendentes. |

k_547a: a operação contratual correta estava no contexto e no schema. O catálogo usa IDs sem descrição adicional do contrato; não houve ablação para separar efeito da apresentação e interpretação do modelo. Ambas as repetições v6 também eram parciais, por direção/hash; esses erros formais desapareceram, mas permaneceu a escolha inadequada de operação.

k_f04b/2: regressão pareada de cobertura, pois a v6 retornava -1 dia e -10000 centavos. A v7 não converte justificativa livre em confirmação operacional. A primeira repetição v7 resolveu a cláusula explicitamente e produziu os valores corretos. A exigência conservadora de resolver todas as cláusulas locais também deve ser revista quanto à aplicabilidade na etapa 10.

Perdas de direção sustentada de custo: k_23d8/1, k_23d8/2 e k_8c65/1. São três na v7, ante cinco na v6. Preservar ausência de magnitude não significa recuperar toda a informação disponível. Não houve magnitude exata indevida nem divergência numérica em H; isso é uma observação desta amostra autoral.

## Controles B/T

B/k_6d82/2 previu delta de custo zero, contra +15000 centavos na referência completa. Sua justificativa confundiu ausência de aditivo com ausência de cobrança por extensão; f_493d L01 exige aditivo para crédito por antecipação, enquanto extensão adicional já é cobrada pela regra vigente. Erro absoluto R$150; MAE de custo B R$16,67 nos nove pares elegíveis. A inferibilidade da magnitude por view B segue pendente; uma falta de relações não justifica afirmar zero.

T/k_23d8/1 previu aumento de prazo sem magnitude, embora a referência mantenha direção desconhecida devido a aceite/espera/duração não definidos. É um achado de direção excessiva frente à referência, separado do MAE e de falsa magnitude. A revisão independente permanece pendente.

Onze saídas globais foram rejeitadas: oito sem justificativa, duas com ID de fonte inexistente na entrada e uma com localizador divergente. A inspeção inclui as fontes serializadas dentro do texto relacional de T, conforme o contrato.

| Execução | Call | Rejeição observada no bruto |
|---|---:|---|
| [k_09c2-B-2](etapa9-v07-r3-90-BHT-R2-20261028-k_09c2-B-2.json) | 844 | Campo justificativa ausente |
| [k_0ca7-B-1](etapa9-v07-r3-90-BHT-R2-20261028-k_0ca7-B-1.json) | 861 | [{"fonte_id": "f_493c", "localizador_retornado": "L01", "localizador_visivel": null}] |
| [k_0ca7-B-2](etapa9-v07-r3-90-BHT-R2-20261028-k_0ca7-B-2.json) | 872 | [{"fonte_id": "f_493c", "localizador_retornado": "L01", "localizador_visivel": null}] |
| [k_23d8-B-2](etapa9-v07-r3-90-BHT-R2-20261028-k_23d8-B-2.json) | 886 | Campo justificativa ausente |
| [k_42a9-T-2](etapa9-v07-r3-90-BHT-R2-20261028-k_42a9-T-2.json) | 898 | Campo justificativa ausente |
| [k_8c65-B-1](etapa9-v07-r3-90-BHT-R2-20261028-k_8c65-B-1.json) | 945 | Campo justificativa ausente |
| [k_98f3-B-1](etapa9-v07-r3-90-BHT-R2-20261028-k_98f3-B-1.json) | 971 | Campo justificativa ausente |
| [k_a064-B-2](etapa9-v07-r3-90-BHT-R2-20261028-k_a064-B-2.json) | 1002 | Campo justificativa ausente |
| [k_a92f-T-2](etapa9-v07-r3-90-BHT-R2-20261028-k_a92f-T-2.json) | 1013 | Campo justificativa ausente |
| [k_b731-T-2](etapa9-v07-r3-90-BHT-R2-20261028-k_b731-T-2.json) | 1050 | Campo justificativa ausente |
| [k_e168-T-1](etapa9-v07-r3-90-BHT-R2-20261028-k_e168-T-1.json) | 1087 | [{"fonte_id": "f_d96520b3de", "localizador_retornado": "L03", "localizador_visivel": "L05"}] |

Os 25 desfechos B sem magnitude apesar de referência completa exata estão individualizados em triagem_todas_condicoes.json, com lacunas e justificativas. Eles não são automaticamente erros: B omite relações, e inferibilidade por view requer auditoria própria. As 180 combinações execução/desfecho foram classificadas; invalidade não foi tratada como acerto ou como preservação de conhecimento.

## Evidências e limite de conclusão

Fontes/trechos das lacunas: auditoria_lacunas_fontes.json. Notas com hashes de arquivos/contextos: notas_auditoria_manual.json. Matriz completa H: auditoria_tecnica.json. Comparação de magnitude/direção v6/v7: comparacao_incerteza.json. Erros globais reproduzíveis: auditar_erros_globais.py.

Os controles demonstram funcionamento do contrato e as falhas registradas. Não certificam suporte semântico de todas as respostas, validade independente dos gabaritos ou superioridade isolada do grafo. H usa schema estrito e B/T mantiveram modo JSON; diferenças de contrato influenciam a validade. Etapas 10/11 não iniciadas.
