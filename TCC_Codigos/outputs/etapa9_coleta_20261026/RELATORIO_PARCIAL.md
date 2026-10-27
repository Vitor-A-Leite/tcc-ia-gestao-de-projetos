# Piloto real da etapa 9 — relatório parcial para revisão

26/10/2026, America/Sao_Paulo. **Coleta real interrompida antecipadamente por decisão operacional durante o piloto; não é experimento final.** Modelo `gpt-6-luna`, High, Responses API, Standard, cache 30 m, até 16.000 tokens de entrada por contagem oficial e 25.000 tokens gerados totais por chamada, zero retries/fallback. Protocolo v 03 e teto agregado US$ 5 preservados. Etapas 10/11 não iniciadas.

A chave local foi carregada somente pelo programa autorizado. Rótulo informado pelo usuário: **TCC-Impacto-Baseline**. O rótulo não foi inferido da credencial e não altera B/H/T. A outra chave, TCC-Impacto-Grafo-LLM-por-no, não foi adicionada nem usada pelo executor. Nenhum valor, trecho, tamanho ou hash de chave foi inspecionado/exibido.

## O que ocorreu

O diretório canônico não existia no início; `--preparar` criou plano/manifesto/ledger com 90 slots e nenhuma chamada. Uma única execução de`--rodar`, com rede autorizada, começou a coleta. Não se usaram fixtures/gabaritos na geração e não se reexecutou slot.

Durante a coleta, após os primeiros timeouts, o coordenador determinou interromper caso ocorressem cinco inferências consecutivas sem resposta pelo mesmo timeout. **Essa guarda foi uma decisão operacional posterior ao início, não uma regra pré-registrada do v 03.** Houve respostas completas intermediárias; depois, as tentativas 8–12 terminaram em cinco timeouts consecutivos. O monitor identificou o coletor dono do lock, enviou SIGINT e registrou a parada no ledger. A tentativa 13 já estava em andamento: ficou com custo desconhecido, sem liberação de reserva. Saída do coletor 130. Não houve aumento de deadline ou troca de modelo/chave/prompts/dados.

Estado final: **6 slots terminados,1 iniciado sem resultado final e 83 não iniciados**. Só k_09c2 tem resultados finais: duas repetições de B/H/T. O segundo caso na ordem, k_0ca7, teve H iniciado/interrompido. Os demais não foram executados; não se inventaram resultados para preencher a amostra.

| Condição | N planejado | Registros finais obtidos | Estado dos registros finais | Iniciado sem resultado | Não iniciados |
|---|---:|---:|---|---:|---:|
| B | 30 | 2 | 1 erro por timeout;1 parcial epistêmico | 0 | 28 |
| H | 30 | 2 | 2 parciais por falhas operacionais locais | 1 | 27 |
| T | 30 | 2 | 2 ok | 0 | 28 |
| Total | 90 | 6 |  | 1 | 83 |

O normalizador mantém todos os 90 slots. Seus 84 registros “ausente” correspondem a 83 não iniciados e 1 iniciado sem resultado; **não são 84 falhas de API**. Não houve divergência de hash/identidade/origem/condição/proveniência entre os seis registros existentes. Estados indeterminados de H são indisponibilidade causada por timeout, não evidência de abstenção adequada do modelo.

## Chamadas e causa observável

Foram marcadas 13 requisições de contagem e 13 inferências:4 retornos completos com uso conciliado,8 timeouts e 1 interrupção em andamento. Não houve retry. Todos os 13 inputs oficialmente contados ficaram entre 2186 e 4568 tokens, abaixo de 16.000. Nenhuma falha observada de autenticação/modelo/parâmetro; as evidências disponíveis mostram cortes no deadline HTTP, não resposta de erro do provedor.

| Tentativa | Slot | Fronteira | Resultado |
|---:|---|---|---|
| 1 | k_09c2 B R 1 | global | timeout |
| 2 | k_09c2 H R 1 | fornecedor n_73fa | timeout |
| 3 | k_09c2 H R 1 | preparação n_915c | análise local completa/válida |
| 4 | k_09c2 H R 1 | componente n_c820 | timeout |
| 5 | k_09c2 T R 1 | global | resposta completa/válida |
| 6 | k_09c2 B R 2 | global | resposta completa/válida, parcial epistêmica |
| 7 | k_09c2 T R 2 | global | resposta completa/válida |
| 8 | k_09c2 H R 2 | fornecedor n_73fa | timeout |
| 9 | k_09c2 H R 2 | preparação n_915c | timeout |
| 10 | k_09c2 H R 2 | componente n_c820 | timeout |
| 11 | k_0ca7 H R 1 | preparação n_7b42 | timeout |
| 12 | k_0ca7 H R 1 | pessoa n_914b | timeout; completou sequência de 5 |
| 13 | k_0ca7 H R 1 | usinagem n_c196 | interrompida por SIGINT |

