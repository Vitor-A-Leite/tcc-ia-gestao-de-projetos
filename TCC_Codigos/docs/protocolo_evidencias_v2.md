# Protocolo V2 — conclusões sustentadas sobre prazo e custo

**Estado:** implementação local, versão de desenvolvimento. Regras e exemplos
aguardam revisão independente do domínio. Não substitui o experimento legado nem
constitui evidência de que uma arquitetura é superior.

## Objetivo e decisão de desenho

Avaliar a resposta a uma pergunta específica: **qual é o efeito em prazo ou custo
de uma entidade, e a informação disponível permite concluir isso?** O fato de
existir uma conexão no grafo não basta para afirmar impacto.

As duas condições usam o mesmo contrato, perguntas, regras de suficiência,
formato de resposta, validação e critérios de providência. O baseline recebe o
texto, catálogo e fatos comuns; o híbrido recebe também as arestas do grafo. Uma
relação explicitamente informada no texto pode ser usada nas duas condições. O
baseline não recebe relações ocultas, referências ou propostas de resposta do motor.

Essa configuração mede o benefício do conhecimento adicional e da arquitetura,
não o efeito puro da representação em grafo. Para isolar representação, seria
necessário outro experimento com o mesmo conhecimento disponibilizado nas duas
condições, apenas em formatos diferentes.

## Unidade de avaliação

Cada pergunta tem uma **entidade de destino** e uma **dimensão** (`schedule` ou
`cost`). Prazo usa dias do modelo declarado; custo usa BRL. Atraso no componente,
atraso na montagem e atraso na entrega final são perguntas diferentes.

Cada resposta contém:

- `status`: `supported`, `no_impact` ou `undetermined`;
- `direction`: `increase`, `decrease`, `none` ou `unknown`;
- `delta`: variação líquida, ou `null` quando desconhecida;
- `unit`: `days` ou `BRL`;
- IDs das evidências, lacunas, justificativa e providências recomendadas.

Prazo positivo significa atraso; negativo, adiantamento. Custo positivo significa
aumento; negativo, redução. **Zero exige evidência de ausência de efeito.** A
falta de dados não pode ser convertida em zero.

A direção pode ser sustentada sem que a magnitude seja conhecida. Por exemplo,
um aumento de custo explicitamente relatado, mas ainda sem valor, admite
`supported/increase` e `delta=null`. Isso não autoriza inventar a quantia.

Confiança subjetiva da IA não é prova e não faz parte desse contrato. O sistema
não valida a veracidade externa de uma mensagem: avalia inferências condicionais
sobre informações registradas com proveniência.

## Evidências e informações faltantes

Cada fato tem ID, entidade, predicado, valor, fonte e trecho exato. O carregamento
confere ID único, entidade, predicado, tipo, finitude numérica e existência do
trecho na fonte. **Isso não é validação semântica automática da anotação:** quem
prepara o conjunto deve conferir que o predicado e o valor representam o texto.
A primeira versão isola raciocínio com fatos anotados. A extração desses fatos a
partir de texto livre é uma tarefa separada e não está sendo pontuada aqui.

O modelo só pode citar fatos efetivamente visíveis à sua condição. O verificador
recalcula a conclusão usando o subconjunto citado. Citar um ID existente, mas
irrelevante ou insuficiente, não passa. Contradições no contexto completo não
podem ser escondidas pela escolha de apenas uma fonte.

Lacunas usam os códigos canônicos descritos em `missing_information_format` na
entrada: por exemplo, `buffer_days:T_ASSEMBLY`. As instruções das duas condições
incluem o mesmo vocabulário. O avaliador verifica completude das lacunas exigidas
pela regra; a justificativa em linguagem natural não é pontuada por um juiz LLM.

## Política temporal implementada

1. Uma variação líquida diretamente informada vale apenas para a entidade citada.
2. `required_for` e `precedes` podem propagar prazo somente com o modelo declarado
   `finish_to_start_with_buffer`, confirmação de que outras restrições permanecem
   inalteradas, informação sobre alternativa pronta e folga aplicável.
3. Sem alternativa, o atraso transmitido é `max(0, atraso de origem − folga)`.
   Alternativa pronta e suficiente absorve o efeito sob as hipóteses declaradas.
4. Adiantamento depende de permissão explícita, folga zero e demais condições do
   modelo. Outras combinações ficam indeterminadas.
5. Convergência de mais de um predecessor alterado exige cronograma e folgas por
   predecessor. O sistema não usa ingenuamente a soma nem o máximo dos atrasos.
6. `belongs_to`, `validated_by` e `supplies` não propagam prazo/custo nessa versão.
   O atraso relatado do motor pode ser anotado diretamente no motor; uma relação
   fornecedor–componente sozinha não quantifica sua disponibilidade.
7. Ausência de caminho, ciclos ou condições insuficientes não provam ausência de
   impacto. Não há truncamento que transforme falta de informação em conclusão.

Não é um mecanismo geral de caminho crítico ou de replanejamento. Calendários,
recursos, concorrência, substituições parciais e restrições mais complexas exigem
outro modelo explícito. O motor não extrapola o efeito da montagem ao prazo final
sem evidência para cada etapa.

## Política financeira implementada

- Variação líquida direta e direção explícita podem sustentar a conclusão no
  escopo da entidade.
- Um atraso não aumenta custo automaticamente.
- Custo indireto de atraso exige diária não negativa e declaração de que esse
  modelo representa **toda a variação líquida de custo** naquele escopo.
- Com esses dados, calcula-se diária × atraso sustentado. Aritmética usa Decimal.
- Diária zero e modelo líquido completo podem provar ausência de custo adicional,
  mesmo quando o prazo ainda é desconhecido.
