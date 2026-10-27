# Status do desenvolvimento

Atualizado em 27/10/2026 (America/Sao_Paulo).

## Resumo vigente — 27/10/2026

**H v05: correção offline concluída para revisão, opt-in, sem nova chamada paga.** Foram aprovados 92 testes; 557 arquivos protegidos e ledger preservados. Ausência passa a ter escopo por cláusula; `lacunas` local é nota e fatos ausentes devem estar em propostas tipadas ou pendências operacionais. Omissão do modelo ainda pode causar falsa precisão; sem validação semântica ou ganho real demonstrado. Avaliação v05 isolada com rejeição de versões misturadas. [Entrega e limitações](ETAPA_09_H_V05_OFFLINE.md). Próximo passo: revisão antes de qualquer novo piloto; etapas 10/11 não iniciadas.

**Piloto real v04: coleta encerrada em 90/90 slots, entregue para revisão.** São 15 casos, B/H/T e duas repetições; 30 resultados por condição e nenhum não iniciado. O R2 SSE executou as 70 pendentes com aprovação humana explícita, em 201 chamadas conciliadas, sem retry ou nova parada. As fases anteriores e as 20 saídas/chamadas 1–71 foram preservadas.

- Orçamento global: 272 tentativas; US$ 1,206550975 comprometidos e US$ 3,793449025 de saldo interno sob teto US$ 5. Inferência conhecida US$ 0,488550975; reserva de inferência desconhecida US$ 0,174; provisão hipotética de contagem US$ 0,544. Não é fatura.
- Cobertura exata prazo/custo: B 5/30 e 7/30; H 2/30 e 2/30; T 21/30 e 22/30. MAE zero somente nos pares exatos elegíveis; custo T tem 21 pares, não 22 acertos. H exato corresponde apenas ao caso k_a064 de impacto zero, em duas repetições. Sem superioridade científica inferida.
- Próxima ação: revisar baixa cobertura H, rejeições de formato/contrato, falsa precisão de T/k_d307 e referências/inferibilidade antes de decidir sobre etapas 10/11. Suporte semântico não auditado. Sem novas chamadas ou correções automáticas.
- [Relatório atual e evidências](../../outputs/etapa9_sse_r2_offline_20261026/execucao_20261027/RELATORIO.md). As seções abaixo preservam o histórico; este resumo rege o estado vigente. Etapas 10/11 não iniciadas.

- **Etapa 0: APROVADA pelo usuário em 24/10/2026.**
- **Etapa 1 e quatro propostas: APROVADAS pelo usuário em 24/10/2026.**
- **Etapa 2: APROVADA pelo usuário em 24/10/2026 (“Avance para a próxima etapa”).**
- **Etapa 3: APROVADA pelo usuário em 24/10/2026 (“Prossiga para a etapa 4”).**
- **Etapa 4: APROVADA pelo usuário em 24/10/2026 (“Aprovado, passe para a 5”).**
- **Etapa 5: APROVADA para progressão pelo usuário em 25/10/2026 (“Faça a etapa 6 agora”).**
- **Etapa 6: APROVADA para progressão pelo usuário em 25/10/2026.**
- **Etapa 7: APROVADA para progressão pelo usuário em 25/10/2026 (“Inicie a etapa 8”).**
- **Etapa 8: APROVADA para progressão pelo usuário em 26/10/2026.**
- **Etapa 9: piloto real v04 encerrado em 90/90; ENTREGUE PARA REVISÃO; auditoria semântica e inferibilidade pendentes.**
- **Etapas 10/11: não iniciadas.**
- Próxima ação: revisar limitações H, erros de formato/contrato e falsa precisão de T/k_d307 antes de decidir sobre etapas 10/11. Sem novas chamadas ou avanço automático.

## Registro anterior — etapa 2

Autorização mais recente: “Aprovo a etapa 1 e as quatro propostas. Pode iniciar a etapa 2 com um agente separado para criar o projeto mínimo e os cenários de desenvolvimento. Traga a entrega para revisarmos antes de avançar.”

[Etapa 2](ETAPA_02_PROJETO_MINIMO.md): projeto fictício Bancada Íris, sete entidades, quatro atividades e marco final, cinco parcelas base, treze documentos/25 trechos, oito casos independentes e referências autorais separadas. Linha base D10 e R$5.000. Material de dados preparado para normalização na etapa 3, sem EstadoProjeto executável completo. Sem grafo operacional, motor, serializadores de views, API/LLM, UI, notebook, avaliação de modelo ou integração do worktree textual.

