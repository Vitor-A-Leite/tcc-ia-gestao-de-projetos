# Etapa 7 — condições baseline e avaliador de impactos

25/10/2026, America/Sao_Paulo. **ENTREGUE, PENDENTE de revisão do coordenador e usuário.** Etapa 6 aprovada para progressão pelo usuário: “Aprovado, pode iniciar a etapa 7 com um agente separado e trazer a entrega para revisarmos antes de avançar.” Somente etapa 7 executada. Etapas 8–11 não iniciadas. Aprovação de software e conferência autoral não equivalem a validação científica independente.

## Arquitetura e fronteiras

Pacotes stdlib novos, sem alterar interfaces anteriores:

- `src/condicoes/views.py`: `montar_views(base, evento, fontes, grafo, *, vinculo)` e `auditar_equivalencia(views)`.
- `src/condicoes/baseline.py`: `Global(transporte, *, modelo, configuracao, timeout_s, repetir_transporte=False, origem).prever(view, *, execucao_id)` e `Simulado(resposta).prever(...)`.
- `src/condicoes/hibrido.py`: `executar_h(base, evento_comum, fontes, estado, evento, view, interpretador, politica, *, vinculo, origem)`.
- `src/avaliacao/execucoes.py`: `validar_manifesto`, `registrar(slot, resultado)`, `normalizar`, `hash_implementacao`.
- `src/avaliacao/metricas.py`: `avaliar(manifesto, registros, referencias, auditorias=())`.
- `src/avaliacao/referencias.py`: preparação autoral por view, sem ler previsões. Somente o pacote avaliador consome referências; os preditores não dependem dele.

Fluxo: inputs originais e grafo vinculado → views inspecionáveis → B/T global ou contrato H existente → resposta original e registro de execução → normalização por manifesto → avaliador com referências separadas. Não há carregamento automático de outputs antigos, respostas prescritas ou referências no runtime de predição. Nenhum transporte concreto, SDK, rede, credencial, chamada paga, modelo científico escolhido, UI ou piloto.

## Views e equivalência

O construtor recebe a base pré-normalizada para conservar dados comuns sem transportar restrições derivadas e metadados do grafo. A seleção é positiva também nas folhas: um dicionário no lugar de texto/número é rejeitado; campos extras aninhados não atravessam a serialização. Textos documentais aprovados são preservados literalmente: esta é uma fronteira de schema/proveniência, não um classificador semântico capaz de detectar gabarito escondido dentro de uma frase autorizada.

| Informação | B | H, união informacional | T |
|---|---|---|---|
| Calendário, moeda, marco, baseline D10/500000 | Comum | Comum | Comum |
| Catálogo, disponibilidade D2, durações, não antes D0, parcelas | Comum | Comum | Comum |
| Quatro documentos comuns e aviso corrente | Literal | Literal | Literal |
| Seis relações, transferência específica e três trechos relacionais | Ausentes | Estruturados | Todos em texto neutro |
| Resultados esperados, família, outro aviso, saídas do motor | Ausentes | Ausentes na view | Ausentes |
| Agenda, interpretação local, política e cálculo | Ausentes | Contrato específico etapas 5/6 | Ausentes |

`vinculo` declara `base_hash`, `grafo_hash`, `versao_base` e `versao_grafo`. Hashes são calculados sobre objetos completos e conferidos. Além do vínculo declarado, `conferir_snapshot` compara identidades, nomes/tipos/fontes das entidades, disponibilidade, durações, restrições contratuais comuns, parcelas, baseline, calendário e passagens das fontes base. Mudar duração, disponibilidade, orçamento, baseline ou texto mantendo IDs é rejeitado, mesmo com hashes recalculados. A correspondência entre as versões pré-normalizada e grafo é declarada pelo chamador; hashes não provam autoria nem equivalência semântica de escopos redigidos de modo diferente. O campo textual de escopo do evento é compartilhado literalmente. A comparação não executa solver.

Endpoints/tipos/FS0, referências e localizadores relacionais são conferidos; transferências devem resolver relação `requer` e restrição existente. A validação integral do DAG/catálogo continua no validador da etapa 3 e no H; o serializador não interpreta impacto. Ordenação por IDs opacos é neutra e não topológica. Campo novo exige ampliar schema/versionar; IDs de caso/família não entram na view (evento tem ID opaco). Não há datas locais calculadas na base atual. Se forem introduzidas futuramente como fatos comuns, sua possibilidade de inferência deverá ser inventariada e preservada nas condições.

