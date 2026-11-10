# Pesquisa aprofundada: mudanças, grafos, custo/prazo e documentos

Consulta em 09/11/2026. Este relatório amplia o levantamento anterior com engenharia de requisitos, propagação de mudanças, digital thread, PLM e gestão de configuração. Não substitui nem altera o relatório anterior.

## Critério de integração e limite da pesquisa

Para esta comparação, **integração completa** exige evidência do mesmo sistema realizando: (A) interpretação de evento/mudança; (B) propagação por dependências; (C) cálculo ou previsão de custo e prazo; (D) localização de documentos/trechos desatualizados ou faltantes; (E) proposta/execução de revisão com controle de versões e proveniência; (F) avaliação conjunta dessa cadeia. **Parcial** significa cobertura demonstrada de parte desses itens. **Não verificada** significa que o material acessível não permite confirmar a cobertura. “Completa” é uma definição operacional desta pesquisa, não uma categoria criada pelos autores.

Não foi confirmada integração completa entre os candidatos abaixo. Isso significa ausência de confirmação neste levantamento, não inexistência universal. Algumas fontes estão acessíveis apenas como resumo ou prévia. Não foram executadas pesquisas internas autenticadas em Scopus/Web of Science nem exportado um corpus bibliográfico reproduzível dessas bases. A pesquisa usou busca web, consultas direcionadas e abertura de fontes editoriais/institucionais. Não se deve apresentá-la como revisão sistemática das principais bases.

## Resultados que mudam o posicionamento

Há um concorrente especialmente próximo da extensão documental: a dissertação de Filius, na TU Delft, identifica dependências entre documentos heterogêneos e regiões impactadas em mudanças reais da Shell. Há também um artigo recente, PTMR-ECM, especificamente sobre evidências de engenharia com versões e localização na fonte. Portanto, nem “documentos heterogêneos com grafo” nem “rastreabilidade entre versões com RAG” devem ser apresentados isoladamente como novidade. As respectivas fontes e limitações estão nas fichas 1 e 2.

A contribuição candidata mais estreita é **avaliar conjuntamente a seleção de revisão documental e a consistência dos impactos calculados em custo/prazo, a partir do mesmo evento**, em um domínio e conjunto de documentos delimitados. Essa formulação ainda precisa ser confrontada com o texto integral dos concorrentes mais próximos e validada por experimento.

## Doze candidatos classificados

### 1. Filius — dependências documentais e lacunas de adição

**B. L. Filius (2026). Inferring Cross-Document Dependencies in Heterogeneous Engineering Documentation: A Knowledge Graph Approach to Management of Change Impact Analysis.** Dissertação de mestrado, TU Delft; defesa registrada em 02/07/2026. Identificador persistente: uuid:a3bffbef-2a2a-477c-86f9-3103118ab1d3; DOI não identificado.

**Classificação: integração parcial, concorrente documental prioritário.** O resumo institucional descreve dependências latentes em Word/Excel, entidades, classificação de dependências, grafo e regiões documentais. Avalia 12 casos MoC da Shell, seis unidades e 467 locais de mudança obtidos por diferenças entre versões. Reporta recall documental macro 0,904, precisão 0,706 e F1 0,776; localização regional: recall 0,625, F1 0,507. A mitigação de lacunas de adição aumenta recall documental de 0,756 para 0,904. Esses números pertencem ao autor. O próprio resumo ressalva que alterações observadas podem subestimar dependências reais e que uma operadora não comprova generalização entre empresas.

