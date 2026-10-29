# Etapa 9 — H v06: encaminhamentos entre nós

27/10/2026, America/Sao_Paulo. **Correção offline implementada para revisão.** A continuidade foi solicitada pelo usuário nesta conversa. A etapa 9 permanece em desenvolvimento; etapas 10/11 não iniciadas. Nenhuma nova chamada paga foi realizada.

## Ponto de retomada

O piloto v05 terminou com 90/90 execuções: H teve 9/30 resultados exatos e 21 parciais. A revisão apontou que alguns nós alegavam falta de permissão para alterações atribuídas a outro nó. Em H/k_09c2/rep1, n_73fa e n_42be registraram esse tipo de pendência; n_c820 tinha permissão para alterar a disponibilidade e lançar p_07a4. Isso foi conferido nos contextos e fontes preservados, sem corrigir a saída histórica.

O bloqueio foi reproduzido com um cenário sintético de quatro nós: n_alpha registra a falta de permissão para p_aa11, cuja custódia pertence a n_join. Na v05, essa pendência impede o processamento dos sucessores. O teste inicial falhou ao esperar resultado completo; a suíte agora conserva essa reprodução como contraprova da v05.

## Implementação

Pacote aditivo `src/hibrido_v06`, sem alterar os módulos congelados v04/v05:

- Contexto explicita `responsabilidades_operacionais`, derivadas das permissões de cada nó. O catálogo contém somente nó, operação, alvo, atributo e unidade. Não contém valores esperados nem inferência de responsabilidade econômica.
- A resposta inclui `encaminhamentos`, com rota externa exata, motivo e evidências visíveis. Uma obrigação local não pode ser encaminhada. Propostas continuam limitadas às permissões do próprio nó.
- O fechamento resolve cada encaminhamento apenas com uma proposta aceita do responsável na passagem atual, correspondente a todos os campos da rota. Uma permissão, outro encaminhamento ou uma nota não satisfaz essa exigência.
- Encaminhamentos podem preceder ou suceder o responsável na ordem topológica. Não causam segunda passagem, novas chamadas, reordenação nem alterações automáticas em outro nó.
- Encaminhamento sem resolução deixa o resultado final parcial. Dados indeterminados continuam indeterminados mesmo quando existe proposta correspondente. `pendencias_operacionais` em texto continuam bloqueando; não há classificador lexical que as apague.
- Confirmações `confirmar_*` continuam locais e vinculadas à cláusula. Encaminhá-las sem identificar o escopo exato é rejeitado.
- As decisões acumuladas são reiniciadas a cada avaliação. O cache é revalidado; resoluções de uma passagem anterior não satisfazem a atual por memória residual.
- Política, plano, evento e snapshot são vinculados. Alterá-los exige construir uma nova política. A normalização confere os encaminhamentos resolvidos contra o rastro de análises e propostas aceitas.

O motor matemático v05 é reutilizado. As fronteiras que mudam de contrato foram versionadas separadamente; não se modificaram globals nem se converteram respostas antigas para o novo schema.

| Fronteira | Versão |
|---|---|
| Formato local | `6.0-h-encaminhamentos` |
| Contexto | `3.0-contexto-no-local` |
| Resposta | `3.0-analise-local` |
| Política | `6.0-politica-h-encaminhamentos` |
| Envelope H | `3.0-h` |
| Manifesto | `3.0-manifesto-h06` |

## Validação

**27 testes v06 aprovados, também sob Python -O; 181 testes de regressão aprovados.** Regressões: etapa 4 (37), etapa 5 (21), etapa 6 (24), etapa 7 (49), H v05 (19), piloto v05 (6), retomada v05 (3) e SSE (22). Total: 208 testes distintos, mais a repetição dos 27 sob otimização.

Cobertura nova: resolução antes/depois do responsável; ausência de proposta; operação diferente; ciclos de encaminhamentos; falta factual; custo desconhecido; responsável rejeitado; limite de análises; cache; adulteração de política/catálogo; escopo de cláusulas; timeout sem retry; transporte, fronteira, normalizador e métricas; rejeição de mistura de versões e de reconciliação adulterada. Os catálogos dos 15 casos de desenvolvimento foram conferidos contra suas permissões.

Na demonstração **sintética e prescrita**, o cenário antes bloqueado chega a Δprazo = 2 dias e Δcusto = 11.000 centavos, com uma única contabilização da obrigação. As contraprovas sem proposta responsável e com falta factual permanecem parciais. São respostas simuladas em contratos diferentes; isso não demonstra que o modelo real produzirá encaminhamentos corretos ou que a cobertura científica aumentou.

Comandos a partir da raiz do repositório:

```sh
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9_h_v06 -v
PYTHONPATH=TCC_Codigos/src python3 -O -m unittest discover -s TCC_Codigos/tests/etapa9_h_v06 -v
PYTHONPATH=TCC_Codigos/src python3 TCC_Codigos/tests/etapa9_h_v06/demonstrar_escopo.py --saida /tmp/tcc-v06-demo.json
```

A demonstração exige destino novo e não sobrescreve artefatos existentes. A API pública mantém `construir`, `avaliar`, `executar_h`, `LocalV06` e `SimuladoV06`. Não há transporte pago v06: a carteira v05 rejeita pedidos com esse formato antes de reservar uma chamada.

## Evidências e limites

Artefatos novos em [etapa9_h_v06_offline_20261027](../../outputs/etapa9_h_v06_offline_20261027/): demonstração sintética completa, catálogo do caso k_09c2, logs normais/otimizados, resumo das regressões e inventários de integridade. Os **1.153 arquivos preexistentes inventariados** de código, dados, testes e outputs foram preservados, incluindo o ledger. A carteira continua com 510 tentativas e US$ 2,096607180 comprometidos, sem gasto incremental.

A revisão de causa identifica uma limitação de representação e coordenação: a v05 oferece apenas pendência textual bloqueante para uma ação externa; a v06 representa o encaminhamento e confere sua resolução. Não foram eliminadas pendências dos 30 resultados H antigos, nem criadas novas métricas sobre eles.

O catálogo é informação operacional adicional no prompt H, derivada do estado/plano. Portanto, a v06 constitui novo protocolo e não pode ser misturada à v05. Permanecem sem auditoria independente o suporte semântico, as referências autorais e a inferibilidade por condição. O modelo ainda pode omitir uma falta, encaminhar a operação errada ou apresentar evidência que não sustenta a proposta; validação estrutural não demonstra semântica. O contexto maior também precisa ter contagem oficial de tokens aferida antes de um piloto real.

**Próximo marco:** revisar o contrato v06, integrar uma nova coorte ao coletor e avaliar seu comportamento real sob o orçamento acumulado. Esse piloto, o congelamento científico e a progressão para etapas 10/11 não foram executados nesta entrega.