Preparação no worktree `/Users/vaugusto/.codex/worktrees/8077/TCC`; destino principal `/Users/vaugusto/Desktop/Faculdade/TCC`, mesmos caminhos relativos. Cópia autorizada somente do pacote novo, documento da etapa 2 e atualizações de PLANO_MESTRE/ETAPA_01/STATUS, após conferência de hashes originais, recusando conflitos e confirmando igualdade final.

## Evidências e limites

Verificações locais da etapa 2: JSON/IDs/unidades/fontes literais, soma do orçamento, cronogramas e custos por aritmética independente simples, oito avisos isolados com precedência expressa, sem resultados finais/expected_* nos inputs. Registro detalhado em `referencias/VERIFICACAO.md`. Referências autorais: conferência documental do coordenador recebida; conferência final dos ajustes e revisão humana independente pendentes; não são ground truth científico validado. Views B/H/T ainda requerem auditoria própria de suporte e vazamento.

Base histórica ebcc16c019793ceab2493649c0051a4d571fc8c2 preservada. Sem suíte histórica nesta etapa, chamadas pagas, credenciais, instalações, commit/push/PR ou alterações em dados/código/resultados antigos. O teste histórico da etapa 0 permanece: 130 testes, 123 aprovados, seis falhas e um erro de ambiente (openai ausente); histórico anterior 124/130, não execução nova.

Pendências preservadas: divergências de rótulos/prompt/pilotos/snapshot/ZIP, revisão científica de referências, cálculo geral e interpretação por nó ainda não implementados, condição textual isolada no worktree 8cc4. Aprovação de uma etapa não certifica o software legado nem congela amostra/modelo final.

## Histórico resumido

Etapa 0 aprovada e etapa 1 autorizada em 24/10/2026. Etapa 1 entregue documentalmente e revisada pelo coordenador: LLM em X e C, requer com projeção específica, restrições identificadas, inaplicabilidade e incidência temporal líquida. Conta didática preservada (+2 dias/+R$400). A aprovação posterior do usuário inclui as quatro propostas; o corpo histórico da especificação foi preservado com nota de vigência.

## Revisão documental da etapa 2 — 24/10/2026

Coordenador conferiu fontes, base e sete casos. Corrigido k_23d8 para custo direcao/aumento ≥R$200, sem magnitude exata, mantendo prazo indeterminado e fatos originais; justificativa nas referências. Descrições de parcelas passaram a nomes humanos. Arquivos afetados/hashes reconferidos; sem suíte histórica. Conferência final dos ajustes, aprovação do usuário e revisão humana independente pendentes. Etapas 3–11 não iniciadas.

## Vigência da transição para etapa 3 — 24/10/2026

Após revisar a entrega da etapa 2, o usuário declarou “Avance para a próxima etapa”. Isso registra a etapa 2 como **APROVADA pelo usuário** e autoriza somente a etapa 3. Menções históricas a aprovação pendente e etapa 3 não iniciada ficam superadas por esta nota, preservando os achados e a distinção entre aprovação do usuário, conferência autoral/documental e revisão humana independente (ainda pendente).

[Etapa 3 — grafo e dependências](ETAPA_03_GRAFO_DEPENDENCIAS.md) entregue aguardando revisão do coordenador e usuário: sete entidades, seis relações semânticas, cinco arcos causais, uma regra de transferência, uma local e uma de custo. Snapshot etapa 2 preservado; baseline D10/R$5.000 declarada. Validador stdlib passou e rejeitou seis contraprovas. Nenhum motor/LLM/views implementado. Etapas 4–11 não iniciadas; não avançar automaticamente.

Preparação da etapa 3: `/Users/vaugusto/.codex/worktrees/d72e/TCC`; destino principal `/Users/vaugusto/Desktop/Faculdade/TCC`. Somente novo pacote grafo, documento ETAPA_03 e updates PLANO_MESTRE/ETAPA_02/STATUS. Originais e snapshot etapa 2 comparados por conteúdo antes de editar; hashes documentais capturados antes da cópia e reconferidos imediatamente antes de substituir. Igualdade final e validação na principal exigidas.

## Vigência da transição para etapa 4 — 24/10/2026

O usuário declarou “Prossiga para a etapa 4”: etapa 3 **APROVADA pelo usuário** e somente etapa 4 autorizada. Menções históricas a etapa 3 pendente/etapa 4 não iniciada ficam superadas por esta nota.

[Etapa 4 — motor determinístico](ETAPA_04_MOTOR_DETERMINISTICO.md) entregue **pendente de revisão do coordenador e usuário**: pacote puro offline, baseline recalculada D10/500000 centavos, oito fixtures manuais, rastros e livro únicos, 37 testes aprovados. Sem LLM, agenda, integração de views ou alteração de legado. Etapas 5–11 não iniciadas; não avançar automaticamente. Revisão humana independente permanece pendente.