Não se confirmou cálculo integrado de custo/prazo, redação automática de novos trechos ou código público. A página foi recuperada em busca dirigida ao repositório; abertura direta deu timeout, e o PDF não foi inspecionado. Não adotamos a alegação de inexistência de sistemas semelhantes feita pelo resumo. [Fonte institucional](https://repository.tudelft.nl/record/uuid%3Aa3bffbef-2a2a-477c-86f9-3103118ab1d3).

### 2. Yang e Li — engenharia multimodal, versões e evidências

**Lu Yang; Yuliang Li (2026). PTMR-ECM: Physical topology-constrained and temporal evolution-aware multimodal retrieval and question answering framework for engineering change management.** Advanced Engineering Informatics, 76, parte D, 105154. DOI: 10.1016/j.aei.2026.105154; fascículo novembro/2026; dia de publicação não confirmado.

**Classificação: integração parcial.** A prévia editorial descreve indexação conjunta de topologia física e versões, evidências atômicas com localização, conteúdo multimodal e o sistema IndusRQA. Avalia documentos de várias versões de um robô espacial com múltiplos braços, incluindo especificações, registros de mudança, PDFs e desenhos. Há ablações, mas não foi possível confirmar tabelas completas, número final de amostras ou métricas numéricas. Não foi confirmado código público.

O acesso direto retornou 403; resumo e trechos editoriais foram obtidos pela busca. Não há no material consultado comprovação de previsão de custo/prazo e escrita controlada da documentação. É precedente para impedir contaminação entre versões, preservar fórmulas como evidência e distinguir recuperação correta de texto apenas semanticamente semelhante. [Prévia da editora](https://www.sciencedirect.com/science/article/pii/S1474034626008463).

### 3. Arora et al. — NARCIA, antes dos LLMs

**Chetan Arora; Mehrdad Sabetzadeh; Arda Goknil; Lionel C. Briand; Frank Zimmer (2015). NARCIA: An Automated Tool for Change Impact Analysis in Natural Language Requirements.** ESEC/FSE 2015, p. 962–965. DOI: 10.1145/2786805.2803185.

**Classificação: integração parcial.** Analisa alterações em requisitos textuais, usa estrutura de frases e justificativa da mudança para ordenar candidatos impactados, sem exigir relações previamente especificadas. O texto do artigo disponibilizado no site dos anais foi recuperado por busca; abertura direta do PDF deu 401. O resumo confirma dois estudos industriais, mas não se reportam aqui números que não foram verificados no material primário consultado. Existe ferramenta descrita; disponibilidade atual do código não confirmada.

É baseline conceitual importante: a intenção da mudança distingue renomeação global de introdução de conceito novo. Não comprova revisão de documentos heterogêneos ou projeção financeira/temporal. [Artigo nos anais](https://cs.unibg.it/esecfse_proceedings/fse15/p962-arora.pdf).

### 4. Goknil et al. — propagação semântica e consistência

**Arda Goknil; Ivan Kurtev; Klaas van den Berg; Wietze Spijkerman (2014). Change impact analysis for requirements: A metamodeling approach.** Information and Software Technology, 56(8), 950–972. DOI: 10.1016/j.infsof.2014.03.002.

**Classificação: integração parcial.** Formaliza tipos de relação e de mudança para propagar propostas e detectar contradições; a ferramenta TRIC apoia a análise. O resumo institucional foi aberto e confirma exemplo ilustrativo, não benchmark industrial generalizável. A obtenção do PDF falhou; não se reportam métricas ou código público não confirmados. A exigência de relações explícitas é custo de preparação relevante. [Fonte institucional com resumo e referência](https://research.utwente.nl/en/publications/change-impact-analysis-for-requirements-a-metamodeling-approach/).

Complemento da mesma linha: **Goknil, Kurtev e van den Berg (2016), A Rule-Based Change Impact Analysis Approach in Software Architecture for Requirements Changes**, arXiv:1608.02757, amplia a propagação para arquitetura via rastros e apresenta exemplo industrial. Consultado resumo dos autores; não se presume status editorial além do registro. [Complemento primário](https://arxiv.org/abs/1608.02757).

Esses trabalhos mostram por que “alcançável no grafo” e “deve mudar” são decisões diferentes. Nenhum material consultado demonstra a cadeia completa definida neste relatório.

### 5. Ahmad, Wynn e Clarkson — requisitos, funções, componentes e retrabalho

**Naveed Ahmad; David C. Wynn; P. John Clarkson (2013; online 18/09/2012). Change impact on a product and its redesign process: a tool for knowledge capture and reuse.** Research in Engineering Design, 24, 219–244. DOI: 10.1007/s00163-012-0139-8.

**Classificação: integração parcial.** Integra domínios de requisitos, funções, componentes e processo de detalhamento, gerando listas dinâmicas para avaliar impactos. O resumo editorial aberto relata experimentos de laboratório com aspirador e produto eletrônico. Não foram confirmados tamanho amostral completo, métricas numéricas ou repositório de código. A ferramenta interativa existe como contribuição descrita, sem comprovação de distribuição atual.

É antecedente forte de avaliação multidomínio. O material acessível não comprova edição textual versionada nem cálculo conjunto de orçamento/cronograma. [Página primária](https://link.springer.com/article/10.1007/s00163-012-0139-8).

### 6. Wynn, Caldwell e Clarkson — recursos e risco de cronograma

**David C. Wynn; Nicholas H. M. Caldwell; P. John Clarkson (2014). Predicting change propagation in complex design workflows.** Journal of Mechanical Design, 136(8), 081009. DOI: 10.1115/1.4027495.

**Classificação: integração parcial.** Simula propagação em workflows considerando concorrência, múltiplas origens de mudança e iterações; prevê necessidades de recursos e risco de cronograma. O registro institucional descreve ilustrações com workflows da Airbus e Rolls-Royce. Foram consultados resumo indexado da TU Delft e página do grupo de Cambridge; o PDF ASME não abriu. Métricas detalhadas e código específico não confirmados. Não converter “necessidade de recursos” automaticamente em orçamento financeiro estimado.

Mostra que mudanças e previsão temporal já eram integradas antes de LLMs, sem evidência aqui de revisão textual de documentos. [Registro institucional](https://repository.tudelft.nl/record/uuid%3A3e457f57-8d13-431f-99a4-fd653c3b06e9); [grupo dos autores](https://camtoolkit.eng.cam.ac.uk/process-modelling/process-modelling-literature).

### 7. Li et al. — dinâmica multietapas de propagação

**Yuliang Li; Wei Zhao; Wenqi Zhang; Meng Chen (2022). A dynamic model for engineering change propagations in multiple product development stages.** AI EDAM, 36, e13; publicação online 16/02/2022. DOI: 10.1017/S089006042100041X. A página apresenta “Yulaing” no cabeçalho e “Yuliang” na correspondência; a grafia final deve ser conferida na exportação bibliográfica.

**Classificação: integração parcial.** Modela entidades suscetíveis/afetadas, duração para resolução e caminhos de propagação; combina equações diferenciais, simulação e seleção por algoritmo genético. O resumo aberto descreve resultados de simulação comparando propagação sequencial e concorrente. Não se confirmou corpus documental real, métricas quantitativas completas ou código público.

Útil para separar previsão dinâmica de mera enumeração de vizinhos. Não demonstra revisão documental nem recuperação de evidências textuais. [Resumo da editora](https://www.cambridge.org/core/product/identifier/S089006042100041X/type/journal_article).

### 8. Kwon et al. — digital thread, grafos e omissões

**Soonjo Kwon; Laetitia V. Monnier; Raphael Barbau; William Z. Bernstein (2020). Enriching standards-based digital thread by fusing as-designed and as-inspected data using knowledge graphs.** Advanced Engineering Informatics, 46, 101102. DOI: 10.1016/j.aei.2020.101102.

**Classificação: integração parcial.** O PDF integral hospedado pelo NIST foi aberto. Integra dados STEP/QIF em grafos e regras para comparar projeto e inspeção, detectar inconsistências e itens ausentes. Demonstração: conjunto de três componentes, com informações de inspeção. O artigo descreve ferramentas e regras; a nota do conjunto ampliado promete disponibilidade online, sem URL verificada nesta consulta. Não se deve declarar código/dados totalmente reproduzíveis sem checagem adicional.

A página NIST usa uma variante do título com “Ontologies”; para citação formal, preferir título e ordem de autores do PDF publicado. É precedente de identificação de lacunas entre representações estruturadas; não equivale a preencher prosa ausente em documentos após um evento, nem integra orçamento/cronograma. [PDF primário](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=929188).

### 9. NASA — gestão integrada como prática documentada

**NASA Software Engineering Handbook, versão C, SWE-053 — Manage Requirements Changes**, atualização de página registrada em 06/05/2022; complementar ao **NASA Systems Engineering Handbook, NASA/SP-2016-6105 Rev2**, seções 6.2 e 6.5.

**Classificação: integração parcial como fonte técnica; integração completa de software não aplicável/não verificada.** O manual vincula análise de mudanças a custos, cronograma, retrabalho documental, rastreabilidade, histórico de versões, atualização de planos e verificação dos produtos alterados. Trata-se de processo e orientação, não de sistema experimental com grafo/LLM. Métricas comparativas, dataset e código não se aplicam.

Isso sustenta a relevância prática de fechar o ciclo entre impacto e documentos. Também impede apresentar a conexão conceitual entre esses elementos como invenção do TCC. Não reutilizar estatísticas secundárias citadas no manual como evidência original sem consultar o estudo de origem. [SWE-053 aberto](https://swehb.nasa.gov/spaces/SWEHBVC/pages/50888907/SWE-053%2B-%2BManage%2BRequirements%2BChanges); [requisitos](https://www.nasa.gov/reference/6-2-requirements-management/); [configuração](https://www.nasa.gov/reference/6-5-configuration-management/).

### 10. DRILS — concorrente contemporâneo de impacto em requisitos

**Romina Etezadi; Ikram Darif; Lionel Briand; Ramesh S; Parkish Peranandam (2026). DRILS: Dependency-based Requirement Change Impact Analysis Using LLMs.** arXiv:2610.33920v1, 24/10/2026; DOI: 10.48550/arXiv.2610.33920.

**Classificação: integração parcial.** LLM, RAG e dependências; três conjuntos automotivos. O texto e limites foram examinados no levantamento anterior. Não demonstra integração completa de orçamento, cronograma e edição documental. Código não verificado. [Fonte primária](https://arxiv.org/html/2610.33920v1).

### 11. Seo e Choi — concorrente contemporâneo de cronograma

**Haram Seo; Minjoo Choi (2026). A large language model-based agent system for interactive large-scale project scheduling.** JCDE, 13(9), 183–203; DOI: 10.1093/jcde/qwag082; 14/09/2026.

**Classificação: integração parcial.** GraphRAG e ferramentas de cronograma; um estaleiro. O artigo informa restrições de disponibilização do código e dados industriais. Detalhes e métricas estão no levantamento anterior. Memória entre revisões é trabalho futuro, não funcionalidade validada. [Editora](https://academic.oup.com/jcde/article/13/9/183/8793612?searchresult=1).

### 12. Stark — livro de PLM como fundamentação

**John Stark (2022). Product Lifecycle Management (Volume 1): 21st Century Paradigm for Product Realisation.** 5ª edição, Springer, 616 páginas. DOI: 10.1007/978-3-030-98578-3.

**Classificação: integração completa não verificada; fonte conceitual.** A página editorial aberta confirma escopo de processos, dados de produto, PDM, PLM e relações com digital threads. Não foi lido o livro integral; não atribuir a ele algoritmo, avaliação ou funcionalidades específicas a partir da descrição comercial. Não se trata de benchmark com dataset/código. Serve para organizar o domínio e diferenciar gestão documental, configuração e ciclo de vida. [Página da editora](https://link.springer.com/book/10.1007/978-3-030-98578-3).

## Complemento BIM verificado

**Huda Dawood; Jonathan Siddle; Nashwan Dawood (2019). Integrating IFC and NLP for automating change request validations.** ITcon, 24, 540–552; dezembro/2019; DOI: 10.36680/j.itcon.2019.030.

**Integração parcial.** O PDF integral foi aberto: ArchiTrack compara versões IFC e valida solicitações em linguagem natural, gerando relatórios e visualizações de adições, modificações e exclusões. O artigo apresenta protótipo e caso de uso exploratório, não uma avaliação completa da cadeia de orçamento, cronograma e revisão de prosa. A automatização da implementação das mudanças é indicada como trabalho futuro. Código e dataset público específico não foram confirmados. [PDF primário](https://www.itcon.org/papers/2019_30-ITcon-Dawood.pdf).

**Contagem editorial para evitar dupla contagem:** as 12 fichas principais contêm dez trabalhos de pesquisa, um agrupamento de manuais NASA e um livro. A ficha 4 cita também um trabalho complementar de 2016, distinto do artigo de 2014; o complemento BIM acrescenta outro. São, portanto, **12 trabalhos de pesquisa únicos explicitamente descritos**, além do livro e do agrupamento de manuais. São 11 famílias se os dois trabalhos Goknil forem agrupados. Essas contagens descrevem apenas a seleção desta nota; não são tamanho de corpus sistemático nem total da área. Os trabalhos de DRILS e Seo/Choi também aparecem no levantamento anterior e devem ser deduplicados numa síntese conjunta.

## Implicações para avaliação e preenchimento de lacunas

“Lacuna” precisa ser operacionalizada. São tarefas distintas: vínculo ausente entre entidades; requisito pai sem cobertura; parâmetro ausente; documento que não existe; seção necessária ainda não escrita; fato desconhecido. Um sistema pode detectar a primeira sem saber resolver as demais. A classificação abaixo é uma recomendação metodológica, não resultado atribuído a uma fonte:

| Tarefa | Gabarito necessário | Resultado permitido |
|---|---|---|
| Detectar trecho desatualizado | Versão anterior, evento e anotação humana | Indicar trecho e motivo |
| Detectar informação ausente | Regra de completude/estrutura esperada | Indicar falta, sem inventar valor |
| Propor revisão | Evidência fonte e alteração aprovada | Minuta rastreável |
| Calcular prazo/custo | Dependências, taxas, calendário, regra de cálculo | Valor calculado com premissas |
| Estimar valor desconhecido | Modelo e dados históricos adequados | Estimativa com incerteza explícita |

Prioridade experimental: comparar sistema atual, recuperação vetorial e híbrido documental; congelar versões; medir separadamente recall de documentos, localização de trechos, qualidade da evidência, informações inventadas, erros de custo/prazo e tempo humano de validação. Casos de adição pura merecem estrato próprio: um método guiado apenas por entidades existentes pode não encontrar o que ainda precisa ser criado. A ressalva do gabarito baseado somente em diferenças é importante: “não foi alterado” não prova “não deveria ter sido alterado”.

## Log de consultas e acesso

Consultas executadas nesta rodada, com refinamentos por título, DOI e domínio:

1. `engineering change propagation knowledge graph documents cost schedule change management digital thread paper`
2. `requirements change impact analysis documents configuration management traceability change propagation 2015 Arora`
3. `engineering change management change propagation prediction cost time Clarkson Simons Eckert 2004`
4. `"digital thread" "engineering change" knowledge graph cost`
5. `"Predicting Change Propagation in Complex Design" doi 2004`
6. `"NARCIA" Arora 2015 requirements change impact`
7. `site:repository.tudelft.nl "Inferring Cross-Document" "precision"`
8. `site:sciencedirect.com/science/article/pii/S1474034626008463 "dataset"`
9. `site:asmedigitalcollection.asme.org "Predicting Change Propagation in Complex Design"`
10. `site:cambridge.org "Predicting change propagation in complex design workflows"`
11. `"PTMR-ECM" "105154" "accuracy"`
12. `"Predicting Change Propagation in Complex Design" site:eng.cam.ac.uk`
13. `"Enriching standards-based digital thread" site:nist.gov`
14. `"NARCIA" site:orbilu.uni.lu`
15. `"Change impact analysis for requirements: A metamodeling approach" authors`
16. `"NARCIA" "160" "72" site:orbilu.uni.lu`
17. `"Software Requirements" "Third Edition" "impact analysis" site:microsoftpressstore.com`
18. `"Product Lifecycle Management" "John Stark" "2022" site:link.springer.com/book`

Fontes alcançadas: Springer, Cambridge Core, Elsevier/ScienceDirect, Oxford Academic, anais ESEC/FSE, arXiv, repositórios TU Delft/Twente/Luxemburgo, Cambridge Engineering, NIST e NASA. Acesso a editoras e repositórios não equivale a varredura de todos os periódicos indexados por elas.

## Exclusões e pendências registradas

- **Blogs comerciais de Aras, TCS, Unity, kiLM e outros:** encontrados em digital thread/PLM; excluídos como comprovação científica de eficácia. Podem virar estudo separado de ferramentas comerciais.
- **Wikipedia, ResearchGate, agregadores e resumos automáticos:** usados no máximo como pistas; sem fundamentar conclusões técnicas quando houve fonte primária.
- **Clarkson, Simons e Eckert (2004), DOI 10.1115/1.1765117:** precedente histórico importante de probabilidade e impacto de propagação em helicópteros, confirmado no grupo dos autores; DOI/ASME não acessível nesta rodada. Mantido como leitura complementar, sem inventar métricas ou disponibilidade de software.
- **Revisão Concepts of change propagation analysis in engineering design, DOI 10.1007/s00163-022-00395-y:** encontrada para navegação de referências; não tratada como experimento primário da cadeia completa.
- **SSRN sobre framework conceitual de mudanças de escopo e sobre agentes de reforço:** não promovidos a candidatos centrais sem inspeção adicional; não confundir framework conceitual com eficácia validada.
- **OSLC engineering-change-impact-traceability-pattern:** tentativa de abrir wiki oficial falhou; cópia espelho não substituiu a verificação primária. Integração e requisitos específicos permanecem não verificados.
- **Livro Software Requirements, terceira edição:** consulta direcionada não produziu evidência primária suficiente nesta rodada; não foi incluído como livro lido.
- **Filius e PTMR-ECM:** obter os textos integrais é a principal pendência bibliográfica antes de sustentar originalidade documental. Ambos já reduzem substancialmente o espaço para alegações genéricas de novidade.

O resultado atual favorece um TCC de integração aplicada e avaliação controlada. Para alegar contribuição científica, é necessário explicitar qual comportamento adicional foi implementado, contra qual baseline, em quais cenários e com que benefício mensurado; adicionar LLM ou grafo a um fluxo conhecido não basta por si só.
