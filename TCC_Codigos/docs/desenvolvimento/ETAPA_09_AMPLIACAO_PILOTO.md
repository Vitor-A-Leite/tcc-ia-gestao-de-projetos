# Etapa 9 — ampliação e piloto de engenharia

26/10/2026, America/Sao_Paulo. **PARCIAL / PRONTA PARA REVISÃO E DECISÃO.** Ampliação e piloto de engenharia entregues; piloto científico com IA real não executado/não habilitado. Autorização humana: “Aprovado, pode iniciar a etapa 9 com um agente separado e trazer a entrega para revisarmos antes de avançar.” Etapa8 aprovada para progressão. Um implementador nesta etapa. **Etapas10/11 não iniciadas.** Revisão autoral, aprovação de software e autoria por outro agente não equivalem a independência científica.

## Critérios e escopo

Leitura dos documentos vigentes de especificação, plano, status e entregas6–8. Nenhum AGENTS.md aplicável encontrado nos diretórios ancestrais ou em TCC_Codigos. Critérios extraídos: diversidade de mecanismos com derivação manual e fontes; separar inputs/referências/aviso corrente; preservar conhecimento/executabilidade; registrar erros com denominadores; ajustar somente desenvolvimento; avaliar prontidão real sem oráculo. Mantidos D0, evento único, dias corridos inteiros [início, fim), BRL/centavos, DAG FS0, máximo de predecessores/restrições, obrigações únicas e incidência nova menos base. Sem API, credenciais, instalação, mudança de UI ou modelo científico escolhido.

A matriz anterior à execução está em `data/desenvolvimento/ampliacao_v1/COBERTURA.md`. Os oito casos Íris foram preservados; o material legado não foi promovido a novos casos quantitativos. Acrescentados **sete avisos em um novo projeto fictício**, escolhido por mecanismos ausentes em cenários documentais: Estação Nácar,8 entidades (6 atividades, marco, pessoa),8 relações (7 FS+1 responsável),7 arcos causais, duas convergências, uma bifurcação e piso contratual positivo. Não há transferência de componente neste projeto; Íris continua cobrindo esse mecanismo e aceite de laudo.

## Dados e referências

Pacote `ampliacao_v1/`: `inputs/{base,estado_projeto,cenarios,fontes}.json`,7 fixtures em `fixtures_prescritas/`, `catalogo.json`, referências autorais isoladas em `referencias/gabaritos.json`, matriz e pacote real. IDs de entidade/evento/caso opacos; caso/família/derivação não atravessam views/contextos. Dois avisos de crédito formam uma família para evitar independência fictícia. Fontes são fictícias, literais, versionadas, com localizadores; aviso atual isolado em cada run.

Nácar base manual: preparar D0–2; usinar D0–4; integrar max(2,4)=D4–7; ensaio D7–9; dossiê max(D8, D7)=D8–11; inspecionar max(9,11)=D11–12; marcoD12. Seis parcelas fixas somam100000 centavos; apoio fixo50000+extensão já prevista15000 (2×7500)=65000; total165000 (R$1.650). Taxa R$75/dia além de10 dias, sem crédito automático. Marco cobre todas as atividades.

| Caso novo | Mecanismo | Delta prazo manual | Delta custo manual |
|---|---|---:|---:|
| k_6d82 | Não antes do dossiê D8→D10; demais restrições/FS preservadas | +2 dias | +R$150 |
| k_0ca7 | Evento altera preparar para6 e usinar para7; duas junções e bifurcação | +2 | +R$150 |
| k_98f3 | Dossiê3→1 dia, sem crédito | −2 | R$0 |
| k_42a9 | Mesma antecipação com aditivo expresso de crédito da extensão | −2 | −R$150 |
| k_b5e1 | Uma certificação de R$123,45 mencionada nos dois ramos | 0 | +R$123,45 uma única vez |
| k_d307 | Usinagem com duração desconhecida ≥0; cobrança únicaR$25 | Indeterminado, delta≥0 | Aumento≥R$25; sem total exato |
| k_a064 | Anotação administrativa de pessoa; quantitativos expressamente preservados | 0 | R$0 |

As derivações e limites foram escritos antes das chamadas ao motor, com fontes, autoria e revisão independente pendente. Não são gabaritos científicos validados; inferibilidade por view de todos os novos avisos fica pendente. Nenhum ajuste por conveniência aos resultados. No caso desconhecido, não converter limite≥0 em direção zero/aumento estrito nem a cobrança mínima em custo total. No de crédito, a incidência base existente impede contar extensão inteira como delta.

## Implementação e execução efetiva

Novo pacote stdlib `src/piloto_engenharia/`: integração explícita `executar_prescrito`, construção de views, predição sem leitura de referências; runner `lote.py` fixa slots antes de executar, registra hashes dos bytes lidos e falhas por slot, continua independentes; catálogo global inválido é erro de lote sem N completo inventado. B/T normais não recebem respostas prescritas nem cópia de H. As contraprovas têm12 slots próprios e fase isolada. `prontidao.py` calcula tetos e diagnostica pendências; não é transporte/launcher nem mecanismo de autorização humana.

**Única alteração em módulo preexistente:** `condicoes/views.py` aceita `responsavel`/`pertence`, já previstos no v1 e no motor. O primeiro caso Nácar revelou rejeição indevida na serialização. A correção não cria arcos de propagação contextual; teste específico inclui ambos os tipos, ausência causal e rejeição de tipo inventado. Motor, adaptadores, orquestração, avaliador, UI, dados/gabaritos e outputs anteriores preservados.

