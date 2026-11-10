# Conferência manual autoral e visual

09–10/11/2026. Conferência pelo assistente que implementou a etapa. Não é aprovação humana, avaliação cega nem revisão independente.

## Prazo e custo

A cadeia de engenharia fecha em 2 + 3 + 5 + 4 = D14. Compras acrescentam 6 dias, chegando a D20. As entregas convergem com esse limite. Montagem dura 5; o maior ensaio dura 10; documentação e liberação duram 3 + 2. Portanto a base termina em D40. As dez parcelas somam 15.200.000 centavos.

| Caso | Conta conferida manualmente | Resultado |
|---|---|---|
| D01 | Entrega motor D19; início da montagem max(20,19,demais entregas)=20 | Fim D40, custo R$152.000. Apenas SR.MOTOR muda. |
| D02 | Entrega D25 → montagem 25–30 → maior teste até D40 → documentação/liberação até D45 | +5 dias; overhead 5×R$300=R$1.500. Sem extensão do intervalo comum do laboratório. |
| D04 | Entrega sem data/límite superior; máximo e sucessores sem término exato | Não completar o relatório com a baseline. Término e custo totais indeterminados. |
| D05 | Motor D23 e MetalForm D24 → max(20,23,24)=24, embora MetalForm abasteça quatro componentes | Fim D44; +R$1.200. Sem somar atrasos de ramos nem multiplicar o fornecedor por quatro. |
| D06 | Testes de carga 12 e térmico 14 → maior ensaio=14 | Fim D44. Laboratório 4×R$500 + overhead 4×R$300 = R$3.200. |
| D09 | Preço p_10 desconhecido; demais preços e calendário conhecidos | Fim D40. Custo total indeterminado; não inferir aumento nem usar R$30.000 silenciosamente. |

## Afirmações e sustentação

A unidade é cenário × documento@versão × trecho × campo. D02 produz três recomendações específicas; SR.FREEZE e SR.CAD permanecem corretos. D07 usa STATUS@2, com os valores finais já registrados: cinco afirmações verificadas, zero recomendações. D08 confirma a disponibilidade original e não altera campos.

Foram conferidas as **14 recomendações** da rodada `runs/dev_05`, comparando aviso, dados base, contratos, cálculo e alteração proposta. **14/14 sustentadas segundo esta conferência autoral**, com zero divergências encontradas. Os juízos, unidades, fontes e contas estão em [qa/suporte_autoral.json](qa/suporte_autoral.json). Esse indicador é separado da verificação mecânica de existência das citações (também 14/14) e **não substitui uma auditoria semântica independente**.

Action Log, Risk Register e Decision Log foram conferidos como controles de não criação automática. Atriagem relacionada mantém pendência de avaliação específica e não emite novas ações/riscos/decisões. Casos positivos de atualização desses artefatos não foram implementados nem avaliados.

## Interface em navegador real

O host de automação do navegador embutido estava indisponível. A validação foi feita no Safari nativo, com árvore de acessibilidade e capturas de tela:

- D02 em replay: D40 → D45, R$153.500, 32/32 análises, três recomendações.
- Modo offline acionado pelo painel: POST local executou o Python; resposta mostrou “SIMULAÇÃO OFFLINE executada agora”, os mesmos resultados e zero chamadas de IA. Arquivo novo preservado em `runs/interativo/`.
- Grafo renderizado, incluindo fornecedores/componentes, cadeia de engenharia, ensaios paralelos, marcos, oito pessoas/áreas e nove documentos/versionamentos (49 nós; D07 tem 50).
- Clique em DOC_CAD@1 abriu versão, trecho CAD.1 e relações descreve/produz, distinto de T_CAD.
- D07 em replay: STATUS@2, cinco campos já atualizados, zero recomendações.
- Reprodução foi iniciada em 0/32 e observada em 8/32. Os totais são explicitamente identificados como resultados do ciclo completo, e a animação como reprodução do rastro.
- Na versão final, a acessibilidade confirmou TEST_LOAD, TEST_THERMAL, TEST_SEAL e TEST_EMC como dominados na convergência, mantendo TEST_LIFE como ramo controlador.
- O SVG inicialmente ocultava botões de nós da árvore de acessibilidade por `role=img`; passou a `role=group` e os botões/documentos ficaram acessíveis. Erro inicial de fechamento de função JS foi corrigido e o arquivo passou no `node --check`.

Não foi realizada uma auditoria completa de acessibilidade nem validação em dispositivos móveis. A folha de estilo contém adaptações responsivas; isso não é evidência de teste mobile.
