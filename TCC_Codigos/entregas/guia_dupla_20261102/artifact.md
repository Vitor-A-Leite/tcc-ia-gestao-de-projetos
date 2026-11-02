# Contrato de autoria e fidelidade

## Referência retida

Arquivo: /Users/vaugusto/.codex/plugins/cache/openai-curated-remote/openai-templates/0.1.1/skills/artifact-template-system-design/assets/reference.docx

SHA-256: 13504f6c221a42c1726460a9e865e563355539ff97d702d6c9b2267b4b261d76

Sete páginas, uma seção. Todas as páginas foram renderizadas em qa/referencia e inspecionadas. Inventário completo de partes, tamanho, hash e classificação em qa/template_inventory.json. XML dos padrões em qa/template_patterns.json. A referência permanece imutável.

## Sistema visual

Papel Letter retrato 12240 × 15840 twips. Margens superior, esquerda e direita 1008; inferior 893; cabeçalho e rodapé 720. Uma seção, primeira página distinta, numeração inicial 1 sem campo visível de página. Cabeçalhos vazios; rodapé inicial vazio e rodapé normal centralizado. Sem campos TOC/REF/PAGE, controles de conteúdo, comentários ou formas opacas a preencher.

Capa: oito parágrafos vazios antes dos dois parágrafos Title, índices 8 e 9 do corpo. Primeiro Helvetica Neue Light 36 pt cinza azulado 5B7085; segundo Helvetica Neue 36 pt negrito azul 082A4A. Brancos posteriores e duas tabelas de metadados. Preservar estrutura e propriedades; substituir somente texto dos campos.

Corpo: padrão no índice 24, Helvetica Neue, cor 233447, justificado, entrelinha 300 twips relativa, depois 110. Copiar pPr/rPr originais. Heading1 no índice 23, 13,5 pt negrito 082A4A, depois 130, entrelinha 285, keepNext/keepLines. Subtítulo Heading3 no índice 38, negrito 5B7085. Listas no índice 44 preservam numId e recuo original; podem ser reutilizadas para sequências. O modelo específico selecionado prevalece sobre cores e bordas genéricas da skill Documents.

Tabelas: padrões nos índices 28 (duas colunas 5112/5112), 69 (três 3337/3722/3381), 86 (três 3303/3313/3824), 96 (três 2954/3713/3773), 40 (quatro 2268/3164/2374/2634) e 55 (quatro 2344/1921/1873/4302). Preservar grids, propriedades, bordas brancas, cabeçalho azul e texto branco, primeira coluna azul claro, demais linhas alternadas. Padding vertical 110 e horizontal 120 twips; alinhamento vertical central, cabeçalho repetido e linhas sem quebra interna. Usar somente para comparação ou registros tabulares. Clonar linhas existentes para expandir, removendo identificadores duplicados.

Figura do índice 35: inline, rId8, image1.png, extensão 6126480 × 3139821 EMU. Substituir o conteúdo ilustrativo por arquitetura real com a mesma proporção, mantendo ancoragem e moldura. Legenda no índice 36. Rodapé footer1 mantém tipografia e alinhamento, recebe identificação do guia. A nota de rodapé de ID interno 0, exibida como nota 1, recebe uma definição útil e sua âncora é mantida no primeiro bloco conceitual.

## Mapeamento e fluxo

O usuário solicita explicação completa para pessoa externa ao desenvolvimento; a estrutura de 12 seções do modelo será preenchida em português, ampliando o corpo por clones dos padrões existentes. Não haverá SLO, equipe fictícia, autenticação ou lançamento em produção inventado para preencher slots.

1. Abstract → visão geral e orientação de leitura.
2. Goals → objetivos e limites.
3. Background → trajetória das etapas 0 a 12.
4. Architecture → componentes e condições B/H/T.
5. Lifecycle → fluxo de um evento e exemplo numérico completo.
6. Contracts → entradas, saídas e conhecimento.
7. Consistency → método experimental, congelamento e reprodução.
8. Security → operação e orçamento real, além da proteção dos registros.
9. Readiness → resultados e interpretação.
10. Alternatives → escolhas de projeto e compromissos.
11. Questions → limitações e questões para orientação.
12. Next steps → roteiro de redação, demonstração e mapa de evidências.

Os títulos devem descrever o assunto. Cada seção aceita subtítulos, parágrafos, tabelas compactas e legendas clonados. Extensão esperada 18–25 páginas, subordinada à legibilidade. Fluxo natural; são permitidas quebras de página em títulos principais quando necessárias para evitar fragmentação. Não reduzir fonte para forçar uma contagem. Fontes longas ficam em parágrafos alinhados à esquerda, seguindo o alinhamento do padrão de legenda, para evitar espaços excessivos entre nomes de arquivos. Caminhos são relativos à pasta TCC_Codigos para facilitar transferência. R1–R12 vinculam afirmações a evidências locais. Manter junto o pequeno quadro de estados de conhecimento por keepNext nas linhas; quadros longos podem continuar com cabeçalhos repetidos. Os grids, estilos e medidas dos quadros permanecem os da referência.

## Partes editáveis e preservadas

Editáveis: word/document.xml (texto, repetição dos padrões, figura, nota e navegação); word/footer1.xml (texto); word/footnotes.xml (texto da nota 1); word/media/image1.png (diagrama real); word/_rels/document.xml.rels (destino do hyperlink de exemplo rId9, demais relações idênticas). Nenhuma parte adicional necessária.

Preserve-only: styles.xml, numbering.xml, settings.xml, fontTable.xml e suas relações, fontes incorporadas, theme1.xml, header1/2.xml, footer2.xml, Content_Types e relações de pacote. SectPr deverá permanecer estruturalmente idêntico. Nenhuma imagem do modelo é editada como imagem: image1 é um diagrama novo gerado de dados do sistema, substituindo o slot de conteúdo.

## Portas de qualidade

Antes da autoria conferir hash da referência. Clonar pacote, modificar exclusivamente partes permitidas, comparar hashes de cada parte preservada. Conferir seção, estilos, relações, tabela, footnote, imagem e ausência de placeholders. Renderizar referência e final com render_and_diff.py em pasta nova. Inspecionar todas as páginas finais, corrigir qualquer corte, sobreposição, tabela quebrada ou título isolado e renderizar novamente. Conferir valores e denominadores com relatórios originais. Não executar inferência, coleta ou scripts que alterem a carteira. Entregar somente DOCX.
