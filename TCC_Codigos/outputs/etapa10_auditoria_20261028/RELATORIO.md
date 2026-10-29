# Etapa 10 — auditoria técnica independente

28/10/2026. **Concluída no escopo técnico, com ressalvas científicas.** Revisores separados, sem o histórico da implementação e sem previsões, resolveram os casos a partir das fontes. As entregas foram seladas antes do confronto. Isso não constitui parecer humano nem garante independência científica externa. A etapa 11 não foi executada.

**Resultado principal:** os 25 desfechos numericamente determinados dos 15 casos de desenvolvimento foram confirmados. Nenhum valor exato do gabarito precisou mudar. As agregações dos 180 registros v6/v7 e os custos das 280 chamadas da última coorte também conferiram. Um novo projeto com três eventos foi preparado, revisado e separado do desenvolvimento; ambiguidades encontradas nas fontes iniciais foram corrigidas antes do congelamento.

## Achados e providências

1. **Premissas do modelo não estavam igualmente explícitas nos contextos.** O primeiro parecer conservou como condicional a direção do custo em k_23d8. Um suplemento só com definições formais preexistentes — sem gabaritos nem exemplos resolvidos — confirmou parcelas não negativas, créditos apenas autorizados, início mais cedo e convergência. O revisor confirmou então Δcusto ≥20000 centavos, mantendo magnitude desconhecida. A primeira derivação permanece intacta. Isso sustenta a verdade no modelo, mas não prova visibilidade de todos os axiomas no piloto. **Corrigido prospectivamente:** as convenções temporais constam agora de fonte comum às três condições no conjunto final v2; os fatos, código e resultados históricos não foram reescritos.
2. **Indeterminação pode ser real ou decorrer do contexto limitado.** A revisão final enumerou 29.281 DAGs, dos quais 1.268 respeitam a linha base e os fatos comuns de B. No primeiro aviso B consegue provar aumento de prazo/custo, mas não um valor único; no aviso de crédito B pode resolver ambos exatamente. No aviso de taxa indefinida, zero é apenas possível. **Corrigido:** referências por view, conjuntos admissíveis e limites separados da verdade completa; o avaliador suplementar não converte compatibilidade com um limite em acerto exato.
3. **Taxa desconhecida estava só no relato, com `lacunas: []`.** **Corrigido na v2:** a lacuna foi também registrada no campo estruturado, sem preencher a taxa ou reutilizar a revogada. O protocolo esclarece que lista vazia não certifica ausência de toda incerteza.
4. **As limitações do piloto permanecem.** H teve 23/30 previsões exatas de prazo e 21/30 de custo, todas compatíveis com a verdade numérica revisada. Restam três execuções H com referência exata e resposta parcial. B/k_6d82/2 errou custo em R$150; T/k_23d8/1 afirmou direção temporal sem suporte na verdade completa. As 11 rejeições globais permanecem no denominador. A auditoria não reparou respostas nem afirma ter revisado semanticamente cada uma das 220 análises locais. A melhoria observada não isola o efeito do grafo, pois prompt, schema e coordenação diferem entre sistemas.
5. **Rastreabilidade histórica:** o ID de regra c_d74a no aviso k_42a9 não foi previamente declarado nas fontes literais, embora a descrição do único apoio permita resolver o cálculo. **Proposto:** esclarecer esse vínculo em eventual nova versão de desenvolvimento; o pacote histórico fica preservado. Não afeta os IDs nem as fontes do novo projeto.

## Casos finais preparados — gabaritos, não previsões

Pacote vigente: [etapa10_v2](../../data/final/etapa10_v2/README.md), projeto fictício Estação de leitura Sálvia. A versão 1 foi preservada como preparação anterior à revisão. Topologia, durações, custos e três avisos foram concebidos sem consultar as previsões do piloto; a revisão 2 só explicitou convenções comuns, versão e lacuna. Nenhum candidato foi executado nesses casos.

| Caso | Δprazo na informação completa | Δcusto na informação completa | O que B consegue identificar |
|---|---:|---:|---|
| k_1671298a5a | +4 dias | +R$344,00 | Prazo em {+3,+4,+6}; custo em {+R$258,+R$344,+R$516}; aumentos certos, magnitudes não únicas |
| k_ec2826cc2a | 0 dia | −R$116,00 | Ambos exatos, por invariância temporal e crédito explícito |
| k_c23705f4ea | +6 dias | 6r centavos, r inteiro ≥0 e sem teto | Prazo em {0,+1,+3,+4,+5,+6}; custo ≥0, sem teto; zero não é um valor identificado |

H/T têm a mesma união informacional; o contexto efetivamente entregue a cada nó H será verificável no rastro de uma coleta futura. A seleção é intencional, com três eventos em um projeto sintético. Ela permite uma avaliação prospectiva exploratória; não sustenta generalização, significância estatística ou estabilidade entre repetições.

## Critérios de conclusão