## Vigência da transição para etapa 5 — 24/10/2026

O usuário declarou “Aprovado, passe para a 5”: etapa 4 **APROVADA pelo usuário** e somente etapa 5 autorizada. Notas históricas de pendência da etapa 4 e etapa 5 não iniciada ficam superadas por esta seção.

[Etapa 5 — adaptador de interpretação por nó](ETAPA_05_ADAPTADOR_LLM.md) entregue **pendente de revisão do coordenador e usuário**. Contratos/contexto por seleção positiva, adaptadores simulado e LLM com transporte injetável, propostas sem aplicação automática, falhas e consumo observado, exemplo prescrito e 21 testes offline. Regressão: 37 testes etapa 4 aprovados, sem mudança no motor. Sem transporte de provedor concreto, credenciais, rede paga, avaliação científica, agenda, UI ou commit/push/PR. Modelos, limites e orçamento do piloto serão definidos antes de coleta autorizada. Etapas **6–11 não iniciadas**; não avançar automaticamente.

## Entrega atual — etapa 6, 25/10/2026

[ETAPA_06_ORQUESTRACAO.md](ETAPA_06_ORQUESTRACAO.md): avaliar com agenda topológica, contexto corrente local, política semântica externa conservadora, cache/revisões, bloqueio de descendentes pendentes, consumo novo separado do histórico e consolidação pelo motor. Oito demonstrações explicitamente SIMULADAS; 24 testes etapa 6 aprovados (também Python -O), 37+21 regressões etapas 4/5 aprovadas, validador etapa 3 aprovado. Nenhum módulo anterior alterado. Aprovação de progressão não é validação científica independente. Entrega pendente; etapas 7–11 não iniciadas.


## Vigência da transição para etapa 7 — 25/10/2026

O usuário declarou “Aprovado, pode iniciar a etapa 7 com um agente separado e trazer a entrega para revisarmos antes de avançar.” Etapa 6 aprovada para progressão; somente etapa 7 autorizada. Menções históricas a etapa 6 pendente/etapa 7 não iniciada ficam superadas.

[Etapa 7](ETAPA_07_BASELINES_AVALIACAO.md) entregue pendente de revisão: views positivas B/H/T vinculadas aos dados comuns, baseline global injetável sem motor, integração explícita H e normalização por manifesto, avaliador separado e referências por view autorais com pendências explícitas. Demonstração simétrica prescrita, sem IA real nem alegação de superioridade. 49 testes novos aprovados também sob Python -O, regressões 37+21+24 aprovadas, validador 3 aprovado. Política automática H, transporte real, revisão semântica independente e decisões do piloto permanecem pendentes. Nenhuma etapa 8, API paga, credencial, instalação, commit/push/PR ou alteração do legado.


### Revisão final da etapa 7 — 25/10/2026

Corrigidos os dois pontos da revisão do coordenador: identificação/view obrigatórias e proveniência H por envelope/contextos/análises efetivamente usadas, inclusive cache sem nova cobrança; limites autorais de custo ≥20000 centavos preservados com unidade/proveniência nas referências geradas e diagnóstico separado de contradição, sem converter limite em valor exato nem incluí-lo no MAE. Gabaritos originais preservados. Demonstração sintética explicitamente restrita a manifesto de teste, com contraprovas simétricas +100/+200/+300 BRL ante mínimo +200. **49 testes etapa 7** aprovados também sob Python -O, **82 regressões** aprovadas e validador 3 aprovado. Integração seletiva com hashes. Inferibilidade B pendente nos casos registrados, revisão semântica independente, política automática H e transporte real continuam pendentes. Entrega da etapa 7 aguarda revisão; **etapas 8–11 não iniciadas**.


## Vigência da transição e entrega — etapa 8, 25/10/2026

O usuário instruiu “Inicie a etapa 8”, após revisar a entrega 7: **etapa 7 aprovada para progressão** e somente etapa 8 autorizada. As pendências históricas de aprovação da etapa 7 ficam superadas para progressão; revisão científica independente continua pendente.

