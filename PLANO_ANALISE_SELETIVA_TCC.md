# Plano de implementação — análise híbrida com seleção de nós de entrada

Data: 10/11/2026. **Status: primeiro incremento implementado e validado offline em `TCC_Codigos/etapas/alfa_documental_v2/`.** A coleta com IA real e a demonstração de economia de API continuam pendentes. Ver [instruções da versão](TCC_Codigos/etapas/alfa_documental_v2/README.md) e [revisão do orquestrador](TCC_Codigos/etapas/alfa_documental_v2/docs/REVISAO_ORQUESTRADOR.md). As seções abaixo preservam o plano que orientou a implementação; descrições de “estado atual” e “estrutura proposta” referem-se ao momento do planejamento.

## Objetivo e decisão de arquitetura

Permitir que o engenheiro escolha um ou mais pontos de entrada no grafo, ou confirme uma sugestão da IA. Manter a interpretação local por IA nos nós selecionados e nos alcançados pela análise, reduzindo consultas a partes não pertinentes do projeto. Calcular os impactos com o motor existente e conservar as recomendações documentais.

A seleção dos pontos de entrada não deve exigir que o usuário enumere todas as consequências. O programa deriva a região de análise das dependências cadastradas, regras e responsabilidades. O grafo completo continua disponível ao cálculo: economizar chamadas à IA não significa cortar predecessores, obrigações ou caminhos matemáticos.

Critério principal: economia medida de custo e tempo com qualidade preservada nos casos avaliados. Não prometer redução para toda mudança; eventos abrangentes podem exigir a rede inteira.

## 1. Estado atual verificado

- `src/hibrido_v07_r3` preserva a versão histórica, cuja política aceita até oito nós.
- `etapas/alfa_documental_v1` reutiliza contratos e motor, acrescenta projeção do Alfa, política para 32 pontos executáveis, comparação de campos preparados do Status Report e demonstração própria.
- A política Alfa consulta todos os 32 pontos. Já reduz o catálogo de responsabilidades enviado em cada contexto, mas não reduz o número de análises.
- O fechamento atual exige cobertura de todos os nós do plano. Alterar apenas a lista de nós ou o limite de chamadas produziria resultados parciais ou poderia mascarar uma omissão.
- A integração Alfa foi testada com interpretações manuais simuladas. Os nove casos de desenvolvimento têm resultados salvos; os oito finais não foram executados. Não confundir redução de análises simuladas com economia observada de API.
- O verificador documental trata cinco afirmações estruturadas do Status Report; os outros três artefatos recebem triagem. Essa limitação continua explícita na nova etapa.

## 2. Preservação e organização

Criar uma versão completa em **`TCC_Codigos/etapas/alfa_documental_v2/`**, substituindo no plano o nome inicialmente proposto `alfa_seletivo_v1`. O objetivo de organização confirmado pelo usuário é identificar facilmente onde estão o motor, o sistema e os dados da versão mais recente, sem precisar reunir arquivos de etapas antigas.

Não alterar código, inputs selados, resultados, carteira ou demonstração de `alfa_documental_v1`, Sálvia e versões históricas. Incorporar na v2 cópias identificadas dos componentes próprios necessários, com suas dependências internas, registrando origem, versão e hash. As importações entre componentes de execução e os caminhos dos dados devem resolver dentro da v2; não depender de `src/` histórico, de `alfa_documental_v1` ou de links simbólicos para pastas anteriores. Bibliotecas externas e a versão do Python continuam declaradas como dependências do ambiente, sem copiá-las integralmente para o repositório.

Fazer primeiro uma migração estrutural com equivalência verificada e só depois implementar seleção, nova agenda e fechamento. Essa separação evita confundir erros de empacotamento com mudanças de comportamento. Copiar somente a dependência necessária, sem levar todas as rodadas históricas, credenciais ou ambientes virtuais.

Antes e depois, conferir hashes dos arquivos preservados. A versão atual continua disponível como comparador e forma de voltar ao comportamento anterior. O novo modo só é executado por comando/interface próprios; nenhum cenário antigo passa a usar seleção implicitamente.

