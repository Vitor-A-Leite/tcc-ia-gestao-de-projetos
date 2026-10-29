# Análise de impacto de eventos em prazo e custo

Material para redação do TCC • Experimento final de 28 de outubro de 2026

## Arquitetura e objetivo do sistema

O sistema investiga a estimação de variações de prazo e custo após eventos de projeto, associando cada conclusão às fontes disponíveis. O experimento final comparou três condições sobre os mesmos avisos: baseline global (B), arquitetura híbrida (H) e relações textuais (T). A arquitetura híbrida entregou corretamente os três prazos e os dois custos determináveis, mantendo a indeterminação monetária no caso cuja taxa substituta não foi definida. As condições globais apresentaram duas rejeições de formato, uma em B e outra em T. Esses resultados descrevem um conjunto exploratório de três casos sintéticos; não demonstram superioridade estatística. [R1–R3]

A unidade estrutural é uma atividade ou um marco, identificado de forma estável. Fontes documentais fornecem durações, precedências, restrições de liberação, parcelas e regras contratuais. O grafo contém relações fim-início com defasagem zero. O LLM interpreta alterações autorizadas para cada nó, formula propostas estruturadas e encaminha operações externas ao responsável correspondente. A coordenação verifica permissões, vínculos, condições e resolução dos encaminhamentos antes da aplicação operacional. [R4–R5]

O motor determinístico calcula os efeitos das propostas aceitas condicionalmente. Para uma atividade i, o início é o máximo entre os términos dos predecessores e as restrições de liberação. O término resulta da soma do início e da duração. Em uma convergência, utiliza-se o maior término dos ramos; seus atrasos não são somados. O custo total é consolidado em um livro de parcelas únicas, evitando que uma mesma obrigação seja cobrada novamente por aparecer em múltiplos ramos. [R4–R5]

O sistema distingue a validade operacional da sustentação semântica. Uma proposta pode satisfazer o contrato de estrutura sem que isso prove sua correção factual. Da mesma forma, conhecimento exato, direção conhecida e indeterminação são estados distintos. O resultado parcial é adequado quando uma magnitude não pode ser identificada; ausência de informação não é convertida automaticamente em zero. A sustentação é verificada depois, com vínculo à resposta e ao contexto efetivamente visível. [R2, R6]

| Condição | Informação e processamento | Saída e chamadas por caso |
|---|---|---|
| B | Fatos comuns e aviso, sem arestas específicas; previsão global pelo LLM | JSON global; uma chamada |
| H | Fatos comuns, relações, contextos por nó, coordenação e motor determinístico | Schema local estrito; seis chamadas observadas |
| T | Fatos comuns e relações de H serializadas em texto neutro; previsão global | JSON global; uma chamada |

As condições são sistemas completos com diferenças simultâneas de informação e processamento. A comparação B/H não isola o efeito do grafo, e H/T também difere por cálculo externo, decomposição e contrato de saída. [R3]

<!-- page -->

## Protocolo experimental e rastreabilidade

O projeto fictício Estação de leitura Sálvia possui cinco atividades, um marco final e seis obrigações de custo. A referência fixa é D15 e R$ 5.204,00. Todos os avisos são prospectivos em D0, sem execução iniciada, em dias corridos inteiros e valores monetários em centavos. Cada aviso é aplicado isoladamente à mesma referência; as mudanças não se acumulam entre os casos. [R4]

O conjunto final foi preparado na etapa 10, separado dos 15 casos empregados em desenvolvimento. As referências foram derivadas e revisadas tecnicamente por agentes distintos antes das previsões, com selos anteriores ao confronto. A versão final v2 esclareceu convenções temporais comuns e a lacuna da taxa, sem ajustar os preditores aos resultados finais. A revisão por agentes de IA não equivale a avaliação humana independente. A auditoria das respostas da etapa 11 foi posterior e realizada pelo coordenador, sem cegamento. [R3, R6–R7]