[Etapa 8 — observatório](ETAPA_08_OBSERVATORIO.md) entregue **pendente de revisão do coordenador e usuário**: interface local isolada para inputs, identidade, resultados antes/depois/deltas, grafo causal e rastro por nó, todos os predecessores, restrições/propostas/decisões/evidências e livro de parcelas únicas. Python calcula pela integração H vigente; replay prescrito claramente simulado, B/T sem execução permanecem indisponíveis. Limites/indeterminação/erros preservados; termos contratuais BASE separados das alterações aceitas e tarifa desconhecida. Avaliação sintética da etapa 7 em área segregada, com n/N e referências explícitas. 16 testes novos aprovados também sob Python -O; 131 regressões etapas 4–7 e validador 3 aprovados. Navegador real conferido em normal/parcial/erro, indeterminação/limites/dispensa, evidências, exportação e tela estreita; capturas reais em outputs/etapa8_verificacao. 186 arquivos preexistentes conferidos por hash antes das notas documentais; legado/dados/gabaritos/módulos anteriores preservados. Sem serviços externos, instalação, credenciais, API paga, commit/push/PR ou política automática. **Etapas 9–11 não iniciadas. Não avançar automaticamente.**


## Vigência e entrega da etapa 9 — 26/10/2026

O usuário aprovou a etapa 8 para progressão e autorizou somente a etapa 9 com agente separado, para revisão antes de avançar. [Etapa 9 — ampliação/piloto](ETAPA_09_AMPLIACAO_PILOTO.md): **PARCIAL / PRONTA PARA REVISÃO E DECISÃO**, sem piloto científico real. Acrescentados sete avisos autorais em Estação Nácar, segundo projeto com duas convergências, bifurcação, restrição positiva e incidência de apoio já na base; oito casos Íris preservados. Referências separadas, manuais, sem revisão científica independente.

Piloto de engenharia **OFFLINE/PRESCRITO/SEM LLM REAL**: 15 slots H planejados, 45 views, 12 execuções ok e três parciais por lacuna; B/T normais sem execução. Doze contraprovas separadas preservam falhas e expõem a dependência de suporte da política externa; callback deliberadamente permissivo aceita conteúdo falso apesar de fonte/hash válidos. Runner registra erros/inputs/hashes por slot e continua independentes. Corrigida apenas a lista de tipos de views para admitir responsavel/pertence já normativos, sem propagação contextual. Motor, adaptadores, orquestração, avaliador, UI e dados/gabaritos anteriores preservados.

27 testes novos aprovados também sob Python -O; 147 regressões etapas 4–8 aprovadas e validador 3 aprovado. Sandbox bloqueou inicialmente o setup HTTP local da etapa 8; log preservado e reexecução com porta temporária local passou 16/16. Sem UI nova, credenciais, instalação, API real/paga, commit/push/PR ou escolha de modelo.

Pacote concreto de decisão em `data/desenvolvimento/ampliacao_v1/PROPOSTA_PILOTO_REAL.md`: seleção/normalização estrutural/obrigações/fechamento e fronteira operacional vs suporte semântico propostos, não aprovados nem implementados como política real. Proposta financeira não aprovada: 15 casos × B/H/T × duas repetições = 90 runs, até 300 chamadas sem retry; modelo, cotação e teto monetário pendentes. Diagnóstico real não pronto. Etapa 9 continua pendente de revisão e decisões, **etapas 10/11 não iniciadas**. Não avançar automaticamente.


## Decisões aprovadas e estimativa — continuação em 26/10/2026

O usuário aprovou **preservar as previsões originais sob verificações operacionais e auditar depois o suporte nas fontes, contabilizando erros sem correção manual**. Escolheu **`gpt-6-luna`, `reasoning.effort=high`, Responses API para o experimento**; isso não altera o modelo do agente executor. Essas duas decisões deixam de estar pendentes. As menções anteriores a modelo não escolhido e à alternativa metodológica não aprovada ficam históricas; implementação de transporte/política, seleção/fechamento, tokenização/cache, limites e auditoria ainda é pendente. A decisão não equivale a suporte semântico verificado, autorização irrestrita de propostas ou aprovação financeira.

Estimativa de um lote completo: 15 casos × B/H/T × 2 repetições = 90 execuções individuais, até 300 chamadas sem retry, entrada até 16.000/chamada. Com saída total histórica de 2.000 (raciocínio+resposta): US$0,78 base sem escrita, **US$0,90 conservador com toda entrada como escrita default30m**. Alternativa High de 25.000 de saída total: US$4,23 base sem escrita, **US$4,35 conservador default30m**. Retenção12h é só comparação: US$4,95 com25k. Reserva sugerida US$5 antes de impostos/câmbio, **não aprovada**, sem taxa de câmbio inventada. Consumo esperado não medido; limites reais ainda não implementados. Cache implícito do provedor não se confunde com cache local de respostas.

