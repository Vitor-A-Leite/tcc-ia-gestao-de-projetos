# Fundamentos para integrar mudança documental, propagação, prazo e custo

Pesquisa web realizada em 9 de novembro de 2026. Recorte: engenharia de mudanças, DSM, desenvolvimento de produtos, rastreabilidade e gestão de configuração. Esta nota distingue livros/manuais de estudos empíricos e modelos avaliados; não constitui revisão sistemática exaustiva.

## Conclusão para o posicionamento do TCC

O elo entre dependências, mudanças, retrabalho, custo e prazo já possui antecedentes fortes. Portanto, não seria defensável apresentar a mera integração desses elementos como inédita. A contribuição potencial deve ser delimitada à operacionalização de uma cadeia verificável a partir de documentos de projeto: evidência textual/versionamento → vínculo validado → elemento afetado → atividade/orçamento → cenário de impacto. Essa é uma recomendação desta pesquisa, não uma conclusão experimental dos livros citados.

Para uma fundamentação enxuta, priorizar Eppinger e Browning (representação), NASA (rastreabilidade/configuração), Clarkson et al. (propagação) e Browning e Eppinger (custo/prazo). Usar Jarratt et al. como mapa do campo. Comparar o protótipo com métodos operacionais dos artigos, nunca com um manual como se fosse algoritmo concorrente.

## Nove referências verificadas e função no trabalho

### 1. Eppinger e Browning — livro de métodos DSM