Foram planejados três casos por três condições e uma repetição, totalizando nove execuções. A ordem prospectiva foi B/H/T para o primeiro caso, H/T/B para o segundo e T/B/H para o terceiro. O balanceamento de posições reduz uma assimetria de ordem, mas não elimina efeitos temporais ou de cache. Uma repetição por condição não permite estimar estabilidade entre execuções. [R3]

O modelo solicitado e observado foi gpt-6-luna, com reasoning high, serviço Standard/default, streaming e cache de 30 minutos. Mantiveram-se os limites oficiais de 16.000 tokens de entrada e 25.000 de saída, 180 segundos por chamada e até oito chamadas ou 1.500 segundos por execução H. O protocolo proibiu retries, reparo de respostas e fallback. Houve 24 chamadas de inferência: três B, 18 H e três T. Todas foram conciliadas e nenhuma execução foi repetida. [R1, R8]

O preditor H 7.2, os prompts, a configuração, os inputs, as views e as referências permaneceram congelados. O executor da coleta foi integrado fora de src e submetido a oito testes offline antes da execução. Gabaritos permaneceram separados e não foram carregados pelos preditores. Após a coleta, conferiram-se 253 artefatos do congelamento anterior e a preservação das chamadas financeiras históricas 1–1114. [R1, R9]

| Caso | Alteração isolada | Referência no projeto completo |
|---|---|---|
| k_1671298a5a | Trilho de 4 para 8 dias e mapa de 7 para 10 dias | Término D19; custo R$ 5.548,00 |
| k_c23705f4ea | Configuração de 3 para 9 dias e revogação da taxa de apoio | Término D21; custo 520400 + 6r centavos |
| k_ec2826cc2a | Crédito definitivo de 11.600 centavos sobre parcela existente | Término D15; custo R$ 5.088,00 |

No segundo caso, r é inteiro não negativo e não possui valor ou limite superior definidos. A apuração do preço não condiciona a execução, permitindo prazo exato e custo indeterminado simultaneamente. [R4, R7]

<!-- page -->

## Medidas e critérios de interpretação

A unidade de evidência é o caso, e não a chamada local ao modelo. Cada condição tem N=3. O protocolo mantém falhas e respostas inválidas nos denominadores, evitando que sua exclusão produza uma comparação artificialmente favorável. A avaliação considera a verdade no projeto completo e, separadamente, o que a condição poderia inferir a partir de sua própria view. [R2–R3]

A cobertura numérica é a proporção de desfechos válidos com magnitude exata em relação às três execuções previstas. O acerto exato exige igualdade com a referência e usa como denominador o número de referências exatas: três para prazo e duas para custo. Assim, H pode ter cobertura monetária de 2/3 e acerto de 2/2 sem contradição, pois o terceiro custo é desconhecido por construção. [R2]

O erro absoluto médio (MAE) é calculado exclusivamente sobre pares em que tanto a previsão válida quanto a referência são exatas: MAE = soma dos erros absolutos dividida pelo número de pares elegíveis. Os denominadores são informados junto aos valores. Magnitudes indeterminadas, direções sem magnitude e respostas inválidas não recebem erro numérico zero. Por isso, MAE zero sobre um único par não caracteriza desempenho equivalente a MAE zero sobre três pares. [R2]

O acerto de direção considera aumento, redução ou zero quando a referência sustenta uma direção. A falsa precisão corresponde a declarar magnitude exata em contexto que permite apenas direção ou indeterminação. A indeterminação adequada exige resposta válida indeterminada quando a view não identifica a magnitude. O zero sustentado requer evidência positiva de ausência de variação, em vez de imputação pela ausência de informação. [R2, R6]

| Medida | B | H | T |
|---|---|---|---|
| Execuções válidas | 2/3 | 3/3 | 2/3 |
| Prazo exato correto por referência exata | 1/3 | 3/3 | 2/3 |
| Custo exato correto por referência exata | 1/2 | 2/2 | 2/2 |
| Cobertura exata de custo | 1/3 | 2/3 | 2/3 |
| Indeterminação monetária adequada | 0/1 | 1/1 | 0/1 |
| MAE de prazo | 0 dias; n=1 | 0 dias; n=3 | 0 dias; n=2 |
| MAE de custo | R$ 0; n=1 | R$ 0; n=2 | R$ 0; n=2 |

