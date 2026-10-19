# Revisão dos critérios e gabaritos de prazo e custo — V2.1

Estado: **referências autorais preparadas para revisão independente; sem novas chamadas à API**.
Esta revisão não altera o grafo, os 36 cenários legados ou os resultados anteriores.

## O que estamos medindo

A pergunta é: **dado este relato e este contexto, qual variação é sustentada neste escopo?**
A resposta é condicional ao relato recebido, não uma confirmação externa de sua veracidade.
Não avaliamos aprovação de gastos, execução de correções ou alteração automática de documentos.

A unidade é uma pergunta identificada por cenário, entidade, atividade, dimensão e medida:

- Prazo: entrega, disponibilidade, início, término, duração ou desvio de progresso.
- Custo: variação **líquida** do custo no escopo explicitado, em BRL no contrato experimental.
- Local: somente o fornecimento ou atividade descrito; não toda a entidade quando o nó representa algo mais amplo.
- Projeto: término da liberação de engenharia e custo total associado ao evento, consultados separadamente.

Cada cenário é independente. Não somar o atraso do S001 ao S028 nem incorporar a decisão do
S007 a outro cenário. O evento e sua data são comuns às condições. Os documentos de status e
logs não têm histórico suficiente por cenário e ficam fora desta versão; datas neles não
substituem uma linha de base e uma situação atual comparáveis. Não se afirma que esses
documentos sejam inúteis: sua inclusão exige seleção temporal e proveniência explícitas.

## Critérios revisados

| Critério | Evidência necessária | Inferência proibida sem dados adicionais |
|---|---|---|
| Mudança de prazo | Direção explicitamente relatada ou valores comparáveis da mesma medida e escopo | Converter uma data absoluta em atraso |
| Medida temporal | Identificar se o relato trata de início, entrega, duração, progresso ou término | Igualar atraso de início ao atraso de conclusão |
| Risco | Registrar possibilidade e pedir confirmação/parâmetros | Tratar “pode consumir três dias” como atraso confirmado de três dias |
| Compromisso/decisão | Distinguir autorização, prazo de ação e efeito efetivo | Tratar aprovação ou promessa como execução ou mudança comprovada |
| Ausência de efeito | Declaração explícita ou modelo completo que demonstre zero naquele escopo | Transformar dado ausente, evento informativo ou ausência de caminho em zero |
| Custo | Variação líquida com moeda/escopo, ou modelo financeiro completo e parâmetros | Inferir sobrecusto por atraso, defeito ou peça de maior capacidade |
| Evidência | Fonte, trecho, data, escopo e condições acessíveis àquela condição | Usar o gabarito, outro cenário ou informação só disponível ao híbrido |
| Contradição | Resolver fontes conflitantes ou manter indeterminação | Selecionar apenas a evidência conveniente |

`status` tem três valores: `supported`, `no_impact`, `undetermined`. A direção pode ser
conhecida sem magnitude; nesse caso, `supported` com `delta=null`. Indeterminação também usa
`delta=null`, mas direção `unknown`. Zero é reservado à ausência sustentada. Dias sem
qualificação na fonte permanecem com base de calendário não especificada; não calculamos
novas datas nem convertemos para dias úteis. “Informativo” não é um veto universal a respostas:
o S035 sustenta manutenção do prazo do fornecimento, sem provar ausência de todo impacto.

## Relações e condições para propagação

Os tipos existentes são relações estruturais cadastradas, não certificados causais.

| Relação | Uso permitido com informação suficiente | Condições a verificar |
|---|---|---|
| `supplies` | Associar fornecimento à disponibilidade da peça | Peça/lote/quantidade corretos, entrega confirmada e disponibilidade útil; não propagar a toda a cadeia |
| `required_for` | Verificar se a indisponibilidade bloqueia a atividade | Data de necessidade, suficiência do material, substituição, folga e demais restrições |
| `precedes` | Avaliar uma restrição de sequência | Confirmar vínculo temporal e defasagem; o nome da aresta sozinho não prova finish-to-start |
| `validated_by` | Identificar requisito de aceitação/liberação | Critério de aprovação, necessidade de reteste, duração e momento de liberação |
| `belongs_to` | Encaminhar análise à área responsável | Não transmite automaticamente atraso ou custo à área |

Uma cadeia só sustenta o efeito final se cada passagem estiver justificada. Para um modelo
simples explicitamente declarado de término–início, sem alternativa, com duração e demais
restrições constantes, o atraso transmitido pode ser `max(0, atraso de disponibilidade − folga)`.
Isso **não** é regra universal para qualquer aresta. Mais de um predecessor alterado exige
cronograma e restrições por predecessor; não se somam atrasos indiscriminadamente.

Para custo de atraso, `diária × atraso` exige declaração de que o modelo cobre a variação
líquida naquele escopo. Custo de reteste, frete e retrabalho não pode ser ignorado para afirmar
custo total zero. Antecipação não implica economia. Modelos parciais respondem somente sobre
seu componente de custo e não sobre o orçamento completo.

## Providências compatíveis

| Conclusão | Recomendação |
|---|---|
| Alteração de prazo sustentada | Conferir previsão, revisar cronograma/status do escopo; investigar repercussão posterior |
| Alteração de custo sustentada | Revisar orçamento/status com a evidência financeira |
| Zero sustentado | Registrar evidência e limitar a conclusão ao escopo |
| Indeterminado | Solicitar as informações listadas antes de concluir |
| Fontes conflitantes | Resolver conflito antes de atualizar previsão |

Um risco pode justificar análise de risco mesmo com prazo/custo indeterminados. Essas
providências não equivalem a decisões aprovadas nem substituem os critérios dos documentos
legados. O gabarito lista recomendações; o sistema não executa alterações.

