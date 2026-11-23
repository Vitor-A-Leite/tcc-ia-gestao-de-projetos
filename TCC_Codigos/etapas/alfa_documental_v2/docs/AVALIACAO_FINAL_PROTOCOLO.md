# Avaliação final: protocolo congelado

Data: 23/11/2026. Situação: **preparada, aguardando autorização para a rodada com IA real**.

## Pergunta

Dada uma mudança no projeto, o sistema identifica corretamente quais trechos dos documentos de gestão precisam ser revisados, e por quê, melhor do que uma IA sozinha?

## Material (novo, não usado no desenvolvimento)

| Item | Origem | Arquivo |
|---|---|---|
| 15 eventos de mudança (F01–F15) | Gerados por IA em sessão sem acesso ao repositório, a partir de um prompt com o estado inicial; revisados pelos autores | `data/projetos/alfa/final/material_gerado.json` |
| 7 documentos em prosa, 34 trechos | idem: 4 Status Reports em estilos diferentes, Action Log, Risk Register e Decision Log | idem |
| Mudança estruturada de cada evento | Tradução manual do comunicado (isola a camada documental) | `data/projetos/alfa/cenarios/final/`, `data/projetos/alfa/simulacoes/final/` |

O prazo e o custo calculados pelo motor para os 15 eventos coincidem com a tabela usada pelas anotadoras.

Distribuição dos eventos:
- 3 atrasos críticos (F01, F08, F15) e 2 absorvidos pela folga (F03, F11);
- 2 de preço (F02, F09) e 2 desconhecidos (F04, F13);
- 2 com dois parâmetros (F05, e F12, que não tem efeito no fim) e 2 de duração (F06, F14);
- 1 confirmação (F07) e 1 de outro projeto (F10).

## Gabarito

Arquivo: `data/projetos/alfa/final/gabarito_final.json`. São 510 pares (15 eventos × 34 trechos), com um rótulo por par: REVISAR, CORRETO, DECISAO_HUMANA, PRESERVAR ou SEM_AFIRMACAO.

1. Pré-anotação independente por duas IAs, em conversas sem acesso ao repositório, com o mesmo prompt: regras, estado inicial e estado de cada evento já calculado.
2. Concordância: 463 de 510 (90,8%), kappa de Cohen 0,850; "revisar × não revisar" concordou em 94,5%.
3. As 47 divergências se concentram em 7 padrões. Foram decididas pelo agente de código, a pedido dos autores, aplicando literalmente as regras do prompt e sem consultar o sistema (`DIVERGENCIAS_PARA_DECIDIR.md`).
4. Errata: na tabela de estados do F15, a folga da SensePro estava escrita como 5, e o correto é 6. Nenhum rótulo muda (registrado no gabarito).
5. **Pendente:** conferência pelos autores de 50 concordâncias sorteadas (`amostra_concordancias.csv`). Se a conferência mudar o gabarito, o manifesto precisa ser preparado de novo, o que não tem custo.

Distribuição: 273 REVISAR, 155 CORRETO, 45 PRESERVAR, 30 SEM_AFIRMACAO, 7 DECISAO_HUMANA.

## Condições

| Condição | O que a IA recebe | Quem decide |
|---|---|---|
| **B: sistema híbrido** | Cada documento e os catálogos (sem evento, cálculo ou gabarito) | A IA extrai as afirmações; o código compara com o cálculo do evento e agrega por trecho |
| **D: IA sozinha** | Regras e estado inicial (os mesmos das anotadoras), o comunicado do evento e um grupo de documentos; **sem** o estado calculado | A própria IA rotula cada trecho |

A condição C do desenvolvimento (avaliação sobre afirmações de referência) não existe aqui, porque o gabarito é por trecho, não por afirmação.