Fonte: métricas auditadas da etapa 11; recontagem separada conferida. N=3 em cada condição. “Válida” inclui resposta parcial quando a parcialidade representa indeterminação legítima. [R2]

Não houve falsa precisão observada nos desfechos válidos. A ausência dessa ocorrência em três casos não estima seu risco em outros projetos. Nas interseções de respostas exatas, B/H e B/T possuem apenas um par por dimensão; H/T possuem dois. Todos esses erros são zero. Não foram realizados testes de significância ou inferências populacionais. [R2]

<!-- page -->

## Resultados e explicação dos três casos

No caso das duas durações, o ramo de alinhamento termina em D14 e o ramo de configuração em D13. A validação depende dos dois, começa em D14 e termina em D19. O apoio cobre até D15; quatro dias adicionais a 8.600 centavos por dia acrescentam R$ 344,00. H e T entregaram esses valores exatos. H aplicou duas substituições de duração, preservou as demais condições e consolidou o apoio apenas uma vez. [R4–R5]

B identificou corretamente aumento de prazo e custo, mas preservou a ausência de magnitude. A justificativa observa que as atividades não alteradas somam 14 dias; portanto, um caminho que determinava D15 precisa conter pelo menos uma atividade alongada. Sem as arestas específicas, os deltas temporais admissíveis são 3, 4 ou 6 dias. Os deltas monetários correspondentes são R$ 258,00, R$ 344,00 ou R$ 516,00. A menor cobertura exata de B nesse caso é compatível com sua informação disponível. [R6–R7]

No caso da taxa desconhecida, a configuração passa a ocupar D7–D16 e a validação D16–D21. H entrega delta temporal de seis dias. A interpretação local do marco reconhece o aditivo e substitui a taxa antiga por valor desconhecido, mantendo fixo e cobertura. A extensão é 6r centavos. Como r pode ser zero, não é sustentado afirmar aumento estrito de custo. H preserva a indeterminação e o limite inferior zero; sua saída não codifica a restrição adicional de múltiplos de seis presente na referência suplementar. [R5–R7]

No crédito contratual, o aviso mantém explicitamente duração, liberação, precedências e condições do apoio. As três condições entregam delta temporal zero. H substitui a parcela de alinhamento de 138.600 para 127.000 centavos e conserva as seis obrigações únicas. O total cai de R$ 5.204,00 para R$ 5.088,00. B e T entregam a mesma redução de R$ 116,00. [R4–R6]

| Caso | B prazo e custo | H prazo e custo | T prazo e custo |
|---|---|---|---|
| Duas durações | Aumento; aumento | +4 dias; +R$ 344 | +4 dias; +R$ 344 |
| Taxa desconhecida | Inválido; inválido | +6 dias; indeterminado | Inválido; inválido |
| Crédito | 0 dias; −R$ 116 | 0 dias; −R$ 116 | 0 dias; −R$ 116 |

Fonte: respostas originais, sem reparo posterior. Aumento sem valor significa direção conhecida, não magnitude exata. Inválido indica rejeição do contrato de saída. [R2, R5]

O rastro H registra 18 análises locais válidas, cinco propostas e 20 encaminhamentos resolvidos no conjunto dos três casos. A conferência das citações mostrou que as fontes estavam presentes nos contextos efetivamente fornecidos. Esses registros apoiam a rastreabilidade da execução; sua existência, isoladamente, não constitui validação semântica automática. [R5–R6]

<!-- page -->

## Falhas de formato e custos observados

As respostas B e T do caso da taxa desconhecida foram rejeitadas porque omitiram o campo obrigatório justificativa no nível superior. As chamadas 1129 e 1130 produziram JSON sintaticamente válido, identidades corretas e quantidades individualmente válidas. O envelope completo não atendia ao contrato global congelado, gerando invalidez nas duas dimensões. Nenhum campo foi acrescentado e nenhuma resposta foi repetida. [R10]

