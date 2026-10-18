# Baseline estável V2: protocolo e separação dos conjuntos

A versão experimental permanece **BASELINE_V2**, com modelo `gpt-6-luna` já
configurado no notebook. Não foi criada V3. Este estado corrige a definição de
entidades e separa desenvolvimento de avaliação, antes do congelamento experimental.
O hash do prompt muda dentro da V2 e identifica este estado; resultados de hashes
anteriores não podem ser misturados aos novos resultados como uma única rodada.

## Conjuntos e uso permitido

| Conjunto | Arquivo em `data/` | IDs | Uso |
| --- | --- | --- | --- |
| Development/pilot set | `scenarios_development_pilot.json` | DEV001–DEV006 | Verificação técnica e desenvolvimento antes do congelamento |
| Test set oficial | `scenarios_ground_truth.json` | S001–S036 | Avaliação final após congelamento; nunca recalibrar o prompt com seus resultados |

Os seis casos novos foram escritos como eventos diferentes, sem reciclar os textos
oficiais. Cobrem atraso, decisão, problema de teste, mudança técnica, ação explícita
e informação sem efeito gerencial. Ambos os notebooks usam DEV001 para o exemplo
e DEV001–DEV006 para o piloto. A variável `scenarios` continua contendo somente os
36 casos oficiais; os lotes completos e suas métricas não recebem o piloto.

Os 36 IDs, textos, datas de ocorrência e tipos de fonte oficiais foram preservados.
Suas anotações foram revisadas, não seus eventos. Nenhuma chamada real à API foi
feita durante esta revisão. Respostas simuladas nos testes verificam software,
não desempenho científico. Os campos `expected_*` e `ground_truth_rationale`
nunca entram no input do LLM; nem relações do grafo são fornecidas ao baseline.

**Limitação histórica:** versões anteriores usaram seis dos casos oficiais como
piloto e já expuseram seu conteúdo durante o desenvolvimento. A separação atual
impede novas calibrações com eles, mas não torna esse conjunto retrospectivamente
inédito. Relate essa exposição no TCC; não o apresente como holdout nunca visto.

## Definições formais de anotação

- `primary_entity`: entidade sobre a qual o evento incide diretamente. Não é
  automaticamente o autor da mensagem, fornecedor que reporta ou responsável.
  Se o objeto não tiver ID no catálogo, use `null`, sem inventar entidade.
- `related_entities`: outras entidades explicitamente envolvidas no evento, mas
  que não são o objeto principal. Não repetir `primary_entity`. Sinônimos e
  referências inequívocas do catálogo são permitidos; dependência no grafo, por
  si só, não constitui menção explícita.
- `impacted_entities`: entidades cujo estado, execução, disponibilidade,
  especificação ou validação é ou pode ser alterado pelo evento. Pode incluir o
  objeto principal e consequências tecnicamente justificadas; não inclui um
  participante apenas por ter sido mencionado. Não é o fecho automático de
  alcançabilidade do grafo nem a saída do motor híbrido. Informações sem efeito
  gerencial têm lista vazia. O grafo/contexto do projeto é uma referência de
  anotação para impactos potenciais, não um algoritmo de geração do gabarito.
- `impacted_artifacts`: artefatos gerenciais que precisam de revisão segundo os
  critérios abaixo. No dataset histórico a chave equivalente é
  `expected_artifacts`; no JSON do baseline continua `impacted_artifacts`.
  Nenhum campo foi renomeado e o JSON das respostas foi preservado.

| Artefato | Evidência necessária |
| --- | --- |
| `risk_register` | Evento introduz, aumenta, materializa ou altera risco relevante |
| `status_report` | Evento altera ou pode alterar o estado atual do projeto |
| `decision_log` | Decisão tomada, aprovada, rejeitada, substituída ou alterada |
| `action_log` | Ação explícita, compromisso, responsável definido ou ação corretiva a acompanhar |

Não deduzir uma ação só porque uma falha tornaria uma investigação razoável.
Uma tarefa corretiva explicitamente ordenada pode exigir `action_log` mesmo
sem responsável nomeado. Registrar uma decisão não implica automaticamente uma
ação adicional; uma autorização expressa para executar/preparar uma tarefa pode
exigir ambos. Mudança já realizada de especificação documenta uma decisão técnica,
mas não inventa uma nova tarefa futura.

