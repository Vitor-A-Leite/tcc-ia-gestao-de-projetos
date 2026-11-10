# Frontend 3D da demonstração local

Atualização de 10/11/2026: a demonstração v2 usa o layout e o visualizador tridimensional da Alfa documental v1. O código visual foi incorporado em `web/`; não há importação ou leitura da pasta histórica durante a execução.

## Uso

- Arrastar gira a câmera; a rolagem sobre o grafo ajusta o zoom. Shift/⌘ + arrastar desloca a vista. Botões e teclado oferecem giro, zoom e reenquadramento.
- Clicar num nó abre seu painel de parâmetros, fontes, análise local e efeitos. A lista **Inspecionar entidade** permite alcançar qualquer nó, inclusive quando houver sobreposição.
- **Selecionar como entrada** inclui o nó inspecionado entre os pontos de partida. A seleção múltipla e os limites ficam em **Entradas e limites da análise**. Entidades de contexto e documentos podem ser inspecionados, mas não são pontos executáveis.
- Anéis azuis indicam entradas; verdes, a região prevista; ocres tracejados, pendências. Estar na região não significa já ter sido interpretado.
- **Vínculos documentais** e **Relações de contexto** mostram relações adicionais. **Ampliar painel** aumenta a área do grafo. A câmera é preservada durante a atualização da sessão.
- A reprodução percorre interpretações registradas. Os cartões continuam mostrando o resultado disponível, não um resultado recalculado para cada quadro.
- Ao pausar, escolha os pendentes e ajuste o limite total no painel **Continuação da análise**. Continuar e cancelar mantêm as regras e o consumo acumulado da v2.

## Integração

`graph3d.js` usa coordenadas XYZ, câmera orbital, projeção em perspectiva e desenho em Canvas. Não depende de CDN ou biblioteca externa. Distâncias e posições organizam a visualização; não representam diretamente prazo ou custo.

O endpoint local `/api/projeto` fornece o grafo e os documentos do cenário antes da execução, sem chamar intérprete e sem consultar gabaritos. O resultado da sessão acrescenta os estados seletivos, projeções auxiliares, rastro e recomendações necessários à inspeção. Contextos completos do transporte e cache não são enviados à interface. O grafo não é retransmitido em cada consulta da sessão.

A interface conserva a distinção entre referência inicial, projeção auxiliar condicional e resultado com completude informada. Uma execução parcial não apresenta prazo ou custo global como confirmado. Nenhum documento oficial é alterado.

## Verificação desta atualização

- Os 35 testes da v2 passaram após a integração.
- A sintaxe dos dois arquivos JavaScript foi validada com `node --check`.
- O estado visual inicial de D02 contém 49 entidades, e o de D07, 50; todas as relações apontam para entidades existentes.
- Em uma sessão temporária D02, limite 1 produziu resultado parcial; a continuação produziu prazo D45, custo de R$ 153.500,00 e três recomendações documentais.
- Um teste isolado do componente verificou coordenadas em profundidades diferentes, alteração da projeção ao girar e preservação da câmera ao atualizar o resultado.
- No Safari, foram conferidos o carregamento da sessão concluída existente, cartões, inspeção, zoom, rotação e desenho do grafo em 3D. A sessão do usuário foi preservada; não foi usada para testar uma nova execução.

As interpretações continuam simuladas. A mudança é de apresentação e exposição dos resultados existentes; não acrescenta avaliação com IA real nem muda o cálculo do motor.
