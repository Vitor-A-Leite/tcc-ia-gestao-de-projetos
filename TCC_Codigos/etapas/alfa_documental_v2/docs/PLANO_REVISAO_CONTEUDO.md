# Plano de revisão do conteúdo documental

Data: 20/11/2026. Escopo: Alfa documental v2. Situação em 21/11/2026: **F0 a F4 implementadas offline; F5 (rodada real) e F6 (interface) pendentes**. Ver "Estado da implementação" ao final.

## Pergunta

Dada uma mudança, o sistema já responde *quais documentos são impactados* (triagem por vínculos) e, para o Status Report, *quais campos cadastrados divergem do cálculo*. Falta responder, para o conteúdo real dos documentos:

1. **Quais informações** o documento afirma sobre o projeto.
2. **Quais delas** ficaram desatualizadas, continuam válidas ou não podem ser verificadas.
3. **Por quê**, com a mudança de origem, o caminho no grafo e o trecho do documento.

O foco é rastreabilidade: ligar cada afirmação de um documento a uma entidade do grafo e cada recomendação a uma cadeia causal conferível. Prazo e custo entram como duas das grandezas verificáveis, não como o objetivo.

## Ponto de partida

| Já existe | Onde | Limite |
|---|---|---|
| Comparação campo a campo de cinco afirmações do Status Report | `src/documentos.py::verificar` | Afirmações estruturadas à mão (`afirmacao={entidade,campo,valor,unidade}`); sem leitura de prosa |
| Estados `revisar`, `ja_atualizado`, `nao_verificavel`; recomendação com evidências e arestas | idem | Justificativa genérica; evidências incluem todas as arestas ancestrais (49 fontes no D02) |
| Triagem de Action Log, Risk Register e Decision Log por vínculos | idem | Estado `avaliacao_especifica_pendente`; regras escritas, mas não aplicadas ao conteúdo |
| IA extrai afirmações de texto; código compara (`fundamentos_valor`, `restricoes_escopo`) | `src/revisao.py`, `src/evidencias_revisao.py` (contrato v3) | Aplicado a propostas de alteração, não a documentos |
| Transporte real com reservas, carteira histórica e teto de US$20 | `src/ia_real.py`, `src/auditoria.py` | Comprometido até 11/11/2026: US$4,955 |

A extensão reutiliza o princípio já validado no revisor v3: **a IA extrai, o código compara**. A IA não decide se um documento está desatualizado; ela diz o que o documento afirma, com citação literal, e o código confronta essa afirmação com o estado calculado.

## Fluxo proposto

```
documento@versão (prosa)
   │  1. extração de afirmações (IA, uma vez por versão do documento)
   ▼
afirmações estruturadas + trecho literal + entidade + predicado
   │  2. validação do contrato (código): citação literal, entidade existe, predicado/campo/unidade permitidos
   ▼
cadastro de afirmações (hash; opcionalmente confirmado por humano)
   │  3. avaliação por cenário (código): predicado × estado calculado
   ▼
estado por afirmação + motivo tipado
   │  4. explicação rastreável (código): caminho determinante mudança → entidade
   ▼
"O que revisar e por quê" (recomendação pendente de validação humana)
```

### Decisão central: extrair uma vez por versão do documento

O que um documento afirma não depende do cenário. O Status Report `STATUS@1` diz "motor no dia 18" em D01, D02 ou D08. Por isso a extração é feita **uma vez por `documento@versão`** e vira um cadastro com hash, no mesmo formato de `afirmacao` que `verificar` já consome. A avaliação por cenário é determinística e não gasta chamadas.

Consequências:

- O custo de IA cresce com o número de versões de documentos, não com o número de mudanças.
- A extração pode ser conferida por uma pessoa antes do uso ("cadastro assistido"), o que separa erro de extração de erro de avaliação na análise dos resultados.
- O caminho atual (afirmações cadastradas à mão) vira a linha de base para comparar.

## 1. Extração de afirmações (IA)

Entrada: os trechos do documento com IDs, o catálogo de entidades do grafo (ID, nome, tipo, aliases) e o catálogo de predicados abaixo. Sem resultados do cálculo, sem cenário, sem referências de avaliação.

Saída por afirmação:

| Campo | Conteúdo |
|---|---|
| `trecho_id` + `citacao` | Trecho de origem e substring literal que sustenta a afirmação |
| `entidade` | ID do catálogo; `null` se o texto não identifica uma entidade |
| `predicado` | Um item do catálogo |
| `campo`, `valor`, `unidade` | Quando o predicado exige |
| `conhecimento` | `exato`, `indeterminado`, `alternativas`, `ausente` (mesmo vocabulário do v3) |
| `referencia_temporal` | `absoluta` (D18), `relativa` ("semana 3"), `implicita` |
| `justificativa` | Curta; por que a citação expressa esse predicado |

Trechos sem afirmação verificável são listados como `nao_mapeado` com a razão. Isso evita que a cobertura pareça maior do que é.

### Catálogo de predicados (avaliados pelo código)

| Predicado | Exemplo de prosa | Regra de avaliação |
|---|---|---|
| `valor(entidade, campo)` | "A MotorTech entrega no dia 18" | Igualdade com o estado calculado; indeterminado não vira zero |
| `sem_alteracao(entidades, campo)` | "Os demais fornecedores seguem no previsto" | Nenhuma das entidades consta em `nos_com_mudanca_*` |
| `no_prazo(marco)` | "Projeto dentro do cronograma" | `fim_novo ≤ fim` vigente do marco |
| `dentro_orcamento()` | "Sem desvio de custo" | `custo_novo ≤ custo` vigente |
| `critico(entidade)` / `nao_critico(entidade)` | "A montagem tem folga" | Folga projetada = 0 ou > 0 |
| `versao(artefato)` | "CAD na revisão 1" | Igualdade com versão cadastrada |
| `compromisso(acao, responsavel, prazo, estado)` | "A-01, Carla, até D12, aberta" | Regra do Action Log (seção 3) |
| `risco(evento, estado)` | "R-01 em monitoramento" | Regra do Risk Register (seção 3) |
| `decisao(id)` | "DEC-01 mantém a arquitetura" | Regra do Decision Log (seção 3) |

O catálogo é fechado e versionado. Uma afirmação que não cabe nele não é forçada a caber: fica `nao_mapeado`.

## 2. Validação do contrato (código)

Reaproveita o parser estrito do v3 (`conferir`, `ErroRevisao`, schema versionado, hash do prompt). Verificações novas:

- `citacao` é substring literal do `trecho_id` informado (`citacao_nao_literal`).
- `entidade` existe no catálogo e é compatível com o predicado (`entidade_invalida`, `predicado_incompativel`).
- `campo` e `unidade` pertencem ao tipo da entidade (`campo_invalido`, `unidade_incompativel`).
- `conhecimento=exato` exige `valor`; `indeterminado` proíbe `valor` (`conhecimento_inconsistente`).
- Duas afirmações com o mesmo trecho, entidade e predicado e valores diferentes geram `afirmacao_conflitante` em vez de escolher uma.

Uma resposta inválida é falha da extração, preservada sem repetição para substituí-la, como nos lotes anteriores.

## 3. Avaliação por cenário (código)

Generaliza `verificar` para receber o cadastro extraído. Cada afirmação recebe um estado e um **motivo tipado**:

| Estado | Motivo | Quando |
|---|---|---|
| `revisar` | `valor_divergente` | Valor exato diferente do calculado |
| `revisar` | `premissa_alterada` | Predicado qualitativo deixou de valer ("no prazo" com fim 45 > 40) |
| `revisar` | `magnitude_sem_suporte` | Documento afirma valor exato, cálculo é indeterminado (D04, D09) |
| `revisar` | `certeza_sem_suporte` | Documento afirma situação qualitativa ("no prazo", "não crítico") que o cálculo indeterminado não decide |
| `revisar` | `afirmacao_conflitante` | O mesmo trecho afirma valores diferentes para a mesma informação |
| `revisar` | `referencia_obsoleta` | Versão citada difere da vigente |
| `ja_atualizado` | `confirmado` | Afirmação compatível com o cálculo (D07, D08) |
| `nao_verificavel` | `execucao_incompleta` / `fora_da_regiao` | Sem estado calculado validado; não se afirma desatualização |
| `julgamento_humano` | `evento_relacionado` | Regra de artefato pede decisão humana (ver abaixo) |
| `preservar` | `registro_historico` | Decisões históricas |
| — | `nao_mapeado` | Trecho sem predicado do catálogo; reportado na cobertura |

