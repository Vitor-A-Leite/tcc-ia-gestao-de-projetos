# Plano de redação: rastreabilidade documental com revisão do conteúdo

Versão de 20 de novembro de 2026, para discussão da dupla e posterior apreciação do orientador. Este plano não registra texto redigido, implementação nem coleta nova.

## 1. Ideia central do texto

O TCC passa a contar uma única cadeia:

> **evento → partes do projeto afetadas → impacto em prazo e custo → afirmações dos documentos que ficaram desatualizadas → por quê**

A rastreabilidade é o eixo. Prazo e custo são o meio de saber *quanto* algo mudou. A contribuição que fecha o trabalho é dizer *qual informação, em qual documento, precisa ser revisada e por qual caminho de causa e efeito*.

Essa formulação recupera o que a proposta original prometia (identificar registros inconsistentes e medir acertos e falsos alertas). O alinhamento de 9/11 registrou que essa parte não havia sido testada (`Alinhamento_Proposta_TCC_20261109.md`, seções "Registro da mudança de escopo" e "Métricas e denominadores").

## 2. Documento base

Usar `Modelo_Academico_TCC_Parcial_Semanas_1_a_4.docx` como esqueleto. Ele já tem a introdução, o problema e o referencial voltados a documentos e rastreabilidade. O material de 28/10 (`TCC_Codigos/entregas/etapa12/material_tcc/Texto_e_tabelas.md`) entra como fonte dos capítulos de cálculo de impacto e do experimento de prazo e custo. O alinhamento de 9/11 fornece o histórico da mudança de escopo e os cuidados de interpretação.

## 3. Como apresentar os estudos sem misturá-los

O trabalho tem quatro conjuntos de evidência, de momentos e projetos diferentes. O texto deve apresentá-los em sequência, cada um com sua própria tabela, denominadores e limites.

| Estudo | Pergunta que responde | Projeto | Evidência | Situação |
|---|---|---|---|---|
| E1. Piloto documental histórico | Quais *tipos* de documento revisar? | Alfa (legado) | 6 casos por condição; precision, recall e F1 por categoria | Concluído; casos expostos no desenvolvimento |
| E2. Experimento de prazo e custo | *Quanto* o evento muda prazo e custo? | Sálvia | 3 casos × 3 condições (B, H, T), congelados antes da coleta | Concluído em 28/10 |
| E3. Alfa documental v2 | Os campos cadastrados do Status Report divergem do cálculo? As propostas da IA têm suporte nas fontes? | Alfa | D01–D09 com IA real (10/11); revisores v2 e v3 (11/11) | Concluído; casos de desenvolvimento |
| E4. Revisão do conteúdo | *Qual frase* de cada documento ficou desatualizada e *por quê*? | Alfa | Casos novos, respostas certas anotadas pela dupla antes da execução | A fazer (`PLANO_REVISAO_CONTEUDO.md`) |

Regras de redação:

- Nunca somar resultados de estudos diferentes nem apresentar E1 a E3 como teste cego de E4.
- E2 usa outro projeto. Não ligar automaticamente seus IDs aos do Alfa.
- D01–D09 são casos de desenvolvimento. Para E4 apresentar resultado final, ele precisa de casos novos com respostas certas congeladas antes (ver decisão D2).
- Hipóteses formuladas depois de uma coleta são apresentadas como expectativa do recorte revisado, não como registro prévio.

## 4. Plano seção por seção

Coluna "Quando": **agora** = pode ser escrito com o que já existe; **F1–F3** = depois da parte do sistema que não usa IA; **F5** = depois da rodada com IA lendo os documentos.

### 1 Introdução

| Seção | Hoje diz | Passa a dizer | Quando |
|---|---|---|---|
| 1.1 Contextualização | Informação nova não é propagada aos artefatos | Manter. Acrescentar o exemplo do motor atrasado e as frases que ficam velhas no Status Report | agora |
| 1.2 Problema | Identificar artefatos afetados e registros obsoletos | Explicitar os três níveis: *qual documento*, *qual afirmação*, *por quê*. Hoje as soluções param no primeiro | agora |
| 1.3 Questões e hipótese | F1 maior para o híbrido | Questão principal reescrita sobre identificação rastreável de afirmações a revisar; questão secundária sobre o papel do cálculo de prazo e custo nessa identificação. Hipótese marcada como expectativa revisada (ver seção 3) | agora, revisar após orientador |
| 1.4 Objetivos | Oito objetivos sobre taxonomia, grafo, regras, baseline | Manter os de grafo, interpretação e rastreabilidade. Acrescentar: (a) calcular impacto em prazo e custo com indeterminação explícita; (b) identificar afirmações desatualizadas no conteúdo dos documentos; (c) justificar cada recomendação pelo caminho determinante no grafo. Retirar ou reduzir "taxonomia de eventos" e "regras tipo de evento → artefato" | agora |
| 1.5 Justificativa | Coerência entre documentos sem depender de atualização manual | Manter. Reforçar que a recomendação é para validação humana e nunca edita o documento | agora |
| 1.6 Delimitação | Quatro artefatos; sem atualização autônoma | Manter os quatro artefatos. Declarar que a leitura de conteúdo é feita em documentos sintéticos em prosa, de um projeto, e que a avaliação completa cobre Status Report e Risk Register (decisão D3) | após D3 |