Lote vigente em `outputs/etapa9_offline_20261026/lote_consolidado/`: **15 runs H OFFLINE/PRESCRITOS/SEM LLM REAL**,45 views,12 execuçõesok e3 parciais por lacuna (k_23d8, k_8c65, k_d307). Prazo13 exatos/15 e2 indeterminados/15; custo12 exatos/15 e3 direcionais/15. B/T normais:0 execuções. Essas são contagens de saída prescrita, não acurácia/cobertura de IA nem MAE científico. Os sete novos avisos foram comparados em teste às referências autorais, sem juiz independente.

Contraprovas separadas: **N12=H8+B2+T2**. H/orquestração:5 parciais,2 erros,1 ok sob callback deliberadamente falso; globais mock:4 erros. API real0. A resposta sem suporte autorizada pelo callback permissivo produz +6 dias/+R$450 indevidos, ainda com fonte/hash válidos. Essa limitação permanece declarada; não se implementou aceite automático semântico. JSON inválido/timeout/contexto obsoleto/unidade/ciclo/limites/fechamento ausente preservam erro ou parcial, sem zero fictício. `RELATORIO_ERROS.md` detalha categorias, correções, limitações e proveniência. Rodadas `lote/` e `lote_final/` são exploratória/intermediária preservadas, não novos cenários ou repetições científicas.

## Prontidão real e decisões revisáveis

Pacote concreto em `data/desenvolvimento/ampliacao_v1/PROPOSTA_PILOTO_REAL.md` e `proposta_lote_real.json`; diagnóstico durável `outputs/etapa9_offline_20261026/prontidao.json` retorna **pronto_para_execucao=false**. Faltam transporte concreto, piso de orçamento/reserva de tokens, modelo/configuração, cotação e orçamento, política H sem oráculo, referências/inferibilidade revisadas e auditoria. Não basta trocar Simulado por LLM.

A proposta detalha seleção determinística conservadora de nós/fontes, normalização estrutural dos inputs comuns, identidade explícita de obrigação, fechamento por cobertura de catálogo e a distinção entre autorização operacional e suporte semântico. Normalização estrutural **não usa chamada LLM adicional** e não generaliza a relato livre sem IDs/obrigações resolvidos. Um normalizador LLM futuro mudaria custo e disponibilidade de informação, exigindo outra decisão.

Decisão metodológica concreta: permitir previsão condicional original sob critérios operacionais fixos, com suporte auditado posteriormente, ou restringir aplicação a operações decidíveis por regras semânticas previamente revisadas. A primeira exige versionar a fronteira; a segunda reduz cobertura. Nenhuma foi aprovada/implementada nesta entrega. Não usar `resolver=True` nem aceitação extraída do gabarito, nem correção humana seletiva por run. O pacote separa decisões humanas de tarefas de código necessárias antes de solicitar autorização do lote real.

Proposta **não aprovada**:15 casos×3 condições×2 repetições=90 runs; H≤8 análises/run; B/T1global/run;≤300 chamadas lógicas/tentativas com0retry. Tetos hipotéticos16000entrada/2000 saída:≤4,8M/0,6M tokens. CustoAPI máximo emBRL=`4,8×preço_entrada_por_milhão+0,6×preço_saída_por_milhão`; valor numérico fica desconhecido até modelo/cotação/câmbio/teto aprovados. Os limites ainda não são impostos por transporte real. Preços hipotéticos em teste não são cotação. Mesmo modelo/configuração por condição, ordem balanceada proposta e logs originais precisam ser revisados antes da coleta.

A comparação futura continua B/H de sistemas completos com assimetria de informação. T controla acesso às relações em texto; H/T ainda diferem em decomposição, chamadas, cálculo e política. Não atribuir exclusivamente ao grafo diferenças futuras. Não há placar artificial próH.

## Validação e comandos

Da raiz do projeto:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9 -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -O -m unittest discover -s TCC_Codigos/tests/etapa9 -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -m piloto_engenharia --dados TCC_Codigos/data/desenvolvimento --saida /tmp/tcc_etapa9_nova_rodada
```

A saída deve ser diretório novo; runner recusa sobrescrever. **27 testes novos aprovados**, também sobPython-O. Cobrem contas manuais, duas convergências, restrição positiva, incidência base/crédito, centavos, deduplicação, limites, lacunas, contextualidade, IDs opacos, isolamento semI/O, vigência/views, contraprovas, slots e continuidade, hashes, catálogo inválido, fase de falhas isolada, diagnóstico conservador e estimativa. Não se chama rede/modelo.

Regressões: **37etapa4+21etapa5+24etapa6+49etapa7+16etapa8=147 aprovadas**. Validador3 aprovado, seis contraprovas rejeitadas. A primeira etapa 8 dentro do sandbox teve13testes aprovados e erro no setupHTTP por bind proibido; reexecução com permissão de porta temporária exclusivamente127.0.0.1 passou16/16. Logs de ambas preservados. UI não foi modificada; não houve navegador novo nem interrupção de servidor anterior. Legado não reexecutado/corrigido.

## Integridade e entrega para revisão

Captura inicial de337arquivos em `integridade_inicial.json`; conferência anterior às atualizações documentais detectou somente a correção intencional deviews. STATUS/PLANO_MESTRE conferidos novamente antes de editar. `integridade_final.json` preserva hashes anteriores, exceções previstas e inventário final da entrega; hash vincula conteúdo, não suporte semântico. Sem reset, limpeza, cópia de diretórios anteriores, commit, push, PR, deploy, credenciais ou gastoAPI.

Revisar matriz/dados/derivações, achado de serialização, robustez do runner e pacote metodológico/financeiro. **Etapa9 permanece parcial para IA real e pendente de revisão desta entrega. Etapas10/11 não iniciadas.** Não avançar automaticamente nem tratar aprovação local como congelamento científico.


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