Regras de artefato, já redigidas em `documentos.py` e agora aplicadas às afirmações extraídas:

- **Action Log:** atraso não cria ação. Uma ação existente vai para `julgamento_humano` se seu prazo ou entidade vinculada mudou no cálculo; senão, `ja_atualizado`.
- **Risk Register:** fato ocorrido não vira risco novo. Um risco existente cujo evento é da mesma classe da mudança (ex.: R-01 "nova ruptura de fornecimento" diante do atraso da MotorTech) vai para `julgamento_humano` com o motivo explícito: o evento pode ter se materializado.
- **Decision Log:** decisões históricas são `preservar`. Só vão para `julgamento_humano` se a mudança declarar alteração da premissa da decisão (os eventos D01–D09 declaram "sem alteração técnica").

## 4. Explicação rastreável (código)

Hoje a recomendação lista todas as arestas ancestrais. A explicação passa a mostrar o **caminho determinante**: partindo da entidade afirmada, seguir para trás a aresta cujo `fim_origem` determinou o `inicio_destino` (estado `transmitido`), até a entidade citada no evento.

Formato gerado por template, sem texto livre da IA:

> **SR.FINISH** — "lançamento previsto para o dia 40" → calculado: dia 45.
> **Por quê:** CHANGE-D02 §1 altera SUP_MOTOR para D25 → C_MOTOR → T_ASSEMBLY → M_PROTO_READY → TEST_LIFE → M_VALIDATION → T_DOC → T_RELEASE → M_RELEASE (fim 40 → 45).
> **Motivo:** `valor_divergente`. **Evidências:** CHANGE.D02 e as fontes das arestas desse caminho.

O caminho acima foi reconstruído da `propagacao` do piloto real D02 (`outputs/ia_real_20261110T050151Z/resultado.json`), seguindo arestas `transmitido` com `fim_origem = inicio_destino`. Arestas `dominado_na_convergencia` e `sem_alteracao` explicam por que outros ramos não determinaram o resultado. As demais arestas ancestrais continuam disponíveis em `calculo_ref` para auditoria. Em convergências (D05), cada ramo determinante é mostrado; não há enumeração exponencial de caminhos.

## Exemplo de referência: D02

Status Report em prosa (sintético, a ser redigido como `STATUS@2-prosa`):

> Projeto dentro do cronograma, com lançamento previsto para o dia 40 e orçamento de R$ 152.000. A MotorTech confirmou o motor para o dia 18; os demais fornecedores seguem no previsto. O congelamento do projeto foi concluído no dia 14 e o CAD está na revisão 1. Não há riscos novos; R-01 segue em monitoramento. A ação A-01 (Carla, confirmar pedidos até D12) está aberta.

Resultado esperado (referência autoral, a congelar antes de qualquer chamada):

| Afirmação | Predicado | Estado | Motivo |
|---|---|---|---|
| "dentro do cronograma" | `no_prazo(M_RELEASE)` | revisar | `premissa_alterada` |
| "lançamento … dia 40" | `valor(M_RELEASE, fim)` | revisar | `valor_divergente` (45) |
| "orçamento de R$ 152.000" | `valor(PROJECT, custo)` | revisar | `valor_divergente` (153.500) |
| "motor para o dia 18" | `valor(SUP_MOTOR, fim)` | revisar | `valor_divergente` (25) |
| "demais fornecedores seguem no previsto" | `sem_alteracao(SUP_GEAR, SUP_HOUSING, SUP_SENSOR, SUP_ELEC; fim)` | ja_atualizado | `confirmado` |
| "congelamento … dia 14" | `valor(M_DESIGN_FREEZE, fim)` | ja_atualizado | `confirmado` |
| "CAD … revisão 1" | `versao(DOC_CAD)` | ja_atualizado | `confirmado` |
| "R-01 segue em monitoramento" | `risco(R-01, monitoramento)` | julgamento_humano | `evento_relacionado` |
| "A-01 … até D12 … aberta" | `compromisso(A-01, …)` | a definir pela regra | prazo D12 não depende de SUP_MOTOR.fim |

