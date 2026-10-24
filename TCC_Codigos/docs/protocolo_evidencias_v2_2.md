# Protocolo V2.2 — medidas de prazo e casos de custo

Implementado localmente, sem novas chamadas à API. Os 34 casos são hipóteses autorais de
desenvolvimento, com gabaritos explícitos por condição. Não são novos fatos do Projeto Alfa,
casos independentes de avaliação ou resultados de modelos de linguagem.

## O que mudou no avaliador

Uma pergunta agora tem `question_id`, `target`, `scope`, `dimension`, `measure` e `day_basis`.
A resposta deve preservar todos esses campos. O avaliador rejeita troca de escopo, base,
entidade ou medida, além de perguntas ausentes, repetidas ou desconhecidas.

| Medida | Significado | O que ela não prova sozinha |
|---|---|---|
| `start` | Deslocamento do início | Mesmo deslocamento no término |
| `delivery` | Deslocamento da entrega | Disponibilidade útil, início ou término de outra atividade |
| `progress_variance` | Desvio de progresso relatado em dias | Nova previsão de entrega ou término |
| `finish` | Deslocamento do término | Momento da entrega ou efeito em outro marco |
| `duration` | Variação da duração | Deslocamento de término sem saber início/restrições |
| `availability` | Deslocamento da disponibilidade útil | Efeito em toda a cadeia |
| `net_cost` | Variação líquida do custo no escopo, em BRL | Mesma variação no custo total do projeto |

Escopos diferentes do mesmo nó são diferentes coordenadas: por exemplo, `lot_A` e `lot_B`.
Bases temporais também são diferentes: `calendar_days`, `working_days` e `unspecified`.
Sem calendário explícito, o módulo não converte dias úteis em corridos. Custo usa
`not_applicable` como base própria; seu modelo pode referenciar uma base temporal específica.

Não há conversão automática entre medidas. O protocolo V2.0, com `schedule_delta_days`
genérico, permanece separado para preservar suas hipóteses e resultados. Os novos casos
usam `2.2-draft`; versões desconhecidas são rejeitadas. Os gabaritos de revisão V2.1 dos
36 cenários continuam em seu formato autoral, sem conversão silenciosa para deltas genéricos.

## Evidências e modelos aceitos

Cada fato tem ID, fonte, trecho, coordenada completa, tipo e parâmetros. O carregamento verifica
integridade estrutural, tipos, números finitos, sinal de folga/diária e presença literal do trecho.
A correspondência semântica entre trecho e anotação continua responsabilidade da revisão do domínio.
Os fatos são anotados: esta etapa isola raciocínio, não testa extração de texto livre.

- `delta`: variação explícita na coordenada consultada.
- `comparison`: atual menos linha de base comparável. Posições temporais são índices em dias,
  com mesma origem e base declaradas, não datas convertidas automaticamente. Custo exige totais
  líquidos comparáveis no mesmo escopo e moeda.
- `direction`: direção explícita; admite magnitude desconhecida. “Sem alteração” sustenta zero.
- `fixed_duration`: permite deslocamento igual de início para término, somente com duração
  e demais restrições constantes. Não converte progresso em previsão ou término em entrega.
- `dependency_shift`: modelo condicional de bloqueio do início por entrega, disponibilidade ou
  término de um predecessor. Exige aresta visível `required_for`/`precedes`, medida de origem,
  mesma base de dias, folga, alternativa pronta/suficiente e demais restrições constantes.
- `delay_cost`: exige diária não negativa, medida temporal contratada, base de dias e confirmação
  de que essa é toda a variação líquida de custo naquele escopo. Modelos parciais não bastam.

No vínculo temporal simples, sem alternativa, `max(0, atraso da origem − folga)` determina
o desvio do início. Com alternativa pronta e suficiente, o efeito é absorvido sob as
hipóteses declaradas. Antecipação requer permissão e folga zero; se explicitamente impedida,
o início fica inalterado. Antecipação com folga positiva exige outro modelo e fica indeterminada.

Uma cadeia precisa de todas as relações e modelos. Mais de um predecessor exige cronograma
por predecessor; o módulo não soma nem escolhe o maior deslocamento. Ciclos ficam indeterminados.
`supplies`, `validated_by` e `belongs_to` não transmitem quantidades neste modelo.
Não haver caminho não prova ausência de efeito.

Para custo, a diária incide somente sobre atraso positivo da medida contratada. Antecipação não
gera economia automática. Diária zero com modelo líquido completo sustenta zero, mesmo sem
conhecer o prazo. Economia exige referência financeira própria; queda de preço unitário sem
quantidade/frete/outras parcelas não demonstra economia líquida.

O módulo considera divergências entre fontes e entre fonte direta e modelo. Não é possível
esconder um conflito disponível citando apenas a evidência conveniente. Uma conclusão
numérica exige prova numérica; uma direção conhecida com `delta=null` não autoriza inventar valor.

## Critérios comuns às condições

