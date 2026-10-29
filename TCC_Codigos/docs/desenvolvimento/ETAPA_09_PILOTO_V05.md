# Etapa 9 — piloto v05 encerrado para revisão

27/10/2026, America/Sao_Paulo. **90/90 slots encerrados**, em nova coorte de 15 casos × B/H/T × duas repetições. O primeiro B terminou com erro DNS antes de inferência; a continuação executou somente os 89 pendentes com rede escalada, sem retry, nova parada ou mudança de código científico. Tentativa 273, primeiro resultado, parada original e resultados v04 preservados. Etapas 10/11 não iniciadas.

| Condição | Prazo exato | Custo exato | MAE dias (pares) | MAE centavos (pares) |
|---|---:|---:|---:|---:|
| B | 4/30 | 8/30 | 0 (4) | 0 (8) |
| H | 9/30 | 9/30 | 0 (9) | 0 (9) |
| T | 23/30 | 21/30 | 0 (23) | 0 (21) |

H terminou com 9 resultados `ok` e 21 parciais. Teve 176/178 análises válidas e duas rejeições (hash/direção). Dos 10 fechamentos completos operacionais, 9 deram valores exatos e um preservou duração desconhecida e custo apenas com aumento/limite inferior. Persistem 20 fechamentos parciais; há pendências de permissão/escopo que não comprovam falta factual global. Exemplo documentado: outros nós alegam não poder lançar obrigação já reconciliada no nó custodiante. Nada foi corrigido retrospectivamente.

H passou de cobertura exata 2/30 para 9/30 nesta amostra; sete dos nove resultados são de impacto não zero. Comparativo descritivo, sem causalidade/superioridade. B/T são novas realizações do mesmo modelo/contexto, sem atribuição das diferenças às correções H. MAE só vale nos pares exatos elegíveis; referências autorais e inferibilidade/suporte ainda sem validação independente. Nenhuma candidata a erro numérico/falsa precisão foi encontrada nos pares/transcrições comparáveis v05; isso não prova suporte semântico.

A coleta usou 238 tentativas novas: uma contagem DNS falha e 237 inferências conciliadas. **510 tentativas acumuladas**; inferência incremental conhecida US$ 0,399556205; comprometimento incremental US$ 0,890056205. **Comprometimento acumulado US$ 2,096607180**, saldo interno **US$ 2,903392820** sob teto US$ 5. Permanecem US$ 0,1885 de reserva de inferência desconhecida e US$ 1,02 de provisão hipotética de contagem. Não é fatura.

50 testes offline aprovados. Inventário de 1049 arquivos rastreados: só ledger e STATUS/PLANO tiveram alterações permitidas; chamadas 1–273, primeiro resultado e fases históricas conferidos. Snapshot DNS preservado em `ledger_apos.sqlite`; snapshot final novo em `retomada_89/ledger_final.sqlite`.

[Relatório completo, latências, custos e evidências](../../outputs/etapa9_piloto_v05_20261027/RELATORIO.md). Próximo passo: revisão de escopo, suporte e resultados antes de qualquer alteração metodológica ou avanço.
