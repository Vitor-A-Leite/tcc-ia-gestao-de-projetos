# Explorador do grafo do Projeto Alfa

Abra `grafo_projeto.html` com duplo clique no Finder ou pelo navegador.
É um arquivo autossuficiente: funciona offline, sem servidor, instalação ou CDN.

## Uso

- Busque por nome, ID, tipo original ou tipo em português. A busca ignora acentos.
- Clique em um resultado ou nó para ver entradas e saídas, com os nomes e tipos originais. Clique em uma relação no painel para navegar até a outra entidade.
- As setas seguem **origem → destino**, exatamente como no JSON. Por exemplo, `Motor elétrico → é necessário para → Montagem do protótipo` corresponde a `required_for`.
- Escolha relações diretas, alcançáveis no sentido das setas ou entidades que alcançam o nó no sentido inverso. Os caminhos destacados percorrem todos os tipos de aresta: não são uma previsão de impacto do motor científico.
- Arraste os nós circulares para mudar a organização. Arraste o fundo para navegar; use a roda ou os botões para zoom. “Enquadrar tudo” restaura a visão geral, “Limpar seleção” remove o destaque e “Reorganizar rede” recalcula o layout inicial. As posições arrastadas duram até recarregar ou reorganizar.
- A legenda traduz os tipos. Nomes e IDs do JSON são preservados; assim, os dois nós chamados “Liberação de engenharia” continuam distinguíveis pelo ID e pelo tipo.
- Os quatro nós `Person` não têm relações na fonte. Nenhuma responsabilidade foi inferida.

## Regenerar

Com Python 3.10+ e sem pacotes adicionais, a partir da pasta `TCC_Codigos`:

```sh
python3 scripts/generate_graph_html.py
```

O script lê `data/project_graph.json`, valida IDs únicos e extremidades das arestas e incorpora o JSON completo em `visualizacao/grafo_projeto.html`. Não altera a fonte, o núcleo em `src/` ou resultados científicos. Os caminhos padrão são relativos ao próprio script, portanto ele também funciona chamado de outra pasta. Opções `--input` e `--output` permitem caminhos alternativos.

A aparência e as interações ficam em `grafo_template.html`; edite o template e regenere o arquivo final. O SHA-256 da fonte fica incorporado no HTML. A saída é determinística para a mesma fonte e o mesmo template.

## Escolha técnica e limites

A skill Graphify foi consultada, assim como o exportador instalado `graphify.export.to_html`. Esse exportador usa vis-network por CDN e uma interface de comunidades em inglês. Optou-se por um explorador SVG próprio, para abrir offline e apresentar os tipos e relações de domínio em português. Não houve extração AST, inferência de novas relações ou substituição do grafo por um mapa de código. Este HTML não é um export oficial do Graphify.

A rede usa nós circulares de tamanho uniforme, cores por tipo e rótulos em português. Um layout determinístico por forças aproxima entidades conectadas e reserva espaço para rótulos. As coordenadas são calculadas no navegador; não representam cronograma, peso ou importância. As setas terminam na borda do destino e acompanham o arraste individual dos nós. Todas as 65 relações aparecem na visão geral, com cruzamentos; selecionar um nó destaca o contexto e o painel permite ler cada relação. Não há edição de entidades ou cálculo de comunidades. A visualização é uma fotografia da fonte: regenere após alterar o JSON.

## Verificação realizada

- Fonte atual: 40 nós, 65 arestas direcionadas, 7 tipos de nós, 5 tipos de relações e 4 nós isolados.
- Cópia JSON incorporada comparada integralmente com a fonte; IDs únicos e extremidades das arestas verificados.
- Nenhum recurso externo de script ou estilo; sintaxe JavaScript verificada com `node --check`.
- Regeneração repetida com comparação byte a byte da saída e confirmação de que o hash da fonte não mudou.
- Execução do JavaScript em DOM simulado com Node: criação dos 40 nós/65 arestas, busca sem acentos, seleção direta, pessoa isolada e alcance nos dois sentidos passaram. Na versão de rede também passaram: 40 nós circulares sem cartões, coordenadas finitas e determinísticas, arraste atualizando arestas, zoom e reorganização. Esse teste não substitui inspeção visual em navegador.
- Inspeção visual não realizada: a ferramenta de navegador bloqueou o protocolo `file://`. A abertura no painel Codex foi solicitada, com retorno `queued`.
