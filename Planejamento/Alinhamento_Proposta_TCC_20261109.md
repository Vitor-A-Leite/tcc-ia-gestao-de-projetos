# Alinhamento da proposta de TCC ao estudo realizado

Versão de 9 de novembro de 2026 para discussão com o orientador.

O trabalho desenvolvido sustenta uma avaliação exploratória de uma arquitetura híbrida para analisar impactos de eventos textuais em prazo e custo. Esta revisão delimita a pergunta e os objetivos a esse objeto, preservando a interpretação por LLM, as relações estruturadas, as regras determinísticas e a rastreabilidade como componentes centrais. A alteração de escopo é proposta para apreciação acadêmica; não representa aprovação do orientador.

## Registro da mudança de escopo

A proposta de referência é `Planejamento/Proposta_TCC_IA_Gestao_Projetos_3_meses.docx`, sobre análise de impacto e consistência documental. O documento da raiz sobre apoio ao desenvolvimento de produtos mecânicos constitui outra proposta e não é a base desta revisão.

A proposta de referência previa identificar inconsistências em Action Log, Risk Register, Decision Log e Status Report, recomendar atualizações e avaliar precision, recall, F1 e falsos alertas. O experimento final avalia impactos quantitativos em prazo e custo, validade das respostas, cobertura, sustentação nas fontes e tratamento de indeterminação. Essas medidas não substituem as métricas de detecção documental prometidas originalmente: correspondem a uma delimitação diferente do objeto de pesquisa.

A revisão é posterior à coleta de 28 de outubro de 2026. Ela deve ser apresentada como evolução do escopo durante o desenvolvimento. O protocolo efetivamente congelado antes do experimento continua sendo a referência metodológica da coleta. Os resultados, gabaritos, falhas e denominadores permanecem os registrados; a reformulação da proposta não constitui confirmação retrospectiva da hipótese original.

## Título proposto

Arquitetura híbrida com inteligência artificial generativa para análise rastreável de impactos em prazo e custo de projetos

## Introdução e delimitação

Eventos descritos em linguagem natural podem alterar durações de atividades, relações operacionais e obrigações de custo de um projeto. Para apoiar decisões, é necessário interpretar o evento, verificar quais informações estão disponíveis e calcular suas consequências sobre o estado do projeto. A ausência de uma taxa ou de uma relação necessária também deve ser reconhecida, pois uma resposta quantitativa sem sustentação pode produzir falsa precisão.

Este trabalho investiga uma arquitetura que combina interpretação textual por modelo de linguagem, representação estruturada das relações do projeto e regras determinísticas de cálculo. O LLM formula propostas locais; mecanismos de validação verificam sua admissibilidade; o motor calcula os efeitos das propostas aceitas. O sistema conserva vínculos entre fontes, operações e resultados para permitir sua inspeção.

A avaliação utiliza cenários sintéticos de um projeto de pequena escala. O domínio de desenvolvimento de produtos motiva a pesquisa, mas o experimento final não valida o uso em um processo completo de desenvolvimento de produto mecânico nem em uma organização real. O recorte abrange alterações de prazo e custo a partir de eventos textuais e informação contratual disponível.

## Problema e pergunta de pesquisa

O problema investigado é como produzir análises de impacto sustentadas pelas informações disponíveis, combinando interpretação semântica e cálculo estruturado, inclusive quando faltam dados para determinar uma magnitude.

Pergunta principal: em cenários sintéticos de um projeto de pequena escala, em que medida uma arquitetura híbrida que combina LLM, relações estruturadas e regras determinísticas produz estimativas corretas e rastreáveis de impactos em prazo e custo, preservando a indeterminação quando a informação é insuficiente?

Pergunta comparativa: quais diferenças de validade, cobertura, acerto, tratamento de indeterminação, latência e custo são observadas entre a arquitetura híbrida e duas condições globais baseadas em LLM, com diferentes formas de acesso às relações do projeto?

A comparação é entre sistemas completos. O desenho não identifica causalmente o efeito isolado da representação em grafo.

## Hipótese de trabalho e tratamento na redação

A expectativa investigativa é que a combinação de interpretação textual, relações explícitas e cálculo determinístico favoreça a produção de impactos sustentados pelas fontes e o reconhecimento de lacunas de informação.

Como esta formulação é posterior à coleta, deve ser descrita como expectativa teórica do recorte revisado, sem atribuir-lhe registro prospectivo. A hipótese original de superioridade na precisão e consistência documental deve ser apresentada no histórico da delimitação, acompanhada da explicação de que não foi testada integralmente.

A análise final é descritiva e exploratória. Resultados favoráveis nos casos observados oferecem evidência de viabilidade e não constituem confirmação estatística de superioridade geral.

