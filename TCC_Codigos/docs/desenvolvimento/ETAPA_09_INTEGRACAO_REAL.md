# Etapa 9 — integração Responses e controles do lote aprovado

## Resumo vigente — 27/10/2026

**Piloto real v04: coleta encerrada em 90/90 slots, entregue para revisão.** São 15 casos, B/H/T e duas repetições; 30 resultados por condição e nenhum não iniciado. O R2 SSE executou as 70 pendentes com aprovação humana explícita, em 201 chamadas conciliadas, sem retry ou nova parada. As fases anteriores e as 20 saídas/chamadas 1–71 foram preservadas.

- Orçamento global: 272 tentativas; US$ 1,206550975 comprometidos e US$ 3,793449025 de saldo interno sob teto US$ 5. Inferência conhecida US$ 0,488550975; reserva de inferência desconhecida US$ 0,174; provisão hipotética de contagem US$ 0,544. Não é fatura.
- Cobertura exata prazo/custo: B 5/30 e 7/30; H 2/30 e 2/30; T 21/30 e 22/30. MAE zero somente nos pares exatos elegíveis; custo T tem 21 pares, não 22 acertos. H exato corresponde apenas ao caso k_a064 de impacto zero, em duas repetições. Sem superioridade científica inferida.
- Próxima ação: revisar baixa cobertura H, rejeições de formato/contrato, falsa precisão de T/k_d307 e referências/inferibilidade antes de decidir sobre etapas 10/11. Suporte semântico não auditado. Sem novas chamadas ou correções automáticas.
- [Relatório atual e evidências](../../outputs/etapa9_sse_r2_offline_20261026/execucao_20261027/RELATORIO.md). As seções abaixo preservam o histórico; este resumo rege o estado vigente. Etapas 10/11 não iniciadas.

## Registro histórico desde 26/10/2026

**Vigência posterior:** a coleta v03 foi iniciada e interrompida por parada diagnóstica autorizada. Não retomar `--rodar`; consulte o [resumo parcial](../../outputs/etapa9_coleta_20261026/RESUMO_PARCIAL.md). A descrição inicial abaixo é histórica; a nota final registra os resultados.

26/10/2026, America/Sao_Paulo. Continuação autorizada da etapa 9. **Entrega técnica para revisão; coleta real e auditoria ainda não executadas. Etapas 10/11 não iniciadas.** Este registro supera as descrições históricas de “sem transporte implementado” na entrega offline, sem promover aquela execução prescrita a IA real.

## Aprovação e escopo implementado

Autorização humana: “Aprovo o limite de US$5 e os 25.000 tokens. Pode continuar a etapa 9 com o agente separado, implementar a integração e os controles de gasto e me orientar a configurar a chave de API localmente.” Mantidos `gpt-6-luna`, High, Responses API; previsão original condicional sob validação operacional e auditoria semântica posterior, sem correção manual seletiva. Esta escolha é do modelo do experimento, não do agente executor.

`data/desenvolvimento/ampliacao_v1/lote_aprovado_v03.json` vincula aprovação, modelo, política, limites, moeda e a pendência de tarifa da contagem. Propostas 0.1/0.2 e outputs anteriores foram preservados. Lote único:15 avisos conhecidos, B/H/T,2 repetições,90 slots; B 30 inferências, T 30, Haté 240. Máximo 300 tentativas de inferência, até 300 HTTP de contagem adicionais; zero retry, sem fallback, busca, ferramentas ou serviços pagos adicionais. Não gerar “lotes de teste real” fora desse mesmo teto. Os testes desta entrega usam mocks e não gastaramAPI.

## Componentes

Novo pacote `src/piloto_real/`, stdlib, sem dependências instaladas:

- `chave.py`: configurador TTY/getpass, entrada oculta, `.env.piloto` exclusivo na raiz,0600, sem sobrescrever arquivo; recusa symlink/permissões inseguras. Verificação informa presença de variável ou arquivo seguro sem ler seu conteúdo e sem validarAPI. O carregamento efetivo ocorre só quando o usuário inicia `--rodar`: ambiente `OPENAI_API_KEY` tem precedência sobre o arquivo exclusivo. `.env` legado não é lido.
- `transporte.py`: HTTPS exclusivamente `api.openai.com/v1/responses` e `/input_tokens`, sem SDK/proxy/redirect/retry. Processo HTTP terminável impõe deadline incluindo DNS/TLS/leitura. Request com `model=gpt-6-luna`, `reasoning.effort=high`, `max_output_tokens=25000`, `service_tier=default`, `prompt_cache_options.ttl=30m`, `tools=[]`, `store=false`, `truncation=disabled`. Não envia `previous_response_id`, ferramentas ou contexto de outros runs.
- `ledger.py`: SQLite ACID/FULL e lock exclusivo do lote, reserva persistida antes de cada tentativa de contagem/envio; limita tentativas globais e por slot. Custo em inteiros nanoUSD, sem converterUSD em custo de projeto ou inventarBRL.
- `politica.py`: normalização estrutural e seleção conservadora, autorização operacional condicional, inventário de obrigações e fechamento conferido ao final; não lê fixtures, gabaritos ou outputs.
- `inputs.py`: lista positiva dos dois pacotes/15 avisos; hashes dos bytes efetivamente lidos, views e vínculo, versões e fontes correntes. Qualquer falha estrutural na preparação bloqueia a coleta antes de rede; não se fabrica amostra completa sem catálogo/snapshot válidos.
- `runner.py` e `__main__.py`: plano e manifesto de 90 slots anteriores à coleta, seis permutações balanceadas de B/H/T por caso/repetição, pareamento, identidade, configurações e hashes do código/inputs/aprovação. Respostas preservadas por slot; falhas não retiram slots do N. Sem consulta ao avaliador/gabarito para decidir proposta ou corrigir previsão.

Única mudança em módulo anterior nesta continuação: `orquestracao/__init__.py` ganha um caminho opcional condicional, usado apenas pela política versionada nova. O padrão antigo continua revisão semântica externa. O caminho novo confere `verificar_fechamento()` antes da consolidação, distingue autorização operacional de suporte e marca resultado/decisões como `condicional_original`/`nao_auditado`. Fórmulas de prazo/custo, parsers, baseline e avaliador não foram alterados. Regressões conferem o padrão anterior.

## Política H implementada, sem oráculo

Evento comum preservado literalmente e vinculado a fonte atual; D 0/IDs/versões devem resolver. A versão do snapshot é normalizada estruturalmente com vínculo registrado. Não há LLM adicional para identificar entidades; relatos livres sem IDs resolvidos ficam fora do escopo e não recebem alvo inventado. Não há `expected_*`, classificação do caso, família ou resposta final nos contextos.

Todos os nós do snapshot são selecionados:7 Íris/8 Nácar, até 8 análises locais. Transferências e FS continuam no solver. Cada contexto recebe nó/atributos, cláusulas catalogadas, relações incidentes, fontes comuns e aviso atual, mais entradas causais correntes do runtime. A granularidade de uma passagem documental pode expor mais de uma relação legítima; não se corta texto para esconder fatos. O H paga essa seleção conservadora; nenhuma poda por resposta esperada ou igualdade prematura de datas.

Predicados disponibilizados por regra são identificadores de aplicabilidade: o modelo declara interpretação/condição, não recebe um booleano autoral de aceite. IDs de efeito canônico são fornecidos pelo adaptador; não se exige que o modelo calcule SHA. O prompt local suplementar explica prefixo de IDs de propostas únicos por nó, resolução das cláusulas obrigatórias e uso de lacunas. Não há reparo de JSON/conteúdo nem dica após erro.

**Obrigações e custódia:** extraem-se somente IDs monetários literais do aviso. Um novoID literal é entregue a um único nó de custódia técnica: primeiroID explicitamente mencionado, preferindo atividade/componente/marco, desempate lexicográfico. Isso é convenção operacional de deduplicação e serialização, **não atribuição causal, econômica ou prova de quem cobra/paga**. Ela resolve avisos Íris que mencionam cartucho/fornecedor mas não explicitam proprietário temporal da parcela; é uma escolha de implementação visível para revisão do coordenador. O registro expõe critério, nó e IDs. A interpretação de “adicional/incluído” e montante continua sendo do modelo e auditável. Os fatos originais do aviso permanecem disponíveis nas três condições.

Lacuna de readequação catalogada recebeID técnico derivado deevento/regra/atributo, com prefixo`lacuna_`; só permite `registrar_lacuna_custo`, nunca criar cobrança exata. Não é obrigação comercial nova conhecida. O modelo não inventa IDs. Substituição de parcela temporal direta continua proibida; alteração temporal passa pela regra catalogada. IDs compartilhados são reconciliados no ledger de projeto existente.

**Fechamento não é um True sem conferência:** o booleano de entrada indica intenção de cobrir o catálogo. Ao final, são exigidos todos os nós com análise operacional válida, operações que resolvam duração/readequação de cada cláusula local e reconciliação de todos os novosIDs monetários explícitos. Falha, nó omitido, limite ou obrigação não tratada deixa parcial; contraprovas demonstram isso. `registro_operacional.fechamento_final` conserva nós exigidos/vistos, obrigações exigidas/reconciliadas e pendências. Fechamento completo é **operacional condicional**, não garantia de que o modelo compreendeu todos os efeitos implícitos no texto. Omissões semânticas dentro de uma resposta estruturalmente completa são erros possíveis a auditar; não são silenciosamente corrigidas.