A inspeção diagnóstica do bruto T encontrou D21, delta +6 e custo 520400+6r centavos, reconhecendo que a taxa pode ser zero. O bruto B preservou as indeterminações compatíveis com sua view. Portanto, a diferença H/T na entrega do prazo desse caso decorreu do cumprimento do formato, sem evidenciar erro de cálculo no conteúdo de T. O diagnóstico não alterou o resultado principal: respostas rejeitadas não foram recuperadas nas métricas. [R6, R10]

| Consumo nos três casos | B | H | T |
|---|---|---|---|
| Chamadas de inferência | 3 | 18 | 3 |
| Latência mediana | 55,80 s | 63,30 s | 23,48 s |
| Inferência conhecida em USD | 0,007209025 | 0,027143525 | 0,004875650 |
| Compromisso com provisão em USD | 0,013209025 | 0,063143525 | 0,010875650 |

Fonte: tempos dos registros e memória de cálculo de usage. Latências são observações de uma repetição por caso e não estimativas estáveis de desempenho. [R8]

O incremento financeiro do experimento final foi US$ 0,087228200, composto por US$ 0,039228200 de inferência conhecida e US$ 0,048000000 de provisão de contagem. As duas respostas rejeitadas também consumiram inferência e permaneceram contabilizadas. Houve 24 operações de contagem e 24 de geração, todas sem retry ou fallback. [R8]

O compromisso acumulado da carteira alcançou US$ 4,567653865, restando US$ 0,432346135 sob o teto de US$ 5. A composição inclui US$ 2,103153865 de inferência conhecida, US$ 2,276000000 de provisão de contagem e US$ 0,188500000 de inferência reservada em 13 tentativas históricas de custo desconhecido. Provisões e reservas são controles conservadores internos e não comprovação de faturamento. A etapa 12 apenas apresenta arquivos salvos e não acrescenta chamadas pagas. [R8–R9]

H utilizou mais chamadas e maior custo incremental que B ou T neste conjunto. A existência de cálculo externo, estrutura local e maior rastreabilidade deve ser considerada junto ao consumo e à validade de entrega. O experimento não estabelece um balanço geral entre custo e benefício para projetos reais. [R1–R3]

<!-- page -->

## Discussão e limites da evidência

Os resultados mostram que a implementação híbrida conseguiu converter alterações documentadas em propostas locais, propagar seus efeitos por precedências convergentes e consolidar custos sem duplicação nos três casos selecionados. A separação entre prazo e custo preservou o prazo calculável diante de lacuna financeira real. O experimento também demonstrou que validade de formato pode limitar a entrega de uma condição mesmo quando seu conteúdo bruto contém cálculos coerentes. [R1, R5–R6]

A hipótese de que relações estruturadas apoiam análise de impacto é compatível com o comportamento observado, mas não foi isolada causalmente. B tem menos informação relacional, enquanto H e T diferem em decomposição, número de chamadas, cálculo externo e schema. Uma ablação de mecanismos requereria controlar essas diferenças em outro protocolo. Alterar B/T após observar o conjunto final e avaliar nos mesmos casos não produziria uma nova avaliação independente. [R3]

A validade externa é limitada por três casos sintéticos de um único projeto pequeno e intencionalmente selecionado. Não há recursos compartilhados, calendários complexos, execução parcial, precedências variadas ou documentação de um projeto real. A estabilidade também é desconhecida, pois houve uma repetição por condição. Os resultados não devem ser descritos como prova de acurácia geral, robustez industrial ou superioridade estatística.

A revisão cega das referências ocorreu antes das previsões, por agentes distintos, enquanto a auditoria das respostas foi posterior e conduzida pelo coordenador. Essa organização melhora a rastreabilidade, mas não substitui parecer de um orientador ou especialista humano. O pacote de revisão da etapa 12 permite registrar a avaliação humana posteriormente, incluindo a exposição prévia aos resultados e eventuais conflitos de papel.

