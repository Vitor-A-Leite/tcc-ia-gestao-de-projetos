# Etapa 9 — aceite técnico da v7

**Critério técnico atendido em 28/10/2026.** A revisão 7.2 foi integrada, validada e executada em 90/90 slots. A conclusão atende à meta solicitada pelo usuário e ao [critério definido antes da coleta](ETAPA_09_CRITERIO_CONCLUSAO.md). Constitui entrega técnica para revisão; não registra aprovação científica ou humana independente. Etapas 10/11 permanecem não iniciadas.

## Evidências dos seis critérios

| Critério | Resultado e evidência |
|---|---|
| 1. Correções prospectivas e testes | 23 testes H e seis de carteira/integração aprovados na revisão final. Vínculo técnico e direção redundante saíram da responsabilidade da LLM; 220/220 análises locais foram válidas, contra 195/203 na v6. Manutenção escopada resolveu os encaminhamentos em k_b731; checklist resolveu k_f04b/1; prazo foi preservado nas duas repetições de k_8c65. A omissão de confirmação em k_f04b/2 permaneceu visível e foi auditada. [Testes e reprodução](../../outputs/etapa9_piloto_v07_r3_20261028/VALIDACAO.md). |
| 2. Preservação das indeterminações | H manteve não exatas as quatro magnitudes de prazo e seis de custo realmente desconhecidas nas referências. Nenhuma falsa magnitude ou direção excessiva em H. Três direções de custo sustentadas não foram recuperadas, ante cinco na v6. Fontes e respostas conferidas, sem transformar preço/duração ausentes em zero. [Auditoria](../../outputs/etapa9_piloto_v07_r3_20261028/AUDITORIA_RESIDUAL.md). |
| 3. Piloto comparável completo | Mesmos 15 casos, B/H/T, duas repetições, views, snapshots, eventos, modelo/configuração e ordem da v6. Código congelado; 90/90 resultados, 280 chamadas novas conciliadas, nenhuma parada, retry ou fallback. Rodadas de desenvolvimento anteriores preservadas separadamente. [Pareamento](../../outputs/etapa9_piloto_v07_r3_20261028/pareamento_verificado.json). |
| 4. Comparação e causas remanescentes | Cobertura, MAE elegível, incerteza/direção, validade, encaminhamentos, tempo e custo comparados. As 180 combinações execução/desfecho foram classificadas; nove execuções H parciais, 11 rejeições B/T, um erro numérico B e uma direção excessiva T foram documentados. [Relatório](../../outputs/etapa9_piloto_v07_r3_20261028/RELATORIO.md) e [auditoria residual](../../outputs/etapa9_piloto_v07_r3_20261028/AUDITORIA_RESIDUAL.md). |
| 5. Carteira e integridade | US$ 4,480425665 comprometidos, abaixo de US$ 5; saldo US$ 0,519574335. Treze reservas desconhecidas históricas preservadas. Código congelado, tabelas anteriores e chamadas 1–834 conferidos; 1.497 arquivos inventariados, sem alterações indevidas. Alterações previstas apenas em STATUS, PLANO e carteira canônica. [Integridade final](../../outputs/etapa9_piloto_v07_r3_20261028/integridade_final.json). |
| 6. Entrega e limites | Relatório, diagnóstico, auditorias, instruções de reprodução, documento da v7, STATUS e PLANO atualizados. A meta encerra a etapa 9 técnica; não inicia auditoria independente ou experimento final. |

## Resultado principal H

| Medida | V6 | V7 revisão 7.2 |
|---|---:|---:|
| Prazo exato | 16/30 | 23/30 |
| Custo exato | 16/30 | 21/30 |
| Análises locais válidas | 195/203 | 220/220 |
| Mediana por execução | 230,47 s | 106,94 s |
| Inferência conhecida da coorte H | US$ 0,465194260 | US$ 0,320810515 |

MAE H zero somente nos 23 pares de prazo e 21 de custo elegíveis, ambos exatos e comparados às referências autorais. Houve oito ganhos e uma perda de cobertura de prazo; seis ganhos e uma perda de custo. Cobertura não equivale à taxa de acerto global. A coorte de desenvolvimento não demonstra generalização nem superioridade isolada do grafo.

## Custo acumulado

A rodada completa consumiu US$ 1,002764765 comprometidos: US$ 0,442764765 de inferência conhecida e US$ 0,56 de provisão de contagem. As duas rodadas interrompidas de desenvolvimento acrescentaram US$ 0,269021210, já incluídos no total. Toda a v7, desde o saldo final da v6, acrescentou US$ 1,271785975.

O acumulado US$ 4,480425665 inclui US$ 2,063925665 de inferência conhecida, US$ 2,228 de provisão de contagem e US$ 0,1885 de reservas de inferência desconhecida anteriores. A provisão de US$ 0,002 por contagem é hipótese conservadora, não tarifa comprovada; o compromisso interno não equivale à fatura. Fontes de preço e cálculo racional separado estão nos artefatos.

## Limitações que permanecem

Três execuções H continuam sem magnitude apesar das referências exatas: k_547a/1 e /2, por encaminhamento de restrição temporal para uma alteração contratual; k_f04b/2, por confirmação estruturada omitida. A última perdeu cobertura em relação à v6. Essas saídas não foram reparadas. A apresentação do catálogo e a exigência conservadora de resolver cláusulas também devem ser consideradas na revisão de aplicabilidade.

H preservou as lacunas reais, mas perdeu informação direcional de custo em k_23d8/1, k_23d8/2 e k_8c65/1. B teve sete rejeições de contrato e um erro de custo de R$150; T teve quatro rejeições e uma direção de prazo excessiva frente à referência. As falhas permanecem nos denominadores e nos arquivos originais.

H passou a usar JSON Schema estrito; B/T conservaram seu modo JSON. Prompt, contrato e coordenação H mudaram juntos. Referências, inferibilidade por view, suporte semântico e equivalência metodológica das condições ainda precisam da revisão independente prevista na etapa 10. Nenhuma conclusão desta entrega substitui essa revisão ou autoriza avanço automático para as etapas 10/11.