Criar um índice simples **`TCC_Codigos/VERSAO_ATUAL.md`**, indicando versão em desenvolvimento, última versão validada, natureza da validação (simulada ou IA real), caminhos e comando de inicialização. Enquanto a v2 estiver em desenvolvimento, manter a v1 como última versão validada offline; após os critérios de aceite, atualizar o índice. Não chamar código incompleto de versão pronta apenas por ser mais novo. Não mover ou renomear pastas históricas nesta implementação.

Estrutura de entrega proposta:

```text
TCC_Codigos/
  VERSAO_ATUAL.md
  etapas/
    alfa_documental_v1/           # histórico preservado
    alfa_documental_v2/
      README.md                  # como executar e limitações
      __main__.py                # entrada única da versão
      pyproject.toml             # versão e dependências do ambiente
      MANIFESTO_ORIGENS.json      # proveniência dos componentes incorporados
      src/                       # motor, IA, seleção e análise documental
      data/projetos/alfa/         # grafo, documentos, parâmetros e eventos
      avaliacao/                 # referências/protocolos, fora da entrada do motor
      web/                       # interface da v2
      tests/                     # testes da versão
      outputs/                   # resultados próprios, sem sobrescrita histórica
      docs/                      # arquitetura e relatórios
```

O código lê os dados versionados de dentro da v2; a identidade/versão do projeto continua separada da versão do software. Referências experimentais não podem entrar no contexto da IA. Não abrir os casos finais reservados para ajustar migração ou seleção. Registros de consumo da v2 devem preservar a continuidade do orçamento acumulado: a pasta nova não zera saldo, elimina reservas ou autoriza novas despesas. Se houver coleta paga, definir a reconciliação antes da ativação, sem usar uma carteira local nova como substituição do histórico financeiro.

Estrutura proposta, ainda não criada:

| Arquivo | Responsabilidade |
|---|---|
| `selecao.py` | Validar seleção manual, catálogo resumido e resposta opcional de sugestão. |
| `alcance.py` | Construir região de interpretação e registrar motivos de inclusão/exclusão. |
| `politica.py` | Definir permissões, responsabilidades, fontes e limites da nova execução. |
| `orquestracao.py` | Executar análise local na região selecionada, controlando versões e encaminhamentos. |
| `fechamento.py` | Verificar cobertura seletiva e completude por prazo/custo. |
| `pipeline.py` | Integrar entradas, cálculo completo, rastros e verificação documental. |
| `avaliacao.py` | Comparar cobertura, resultados, recomendações e consumo. |
| `testes.py`, `web/`, `README.md` | Testes, demonstração separada e instruções. |

Reutilizar o comportamento do adaptador e do esquema de resposta local por cópias internas verificadas, sempre que compatíveis. O contrato de sugestão de entradas é separado do contrato de interpretação local. Não modificar o parser histórico nem tornar o parser novo permissivo para esconder falhas.

## 3. Escolha dos pontos de entrada

### Modo manual — padrão

O engenheiro seleciona um ou mais nós por clique, busca ou lista. Mostrar nome, tipo, descrição e ID. Não gastar chamadas de IA para interpretar uma escolha já explícita.

Validar IDs, versão do projeto, duplicações e tipo de nó. No primeiro incremento, selecionar pontos executáveis. Selecionar um documento pode destacar entidades vinculadas, mas requer escolher/confirmar os pontos executáveis correspondentes; não transformar documento ou área em atividade temporal.

Comparar a escolha com as entidades explicitamente mencionadas no evento. Uma divergência deve aparecer antes da execução. Não apagar menções do evento para fazer a seleção parecer completa.

### Modo assistido — opcional

Um botão solicita sugestão da IA. Fornecer evento e catálogo compacto: ID, nome, tipo, descrição curta e aliases existentes. Não enviar todos os documentos, cronograma detalhado ou todo o contexto de cada nó para essa escolha.

A resposta deve apontar IDs existentes, justificativas ligadas ao evento e ambiguidades. Permitir vários nós e nenhum nó identificado. A sugestão é revisável pelo engenheiro; não representa aprovação do impacto nem prova de que o escopo está completo.

