# Entrega Alfa documental v2 — 10/11/2026

A v2 implementa seleção manual de entradas, alcance conservador com interpretação local preservada, limite livre de nós, pausa com pendentes, continuação, cancelamento e revisão documental. O pacote é autossuficiente e mantém as versões anteriores intactas. **A validação é offline, com interpretações preparadas manualmente. Não houve nova chamada paga.**

## Resultado da comparação de desenvolvimento

As nove execuções seletivas preservaram os valores, estados de conhecimento, limites quantitativos, classificação das cinco afirmações e recomendações documentais da referência anterior. O comparador de cobertura completa foi migrado primeiro, com equivalência conferida antes da alteração da agenda.

| Caso | Interpretações completas | Interpretações seletivas | Prazo final | Custo final | Recomendações |
|---|---:|---:|---:|---:|---:|
| D01: atraso absorvido | 32 | 13 | 40 dias | R$ 152.000 | 1 |
| D02: atraso crítico | 32 | 13 | 45 dias | R$ 153.500 | 3 |
| D03: preço sem atraso | 32 | 13 | 40 dias | R$ 155.000 | 1 |
| D04: entrega sem data | 32 | 13 | Indeterminado | Indeterminado | 3 |
| D05: fornecedores e convergência | 32 | 18 | 44 dias | R$ 153.200 | 3 |
| D06: ensaios e custo compartilhado | 32 | 6 | 44 dias | R$ 155.200 | 2 |
| D07: relatório já atualizado | 32 | 13 | 45 dias | R$ 153.500 | 0 |
| D08: sem alteração | 32 | 13 | 40 dias | R$ 152.000 | 0 |
| D09: preço desconhecido | 32 | 13 | 40 dias | Indeterminado | 1 |
| **Total** | **288** | **115** | | | **14** |

Foram evitadas **173 interpretações locais simuladas, redução de 60,07%**. Isso mede o trabalho da agenda sob respostas manuais, e não economia observada de tokens, dinheiro ou tempo de API. A qualidade de seleção de uma IA real continua sem avaliação. O tempo de software registrado inclui serialização e persistência e não representa a latência de um serviço de IA.

As entradas manuais usadas foram as menções cadastradas nos eventos. Portanto a comparação pressupõe uma seleção correta do engenheiro; não mede seu esforço nem seu erro. A referência de equivalência deriva da versão anterior e as referências documentais são autorais. Uma revisão humana independente e uma coleta congelada continuam necessárias para alegações científicas mais fortes.

Evidências: [métricas offline](metricas_offline.json), [migração estrutural](migracao_estrutural.json), resultados completos em `outputs/comparacao_20261110T042602276810Z/`. O avaliador persiste as previsões antes de consultar as referências. Os oito casos finais reservados não foram copiados ou usados para ajuste.

## Controles exercitados

- **35 testes funcionais e adversos aprovados**, com sockets bloqueados. Os 34 testes anteriores também passaram depois de copiar apenas a v2 para um diretório temporário fora do repositório.
- Limite livre 1..N; rejeição de vazio, zero, negativos, booleanos, frações, duplicações, alvos inexistentes/contextuais, versão obsoleta e seleção maior que o teto. N vem da projeção, não de uma constante de produto.
- D02 interrompido em um nó e retomado até 13, com apenas 13 solicitações acumuladas. O primeiro nó não é interpretado novamente. Pedidos duplicados com a mesma identidade não geram trabalho novo.
- Continuação somente de um sucessor com predecessor pendente não executa indevidamente. Dependências não escolhidas aparecem como bloqueios e os totais globais permanecem indeterminados.
- Cancelamento durante uma interpretação preserva a resposta em andamento e impede o próximo passo. O caso de teste completou uma única solicitação simulada; o resultado ficou parcial e cancelado.
- Um encaminhamento válido para um predecessor fora da região ampliou a análise e invalidou o contexto de um sucessor. A reanálise contou como nova solicitação, sem duplicar a contagem de nós distintos.
- Mudança de configuração ou fontes impediu reuso. Uma resposta inválida ficou registrada como falha e não virou ausência de efeito.
- Sugestão de entradas conta no orçamento total, inclusive quando falha. Confirmar/corrigir as entradas é requisito também do backend, e o histórico preserva sugestão e seleção do engenheiro. Repetir o mesmo pedido inválido não invoca novamente o transporte. Confirmação/correção preserva a mesma sessão e o consumo da sugestão.
- Transporte real recusado tanto na sessão quanto na entrada do pipeline. Nenhuma credencial, carteira nova ou contador de custo artificial foi criado.

Logs: [testes locais](testes_offline.txt), [testes isolados](testes_isolados.txt). A validação independente do orquestrador e a inspeção de interface são registradas separadamente em `REVISAO_ORQUESTRADOR.md`, quando concluídas.

## Preservação e estrutura

O inventário inicial contém 2.205 arquivos históricos. A conferência final está em `preservacao_depois.json`. A v1, o código compartilhado histórico, os dados selados, os resultados e a carteira são preservados. O manifesto registra hashes de origem e do conteúdo incorporado; ajustes de namespace e evoluções da v2 são identificados, sem atribuir a versão seletiva ao código original.

As dependências próprias necessárias estão em `src/vendor`, com imports relativos. Os dados executáveis residem em `data/projetos/alfa`; referências de avaliação ficam fora deles. Bibliotecas externas não foram copiadas e não há dependência de pacote externo no runtime atual. A interface usa apenas HTML/CSS/JavaScript locais e servidor Python local.

## Limitações e trabalho restante

Esta entrega demonstra redução do número de análises locais necessárias no modelo cadastrado, preservando os resultados dos casos sintéticos avaliados. Não demonstra generalização, qualidade de IA, superioridade causal do grafo nem desempenho econômico de um SaaS.

O seletor da demo é uma resposta manual baseada nas menções existentes. O contrato admite transporte injetado simulado, zero ou múltiplas sugestões e ambiguidades; conectar IA real depende de nova validação e orçamento explícitos. O controle de tokens e dinheiro tem valor zero verificável no modo offline. Antes de habilitar chamadas reais, implementar reservas transacionais, conferir uso e preços do provedor e reconciliar a carteira histórica — a pasta nova não reinicia o saldo.

A avaliação documental continua limitada a cinco afirmações preparadas do Status Report, com triagem dos três outros artefatos. O grafo, as relações, as fontes e os quantitativos são cadastrados. Não há áudio/PDF/Word automático, novos nós criados pelo evento, escrita oficial, memória cumulativa de eventos, calendário útil ou restrição de capacidade de recursos.

O próximo passo científico é congelar casos e procedimento de seleção, revisar os gabaritos com o orientador, medir esforço humano separadamente e executar um piloto real autorizado. Comparar cobertura completa, escolha do engenheiro e sugestão de IA com os mesmos fatos, registrando a sugestão original e a correção humana. Casos parciais ou incorretos não devem ganhar uma comparação apenas por custarem menos.
