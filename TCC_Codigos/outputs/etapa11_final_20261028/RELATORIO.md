# Experimento final — etapa 11

28/10/2026 · três casos inéditos · uma repetição por condição · preditor H 7.2 congelado.

**Experimento concluído: 9/9 execuções, 24 chamadas novas conciliadas e compromisso acumulado de US$ 4,567653865, sob o teto de US$ 5.** H acertou os três prazos e os dois custos determináveis, preservando a indeterminação monetária real. B e T tiveram uma resposta global rejeitada cada por falta do campo obrigatório `justificativa`; essas respostas permanecem inválidas na comparação.

## Resultados por caso

Os valores abaixo são variações em relação à referência D15 / R$ 5.204,00. “Inválido” significa que a resposta não foi aceita pelo contrato congelado, mesmo quando seu conteúdo bruto era correto.

| Caso / alteração isolada | Referência completa: prazo; custo | B: prazo; custo | H: prazo; custo | T: prazo; custo |
|---|---|---|---|---|
| `k_1671298a5a` — duas durações substituídas | +4 dias; +R$ 344,00 | Aumento sem magnitude; aumento sem magnitude | +4 dias; +R$ 344,00 | +4 dias; +R$ 344,00 |
| `k_c23705f4ea` — configuração de 3 para 9 dias e taxa revogada | +6 dias; indeterminado | Inválido; inválido | +6 dias; indeterminado | Inválido; inválido |
| `k_ec2826cc2a` — crédito em parcela existente | 0 dias; −R$ 116,00 | 0 dias; −R$ 116,00 | 0 dias; −R$ 116,00 | 0 dias; −R$ 116,00 |

No primeiro caso, B não recebe as arestas. Sua justificativa demonstra corretamente que um caminho de 15 dias inclui ao menos uma atividade alongada, pois as demais durações somam somente 14 dias. Portanto, identifica aumento de prazo e custo, sem inventar magnitude. Os domínios auditados para B são {3, 4, 6} dias e {258, 344, 516} reais. Essa menor cobertura é coerente com a informação disponível.

No caso incerto, H calcula D21 e mantém o custo desconhecido: a extensão custa **6r centavos**, com taxa substituta inteira `r ≥ 0`, sem limite superior. Zero é possível, mas não está identificado; a taxa antiga de R$ 86/dia não foi reutilizada. H conserva o limite inferior de zero para o delta, mas não serializa a restrição discreta de múltiplos de seis. Esse limite externo é correto e menos informativo que o domínio completo.

No crédito, as três condições mantêm D15 e calculam R$ 5.088,00. O zero temporal é sustentado pela declaração expressa de manutenção das condições, e o crédito é aplicado uma única vez à obrigação existente.

## Comparação com denominadores

Cada condição tem N=3, incluindo as respostas inválidas. Há três referências temporais exatas e apenas duas referências monetárias exatas. Cobertura exata, acerto sobre referências exatas e indeterminação adequada são medidas diferentes.

| Medida | B | H | T |
|---|---:|---:|---:|
| Execuções válidas, completas ou parciais | 2/3 | 3/3 | 2/3 |
| Prazo: cobertura exata | 1/3 | 3/3 | 2/3 |
| Prazo: acerto exato / referências exatas | 1/3 | 3/3 | 2/3 |
| Custo: cobertura exata | 1/3 | 2/3 | 2/3 |
| Custo: acerto exato / referências exatas | 1/2 | 2/2 | 2/2 |
| Direção correta de prazo / referências com direção | 2/3 | 3/3 | 2/3 |
| Direção correta de custo / referências com direção | 2/2 | 2/2 | 2/2 |
| Indeterminação monetária adequada em resposta válida | 0/1 | 1/1 | 0/1 |
| MAE de prazo, somente pares exatos válidos | 0 dias (n=1) | 0 dias (n=3) | 0 dias (n=2) |
| MAE de custo, somente pares exatos válidos | R$ 0 (n=1) | R$ 0 (n=2) | R$ 0 (n=2) |
| Falsa precisão em desfechos válidos observados | 0 | 0 | 0 |
| Zero temporal sustentado | 1/3 | 1/3 | 1/3 |

