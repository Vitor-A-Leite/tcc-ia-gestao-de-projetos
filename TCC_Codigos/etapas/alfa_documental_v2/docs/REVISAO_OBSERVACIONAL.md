# Revisão observacional de propostas

A revisão registra duas respostas separadas: o que pode ser verificado pelo contrato e o que um revisor de IA alega encontrar nas fontes. Nenhuma delas muda o aceite operacional, o fechamento, o cálculo, a aprovação humana ou `suporte_semantico='nao_auditado'` da execução original. Não há veto automático nem aprovação fictícia.

## Auditoria offline de uma coleta existente

Da raiz do repositório:

```bash
python3 -B TCC_Codigos/etapas/alfa_documental_v2 auditar \
  TCC_Codigos/etapas/alfa_documental_v2/outputs/ia_real_20261110T050151Z/resultado.json \
  --saida /tmp/auditoria-d02-nova.json
```

O comando só lê a coleta. O destino deve ser novo: um arquivo existente provoca erro antes de qualquer revisão. A CLI não carrega credenciais nem oferece chamada de IA real. Ela produz as análises determinísticas e os pacotes de evidência, sem preencher pareceres semânticos. O marco indevido `release_M_PROTO_READY=25` pode continuar como **candidata estrutural**: detectar falta de suporte na prosa é tarefa distinta.

A API equivalente é `auditar_arquivo(origem, destino)`. Para objetos em memória, use `auditar_resultado(resultado)`. Ambas ficam em `src.auditoria`; a entrada não é modificada. O relatório registra hash do resultado e, no caminho por arquivo, SHA256 dos bytes originais, além do vínculo proposta/contexto e hashes dos pacotes.

## Observação durante uma execução

```python
from TCC_Codigos.etapas.alfa_documental_v2.src.pipeline import simular
from TCC_Codigos.etapas.alfa_documental_v2.src.revisao import Observador

resultado = simular('D02', observador=Observador())
registros = resultado['revisao_observacional']['registros']
```

Também há o parâmetro `observador` em `pipeline.executar` e `orquestracao.avaliar`. O gancho roda após a validação estrutural e o vínculo da resposta, antes da incorporação. O contexto/pedido do proponente é idêntico com e sem observador. Parecer, erro e tempo da observação ficam separados do cálculo; o tempo do observador não consome o limite de execução do solver.

O padrão é desativado. O gancho aceita apenas análise determinística ou revisor **offline** identificado. A revisão real ocorre exclusivamente pela auditoria separada descrita abaixo; as sessões de interpretação em `Sessoes` não recebem chamadas adicionais ocultas.

## Revisor injetável e demonstração prescrita

`RevisorIA(transporte, modelo=..., configuracao=..., modo='offline')` exige um transporte com `origem='simulado'`. O transporte recebe `mensagens`, `formato_resposta`, modelo, configuração e timeout, e retorna `RespostaTransporte`. Não há tentativa adicional nem cache de parecer. Respostas offline não podem declarar tokens ou custo reais positivos; métricas ausentes permanecem `null`.

Esta demonstração usa deliberadamente o auxiliar de **teste**, que prescreve pareceres para exercitar o contrato. Não é inferência de IA nem evidência de capacidade semântica:

```python
from TCC_Codigos.etapas.alfa_documental_v2.src.pipeline import simular
from TCC_Codigos.etapas.alfa_documental_v2.src.revisao import Observador
from TCC_Codigos.etapas.alfa_documental_v2.tests.test_revisao import revisor_teste

resultado = simular('D02', observador=Observador(revisor_teste()))
assert resultado['suporte_semantico'] == 'nao_auditado'
assert resultado['revisao_observacional']['registros'][0]['revisao_semantica']['natureza'] == 'simulacao_nao_mede_ia'
```

O teste `test_piloto_marco_sem_suporte_continua_numericamente_igual` injeta uma resposta manual de suporte insuficiente para o marco do piloto. Demonstra armazenamento e não interferência; não demonstra que um modelo detecta o erro sozinho.

## Conteúdo e limites das checagens

Cada proposta registra identidade, hash, decisão determinística, motivos, vigente/proposto, duplicadas e conflitos. As decisões possíveis são `candidata`, `ja_atualizado`, `ja_incorporado`, `incompativel`, `conflito` e `requer_revisao`. Não são decisões de aceite.

