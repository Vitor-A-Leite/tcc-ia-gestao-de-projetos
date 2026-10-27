# Etapa 9 — R2 SSE pronto para revisão, sem execução paga

26/10/2026, America/Sao_Paulo. **Carteira real intacta: 71 tentativas, 20 slots terminados e 70 não iniciados.** Comprometimento interno US$ 0,430331335; saldo interno US$ 4,569668665 sob o teto acumulado de US$ 5. Nenhuma chamada paga, leitura de chave, ativação R2 ou tabela R2 foi criada na carteira real nesta entrega. Os registros simulados de chamada 72/21 slots nos logs pertencem exclusivamente a cópias temporárias de teste.

## Mudança e caminho completo

Pacote novo `src/retomada_v04_sse/`, preservando fontes, manifestos, respostas, snapshots e as duas paradas anteriores. O POST de geração acrescenta apenas `stream: true`; prompts, entradas, contrato local v04, gpt-6-luna/high, 25.000 tokens totais, contagem oficial até 16.000, tier default, cache 30 min, ferramentas vazias, store false e truncation disabled permanecem. O POST `/input_tokens` continua JSON com os mesmos campos e valores. O hash reservado passa a identificar o payload efetivamente enviado, incluindo streaming.

A documentação oficial descreve SSE com `stream: true` e eventos terminais com o objeto Response. O código usa esse objeto, sem construir uma previsão a partir dos deltas. [Guia de streaming](https://developers.openai.com/api/docs/guides/streaming-responses), [referência de eventos](https://developers.openai.com/api/reference/resources/responses/streaming-events).

| Arquivo novo | Responsabilidade |
|---|---|
| [parser.py](../../src/retomada_v04_sse/parser.py) | UTF-8 incremental, fragmentos, CR/LF/CRLF, data multilinha, comentários, terminal e limites. |
| [http.py](../../src/retomada_v04_sse/http.py) | Worker terminável, SSE na geração e JSON na contagem, deadline fixo e telemetria segura. |
| [transporte.py](../../src/retomada_v04_sse/transporte.py) | ResponsesSSE para B/T e LocalSSE para H; usage/parser/validador anteriores. |
| [__init__.py](../../src/retomada_v04_sse/__init__.py) | Lista fechada, âncoras, carteira, runner e vínculo de código/adendo nos resultados. |
| [__main__.py](../../src/retomada_v04_sse/__main__.py) | Preparo somente leitura; coleta depende de ativação técnica explícita. |

O runner conserva ordem e seleção. H mantém até oito análises/chamadas e 1.500 s totais, como no adendo anterior. O resultado recebe `adendo_transporte_sse` antes de persistir, inclusive em falha. Os hashes antigos não são apresentados como cobertura do código R2. [Diff mínimo do adaptador](diff_adaptador.diff) e [diff dos arquivos novos](novos_arquivos.diff).

## Terminais, erros e deadline

Somente `response.completed` fornece uma resposta completa ao pipeline. Recusa continua recusa, nunca previsão válida. Terminais failed/incomplete preservam o Response original e eventual usage verificável, mas não tornam texto parcial válido e interrompem a coleta. Usage ausente/incoerente mantém reserva e aciona a guarda; conteúdo completo original não é reparado. Erro SSE, EOF sem terminal, JSON/UTF-8 inválido, divergência de tipo/status, truncamento ou excesso de limites falham conservadoramente, sem retry/fallback.

O parser não retém texto dos deltas: preserva Response terminal e resumo de eventos/bytes. Limites: 8 MiB no fluxo, 4 MiB por evento/linha e 100 mil eventos. Excesso vira falha operacional. O deadline é absoluto: contagem consome parte dos 180 s; eventos/heartbeats não renovam o prazo. O processo pai desconta inicialização da espera e confere o prazo ao receber. A limpeza de processo conserva o join limitado da implementação anterior.

`ultimo_sse` é limpo em cada operação válida, inclusive antes de timeout/EOF na contagem seguinte. Telemetria de falha contém somente enums, classe permitida e errno inteiro; mensagens cruas, conteúdo e headers de exceções não são registrados. Nenhum detalhe novo é atribuído retroativamente às chamadas 61/71.

## Adendo, limites e ativação

[Adendo final regenerado](adendo_r2_offline.json), com hashes finais; o rascunho anterior foi mantido em `rascunhos/`. Exatamente 70 IDs pendentes: B 23, H 23 e T 24. As 20 saídas, chamadas 1–71, manifestos e ambas as paradas ficam ancoradas. Novas ativações/paradas seriam registradas em tabelas próprias, append-only, no mesmo SQLite/lock. Cap global 300 e teto US$ 5 permanecem transacionais; guardas anteriores não foram relaxadas.

Passagem máxima: **219 chamadas novas, 290 agregadas**. Reserva adicional máxima US$ 3,6135; comprometimento global máximo **US$ 4,043831335**, incluindo o saldo comprometido anterior. É projeção conservadora, não gasto realizado ou tarifa comprovada de contagem.

O R2 **não está ativado**. Após revisão favorável e liberação operacional do coordenador, o caminho já implementado é:

```sh
PYTHONPATH=TCC_Codigos/src python3 -m retomada_v04_sse --rodar --revisao-coordenador-registrada
```

Esse comando não foi executado. A liberação é técnica, vinculada à autorização humana original dos 90 slots/180 s/US$ 5; não representa uma nova fala ou aprovação financeira do usuário. A CLI recusa coleta sem a liberação, antes de carregar chave. Não há chamada extra de teste.

## Verificação e ressalvas

**22 testes distintos passaram**, em cópias do SQLite e mocks: 15 iniciais, três do runner/contrato/telemetria, três do worker/guarda e uma contraprova dos parâmetros do adendo. Uma revalidação direcionada confirmou que a inicialização consome o mesmo prazo e a telemetria anterior é descartada; não foram repetidas suítes históricas amplas. [Testes](../../tests/etapa9_sse_r2/test_sse.py) e logs neste diretório.

Os testes cobrem igualdade do Response/usage final, diferença única stream no payload local, contagem HTTP idêntica à anterior, fragmentos e multiline/CRLF, recusa, erro sanitizado, EOF/truncamento, failed/incomplete com/sem usage, memória, deadline não deslizante, ausência de vazamento, runner sem retry, replay/concorrência, âncoras, orçamento/cap e paradas persistentes.

[Integridade final](integridade_final.json): esquema e todas as tabelas da carteira real iguais ao snapshot após R1; 88 arquivos da primeira fase, 34 artefatos R1 e 38 fontes anteriores conferidos sem alteração. Código e adendo R2 coincidem por hash. A carteira real permanece em 71 tentativas/20 resultados; mocks não foram incorporados.

Streaming é uma mitigação operacional **a testar**, não uma causa/correção comprovada dos fechamentos em aproximadamente 60,8 s. Compatibilidade real, comportamento do serviço, memória e latência não foram testados contra a API. A hipótese de timeout intermediário permanece não comprovada.

A futura apresentação deve separar fase inicial, R1 e R2, além do consolidado descritivo somente da coorte v04. Os 70 não iniciados são cobertura pendente, não erros observados do modelo; eventual classe mecânica do normalizador será apresentada separadamente. Nenhuma equivalência científica é presumida; suporte semântico e inferibilidade permanecem pendentes. Sem etapas 10/11, commit, push ou deploy.
