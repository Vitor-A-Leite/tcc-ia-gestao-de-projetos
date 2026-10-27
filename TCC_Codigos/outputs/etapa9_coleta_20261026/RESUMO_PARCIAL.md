# Coleta real da etapa 9 — resumo para revisão

26/10/2026, America/Sao_Paulo. **Parcial, com parada diagnóstica autorizada durante a coleta.** Não é experimento final. Modelo/protocolo v 03 preservados: gpt-6-luna High, entrada≤16.000 por contagem oficial, saída total≤25.000, Standard/cache 30 m, sem retry/fallback, teto agregado US$ 5.

O programa usou a chave local cujo rótulo **informado pelo usuário** é TCC-Impacto-Baseline; não inferiu esse nome da credencial. A chave TCC-Impacto-Grafo-LLM-por-no não foi adicionada. Nenhum segredo foi exibido/inventariado.

A coleta recebeu quatro retornos completos, mas houve oito timeouts. As inferências 8–12 formaram cinco timeouts consecutivos: o monitor interrompeu o coletor identificado com SIGINT e preservou a tentativa 13 em andamento como custo desconhecido. Essa regra de parada foi decisão operacional posterior ao início, não condição pré-registrada do v 03. Não se aumentou deadline nem se repetiram slots.

| Condição | N planejado | Registros finais | Iniciado sem resultado | Não iniciados |
|---|---:|---:|---:|---:|
| B | 30 | 2: timeout e parcial epistêmico | 0 | 28 |
| H | 30 | 2: parciais por falha operacional | 1 | 27 |
| T | 30 | 2: ok | 0 | 28 |

Só **um caso**, k_09c2, tem resultados finais B/H/T, em duas repetições. T previu +2 dias/+R$ 400 nas duas: coincide com referência **autoral**, sem validação científica independente. B R 2 explicitou falta de relações: prazo indeterminado e custo aumenta sem magnitude exata; não foi timeout nessa resposta. H ficou indeterminado por timeouts/bloqueio de descendentes, não por uma abstenção semântica julgada adequada.

| Condição | Cobertura exata prazo/custo | MAE prazo | MAE custo |
|---|---|---|---|
| B | 0/30 em ambos | não calculável,0/30 pares | não calculável,0/30 pares |
| H | 0/30 em ambos | não calculável,0/30 pares | não calculável,0/30 pares |
| T | 2/30 em ambos | 0 dias, sobre 2/30 pares | R$ 0, sobre 2/30 pares |

Interseções B/H, B/T, H/T: **0/30 em ambos os desfechos**. Não há comparação numérica pareada ou conclusão de vantagem. Os dois acertos T são repetições do mesmo caso. Oito timeouts e uma interrupção são falhas operacionais, não erros numéricos do modelo. Os 84 ausentes do normalizador são 83 não iniciados+1 interrompido, não 84 falhas de API. Zeros mecânicos de acerto/falsa certeza/abstenção de execuções ausentes não demonstram bom desempenho. Suporte semântico e inferibilidade continuam pendentes; nenhum zero sustentado foi auditado.

**Tempo: ** deadline 30 s inclui contagem+inferência. Timeouts com latência final disponível ficaram em≈30,006–30,014 s. Retornos completos observados:20,567–29,059 s. A hipótese de deadline restritivo merece teste isolado; esses dados não separam raciocínio, rede e serviço.

**Contabilidade, não fatura: **13 contagens e 13 inferências marcadas;4 com uso conciliado (15757 tokens de entrada,10521 de saída total) e 9 sem custo conciliado. Inferência conhecida **US$ 0,007229825**; reserva de inferência desconhecida **US$ 0,1305**; provisão hipotética de contagem **US$ 0,026**. Comprometimento interno **US$ 0,163729825**; saldo interno livre **US$ 4,836270175**. As 9 reservas integrais somam US$ 0,1485 e já incluem parte da provisão, sem dupla soma. Nenhuma reserva desconhecida foi liberada. A provisão não é tarifa publicada/cobrança comprovada; fatura e câmbio não foram consultados.

Avaliador v 1 não aceita limite em referência indeterminada: o limite Δprazo≥0 de k_d307 foi conservado explicitamente fora desse schema na projeção de avaliação, sem mudar o original ou convertê-lo em exato/direção. Não há previsão entregue desse caso; nenhum acerto foi ajustado por isso.

Artefatos: [relatório detalhado](RELATORIO_PARCIAL.md), [avaliação autoral](avaliacao_autoral.json), [contabilidade e erros](contabilidade_e_erros.json), [parada](parada_diagnostica.json), snapshot de ledger/plano/manifesto em `snapshot_pos_parada/`. Os seis JSON exportados são idênticos aos blobs originais do ledger canônico.

[Próximo diagnóstico proposto](PROPOSTA_DIAGNOSTICO_SEGUINTE.md): começar por uma chamada, até duas no máximo, deadline 180 s, mesmos payloads/modelo/prompts/dados/tokens, resultados separados e reserva adicional≤US$ 0,033 no **mesmo saldo acumulado**. Não executado; exige adendo técnico sem zerar carteira ou substituir slots originais. Não retomar `--rodar` antes da revisão. Etapas 10/11 não iniciadas.