A checagem reutiliza o validador histórico e verifica permissões, entidade/alvo/atributo/unidade, condições, referências, versão e integridade local do contexto. Compara entradas locais; um fim calculado de predecessor não vira restrição local. Ausência ou valor indeterminado não é convertido em zero. Para parcelas e aditivos, considera operações financeiras explicitamente incorporadas, pois o contexto corrente do motor pode conservar a base financeira. Aditivos em parâmetros diferentes não são conflito apenas por terem mapas diferentes.

`ja_atualizado` informa igualdade de entrada, sem certificar suporte. Uma confirmação de manutenção pode continuar necessária ao fechamento mesmo sem efeito numérico. `ja_incorporado` exige a mesma origem causal estruturada, operação, alvo e valor. Registros legados de `alteracoes_incorporadas` não carregam `origens_causais`: nesses registros, uma operação igual é sinalizada, mas não certificada como o mesmo fato. Citações iguais podem conter fatos distintos. Não há deduplicação semântica por palavras-chave.

O pacote usa somente o contexto original: entidade/atributo, vigente/proposto, fontes literais com documento/versão/localizador, relações, regras, restrições, parcelas, entradas correntes e operações incorporadas. Não usa resultados finais, referências de avaliação, gabaritos ou a justificativa do proponente como evidência. Hashes provam correspondência local dos dados, não autenticidade externa dos documentos.

O contrato `2-revisao-observacional` fixa o objeto avaliado no código. A IA avalia sete aspectos da proposta, cobrindo entidade, alvo, atributo, unidade, valor, condições e escopo. Cada aspecto contém estado, IDs de fontes e justificativa. Os estados possíveis são `sustentado`, `contradito`, `insuficiente`, `ambiguo` e `nao_aplicavel`. Este último se aplica exclusivamente a condições vazias.

O parecer global contém `sustentada`, `contradita`, `suporte_insuficiente` ou `ambigua`, tipo de efeito, fontes examinadas, justificativa e suporte ausente. O código verifica a coerência entre a conclusão e os aspectos. Uma conclusão favorável exige suporte em todos os aspectos aplicáveis, referências de evidência e cobertura de todas as fontes citadas pela proposta. Uma conclusão desfavorável exige ao menos um aspecto com o estado correspondente. Valores indeterminados recebem avaliação na representação original.

A resposta da IA seleciona IDs do catálogo de fontes. Após a validação, o código recupera documento, versão, localizador e trecho integral original em `fontes_examinadas`. Os IDs selecionados ficam em `fontes_selecionadas`. Os campos de identidade utilizados pelos consumidores anteriores são derivados do objeto avaliado após um parecer favorável. `resposta_bruta` preserva a resposta recebida e `parecer` contém a representação validada e enriquecida.

Há prompt e JSON Schema versionados, seguidos de parser e validador local estritos. Erros registram código, caminho do campo e mensagem. Entre os diagnósticos estão `fonte_invalida`, `fonte_duplicada`, `fonte_nao_examinada`, `cobertura_incompleta`, `evidencia_ausente`, `aspecto_inconsistente`, `parecer_inconsistente` e `efeito_incompativel`. A identidade registra o hash do prompt e cada revisão registra o hash do schema. A interpretação semântica permanece sujeita a erro mesmo quando o contrato é atendido.

Os registros v1 e v2 podem ser relidos por `validar_parecer`. Para exercitar explicitamente um contrato anterior, use `RevisorIA(..., versao=VERSAO_LEGADA)` ou `RevisorIA(..., versao=VERSAO_V2)`. Cada requisição exige a versão correspondente da resposta. A releitura dos 19 pareceres v1 reproduz os dez aceitos pelo contrato e as nove rejeições originais. Os 23 pareceres da primeira avaliação v2 também são reproduzidos integralmente.

## Contrato v3 e uso dos metadados

O padrão atual é `3-revisao-observacional`. `montar_pacote` inclui `metadados_escopo` e `valores_avaliados`. Para revisar um pacote histórico com o novo contrato, `atualizar_pacote(pacote)` produz um pacote v3 com novo hash, conservando a proposta e a referência ao contexto original.

O cadastro `data/projetos/alfa/escopo_revisao.json` explicita a política de entrada já utilizada pelo normalizador do Alfa. Registra o projeto, a versão, os aliases conhecidos, o vínculo entre cada evento e seu documento/versão e a vigência prospectiva desde D0. A declaração de vigência é procurada por correspondência exata nesse cadastro. O instante de observação tem significado próprio. Uma declaração sem cadastro gera vigência indisponível. Divergências de projeto, versão ou documento são registradas pelo código.

