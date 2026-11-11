# Executor preparado para D01–D09

Preparação autorizada em 10/11/2026. **A coleta não está autorizada nem foi iniciada.** O usuário aumentou o orçamento para US$20 e pediu para confirmar o início somente após o executor estar pronto.

## Protocolo

- Nove cenários de desenvolvimento D01–D09, uma execução de cada; casos finais reservados ficam fora do lote.
- Proponente e revisor usam a configuração já suportada: `gpt-6-luna`, raciocínio `high`. Não há fallback ou retry automático.
- A seleção é sugerida pela IA. A aceitação automática exige ausência de ambiguidades e correspondência exata com o conjunto de entidades mencionadas cadastrado no evento. São permitidas múltiplas entradas, incluindo D05 e D06. Menções são metadados de entrada, não gabaritos de impactos. Divergência exige inspeção; o executor não corrige a resposta nem pede outra.
- Todos os nós elegíveis ficam disponíveis; a região é determinada pelas relações e encaminhamentos, com os limites acumulados da sessão.
- O revisor permanece em observação. Seus pareceres não modificam as propostas nem o cronograma.

## Sequência congelada

1. **Verificação inicial do revisor:** uma chamada sobre a proposta histórica de `M_PROTO_READY`. Verifica contrato, transporte e parser. Qualquer um dos quatro pareceres semanticamente válidos permite prosseguir; não se exige concordância com uma conclusão desejada. Não altera nem repete o piloto original.
2. **Coleta:** D01 a D09, nessa ordem. Sugestão, seleção, sessão, resultado e chamadas são preservados separadamente.
3. **Revisão:** auditoria determinística e IA de cada proposta válida dos resultados salvos, também de D01 a D09.
4. **Avaliação:** somente após salvar todas as previsões e revisões, leitura da referência autoral de desenvolvimento e comparação de valores/estados/documentos. Referências não entram nos pedidos do proponente ou revisor. Divergência de resultado é registrada, nunca corrigida por nova tentativa.

O manifesto congela código, dados, configuração, preços usados na estimativa, piloto de verificação e arquivo de referência por hash. A verificação por hash da referência não fornece seu conteúdo à IA. Preparar não lê credencial, não abre os ledgers para escrita e não chama o serviço.

## Orçamento

US$20 são tratados como **teto acumulado**, incluindo o histórico, e não como US$20 adicionais. No preparo, o comprometimento histórico é US$4,601079675, deixando US$15,398920325 de margem.

| Etapa | Limite de tentativas | Teto |
|---|---:|---:|
| Verificação inicial | 1 | US$0,015 |
| Coleta por cenário, incluindo sugestão e eventuais reanálises por expansão | 65 | US$0,99 |
| Revisão por cenário | 40 | US$0,60 |
| Lote completo: verificação + nove coletas + nove revisões | 946 | **US$14,325** |

São tetos conservadores, não estimativas de gasto efetivo. O máximo do lote mais o histórico informado chega a US$18,926079675, abaixo do teto acumulado. Cada inferência é precedida de uma consulta de contagem: requisições HTTP não equivalem ao número de inferências.

A carteira v2 continua em `outputs/consumo_ia_real.sqlite`; o histórico externo continua sendo somado, sem reinício de saldo. Todas as fases do lote compartilham essa carteira e possuem IDs exclusivos de rodada e de grupo. O transporte reserva e verifica, na mesma transação SQLite, os tetos da fase, do lote e acumulado. O executor antigo conserva seus padrões anteriores; o novo lote passa os limites explicitamente.

Cada tentativa reserva US$0,015, até 64.000 tokens de entrada e 16.000 de saída, com os preços já utilizados pelo transporte. A revisão reserva 360 segundos para contagem e geração. Uso desconhecido mantém a reserva e interrompe o lote. Preços/modelo são a configuração congelada do transporte existente; os testes offline não verificam disponibilidade ou faturamento do serviço real.

## Preparar e iniciar são ações separadas

Preparar, sem rede:

```bash
python3 -B -m TCC_Codigos.etapas.alfa_documental_v2.src.lote_ia preparar \
  --destino TCC_Codigos/etapas/alfa_documental_v2/outputs/lote_desenvolvimento_preparado_20261110
```

Isso grava somente `manifesto.json`, com estado `aguardando_autorizacao`. O diretório deve ser novo. Alteração posterior do código/dados invalida o manifesto e exige novo preparo.

**Somente depois da confirmação futura do usuário**, executar:

```bash
python3 -B -m TCC_Codigos.etapas.alfa_documental_v2.src.lote_ia executar \
  TCC_Codigos/etapas/alfa_documental_v2/outputs/lote_desenvolvimento_preparado_20261110/manifesto.json \
  --autorizar-coleta --autorizacao 'Registrar aqui a autorização efetivamente recebida do usuário'
```

Esse comando não foi executado nesta preparação. O registro textual não deve ser preenchido com autorização inventada. Só após as verificações e a confirmação explícita o executor lê `.env.piloto`, exigindo arquivo protegido 0600. A credencial não é gravada no manifesto.

`execucao.json` é criado exclusivamente antes das chamadas; uma segunda execução no mesmo lote é recusada. Não há retomada automática de lote interrompido. Inspecionar registros e reservas antes de decidir qualquer nova execução, evitando cobrar ou repetir cenários silenciosamente.

## Falhas e incerteza

O executor para diante de ambiguidade, resposta inválida, erro de transporte, limite atingido ou falha de revisão. A auditoria usa `parar_em_falha=True`, persistindo a primeira falha antes de interromper novas propostas. O comportamento padrão da API de auditoria anterior permanece inalterado.

Uma previsão indeterminada por falta legítima de informação **não é falha técnica**: D04 pode concluir a interpretação com previsão parcial. O executor registra `estado_previsao` e `completude` separadamente de `coleta=concluida`. Um parecer desfavorável válido também não interrompe o protocolo. Falhas deixam os demais cenários explicitamente não executados e preservam o checkpoint, inclusive resultados parciais.

## Validação offline

A suíte `tests/test_lote_ia.py` usa HTTP falso e bloqueia sockets. Exercita a execução completa dos nove cenários com revisão, múltiplas entradas, incerteza factual, preparação sem credencial/gasto, aprovação ausente, manifesto obsoleto, orçamento acumulado/grupo, seleção ambígua, falha local, falha na primeira revisão e recusa de repetir o lote.

A execução de teste é identificada como `teste_http_injetado_nao_mede_ia`. Respostas prescritas verificam integração, não capacidade semântica do modelo. Nenhuma chamada paga foi realizada.

Validação desta preparação: **81 testes passaram** (71 anteriores e 10 novos), incluindo a execução completa com HTTP falso. O manifesto foi gerado e validado em `outputs/lote_desenvolvimento_preparado_20261110/manifesto.json`; seu estado é `aguardando_autorizacao`, sem `execucao.json`. Os dois ledgers históricos foram conferidos contra os objetos versionados e permanecem intactos.