No Alfa, começar com o catálogo compacto completo, desde que caiba no limite medido de entrada. Para catálogos maiores, usar busca local por nomes/aliases e filtro por projeto; se a seleção de candidatos for incerta, solicitar refinamento em vez de eliminar silenciosamente opções. Evitar adicionar embeddings pagos ou outro serviço nesta versão.

Limitar a **uma chamada de sugestão por pedido explícito**, incluída no orçamento total. Guardar a sugestão com vínculo ao evento e à versão do catálogo para evitar chamadas repetidas na mesma interação. Sem votação entre agentes, tentativas automáticas sucessivas ou consultas por nó para escolher o nó.

### Registro de seleção

Adicionar metadados próprios, preservando o evento original. Exemplo ilustrativo, não contrato executável:

```json
{
  "modo": "manual",
  "nos_entrada": ["SUP_MOTOR"],
  "limite_nos_analise": 10,
  "escopo": "impacto_do_evento",
  "projeto_versao": "versao_identificada",
  "origem_selecao": "engenheiro"
}
```

Separar dois usos: **análise do evento**, que precisa cobrir todas as alterações identificadas, e **teste delimitado**, no qual o engenheiro escolhe uma hipótese/parte do projeto. Um teste delimitado não pode ser apresentado como certificação de ausência de impactos fora desse escopo.

### Limite de nós escolhido pelo usuário

Requisito confirmado pelo usuário: além dos pontos de entrada, o engenheiro **digita livremente a quantidade máxima de nós** que a análise pode alcançar. Não oferecer uma lista fechada com valores como 8 ou 10: esses números são apenas exemplos. Mostrar junto ao campo o máximo possível, calculado a partir dos nós elegíveis da versão do projeto. Trata-se de teto, não de meta nem de lista obrigatória de nós.

- `limite_nos_analise` aceita qualquer inteiro de **1 até N**, sendo N o total de nós executáveis elegíveis na versão carregada, ou `"todos"` como atalho opcional. Contar nós distintos submetidos à interpretação local, incluindo os pontos de entrada; isso deve estar explícito na interface.
- Exibir “Máximo disponível para análise: N nós”, calculado em tempo de execução, sem fixar oito, dez ou 32 no código. Exibir separadamente o total de nós do grafo quando houver documentos, pessoas e áreas que não executam análise local, evitando confundir o total visualizado com o máximo analisável. No Alfa, os 32 atuais são um dado da projeção, não uma constante universal.
- Rejeitar vazio, zero, negativos, frações e valores acima de N com mensagem clara; não arredondar nem reduzir silenciosamente. Se o usuário já selecionou K entradas, o limite também precisa ser pelo menos K. Ao mudar projeto/versão, recalcular e revalidar N. A região potencialmente afetada pode ser menor que N; informar essa estimativa separadamente, sem transformá-la no máximo estrutural.
- A opção `"todos"` permite chegar a todos os pontos executáveis da versão do projeto, mas a seleção continua evitando regiões sem pertinência. Não obriga uma varredura completa. No Alfa atual, são 32 pontos executáveis, não todos os nós documentais/contextuais da visualização.
- Reanalisar um nó já contado não aumenta a quantidade de nós distintos, mas consome chamadas, tokens, tempo e orçamento. Limite de nós e limite de chamadas são controles separados.
- Se houver mais pontos de entrada do que o limite, rejeitar a configuração antes da execução; não descartar escolhas silenciosamente.
- Se forem necessários mais nós do que o teto escolhido, listar os pendentes e o motivo da expansão. A execução para com cobertura parcial e permite ao usuário decidir sobre um novo limite; não apresentar falta de análise como ausência de impacto.
- Se apenas quatro nós forem pertinentes e o limite for dez, analisar quatro. Não visitar outros seis para completar a quantidade.
- O limite controla o alcance da interpretação por IA. O cálculo determinístico pode usar o grafo completo para conservar predecessores e convergências; resultados condicionais não substituem a interpretação que ficou pendente.
- A ordenação da fila deve ser determinística e registrada, respeitando dependências e obrigações, para que a escolha dos primeiros nós não dependa de uma ordem acidental.