### 2 Referencial teórico

| Seção | Ação | Quando |
|---|---|---|
| 2.1 Gestão de projetos e informação | Manter; já trata documentação como representação do estado do projeto | agora |
| 2.2 Rastreabilidade e análise de impacto | Acrescentar análise de impacto de mudanças e cálculo de prazo por precedências (base: `Literatura_rastreabilidade_20261109.md`, `Pesquisa_fundamentos_20261109.md`) | agora |
| 2.3 LLM e RAG | Manter. Acrescentar o princípio "a IA extrai, regras conferem" e limites de verificação de afirmações por LLM | agora |
| 2.4 Documentação e dimensão temporal | Manter Kostis et al. (decisões substituídas) e ligar à ideia de afirmação obsoleta | agora |
| 2.5 Lacuna | Reescrever: o que falta é ir de "documento afetado" para "afirmação desatualizada, com caminho causal verificável e indeterminação preservada" | agora, conferir com a literatura |

### 3 Metodologia

| Seção | Conteúdo | Quando |
|---|---|---|
| 3.1 Classificação | Aplicada, construção de protótipo e avaliação exploratória em ambiente sintético | agora |
| 3.2 Evolução do escopo | Nova subseção: linha do tempo E1 → E2 → E3 → E4, com o motivo de cada mudança | agora |
| 3.3 Arquitetura | Atualizar o quadro de etapas: interpretação local → validação → cálculo determinístico → leitura das afirmações → conferência pelo código → explicação pelo caminho → aprovação humana | agora (estrutura); F1–F3 (detalhes) |
| 3.4 Projeto Alfa | Manter os 40 nós e 65 relações. Descrever os quatro documentos e as versões em prosa criadas para E4 | F0 |
| 3.5 Casos e respostas certas | Casos novos de E4; anotação independente pelos dois autores, reconciliação e congelamento antes da execução (procedimento que o modelo acadêmico já previa em 3.4) | F0 |
| 3.6 Condições | A: afirmações cadastradas manualmente; B: leitura por IA sem conferência humana; C: avaliação sobre as afirmações de referência | agora |
| 3.7 Métricas | Por afirmação: precisão, revocação e F1 de "revisar"; falsos alertas em afirmações corretas; acerto do motivo; validade do caminho mostrado; preservação da indeterminação; custo e falhas. Para E2, manter as métricas de 28/10 | agora |

### 4 Desenvolvimento

| Seção | Conteúdo | Fonte | Quando |
|---|---|---|---|
| 4.1 Protótipo documental inicial | E1 e suas limitações (regra fixa por tipo de evento não lê conteúdo) | `Integracao_documental_prazo_custo_20261109.md` | agora |
| 4.2 Cálculo de impacto | Arquitetura híbrida de prazo e custo | Material de 28/10 | agora |
| 4.3 Alfa documental v2 | Seleção de entradas, comparação de campos do Status Report, revisores v2 e v3 | `alfa_documental_v2/README.md`, `AVALIACAO_REVISOR_V3.md` | agora |
| 4.4 Revisão do conteúdo | Catálogo de afirmações, motivos, caminho determinante, regras dos outros artefatos | `PLANO_REVISAO_CONTEUDO.md` e código | F1–F3, F4 |

### 5 Resultados

| Bloco | Conteúdo | Quando |
|---|---|---|
| 5.1 E1 | Tabela de precision, recall e F1 por categoria, com a ressalva de que a regra e a resposta certa podem coincidir | agora |
| 5.2 E2 | Os nove desfechos, rejeições de formato, custo e latência | agora |
| 5.3 E3 | D01–D09 com IA real e revisores v2 e v3, apresentados como desenvolvimento | agora |
| 5.4 E4, exemplo trabalhado | Status Report do motor atrasado frase por frase, com estado, motivo e caminho | F1–F3 |
| 5.5 E4, avaliação | Condições A, B e C nos casos novos, com contagens e denominadores | F5 |

