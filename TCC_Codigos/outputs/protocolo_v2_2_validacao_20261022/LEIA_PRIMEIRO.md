# Validação offline V2.2 — 22/10/2026

34 casos hipotéticos de desenvolvimento, 92 perguntas por condição (184 no total).
68/68 registros demonstrativos passaram na comparação com gabaritos autorais.
118 testes de software passaram com rede bloqueada. Nenhuma nova chamada à API.

Esses resultados NÃO são previsões de IA, comparação empírica entre modelos ou revisão independente.
Os casos foram usados no desenvolvimento; os gabaritos continuam pendentes de revisão do domínio.

- CADERNO_CASOS_ADICIONAIS.md: hipóteses, parâmetros, gabaritos A/H e justificativas para revisão.
- cobertura_gabaritos.json: distribuição das referências, sem usar as respostas do motor.
- requests_without_references.jsonl: entradas com contrato, regras e esquema; sem gabaritos.
- evaluations.jsonl e summary.json: respostas injetadas pelo motor e sua validação funcional.
- TESTES_OFFLINE.log: registro dos 118 testes.
- compatibilidade_v2_0/: 15 exemplos antigos, 60 perguntas, 30/30 registros aprovados.
- contraprova_previsoes_sinteticas.jsonl: respostas demonstrativas com um erro deliberado.
- contraprova_troca_inicio_termino/: avaliador detecta a afirmação sem suporte (saída 1 esperada).
- CONTRAPROVA.log: execução da contraprova; não são resultados de um modelo de IA.
- manifest.json: hashes dos arquivos, fontes e registro de preservação dos dados legados.

Na contraprova, o início de SC01 atrasa quatro dias e nenhum modelo informa o término.
Atribuir +4 ao término usando a prova do início é uma afirmação sem suporte. O erro é
identificado sem descartar o registro, mantendo 184 perguntas nos denominadores esperados.

O grafo hipotético deste conjunto é separado do grafo real do Projeto Alfa. Os 36 cenários,
o grafo real e o gabarito autoral V2.1 mantiveram seus hashes anteriores.