### Decisão sobre os nós pendentes: prosseguir ou cancelar

Ao atingir o limite, pausar o agendamento de novas chamadas e apresentar os nós pendentes, os motivos, as dependências necessárias, os resultados parciais e o consumo acumulado. O engenheiro pode selecionar os nós pendentes que deseja analisar e escolher:

- **Prosseguir com selecionados:** mostrar os predecessores/obrigações adicionais necessários e uma estimativa do consumo incremental. Registrar o novo limite total de nós e eventuais ajustes de orçamento aprovados; a seleção não autoriza ultrapassar limites silenciosamente. Retomar do ponto salvo, reaproveitando análises ainda válidas e executando somente trabalho novo ou invalidado. Dependências não selecionadas que sejam indispensáveis permanecem bloqueios explícitos até serem incluídas ou o escopo ser revisto.
- **Cancelar análise:** encerrar o agendamento sem novas chamadas, preservando resultados, recomendações, custos já incorridos e lista de pendências. Marcar a execução como cancelada com resultado parcial, sem publicar conclusão global completa e sem aplicar mudanças ao projeto/documentos oficiais.

Não retomar automaticamente por tempo decorrido ou ao recarregar a página. Persistir o ponto de retomada com versão do projeto, evento, contextos, resultados, fila, limites e consumo. Cliques repetidos em prosseguir não podem iniciar duas retomadas nem duplicar cobranças. Uma solicitação já enviada ao provedor pode terminar e gerar consumo mesmo após cancelamento; conservar seu registro e impedir chamadas seguintes. Mudança de versão, fontes ou configuração exige revalidar o ponto salvo e identificar o trabalho que precisa ser refeito.

Se o engenheiro prosseguir apenas com parte dos pendentes, a cobertura global permanece parcial enquanto houver obrigações necessárias não resolvidas. Continuar a análise não equivale a aprovar recomendações documentais.

## 4. Propagação com IA preservada

### Primeiro incremento: região conservadora antes da execução

1. Carregar e validar estado, evento, seleção e fontes.
2. Usar os pontos de entrada como sementes. Incluir também outros pontos explicitamente confirmados como parte da mesma mudança.
3. Percorrer dependências de impacto cadastradas, respeitando direção e tipo. Incluir os responsáveis por cláusulas e parcelas pertinentes, mesmo quando não estiverem apenas na cadeia temporal.
4. Resolver obrigações compartilhadas por identificador único. Uma cobrança com vários caminhos não deve ser multiplicada.
5. Obter predecessores de fora da região como entradas de cálculo e contexto com origem verificável. Não ignorar o outro ramo de uma convergência.
6. Ordenar os nós selecionados pelas dependências. Manter uma análise local de IA para cada nó da região; fornecer evento, informações locais, regras e estados relevantes dos predecessores.
7. Executar o motor com o estado completo e as propostas aceitas. Verificar os documentos como na integração atual, considerando a validade de cada resultado.

Esse incremento prioriza uma seleção conservadora e compreensível: evita consultar ramos independentes, mas não tenta podar cada sucessor com heurísticas frágeis. Não deve ser apresentado como substituição da IA por cálculo em todo o subgrafo.

### Ampliação controlada durante a análise

Preservar encaminhamentos validados para outros responsáveis. Se surgir um alvo pertinente fora da região, registrar a causa e ampliar o plano respeitando orçamento e dependências. Reprocessar apenas resultados cujo contexto ficou obsoleto; se a ampliação exigir rever entradas já usadas e não houver orçamento, declarar a pendência. Nunca reutilizar como atual uma interpretação ligada a outra versão dos predecessores.

Evitar um laço ilimitado: controlar revisões e chamadas pelo orçamento global. Cada combinação de evento, nó, fontes, permissões, versões dos predecessores, modelo e configuração só pode reutilizar resultado compatível. Cache é otimização técnica, não nova evidência ou repetição experimental independente.

### Regras que impedem omissões

