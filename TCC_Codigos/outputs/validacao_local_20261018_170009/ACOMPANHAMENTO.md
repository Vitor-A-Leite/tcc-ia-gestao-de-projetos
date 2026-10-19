# Validação local do TCC — acompanhamento

- Ambiente e dados: aprovados — Python 3.12, 40 nós, 65 arestas, 36 cenários; notebooks com sintaxe válida.
- Testes automatizados sem rede: 34 aprovados (incluindo cinco regressões do executor de pilotos).
- Preparação local: aprovada — notebook inicial executado pelo terminal, sem API.
- Simulação completa de baseline e híbrido: aprovada — 36 cenários por condição, cliente simulado e rede bloqueada; artefatos em 04_simulacao_completa/.
- Piloto real baseline: concluído — 6/6 respostas válidas; tipo correto em 6/6.
- Piloto real híbrido: concluído — 6/6 respostas válidas; tipo correto em 5/6 (S035 incorreto).
- Experimento real completo de 36 casos: não solicitado nesta rodada.

Resultados desta rodada serão preservados nesta pasta. A chave não será registrada.

## Pilotos reais — acompanhamento

| Condição | Cenário | Tipo previsto | Tipo de referência | Formato/execução |
|---|---|---|---|---|
| baseline | S001 | delay | delay | OK |
| baseline | S003 | test_problem | test_problem | OK |
| baseline | S007 | supplier_change | supplier_change | OK |
| baseline | S009 | informational | informational | OK |
| baseline | S024 | test_problem | test_problem | OK |
| baseline | S035 | informational | informational | OK |
| hybrid | S001 | delay | delay | OK |
| hybrid | S003 | test_problem | test_problem | OK |
| hybrid | S007 | supplier_change | supplier_change | OK |
| hybrid | S009 | informational | informational | OK |
| hybrid | S024 | test_problem | test_problem | OK |
| hybrid | S035 | supplier_change | informational | OK |

Acertar o tipo do evento não significa acertar todas as entidades ou documentos impactados.

## Resultado final

[Abra RESULTADOS.md](RESULTADOS.md) para as métricas reais e os três pontos de revisão: classificação do S035, propagação ampla e entidade principal ausente em três casos. Nenhum código científico ou prompt foi alterado após observar o piloto.