- **B:** uma chamada por documento (a extração não depende do evento), ou seja, 7 por repetição.
- **D:** uma chamada por evento e grupo, ou seja, 45 por repetição. Os grupos são (STATUS_A, STATUS_B), (STATUS_C, STATUS_D) e (ACTION_LOG, RISK_REGISTER, DECISION_LOG).
- Modelo `gpt-6-luna`, esforço `high`, nas duas condições.
- **3 repetições**, cada chamada com uma única tentativa: falhas são preservadas e entram nos denominadores.

## Regra de agregação na condição B (fixada antes)

Por trecho e evento:
- Decision Log: sempre PRESERVAR.
- Demais documentos:
  - nenhuma afirmação extraída → SEM_AFIRMACAO;
  - alguma afirmação "revisar" → REVISAR;
  - senão, alguma "julgamento_humano" → DECISAO_HUMANA;
  - senão → CORRETO (inclui `ja_atualizado`, `nao_verificavel` e `preservar`).
- Documento sem extração válida, ou grupo sem anotação válida → FALHA. Conta como "não revisar" e como erro nas métricas de classe.

## Métricas

- **Principal:** precisão, revocação e F1 de REVISAR por par (evento, trecho).
- **Secundárias:**
  - acurácia em 4 classes (REVISAR, DECISAO_HUMANA, PRESERVAR, NAO_REVISAR) e em 5 rótulos;
  - falsos alertas em trechos corretos;
  - compatibilidade de motivo nos acertos;
  - falhas, tokens e custo.
- Média, mínimo e máximo entre as 3 repetições.

## Mudanças de código feitas antes do congelamento

- **Contrato de extração v3:** campos `duracao` e `folga`, entidades de parcela (`p_*`), conhecimento `faixa` com `limites` (semanas), regra para frases condicionais e para itens de Action Log, Risk Register e Decision Log. Instruções v2 preservadas em `SISTEMA_V2`.
- **Avaliador:** folga total projetada, duração, custo por parcela, `sem_alteracao` de parcelas e faixas.
- **Simulação:** mudança de custo com parcela explícita (o frete é a segunda parcela da MetalForm).
- **Condição D:** `src/ia_sozinha.py`. **Avaliação:** `src/avaliacao_final.py`. **Executor:** `scripts/avaliacao_final.py`.
- Testes: os predicados novos foram exercitados **só em D01–D09**. Nenhuma instrução foi ajustada com respostas da IA sobre o material final, porque nenhuma chamada foi feita.

**Limitação a declarar:** os tipos de afirmação acrescentados ao catálogo (folga, duração, parcela, semanas) foram escolhidos depois de ler o material final, para que o sistema tivesse vocabulário para ele. A mesma convenção de semanas foi dada às anotadoras e à condição D.

## Execução

```bash
python3.12 -B -m TCC_Codigos.etapas.alfa_documental_v2.scripts.avaliacao_final executar \
  TCC_Codigos/etapas/alfa_documental_v2/outputs/avaliacao_final_20261123 --autorizacao "..."
```

As repetições podem rodar em paralelo, uma por processo, com `--repeticao 1`, `--repeticao 2` e `--repeticao 3`. A comparação roda sozinha quando as três terminam.

## Orçamento

| Item | Valor |
|---|---|
| Chamadas | 156 (21 em B, 135 em D) |
| Reserva máxima travada | US$ 2,34 (156 × US$ 0,015) |
| Custo estimado | cerca de US$ 0,45 |
| Comprometido antes | US$ 4,9706 |
| Teto acumulado | US$ 20 |

## Limites

- Projeto único e sintético; material gerado por IA e revisado pelos autores.
- Gabarito pré-anotado por IAs: as divergências foram decididas por regra pelo agente que construiu o sistema, e a conferência humana se limita a uma amostra.
- A condição D usa a mesma família de modelo que o sistema; uma das anotadoras pode ser da mesma família.
- A mudança estruturada de cada evento foi traduzida à mão: a avaliação mede a camada documental, não a interpretação do comunicado.