Deadline:30 s por chamada lógica, incluindo contagem e inferência. Entre tentativas finalizadas com latência persistida nos envelopes, os timeouts ficaram aproximadamente entre 30,006 e 30,014 s. Os dois timeouts do slot interrompido têm erro/deadline registrados no ledger, mas não envelope final com duração individual; não se inventou medida exata. A análise H completa levou 23,863 s; T R 1,21,722 s; B R 2,29,059 s; T R 2,20,567 s. H R 1/R 2 consumiram 83,902 s/90,043 s até devolver parcial e bloquear descendentes. As medidas são observações deste caso, não médias gerais.

**Hipótese de engenharia: ** o deadline 30 s parece restritivo para este modo High/contextos. Há integração funcional de conteúdo (3 respostas globais e 1 análise local válidas), mas também 8 cortes temporais. Não foi observado quando o servidor terminaria as respostas cortadas nem medida separadamente a latência da contagem; portanto não se pode atribuir os timeouts exclusivamente ao raciocínio do modelo, à rede ou ao serviço. Isso motiva diagnóstico isolado com deadline maior, sem mudar simultaneamente modelo/prompts/dados.

## Prazo/custo versus referências autorais

Referência de desenvolvimento k_09c2: **+2 dias e+40000 centavos BRL(R$ 400)**. É derivação autoral previamente registrada, não gabarito científico independente. A avaliação não foi dependência do preditor. Os arquivos de referência originais e as previsões não foram corrigidos após a coleta.

| Resultado entregue | Prazo | Custo do projeto | Comparação numérica |
|---|---|---|---|
| B R 1 | sem previsão, timeout | sem previsão | sem par numérico |
| B R 2 | indeterminado por ausência de precedências | direção: aumento, sem total exato; texto menciona mínimo R$ 200 | direção de custo coincide com referência; fora do MAE |
| H R 1/R 2 | indeterminado operacional | indeterminado operacional | faltou interpretação validada de nós/cláusulas; fora do MAE |
| T R 1/R 2 | +2 dias | +R$ 400 | coincidência exata em ambas as repetições |

Cobertura exata é quantidade de previsões exatas válidas/N planejado; não é acurácia. MAE só usa predição e verdade exatas. Valores ausentes/erros não receberam zero nem penalidade arbitrária.

| Condição | Cobertura prazo | MAE prazo(n/N) | Cobertura custo | MAE custo(n/N) |
|---|---:|---|---:|---|
| B | 0/30 | não calculável(0/30) | 0/30 | não calculável(0/30) |
| H | 0/30 | não calculável(0/30) | 0/30 | não calculável(0/30) |
| T | 2/30(6,67%) | 0 dias(2/30) | 2/30(6,67%) | R$ 0(2/30) |

Os dois pares numéricos de T são duas repetições de **um único caso**, não dois projetos/casos independentes. Acerto exato T:2/26 referências de prazo exatas elegíveis e 2/24 de custo, sempre N 30. Direção de custo B:1/30 elegíveis, a partir de uma única resposta direcional. Interseções exatas B/H, B/T, H/T: **0/30 em prazo e custo**; todos os MAE pareados são desconhecidos. Não é possível concluir vantagem de T, de H ou de B desta coleta truncada. H/B diferem também em informação, decomposição, chamadas e solver; T não isola sozinho o efeito causal de representação.

## Indeterminação, falsa certeza e suporte

Nos quantitativos normalizados: B tem 1 indeterminado de prazo/1 direcional de custo; H tem 2 indeterminados por desfecho decorrentes de falhas operacionais; T tem 2 exatos por desfecho. O restante é erro/ausente para manter N 30, conforme discriminação acima. Não chamar indisponibilidade operacional de incapacidade matemática ou erro de interpretação do LLM.

Pela regra mecânica do avaliador, nenhuma das 2 afirmações exatas recebidas por desfecho(T) contradiz o estado de exatidão da referência por view previamente registrada:0/2 sinalizadas. **Isso não é auditoria semântica nem estimativa populacional da taxa de falsa certeza.** Não existem previsões exatas B/H recebidas para esse diagnóstico. A inferibilidade B de k_09c2 já estava pendente antes de ver respostas e permanece pendente. H/T usam referências por view autorais da etapa 7, sem validação independente; todos os novos casos Nácar conservam inferibilidade pendente.

