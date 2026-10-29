# Etapa 9 — piloto v06 e comparação com v05

27/10/2026, America/Sao_Paulo. **Integração concluída e coleta encerrada em 90/90 execuções.** Sem parada, reenvio ou alteração de respostas. Etapas 10/11 não iniciadas.

Autorização direta do usuário: “Pode integrar a v6 e rodar um novo piloto, mantendo o limite acumulado de US$ 5. Depois me mostre a comparação com a v5.”

## Resultado principal

A cobertura exata H passou de **9/30 para 16/30** em prazo e custo (30% → 53,3%): oito ganhos e uma perda entre os mesmos pares. MAE zero somente nos 16 pares exatos elegíveis de cada desfecho. H permanece abaixo de T nesta rodada em cobertura; nenhuma superioridade científica é inferida.

| Condição | Prazo exato v05 → v06 | Custo exato v05 → v06 |
|---|---:|---:|
| B — IA sem relações do grafo | 4/30 → 5/30 | 8/30 → 8/30 |
| H — grafo e IA por nó | 9/30 → 16/30 | 9/30 → 16/30 |
| T — IA com relações em texto | 23/30 → 21/30 | 21/30 → 20/30 |

Cobertura significa disponibilidade de quantidade exata, não taxa de acerto sobre as 30 execuções. B/k_d307/1 prevê aumento exato de R$25 frente a referência autoral direcional com limite inferior de R$25; candidato a falsa precisão. Assim, B tem oito custos exatos, mas sete pares de custo elegíveis ao MAE. B/T foram reexecutados sem mudança de seus algoritmos; suas diferenças não são atribuídas à v06 H.

H teve 195/203 análises válidas, cinco rejeições de direção e três de contexto_hash; v05 teve 176/178 válidas. Fechamentos completos operacionais: 10 → 17; um deles preserva indeterminação factual. Ocorrências de encaminhamento: 249 resolvidas e 25 pendentes, com possibilidade de vários nós apontarem à mesma operação. Mediana por execução H: 108,95 → 230,47 s; inferência conhecida H: US$ 0,279920255 → US$ 0,465194260 (+66,2%).

## Integração e limites

Pacote aditivo `src/piloto_v06` integra H v06 à carteira única e à avaliação isolada. Nova coorte de 90 IDs: 15 casos fictícios × B/H/T × duas repetições, com os mesmos inputs/views, ordem, modelo e parâmetros da v05. Modelo gpt-6-luna/High, streaming, Standard/cache 30 min, entrada oficial ≤16 mil tokens, saída total ≤25 mil, deadline total por chamada 180 s, H ≤8 análises e 1.500 s, zero retries/fallback. Até 300 tentativas novas (810 globais); teto monetário prevalece. Maior entrada oficial observada: 10.243 tokens.

55 testes offline aprovados antes da ativação: seis de integração/carteira, 27 H v06 e 22 SSE. Pareamento dos 90 slots conferido em inputs/hashes/configuração. Código e prompts congelados no adendo e preservados durante a coleta. Credencial local existente usada apenas para autenticar em api.openai.com.

## Carteira acumulada

| Parcela | USD |
|---|---:|
| Comprometido antes da v06 | 2,096607180 |
| Incremento comprometido v06 | 1,112032510 |
| Inferência conhecida v06 | 0,586032510 |
| Provisão hipotética de contagem v06 | 0,526000000 |
| **Comprometido acumulado** | **3,208639690** |
| **Saldo interno sob US$ 5** | **1,791360310** |

263 chamadas novas, todas conciliadas; 773 tentativas acumuladas. As 13 reservas desconhecidas anteriores foram mantidas. O comprometimento inclui reservas/provisões e não equivale à fatura. Não houve reinicialização de orçamento.

## Preservação e aprovação da execução

Conferidos 1.208 arquivos preexistentes, tabelas/schemas históricos, chamadas 1–510 e todos os JSONs por execução. Somente carteira e resumos STATUS/PLANO tiveram alterações previstas. Snapshots antes/depois e resultados v04/v05 preservados. Nenhum commit ou push nesta rodada.

A revisão automática inicialmente rejeitou a execução por considerar o payload possivelmente sensível. A inspeção confirmou dados inteiramente fictícios e loader restrito aos oito JSONs dos dois projetos. O mesmo comando foi aprovado após apresentar essas evidências. Nenhuma chamada ou reserva ocorreu na rejeição; nenhum documento pessoal entrou nos prompts.

## Entrega e próxima revisão

[Relatório comparativo completo](../../outputs/etapa9_piloto_v06_20261027/RELATORIO.md), [diagnóstico dos casos](../../outputs/etapa9_piloto_v06_20261027/DIAGNOSTICO.md) e [comparação por caso/repetição](../../outputs/etapa9_piloto_v06_20261027/comparacao_por_caso.csv).

Revisar as rejeições de identidade/direção, o encaminhamento que solicita substituição mas recebe confirmação de manutenção (k_b731/1), a resolução ausente de cláusula em k_f04b/1 e o candidato B/k_d307/1. Não modificar respostas para melhorar métricas. Referências autorais, inferibilidade por view e suporte semântico permanecem sem auditoria independente; esta é uma comparação descritiva de desenvolvimento. Etapas 10/11 permanecem não iniciadas.