## Objetivo geral

Desenvolver e avaliar, em cenários sintéticos, uma arquitetura híbrida que combine interpretação de eventos textuais por LLM, relações estruturadas e regras determinísticas para analisar impactos em prazo e custo de projetos, com rastreabilidade das fontes e tratamento explícito da informação insuficiente.

## Objetivos específicos

1. Definir uma representação mínima de atividades, precedências, restrições e obrigações de custo.
2. Implementar a interpretação de eventos textuais em propostas estruturadas, delimitadas pelo contexto e pelas permissões de cada nó.
3. Integrar validação, coordenação das propostas e cálculo determinístico dos impactos em prazo e custo.
4. Registrar vínculos entre fontes, propostas aceitas, operações e desfechos para inspeção da análise.
5. Comparar a arquitetura híbrida com condições globais baseadas em LLM, explicitando as diferenças de informação, processamento e contrato de saída.
6. Avaliar validade, cobertura exata, acerto, erro nos pares elegíveis, indeterminação, custo e latência.
7. Analisar falhas e ameaças à validade, delimitando as conclusões ao conjunto observado.

## Metodologia alinhada

A pesquisa compreende construção de protótipo e avaliação experimental exploratória em ambiente sintético. A redação deve distinguir a evolução do sistema durante o desenvolvimento da avaliação final com preditores e referências congelados.

O desenvolvimento utilizou 15 casos e diferentes revisões do sistema. Esses resultados documentam decisões de implementação e falhas encontradas. Não devem ser agregados ao conjunto final como se fossem observações inéditas de uma única versão fixa.

O experimento final utilizou três casos inéditos de um único projeto, com uma execução por condição, totalizando nove execuções. Os casos abrangem substituição de durações, alteração de duração com revogação de taxa e crédito em obrigação existente. Cada evento foi aplicado isoladamente ao mesmo estado de referência, D15 e R$ 5.204,00.

As condições comparadas foram:

- B, baseline global: recebe fatos comuns e o aviso, sem as arestas específicas do projeto; produz uma resposta global em uma chamada.
- H, arquitetura híbrida: utiliza relações estruturadas, contextos por nó, coordenação, schema local estrito e motor determinístico; realizou seis chamadas por caso.
- T, relações textuais: recebe fatos comuns e as relações serializadas em texto, produzindo uma resposta global em uma chamada.

B dispõe de menos informação relacional. H e T também diferem por decomposição, cálculo externo, quantidade de chamadas e contrato de saída. Essas diferenças devem acompanhar a interpretação das comparações.

As referências foram preparadas e revisadas tecnicamente por agentes antes das previsões. Preditores, entradas, views e referências foram congelados antes da coleta final. Não houve retry, reparo ou fallback. A auditoria posterior das respostas foi feita após a coleta e não equivale a revisão humana cega ou validação científica externa.

## Métricas e denominadores

| Medida | Definição de uso no TCC |
|---|---|
| Validade | Execuções aceitas pelo contrato de saída sobre as três execuções da condição |
| Cobertura exata | Respostas exatas válidas por dimensão sobre as três execuções |
| Acerto exato | Respostas exatas corretas sobre as referências exatas disponíveis, três temporais e duas monetárias |
| Erro absoluto médio | Erro apenas nos pares exatos válidos elegíveis, sempre acompanhado do número de pares |
| Indeterminação adequada | Reconhecimento válido da insuficiência de informação no caso monetário indeterminado |
| Sustentação e rastreabilidade | Inspeção dos vínculos com fontes e contextos efetivamente disponíveis, distinguindo validade estrutural e correção semântica |
| Custo e latência | Consumo observado e tempo por condição, separando inferência conhecida, provisões e reservas |

Respostas inválidas permanecem nos denominadores aplicáveis. Uma resposta incerta adequadamente sustentada não deve ser tratada como erro numérico. Erro médio igual a zero em poucos pares não representa acerto de todas as execuções.

Precision, recall e F1 para identificação de documentos afetados ficam fora da avaliação deste recorte. Sua inclusão exigiria tarefa documental definida, unidades de classificação e referências próprias.

## Resultados que sustentam o recorte

No experimento final, H apresentou três execuções válidas, acertou três de três referências temporais e duas de duas referências monetárias exatas, preservando a indeterminação no custo restante. Suas 18 análises locais foram válidas. Esses resultados demonstram funcionamento nos casos observados e permitem discutir cálculo, coordenação e incerteza com evidências inspecionáveis.