A proposta original0.1 e seus hashes foram preservados. Duas variantes documentais0.2 registram o modelo escolhido e distinguem2k histórico de25k proposto. Não houve substituição silenciosa do limite nem autorização de lote. Detalhes, preços e fontes oficiais fornecidas pelo coordenador em26/10/2026 estão em `data/desenvolvimento/ampliacao_v1/ESTIMATIVA_CUSTO_CONFIGURACAO.md`.

**Configuração local:** não enviar chave no chat. O runner quantitativo não carrega `.env`, não lê `OPENAI_API_KEY` e não tem transporte real. Somente o caminho legado inspecionado oferece carregamento local de `.env`; isso não habilita o novo experimento. Configure futuramente `OPENAI_API_KEY` no ambiente do processo de execução. Nenhum segredo, `.env` real ou valor de variável foi lido; nenhum arquivo com chave foi criado. Sem chamadas externas/API/modelo, implementação nova, testes de regressão desnecessários, gasto ou início de etapas10/11 nesta continuação. A aritmética documental foi conferida com Decimal.


## Integração e teto aprovados — 26/10/2026

O usuário aprovou o teto agregado **US$5** e **25.000 tokens de saída total por chamada** e autorizou implementar a integração da etapa 9. `gpt-6-luna`, High, Responses API, Standard e TTL 30 m permanecem os parâmetros do experimento. A aprovação financeira já existe; não se pede nova autorização financeira para esse mesmo lote. Não inclui etapas 10/11, serviços adicionais, retries ou outro lote. Propostas anteriores com orçamento não aprovado são históricas.

[Integração da etapa 9](ETAPA_09_INTEGRACAO_REAL.md): transporte Responses/contagem oficial, política H operacional condicional sem fixtures/gabarito, fechamento conferido por nós/cláusulas/obrigações,90 slots B/H/T, ledger persistente/lock/reservas e configuração local segura implementados. Suporte fica **não auditado**, preservando previsões originais e erros para auditoria posterior. Custódia técnica monetária é convenção de deduplicação exposta, não atribuição causal/econômica.

Inferência máxima estimadaUS$4,35; provisão hipotética de contagemUS$0,60, comprometimento máximo internoUS$4,95. Tarifa/gratuidade de `/responses/input_tokens` não está estabelecida nas fontes consultadas; a provisão não é preço comprovado nem prova de teto de fatura desse endpoint. O ledger não libera custo desconhecido, interrompe antes de excesso e não repete slot iniciado na retomada. A revisão técnica precisa incluir essa hipótese e a custódia da política.

26 testes novos de integração e segurança offline aprovados, também sob Python-O;174 regressões das etapas 4–9 aprovadas. Testes exercitaram 90 slots com mocks válidos, não coleta de IA. Nenhuma chave real foi lida/exposta/inventariada; o usuário configura `.env.piloto`0600 pelo Terminal com `python3 -m piloto_real --configurar-chave`, com `PYTHONPATH=TCC_Codigos/src`. `--checar-chave` só informa presença e não testa API. O runner quantitativo agora sabe carregar a variável/arquivo exclusivo no momento de`--rodar`; o legado permanece isolado.

Entrega técnica para revisão do coordenador antes de coletar. O executor **não executou `--rodar`**, não criou ledger de coleta real e gastou **US$0 em API do piloto**. Etapa 9 segue parcial até coleta/auditoria; etapas 10/11 não iniciadas. Guia e comandos exatos em `ETAPA_09_INTEGRACAO_REAL.md`; aprovação versionada em `data/desenvolvimento/ampliacao_v1/lote_aprovado_v03.json`.


## Coleta real parcial e parada diagnóstica — 26/10/2026

O usuário confirmou configuração local e autorizou o lote real com teto agregado US$ 5. Rótulo de chave **informado pelo usuário**: TCC-Impacto-Baseline; não inferido da credencial. A outra chave TCC-Impacto-Grafo-LLM-por-no não foi adicionada. Somente o programa carregou a credencial; nenhum segredo foi lido/exibido/inventariado pelo executor.

O v03 foi preparado/executado uma vez no diretório canônico. A coleta real gerou 13 contagens e 13 inferências marcadas: quatro retornos completos com uso conciliado, oito timeouts e uma interrupção. Por instrução operacional do coordenador durante a coleta, cinco timeouts consecutivos (tentativas 8–12) levaram a SIGINT seguro e parada registrada, preservando a tentativa 13 e suas reservas. Essa guarda foi decisão posterior ao início, não regra pré-registrada do v03. Nenhum deadline, modelo, prompt, dado ou orçamento foi alterado; nenhum slot foi repetido.

