# Etapa 9 — estado da coorte v04 após retomada

26/10/2026, America/Sao_Paulo. Relatório descritivo de duas fases operacionais, com interrupção e retomada autorizada pelo coordenador sob a autorização humana existente. Não é experimento final controlado. N90 planejado,N30 por condição,15 casos × duas repetições. As métricas abaixo consolidam somente a coorte v04; v03 e diagnóstico de 180 s ficam separados.

Estado: 20 slots concluídos, 70 não iniciados. Parada nova: RemoteDisconnected na fase de cabeçalho HTTP, chamada 71. O relatório original de 17 slots e a chamada 61 permanecem intactos no diretório etapa9_coorte_v04_20261026. Os 73 IDs da retomada foram registrados antes da geração, sem reabrir 17 terminados, repetir tentativa 61 ou liberar suas reservas.

|Fase|Slots concluídos|Por condição|Chamadas novas|Tempo dos slots(s)|Inferência conhecida(US$)|
|---|---:|---|---:|---:|---:|
|Fase 1|17|B: 5; H: 6; T: 6|46|1551.44|0,08668216|
|Retomada|3|B: 2; H: 1|10|301.34|0,01532866|

|Condição|Realizados/30|Não iniciados|Estados da execução|
|---|---:|---:|---|
|B|7/30|23|parcial: 6; erro: 1|
|H|7/30|23|parcial: 7|
|T|6/30|24|ok: 4; parcial: 1; erro: 1|

|Condição/desfecho|Cobertura exata|MAE em pares exatos válidos|Estados do desfecho|
|---|---:|---|---|
|B:prazo|0/30|não calculável;n=0/30|indeterminado: 6; invalido: 1; erro: 23|
|B:custo|0/30|não calculável;n=0/30|direcao: 3; indeterminado: 3; invalido: 1; erro: 23|
|H:prazo|0/30|não calculável;n=0/30|indeterminado: 7; erro: 23|
|H:custo|0/30|não calculável;n=0/30|indeterminado: 7; erro: 23|
|T:prazo|4/30|0 dia_corrido;n=4/30|exato: 4; indeterminado: 1; invalido: 1; erro: 24|
|T:custo|4/30|0 BRL_centavo;n=4/30|exato: 4; direcao: 1; invalido: 1; erro: 24|

|Par/desfecho|Interseção comparável|MAE na interseção|
|---|---:|---|
|B/H: prazo|0/30|não calculável|
|B/H: custo|0/30|não calculável|
|B/T: prazo|0/30|não calculável|
|B/T: custo|0/30|não calculável|
|H/T: prazo|0/30|não calculável|
|H/T: custo|0/30|não calculável|

Contabilidade global: 71 tentativas reservadas/300; US$ 0,114331335 inferência conhecida +US$ 0,174 reserva de inferência desconhecida +US$ 0,142 provisão hipotética de contagem =US$ 0,430331335 comprometidos. Saldo interno US$ 4,569668665 sob tetoUS$ 5. Provisão não é tarifa publicada; não é fatura/saldo da conta. Reservas integrais já incluem sua parcela de provisão; não somar duas vezes.

Coorte v04: 56contagens HTTP e 56 inferências marcadas; uso conciliado 253561 tokens de entrada/151206saída total incluindo reasoning. Custos/tokens desconhecidos não foram estimados como zero. Chamadas anteriores 1–15 são só contabilidade global, não entram nas métricas v04.

Prazo em dias corridos e custo em centavos BRL. MAE cobre somente previsão exata válida e referência exata AUTORAL. Interseções pareadas e denominadores estão explícitos. Repetições não são casos independentes. Nenhuma imputação de zero aos ausentes; sua classe mecânica de erro no normalizador não é erro numérico observado. Referência indeterminada k_d307 conserva limite separadamente conforme adaptação já revisada do avaliador1.0. Valores, direções, intervalos, lacunas e resultados por execução estão em normalizacao.json, sem correção.

Suporte semântico não auditado; inferibilidade pendente nas referências novas e sem validação independente. Acerto numérico/MAE selecionado não autoriza superioridade científica. H parcial pode resultar de falha de contrato, bloqueio operacional ou lacuna, que não equivale a abstenção semanticamente adequada. Falhas globais e locais estão em contabilidade_e_erros.json. Nenhuma previsão foi reparada ou repetida.

## Parada e telemetria da retomada

{"call_id": 71, "slot": "etapa9-coorte-v04-180s-20261026-k_42a9-H-1", "erro": "http_indisponivel", "falha_transporte": {"status_http": null, "provider_code": null, "fase": "cabecalho", "classe_excecao": "RemoteDisconnected", "errno": null}, "fase_macro": "inferencia", "contagem_oficial": 5281, "response_presente": false}

A telemetria nova registra somente fase enumerada/classe permitida/errno inteiro; não contém mensagem crua,headers,conteúdo ou segredo. A fase envio pode incluir DNS/TLS pela conexão lazyHTTPS. Classe/fase descrevem a operação onde a exceção foi capturada, sem provar causa externa. Não se reconstruíram detalhes da chamada 61. Nova falha não esclarecida mantém a coleta parada, sem retomada automática.

Integridade:17 slots terminados,chamadas 1–61,fontes/manifesto/parada/relatório parcial preservados por comparação ao snapshot e hashes. Novos resultados vinculam hash do adendo/código do retomador; não alegam cobertura pelo hash antigo. Payloads contados/gerados e parâmetros conferidos, mesma carteira/lock/caps. Cinco testes offline passaram antes da ativação, sem rede ou leitura de chave; sem chamada extra de teste. PROTOCOLO.md e adendo_retomada.json documentam a decisão operacional. Sem etapas 10/11,commit/push/deploy.

## Resultado desta retomada

Foram concluídos somente três dos 73 slots: B/k_23d8/repetição2 retornou campos incompatíveis com o contrato global (uso conciliado, resultado inválido preservado); B/k_42a9/repetição1 retornou previsão parcial; H/k_42a9/repetição1 ficou parcial após a falha71. Nenhum slot terminado anteriormente foi reaberto. Há 70 slots não iniciados e nenhum iniciado sem resultado.

Falha 71: nó n_ae50, contagem oficial 5281 tokens concluída, inferência marcada, RemoteDisconnected na fase cabeçalho em 60.810,171 ms totais da tentativa; deadline de 180 s não foi atingido pelo relógio externo. Sem status HTTP/provider_code/request_id/usage/resposta, errno ausente; reservaUS$ 0,0165 mantida. A implementação local de http.client.HTTPResponse._read_status lança RemoteDisconnected ao receber EOF antes da linha de status HTTP. Isso distingue a falha de interpretaçãoJSON/contrato do modelo, mas não identifica quem fechou a conexão ou por quê; não prova autenticação/modelo/parâmetro inválido. [Evidência segura da chamada 71](falha_call_71.json). A tentativa 61 permanece indeterminada, sem acrescentar-lhe telemetria retroativa.

A nova parada é persistente própria da retomada, além da parada original intacta. Não há segunda liberação ou retry. A entrega volta para revisão do coordenador antes de qualquer nova continuação.