O sistema permanece um protótipo experimental auditável. O escopo demonstrado é a análise de impacto sobre prazo e custo em avisos sintéticos; o trabalho não avaliou manutenção automática de documentos reais, uso por equipes de projeto ou desempenho em produção. A redação do título, dos objetivos e das conclusões deve refletir essa delimitação, mesmo que documentos iniciais do TCC descrevam uma ambição mais ampla.

Como conclusão delimitada, H entregou resultados válidos e sustentados para as duas dimensões nos três casos, incluindo a indeterminação apropriada. B identificou o que era inferível nas respostas válidas, e T coincidiu com H nos dois casos em que seu envelope foi aceito. A contribuição demonstrada é uma implementação com rastros de interpretação, propagação e custos verificáveis, acompanhada de uma comparação exploratória que preserva falhas e incertezas.

## Uso deste material na redação

As seções anteriores podem integrar os capítulos de implementação, metodologia, resultados e discussão. A numeração dos capítulos, a revisão bibliográfica e as regras institucionais de apresentação devem ser harmonizadas com o texto completo do TCC. As referências R1–R10 abaixo identificam evidências do próprio projeto; não substituem referências bibliográficas sobre o tema. O conjunto final permanece selado, e futuras melhorias devem utilizar novos casos reservados.

<!-- page -->

## Fontes internas e mapa de evidências

Os caminhos abaixo são relativos à pasta etapa12. O índice COMECE_AQUI.html também fornece acesso navegável. As cópias possuem hashes e caminhos originais em evidencias/PROVENIENCIA.json.

| Código | Evidência incluída | Uso no texto |
|---|---|---|
| R1 | evidencias/etapa11/RELATORIO.md | Síntese, protocolo executado e limites |
| R2 | evidencias/etapa11/metricas_auditadas.json e recontagem_metricas.json | Métricas e denominadores |
| R3 | evidencias/protocolo_final.md e etapa11/manifesto.json | Protocolo prospectivo e ordem |
| R4 | evidencias/inputs/ e evidencias/views.json | Fontes, projeto e informação disponível |
| R5 | evidencias/etapa11/registros.json | Previsões e rastros originais |
| R6 | evidencias/etapa11/auditoria_semantica.json e auditoria_local_H.json | Suporte posterior por resposta e nó |
| R7 | evidencias/referencias.json e evidencias/revisao_cega/ | Gabaritos e derivação anterior à coleta |
| R8 | evidencias/etapa11/auditoria_uso.json e operacional.json | Consumo, reservas e latência |
| R9 | evidencias/etapa11/integridade_depois.json e selo_final.json | Integridade e congelamento |
| R10 | evidencias/etapa11/falhas_formato.json | Brutos rejeitados e diagnóstico |

As expressões “revisão cega” e “independente” referem-se à separação técnica entre autoria e revisão das referências por agentes, documentada na etapa 10. A auditoria de suporte das previsões finais não foi cega. Não há parecer humano emitido no momento desta entrega.

## Roteiro de demonstração associado

1. Abrir demonstracao/index.html e selecionar Duas atividades mais longas. Comparar a direção fornecida por B com os valores exatos de H e T.
2. Em Acompanhar H, selecionar Validar leitura conjunta. Conferir os fins D14 e D13 dos predecessores, o início D14 e o fim D19. Abrir as fontes citadas e consultar o apoio no livro de parcelas.
3. Selecionar Prazo conhecido e taxa desconhecida. Conferir o prazo +6 e o custo indeterminado de H. Abrir os brutos rejeitados de B/T e verificar a ausência de justificativa, sem alterar sua classificação.
4. Selecionar Crédito sem mudança de prazo. Conferir delta temporal zero e redução de R$ 116,00. No nó de alinhamento, conferir a parcela de 127.000 centavos.
5. Em Ver avaliação, explicar a diferença entre cobertura de custo 2/3 e acerto monetário 2/2 para H. Identificar os denominadores do MAE e o limite do conjunto experimental.

O observatório apresenta registros salvos. A navegação entre passos é didática e não reproduz o tempo de execução das chamadas nem gera novas previsões.
