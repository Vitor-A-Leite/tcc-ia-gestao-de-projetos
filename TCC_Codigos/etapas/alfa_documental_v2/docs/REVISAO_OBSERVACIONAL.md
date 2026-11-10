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

O parecer contém `sustentada`, `contradita`, `suporte_insuficiente` ou `ambigua`, tipo de efeito, entidade/alvo/atributo/unidade/valor sustentados, fontes examinadas, citação literal, justificativa e suporte ausente. Há prompt e JSON Schema, seguidos de parser/validador local estritos. Campos extras, JSON com chaves repetidas, fonte inventada, versão divergente, recusa, incompletude, falha de transporte ou incoerência entre campos resultam em `requer_revisao`, sem parecer sustentado. Citações literais válidas ainda não provam que o raciocínio da IA está correto.

A auditoria documental apenas reapresenta os estados da verificação de afirmações previamente cadastradas, inclusive `ja_atualizado` e `nao_verificavel`. Não extrai novas afirmações de prosa nem reescreve documentos.

## Revisão real: API explícita e orçamento independente

Este caminho foi exercitado somente com HTTP falso nos testes. Nenhuma chamada paga foi executada nesta implementação. A compatibilidade do schema com o serviço real ainda exige um ensaio futuro autorizado.

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

```bash
python3 -B TCC_Codigos/etapas/alfa_documental_v2 testar
# ou, da raiz do repositório:
python3 -m unittest discover -s TCC_Codigos/etapas/alfa_documental_v2/tests -t . -q
```

A CLI `testar` descobre a suíte inteira. Os testes cobrem estrutura, valores desconhecidos, igualdade, repetição, conflito, custo/unidade, parser/fontes/vínculos, pareceres prescritos, falhas, orçamento/reservas, repetição de destino e observação sem alteração dos resultados/contextos do proponente. Os testes de HTTP usam transporte falso em diretório temporário; os dados e gastos históricos não são alterados.
