# Etapa 9 — ajuste de formato local v04, revisão offline

26/10/2026. Entrega offline, sem rede, leitura de chave ou novas chamadas. O diagnóstico aprovado de duas chamadas/180 s já terminou e permanece integral em `outputs/etapa9_diagnostico_180s_20261026/`. Esta versão não retoma a coleta.

## Problema e mudança

A resposta H local real continha predicados textuais fora do catálogo vazio e valores quantitativos escalares. O parser correto rejeitou a primeira incompatibilidade. O pacote novo `src/formato_local_v04/` torna explícito o contrato solicitado, sem alterar parser, validador, dados, referências ou resposta observada:

- Valores quantitativos usam Conhecimento com seis campos; confirmação usa escalar com regra local, condição confirmada e avaliação local de custo zero quando exigida.
- `aplicar_regra_catalogada` usa objeto aditivo não vazio, limitado a taxa_centavos_dia (inteiro não negativo ou null), base_contratada_dias (inteiro não negativo) e politica_reducao (sem_credito ou recalculavel_com_credito).
- Predicados são copiados literalmente do catálogo, inclusive quando são texto. Catálogo vazio implica condições vazias. Justificativa fica em justificativa; referências às fontes em evidencias; lacunas não viram condições.
- `registrar_lacuna_custo` não admite conhecimento exato. IDs, unidades, fontes, efeitos canônicos e permissões vêm do contexto sem consulta a gabarito.

O descritor de contrato é instrução de conteúdo, **não JSON Schema aplicado pelo provedor**. O envelope API continua `json_object`; o conteúdo do prompt/payload e seus hashes mudam. Isso não garante obediência ou suporte semântico de uma futura resposta real.

## Versão, proveniência e isolamento

A versão `4.0-formato-local` é opt-in em LocalV04/ResponsesV04. O transporte exige manifesto próprio com versão e slots novos e recusa slots históricos; nenhuma carteira/adendo executável foi registrado nesta entrega. A CLI antiga permanece intacta.

`requisicao_adaptador_hash` identifica o pedido v04 efetivamente entregue ao transporte; `contrato_resposta_hash` identifica o descritor. `config_hash` continua significando apenas configuração, não prompt. O transporte herdado acrescenta a nota operacional condicional2.0 compatível e reserva com o hash do payload HTTP final: os testes verificam esse vínculo e a igualdade dos campos comuns entre contagem e geração. O hash do adaptador não é apresentado como hash HTTP.

Na orquestração existente, o tipo qualificado `formato_local_v04.LocalV04` entra em contrato_execucao antes do contexto_hash e da consulta ao cache; troca de instância também muda a geração. Portanto a classe nova separa cache legado. Uma futura alteração de conteúdo deve ganhar versão/tipo novo e manifesto próprio, sem trocar prompt/transporte de instância ativa ou importar cache antigo. Não houve integração paga ou retomada via orquestração nesta entrega.

Modelo, raciocínio high, limite 25000, teto de entrada 16000, cache TTL, política sem retries, seleção e critérios semânticos permanecem. O deadline não é ampliado pelo pacote: ele recebe o prazo do futuro protocolo. Os dois diagnósticos de 180 s não autorizam automaticamente um novo lote.

## Verificação

15 testes novos passaram em execução normal e Python -O: nove operações, três formas de valor, catálogo textual/vazio, confirmações, lacunas, identidades, tipos, duplicatas, imutabilidade, isolamento e caminho HTTP inteiramente mockado. A resposta real foi apenas relida e rejeitada novamente pelo mesmo parser, sem alteração. Mais 54 regressões das etapas 5, integração real e diagnóstico passaram. O teste de processo/deadline foi reexecutado isoladamente por `python -m unittest` porque o runner inicial via stdin causou aviso de spawn; passou sem aviso.

Evidências em `outputs/etapa9_formato_v04_20261026/`: logs, payload_mock.json e integridade_final.json. O mock usa números arbitrários e prova forma/transporte, não validade de previsões ou melhoria real de adesão.

## Próximo passo para revisão

Revisar este formato antes de qualquer chamada. Uma futura execução exige protocolo/adendo versionado, slots novos e integração persistente na mesma carteira acumulada; deve contar oficialmente o **novo** payload antes de gerar, respeitando os limites aprovados. Não reiniciar o ledger nem substituir resultados pagos anteriores.

Saldo interno preservado: comprometimento US$ 0,172820515 e disponibilidade US$ 4,827179485 sob teto US$ 5, com reservas desconhecidas e provisão hipotética de contagem mantidas. Não é fatura/saldo de conta. Etapa 9 permanece parcial; etapas 10/11 não iniciadas. Sem commit/push.

## Contraprova direcionada do cache

Um teste adicional, sem repetir as suítes, executou a orquestração real com respostas mock e entradas idênticas: LLM anterior → repetição anterior → LocalV04 → repetição LocalV04. A configuração é `{tipo, modelo, configuracao, timeout_s, repetir, politica_versao}`; o vínculo é `(id(interpretador), id(politica.resolver), hash_json(configuracao))`. A mudança de vínculo incrementa geracao. O contexto inclui `contrato_execucao={configuracao,geracao}` antes de calcular contexto_hash; a chave efetiva é `(execucao_id,no_id,contexto_hash)`. O tipo muda de `interpretacao_no.adaptadores.LLM` para `formato_local_v04.LocalV04`.

A contraprova confirmou igualdade das entradas sem os campos de execução/revisão, igualdade de modelo/configuração/deadline, hashes e chaves distintos, ausência de reutilização cruzada e reutilização própria nas duas repetições. Evidência concreta das assinaturas, hashes e chaves em `cache_contraprova.json`; log em `cache_contraprova.log`. Total: 15 testes normais e -O, mais 1 teste direcionado do cache, além das 54 regressões já registradas. A primeira asserção do teste incluía passos determinísticos sem análise; foi corrigida para comparar somente entradas com análise. Não houve alteração de produção.
