# Continuação autorizada de D04

O lote de 10/11/2026 parou por falha de rede em `TEST_THERMAL`. O usuário
autorizou: “Continue a partir de D04, retomando de onde falhou”. Essa autorização
permite uma continuação explícita; não habilita retries automáticos.

O executor `scripts/retomar_lote_d04.py` fica fora de `src` para preservar a
assinatura do runtime, o contrato, os prompts e o manifesto original. Antes de
qualquer chamada, um probe offline verifica que os oito resultados válidos são
reutilizados e que o primeiro pedido é idêntico ao pedido de `TEST_THERMAL` que
falhou. Uma barreira impede repetir os nós válidos ou tentar duas vezes um nó
na continuação. Os artefatos originais são verificados por hash e preservados.

Uma cópia do checkpoint mantém seleção, contexto, respostas válidas, tentativas
e consumo acumulado. Somente o envelope de erro sai do cache operacional; ele
permanece no original e no adendo da cópia. Preflight, D01–D03 e sugestão de D04
não são repetidos. A sequência restante segue o protocolo congelado: concluir
D04, coletar D05–D09, revisar as propostas D01–D09 e comparar com a referência
autoral somente ao final. Nenhum parecer é usado para refazer as respostas.

A reserva de US$0,015 da chamada sem resposta continua inconciliada no ledger.
Durante a execução da cópia, `uso_desconhecido` é o bloqueio de **novas** chamadas
com consumo desconhecido; a incerteza anterior permanece explícita em
`uso_desconhecido_anterior` e `retomada.consumo_anterior`. Ao persistir o resultado,
o indicador total `uso_desconhecido` volta a refletir ambas as etapas. Não há
conciliação fictícia, estorno, nem afirmação de que a chamada anterior foi grátis.

O transporte da continuação usa uma rodada separada na mesma carteira e no mesmo
grupo do lote. Os tetos de D04 descontam todas as dez tentativas anteriores e
US$0,0279946 comprometidos. Permanecem o teto do lote e o teto histórico total de
US$20. Uma nova falha interrompe a execução. Uma trava persistente e a consulta
ao ledger impedem iniciar duas continuações, inclusive em pastas distintas.

Sem `--autorizar-coleta`, o comando executa apenas as verificações offline, sem
ler chave, alterar carteira ou chamar API. Com a opção, exige `--destino` novo
e `--autorizacao` explícita. O adendo registra autorização, hashes e verificação.