Para reduzir ambiguidades: atualização de desenho/BOM é representada por `T_CAD`;
consolidação gerencial de cronograma/status, sem nó próprio, por `AREA_PM`.
Referências ao conjunto fechado dos cinco ensaios identificam os cinco testes
do catálogo. Fornecedor novo, embalagem, sala ou documento sem ID não recebem IDs
inventados. O marco e a tarefa homônimos de liberação de engenharia são distinguidos
pelo evento (estado do gate versus execução da preparação/liberação).

A existência de impactos potenciais anotados com contexto técnico, não inteiramente
expresso no evento, é uma limitação para o baseline sem relações. Documente essa
assimetria ao comparar condições; não remova impactos apenas porque o LLM não os
previu e não acrescente regras que reproduzam as respostas esperadas de um caso.

## Revisão do ground truth antes do congelamento

`data/ground_truth_review_baseline_v2.json` registra a revisão dos **36 casos**,
com justificativa e diferenças antes/depois por campo. O commit de origem é
registrado. A revisão foi feita pelo assistente a partir de texto, catálogo e
critérios formais, sem consultar predições ou ajustar métricas para favorecer
baseline ou híbrido. Os campos temporais, responsáveis e classes de evento
preexistentes não foram alterados nesta revisão de entidades/impactos.

Principais correções: componente afetado em vez de fornecedor emissor; objeto da
ação em vez da pessoa responsável; componente defeituoso em vez do ensaio que
observa o defeito; exclusão de entidades relacionadas não mencionadas; separação
entre participante e entidade impactada; remoção de `action_log` sem tarefa
explícita e inclusão quando há tarefa expressamente autorizada. Alguns casos
permanecem iguais, com justificativa de manutenção.

Esta revisão de coerência não é dupla anotação independente. Antes de executar o
lote oficial, os dois autores devem revisar todos os 36 registros, reconciliar
ambiguidades e confirmar o congelamento. Se houver divergência antes do
congelamento experimental, corrigir o gabarito pelo critério, sem ver a saída do
LLM, registrar a decisão e atualizar os hashes em novo commit, preservando a tag
anterior. Não mover/recriar a tag já publicada para ocultar alterações.

## Congelamento e rastreabilidade

A tag `baseline-v2-frozen` identifica o **snapshot técnico estável** solicitado,
não comprova aprovação dos dois autores, disponibilidade real do modelo na API ou
execução científica. `baseline_v2_snapshot.json` registra modelo e hashes dos
artefatos desse snapshot. A disponibilidade do modelo precisa ser confirmada
com a conta do experimento; não substituir silenciosamente o modelo se falhar.

Antes do congelamento experimental, registrar:

1. Aprovação do ground truth pelos dois autores e resolução das ambiguidades.
2. Prompt V2 e seu SHA-256, modelo/identificador exato e parâmetros da chamada existente.
3. Hashes dos conjuntos e grafo, versões de Python/SDK e commit do código executado.
4. Encerramento do desenvolvimento usando somente DEV001–DEV006.

Depois do congelamento, **prompt, modelo e ground truth não podem ser alterados**
na rodada. Divergências e erros devem ser reportados; uma revisão futura constitui
outro protocolo/rodada, com resultados separados. Não ajustar o prompt após ver
o test set e não escolher o gabarito que favorece qualquer condição.

`RUN_FULL_EXPERIMENT = False` continua sendo o padrão. Ativá-lo só após as etapas
acima. Os outputs continuam em `outputs/baseline_v2/`; preserve qualquer rodada
anterior antes de executar, pois a rotina existente pode sobrescrever os arquivos.
Não misture os novos IDs DEV com arquivos de pilotos anteriores que usavam IDs S.

O parser, validador, chamada `client.responses.create`, JSON das respostas e
cálculo de métricas foram mantidos. O prompt não contém regras por cenário,
IDs de casos ou respostas esperadas. O helper histórico `src/tcc_agent/baseline.py`
e seus prompts em `outputs/prompts/` não são o prompt V2 experimental; o notebook
`TCC_Baseline_LLM.ipynb` é a fonte desse protocolo.