EPPINGER, Steven D.; BROWNING, Tyson R. *Design Structure Matrix Methods and Applications*. Cambridge: MIT Press, 2012. ISBN 9780262017527. A editora confirma publicação em 25 maio 2012 e 352 páginas; a edição paperback é de 2016, não a origem do livro. A apresentação descreve representação de elementos e interações de sistemas complexos. [Página oficial MIT Press](https://mitpress.mit.edu/9780262017527/design-structure-matrix-methods-and-applications/).

**Uso:** fundamentar representação de dependências e justificar uma baseline matricial para o grafo. **Classe:** livro metodológico; não estudo experimental independente. **Limite:** página editorial consultada, sem leitura integral do livro; não atribuir fórmulas ou resultados a capítulos não inspecionados.

### 2. Clarkson, Simons e Eckert — método fundacional de propagação

CLARKSON, P. John; SIMONS, Caroline; ECKERT, Claudia. Predicting Change Propagation in Complex Design. *Journal of Mechanical Design*, v. 126, n. 5, p. 788–797, 2004. DOI [10.1115/1.1765117](https://doi.org/10.1115/1.1765117). A ficha de publicações do autor em Cambridge confirma título, ano, periódico e páginas no resultado indexado. [Cambridge](https://www-edc.eng.cam.ac.uk/people/john-clarkson).

**Uso:** antecedente central do Change Prediction Method e comparação conceitual entre alcance de dependências e previsão de propagação. **Classe:** artigo metodológico fundacional. **Limite:** abertura do DOI indisponível e página Cambridge retornou 403; leitura integral não realizada. A versão de conferência ASME de 2001 informa estudo em GKN Westland Helicopters, modelos de probabilidade/impacto e protótipo; não contar conferência e artigo como duas validações independentes. [Registro ASME da versão de 2001](https://doi.org/10.1115/detc2001/dtm-21698). Conferir detalhes do experimento e fórmulas no texto de 2004 antes de reproduzir o método.

### 3. Jarratt et al. — revisão do campo

JARRATT, T. A. W.; ECKERT, C. M.; CALDWELL, N. H. M.; CLARKSON, P. J. Engineering change: an overview and perspective on the literature. *Research in Engineering Design*, v. 22, p. 103–124, 2011. DOI [10.1007/s00163-010-0097-y](https://link.springer.com/article/10.1007/s00163-010-0097-y). Publicação online: 4 dezembro 2010; fascículo: abril 2011.

O resumo cobre alterações em partes, desenhos e software já liberados, incluindo interações entre elementos, métodos e aspectos organizacionais. **Uso:** definição de mudança de engenharia e taxonomia para buscar estudos adicionais. **Classe:** revisão, não experimento de um detector documental. **Acesso:** resumo, metadados e referências da editora; conteúdo completo sob assinatura. Não chamar de revisão sistemática sem confirmar protocolo no texto.

### 4. Browning e Eppinger — custo e prazo por rede de atividades

BROWNING, Tyson R.; EPPINGER, Steven D. Modeling Impacts of Process Architecture on Cost and Schedule Risk in Product Development. *IEEE Transactions on Engineering Management*, v. 49, n. 4, p. 428–442, novembro 2002. DOI 10.1109/TEM.2002.806709. [Texto disponibilizado pelo autor no MIT](https://stuff.mit.edu/people/eppinger/pdf/Browning_DSM_Sim_IEEE.pdf).

Modela atividades que trocam entregáveis, duração e custo incertos, curva de melhoria e retrabalho provocado por mudanças nas entradas. Simulação produz distribuições de custo e duração. Apresenta aplicação ao projeto preliminar de veículo aéreo de combate não tripulado. **Uso:** antecedente mais direto para o elo grafo de atividades → retrabalho → custo/prazo. **Classe:** modelagem/simulação com aplicação industrial, não ensaio controlado de IA. **Acesso:** PDF integral de 15 páginas aberto; resumo e formulação inicial consultados. **Limite:** não estimar benefício quantitativo ou generalização sem analisar resultados e parâmetros completos.

### 5. Wynn, Caldwell e Clarkson — propagação em workflows

WYNN, David C.; CALDWELL, Nicholas H. M.; CLARKSON, P. John. Predicting change propagation in complex design workflows. *Journal of Mechanical Design*, v. 136, n. 8, art. 081009, 2014. DOI [10.1115/1.4027495](https://doi.org/10.1115/1.4027495). [Registro TU Delft](https://repository.tudelft.nl/record/uuid%3A3e457f57-8d13-431f-99a4-fd653c3b06e9); [repositório Suffolk](https://oars.uos.ac.uk/132/).

O resumo descreve simulação de recursos e risco de cronograma considerando simultaneidade, múltiplas origens de mudança e iterações; ilustrações em workflows Airbus e Rolls-Royce. **Uso:** comparação com propagação além de componentes, incluindo atividades e calendário. **Classe:** modelo de simulação ilustrado em workflows industriais. **Limite:** metadados/resumo consultados; Suffolk declara não disponibilizar texto completo. Não afirmar validação preditiva retrospectiva apenas com base nas ilustrações.

### 6. Eckert, Clarkson e Zanker — evidência industrial de mudança

ECKERT, Claudia; CLARKSON, P. John; ZANKER, Winfried. Change and customisation in complex engineering domains. *Research in Engineering Design*, v. 15, p. 1–21, 2004. DOI [10.1007/s00163-003-0031-7](https://link.springer.com/article/10.1007/s00163-003-0031-7). Publicação online em 17 dezembro 2003; volume de 2004.

O resumo informa estudo de caso detalhado no setor aeroespacial e análise de processos formais e informais de mudança, incluindo propagação quando margens de tolerância são excedidas. **Uso:** motivar dependências técnicas e limites de assumir que toda ligação documental implica impacto efetivo. **Classe:** estudo de caso industrial. **Acesso:** resumo/metadados da editora, texto integral sob assinatura. Sem inspeção integral, não reportar tamanho da amostra ou supostos percentuais de melhoria.

### 7. NASA — handbook e rastreabilidade/configuração

NASA. *NASA Systems Engineering Handbook*. NASA SP-2016-6105 Rev2, 2016. [PDF oficial integral](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf). Não confundir a pasta web “2018/09” com ano do documento, identificado na folha inicial.

A seção [6.2 Requirements Management](https://www.nasa.gov/reference/6-2-requirements-management/) relaciona rastreabilidade bidirecional, documentos de projeto, testes e avaliação de mudanças em custo, prazo, arquitetura e interfaces. A seção [6.5 Configuration Management](https://www.nasa.gov/reference/6-5-configuration-management/) trata identificação, baselines, controle de mudanças e histórico de configuração.

**Uso:** definir entidades e relações, exigir versão/baseline e distinguir proposta, aprovação e implementação. **Classe:** manual técnico de práticas, não evidência de desempenho de uma ferramenta. **Acesso:** PDF e seções oficiais abertos. A adequação dessas práticas ao protótipo é uma decisão metodológica do TCC, não obrigação normativa automática.

### 8. INCOSE — manual de engenharia de sistemas

INCOSE (ed.). *INCOSE Systems Engineering Handbook*. 5. ed. Wiley, 2023. ISBN paperback 9781119814290; 368 páginas; edição impressa julho 2023 segundo a editora. [Wiley](https://www.wiley.com/en-us/INCOSE%2BSystems%2BEngineering%2BHandbook%2C%2B5th%2BEdition-p-9781119814290).

A descrição oficial aborda práticas e processos do ciclo de vida, alinhados a ISO/IEC/IEEE 15288:2023. **Uso:** enquadramento de engenharia de sistemas e gestão técnica. **Classe:** handbook profissional. **Limite:** metadados/descrição obtidos pelo resultado indexado oficial; tentativas de abertura Wiley retornaram 403. Não foi lido integralmente. O [portal INCOSE](https://portal.incose.org/ItemDetail?Category=EBOOKS&WebsiteKey=d4c31fa4-467a-4959-b48b-cae3ea93e516&iProductCode=SEHB5) informa acesso digital restrito a membros/CAB Associates e compra por não membros; não afirmar acesso livre.

### 9. PMI — controle integrado de mudanças, com acesso parcial identificado

PROJECT MANAGEMENT INSTITUTE. *A Guide to the Project Management Body of Knowledge (PMBOK Guide)*, 6. ed.; material oficial de errata da quinta impressão, páginas corrigidas da seção 4.6. [PDF oficial consultado](https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmbok-guide-6th-edition-5th-printing.pdf).

O arquivo é uma errata de sete páginas, não o livro completo. A página reproduzida 115 relaciona baselines de custo/prazo, base das estimativas, registro de mudanças e matriz de rastreabilidade como insumos da avaliação. **Uso:** justificar integração gerencial e proveniência das estimativas. **Classe:** referência de prática, não estudo experimental. **Limite:** citar precisamente material consultado; não apresentar a 6ª edição como edição mais recente nem inferir conteúdo de outras edições. Metadados completos do exemplar devem ser conferidos se o livro for incluído na bibliografia definitiva.

## Desenho recomendado da comparação — proposta desta pesquisa

| Camada | Baseline recomendada | Medida de avaliação |
|---|---|---|
| Extração de vínculos | Identificadores/referências explícitas; eventual similaridade textual | Precisão e revocação dos vínculos contra anotação humana |
| Propagação | Alcance transitivo em DSM/grafo validado | Precisão/revocação dos itens afetados; justificativa de cada caminho |
| Custo | Soma do retrabalho aplicável, com taxas e premissas rastreáveis | Erro absoluto frente a cenário de referência ou dados reais |
| Prazo | Recalcular precedências e caminho crítico | Diferença da data final; evitar somar atrasos paralelos |
| Valor gerencial | Processo manual apoiado em matriz e documentos | Tempo da análise, omissões e concordância entre avaliadores |

Essas métricas são sugestões para o TCC. Uma aresta de rastreabilidade não comprova causalidade de propagação. A soma de durações não equivale ao atraso do projeto quando há paralelismo e folga. Cenários sintéticos servem para verificar comportamento, mas não demonstram precisão preditiva industrial. Se não houver horas/custos reais de retrabalho, chamar a saída de estimativa por cenário e declarar hipóteses.

## Registro de busca e limites

Consultas executadas incluíram: “Clarkson Simons Eckert 2004 predicting change propagation complex design journal”; “Engineering change: an overview and perspective on the literature”; “Eppinger Browning Design Structure Matrix Methods Applications MIT Press 2012”; “site.nasa.gov systems engineering handbook configuration management requirements management 6.5”; “site.incose.org systems engineering handbook fifth edition 2023”; “integrated change control site.pmi.org cost schedule”; “Modeling impacts of process architecture on cost and schedule risk Browning Eppinger MIT”; e buscas por títulos exatos com restrição a ASME, Springer e Wiley.

Foram priorizados editoras, autores e repositórios institucionais. Resultados secundários serviram apenas para descobrir DOI/candidatos, sem substituir fontes primárias nas sínteses. O acesso variou entre PDF aberto, resumo editorial, registro institucional e resultado oficial indexado. Não houve aquisição de livros, acesso autenticado, levantamento sistemático de todas as bases ou reprodução dos modelos. Contagem desta nota: quatro artigos de método/caso, uma revisão e quatro livros/manuais/materiais de prática; não nove estudos experimentais equivalentes.
