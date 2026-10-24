# Observatório 3D do Projeto Alfa

Na raiz do repositório, execute com Python 3.10+ (o ambiente local usa 3.12):

```sh
.venv/bin/python TCC_Codigos/scripts/serve_graph3d.py
```

Abra http://127.0.0.1:8765. Não requer dependências de frontend ou internet.
Selecione um dos 36 cenários e clique em **Executar ao vivo**. O modo inicial
injeta a interpretação de referência e executa o motor Python de verdade;
nenhum LLM é chamado. As relações percorridas são emitidas pelo BFS durante
sua execução, e não reconstruídas pela interface.

Arraste a rede para girar nos três eixos espaciais (rotação horizontal/vertical),
use a roda para zoom e clique em nós ou use a lista de entidades para inspecionar.
A renderização usa coordenadas 3D e projeção perspectiva em Canvas, sem CDN.
Rótulos sobrepostos são reduzidos; a lista mantém acesso a todas as entidades.

## Replay

Após executar, clique em Replay. Há pausa, próximo passo, velocidade e uma
linha do tempo que permite retroceder. O replay usa intervalos didáticos entre
eventos; o tempo real de cada evento aparece no painel. O motor normalmente
termina em milissegundos, portanto passos ao vivo podem chegar no mesmo quadro.
A partícula animada destaca a relação do passo selecionado; seu movimento é
ilustrativo e não representa duração computacional.

Registros são preservados por UUID em `TCC_Codigos/outputs/observatorio3d/`.
A lista de execuções permite reabri-los após reiniciar o servidor; o botão de
exportação baixa o JSON. Falhas também ficam registradas. Fechar a página não
cancela uma chamada de IA que já começou.

## IA real

Instale as dependências de `requirements-experiments.txt`, configure a chave
local conforme o README principal e inicie:

```sh
.venv/bin/python TCC_Codigos/scripts/serve_graph3d.py --allow-api
```

Selecione **IA real · chamada paga** antes de executar. Cada clique faz uma
chamada ao interpretador do notebook híbrido atual, reutilizando seu prompt,
modelo e validação por meio de `run_pilots.load_condition`. Não há repetição
automática da chamada. A interface mostra espera durante a API e depois sua
interpretação validada; não transmite tokens nem raciocínio interno do modelo.
O servidor só escuta em 127.0.0.1 e não serve a pasta do projeto.

## Escopo científico

Esta versão acompanha `HybridImpactPipeline` (BFS com profundidade 4) e os
cenários originais de `scenarios_ground_truth.json`. Nós são entidades; não são
agentes de IA separados. As entradas e saídas de cada nó são passos de
propagação e caminhos, não novas inferências de LLM. A lista de entidades
alcançadas não comprova magnitude de atraso ou custo. Protocolos V2/V2.2 e
novos casos hipotéticos possuem contratos próprios e ainda não estão integrados.
Os arquivos de casos existentes não são modificados por esta interface.

## Validação

`tests/test_observatorio3d.py` verifica paridade de resultados e telemetria nos
36 casos, incluindo ausência de propagação em eventos informativos, e o
adaptador de IA com resposta simulada. A suíte offline preexistente também
passou. Nenhuma chamada paga foi realizada durante a implementação.

## Reposicionar no plano da tela

Segure Command e arraste no trackpad (incluindo o arraste com três dedos quando
habilitado no macOS), ou use Command + rolagem horizontal/vertical. O grafo
se desloca sem mudar rotação ou zoom. Reenquadrar também zera esse deslocamento.
O navegador recebe arraste/rolagem e a tecla modificadora, não a contagem de
dedos; gestos capturados pelo macOS não chegam à página.

## Filtros

As categorias podem ser marcadas individualmente e combinadas. “Todas as
categorias” restaura as marcações. “Apenas envolvidos no processo” restringe
a rede às entidades da interpretação e às extremidades dos passos de propagação
já recebidos (ao vivo) ou alcançados no replay. Antes da interpretação, esse
filtro mostra uma rede vazia com aviso. As duas restrições se combinam.
Arestas só aparecem quando ambos os nós estão visíveis; posições, resultados
e registros permanecem iguais. A lista de inspeção acompanha os filtros.

## Formas por categoria

Fornecedor: hexágono; componente: quadrado; atividade: triângulo; marco:
losango; teste: pentágono; área: estrela; pessoa: círculo. As formas aparecem
na rede, nos filtros e na legenda, além das cores existentes. O destaque de
seleção e propagação acompanha o contorno de cada forma.