| Critério | Evidência e decisão |
|---|---|
| Preservação e orçamento | Inventário anterior, comparação da carteira e `verificacao_final.json`; nenhuma alteração indevida ou chamada nova |
| Revisão cega dos gabaritos | [Parecer inicial](revisao_cega/NOTAS.md), [adendo formal](revisao_cega/ADENDO_MODELO.md) e [confronto](confronto_desenvolvimento.json); selos preservados |
| Métricas e custo | [Recomputação](auditoria_metricas.json) dos 180 registros e [usage](auditoria_uso.json) das 280 chamadas; sem divergências nas agregações publicadas |
| Separação e casos inéditos | Autor separado de revisor; [parecer v2](revisao_final_v2_cega/NOTAS.md), três casos/projeto novos, referências fora dos inputs, nenhuma previsão final |
| Congelamento e compatibilidade | 141 arquivos do preditor preservados; 9 slots/18 contextos iniciais; seis contraprovas de vínculo; manifesto, views, protocolo e referências cobertos por `congelamento.json` |
| Entrega e limites | Este relatório, protocolo prospectivo, scripts reproduzíveis e ficha humana não preenchida; sem presumir aprovação científica |

## Escopo da verificação

Os totais abaixo são unidades do inventário de revisão, não uma taxa de acerto dos modelos; categorias se sobrepõem. `0/N` significa nenhum defeito remanescente observado naquela parte da entrega, não validação humana nem cobertura semântica integral do piloto. Os erros preditivos existentes estão descritos acima.

### Qualidade e utilidade do pacote

| Categoria | Defeitos observados | Avaliação |
|---|---|---|
| Completude no escopo | 0/1 | Conjunto prospectivo e limites da revisão documentados; aceite técnico separado de parecer humano |
| Clareza analítica | 0/2 | Distinções cobertura/acerto e valor identificado/possível verificadas |
| Visual/interação | N/A | Pacote documental e computacional, sem dashboard |

### Correção e robustez analítica

| Categoria | Defeitos observados | Avaliação |
|---|---|---|
| Autoridade/proveniência | 0/19 | 18 referências de casos e uma reconciliação de custos; fontes fictícias e origem dos selos identificadas |
| Valores e agregações | 0/31 | Referências de 18 casos, 12 resumos dimensão/condição/versão e uma reconciliação; não significa ausência de erros nas previsões |
| Coerência de gráficos | N/A | Nenhum gráfico nesta auditoria |
| Detalhes de fontes em interface | N/A | Evidência em arquivos e trechos, sem interface de dashboard |
| Coerência entre artefatos | 0/2 | Pareamento v6/v7 e confronto autor/revisor final |
| Qualidade dos dados | 0/6 | Três casos finais, pareamento, carregamento e tratamento de ausências/domínios |
| Sustentação das conclusões | 0/2 | Limites de inferibilidade e de independência científica explícitos |

O registro de cobertura está em `cobertura_revisao.json`. A auditoria de valores finais foi reproduzida integralmente em diretório temporário; os artefatos selados permaneceram intocados. As 59 verificações do parecer v2, seis contraprovas de inputs e dez do avaliador foram aprovadas. Não houve teste do desempenho do modelo nos casos finais.

## Carteira e protocolo futuro

**Nenhuma chamada paga na etapa 10.** Carteira única mantém 1.114 tentativas e **US$4,480425665 comprometidos**, saldo **US$0,519574335** sob teto US$5. Inclui inferência conhecida US$2,063925665, provisões de contagem US$2,228 e reservas de inferência desconhecida US$0,1885; as 13 tentativas desconhecidas históricas continuam preservadas. Não é fatura.

O [protocolo congelado](../../docs/desenvolvimento/ETAPA_10_PROTOCOLO_FINAL.md) prevê três casos, B/H/T e uma repetição: nove slots e no máximo 30 tentativas. Pela reserva vigente, o máximo incremental é US$0,495, levando o compromisso a no máximo **US$4,975425665**. Preços, carteira e hashes devem ser reconferidos antes de coleta autorizada. O teto prevalece sobre completar o lote.

Está pronto o carregador exclusivo de inputs, o manifesto de nove slots, a política/preditor congelada e o pós-processamento. O runner histórico de 90 slots permanece intacto e não deve ser usado para este lote. A integração do executor pago com o novo manifesto e sua reserva atômica pertence à etapa 11, antes de qualquer envio; não há autorização implícita de coleta nesta entrega.

## Reprodução e revisão humana

Da raiz do projeto, executar os scripts dentro de `TCC_Codigos/outputs/etapa10_auditoria_20261028/`: `auditar_pilotos.py`, `auditar_uso.py`, `reproduzir_cega.py`, `confrontar_desenvolvimento.py`, `preparar_final.py`, `consolidar_referencias_finais.py`, `avaliar_final.py` e `verificar_final.py`. São offline. O último verifica integridade e congelamento; não cria um novo congelamento. Os geradores devem ser usados em cópia para não mudar timestamps de artefatos selados. Não executar os scripts dos revisores dentro das pastas seladas: usar cópia temporária, conforme os registros de reprodução.

Para parecer humano, usar [ficha de revisão](../../docs/desenvolvimento/ETAPA_10_PARECER_HUMANO.md). A autorização de trabalho do usuário e a revisão por outros agentes não foram registradas como aprovação de orientador/especialista. Não houve contato com terceiros, publicação, commit ou execução da etapa 11.
