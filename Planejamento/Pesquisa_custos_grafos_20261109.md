# Grafos, ontologias, custos, prazos e mudanças na construção

Pesquisa exploratória direcionada realizada em 09/11/2026. Não é revisão sistemática nem busca exaustiva. Foram priorizadas páginas de editoras, PDFs dos artigos e repositórios institucionais. Um resultado de busca indexado de uma editora é distinguido de leitura do texto integral. Campos não demonstrados não equivalem a ausência comprovada no artigo completo.

## Resultado principal

Há precedentes substanciais para BIM/ontologias e cálculo de custos, incluindo trabalhos anteriores a LLMs. Também há integração explícita de grafos, custos, cronogramas e recursos em Hagedorn et al. (2025) e no preprint de Cassandro et al. (2026). Portanto, não é defensável alegar que essa integração nunca foi feita. O recorte potencial para o TCC é mais específico: extração de evidências de documentos heterogêneos, atualização rastreável após revisões e propagação verificável de impactos em prazo e custo. Nesta amostra, as demonstrações dessas capacidades aparecem distribuídas entre trabalhos diferentes.

É necessário separar: (a) representar custos e prazos; (b) consultar inconsistências; (c) registrar impactos informados por humanos; (d) calcular impactos; (e) recalcular após uma revisão documental. São níveis de capacidade distintos.

## Matriz de capacidades verificadas

Legenda: S = explicitamente demonstrado/descrito; P = parcial ou proposta; ND = não demonstrado no material acessível. “Documento” significa processamento de texto documental, não simplesmente importar IFC/XML. “Revisão” significa tratar mudança de informação/projeto, não revisão bibliográfica.

| ID | Estudo | Grafo/ontologia | Custo | Prazo | Documento | Revisão | Lacuna principal frente ao recorte |
|---|---|---|---|---|---|---|---|
| 1 | Staub-French et al., 2003, feature ontology | S | S | ND | ND | P | Manutenção de estimativas, sem pipeline documental comprovado |
| 2 | Lee et al., 2014 | S | P | ND | ND | ND | Infere itens de revestimento; não integra o ciclo completo |
| 3 | Lawrence et al., 2014 | Mapeamentos; KG ND | S | ND | ND | S/P | Mudanças BIM→custo, sem prova acessível de KG/documentos |
| 4 | Niknam e Karshenas, 2015 | S | S | ND | ND | ND | Integra fontes estruturadas de orçamento |
| 5 | Xu et al., 2016 | S | S | ND | ND | P | Conhecimento de medição/orçamento; revisão automática não comprovada |
| 6 | Abanda et al., 2017 | S | S | ND | P | ND | Regras NRM formalizadas; uso de software 4D não prova integração de prazo |
| 7 | Rasmussen et al., 2019 | S | ND | ND | ND | S | Atualização de dependências demonstrada em cálculo térmico |
| 8 | Akanbi e Zhang, 2021 | S | S | ND | S | ND | Extração e matching para custos, sem replanejamento demonstrado |
| 9 | Hagedorn et al., 2025 | S | S | S | ND | P | Validação por consultas; equivalência de recursos ainda exige humanos |
| 10 | Torkanfar et al., 2025 | S | Registro | Registro | Referências | S | Registra impactos estimados pelos participantes; não os calcula |
| 11 | Zhang et al., 2025 | S | ND | ND | P/BCF | S | IFC+BCF e workflow; cálculo financeiro/temporal não verificado |
| 12 | Cassandro et al., 2026 | S | S | S | P | ND | Preprint; ligação semiautomática com validação de especialistas |

## Candidatos bibliográficos e evidências

### 1. A feature ontology to support construction cost estimating