B e T tiveram uma resposta rejeitada cada por omissão do campo obrigatório de justificativa. Seus conteúdos brutos eram coerentes, mas não foram recuperados nas métricas. No caso de alteração das durações, a resposta direcional de B era compatível com a informação disponível. Portanto, as diferenças observadas não devem ser narradas como simples incapacidade de cálculo dos modelos globais.

H utilizou mais chamadas e apresentou maior custo de inferência conhecido que as condições globais. Sua mediana de latência foi 63,30 segundos, contra 55,80 em B e 23,48 em T. A discussão deve considerar esses custos juntamente com cobertura, validade e possibilidade de inspeção.

## Correspondência entre objetivos e evidências

| Objetivo | Evidência principal | Limite da conclusão |
|---|---|---|
| Representação do projeto | Estado, relações, fontes e views congelados na etapa 10 | Projeto sintético de pequena escala |
| Interpretação e integração | Preditor H 7.2 e rastros locais da etapa 11 | Validade estrutural não prova correção semântica |
| Rastreabilidade | Auditorias semântica e local de H | Inspeção técnica sem parecer humano emitido |
| Comparação | Nove registros finais de B, H e T | Uma execução por condição em cada caso |
| Métricas | Métricas auditadas, recontagem e dados operacionais | Denominadores pequenos e diferentes por medida |
| Análise crítica | Falhas de formato e limites registrados no relatório | Sem generalização ou efeito isolado do grafo |

## Contribuição e limites

A contribuição técnica é um protótipo que articula interpretação semântica, validação local, coordenação e cálculo de impactos com fontes rastreáveis. A contribuição empírica é uma comparação exploratória entre três condições, incluindo resultados parciais, rejeições de formato e informação monetária insuficiente.

O estudo não demonstra redução de esforço de gestores, melhoria de decisões em empresas, superioridade estatística, estabilidade entre repetições ou benefício causal exclusivo do grafo. Também não comprova manutenção automática da consistência dos quatro artefatos gerenciais previstos inicialmente. Esses pontos constituem extensões possíveis e não resultados alcançados.

## Texto sugerido para a conclusão

A arquitetura híbrida mostrou viabilidade técnica para analisar impactos em prazo e custo nos três cenários sintéticos avaliados. Ela produziu os três resultados temporais exatos e os dois resultados monetários determináveis, mantendo a indeterminação quando a taxa necessária não estava disponível. Os rastros de execução permitiram inspecionar as fontes e operações relacionadas aos desfechos. A comparação com as condições globais revelou diferenças de cobertura e validade, acompanhadas de maior consumo de inferência pela arquitetura híbrida. O número reduzido de casos, a ausência de repetições no conjunto final e as diferenças simultâneas entre os sistemas limitam as conclusões à evidência exploratória observada, sem demonstrar superioridade geral ou efeito isolado do grafo.

## Organização da redação e próximos passos

A introdução deve apresentar o problema de análise de impactos e a delimitação alcançada. A fundamentação deve cobrir análise de impacto de mudanças, precedências e cálculo de prazo, regras de custo, LLMs, rastreabilidade e tratamento de informação insuficiente, com literatura efetivamente consultada. Este alinhamento não substitui a revisão bibliográfica.

A metodologia deve descrever o histórico de mudança de escopo, o desenvolvimento e o protocolo final. O capítulo de arquitetura deve explicar os componentes e um exemplo completo de processamento. Resultados e discussão devem apresentar os nove desfechos, seus denominadores, as falhas e os custos. A conclusão deve responder à pergunta revisada dentro dos limites observados.

Para consolidar o TCC, restam a apreciação do recorte pelo orientador, a revisão humana das referências e interpretações, a integração da fundamentação bibliográfica e a redação conforme as normas da instituição. A revisão humana futura deve ser datada e distinguida das revisões técnicas já realizadas. Se o orientador exigir o escopo documental original, será necessário complementar a avaliação com os quatro artefatos e suas métricas específicas.

## Fontes internas para conferência

- Proposta original: `Planejamento/Proposta_TCC_IA_Gestao_Projetos_3_meses.docx`.
- Relatório final: `TCC_Codigos/outputs/etapa11_final_20261028/RELATORIO.md`.
- Critérios da coleta final: `TCC_Codigos/docs/desenvolvimento/ETAPA_11_CRITERIO_CONCLUSAO.md`.
- Material de redação: `TCC_Codigos/entregas/etapa12/material_tcc/Texto_e_tabelas.md`.
- Estado e histórico do projeto: `TCC_Codigos/docs/desenvolvimento/STATUS.md`.

Os nomes e caminhos identificam as evidências locais; na versão acadêmica, devem ser convertidos em referências a seções, quadros, apêndices e ao repositório disponibilizado conforme as regras da instituição.
