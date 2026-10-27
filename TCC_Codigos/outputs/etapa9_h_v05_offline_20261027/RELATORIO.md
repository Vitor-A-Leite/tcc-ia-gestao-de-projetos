# Etapa 9 — correção H v05 exclusivamente offline

27/10/2026, America/Sao_Paulo. **Implementação opt-in entregue para revisão; nenhuma chamada paga.** Os resultados reais v04 continuam históricos, sem reparo, reclassificação ou recálculo de suas métricas. Etapas 10/11 não iniciadas.

## Diagnóstico e contraprovas

Aplicado o ciclo de diagnóstico com cinco hipóteses ordenadas antes dos testes: interface insuficientemente explícita para justificativa; ausência de cláusula confundida com total do nó; notas locais sobrescrevendo o solver; custo temporal simbólico confundido com fato ausente; necessidade de preservar desconhecimento factual. As contraprovas mínimas usam dados sintéticos prospectivos, sem gabaritos reais.

A reprodução offline dos originais confirmou 15 rejeições `Texto obrigatório` (justificativa em lista), três `Ausência exige zero local sustentado`, uma divergência de hash e uma direção incompatível. O histórico mantém 20 fechamentos parciais, oito completos operacionais com ambos os resultados indeterminados e dois exatos. O log RED original contém duas falhas específicas: ausência de cláusula com outras obrigações no mesmo nó e nota sobre marco global anulando cálculo conhecido. A suíte final passou a afirmar essas falhas do legado; os testes v05 afirmam os resultados corrigidos. Nada converteu as respostas antigas para fazê-las passar.

## Mudanças versionadas

Todo código novo está em `src/hibrido_v05/`, sem modificação dos módulos anteriores, B/T ou transporte financeiro.

- **Interface:** schema `2.0-analise-local`, contexto `2.0-contexto-no-local`, formato `5.0-h-local-escopado`. `justificativa` é string não vazia; arrays continuam rejeitados, sem concatenação. Prompt/descritor explicitam tipos, catálogo, condições e Conhecimento. Aderência de um LLM real ainda não foi testada.
- **Escopo:** confirmações de ausência vinculam exatamente uma regra, cláusula citada e predicado correspondente. Zero refere-se à cobrança daquela cláusula, não à avaliação agregada do nó. Outras obrigações podem coexistir. Ausência e custo positivo/desconhecido da mesma cláusula são contraditórios; duas cláusulas no mesmo nó não se resolvem mutuamente. Manutenção e substituição concorrente também são rejeitadas.
- **Fechamento:** a política verifica cada regra. `pendencias_operacionais` é obrigatório e bloqueia conservadoramente o resultado quando há fato necessário fora da representação. Desconhecimento representável continua em propostas tipadas e propaga pelo motor.
- **Cálculo:** `lacunas` local passa a nota diagnóstica, preservada em `notas_diagnosticas_locais`, sem sobrescrever indiscriminadamente resultados do solver. O custo ligado ao marco usa o cronograma final. Mantidos DAG prospectivo, FS zero, máximo na convergência, livro de obrigações únicas e regra de ausência de crédito automático. O caso sintético termina em D9 (max(6,5)+3), contra D7 de base: +2 dias e +11.000 centavos (10.000 temporais +300 e +700 de obrigações distintas).
- **Fronteira e avaliação:** envelope `2.0-h`, origem `orquestracao_v05`. Entrada separada `hibrido_v05.avaliacao.normalizar`, manifesto `2.0-manifesto-h05`, protocolo H `5.0-politica-h-escopada`; confere versões/contextos e revalida análises locais bem-sucedidas. O normalizador antigo permanece intacto. `hibrido_v05.metricas.avaliar` conserva a mesma lógica de métricas em cópia versionada, mudando apenas seus imports para a nova entrada e os limites existentes. Nenhum ID ou versão é falsificado para passar no legado. A cópia requer manutenção sincronizada caso a lógica comum evolua.

## Verificação

**92 testes offline aprovados:** 19 do H v05, 24 de regressão da etapa 6 e 49 da etapa 7. Logs completos neste diretório. Os testes v05 incluem contraprovas diferenciais, justificativa tipada, hashes/referências/direção/booleanos, contradições, duas regras no mesmo nó, obrigações distintas, prazo/custo sintéticos, duração e taxa realmente ausentes, pendência factual, interface de transporte e pipeline da fronteira à normalização/métricas. A fixture de fronteira usa inputs de desenvolvimento e respostas MOCK sem interpretação semântica; não é reexecução de modelo ou medição de acurácia. Rejeição de envelope e schema local antigos foi testada; o normalizador legado rejeita o manifesto novo.

Comandos reproduzíveis a partir da raiz:

```sh
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9_h_v05 -v
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa6
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa7
PYTHONPATH=TCC_Codigos/src python3 TCC_Codigos/outputs/etapa9_h_v05_offline_20261027/reproduzir_legado.py
```

## Limitações e decisão de revisão

A mudança de `lacunas` para nota é metodológica: depende de o modelo declarar fatos realmente ausentes em propostas tipadas ou `pendencias_operacionais`. **Omissão ou classificação errada pode causar falsa precisão.** O motor não detecta sozinho essa omissão; a validação de contrato e referências não comprova suporte semântico. As pendências textuais não representáveis bloqueiam ambos os desfechos conservadoramente; incerteza de taxa representada preserva prazo exato e custo desconhecido. Aderência real à interface, qualidade semântica e inferibilidade por view seguem não demonstradas. Nenhum ganho de cobertura ou superioridade foi inferido dos testes.

A implementação permanece opt-in. Não há ativação no coletor pago: o adaptador exige transporte vinculado à v05 e rejeita o v04. Uma futura integração paga precisa de revisão do protocolo e da vinculação à carteira, com adendo explícito; este trabalho não a executa nem a autoriza. A revisão deve decidir sobre a separação nota/pendência e a confirmação por cláusula antes de novo piloto.

## Integridade e orçamento

`integridade_final.json`: **557/557 arquivos protegidos inalterados**, incluindo código anterior, dados, outputs e evidências reais. Comparação integral lógica do ledger com `snapshot_antes/ledger.sqlite` idêntica, incluindo schema e todas as linhas. Mantidas 272 tentativas e os 90 slots reais encerrados; zero novas chamadas, leitura de chave ou gasto.

O controle acumulado permanece US$ 1,206550975 comprometidos (US$ 0,488550975 de inferência conhecida, US$ 0,174 de reserva desconhecida e US$ 0,544 de provisão hipotética de contagem). Saldo interno US$ 3,793449025 sob teto US$ 5; não é fatura. Raw, referências, manifests e snapshots anteriores permanecem intactos.

Evidências: `contraprovas_antes.log`, `contraprovas_depois_inicial.log`, `escopos_interface.log`, `testes_finais.log`, `regressao_etapa6.log`, `regressao_etapa7.log`, `reproducao_legada.json`, `revalidacao_legado_final.log`, `integridade_antes.json`, `integridade_final.json`, `snapshot_antes/ledger.sqlite`.