O baseline e o híbrido recebem os mesmos fatos comuns, modelos condicionais, perguntas,
instruções, esquema de resposta e critérios de providência. O híbrido recebe também as
arestas do grafo hipotético. Um modelo condicional não substitui uma aresta identificando
um predecessor. Quando a relação é explicitada no texto, as duas condições podem usá-la:
o SC32 testa exatamente isso.

Referências e justificativas não entram nos pedidos exportados. O avaliador compara:

1. Conclusão e magnitude com o gabarito autoral do contexto visível.
2. Afirmação com o contexto disponível e com o subconjunto de provas citadas.
3. Completude das lacunas e compatibilidade das recomendações.
4. Resultado com a referência de contexto completo, em métrica separada.

Referência e motor podem divergir: o relatório sinaliza a divergência e reprova para revisão,
sem reescrever o gabarito. Declarar indeterminação apesar de evidência suficiente conta como
conclusão perdida. Registros inválidos continuam no denominador, inclusive nas subdivisões.

As métricas são apresentadas por dimensão, medida, estado esperado e direção esperada,
além das medidas globais. Perguntas do mesmo cenário são correlacionadas, não repetições
estatísticas independentes. Igualdade de critérios não implica igualdade de respostas quando
um contexto possui conhecimento adicional. Esta configuração avalia arquitetura mais conhecimento,
não o efeito puro da representação em grafo.

## Cobertura dos 34 casos adicionais

São 92 perguntas por condição (72 temporais e 20 financeiras), ou 184 respostas nas duas condições.

| Dimensão e condição | Alteração sustentada | Zero sustentado | Indeterminado |
|---|---:|---:|---:|
| Prazo — baseline | 23 | 2 | 47 |
| Prazo — híbrido | 33 | 8 | 31 |
| Custo — baseline | 5 | 2 | 13 |
| Custo — híbrido | 8 | 6 | 6 |

Ambas as dimensões incluem aumento e redução. A cobertura foi ampliada deliberadamente,
mas a amostra não está estatisticamente balanceada nem representa frequências reais de ocorrência.

- SC01–SC07: medidas distintas, comparação com base e duração constante.
- SC08–SC13: folga, alternativa, antecipação e restrições insuficientes.
- SC14–SC21: custo maior, menor, zero, direção sem magnitude, preço parcial e escopo financeiro.
- SC22–SC26: lotes, calendários, conflitos, predecessores múltiplos e relação não temporal.
- SC27–SC34: cadeia completa, duração isolada, magnitude ausente, desvios diferentes, conflito
  entre modelo/fonte, relação textual comum, aritmética decimal e risco/data sem desvio confirmado.

Exemplos numéricos: SC08 tem entrega +10 dias, folga 3, início +7 e término +7 somente com
duração constante; custo líquido +R$ 1.400 com diária de R$ 200 por dia de atraso no término.
SC09 tem folga 12 e absorve o atraso. SC15 declara totais líquidos de R$ 1.000 e R$ 800,
sustentando economia de R$ 200. Esses números são hipóteses de desenvolvimento.

## Execução local sem API

Na raiz superior do repositório:

```sh
.venv/bin/python TCC_Codigos/scripts/test_offline.py
.venv/bin/python TCC_Codigos/scripts/evaluate_evidence_protocol.py --cases TCC_Codigos/data/evidence_protocol_v2_2_cases.json --output TCC_Codigos/outputs/nova_validacao_v2_2
```

A pasta precisa ser nova. O comando bloqueia sockets, não carrega `.env`, não instancia cliente
nem usa credenciais. A demonstração injeta respostas do motor e as confere contra referências
autorais: é validação do software, não teste de IA. O modo sem `--cases` preserva os 15 exemplos V2.0.

Para respostas externas, o mesmo comando aceita `--predictions previsoes.jsonl`, com
`case_id`, `condition` e `prediction` para todos os casos e condições. Não faz chamadas à API.
As entradas exportadas incluem contrato, regras e esquema JSON V2.2. O antigo adaptador
`call_model` V2.0 não deve ser usado com essas perguntas; não há coleta real V2.2 nesta etapa.

Arquivos principais:

- `src/tcc_agent/scoped_evidence.py`: perguntas, fatos, modelos, prova e avaliação V2.2.
- `data/evidence_protocol_v2_2_cases.json`: hipóteses e gabaritos por condição, com justificativas.
- `scripts/evaluate_evidence_protocol.py`: seleção explícita de versão, exportação e avaliação offline.
- `tests/test_scoped_evidence.py`: regressões e contraprovas.
- `outputs/protocolo_v2_2_validacao_20261022/`: resultados demonstrativos e contraprova de troca de medida.

## Situação para o próximo experimento

Os casos e o avaliador estão prontos para revisão local. Nenhuma chamada nova à IA foi feita.
As referências são autorais e os casos foram usados no desenvolvimento: não são promovidos
à avaliação independente. Antes da coleta final, revisar os modelos e gabaritos com especialista,
separar casos novos por família causal/template, congelar fontes/configuração e definir
repetições/análise pareada. Manter hipóteses separadas dos fatos reais do projeto e relatar
a diferença entre extração de texto, raciocínio controlado e avaliação do sistema completo.