**Etapa 9 PARCIAL:** seis registros finais, um slot iniciado sem resultado final e 83 não iniciados, N planejado 30 por condição. Só k_09c2 tem resultados B/H/T em duas repetições: T coincidiu com referência autoral (+2 dias/+R$ 400); B R2 declarou prazo indeterminado e aumento de custo sem magnitude; B R1 teve timeout; H devolveu parcial operacional por timeouts locais. Interseções exatas B/H, B/T e H/T são zero; não há conclusão de superioridade. Suporte semântico/inferibilidade permanecem pendentes; ausentes e timeouts não são acertos nem erros numéricos.

Inferência conhecida US$ 0,007229825; reserva de inferência desconhecida US$ 0,1305; provisão **hipotética** de contagem US$ 0,026. Comprometimento interno US$ 0,163729825; saldo interno US$ 4,836270175. Não é fatura/saldo da conta nem tarifa comprovada do endpoint de contagem; reservas desconhecidas não foram liberadas.

[Resumo parcial](../../outputs/etapa9_coleta_20261026/RESUMO_PARCIAL.md), relatório detalhado, avaliação autoral, contabilidade, parada e snapshot dos originais estão em `outputs/etapa9_coleta_20261026/`. O limite de prazo indeterminado de k_d307 foi preservado explicitamente fora do schema de limites do avaliador v1 na projeção, sem mudar o original/estado ou qualquer previsão.

[Próximo diagnóstico proposto](../../outputs/etapa9_coleta_20261026/PROPOSTA_DIAGNOSTICO_SEGUINTE.md): começar por uma chamada, até duas, somente deadline maior (180 s), mesmos payloads/modelo/prompts/dados e controle do mesmo saldo acumulado; reserva adicional máxima US$ 0,033. **Não executado.** O teto financeiro US$ 5 já está aprovado; o adendo precisa revisão técnica/metodológica, não zeragem do ledger nem nova carteira. Não retomar `--rodar` ou substituir slots antes da revisão. Etapas 10/11 não iniciadas; sem commit/push/PR.


## Diagnóstico de 180 s aprovado e executado — 26/10/2026

O usuário aprovou até duas chamadas diagnósticas, mantendo os demais parâmetros, resultados anteriores e o teto acumulado US$ 5. O adendo foi implementado em pacote separado `diagnostico_etapa9`, testado offline (7 testes, também sob Python -O) e executado exatamente duas vezes: tentativas 14 e 15, uma por slot diagnóstico, sem retries, na mesma carteira. Os payloads enviados são idênticos aos originais 1 e 4; os 90 slots, os seis resultados existentes, as 13 tentativas anteriores e a parada original foram preservados por comparação ao snapshot. O coletor v03 não foi retomado.

B global completou com formato válido em **39,523 s**, com prazo indeterminado e custo direcional. H local completou a resposta em **55,344 s**, mas o validador rejeitou `propostas[0].condicoes[0].predicado`: **Condição fora de catálogo**. O contexto tinha `predicados=[]`, enquanto a resposta usou frases como predicados; valores quantitativos também vieram escalares, embora o contrato exija Conhecimento. JSON, identidades e contexto/hash conferem; a revalidação offline pelo adaptador normal reproduziu a mesma rejeição. Não houve reparo, aplicação ao motor, substituição do timeout original ou composição retrospectiva de H. Suporte semântico permanece não auditado.

Os retornos acima de 30 s favorecem a hipótese de limite temporal restritivo para essas novas tentativas; não provam a causa de todos os timeouts. A orientação do prompt/schema local também precisa ser tornada explícita, especialmente para catálogo vazio e tipos de valor. Esse próximo ajuste foi proposto, **não implementado/executado** nesta entrega. Sem terceira chamada.

Inferência incremental conhecida **US$ 0,005090690**; provisão hipotética adicional de contagem US$ 0,004. Inferência conciliada acumulada US$ 0,012320515; comprometimento interno acumulado **US$ 0,172820515**; saldo interno **US$ 4,827179485**, mantendo as nove reservas desconhecidas anteriores. Não é fatura ou tarifa comprovada de contagem.

[Relatório do diagnóstico](../../outputs/etapa9_diagnostico_180s_20261026/RELATORIO.md), respostas originais, revalidação derivada, contabilidade e testes em `outputs/etapa9_diagnostico_180s_20261026/`. A avaliação dos 90 slots não foi alterada nem recebeu esses diagnósticos. Etapa 9 permanece parcial, entregue para revisão; não iniciar etapas 10/11 ou novas chamadas automaticamente.


## Ajuste de formato local v04 — revisão offline (26/10/2026)