A autorização repete validação de schema/identidade/permissões, condições declaradas confirmadas, regras, operações e restrições de origem/obrigações. Não é `resolver=lambda:True` nem julgamento semântico. Um teste injeta duração 9 para fonte que diz 1: o H conserva +6 dias/+45000 centavos, sem ajustar para a referência autoral, e registra suporte não auditado. Esse é o comportamento metodológico aprovado: contabilizar depois a interpretação errada, distinguindo-a de falha de formato. Não há alegação de suporte sustentado por mera citação/hash.

## Tokens, moeda e medição

A contagem usa [o endpoint oficial](https://developers.openai.com/api/docs/guides/token-counting), com os mesmos `model/input/reasoning/text` que serão usados na inferência. `tools=[]`, sem conversa anterior; não há esquema de saída diferente entre contagem e geração. Só envia inferência após contagem oficial inteira≤16000. Proteção local de 100.000 bytes impede payload exagerado, mas **não é uma estimativa de tokens nem fundamenta a garantia de entrada**. Erro/contagem indisponível não libera inferência. Se vier>16000, registra inadequação ao escopo/hipótese e para novas tentativas do lote, mantendo slots e reservas; não trunca documentos seletivamente.

Os 25.000 tokens são o total gerado, raciocínio+resposta, conforme [guia oficial de raciocínio](https://developers.openai.com/api/docs/guides/reasoning). `incomplete`/recusa preservam bruto e falha original, inclusive uso; não se tenta nova resposta. Deadline 30 s inclui contagem+inferência de cada chamada lógica; H tem 300 s de parede, máximo 8 análises, conferidos entre chamadas. Uma respostaHigh pode ultrapassar 30 s e falhar; isso é limite operacional registrado, não garantia de completar 25 k.

Preços [Standard consultados](https://developers.openai.com/api/docs/pricing): entrada 0,10 USD/M, saída 0,50 USD/M, cache lido 0,01 USD/M, escrita 30 m 0,125 USD/M. Reconciliação usa categorias disjuntas: entrada ordinária=`input_tokens-cached_tokens-cache_write_tokens`; leituras e escritas não se somam novamente. Raciocínio já está em`output_tokens` e não é cobrado duas vezes. TTL 12 h no uso observado é desvio, não opção automática. [A documentação de caching](https://developers.openai.com/api/docs/guides/prompt-caching) estabelece os campos de escrita porTTL e a cobrança não aditiva.

Eco`prompt_cache_options`/`service_tier` é opcional; sua ausência não transforma previsão válida em erro. A configuração solicitada fica no request persistido. Uso suficiente permite conciliação sem exigir eco inexistente. Modelo solicitado/observado ficam separados: a página oficial do[gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna) consultada lista apenas esse identificador de snapshot; não foi inventada allowlist de nomes com prefixo. Um nome/tier/TTL observado divergente preserva a resposta recebida, mantém reserva e bloqueia novas tentativas para revisão, sem substituir modelo. Medição ausente/incoerente mantém reserva e não apaga conteúdo; a contabilidade permanece incerta. Divergência explícita ou uso além dos limites interrompe novas tentativas.

`custo_api_centavos` dos contratos anteriores fica null: **não é BRL calculado a partir de USD**. Uso original e custo de inferência em nanoUSD ficam no ledger/metadados; custo de projeto continua em centavos BRL. Não há câmbio, impostos ou serviços extras na estimativa.

## Orçamento persistente e limites da provisão de contagem

Cada tentativa reserva antes da contagem **US$0,0165**:US$0,0145 para inferência máxima(16 k× 0,125/M+25 k× 0,50/M) eUS$0,002 de provisão de contagem.300 reservas integrais somamUS$4,95, dentro do teto agregadoUS$5. A cada nova tentativa, transação confere saldo, contador global 300 e limite por slot(B/T 1, H 8). Lock do lote impede processos concorrentes; o CLI usa uma única pasta canônica. Não oferece argumento para criar outro orçamento ou repetir lote por engano. Não é proteção contra edição manual/cópia do ledger por um operador.

**A provisão de contagem é hipótese contábil, não tarifa publicada.** Não foi localizada declaração de preço/gratuidade do endpoint. OsUS$0,60 totais consideram hipoteticamente 300 contagens de 16 k a 0,125 USD/M; não se afirma que o endpoint cobre isso. A requisição que retornar>16 k invalida essa hipótese para si; fica reservada integralmente, sem inferência nem continuação cega. O código garante o teto do comprometimento interno nas tarifas/hipóteses registradas, **não prova um teto de cobrança do provedor para um endpoint sem preço estabelecido**. Esta dúvida deve ser tratada na revisão técnica antes de coletar; não foi convertida em falsa gratuidade. Não há nova solicitação de aprovação financeira nesta entrega: o tetoUS$5 já está aprovado.

Somente usage confiável concilia a parcela de inferência; a provisão de contagem não é liberada automaticamente. Timeout, conexão interrompida ou resposta sem uso mantém toda a reserva. Cada request/hash, contagem e marcação anterior ao envio, response original sanitizado, modelo e conciliação são persistidos. `HTTP_contagem_marcadas`/`HTTP_inferencia_marcadas` indicam intenção persistida de envio, que pode não chegar ao servidor se o processo morrer; não são prova de cobrança.

Slots iniciados e interrompidos ficam indisponíveis na retomada; **não são reenviados**. Slots pendentes independentes podem prosseguir sob o mesmo ledger. Nenhuma inferência é liberada por timeout com custo desconhecido. Resultados canônicos são blobs originais no SQLite; exportação usa publicação atômica exclusiva, sem sobrescrever. Plano/código/inputs divergentes bloqueiam retomada, em vez de criar orçamento substituto. Resumo deriva dos 90 slots planejados; abortar por orçamento/falha preserva os N 30 de B/H/T, sem deltas zero inventados ou MAE em erros.

## Chave e comandos para o usuário

O runner anterior não carregava chave; o novoCLI agora oferece carregamento exclusivo e seguro. **Não envie chave no chat.** Nenhum `.env` real, valor/trecho/tamanho/hash de chave foi lido pelo executor. O usuário pode ter configurado seu arquivo em paralelo; esse arquivo não entra em inventários. Sem instalarSDK ou dependências.

No Terminal:

```sh
cd /Users/vaugusto/Desktop/Faculdade/TCC
PYTHONPATH=TCC_Codigos/src python3 -m piloto_real --configurar-chave
PYTHONPATH=TCC_Codigos/src python3 -m piloto_real --checar-chave
```

O primeiro comando exigeTTY, recebe entrada oculta e cria`.env.piloto`0600, já ignorado peloGit. Recusa sobrescrever/symlink e confere que o caminho é ignorado/não rastreado. O exemplo público sem segredo é`TCC_Codigos/config/piloto.env.example`. O segundo comando só informa presença segura local/variável; **não testa a chave nem chamaAPI**. Variável exportada em outro terminal não aparece automaticamente no app já aberto; o arquivo exclusivo torna o carregamento explícito no processo do runner. O caminho legado continua isolado.

Após revisão técnica do coordenador, o lote já aprovado pode ser preparado sem rede e iniciado no mesmo checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -m piloto_real --preparar
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -m piloto_real --rodar
```

Saída fixa:`TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026/`. Não apagar/recriar essa pasta para “tentar de novo”; retomar com o mesmo comando preserva ledger e não repete slots iniciados. Não houve execução de`--rodar` nem preparação de um ledger real pelo executor. Os testes completos de 90 slots rodaram apenas com mocks em diretórios temporários.

ErrosHTTP de provedor não gravam headers nem corpo de erro que possa conter credencial. Respostas bem-sucedidas têm redator de segredos antes da persistência, inclusive se um mock ecoar a chave sintética. A sanitização remove somente segredos; não corrige significado nem magnitude da previsão. Credential permanece fora de argumentos/histórico/logs. A ferramenta`openai-platform-api-key` não estava disponível neste ambiente; usou-se configuração local solicitada, não busca de credenciais.

## Verificação e pendências

Logs em`outputs/etapa9_integracao_20261026/`.26 testes novos offline cobrem payload/contagem antes de enviar, deadline de processo bloqueado, ausência de ecos/uso, incompletude/recusa, desvio de modelo/cache, contabilidade disjunta, reserva/retomada/concorrência, teto 300/US 5,90 slots válidos B/H/T, erros preservados, fechamento/obrigações/cláusulas, preservação de interpretação errada, segredo sintético eGitignore. Mesmos testes sobPython-O. Regressões 4–9:37+21+24+49+16+27=174 aprovadas. Não repetir ou misturar essas respostasmock como piloto real; nenhuma métrica de IA foi produzida.

Pendentes antes/depois da coleta: revisão técnica desta política/custódia/provisão de contagem, status local fornecido pelo usuário, coleta sob ledger único, auditoria de suporte/inferibilidade por view e análise dos resultados originais. O autor da integração não se torna revisor científico independente. Etapa 9 continua **parcial até coleta/auditoria**, sem congelamento ou experimento final. Sem commit, push, PR, deploy, limpeza de dados ou início das etapas 10/11.


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