A primeira linha é o ganho em rastreabilidade: o cadastro atual não tem como representar "dentro do cronograma", e é justamente esse tipo de frase que fica desatualizado sem ninguém perceber.

## Corpus e avaliação

### Corpus

- Versões em prosa dos quatro artefatos de situação (Status Report, Action Log, Risk Register, Decision Log), com as mesmas informações dos registros estruturados atuais e frases qualitativas adicionais.
- Variante em prosa do Status Report já atualizado (para D07).
- Controles de extração, cada um isolando uma dificuldade:
  - C1 data relativa ("final da semana 3");
  - C2 paráfrase sem o ID ("o fornecedor do motor");
  - C3 afirmação qualitativa sem número ("sem impacto no cronograma");
  - C4 trecho de outro projeto ou outra versão (reuso de N05/N06);
  - C5 valor indeterminado no documento ("data a confirmar");
  - C6 frase sem afirmação verificável (opinião, contexto);
  - C7 duas afirmações conflitantes no mesmo documento.

Referências autorais em `avaliacao/referencias/conteudo/`, gravadas e com hash **antes** da primeira chamada, fora do pacote enviado à IA.

### Comparações

| Condição | O que mede |
|---|---|
| A. Cadastro manual atual (5 afirmações) | Linha de base |
| B. Extração por IA, sem confirmação humana | Capacidade automática ponta a ponta |
| C. Extração por IA + avaliação sobre o cadastro de referência | Isola o erro de avaliação do erro de extração |

### Métricas

- Extração: precisão e revocação de afirmações por trecho; acerto de entidade e predicado; taxa de `nao_mapeado` correta.
- Avaliação: acerto do estado por afirmação × cenário (D01–D09); falsos "revisar" e falsos "já atualizado" contados separadamente.
- Explicação: o caminho mostrado é um caminho determinante válido no grafo (conferível por código).
- Consumo: chamadas, tokens, custo e falhas, com reservas.

### Orçamento estimado

Extração por versão de documento: cerca de 5 artefatos + 1 variante + 7 controles ≈ 13 chamadas. Pelo custo médio do v3 (US$0,0802 / 28 chamadas ≈ US$0,003), o custo estimado fica em torno de US$0,04. Com reserva de US$0,015 por tentativa, o teto da rodada seria ≈ US$0,20, dentro do teto acumulado de US$20. A avaliação por cenário não usa IA.

## Fases

| Fase | Entrega | Critério de conclusão |
|---|---|---|
| F0 | Corpus em prosa, controles e referências autorais com hash | Arquivos congelados antes de qualquer chamada |
| F1 | Catálogo de predicados e avaliação determinística sobre cadastro (refatoração de `verificar`) | Condição A reproduz os resultados atuais de D01–D09; testes de cada predicado |
| F2 | Explicação por caminho determinante | Testes com D02 (linear), D05 (convergência), D01 (folga absorve) e D04 (indeterminado) |
| F3 | Regras de Action Log, Risk Register e Decision Log aplicadas às afirmações | Estados `julgamento_humano` e `preservar` com motivo; nenhuma ação, risco ou decisão criada |
| F4 | Contrato de extração: prompt, schema, parser e diagnósticos | Testes offline com transporte prescrito, incluindo citação inventada e entidade inexistente |
| F5 | Rodada real de extração, com autorização explícita e teto | Comparação das condições A, B e C registrada |
| F6 | Painel "O que revisar e por quê" na interface | Mostra trecho, estado, motivo e caminho; nada altera o documento oficial |

F1 a F3 não usam IA e já entregam valor: o "por quê" e as regras dos outros artefatos funcionam sobre o cadastro atual. F4 e F5 acrescentam a leitura da prosa.

## Invariantes mantidos

- Nenhuma recomendação altera documento oficial; aprovação continua em `registrar_decisao`, append-only.
- Indeterminado não vira zero nem "desatualizado"; execução incompleta gera `nao_verificavel`.
- Afirmação extraída por IA não é certificação semântica; `suporte_semantico` continua `nao_auditado`.
- Referências de avaliação não entram no pacote enviado à IA.
- Falhas de extração são preservadas, sem repetição para substituí-las.