Fatos relacionais legítimos comuns **permanecem em B/H/T**: fornecedor fornece cartucho (planejamento L02); nomes como receber cartucho; montagem com lote substituto e condição de aceite (cláusula técnica); apoio vinculado ao marco final; obrigações únicas e aditivos identificados pelo evento. Planejamento L05 menciona existência/exaustividade da ficha relacional, mas não revela seus endpoints. Avisos também podem relacionar fornecedor, cartucho, obrigação e cláusula. Não foram apagados seletivamente. T serializa cada relação com id, origem, destino, tipo, proveniência e lag quando FS, a transferência com operação/atributo/restrição/proveniência e cada fonte exclusiva literal. `auditar_equivalencia` compara hashes dos comuns e reconstrói o texto T integral a partir do H; seis relações e uma transferência, sem poda por caso.

Assimetria principal: B tem menos conhecimento explícito; H também tem decomposição local, múltiplas chamadas, política externa e cálculo. T controla disponibilidade das relações em texto, mas H/T ainda diferem nesses mecanismos. Não é possível atribuir efeito causal exclusivo à representação em grafo. Os descritores operacionais do H (permissões, regras catalogadas, contexto corrente e dispensas) continuam no contrato local, não no prompt global; seus fatos documentais comuns permanecem nas três views.

## Baseline e ResultadoFinal

O prompt `SISTEMA` de `baseline.py` faz a mesma pergunta de variação final de prazo e custo para B/T, sob mesmo marco, moeda, calendário e sinal. Um único request lógico sem ferramentas; uma tentativa de conteúdo. Retry opcional idêntico somente para timeout/falha transitória, sem dicas ou reparos. Modelo/configuração/timeout/origem são obrigatórios, sem definir o protocolo científico final. A origem `transporte_mock` distingue testes de transporte de `simulado` (resposta prescrita) e `llm_transporte_injetado` (declaração de transporte que ainda precisa ser implementado/validado).

Resposta contém identidade de execução/projeto/versão/evento/view, justificativa e seis quantidades no formato ResultadoFinal: fim_base, fim_novo, delta_dias, custo_base, custo_novo, delta_centavos. Cada quantidade tem estado, valor, direção, evidências, lacunas, motivo e unidade explícita. Parser confere campos, inteiros sem bool/fração, unidades, identidade e evidências visíveis. Valores absolutos negativos são inválidos; deltas negativos são permitidos. Exato exige evidências e ausência de lacuna, incluindo zero; direção sem magnitude exige evidência e lacuna; inaplicável exige motivo. Nenhuma evidência existente prova interpretação correta.

O parser **não chama motor, calcula rede, corrige valor nem substitui resposta** por referência. Inconsistências entre base/novo/delta são conservadas; o avaliador pode sinalizar `inconsistencia_aritmetica` por subtração das próprias quantidades da resposta, sem usar grafo nem alterar previsão. O rastro por nó, referências de nós e livro podem ficar vazios, motivo `condicao_sem_motor`. Não há processamento fictício de grafo.

Execução ok/parcial/erro é separada do conhecimento. Resposta inválida, recusa, truncamento, timeout e falha de transporte preservam erro/bruto/tentativas e não produzem delta zero. Consumo guarda chamadas, modelo solicitado/configuração/hash, modelo observado/request_id por tentativa, tokens, custo API e latência ponta a ponta. Qualquer tentativa sem medição torna o total correspondente desconhecido; não imputa zero. Timeout precisa ser cumprido pelo transporte síncrono. Simulado passa pelo mesmo parser, mantém origem explícita e zero chamadas/tokens/custo API; não é execução de IA.

## Integração H e manifesto