### 6 Discussão, 7 Conclusão

- Discussão: o que muda ao sair de "documento afetado" para "afirmação a revisar"; o papel do cálculo de prazo e custo como fonte de verdade da conferência; onde a IA errou ao ler e onde o código barrou; custo.
- Limites: projeto sintético único, documentos escritos pelos autores, poucos casos, uma execução por condição, nenhuma edição automática, nenhum estudo com gestores.
- Conclusão: responder à pergunta reescrita estritamente dentro do que E4 mostrar; E1 a E3 sustentam as etapas anteriores da cadeia.
- Quando: estrutura agora; texto final após F5.

## 5. Figuras e quadros previstos

1. A cadeia evento → entidades → prazo e custo → afirmações → por quê (Introdução ou 3.3).
2. Linha do tempo dos estudos E1–E4 (3.2).
3. Quadro de etapas da arquitetura com responsável (IA, código, humano) (3.3).
4. Grafo destacando o caminho determinante do D02: SUP_MOTOR → C_MOTOR → T_ASSEMBLY → M_PROTO_READY → TEST_LIFE → M_VALIDATION → T_DOC → T_RELEASE → M_RELEASE (5.4).
5. Tabela frase por frase do Status Report no D02 (5.4).
6. Tabela de métricas de E4 com contagens (5.5).

## 6. Ordem de trabalho

| Etapa | Redação | Sistema |
|---|---|---|
| 1 | Introdução, referencial, 3.1, 3.2, 3.6, 3.7; capítulo 4.1–4.3; resultados E1–E3 | — |
| 2 | Levar ao orientador a pergunta reescrita e as decisões da seção 7 | — |
| 3 | 3.4 e 3.5 | F0: documentos em prosa, casos novos e anotação independente das respostas certas pela dupla |
| 4 | 4.4 e 5.4 | F1–F3: catálogo, motivos, caminho determinante, regras dos outros artefatos |
| 5 | 5.5, discussão e conclusão | F4–F5: leitura por IA, rodada real autorizada |
| 6 | Revisão final e normalização | — |

A etapa 1 não depende de nada novo e pode começar já. A anotação independente da etapa 3 é a tarefa que exige os dois autores separadamente: cada um marca, sem consultar o outro, quais frases devem ser revisadas e por quê; depois as divergências são reconciliadas e o resultado é congelado.

## 7. Decisões para o orientador

- **D1. Eixo do trabalho.** Rastreabilidade documental como eixo, com prazo e custo como meio (recomendado, coerente com o modelo acadêmico e com a proposta original), ou prazo e custo como eixo, como no alinhamento de 9/11.
- **D2. Casos de E4.** Casos novos e congelados, com anotação independente (recomendado, permite apresentar E4 como avaliação), ou reaproveitar D01–D09, apresentando E4 só como demonstração de desenvolvimento.
- **D3. Alcance de E4.** Avaliação completa só em Status Report e Risk Register (recomendado pelo prazo), ou nos quatro artefatos.
- **D4. Quantidade de casos.** O parecer de 9/11 sugeriu de 12 a 18 cenários novos como cobertura exploratória. Definir o número conforme o prazo de entrega e o orçamento (teto acumulado de US$20, com US$4,96 comprometidos até 11/11).

## 8. Fontes internas

- Modelo acadêmico: `Modelo_Academico_TCC_Parcial_Semanas_1_a_4.docx`.
- Proposta original: `Planejamento/Proposta_TCC_IA_Gestao_Projetos_3_meses.docx`.
- Alinhamento e integração: `Planejamento/Alinhamento_Proposta_TCC_20261109.md`, `Planejamento/Integracao_documental_prazo_custo_20261109.md`.
- Experimento de 28/10: `TCC_Codigos/entregas/etapa12/material_tcc/Texto_e_tabelas.md`, `TCC_Codigos/outputs/etapa11_final_20261028/RELATORIO.md`.
- Alfa documental v2: `TCC_Codigos/etapas/alfa_documental_v2/README.md`, `docs/AVALIACAO_REVISOR_V3.md`, `docs/PLANO_REVISAO_CONTEUDO.md`.
- Literatura: `Planejamento/Literatura_rastreabilidade_20261109.md`, `Planejamento/Mapa_literatura_integrada_TCC_20261109.md`.