O prazo indeterminado da view B no segundo caso também não conta como abstenção válida: seu envelope foi rejeitado. Na interseção pareada de respostas exatas, B/H e B/T têm n=1 por dimensão; H/T têm n=2 por dimensão. Todos esses erros são zero. Esses denominadores pequenos não permitem concluir superioridade global a partir do MAE.

Estados normalizados por dimensão: B tem um exato, uma direção e um inválido tanto em prazo quanto em custo; H tem três prazos exatos e dois custos exatos mais um indeterminado; T tem dois exatos e um inválido em cada dimensão. Não houve contradição dos domínios auditados, erro aritmético ou direção incorreta entre as previsões válidas. A rejeição de formato continua sendo falha do sistema.

## Falhas e auditoria de suporte

As chamadas **1129 (T)** e **1130 (B)** produziram JSON sintaticamente válido, com identidades corretas e quantidades individualmente válidas, mas omitiram `justificativa` no nível superior. O validador global exige esse campo; o registro de execução marca `saida_invalida`, normalizada como inválido em ambas as dimensões.

O bruto T contém D21, delta +6 e a expressão monetária 520400+6r, reconhecendo que a taxa pode ser zero. O bruto B conserva prazo e custo indeterminados por ausência de arestas e da taxa. A leitura diagnóstica é coerente com as fontes. **Nenhum campo foi inserido, nenhuma resposta foi reparada e nenhuma pontuação foi recuperada.** A diferença H/T no prazo desse caso decorre da validade da entrega; não demonstra erro de cálculo de T. Evidência integral em [falhas_formato.json](falhas_formato.json), vinculada às chamadas originais.

A auditoria posterior do coordenador examinou as 18 dimensões: 14 desfechos válidos sustentados; quatro dimensões sem desfecho aceito, registradas como suporte insuficiente por invalidez do envelope. Não há julgamento sem vínculo ao hash da resposta e à view. O julgamento do bruto rejeitado é separado da pontuação principal.

H teve **18/18 análises locais válidas**, seis por caso. Foram conferidas as fontes efetivamente presentes nos contextos, as cinco propostas no total, os 20 encaminhamentos resolvidos e as seis parcelas únicas de cada livro. O caso incerto tem fechamento operacional completo e resultado monetário parcial por lacuna real; isso não constitui pendência de interpretação. [Auditoria dos desfechos](auditoria_semantica.json) e [rastro local auditado](auditoria_local_H.json).

As referências foram derivadas e revisadas cegamente na etapa 10, antes das previsões. Esta auditoria das respostas foi feita pelo coordenador após a coleta, sem cegamento. Não é parecer humano nem revisão científica externa; nenhuma assinatura foi presumida.

## Tempo e custo

| Medida, três execuções por condição | B | H | T |
|---|---:|---:|---:|
| Chamadas de inferência | 3 | 18 | 3 |
| Latência mediana por execução | 55,80 s | 63,30 s | 23,48 s |
| Faixa observada | 16,69–75,31 s | 34,39–74,88 s | 18,32–32,52 s |
| Inferência conhecida | US$ 0,007209025 | US$ 0,027143525 | US$ 0,004875650 |
| Compromisso incremental, incluindo provisão de contagem | US$ 0,013209025 | US$ 0,063143525 | US$ 0,010875650 |

O incremento total foi **US$ 0,087228200**: US$ 0,039228200 de inferência calculada a partir do uso observado e US$ 0,048000000 de provisão de contagem. Todas as 24 chamadas, IDs 1115–1138, foram conciliadas; as duas rejeições de formato também geraram consumo e permanecem contabilizadas. Houve 24 operações de contagem e 24 de geração, sem retries, fallback ou novas reservas desconhecidas.