`executar_h` confere novamente snapshot e view, a identidade/texto/origem/escopo/lacunas do evento, versão normalizada e suas evidências contra o aviso comum. Só então chama `orquestracao.avaliar` com o interpretador e a política fornecidos. Retém saída, rastro/contextos locais e consumo existentes; acrescenta vínculo da view/snapshot/evento, versão da política e configuração/origem do interpretador. Interpretador explicitamente simulado não pode ser rotulado real. A união informacional H não garante que a política tenha selecionado todos os fatos necessários; contextos efetivos continuam auditáveis no rastro. **Nenhuma política automática de suporte/seleção foi criada**. Sem política externa suficiente o H mantém parcial/revisão, como na etapa 6.

Manifesto `1.0-manifesto`: uso (`teste_prescrito|desenvolvimento|piloto|final`), condições B/H e T opcional, slots de execução com projeto/evento/caso/repetição/condição, versões de projeto/protocolo, hashes de view/snapshot/evento/código/configuração, modelo e origem. `hash_implementacao()` vincula os arquivos Python dos cinco pacotes; a demonstração utiliza esse hash real. Cada caso/repetição deve ter todas as condições declaradas, IDs/slots únicos. Origens diferentes na mesma condição exigem manifestos/relatórios separados. Manifesto não escolhe número de repetições/modelo/amostra/ordem; essas decisões continuam no piloto e congelamento.

`registrar` conserva resultado integral e hash, sem corrigir nada. Normalização valida metadados/identidade/versão/view/configuração/origem/modelo. Em H exige condição H e envelope 1.0-h, verifica hashes efetivos de entrada e proveniência do envelope, dos contextos e de todas as análises usadas no rastro (novas ou cacheadas), sem converter simulado em IA real. Ausente vira erro operacional por slot; duplicado ou divergente fica inválido e anotado. Extras ficam em anomalias com quantidade; não entram ocultamente na amostra prevista. Não há seleção da “melhor resposta”. O N é sempre o número de slots previstos por condição/desfecho. Referência ausente, duplicada ou com versão/view divergente interrompe avaliação explicitamente, para evitar um resultado aparentemente completo.

O manifesto é uma declaração de execução confiável do chamador, não prova independente de que um provedor real foi chamado. Transporte injetável pode ser mock; origem precisa ser registrada honestamente. Dados de custo API e latência são listados separadamente do custo do projeto; simulações não são agregadas com chamadas reais.

## Métricas e denominadores

Por condição e desfecho há N, contagens/taxas de exato (inclui zero), direção, indeterminado, inaplicável, inválido e erro operacional. Formato/unidade válido é diferente de acerto factual e de suporte semântico.

- Cobertura numérica = `n_exatos_validos/N`, mesmo quando valor está errado.
- Erro absoluto = `abs(delta_predito-delta_referencia)`, dias ou centavos. MAE = soma dos erros/n de pares com predição exata válida e verdade exata; registra n/N e seleção. Custo também mostra MAE_BRL = MAE_centavos/100. Sem pares, null.
- Acerto exato exige igualdade no dia/centavo. Reporta n, referências exatas elegíveis e N, conservando inválidos/abstenções/erros como ausência de acerto. Não inventa penalidade ou erro zero.
- Direção compara redução/zero/aumento para verdade exata ou direcional. Respostas exatas e direcionais podem acertar esse eixo. Denominador elegível inclui todos os slots de referência com direção conhecida. Matriz publica estado/direção de referência versus predição, inclusive falhas.
- Pareadas B/H, B/T e H/T apresentam N e interseção numérica por caso/repetição, lista dos pares e MAE na mesma interseção. Cobertura individual está nas métricas. Menor MAE com cobertura distinta não demonstra superioridade global.
- Falsa certeza = predição exata quando referência **por view** permite só direção/indeterminação. Exibe número de contextos auditáveis e N. Estado por view pendente não recebe conclusão inventada.
- Adequação da indeterminação conta abstenção quando referência por view é indeterminada, com elegíveis e N. Erro operacional é classe distinta de indeterminação.
- Zero sustentado exige predição exata zero **e auditoria explícita sustentado**, vinculada a execução, hash da resposta, view e desfecho. Exibe n/N. Citação válida ou acerto numérico não bastam.

Auditoria semântica recebe revisor, justificativa e rubrica sustentado|contradito|insuficiente; sem ela, `nao_auditado`. Auditoria obsoleta fica não vinculada, não desaparece. Ela não reescreve a previsão original. Falsa certeza por estado epistêmico e auditoria da ligação evidência→conclusão são indicadores complementares, não equivalentes. Contagens automáticas não provam qualidade da interpretação.