- Não parar a análise só porque o prazo final permaneceu igual: uma folga pode absorver o atraso, mas a disponibilidade do fornecedor ou o relatório ainda pode mudar.
- Não excluir impactos de custo porque não houve alteração temporal.
- Não tratar ausência de proposta da IA, nome pouco semelhante ou baixa pontuação de busca como prova de ausência de impacto.
- Não atravessar indistintamente todas as relações. Relações documentais e contextuais não são automaticamente precedências temporais.
- Diante de evento genérico, vínculo ambíguo ou regra insuficiente, registrar pendência/ampliar escopo explicitamente, sem publicar zero por falta de análise.

Uma segunda otimização, futura e separadamente avaliada, poderá interromper a expansão onde houver critério seguro por dimensão. Não é requisito do primeiro incremento.

## 5. Fechamento seletivo — principal cuidado técnico

Criar um fechamento próprio; não remover simplesmente a exigência de cobertura do fechamento histórico.

Cada nó terá um estado explícito: `interpretado`, `reutilizado_com_vinculo`, `calculado_sem_interpretacao`, `fora_do_escopo_justificado`, `pendente` ou `bloqueado_por_limite`.

Para publicar um resultado completo no escopo declarado, exigir:

- Todas as alterações identificadas no evento têm responsáveis cobertos, ou justificativa explícita de exclusão do teste delimitado.
- Cada nó exigido para interpretação foi processado, e as cláusulas/encaminhamentos pertinentes foram resolvidos.
- Os nós não consultados possuem justificativa registrada com base na seleção, nas dependências e nas premissas. Exclusão por alcance é válida sob o modelo cadastrado; não prova que a documentação ou o grafo sejam completos no mundo real.
- O cálculo conserva todos os predecessores, restrições e parcelas necessários. Não trocar desconhecimento por valores da baseline.
- Prazo e custo têm fechamentos separados: pendência monetária não bloqueia prazo determinável; pendência temporal pode afetar os dois.
- As recomendações documentais usam somente resultados sustentados naquele escopo. Estados auxiliares/condicionais não devem virar totais confirmados.

Uma execução parcial pode preservar resultados locais válidos, como já faz o Alfa, mas precisa distinguir esses resultados de uma conclusão global. As dispensas não podem fabricar confirmações semânticas de cláusulas ou assinatura humana.

## 6. Controle de custo e tempo

**A seleção manual é o caminho padrão de menor custo adicional.** A sugestão por IA é uma conveniência opcional que precisa compensar o consumo extra.

- Configurar tetos por execução de chamadas, tokens de entrada/saída, tempo e reserva monetária. Verificar antes de enviar cada solicitação, incluindo sugestão e possíveis reanálises.
- Respeitar também o limite de nós escolhido pelo engenheiro. `"todos"` remove apenas o teto numérico de nós da região elegível, sem remover os demais limites. Mostrar conflitos entre a região prevista e o orçamento antes da execução, quando identificáveis.
- Para a comparação experimental inicial no Alfa, configurar explicitamente um teto de 32 chamadas totais, incluindo sugestão. Esse valor pertence ao protocolo comparativo e não é um limite fixo do produto nem do campo de quantidade de nós. Se a região exigir 32 análises locais mais uma sugestão, mostrar a incompatibilidade com esse orçamento antes da coleta; não fazer 33 silenciosamente. Em outros projetos/execuções, limites de chamadas são configuração separada do N calculado para os nós.
- O teto de chamadas não garante menor custo: medir os tokens de todo o fluxo e o custo da configuração efetivamente utilizada. Limites monetários devem usar preços verificados na ocasião da execução.
- Não executar primeiro o seletivo e, em seguida, a análise completa automaticamente. Uma comparação experimental com os dois modos é uma coleta separada e contabilizada.
- Não repetir respostas falhas automaticamente nem dividir pedidos em várias chamadas sem registrar e reservar esse consumo.
- Reduzir contexto por pertinência e identificadores; não cortar fontes necessárias só para caber no limite. Bytes de JSON não substituem contagem de tokens.
- Reaproveitar cálculo determinístico e resultados compatíveis; primeira versão com agenda previsível, sem adicionar uma arquitetura multiagente concorrente.
- Exibir consumo total e pendências. Ao atingir um limite, interromper com resultado explicitamente parcial.