- Adiantamento não gera economia automaticamente. No modelo que contempla somente
  custos adicionais de atraso, antecipação implica zero desse componente de custo;
  economia requer evidência própria.

## Providências: recomendações, sem execução automática

| Resultado | Providência |
|---|---|
| Prazo alterado sustentado | Revisar cronograma e status |
| Custo alterado sustentado | Revisar orçamento e status |
| Ausência de impacto sustentada | Registrar evidência |
| Informação insuficiente | Solicitar informação |
| Fontes contraditórias | Resolver conflito de informação |

Não se presume decisão tomada, ação corretiva aprovada ou necessidade de alterar
um registro só porque seria possível imaginar uma consequência. O módulo não
modifica os quatro documentos legados e não cancela compras, altera prazos ou
aprova gastos.

## Referências e justiça da comparação

Há duas perguntas diferentes:

1. **A conclusão era correta e sustentada pelo contexto que aquela condição viu?**
2. **Ela coincide com o resultado de referência usando o contexto completo?**

Essas medidas são reportadas separadamente. Se o baseline não conhece uma
dependência, a resposta correta para aquele contexto pode ser `undetermined`,
enquanto o híbrido consegue concluir com a relação e parâmetros disponíveis.
Isso evita tratar uma abstenção justificada como alucinação. Por outro lado,
abster-se quando há evidência suficiente também conta como erro.

As referências são registradas manualmente por condição. O motor não gera nem
reescreve as referências. Se suas regras divergem da referência registrada, a
avaliação sinaliza `reference_rule_agreement=false` e reprova o caso para revisão.
A referência não deve ser alterada apenas para fazer o motor passar.

Não há um único placar ponderado que esconda afirmações indevidas. São reportados
acerto de conclusão (estado/direção), acerto de magnitude, precisão numérica
indevida, acerto completo com contexto visível, resultado com contexto completo,
evidência, lacunas,
providência, conclusões perdidas e afirmações não sustentadas. Respostas ausentes,
duplicadas ou inválidas não são descartadas para melhorar a métrica.

## Exemplos de desenvolvimento e limites científicos

`data/evidence_protocol_v2_examples.json` contém 15 exemplos hipotéticos,
identificados como `development_rule_example` e `draft_needs_domain_review`.
Folgas, diárias e antecipações desses exemplos são **hipóteses de teste**, não
fatos acrescentados ao Projeto Alfa. Cada exemplo consulta prazo e custo nas
duas condições, totalizando 60 perguntas.

A demonstração usa respostas do próprio motor para testar sua compatibilidade
com referências autorais e com seu certificado de evidência. Isso é teste de
software; **não mede uma IA, não constitui revisão independente e não demonstra
superioridade do híbrido**. O relatório mantém esse rótulo.

Antes de executar um novo experimento real: revisar regras e anotações com o
orientador/especialista, produzir casos independentes não usados no desenvolvimento,
fixar modelo e parâmetros, registrar custos/tempos e executar repetições conforme
o protocolo. Os seis casos do piloto antigo já vistos não são um teste independente.
Os 36 cenários legados não possuem referências suficientes de prazo/custo e não
foram automaticamente rotulados como impacto zero.

## Como executar localmente, sem API

Na raiz do repositório, com Python 3.10+:

```sh
python3 TCC_Codigos/scripts/test_offline.py
python3 TCC_Codigos/scripts/evaluate_evidence_protocol.py --output TCC_Codigos/outputs/nova_demonstracao_v2
```

A pasta deve ser nova. O comando exporta:

- `requests_without_references.jsonl`: entradas sem gabarito, para cada condição;
- `evaluations.jsonl`: respostas demonstrativas e verificação por pergunta;
- `summary.json`: medidas separadas e avisos de escopo.

Para avaliar respostas reais coletadas separadamente, o JSONL deve conter
`case_id`, `condition` e `prediction`, cobrindo todos os casos nas duas condições:

```sh
python3 TCC_Codigos/scripts/evaluate_evidence_protocol.py --predictions previsoes.jsonl --output TCC_Codigos/outputs/nova_avaliacao_v2
```

O adaptador `call_model(client, model, case_id, context, questions, condition)`
usa o mesmo prompt e Structured Outputs nas duas condições. Recebe o cliente,
não carrega chaves e não é chamado automaticamente por nenhum comando acima.
Foi testado com cliente simulado; nenhuma nova chamada à API foi feita para este
protocolo. O adaptador não envia referências nem conclusões do motor para o LLM.
Respostas brutas inválidas são preservadas para auditoria.

## Onde está a implementação

- `src/tcc_agent/evidence_assessment.py`: contrato, contexto, regras, prova e avaliação.
- `scripts/evaluate_evidence_protocol.py`: demonstração e avaliação de previsões externas.
- `tests/test_evidence_assessment.py`: regressões e contraprovas.
- `data/evidence_protocol_v2_examples.json`: exemplos autorais e referências por contexto.

Nenhum grafo, gabarito, prompt ou resultado legado foi substituído.

## Revisão V2.1: escopo e medida temporal

A [revisão dos critérios e gabaritos](revisao_criterios_gabaritos_v2_1.md) separa
início, duração, entrega, progresso e término. O avaliador V2.0 acima não distingue
essas medidas e continua restrito aos modelos declarados dos exemplos de desenvolvimento.
Não converter automaticamente os novos gabaritos para `schedule_delta_days` genérico.
Foram preparadas referências autorais dos 36 relatos; faltam revisão independente,
cobertura financeira e casos reservados antes do próximo experimento real.