Nenhuma auditoria de ligação fonte→condição→conclusão foi adicionada; suporte permanece`nao_auditado`, inclusive para T correto numericamente. Zero sustentado não foi demonstrado. Não premiar abstenção H por causa de timeout. O cálculo de métricas mecânicas está separado da validação autoral do contexto visível e da futura revisão científica independente.

## Custos e saldo — não é fatura do provedor

Uso conhecido somente das 4 inferências conciliadas: **15757 tokens de entrada e 10521 tokens de saída total**, incluindo raciocínio. Categorias de cache foram tratadas como disjuntas e o custo foi reconferido independentemente com Fraction e as tarifas USD aprovadas; sem dupla contagem de raciocínio/escrita. Uso das 9 tentativas sem resposta/uso suficiente **não é zero**.

| Parcela disjunta | USD |
|---|---:|
| Inferência calculada a partir deusage conhecido | 0,007229825 |
| Reserva de inferência não conciliada(9 × 0,0145) | 0,130500000 |
| Provisão hipotética de contagem(13 × 0,002) | 0,026000000 |
| Comprometimento interno total | **0,163729825** |
| Teto agregado aprovado | 5,000000000 |
| Saldo interno livre após reservas | **4,836270175** |

As 9 reservas integrais não conciliadas somam US$ 0,1485; esse valor **já inclui**US$ 0,018 de provisão dessas 9 contagens e não deve ser somado novamente à tabela. Não houve liberação dessas reservas na interrupção. A provisão total US$ 0,026 não é cobrança comprovada nem tarifa publicada da contagem. Não se consultou fatura/dashboard financeiro ou saldo da conta OpenAI, nem se inventou câmbio. O saldo acima é saldo do controle interno deste lote sob suas hipóteses, não crédito disponível na conta.

## Pós-processamento, validação e artefatos

A avaliação usa o manifesto original de 90 slots e os 6 registros originais do SQLite. O adaptador de relatório encontrou uma limitação já existente do avaliador v 1: ele rejeita limite no estado`indeterminado`. A referência Nácar k_d307 tem prazo indeterminado com limite Δ≥0. **O arquivo original permaneceu intacto e o estado não virou exato/direção**; na projeção de avaliação, esse limite fica no campo explícito`limite_indeterminado_preservado_fora_do_schema_v1`, com nota, e não entra no diagnóstico de limites do avaliador v 1. A referência continua sem par MAE. O limite direcional de custo≥2500 foi transcrito com a enumeração de proveniência autoral aceita pelo avaliador. Não há previsão entregue de k_d307 nesta coleta; essa adaptação não explica ou altera qualquer acerto observado.

Conferências pós-coleta: N 30 por condição;6 registros presentes e 84 ausentes coerentes com estado do ledger; nenhuma duplicata/divergência dos 6 hashes; recomputação separada de cobertura/MAE; conciliação independente da contabilidade conhecida; hash do código igual ao plano; dados/referências originais preservados. Essas são verificações de aritmética/proveniência, não independência científica. Nenhum teste com nova API foi feito.

- Originais canônicos:`../etapa9_piloto_real_aprovado_20261026/{ledger.sqlite,plano.json,manifesto.json}` e 6 exports JSON idênticos aos blobs originais.
- Snapshot consistente pós-parada:`snapshot_pos_parada/`, com hashes em`execucao_efetiva_v03.json`; não substitui nem zera o ledger original.
- `parada_diagnostica.json`, `monitor.log`, `acompanhamento.jsonl`: decisão operacional, identificação segura e evolução da coleta.
- `normalizacao.json`, `avaliacao_autoral.json`, `referencias_avaliacao_autoral.json`: resultados avaliados, denominadores e projeções autorais explícitas.
- `contabilidade_e_erros.json`: chamadas, causas, uso conhecido, reservas/saldo e proveniência.
- `avaliar_coleta.py`: reprodução apenas de pós-processamento; sem rede/chave/geração.
- `PROPOSTA_DIAGNOSTICO_SEGUINTE.md`: no máximo 2 chamadas propostas com deadline maior e o mesmo saldo acumulado; **não executadas**.

O piloto da etapa 9 permanece parcial e requer revisão. Nenhuma conclusão científica de superioridade, correção seletiva, alteração do protocolo original, zeragem de ledger, nova chave ou avanço às etapas 10/11.
