# Literatura para impacto de mudanças e rastreabilidade documental

Data de consulta: 9 de novembro de 2026. Levantamento exploratório direcionado, com fontes primárias; não é revisão sistemática, não mede a frequência de abordagens na literatura e não comprova ausência de trabalhos concorrentes. Os resultados descritos pertencem aos experimentos dos autores, não ao TCC.

## Conclusão para o posicionamento

A combinação genérica de LLM, recuperação de contexto e grafos já aparece tanto na gestão de cronogramas quanto na análise de impacto em requisitos. Portanto, essa combinação isolada é uma justificativa técnica, mas não uma alegação segura de originalidade. O trabalho pode se diferenciar por uma pergunta avaliável: **quanto a inclusão de dependências documentais versionadas e evidências localizáveis melhora a identificação de trechos que precisam de revisão após uma mudança de projeto, preservando a consistência dos cálculos de prazo e custo?** Essa é uma proposta de recorte, ainda não uma lacuna comprovada. [Seo e Choi](https://doi.org/10.1093/jcde/qwag082); [DRILS](https://arxiv.org/abs/2610.33920v1).

## Oito trabalhos úteis

### 1. Seo e Choi — cronograma, ferramentas e GraphRAG (2026)

**A large language model-based agent system for interactive large-scale project scheduling.** Journal of Computational Design and Engineering, 13(9), 183–203. DOI: 10.1093/jcde/qwag082. A primeira abertura do endereço fornecido falhou por redirecionamento; o DOI, a página do fascículo e o conteúdo indexado da editora permitiram verificar título, autores e conteúdo.

O sistema usa um agente ReAct, GraphRAG e ferramentas de análise, modificação e otimização. Avalia um cronograma industrial naval, com 1.088 atividades e 2.653 relações, por perguntas de análise e atualização. Reporta aproximadamente 90% de acurácia e atribui parcela importante do ganho às ferramentas. Não é evidência de igual desempenho em outros domínios. Os autores apontam memória do grafo entre revisões, verificação intermediária e transferência de domínio como próximos passos. É o concorrente mais direto para o núcleo de cronograma do TCC; sugere avaliar a contribuição adicional da rastreabilidade temporal, sem atribuir todos os ganhos ao LLM. [Artigo da editora](https://academic.oup.com/jcde/article/13/9/183/8793612?searchresult=1).

### 2. Etezadi et al. — DRILS (2026, preprint)

**DRILS: Dependency-based Requirement Change Impact Analysis Using LLMs.** arXiv:2610.33920v1, submetido em 24/10/2026.

Combina arquitetura multiagente, RE-RAG e grafo de dependências de requisitos para prever conjuntos impactados. Reporta médias de 87,1% de recall, 76,3% de precisão e 81% de F1. A avaliação abrange três conjuntos automotivos; os autores reconhecem a necessidade de avaliação em outros domínios. A versão consultada é um preprint: não foi verificada publicação revisada por pares. É evidência direta contra alegar que LLM + grafo para impacto de mudanças em requisitos seja uma ideia inédita. Serve como referência para ablação e para medir o esforço de validação humana. Seu resultado não demonstra cálculo de impactos financeiros ou revisão coordenada de documentos de gestão. [Resumo e versão](https://arxiv.org/abs/2610.33920v1); [texto integral, especialmente seção 6](https://arxiv.org/html/2610.33920v1).

### 3. Etezadi et al. — ProReFiCIA (2025–2026, preprint)

**LLM-Driven Cost-Effective Requirements Change Impact Analysis.** arXiv:2511.00262, versão 6, revisada em 03/09/2026.

Prediz requisitos impactados e reduz o conjunto submetido à revisão humana. O resumo da versão atual informa 85,7% de recall em conjunto industrial não visto, com revisão de 3,0% dos requisitos; a inclusão de conhecimento de domínio por RAG eleva recall a 95,8%, com revisão de 3,4%. Esses valores não devem ser misturados com os resumos de versões anteriores. **“Cost” nesse trabalho é esforço de inspeção do conjunto de requisitos, não orçamento do projeto.** Essa distinção evita usar uma referência de custo operacional da análise como comprovação de previsão financeira. [Fonte primária, v6](https://arxiv.org/abs/2511.00262v6).

### 4. Ali, Naganathan e Bork — rastreabilidade com recuperação híbrida (2024)

**Establishing Traceability Between Natural Language Requirements and Software Artifacts by Combining RAG and LLMs.** ER 2024, p. 295–314. DOI: 10.1007/978-3-031-75872-0_16.

Relaciona requisitos em linguagem natural a classes de diagramas UML, comparando índices por palavras-chave, vetores, grafos e suas combinações. O repositório institucional identifica contribuição completa revisada por pares. Consultados metadados e resumo institucional, não todo o artigo; por isso não se extraem números experimentais ou detalhes adicionais de implementação. Mostra que recuperação híbrida e rastreabilidade entre artefatos já são um precedente relevante, embora o alvo sejam artefatos de software. [Registro e resumo da TU Wien](https://repositum.tuwien.at/handle/20.500.12708/205507).

### 5. Hippargi, Kamsties e Naumann — manutenção de rastreabilidade (2025)

**Evaluating the Capabilities of LLMs in Traceability Maintenance for Automotive System and Software Requirements.** NLP4RE, CEUR Workshop Proceedings, volume 3959.

Apresenta cinco estudos com ChatGPT-4o sobre rastreabilidade de requisitos de sistema e software, incluindo inconsistências e sugestões de revisão. Os próprios autores limitam as conclusões: conjunto pequeno, requisitos de baixa complexidade e restrições de confidencialidade; apresentam o modelo como apoio à análise preliminar com verificação humana. É útil para desenhar a revisão de trechos e a avaliação por especialistas. Não sustenta edição documental autônoma confiável. [Artigo completo](https://ceur-ws.org/Vol-3959/NLP4RE-short2.pdf).

### 6. Zhao e Xu — caminhos de evidência em GraphRAG (2026)

**A GraphRAG-Based Dual-Path Structural Diffusion Retrieval Framework for Requirement-Code Traceability Link Recovery.** Information, 17(6), 541. DOI: 10.3390/info17060541.

O DSDR constrói grafos heterogêneos de requisitos e código, combina alinhamento semântico com difusão estrutural e reconstrói caminhos para validação por LLM. Avalia cinco conjuntos; o equilíbrio entre precisão e recall varia por projeto. A lição para o TCC é separar recuperação de candidatos, evidência estrutural e decisão de impacto. Um caminho no grafo é evidência inspecionável, mas sua presença não prova, por si só, que um texto precisa ser alterado. A transferência de código para documentos de gestão exige nova avaliação. [Artigo completo](https://www.mdpi.com/2078-2489/17/6/541).

### 7. Nanduri e Delhi — documentos diários e cronograma (2026)

**Automated Schedule Enrichment from Daily Progress Reports: A Bi-Directional Neuro-Symbolic AI Approach.** EC³ 2026. DOI: 10.35490/EC3.2026.312.

Integra relatórios diários e cronograma com LLMs e grafos de conhecimento, verificando restrições temporais, de recursos, espaciais e causais. Avalia um projeto real, 173 relatórios e 1.000 atividades de validação; informa mediana de confiança de 0,825 e nenhuma violação das restrições consideradas. Confiança interna e ausência de violações não equivalem a acurácia completa de impactos. É precedente próximo para conectar documentos de execução ao cronograma, mas o problema declarado é enriquecimento do cronograma, não gestão de toda a revisão documental decorrente de solicitações de mudança. [Página oficial](https://ec-3.org/publication/ec32026_312/); [artigo completo](https://ec-3.org/wp-content/uploads/2026/08/EC32026_312.pdf).

### 8. Vogelsang et al. — qualidade textual como variável experimental (2025)

**On the Impact of Requirements Smells in Prompts: The Case of Automated Traceability.** ICSE-NIER 2025, conforme registro dos autores em arXiv:2501.04810.

Investiga dois LLMs e problemas de formulação de requisitos. Encontra efeito pequeno, mas significativo, na classificação da existência de vínculo requisito–código; não encontra efeito significativo na localização das linhas relacionadas. A conclusão é dependente da tarefa, não uma lei geral de que linguagem ambígua sempre piora qualquer resultado. Recomenda, para o experimento do TCC, estratificar textos claros, ambíguos, contraditórios e incompletos. Consultado o resumo primário, sem derivar detalhes adicionais do desenho. [Registro dos autores](https://arxiv.org/abs/2501.04810).

## Comparação com os dois recortes do TCC

| Recorte | Precedentes próximos | Diferenciação candidata a testar |
|---|---|---|
| Mudança → tarefas → prazo/custo | Seo e Choi para cronograma; ProReFiCIA e DRILS para seleção de impactos | Evidência de que a interpretação textual melhora a seleção das alterações que alimentam cálculos determinísticos, com erros e limites explicitados |
| Mudança → requisitos/trechos → documentos a revisar | DRILS; Ali et al.; Hippargi et al.; DSDR | Identificação de trechos e versões em documentos heterogêneos de gestão, mantendo proveniência e distinguindo revisar, verificar e apenas informar |
| Documentos → informação operacional | Nanduri e Delhi | Coerência entre revisão documental proposta e resultados numéricos de cronograma/orçamento |

As diferenças acima são inferências de projeto a partir das tarefas declaradas pelas fontes. Não constituem prova de que nenhum trabalho anterior já realizou a combinação proposta. Para sustentar uma lacuna mais forte, ainda seria necessário pesquisar explicitamente engenharia de mudanças, engenharia de sistemas, BIM, gestão de configuração e documentos de projeto, incluindo métodos anteriores aos LLMs.

## Desenho prático de avaliação proposto

Esta seção é recomendação metodológica para o TCC, não resultado dos artigos.

1. **Unidade de teste:** um pacote de projeto com documentos versionados, atividades e orçamento estruturados, mais uma solicitação de mudança. Registrar o estado anterior, a alteração solicitada, artefatos realmente impactados e o resultado esperado. Se os dados forem sintéticos, declarar isso e impedir que o mesmo gerador determine sozinho o gabarito.
2. **Gabarito humano:** dois avaliadores, quando viável, anotam independentemente documentos, trechos, tipos de vínculo e alterações numéricas esperadas; resolver divergências e registrar critérios. “Relacionado ao tema” não basta para rotular “precisa de revisão”.
3. **Comparadores:** busca lexical; recuperação vetorial; grafo com regras sem LLM; LLM com recuperação vetorial; sistema híbrido completo. Usar os mesmos documentos, pedidos, modelo e orçamento de contexto nas comparações pertinentes. Incluir a versão atual do sistema como baseline da extensão documental.
4. **Ablações essenciais:** retirar grafo; retirar versionamento; retirar evidências de trechos. Assim é possível saber se a melhoria decorre do recurso proposto ou apenas de mais contexto e chamadas ao modelo.
5. **Métricas separadas:** precisão/recall/F1 de documentos e trechos; recall dos impactos críticos; proporção de citações que realmente sustentam a indicação; referências a versões erradas; erros absolutos de prazo e custo contra cálculo de referência; latência e custo de execução. Não reunir tudo em uma única “acurácia”.
6. **Utilidade humana:** medir tempo de revisão e quantidade de correções necessárias, comparando análise manual com análise assistida. Se não houver estudo com usuários, chamar o resultado de desempenho técnico, sem alegar redução comprovada do esforço profissional.
7. **Casos difíceis:** mudança sem impacto; troca apenas de redação; mesmo termo com sentidos distintos; remoção de requisito; dependência indireta; documentos contraditórios; trecho movido; versão obsoleta; mudança em atividade com folga; alteração sem taxa de custo informada.
8. **Separação experimental:** ajustar prompts e limites em casos de desenvolvimento, congelar configurações e avaliar em pedidos e, quando possível, projetos separados. Repetir execuções para observar variabilidade; relatar resultados por cenário e incerteza, sem vender pequenas amostras como generalização industrial.

Um resultado de TCC defensável seria: “No conjunto avaliado, a integração de dependências documentais versionadas melhorou a recuperação de trechos impactados em relação à recuperação vetorial, com evidências verificáveis e cálculos determinísticos consistentes”. A direção e a magnitude desse resultado só podem ser escritas depois do experimento. Caso não haja ganho, identificar quando o grafo acrescenta custo ou falsos positivos também responde à pergunta de pesquisa.
