# Protocolo prospectivo de coleta — NÃO AUTORIZADO / NÃO EXECUTADO

A preparação e a demonstração são offline. O adaptador `LocalV07R3` continua disponível por injeção na fronteira `pipeline.executar`; isso não é prova de uma chamada real. O CLI e o servidor desta etapa não carregam chaves nem expõem execução paga. A integração transacional de uma nova coorte de 32 chamadas por execução na carteira única permanece pendente de autorização e de adendo; o runner histórico de oito chamadas não deve ser disparado para o Alfa.

## Carteira existente

Banco canônico: `../../outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite`, lido em modo somente leitura. 1.138 tentativas históricas, 13 reservas desconhecidas preservadas. Compromisso US$ 4,567653865; teto US$ 5; saldo US$ 0,432346135. `orcamento_antes.json` contém o hash e os valores inteiros em nanoUSD. Não houve reinício de contabilidade nem nova chamada de contagem/inferência.

As autorizações anteriores referem-se às coortes da Sálvia e às suas condições. Não cobrem automaticamente esta ampliação do Alfa nem o aumento de chamadas por execução.

## Coleta proposta

| Fase | Casos / repetições | Execuções H | Máximo de chamadas locais | Provisão incremental histórica |
|---|---|---:|---:|---:|
| Piloto de integração | D02 e D04, uma vez cada | 2 | 64 | US$ 1,056 |
| Avaliação reservada posterior | H01–H08, duas repetições | 16 | 512 | US$ 8,448 |
| Total, se ambas forem aprovadas separadamente | 18 execuções | 18 | 576 | US$ 9,504 |

A provisão usa **US$ 0,0165 por tentativa**, reproduzindo a reserva interna histórica (`piloto_real.ledger.RESERVA`): US$ 0,0145 de inferência e US$ 0,002 de contagem hipotética. **Não é cotação atual do provedor nem custo observado do Alfa.** Cada tentativa admite uma contagem e uma inferência; logo, 64 inferências correspondem a até 128 requisições HTTP no piloto. Se os preços atuais exigirem reserva maior, não iniciar sem revisão do teto.

Somente o piloto elevaria o compromisso máximo a **US$ 5,623653865**, acima dos US$ 5 existentes. Propõe-se autorização específica de até **US$ 1,056 adicionais**, com teto acumulado de **US$ 5,63**, somente para D02/D04, 64 chamadas locais e nenhuma repetição automática. A avaliação reservada exigirá aprovação separada; piloto + avaliação completos levariam a US$ 14,071653865 pela mesma hipótese conservadora.

## Procedimento obrigatório antes e durante a coleta

1. Confirmar modelo/configuração e preços vigentes; o histórico usou `gpt-6-luna`, reasoning high, Standard/default, SSE. Esta etapa não verificou disponibilidade/preço atual pela API.
2. Auditar independentemente referências e regras documentais; não enviar referências nem fixtures de simulação ao modelo. Menções e trechos cadastrados são entradas; operações locais serão produzidas pelo modelo.
3. Congelar hashes de código, inputs, prompts, schema, responsabilidades e protocolo. Uma repetição é uma nova execução identificada; falhas não são apagadas. Os oito casos finais permanecem sem execução; são autorais, não cegos ao autor e não constituem teste externo.
4. Criar adendo append-only na **mesma** carteira, com slots Alfa próprios, reserva atômica, teto acumulado e limite de 32 chamadas por slot. Testar em cópia temporária da carteira, preservando tabelas/chamadas históricas. Não executar com um ledger vazio ou com a classe histórica de limite oito.
5. Contar oficialmente cada payload sem truncamento. Limite planejado: entrada 16.000, saída total 25.000 tokens, 180 s por chamada, 5.820 s por execução H. Os 288 contextos offline foram medidos em bytes; isso não atesta contagem de tokens. Se ultrapassar limites, parar e preservar a tentativa, sem cortar fontes/nós.
6. Persistir pedido, resposta bruta, IDs, tokens, uso, custo reservado/conciliado, rejeições e falhas imediatamente. Sem retry, fallback, reparo ou preenchimento retrospectivo. Interrupções retêm reservas desconhecidas.
7. Avaliar prazo e custo separadamente, com estados exato/indeterminado e magnitudes. Denominadores incluem falhas. Documentos: unidade cenário × documento@versão × trecho × campo; TP/FP/FN/TN, precision, recall, F1, abstenções e sustentação por fonte. Revisão semântica independente deve verificar se as evidências implicam a recomendação, não apenas se a citação existe.
8. Não autorizar atualização oficial a partir do resultado do modelo. Recomendações, decisão humana e execução de edição permanecem registros distintos.

Os resultados offline demonstram integração de componentes de software com entradas preparadas. O piloto real mediria viabilidade de execução e falhas de interpretação nessa configuração; 16 execuções finais ainda seriam uma avaliação pequena de um projeto sintético. Não sustentam superioridade geral nem causalidade isolada do grafo.