A carteira única passou de US$ 4,480425665 para **US$ 4,567653865**, restando **US$ 0,432346135** sob o teto acumulado. A composição final é US$ 2,103153865 de inferência conhecida, US$ 2,276000000 de provisão de contagem e US$ 0,188500000 de inferência reservada em 13 tentativas históricas desconhecidas. Essas reservas foram preservadas. Compromisso conservador interno não é confirmação da fatura.

As tarifas verificadas em 28/10/2026 foram US$ 0,10/M de entrada simples, US$ 0,01/M de leitura em cache, US$ 0,125/M de escrita em cache de 30 minutos e US$ 0,50/M de saída. As categorias de entrada foram tratadas como disjuntas; os tokens de raciocínio já pertencem à saída total. Fontes: [modelo gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna) e [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). A provisão de US$ 0,002 por contagem é hipótese conservadora do projeto, não preço publicado. [Memória de cálculo](auditoria_uso.json).

## Protocolo, integridade e conclusão

Foram usados os três casos inéditos de `data/final/etapa10_v2`, na ordem prospectiva B/H/T, H/T/B e T/B/H. Modelo solicitado e observado gpt-6-luna, reasoning high, Standard/default, stream, cache 30m, entrada oficial até 16.000 tokens, saída até 25.000, 180 s por chamada e até oito chamadas/1.500 s por H. H fez seis chamadas por caso. O limite autorizado era 30 tentativas, com reserva máxima incremental de US$ 0,495; nenhuma execução foi repetida.

O executor novo fica fora de `src`; passou em oito testes offline com cópias descartáveis da carteira. O adendo foi congelado antes da coleta. Preditores, prompts, inputs, views e gabaritos não foram alterados após observar resultados. B/T enviaram exatamente suas views congeladas; os contextos H foram vinculados ao snapshot e conferidos. Referências não foram carregadas pelos preditores.

Foram conferidos **253 artefatos do congelamento da etapa 10**, **152 arquivos do runtime** e o inventário de **1.768 arquivos anteriores**. As únicas alterações nesse inventário são os documentos vivos STATUS/PLANO e a carteira canônica por acréscimo da nova coorte; as tabelas históricas e as chamadas 1–1114 mantêm o hash anterior. Snapshot final, respostas em arquivos e respostas no ledger coincidem. [Comprovante de integridade](integridade_depois.json).

Os cinco itens do [critério de conclusão](../../docs/desenvolvimento/ETAPA_11_CRITERIO_CONCLUSAO.md) foram cumpridos. As métricas do avaliador congelado foram reproduzidas por contagem separada, os custos recalculados de `usage`, os desfechos e as falhas auditados e o orçamento preservado. O aceite é do experimento executado e documentado, não de perfeição geral do sistema.

Três casos sintéticos de um único projeto e uma repetição por condição não sustentam generalização, estabilidade ou superioridade estatística. B recebe menos relações; H também difere de T por decomposição, cálculo externo, múltiplas chamadas e schema estrito, enquanto B/T usam JSON global. A comparação é entre sistemas completos; o efeito isolado do grafo não foi identificado. Os casos finais agora estão expostos: correções futuras de contrato devem ser avaliadas em novos casos reservados, sem reclassificar esta coleta.

## Reprodução offline e evidências

Na raiz do projeto, sem credencial e sem rede:

```bash
python3 TCC_Codigos/outputs/etapa11_final_20261028/registrar_auditoria_semantica.py
python3 TCC_Codigos/outputs/etapa11_final_20261028/auditar_coleta.py
```

Os scripts aceitam artefatos existentes somente quando o conteúdo coincide; não modificam as previsões. Não executar novamente o comando de coleta como forma de avaliação.

- [Manifesto](manifesto.json), [adendo congelado](adendo_aprovado.json), [preflight](preflight.json), [testes](testes_executor.log) e [log da coleta](coleta.log).
- [Resultados originais agregados](registros.json), [normalização](normalizacao.json), [métricas auditadas](metricas_auditadas.json), [recontagem independente](recontagem_metricas.json) e [latências](operacional.json).
- Snapshots `ledger_antes.sqlite` e `ledger_final.sqlite`, carteira canônica preservada e [selo final](selo_final.json).