O pacote preserva um snapshot do cadastro, seu hash, os campos de origem e o resultado das verificações. A IA referencia esse registro por `CONTEXTO.ESCOPO`, em `contexto_ids` do aspecto `escopo` e em `contextos_examinados`. A representação validada contém `contextos_resolvidos`. Os demais aspectos usam evidência documental.

Em `restricoes_escopo`, a IA extrai restrições documentais explícitas de projeto, versão e início/fim de vigência. Cada restrição registra o campo, estado de conhecimento, valores, fontes e justificativa. O silêncio documental produz uma lista vazia. O código compara as restrições extraídas ao cadastro e confere o estado declarado em `aspectos.escopo`. Um cadastro verificado com lista vazia resulta em `sustentado`. Uma restrição explícita incompatível resulta em `contradito`. Alternativas e lacunas recebem classificação própria. A interpretação das restrições textuais cabe à IA.

Em `fundamentos_valor`, a IA descreve a afirmação aplicável a cada campo de `valores_avaliados`. Registra `conhecimento`, `valores`, `fonte_ids`, `aplicabilidade` e `justificativa`. O código verifica referências e cardinalidade e realiza a comparação. Uma fonte indeterminada e uma proposta exata resultam em `insuficiente`. Fonte e proposta indeterminadas sustentam o estado de conhecimento. Valores exatos divergentes, referentes ao mesmo objeto e vigência, resultam em `contradito`. Uma afirmação de outro período ou objeto resulta em suporte insuficiente para essa comparação.

O parser exige coerência entre os fundamentos, os aspectos e o parecer global. As comparações ficam em `comparacoes_codigo`. Erros específicos incluem `classificacao_valor_inconsistente`, `classificacao_escopo_inconsistente` e `fundamento_inconsistente`. A conferência é condicionada à extração semântica feita pela IA. A classificação de falsos positivos e falsos negativos exige avaliação dos documentos e dessas extrações.

A auditoria documental apenas reapresenta os estados da verificação de afirmações previamente cadastradas, inclusive `ja_atualizado` e `nao_verificavel`. Não extrai novas afirmações de prosa nem reescreve documentos.

## Revisão real: API explícita e orçamento independente

O lote de desenvolvimento de 10/11/2026 exercitou o contrato v1 no serviço real e produziu 19 tentativas de revisão. Os registros estão em `outputs/lote_desenvolvimento_revisoes_finais_20261110`. A avaliação do contrato v2 usa o executor de comparação descrito adiante.

O chamador fornece um `TransporteReal` já configurado com a carteira histórica correta. O módulo não procura chaves, cria credenciais ou reconstrói o histórico monetário:

```python
from TCC_Codigos.etapas.alfa_documental_v2.src.auditoria import TransporteRevisaoReal, auditar_arquivo
from TCC_Codigos.etapas.alfa_documental_v2.src.revisao import RevisorIA
from TCC_Codigos.etapas.alfa_documental_v2.src.ia_real import MODELO, CONFIG

# transporte_com_carteira é um TransporteReal previamente configurado pelo chamador.
revisor = RevisorIA(TransporteRevisaoReal(transporte_com_carteira),
                   modelo=MODELO, configuracao=CONFIG, modo='ia_real')
auditoria = auditar_arquivo('resultado.json', 'auditoria-real-nova.json',
    revisor=revisor,
    limites={'max_solicitacoes': 2, 'max_tokens_entrada': 128000,
             'max_tokens_saida': 32000, 'max_segundos': 1000,
             'max_custo_centavos': 3})  # centavos de USD
```

A sessão de auditoria persiste o pedido antes de chamar o transporte. Antes de cada tentativa, reserva capacidade para 64.000 tokens de entrada, 16.000 de saída, USD 0,015 e 360 segundos (até 180 s para contagem e 180 s para geração). Usa `TransporteReal.gerar`, preservando os tetos de rodada/carteira existentes. Contabiliza deltas observados e comprometimento; falha com uso desconhecido mantém a reserva e bloqueia novos pedidos. Não transforma custo desconhecido em custo zero.

O resultado guarda pedido, resposta textual bruta, envelope de transporte, resposta da API quando disponível, modelo/configuração, uso informado, latência medida e sessão financeira. O `TransporteReal` mantém adicionalmente seus registros brutos e ledger. A identidade do revisor fica separada da identidade do proponente.

Repetir o mesmo destino é recusado antes de qualquer gasto. Um novo destino constitui nova auditoria e pode gastar novamente dentro de um novo orçamento explícito. Não há cache nem retomada automática de auditoria real: revisor/configuração diferentes nunca reutilizam silenciosamente um parecer anterior. Auditoria interrompida deve ser inspecionada junto ao ledger antes de iniciar outra; a coleta original permanece intacta.