Não haverá chamada paga para implementar e testar o primeiro incremento. A coleta real precisa de protocolo e orçamento explícitos; esta solicitação de plano não amplia o teto financeiro histórico. Sem piloto real não haverá afirmação de economia medida de API.

## 7. Interface proposta

Criar demonstração separada que preserve a anterior e ofereça:

1. Escolher evento/cenário e versão do projeto.
2. Selecionar um ou mais nós no grafo ou buscar por nome.
   Digitar a quantidade no campo numérico “Máximo de nós analisados”, exibindo “Máximo disponível para análise: N nós”. Oferecer opcionalmente “Usar todos”, que seleciona esse máximo sem obrigar a visitar todos. Informar que as entradas contam e distinguir o total do grafo do total elegível quando forem diferentes.
3. Opcionalmente pedir sugestão e confirmar/corrigir os nós sugeridos.
4. Visualizar a região prevista de análise, os motivos de inclusão e uma estimativa de consumo.
5. Executar e acompanhar nós interpretados, apenas calculados, excluídos e pendentes.
   Ao atingir o limite, selecionar pendentes e escolher “Prosseguir com selecionados” ou “Cancelar análise”, visualizando consumo acumulado e estimativa adicional.
6. Consultar prazo, custo e recomendações documentais com evidências.

Usar ações simples: “Selecionar entrada”, “Sugerir entradas” e “Analisar mudança”. Não expor nomes de módulos, hashes ou detalhes de parser no fluxo principal. Deixar detalhes técnicos na inspeção. Não chamar uma simulação de execução real de IA.

## 8. Testes e avaliação

### Verificação de software, offline

- Reexecutar os 27 testes da etapa Alfa preservada e conferir integridade. As falhas históricas já registradas devem permanecer identificadas; não declarar toda a suíte aprovada sem evidência.
- Copiar somente a pasta v2 para um diretório temporário fora da árvore do repositório e executar os testes/demonstração offline com suas dependências declaradas, sem acesso implícito ao `src` antigo pelo caminho de importação. Verificar que código, dados e interface da execução vêm dessa pasta. Antes da seleção, comparar a migração estrutural com os resultados de desenvolvimento da v1, desconsiderando apenas metadados próprios de execução.
- Testar seleção única/múltipla, nó inexistente, versão obsoleta, entidade contextual, evento ambíguo e seleção divergente das menções.
- Testar campo livre com valores variados, limites 1 e N, `"todos"`, valores inválidos e acima de N, seleção inicial maior que o teto e atualização do máximo ao mudar projeto/versão. Testar contagem de nós únicos versus reanálises e término antecipado quando houver menos nós pertinentes. Ao atingir o limite, conferir fronteira pendente e resultado parcial, sem ultrapassagem silenciosa. N deve vir dos dados, nunca dos números de exemplo do plano.
- Testar retomada com seleção de pendentes, dependências adicionais, limites acumulados, preservação do ponto salvo e reutilização válida. Testar cancelamento, chamada em andamento, duplo clique, recarga da interface e alteração de versão; não repetir chamadas válidas nem declarar cobertura completa com pendências.
- Testar convergência com predecessor fora da região, atraso absorvido, preço sem atraso, custo compartilhado e informação desconhecida.
- Testar encaminhamento para fora da região, invalidade da resposta, esgotamento de orçamento e necessidade de reanálise por mudança de predecessor.
- Testar documento já atualizado, mudança local sem impacto global e preservação dos estados parciais.
- Verificar que nós não consultados não são marcados como analisados nem recebem evidências fabricadas.
- Confirmar que cada chamada opcional, falha ou reanálise conta para o limite; mesma entrada pode reutilizar cache, mas versão/fonte/modelo diferente invalida o reuso.

Usar os nove casos de desenvolvimento conhecidos para integração. Não abrir os oito casos finais reservados para escolher regras de seleção ou ajustar a implementação.

### Comparação científica

Comparar três modos de **seleção**, mantendo o restante da arquitetura equivalente:

| Modo | Entrada | O que mede |
|---|---|---|
| Cobertura completa Alfa | Todos os 32 pontos | Referência operacional. |
| Seleção manual | Nós definidos por procedimento e registrados antes da execução | Benefício da seleção assistida pelo engenheiro; esforço humano registrado separadamente. |
| Seleção sugerida por IA | Catálogo + evento + revisão registrada | Benefício e erros do seletor, incluindo seu consumo. |

Congelar protocolo, casos, modelo, configurações, limites e critérios antes da coleta. Resultados da cobertura completa não são automaticamente o gabarito: usar referências revisadas separadamente. Se houver correção humana da sugestão, reportar o resultado da sugestão original e o da seleção confirmada; não atribuir à IA o acerto do engenheiro.

Medir chamadas, tokens, custo total, latência total, cobertura dos efeitos necessários, precisão de prazo/custo, indeterminação adequada, completude e qualidade documental por item. Não premiar um método só por custar pouco ao deixar de concluir casos. Comparar economia também entre execuções com qualidade e cobertura equivalentes. Tempo humano de seleção/revisão é distinto de latência de API.

### Critérios de aceite

- Nenhuma alteração em artefatos históricos e nenhuma regressão nova nos comportamentos cobertos.
- Mesmos valores/estados e revisões esperadas nos testes de equivalência completos; execução parcial corretamente sinalizada nos testes adversos.
- Menos análises locais em eventos de escopo restrito. Caso abrangente pode ter o mesmo número; não prometer ganho universal.
- Nenhuma chamada redundante ao seletor no modo manual e cumprimento dos tetos em todos os caminhos.
- Na coleta real, demonstrar redução de consumo/latência no conjunto definido sem perda de qualidade pelos critérios pré-fixados. Se houver troca entre economia e cobertura, reportá-la e manter o modo anterior como opção; não declarar sucesso irrestrito.

## 9. Sequência de implementação e entregas

1. **Congelar a referência:** inventário, hashes, comandos reproduzíveis e teste da versão atual.
   Preparar o pacote completo `alfa_documental_v2`, o índice `VERSAO_ATUAL.md` e o manifesto de origens; verificar autonomia e equivalência antes de modificar o fluxo de análise.
2. **Implementar seleção manual e alcance conservador:** sem IA adicional, com rastros e casos de seleção.
3. **Integrar agenda e fechamento próprios:** preservar contexto, permissões, cálculo e recomendações; testar exclusões e pendências.
4. **Adicionar controle global de consumo:** garantir limites antes de qualquer possibilidade de chamada real.
5. **Entregar demonstração manual:** escolha por clique/busca, região prevista e resultados comparáveis em simulação.
6. **Adicionar sugestão opcional:** catálogo compacto, uma chamada, validação e confirmação; testar inicialmente com transporte simulado.
7. **Medir offline e revisar metodologia:** relatório de cobertura, análises evitadas, equivalência e limitações; isso não mede desempenho da IA.
8. **Preparar piloto real delimitado:** contagem e orçamento revisados, referências humanas e protocolo congelado antes de coleta autorizada.

Entregáveis: pacote separado, testes, demonstração, relatório comparativo, especificação dos contratos e documentação das limitações. Atualização do TCC deve distinguir contribuição de seleção, capacidade documental e resultados simulados/reais.

## Fora do primeiro incremento

Não implementar nesta mudança importação de áudio/Word/PDF, criação automática de grafo, alterações de topologia pelo evento, atualização de documentos oficiais, calendário útil, planejamento de recursos ou SaaS. Não generalizar regras específicas do Alfa apenas renomeando identificadores. Essas evoluções continuam no [arquivo de tópicos](TOPICOS_TCC.md).

Referências locais: [Alfa documental](TCC_Codigos/etapas/alfa_documental_v1/README.md), [resultados e limitações](TCC_Codigos/etapas/alfa_documental_v1/RELATORIO.md), [política atual](TCC_Codigos/etapas/alfa_documental_v1/politica.py), [agenda atual](TCC_Codigos/etapas/alfa_documental_v1/orquestracao.py).