## Referências por condição e decisões pendentes

`outputs/etapa7_offline_20261025/referencias_por_view.json` contém oito cenários, duplicados apenas para as duas versões de projeto consumidas (16 registros, nunca 16 casos). Mantém verdade autoral, derivação manual, hash da referência original, fontes/localizadores/hashes visíveis por view, hash relacional, hash da view e status autoral pendente de revisão independente. Não lê previsões para preparar esta tabela e não altera gabaritos anteriores. Há campos explícitos de alcance e revisores vazios; autoria desta etapa não é revisão independente.

| Caso | B: prazo / custo | H/T: prazo / custo, união documental |
|---|---|---|
| k_b731 | pendente / pendente | exato 0 / exato 0 |
| k_09c2 | pendente / pendente | exato +2 / exato +40000 |
| k_e168 | exato 0 / exato +30000 | exato 0 / exato +30000 |
| k_547a | pendente / pendente | exato +2 / exato 0 |
| k_a92f | pendente / pendente | exato 0 / exato +15000 |
| k_23d8 | indeterminado / direção aumento | indeterminado / direção aumento |
| k_f04b | pendente / pendente | exato −1 / exato −10000 |
| k_8c65 | pendente / direção aumento | exato +2 / direção aumento |

A anotação autoral B de k_e168 usa preservação da disponibilidade D2, aceite e demais condições: mantém o cronograma e adiciona somente a taxa. k_23d8 usa a cláusula comum que proíbe estimar duração/readequação sem aceite; adicional não negativo sustenta aumento sem total. k_8c65 tem taxa antiga inaplicável e adicional explícito, sem novo preço exato. Os demais B permanecem pendentes: falta de precedências não prova, sozinha, que nenhuma inferência global legítima seja possível a partir do contexto. Não se força indeterminação para favorecer H, nem se copia a verdade completa para B. Rever essa suficiência antes de qualquer experimento. H/T documentais usam a derivação manual existente; suficiência dos contextos locais efetivamente selecionados pelo H requer auditoria própria.

## Reprodução offline