Implementado em pacote separado, sem novas chamadas nem leitura de chave: contrato descritivo explícito para Conhecimento, confirmações e aditivo; predicados literais do catálogo e vazio => condições vazias. Parser e resposta real rejeitada permanecem intactos. 15 testes novos (normal e -O) e 54 regressões passaram. Prompt/payload e hashes mudam; envelope json_object e parâmetros da API permanecem. Novo transporte exige manifesto/slots próprios, recusa slots históricos e não habilita coleta.

[Entrega v04 para revisão](ETAPA_09_AJUSTE_FORMATO_V04.md). Próxima execução depende de protocolo/adendo versionado na mesma carteira e nova contagem oficial do payload. Ledger preservado, comprometimento interno US$ 0,172820515 sob teto US$ 5. Etapa 9 parcial; 10/11 não iniciadas.

Contraprova adicional de cache aprovada: mesmo modelo/configuração/entradas, tipo e geração distintos produzem contexto_hash/chaves distintos; sem reuso legado e com reuso próprio. Evidência em `outputs/etapa9_formato_v04_20261026/cache_contraprova.json`. Apenas esse teste direcionado foi executado; núcleo histórico intacto.


## Coorte real v04 — parada operacional em 26/10/2026

Após autorização humana,90slots novos foram registrados no mesmo SQLite:15casos × B/H/T ×2, mantendo histórico e deadline180s. H≤8chamadas, tempo agregado1500s=8×180+60, sem alterar seleção/política. Cinco testes de integração e dois direcionados de payload/validação passaram.

Executados17/90slots (B5,H6,T6), com46novas chamadas;73slots não iniciados. Parada antecipada registrada em http_indisponivel da call61 (H/k_23d8/R2/n_42be), após contagem5601 e inferência marcada;60,791s na tentativa, sem resposta/usage/status. O código provém do catch amplo do workerHTTP; não permite identificar rede/TLS/JSON ou integração, nem atribuir autenticação/modelo/parâmetro. Não houve replay.

Inferência nova conhecidaUS$0,086682160; duas reservas integrais novasUS$0,033; provisão hipotética de contagemUS$0,092 (incluída parcialmente nessas reservas, sem dupla soma). Comprometimento globalUS$0,380502675; saldo internoUS$4,619497325 sob tetoUS$5. Ledger histórico, chamadas1–15 e arquivos conferidos preservados.

T teve cobertura exata4/30 em prazo e custo eMAE0 nos4pares exatos autorais (duas repetições de dois casos); B/H sem magnitude exata. Interseções numéricas pareadas0/30. Sem conclusão de superioridade; suporte semântico/inferibilidade pendentes.

[Relatório v04 para revisão](../../outputs/etapa9_coorte_v04_20261026/RELATORIO.md), brutos, contabilidade, métricas, snapshots e integridade no mesmo diretório. Opção técnica não ativada de retomar somente73pendentes: até229chamadas novas/290agregadas, reserva máxima globalUS$4,159002675; exige evento/adendo append-only, sem apagar parada ou resultados. A autorização financeira dos90slots/US$5 permanece; decisão técnica cabe ao coordenador. Coleta parada para revisão. Etapa9 parcial;10/11 não iniciadas; sem commit/push/deploy.


## Retomada operacional v04 — nova parada em 26/10/2026

Por decisão operacional do coordenador vinculada à autorização humana dos 90 slots/180s/US$ 5, foi registrado adendo append-only separado e retomada somente a lista dos 73 pendentes, sem atribuir aprovação humana nova. Pacote retomada_v04, mesmo SQLite/lock/caps, paradas próprias, código/adendo vinculados aos novos resultados. Cinco testes offline passaram antes da ativação; telemetria de erro segura acrescenta fase enumerada/classe permitida/errno, sem alterar prompts ou parâmetros HTTP.

A retomada concluiu3 slots com 10 chamadas, somando 20/90 terminados (B7,H7,T6);70não iniciados. Nova parada na call71,H/k_42a9/R1/n_ae50: contagem de 5.281concluída, inferência marcada; RemoteDisconnected na fase de cabeçalho,60,810s na tentativa, sem resposta/statusHTTP/request_id/usage/errno. EOF antes do statusHTTP não identifica quem fechou a conexão ou causa externa; não prova auth/modelo/parâmetro inválido. Reserva integral mantida; não houve retry ou outra liberação. Chamada61 e17 terminados anteriores continuam intactos.

Comprometimento da retomadaUS$ 0,049828660: inferência conhecidaUS$ 0,015328660 +reserva de inferência desconhecidaUS$ 0,0145 +provisão hipotética de contagemUS$ 0,020. Global71 tentativas/300,US$ 0,430331335comprometidos eUS$ 4,569668665de saldo interno sob tetoUS$ 5;12 reservas desconhecidas mantidas. Não é fatura/tarifa comprovada.

