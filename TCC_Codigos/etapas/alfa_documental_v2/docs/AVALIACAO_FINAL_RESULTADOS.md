# Avaliação final: resultados

Rodada de 23/11/2026, manifesto `final-b1dc3192a27a44868ca48366f84913dd`, pasta `outputs/avaliacao_final_tentativa2_20261123/`. O protocolo está em `docs/AVALIACAO_FINAL_PROTOCOLO.md`.

Unidade de análise: o par (evento, trecho). São 510 pares por repetição, em 3 repetições. O gabarito tem 273 pares REVISAR.

## Resultado principal (protocolo congelado)

| Medida (média das 3 repetições; mín.–máx.) | B: sistema híbrido | D: IA sozinha |
|---|---|---|
| Precisão de REVISAR | 0,949 (0,922–1,000) | **0,983** (0,976–0,991) |
| Revocação de REVISAR | 0,510 (0,300–0,696) | **0,857** (0,817–0,901) |
| F1 de REVISAR | 0,644 (0,462–0,793) | **0,915** (0,896–0,937) |
| Acurácia em 4 classes | 0,705 | **0,890** |
| Pares sem resposta válida (FALHA) | 170 por repetição | 34 por repetição |

**Pelo protocolo, a IA sozinha superou o sistema híbrido.** A diferença vem principalmente das falhas: quando um documento falha na condição B, ele fica sem resposta nos 15 eventos de uma vez. Na condição D, uma falha afeta só um evento e um grupo de documentos.

## Desempenho quando há resposta válida

| Medida (agregada nas 3 repetições) | B | D |
|---|---|---|
| Pares com resposta válida | 1.020 de 1.530 | 1.427 de 1.530 |
| Precisão / revocação / F1 nos pares válidos | 0,937 / 0,935 / 0,936 | 0,983 / 0,935 / 0,958 |
| Nos 957 pares válidos nas duas condições | 0,937 / 0,934 / 0,935 | 0,985 / 0,929 / 0,956 |

Com resposta válida, as duas condições ficam próximas. A revocação é praticamente igual, e D tem menos falsos alertas: 6 contra 26 nos pares comuns.

## Causas das falhas e dos erros de B

**Falhas de extração (6 documentos em 21):**
- 4 por **"não mapeado" duplicado**: o mesmo trecho de observações foi listado duas vezes, provavelmente uma por ser opinião e outra por citar outro projeto.
- 2 por **citação não literal**:
  - uma só pela maiúscula inicial ("A Liberação…" em vez de "a Liberação…");
  - outra por paráfrase ("caminho crítico agora passa por compras e fabricação").

São falhas de **rigidez do contrato**, não de leitura errada do conteúdo.

**Erros nos pares válidos** (somados nas repetições em que o documento foi válido):
- **ACTION_LOG.A3, 15 falsos alertas:** **defeito do avaliador.** A IA extraiu a versão como `"revisão 1"` e o código comparou esse texto com `"1"` sem normalizar.
- **RISK_REGISTER.R2, 15 omissões:** o sistema marcou DECISAO_HUMANA, e o gabarito diz REVISAR. Esse caso é o padrão **P5** das divergências, em que a IA anotadora 1 também tinha marcado DECISAO_HUMANA.
- **STATUS_C.OBSERVACOES, 11 omissões:** a premissa "intervalo antes da montagem" não cabe no catálogo de predicados. É o padrão **P2**.
- **STATUS_A.ENGENHARIA, 9 falsos alertas; STATUS_D e STATUS_C.CUSTOS, 4:** casos isolados.

## Análise de sensibilidade pós-hoc (não substitui o resultado principal)

`scripts/sensibilidade_final.py` reavalia B sobre as **respostas brutas já gravadas**, sem nenhuma chamada nova, com ajustes identificados depois da rodada.

| B, média das 3 repetições | Precisão | Revocação | F1 | Acurácia 4 classes | Documentos válidos |
|---|---|---|---|---|---|
| Principal (congelado) | 0,949 | 0,510 | 0,644 | 0,705 | 6 / 4 / 5 |
| (a) Validador tolerante a maiúsculas e a "não mapeados" duplicados | 0,959 | 0,855 | 0,898 | 0,885 | 7 / 6 / 7 |
| (b) (a) mais normalização da versão | **0,988** | 0,855 | **0,912** | 0,899 | 7 / 6 / 7 |
| D, para comparação (principal) | 0,983 | 0,857 | 0,915 | 0,890 | — |

Com os dois ajustes, B fica no mesmo nível de D (F1 0,912 contra 0,915), com precisão um pouco maior. Esses números foram obtidos **depois de conhecer os erros**. Para valer como resultado, os ajustes precisariam ser congelados e testados numa rodada nova, com material inédito.

## O que cada condição oferece além do rótulo

- **B:** cada recomendação traz a afirmação extraída, o valor calculado pelo motor e o caminho determinante no grafo. A explicação é verificável por código. A IA não faz cálculo: só lê.
- **D:** a justificativa é texto livre da IA. Ela precisou calcular datas e custos sozinha a partir do estado inicial. A compatibilidade de motivo nos acertos foi alta nas duas condições: 96–97% em D e 93–97% em B.

## Consumo

| Item | Chamadas | Custo (USD) |
|---|---|---|
| Tentativa 1, interrompida pelo corte da VPN | 31 | 0,0465 conciliado + 0,21 em reservas de uso desconhecido |
| Testes de conexão | 2 | 0,0049 + 0,015 em reserva |
| Tentativa 2: B | 21 | 0,0768 |
| Tentativa 2: D | 135 | 0,3489 conciliado + 0,045 em reservas (3 falhas de rede) |
| **Total do dia** | 189 | **cerca de 0,75 comprometido** |
| Comprometido no histórico | — | 5,7177 (teto de US$ 20) |

## Limites

- Material único e sintético, gerado por IA e revisado pelos autores. Gabarito pré-anotado por IAs: as divergências foram decididas por regra pelo agente que construiu o sistema, e a amostra de concordâncias **ainda não foi conferida pelos autores**.
- Os padrões P2 e P5 decididos no gabarito explicam parte dos erros de B. Com outra decisão em P5, B ganharia 15 acertos.
- D e uma das anotadoras podem ser da mesma família de modelo. As regras dadas a D são as mesmas das anotadoras, o que tende a favorecer D. O gabarito foi construído com o mesmo tipo de raciocínio que D faz.
- O catálogo de B foi ampliado depois de ler o material final.
- 3 repetições não bastam para conclusões estatísticas: a variação entre elas foi grande em B (F1 de 0,46 a 0,79).