**Sheryl Staub-French, Martin Fischer, John Kunz, Kos Ishii e Boyd Paulson (2003).** AI EDAM, 17(2), 133–154. [DOI 10.1017/S0890060403172034](https://doi.org/10.1017/S0890060403172034). [Fonte primária Cambridge](https://www.cambridge.org/core/journals/ai-edam/article/abs/feature-ontology-to-support-construction-cost-estimating/FD3CC0F4B78AFB4ABECBE4F789BE2169).

Formaliza características de modelos de produtos que afetam custos, incluindo interseções e similaridades. Um protótipo transforma modelos orientados ao projetista em modelos orientados ao orçamentista. O resumo relata testes de geração e manutenção de estimativas com melhorias qualitativas frente a modelos convencionais; não foram verificados tamanho da amostra ou percentuais. Precedente importante para conhecimento explícito sobre relações projeto→custo e manutenção das estimativas. Não comprova extração documental nem cronograma integrado. Acesso: resumo editorial indexado, não texto integral.

Artigo complementar da mesma linha, não contado como evidência independente: **Staub-French, Fischer, Kunz e Paulson (2003), An Ontology for Relating Features with Activities to Calculate Costs**, Journal of Computing in Civil Engineering, 17(4), 243–254. [DOI e ASCE](https://ascelibrary.org/doi/10.1061/%28ASCE%290887-3801%282003%2917%3A4%28243%29). Ontologia relaciona características, atividades, recursos e produtividade para calcular custos; resumo primário acessível pela busca.

### 2. BIM and ontology-based approach for building cost estimation

**Seul-Ki Lee, Ka-Ram Kim e Jung-Ho Yu (2014).** Automation in Construction, 41, 96–105. [DOI 10.1016/j.autcon.2013.10.020](https://doi.org/10.1016/j.autcon.2013.10.020). [Editora](https://www.sciencedirect.com/science/article/pii/S092658051300188X).

Usa ontologias de condições de trabalho e itens de serviço, com regras semânticas, para selecionar itens apropriados a partir de BIM. O fluxo descrito converte IFCXML em RDF e realiza inferência. Demonstração limitada a revestimento cerâmico. O resultado é seleção consistente de itens, não evidência de previsão de estouro orçamentário ou integração com cronograma. Os autores dizem que a ontologia precisa de revisão conforme mudam técnicas e tipos de obra; isso não equivale a atualização automática após uma revisão de documento. Acesso: resumo e trechos editoriais indexados.

### 3. Creating flexible mappings between Building Information Models and cost information

**Michael Lawrence, Rachel Pottinger, Sheryl Staub-French e Madhav Prasad Nepal (2014).** Automation in Construction, 45, 107–118. [DOI 10.1016/j.autcon.2014.05.006](https://doi.org/10.1016/j.autcon.2014.05.006). [Editora](https://www.sciencedirect.com/science/article/abs/pii/S0926580514001174).

Aborda mapeamentos BIM–custos e o problema de alterações de projeto afetarem quantidades, produtividade, métodos e itens associados. É candidato prioritário para a discussão de manutenção de vínculos e rastreabilidade de mudanças. O trecho editorial consultado estabelece claramente o problema e o domínio; não autoriza classificar a solução como knowledge graph nem registrar números de avaliação. Leitura integral pendente para confirmar implementação e testes de propagação. A página direta retornou 403; resumo indexado e registro na página de publicações da autora foram localizados.

### 4. Integrating distributed sources of information for construction cost estimating using Semantic Web and Semantic Web Service technologies

**Mehrdad Niknam e Saeed Karshenas (2015).** Automation in Construction, 57, 222–238. [DOI 10.1016/j.autcon.2015.04.003](https://doi.org/10.1016/j.autcon.2015.04.003). [Repositório Marquette](https://epublications.marquette.edu/civengin_fac/157/); [editora](https://www.sciencedirect.com/science/article/pii/S0926580515000813).

Integra BIM de projetistas, conhecimento de serviços/montagens dos empreiteiros e preços de fornecedores em OWL, SPARQL e serviços semânticos. Os trechos editoriais descrevem protótipo Java e armazenamento OpenRDF Sesame; a validação compara tempo de elaboração com WinEst, mas não foi verificado percentual. Os próprios autores limitam o objetivo à redução de tarefas repetitivas, sem automação integral. Barreiras incluem ontologias padrão ainda indisponíveis. Não é pipeline de documentos nem integração verificada com prazo. Acesso: página institucional aberta e trechos da editora; PDF integral não lido.

### 5. A framework for integrating syntax, semantics and pragmatics for computer-aided professional practice: With application of costing in construction industry

**Shen Xu, Kecheng Liu, Llewellyn C. M. Tang e Weizi Li (2016).** Computers in Industry, 83, 28–45. [DOI 10.1016/j.compind.2016.08.004](https://doi.org/10.1016/j.compind.2016.08.004). [HKU Scholars Hub](https://hub.hku.hk/handle/10722/265499).

Relaciona informações BIM a conhecimento profissional necessário à criação de itens de quantitativos/orçamento. O resumo descreve ontologia semântica e encadeamento para frente. A motivação reconhece o caráter dinâmico e colaborativo da preparação de BOQ. Esse reconhecimento não demonstra, por si, sincronização incremental ou propagação de mudanças. Não foram verificados corpus documental, cronograma integrado ou resultados numéricos. Acesso: metadados e resumo no repositório dos autores; o registro informa não haver arquivo associado.

### 6. BIM – New rules of measurement ontology for construction cost estimation

**F. H. Abanda, B. Kamsu-Foguem e J. H. M. Tah (2017).** Engineering Science and Technology, an International Journal, 20(2), 443–459. [DOI 10.1016/j.jestch.2017.01.007](https://doi.org/10.1016/j.jestch.2017.01.007). [Editora](https://www.sciencedirect.com/science/article/pii/S2215098616309156); [PDF institucional localizado](https://radar.brookes.ac.uk/radar/file/2751b858-0bd7-4684-8996-8c4e3f790834/1/abanda2017BIM_s.pdf).

Formaliza New Rules of Measurement para orçamento na licitação usando Methontology. Combina avaliação semântica por especialistas, reasoners e aplicação em edifício com software BIM 4D. É evidência de normas de medição tornadas processáveis por máquina. Não confundir software 4D usado na validação com integração demonstrada de cronograma, nem formalização de regras com extração NLP automática do documento normativo. Acesso: resumo primário indexado; abertura direta da editora e PDF institucional retornou 403.

### 7. Managing interrelated project information in AEC Knowledge Graphs

**Mads Holten Rasmussen, Maxime Lefrançois, Pieter Pauwels, Christian Anker Hviid e Jan Karlshøj (2019).** Automation in Construction, 108, 102956. [DOI 10.1016/j.autcon.2019.102956](https://doi.org/10.1016/j.autcon.2019.102956). [DTU](https://orbit.dtu.dk/en/publications/managing-interrelated-project-information-in-aec-knowledge-graphs/); [versão dos autores](https://www.maxime-lefrancois.info/docs/Holten-AUTCON2019-OPM.pdf).

Estende Ontology for Property Management para confiabilidade, valores mutáveis e dependências entre propriedades. OPM-QG gera SPARQL 1.1 para consultar/manipular o grafo e separa fatos explícitos de dados deduzidos. Demonstração em cálculo de perdas térmicas de ambientes de um edifício. É antecedente direto da arquitetura de atualização e proveniência, mas não evidência de cálculo de custos/prazos. A transposição para esses domínios é hipótese de implementação, não resultado deste artigo. Acesso: resumo institucional e trechos da editora, PDFs primários localizados.

### 8. Design information extraction from construction specifications to support cost estimation

**Temitope Akanbi e Jiansong Zhang (2021).** Automation in Construction, 131, 103835. [DOI 10.1016/j.autcon.2021.103835](https://doi.org/10.1016/j.autcon.2021.103835). [Editora](https://www.sciencedirect.com/science/article/pii/S0926580521002867); [Purdue Research Foundation](https://prf.flintbox.com/technologies/e0e497b0-e5f0-4b8e-9c4d-5705675bba46).

Propõe NLP semântico para extrair informação de especificações em formato AIA e associá-la a materiais de uma base, apoiando orçamento. A editora descreve teste em **oito projetos residenciais de madeira em Detroit**. A página da instituição reporta **99,2% de precisão na extração**, **100% no matching** e **tempo equivalente a 5,56% do método manual**; esses números foram verificados no texto indexado da fonte institucional, não em tabela do artigo. Não são acurácia monetária, economia financeira ou redução do prazo da obra. Sem evidência acessível de revisão incremental ou integração com cronograma. Acesso: trechos primários; página Purdue aberta exige JavaScript.

### 9. A Shared Construction Resource Ontology for Semantically Aligning Cost and Time Domains in Construction Projects

**Philipp Hagedorn, Jacopo Cassandro, Katharina Sigalov, Claudio Mirarchi, Alberto Pavan e Markus König (2025).** LDAC 2025, CEUR Workshop Proceedings, vol. 4113. [PDF integral](https://ceur-ws.org/Vol-4113/paper1.pdf). DOI não identificado no PDF consultado. [Ontologias e dados anunciados pelo artigo](https://cpm-ont-network.github.io/).

Integra DTC para tarefas, Cost Item, Construction Resource e ifcOWL. Dados de Microsoft Project/XML, custos e geometria se conectam por atribuições explícitas e parâmetros de utilização/quantidade. Avalia perguntas de competência por SPARQL; os resultados mostram tarefas, itens, objetos IFC e recursos compartilhados, incluindo inconsistência de representação de mão de obra. A conclusão afirma permitir refletir mudanças geométricas em custo/prazo; a avaliação consultada privilegia representação e consultas, não experimento longitudinal de recalculação após documentos revisados. Reconhece validação manual para recursos representados diferentemente e generalização entre contextos ainda pendente. Acesso: PDF integral aberto, especialmente pp. 5–12. Excelente antecedente direto; não é mera coincidência terminológica.

### 10. Decentralized and Collaborative Information Management System in Construction Contract Administration: A change management case study

**Navid Torkanfar, Ehsan Rezazadeh Azar e Brenda McCabe (2025).** ITcon, 30, 1123–1149. [DOI 10.36680/j.itcon.2025.046](https://doi.org/10.36680/j.itcon.2025.046). [PDF integral](https://www.itcon.org/papers/2025_46-ITcon-SI-Torkanfar.pdf).

Ontologia, workflow e Hyperledger Fabric apoiam gestão contratual de mudanças. A avaliação usa **três cenários simulados**, com **30 transações em 30 blocos**. Funções registram BOQ, estimativa, impacto de custo/prazo, revisões, negociação e change order. O documento BOQ é referenciado por URL. Atenção: EstimateCost **registra** valor estimado pelo contratante; EvaluateChange **registra** impactos, não demonstra algoritmo que os derive. É precedente forte de rastreabilidade e revisão com custo/prazo, mas não de extração automática do documento ou cálculo autônomo. Acesso: PDF integral, particularmente pp. 12–14.

### 11. Integration of BIM and ontologies for pumped storage hydropower design change management in EPC projects

**Shihang Zhang, Sherong Zhang, Han Liu, Xiaohua Wang, Zhiyong Zhao, Chao Wang e Lei Yan (2025).** Automation in Construction. [DOI 10.1016/j.autcon.2025.106189](https://doi.org/10.1016/j.autcon.2025.106189). [Editora](https://www.sciencedirect.com/science/article/abs/pii/S0926580525002298).

Integra ontologias de IFC e BIM Collaboration Format em Semantic Design Change Management System, com protótipo para empreiteiros EPC e estudo de caso em hidrelétrica reversível. Demonstra integração semântica voltada a mudanças, não apenas menção a BIM. O resumo relata eficiência e padronização, mas não fornece números verificáveis nem sustenta classificação como estimador de custos/prazos. BCF é informação estruturada sobre problemas/comunicação; não deve ser tratado automaticamente como análise de contratos e especificações em texto livre. Acesso: resumo e highlights primários indexados; abertura direta retornou 403.

### 12. A Knowledge Graph Framework for Consistency Checking across Cost, Scheduling, and Resource Domains in Construction Projects with LLM-Supported Semantic Linking

**Jacopo Cassandro, Philipp Hagedorn, Katharina Sigalov, Claudio Mirarchi, Alberto Pavan e Markus König (2026).** **Preprint SSRN**, publicado em 24/06/2026; status de artigo revisado por pares não confirmado. [DOI 10.2139/ssrn.6989042](https://doi.org/10.2139/ssrn.6989042). [Registro](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6989042).

Integra cronograma, custos, recursos e modelo construtivo em KG. Adiciona RAG/LLM para ligar semiautomaticamente tarefas e itens de custo, conservando validação especializada; consultas SPARQL verificam consistência entre domínios. É o candidato mais próximo do núcleo KG+custo+prazo+LLM. Não foi verificada ingestão de contratos/especificações heterogêneas nem propagação incremental após versões documentais. Nenhuma métrica de precisão foi extraída. Acesso: resumo oficial SSRN indexado, 74 páginas anunciadas; página/PDF retornaram 403 ao abrir. Deve ser lido integralmente antes de fechar alegação de lacuna.

## Interpretação para delimitar contribuição

Uma formulação prudente é: “Embora existam soluções ontológicas para orçamento BIM, extração de especificações, gestão de mudanças e integração custo–prazo–recursos, este trabalho investiga uma combinação delimitada dessas capacidades em um fluxo documental rastreável.” Não usar “primeiro sistema” ou “não há estudos integrados”.

Avaliação recomendada para distinguir a contribuição: conjunto pequeno de projetos com versões documentais controladas; vínculo evidência→entidade/relação→atividade/item; detecção de alterações; cálculo determinístico de impactos a partir de premissas explícitas; revisão humana de vínculos incertos; comparação com baseline sem grafo e com atualização manual. Essa recomendação é inferência de desenho de pesquisa, não resultado dos artigos.

## Log de consultas e limitações

Consultas executadas em buscador web nesta sessão (09/11/2026):

- `construction ontology cost estimation schedule change management knowledge graph`
- `"BIM" "ontology" "cost estimation"`
- `"knowledge graph" "change" "cost" construction schedule`
- `"Integrating distributed sources of information for construction cost estimating" authors`
- `"ontology" "change management" "Torkanfar" 2025`
- `"ontology" "construction" "cost" "change impact"`
- `"Design information extraction from construction specifications to support cost estimation" 103`
- `"BIM – New rules of measurement ontology" Abanda`
- `"ontology" "cost estimating" "Staub-French" 2003`
- `"cost" "change" "ontology" "Automation in Construction"`
- `"A feature ontology to support construction cost estimating" site:cambridge.org`
- `"ontology" "cost estimates" "changes" "Staub"`
- `"Integration of BIM and ontologies for pumped storage" DOI`
- `"An Ontology for Relating Features with Activities to Calculate Costs" doi`
- `"Creating flexible mappings" "mappings" "prototype"`
- `"Integrating distributed sources" "10.1016"`
- `"Managing interrelated project information in AEC Knowledge Graphs" Rasmussen`
- `"A Knowledge Graph Framework for Consistency Checking" 6989042`
- `"Creating flexible mappings between" site:cs.ubc.ca`
- `"An Ontology for Relating Features" site:ascelibrary.org`

Foram abertas fontes primárias, com leitura integral disponível para Hagedorn e Torkanfar. Várias páginas Elsevier/SSRN retornaram HTTP 403; seus resumos indexados foram usados com sinalização explícita. Resultados secundários serviram somente para localizar DOI/registro e foram substituídos por fontes primárias quando disponíveis. Não se consultaram diretamente índices pagos Scopus/Web of Science. Datas de coleta indexadas inconsistentes não foram usadas como datas bibliográficas. Não foram inventados números onde apenas melhorias qualitativas eram mencionadas.

Outros resultados localizados, fora do núcleo de 12: Lee et al. (2012), Automatic Inference of Standard BOQ Items using BIM and Ontology, DOI 10.6106/KJCEM.2012.13.3.099; Ma et al. (2016), Ontology-Based Representation and Reasoning in Building Construction Cost Estimation in China, DOI 10.3390/fi8030039; Herrera et al. (2026), Structuring Knowledge for AI-Driven Schedule Management in Digital Construction Twins, DOI 10.35490/EC3.2026.277. Demandam leitura específica antes de inclusão na argumentação final.