## Testes

As regressões v2 exercitam os 19 pacotes históricos, a recuperação literal das fontes, o vínculo do objeto avaliado, os sete aspectos, a coerência das conclusões, as entradas indeterminadas de D04/D09 e o documento já atualizado de D07. A avaliação em lote tem testes de retomada, interrupção em voo, reservas financeiras, manifesto obsoleto e classificação dos controles.

```bash
python3 -B TCC_Codigos/etapas/alfa_documental_v2 testar
# ou, da raiz do repositório:
python3 -m unittest discover -s TCC_Codigos/etapas/alfa_documental_v2/tests -t . -q
```

A CLI `testar` descobre a suíte inteira. Os testes cobrem estrutura, valores desconhecidos, igualdade, repetição, conflito, custo/unidade, parser/fontes/vínculos, pareceres prescritos, falhas, orçamento/reservas, repetição de destino e observação sem alteração dos resultados/contextos do proponente. Os testes de HTTP usam transporte falso em diretório temporário; os dados e gastos históricos não são alterados.

## Comparação versionada do revisor v2

O executor `scripts/avaliar_revisor_v2.py` reconstrói os pacotes a partir das 19 propostas coletadas e inclui quatro controles. N01 reapresenta a proposta histórica de `release_M_PROTO_READY=25`. N02 contrapõe uma proposta D26 a um aviso D25. N03 propõe D25 diante de disponibilidade desconhecida. N04 oferece duas datas alternativas sem confirmação. Os três últimos controles são variantes sintéticas identificadas nos registros.

O preparo grava entradas, referências de avaliação e manifesto com hashes do código, configuração, fontes e resultados de origem. As referências autorais e os pareceres anteriores ficam em arquivo próprio. A chamada recebe o pacote documental. A comparação lê as referências após persistir os resultados de todos os casos.

```bash
python3 -B -m TCC_Codigos.etapas.alfa_documental_v2.scripts.avaliar_revisor_v2 preparar /tmp/avaliacao-nova
python3 -B -m TCC_Codigos.etapas.alfa_documental_v2.scripts.avaliar_revisor_v2 executar /tmp/avaliacao-nova \
  --autorizacao 'Registrar aqui a autorização efetivamente recebida'
```

O lote usa uma sessão persistente por caso, reserva máxima de US$0,015 por tentativa e teto conjunto de US$0,345 para os 23 casos. A carteira histórica participa do teto acumulado de US$20. O bloqueio de arquivo serializa a execução do mesmo manifesto. Ao retomar o comando, os checkpoints existentes são reapresentados e os casos pendentes seguem para avaliação. Uma tentativa interrompida fica identificada no relatório, com sua reserva financeira registrada.

`comparacao.json` apresenta validade contratual, classificações, concordância com pareceres anteriores válidos, concordância dos controles com a referência autoral, cobertura declarada de fontes/aspectos e consumo. A cobertura conta referências selecionadas. A qualidade da interpretação é examinada pelos controles e pela inspeção dos pareceres. Os quatro controles constituem uma amostra de desenvolvimento.

## Avaliação das correções v3

O executor `scripts/avaliar_revisor_v3.py` prepara 28 casos. São 19 propostas históricas, os quatro controles anteriores e cinco controles adicionais para projeto divergente, versão divergente, início de vigência divergente, aliases cadastrados e data anterior com nova magnitude desconhecida. Os identificadores operacionais dos controles utilizam apenas seus números. As referências autorais ficam no arquivo de comparação.

```bash
python3 -B -m TCC_Codigos.etapas.alfa_documental_v2.scripts.avaliar_revisor_v3 preparar /tmp/avaliacao-v3-nova
python3 -B -m TCC_Codigos.etapas.alfa_documental_v2.scripts.avaliar_revisor_v3 executar /tmp/avaliacao-v3-nova \
  --autorizacao 'Registrar aqui a autorização efetivamente recebida'
```

A reserva máxima da rodada é US$0,42. O executor reutiliza a carteira e os mecanismos de checkpoint da avaliação anterior. O manifesto congela o cadastro, o código, as entradas e os hashes dos resultados históricos. A comparação apresenta também os quatro casos de regressão de escopo. A suíte exercita leitura histórica, valores desconhecidos, aliases, vigência, documentos divergentes, campos monetários compostos, retomada e orçamento.