## Decisões em aberto

1. **Confirmação humana da extração.** Recomendado: medir sem confirmação (condição B) e com referência (condição C); no uso, tratar a extração como cadastro assistido que a pessoa confere uma vez por versão.
2. **Escopo para o TCC.** Recomendado: F0–F3 completos e F4–F5 só para Status Report e Risk Register. São os dois artefatos em que a diferença entre "impactado" e "o que revisar" aparece com mais clareza.
3. **Regra do Action Log no D02.** A-01 (confirmar pedidos até D12) depende do fornecedor, mas seu prazo não depende da entrega. Definir na referência autoral se o estado esperado é `ja_atualizado` ou `julgamento_humano`.

## Estado da implementação (21/11/2026)

| Fase | Situação | Onde |
|---|---|---|
| F0 | Corpus em prosa: Status Report vigente e atualizado (D07), Action Log, Risk Register, Decision Log e 7 controles de extração. Afirmações de referência (29) e estados esperados de D01–D09 (117) gravados antes do avaliador | `data/projetos/alfa/conteudo/documentos_prosa.json`, `avaliacao/referencias/conteudo/` |
| F1 | Catálogo de nove predicados e avaliação determinística; condição A (cadastro manual) reproduz `documentos.verificar` em D01–D09 | `src/conteudo.py` |
| F2 | Caminho determinante, ramos paralelos resumidos, absorções por folga e efeitos de custo; evidências restritas ao caminho | `src/conteudo.py::explicar` |
| F3 | Regras de Action Log (`julgamento_humano` se a entidade vinculada mudou), Risk Register (idem, na dimensão do risco) e Decision Log (`preservar`) | `src/conteudo.py::_avaliar_artefato` |
| F4 | Prompt, JSON Schema estrito, catálogo de entidades, validador com diagnósticos (`citacao_nao_literal`, `predicado_incompativel`, `conhecimento_inconsistente`, `cobertura_incompleta`, `registro_ausente`…), executor offline e métricas de extração | `src/extracao.py` |
| F5 | **Não executada.** `ExtratorIA(modo='ia_real')` recusa com `modo_indisponivel`; falta ligar à sessão com orçamento e obter autorização | — |
| F6 | **Não feita.** Saída disponível pela CLI | `__main__.py conteudo` |

Uso, da raiz do repositório:

```bash
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 conteudo D02
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 conteudo D02 --condicao cadastro --json
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 avaliar-conteudo /caminho/novo
```

Rodada offline registrada em `outputs/revisao_conteudo_dev_20261121/comparacao.json`: na condição C, 117 de 117 afirmações × cenário com estado e motivo iguais aos esperados (31 "revisar", nenhum falso alerta, nenhuma omissão); a condição A reproduz a verificação atual nos nove cenários. **Isso mede coerência do avaliador com a referência de desenvolvimento, não desempenho de IA:** os casos são expostos, a referência foi redigida pelo mesmo agente que implementou o avaliador e nenhuma chamada de IA foi feita. A avaliação que vale como resultado do TCC exige casos novos, respostas anotadas pela dupla e a condição B (F5).

Decisões tomadas na implementação:

- Conflito é detectado dentro do mesmo trecho; seções diferentes podem se referir a momentos diferentes.
- Criticidade projetada = fecho para trás a partir de `M_RELEASE` pelas relações em que o fim da origem determina o início do destino. Com valores indeterminados a jusante, a criticidade é indeterminada.
- `no_prazo` e `dentro_orcamento` usam os limites do valor indeterminado quando eles decidem a comparação; caso contrário, `certeza_sem_suporte`.
- A regra do Action Log no D02 ficou `julgamento_humano` (a entidade vinculada SUP_MOTOR mudou). A decisão D3 do plano de redação continua aberta para a anotação da dupla.

Testes: `tests/test_conteudo.py` (16 testes). Suíte completa: 139 testes passando. O comando `integridade` já acusava, antes desta mudança, divergência de manifesto em `src/pipeline.py`, `src/orquestracao.py`, `src/ia_real.py` e `__main__.py`; o manifesto não foi atualizado.