## Gabaritos preparados e cobertura observada

Fonte: `data/scenarios_ground_truth.json` (36 relatos) e `data/project_graph.json`
(catálogo e 65 arestas). O JSON de referências registra SHA-256 de ambas as fontes.
As respostas foram anotadas nesta revisão, sem chamar o motor para gerar gabaritos e sem
copiar as listas legadas de entidades impactadas. São referências autorais, ainda sem
concordância de especialista independente.

Arquivo: `data/reference_sets/alfa_schedule_cost_v2_1_draft.json`.

Há 136 perguntas por condição: 68 de prazo e 68 de custo. São 32 pares locais e
36 pares do projeto. S009, S022, S027 e S034 consultam apenas o projeto: não há uma
atividade local adicional adequadamente identificada para essas perguntas.

| Dimensão, em cada condição | Alteração sustentada | Zero sustentado | Indeterminado |
|---|---:|---:|---:|
| Prazo | 5 | 1 | 62 |
| Custo | 0 | 0 | 68 |

As cinco alterações de prazo são: S001 entrega do motor +10; S008 início do teste +4;
S014 entrega da placa +7; S021 atraso de progresso da usinagem +5; S029 início da revisão
do relatório +3. S035 sustenta prazo inalterado somente no fornecimento citado.
Nenhum desses relatos determina numericamente a variação da liberação final.

Nos dados atuais, as referências coincidem entre baseline e híbrido: o grafo não acrescenta
folgas, calendários ou parâmetros financeiros suficientes para mudar essas conclusões.
Isso é resultado da inspeção das fontes, não meta de equilíbrio entre arquiteturas.

**Limitação central:** responder “indeterminado” a tudo acertaria 130/136 perguntas
(95,6%) por condição. Acurácia global isolada seria enganosa. O conjunto testa principalmente
contenção de inferências e reconhecimento de efeitos locais; não mede adequadamente
capacidade de calcular custos, adiantamentos, economias ou ganho do contexto estrutural.

## Comparação justa e próximos gabaritos

Mesmos critérios, perguntas, catálogo, relato e formato nas duas condições; só o híbrido recebe
as arestas. Respostas sustentadas pelo contexto visível e coincidência com resultado de
contexto completo continuam medidas separadas. Para comparar apenas representação em grafo,
seria necessária condição adicional com o mesmo conhecimento em texto.

As entidades e atividades consultadas já estão identificadas nas perguntas fornecidas às duas
condições. Este conjunto avalia raciocínio sobre perguntas delimitadas, não a capacidade de
extrair sozinho todas as entidades ou todos os impactos relevantes de um texto livre. Essa
extração deve ter avaliação própria, sem receber as anotações de referência como entrada.

Antes de novas chamadas, preparar casos com dados suficientes para as células abaixo,
com fontes do projeto ou hipóteses explicitamente rotuladas, nunca acrescentadas como fatos reais:

| Célula necessária | Dados para gabarito justificável |
|---|---|
| Atraso transmitido | Entrega, necessidade, vínculo temporal, folga, alternativas e outras restrições |
| Atraso absorvido / zero | Mesmos dados e evidência de folga suficiente ou alternativa realmente pronta |
| Antecipação | Antecipação da origem e permissão/condições para antecipar o destino |
| Custo maior | Variação líquida direta ou modelo completo com preços, quantidades e custos aplicáveis |
| Custo menor | Economia líquida demonstrada, incluindo custos adicionais de mudança |
| Custo zero | Declaração de ausência de variação líquida ou cálculo completo com resultado zero |
| Indeterminação | Omissões identificáveis; separar informação essencial ausente de contexto irrelevante |
| Conflito | Fontes incompatíveis com data/escopo comparáveis e regra de resolução |

Os 15 exemplos V2.0 já cobrem parte dessas células como **desenvolvimento hipotético**.
Não são promovidos a avaliação independente. Os 36 cenários e o piloto também já foram
inspecionados. O conjunto final deve reservar casos novos, fixar referências antes das
previsões, registrar revisão por especialista e divergências/adjudicação, e separar conjuntos
por família causal/template para reduzir vazamento. Não há tamanho amostral ou limiar de
superioridade validado nesta preparação.

Reportar acertos por estado, direção, medida e dimensão, afirmações indevidas, abstenções
justificadas, conclusões perdidas, magnitude, evidência e providência. Perguntas do mesmo
cenário são correlacionadas: não tratar 272 respostas como 272 casos independentes. A
comparação é pareada por cenário; definir repetições e análise de incerteza antes da execução.

## Auditoria offline e compatibilidade

```sh
.venv/bin/python TCC_Codigos/scripts/audit_schedule_cost_references.py --output TCC_Codigos/outputs/nova_revisao
.venv/bin/python TCC_Codigos/scripts/test_offline.py
```

A pasta de saída precisa ser nova. O pacote contém auditoria, hashes, caderno de revisão
por pergunta e entradas sem respostas para as duas condições. Não carrega `.env`, não usa
credenciais e bloqueia rede. A auditoria confere integridade, cobertura, citações e coerência
estrutural; **não certifica a interpretação semântica nem avalia a IA**.

O avaliador V2.0 usa apenas entidade/dimensão e `schedule_delta_days` genérico. Ele não pode
receber estas referências por adaptação automática: primeiro deve incorporar medida e escopo,
com testes de que atraso de início ou progresso não se transforma em atraso de término.
Os pacotes V2.1 são de revisão, não arquivos de execução do runner antigo. O indicador
`approved_for_real_runs=false` é deliberado; nenhum comando desta revisão chama a API.

A liberação para experimento exige revisão independente das referências, cobertura adequada,
casos reservados e executor/avaliador compatíveis, com hashes da configuração congelada.