Da raiz do repositório, Python 3.9+, somente biblioteca padrão. `PYTHONDONTWRITEBYTECODE` evita o cache externo do Python da máquina.

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=TCC_Codigos/src
python3 -m unittest discover -s TCC_Codigos/tests/etapa7 -v
python3 -O -m unittest discover -s TCC_Codigos/tests/etapa7 -q
python3 -m condicoes TCC_Codigos/data/desenvolvimento/projeto_minimo_v1/inputs TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/estado_projeto.json TCC_Codigos/outputs/etapa7_offline_20261025/views
python3 -m avaliacao referencias TCC_Codigos/data/desenvolvimento/projeto_minimo_v1 TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/estado_projeto.json TCC_Codigos/outputs/etapa7_offline_20261025/referencias_por_view.json
python3 -m avaliacao.demonstracao TCC_Codigos/outputs/etapa7_offline_20261025/demo
python3 -m avaliacao avaliar TCC_Codigos/outputs/etapa7_offline_20261025/demo/manifesto.json TCC_Codigos/outputs/etapa7_offline_20261025/demo/previsoes_prescritas.json TCC_Codigos/outputs/etapa7_offline_20261025/demo/referencias_sinteticas.json /tmp/etapa7_metricas_reproduzidas.json --auditorias TCC_Codigos/outputs/etapa7_offline_20261025/demo/auditorias_prescritas.json
python3 -m unittest discover -s TCC_Codigos/tests/etapa4 -q
python3 -m unittest discover -s TCC_Codigos/tests/etapa5 -q
python3 -m unittest discover -s TCC_Codigos/tests/etapa6 -q
python3 TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/validar.py
```

49 testes novos aprovados, também Python -O; regressões 37+21+24=82 aprovadas; validador etapa 3 aprovado com seis contraprovas rejeitadas. Cobertura: vazamento aninhado/folhas/outro aviso, fatos relacionais comuns preservados, equivalência e completude T, ordem/IDs variados, divergências de dados/fontes/snapshot, baseline sem motor, seis quantidades/negativos/unidades/evidências/identidade, preservação de inconsistência, recusa/truncamento/JSON inválido/timeout/retry/falhas, consumo observado, manifesto/ausentes/duplicatas/extras/versões, MAE/denominadores/redução/zero/direção/indeterminação/falsa certeza, auditoria pendente/obsoleta, referência obsoleta, integração com H simulado real da etapa 6 e preservação da origem. Sem reexecutar/corrigir legado.

Demonstração `demo/RELATORIO.md` e `metricas.json`: **mesmas respostas sintéticas prescritas nas três condições**, oito contraprovas, zero chamadas reais. N=8 em cada desfecho/condição; três exatos válidos, um direção, dois indeterminados, um inválido, um erro. Cobertura 3/8; pares numéricos 2/8; MAE 1,5 dia / 150 centavos (R$1,50); um acerto exato entre cinco referências exatas, um zero sustentado por auditoria prescrita, uma falsa certeza, uma abstenção apropriada entre duas referências indeterminadas. Interseção pareada 2/8. Teste de cálculo de métricas, **não avaliação de IA nem placar de superioridade**. Os oito avisos autorais não foram usados para fabricar respostas comparativas B/H/T.

## Integridade e revisão

90 arquivos anteriores (dados, docs, módulos, testes e outputs etapas 4/6) conferidos por SHA256 entre worktree e principal antes da implementação. Integração seletiva dos novos pacotes, testes, views/referências/demo e deste documento; somente STATUS/PLANO_MESTRE existentes recebem nota de vigência. Destinos existentes são reconferidos contra os hashes iniciais imediatamente antes da cópia, recusando mudanças concorrentes. Registro de integridade acompanha outputs. Dados/gabaritos anteriores, módulos/testes anteriores e outputs anteriores preservados por hash. Sem substituir diretórios inteiros, instalação, credenciais, chamada paga, commit/push/PR.

Para revisão antes da próxima etapa: suficiência autoral das referências por view (especialmente B pendente), auditoria humana independente, política automática H de seleção/fechamento/suporte, transporte real e protocolo/modelo/orçamento/repetições futuros. A entrega prepara comparação reproduzível offline e registra limitações; não demonstra superioridade e não congela o experimento. **Etapa 7 não aprovada; etapas 8–11 não iniciadas.**


## Revisão final do coordenador — proveniência H e limites

Os dois pontos concretos foram confirmados na entrega anterior e corrigidos somente nas fronteiras da etapa 7. Nenhum módulo/dado/gabarito das etapas anteriores foi alterado.

`executar_h` agora identifica explicitamente `condicao=H`, `contrato_h=1.0-h` e conserva a condição original em `condicao_orquestracao=orquestracao_v1`. `normalizar` exige `view_hash` presente e igual ao manifesto, além da condição correta para **todas** as condições. Um resultado B não pode preencher um slot H, mesmo com as demais identidades ajustadas. Alterar apenas o rótulo para H também não supre o envelope específico.

O contrato real de orquestração conserva cada análise em `rastro_orquestracao[].analise`, incluindo `processamento=reuso_cache`. Portanto a conferência H percorre essas análises e verifica execução/evento/nó, hash e identidade do contexto, snapshot original, modelo/configuração do contexto e origem/modelo/configuração/hash de cada análise usada. Também confere envelope H e observações novas quando presentes. A contagem de análises deve corresponder ao rastro. Isso não depende de haver chamada nova: um reuso integral com três análises no cache e `observacoes_novas=[]` passa, mantendo chamadas/tokens novos zero. Nenhum consumo é recalculado ou cobrado pelo normalizador.

Há duas particularidades explícitas do contrato anterior: Simulado local registra modelo null/configuração vazia/config_hash null; o envelope H vincula a configuração vazia por seu hash canônico. Essa equivalência só é permitida para origem simulada. O adaptador local da etapa 5 usa a origem `llm_transporte_injetado` mesmo quando recebe um transporte mock; o H registra `transporte_mock` por declaração explícita do chamador e aceita essa origem local sob a categoria mock. Isso não autoriza análise Simulado como mock/IA real, nem é prova independente de chamada ao provedor. Modelo observado pelo transporte continua preservado separado do modelo solicitado; o manifesto vincula o solicitado.

A demonstração sintética tem envelope H explicitamente `prescrito_sem_execucao`, rastro vazio, zero análises/chamadas. Essa variante só é aceita em manifesto `uso=teste_prescrito`, origem simulada e política de demonstração explícita; é inválida em desenvolvimento/piloto/final. Os testes de cache usam o `executar_h` verdadeiro, política/interpretador prescritos e um transporte mock explicitamente rotulado, não esse envelope sintético. Falhas e slots inválidos continuam no N.

Os gabaritos originais de k_23d8 e k_8c65 **não possuem limite estruturado**: a derivação textual declara delta ≥20000 centavos e custo novo ≥520000. `referencias.py` registra uma transcrição autoral explícita somente no avaliador, vinculada ao hash integral do gabarito, derivação literal e fontes. A presença da expressão original é conferida para não aplicar silenciosamente a transcrição após mudança da derivação. Não é extração geral por linguagem natural nem nova revisão independente.

Representação gerada para custo: `estado=direcao`, `valor=null`, `direcao=aumento`, `unidade=BRL_centavo`, `limites={inferior:20000, superior:null, unidade:BRL_centavo, grandeza:delta, proveniencia:{tipo, referencia_origem_hash, derivacao, fonte_ids}}`. O custo novo mínimo 520000 permanece na derivação preservada; o limite estruturado é explicitamente do **delta** para não misturar grandezas. As views com estado direcional autoral recebem o mesmo limite e somente os IDs de fontes visíveis. As pendências B permanecem pendentes; nenhuma desigualdade vira igualdade.

`avaliacao/limites.py` valida inteiros sem bool/fração/texto, unidade/grandeza, ao menos uma fronteira, ordem das fronteiras, coerência com valor exato/direção e proveniência obrigatória. Referência direcional com limites iguais exige revisão em vez de conversão automática para exato. Unidade/limite/proveniência inválidos interrompem a avaliação explicitamente. Referências exatas que contradigam seu próprio limite são rejeitadas.

O relatório acrescenta `contradicao_limite` contra a verdade autoral e `contradicao_limite_visivel` contra o limite da view, separadamente de acerto, MAE e auditoria semântica. Por desfecho mostra contradições/comparáveis/N; comparável exige predição exata válida e limite conhecido. Detalhes marcam `contradiz`, `compativel_sem_demonstrar_exatidao` ou `nao_comparavel`. Essa compatibilidade não é acerto exato, sustentação semântica ou justificativa para falsa certeza. MAE continua restrito a pares exatos.

A demonstração reproduzível inclui `demo/limite_10000.json`, `limite_20000.json` e `limite_30000.json`, com manifesto, respostas, referências, auditorias prescritas e métricas. A referência direcional mínima 20000 recebe predição exata 10000, 20000 ou 30000, igualmente em B/H/T. O primeiro contradiz o limite (1/1 comparável, N=8); os outros são compatíveis (0/1) sem exatidão sustentada. Nos três arquivos MAE permanece 150 centavos sobre os mesmos 2/8 pares exatos e o caso direcional não entra no MAE. A falsa certeza por view permanece explícita. Não é experimento nem comparação de IA.

Validação final: **49 testes da etapa 7**, incluindo 14 novos testes de revisão com subcasos, aprovados também sob Python -O. Regressões das etapas 4/5/6: **37+21+24=82** aprovadas; validador da etapa 3 aprovado. A revisão não altera a orquestração nem seus critérios de suporte: confere sua proveniência efetivamente registrada. Os testes cobrem reuso integral sem novos tokens/chamadas, rejeição de B como H, view ausente/divergente, envelope/análises cacheadas com origem/modelo/configuração divergentes, rastro/contagem ausentes, desigualdades, proveniência/unidades/valores inválidos e separação do MAE.

Antes da revisão, 136 arquivos da entrega e etapas anteriores foram capturados iguais entre worktree e principal. A nova integração seletiva verifica os destinos contra essa captura, copia só os arquivos alterados/novos da etapa 7 e suas notas de status, e registra `integridade_revisao_final.json`. O registro da integração inicial permanece preservado. Sem alteração de gabaritos, fonte original, motor, adaptador local, orquestração ou outputs anteriores às etapas 7. Etapa 7 continua pendente de revisão; etapas 8–11 não iniciadas.