Métricas descritivas da coorte v04: T mantém4/30exatos em prazo/custo,MAE0nos4 pares autorais; B/H sem magnitude exata e interseções pareadas0/30. Fases não tratadas como experimento final controlado; sem misturarv03/diagnóstico; suporte semântico/inferibilidade pendentes. [Entrega atual para revisão](../../outputs/etapa9_retomada_v04_20261026/RELATORIO.md), evidência da call71,contabilidade,brutos,snapshot e integridade no diretório. Relatório parcial17 slots preservado em etapa9_coorte_v04_20261026. Coleta novamente parada para revisão técnica. Etapa 9 parcial;10/11 não iniciadas; sem commit/push/deploy.


## R2 SSE — preparação offline para revisão (26/10/2026)

Implementado em pacote separado `retomada_v04_sse`, com runner sob ativação explícita, geração `stream:true`, contagem JSON intacta, parser incremental de Response terminal e deadline total fixo de 180 s. Guardas, carteira, prompts/modelo e contrato local preservados. Adendo final congela 20 resultados e chamadas 1–71, ambas as paradas e lista exatamente 70 pendentes. Projeção: até 219 novas chamadas/290 agregadas, comprometimento máximo US$ 4,043831335 sob teto acumulado US$ 5.

22 testes distintos offline passaram; logs de call72/21 slots são mocks em cópias temporárias. Integridade confirmou carteira real inteira igual ao snapshot R1, 71 tentativas, 20 resultados e 70 não iniciados; nenhuma tabela/ativação R2, chamada paga ou leitura de chave nesta entrega. Streaming não comprova a causa dos fechamentos em 60,8 s. [Entrega offline R2 para revisão](../../outputs/etapa9_sse_r2_offline_20261026/ENTREGA_OFFLINE.md), código/diffs, adendo e integridade disponíveis. Coleta continua parada até liberação técnica do coordenador. Não iniciados serão separados de erros observados do modelo na apresentação. Sem etapas 10/11 ou commit/push/deploy.


## Disparo R2 bloqueado pela revisão automática (26/10/2026)

A liberação técnica do coordenador foi recebida, mas o comando pago não iniciou: a revisão automática considerou que a autorização humana original não cobre claramente SSE/`stream:true` e que a decisão do coordenador não substitui aprovação humana explícita dessa mudança. Nenhum contorno ou retry. Carteira reconferida somente leitura:71tentativas,20terminados,70pendentes,US$0,430331335comprometidos,sem tabelas/ativaçãoR2. Código/adendo revisados intactos. [Registro do bloqueio](../../outputs/etapa9_sse_r2_offline_20261026/BLOQUEIO_EXECUCAO.md). Aguardar aprovação explícita do usuário para SSE;sem etapas10/11.


## Aprovação humana explícita SSE e início do R2 (27/10/2026)

O usuário respondeu literalmente “Autorizo a continuação com streaming” no chat coordenador, para as 70 pendentes com modelo/high, deadline total 180 s e teto acumulado US$ 5. A aprovação foi registrada em arquivo novo, sem reescrever código/adendo/IDs de 26/10. O mesmo comando R2 foi reavaliado e iniciou após a confirmação de hashes e carteira em 71 tentativas/20 resultados. O bloqueio anterior continua como histórico; não houve contorno.

Coleta R2 em andamento, no mesmo SQLite/lock e sob as guardas aprovadas, sem retries/probes ou reexecução dos 20 resultados. Entrega de execução em `outputs/etapa9_sse_r2_offline_20261026/execucao_20261027/`; [aprovação humana](../../outputs/etapa9_sse_r2_offline_20261026/aprovacao_humana_streaming_20261027.json). Relatório final após término ou parada, por fases e consolidado descritivo v04; não iniciados separados de erros observados. Sem etapas 10/11.


## Fechamento da coleta real v04 — 27/10/2026

Coleta encerrada em 90/90, sem pendentes. R2: 70 slots/201 chamadas, todas conciliadas, sem nova parada ou retry. Global: 272 tentativas e US$ 1,206550975 comprometidos sob teto US$ 5. [Entrega final para revisão](../../outputs/etapa9_sse_r2_offline_20261026/execucao_20261027/RELATORIO.md), com fases separadas, denominadores, custos, diagnóstico observado e integridade. Nenhuma previsão/prompt/código foi corrigido após coleta. Recomendações de revisão antes da etapa 10 constam no relatório; etapas 10/11 permanecem não iniciadas.
