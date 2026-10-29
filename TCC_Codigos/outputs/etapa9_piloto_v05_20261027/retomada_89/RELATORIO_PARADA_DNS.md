# Etapa 9 — integração v05 e parada do novo piloto

27/10/2026, America/Sao_Paulo. **A integração v05 foi preparada e testada; a coleta real parou na primeira tentativa por falha de DNS, antes de qualquer inferência.** Não houve retry ou alteração dos parâmetros após a parada. O piloto v05 não foi concluído e não produz comparação de desempenho com v04.

## Autorização e configuração

Autorização humana citada pela coordenação nesta sessão: “Aprovo as correções da v05. Pode pedir ao agente da etapa 9 para integrar a nova versão e rodar outro piloto, mantendo o limite acumulado de US$ 5. Traga os resultados para revisarmos.”

`adendo_aprovado.json` congela nova coorte de 15 casos × B/H/T × duas repetições = 90 IDs próprios, sem substituir qualquer resultado v04. Mesmos inputs, views, ordem balanceada, gpt-6-luna, High, streaming, saída total máxima 25.000 tokens, entrada oficial ≤16.000, Standard, cache30m, deadline **total de 180 s incluindo contagem e geração**, zero retries/fallback; H até oito análises/chamadas e 1.500 s. O teto operacional passa de 272 tentativas anteriores a até 572 (até 300 novas), subordinado sempre ao teto acumulado de US$ 5. Não se reiniciou a carteira ou se liberaram reservas desconhecidas.

H usa formato `5.0-h-local-escopado`, schema `2.0-analise-local`, política `5.0-politica-h-escopada`, fronteira `2.0-h` e avaliação isolada `2.0-manifesto-h05`. B/T conservam os contratos e payloads científicos anteriores. A integração nova está em `src/piloto_v05/`; a contagem e conciliação reutilizam a carteira histórica, com novas tabelas `coorte_v05`, `slots_v05` e `parada_v05`. O transporte v05 valida prompt/descritor antes de reservar; não injeta a antiga nota H 2.0 sobre o prompt v05. Hashes e código congelado permanecem iguais ao adendo. Sem edição de prompts ou semântica durante a coleta. Etapas 10/11 não iniciadas.

## Ocorrência real e estado final

A tentativa **273**, slot `k_09c2/B/repetição1`, marcou o início da contagem oficial. O transporte registrou `http_indisponivel`, fase `envio`, exceção `gaierror`, errno8, sem status HTTP nem código do provedor. Não houve retorno da contagem, envio da inferência, resposta de modelo ou usage. Essa evidência identifica falha de resolução DNS neste ambiente; não permite concluir que houve autenticação recusada, indisponibilidade do modelo ou problema de interpretação.

A guarda registrou `Falha transporte/protocolo: http_indisponivel` e encerrou a execução em aproximadamente **0,38 s** no primeiro slot. Esse tempo mede a falha local, não latência do modelo. O registro bruto sanitizado está no mesmo ledger. Não foi tentada outra chave, outra API, nova contagem ou repetição. Não houve rejeição de aprovação automática; a parada decorreu da guarda de transporte após falha DNS.

| Condição | Planejados | Slots terminados | Pendentes | Inferências enviadas | Prazo/custo exatos | Precisão/MAE | Inferência incremental conciliada |
|---|---:|---:|---:|---:|---|---|---:|
| B | 30 | 1, com erro de transporte | 29 | 0 | 0/30; 0/30 | não estimável | US$ 0 |
| H | 30 | 0 | 30 | 0 | 0/30; 0/30 | não estimável | US$ 0 |
| T | 30 | 0 | 30 | 0 | 0/30; 0/30 | não estimável | US$ 0 |

O avaliador mantém N=30 por condição e MAE=null sem pares elegíveis. Nos JSON, slots ausentes entram na classe operacional `erro`; isso não significa 89 falhas de chamadas: eles **não foram iniciados**. A cobertura zero sobre o planejado descreve a coleta interrompida e não capacidade do modelo. Não há medição de latência ou custo de H/T nesta coorte. Falsa precisão também não é avaliável sem previsões; contagens zero não evidenciam segurança ou acurácia.

## Comparativo descritivo v04/v05

| Condição | v04: prazo exato | v04: custo exato | v05: previsões obtidas |
|---|---:|---:|---:|
| B | 5/30 | 7/30 | 0 |
| H | 2/30 | 2/30 | 0 |
| T | 21/30 | 22/30 | 0 |

As métricas v04 continuam preservadas, sem reprocessamento com v05. Os dois H exatos v04 pertencem ao mesmo caso de impacto zero em duas repetições. O custo T v04 tem apenas21 pares exatos elegíveis e uma previsão exata2500 centavos em `k_d307/rep1` diante de referência autoral com aumento e limite inferior2500, sem total exato: falsa precisão permanece questão de revisão. MAE zero nos pares elegíveis v04 não é acerto universal, nem prova de superioridade. Referências são autorais, sem validação científica independente e com inferibilidade/suporte ainda pendentes.

A v05 não tem observações de IA para avaliar melhorias. `lacunas` local é nota diagnóstica; fatos ausentes precisam estar em propostas tipadas ou `pendencias_operacionais`. Omissão/má classificação pelo modelo pode causar falsa precisão, e validação de contrato/citação não comprova semântica. As correções aprovadas e testes offline não demonstram aderência de um modelo real.

## Testes e integração

**47 testes offline aprovados no fechamento:** seis da integração nova, 19 do H v05 e22 do SSE existente. Os cinco testes iniciais de integração,19 H e22 SSE passaram antes da ativação; o sexto teste ponta a ponta foi acrescentado e executado após a parada, em resposta à revisão da coordenação. Nenhum arquivo do pacote congelado foi alterado para esse teste adicional.

O teste ponta a ponta usa cópia temporária do snapshot anterior, transporte HTTP MOCK e três slots B/H/T. H produz análises locais válidas explicitamente sem interpretação factual, passa por `executar`→LocalV05/LocalSSE→carteira→fronteira→normalização v05 e termina parcial por pendência operacional. Não é execução de IA ou métrica de acurácia. Também se verifica a avaliação de falha H antes de qualquer análise, preservando o denominador e classificando o envelope inválido. Os testes cobrem payload B/T idêntico ao SSE antigo, timeout compartilhado entre operações, pedido v05 sem nota antiga, uma única contagem/geração sem retry, rejeição de versão mista, mesma carteira, IDs273+, não replay, teto572 e bloqueio monetário antes de HTTP.

Os números de chamadas/uso registrados no log MOCK pertencem exclusivamente às cópias temporárias; **não** entram na contabilidade real.

Reprodução sem rede/chave:

```sh
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9_piloto_v05 -v
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9_h_v05
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9_sse_r2
PYTHONPATH=TCC_Codigos/src python3 TCC_Codigos/outputs/etapa9_piloto_v05_20261027/verificar_integridade.py
```

## Carteira acumulada

| Parcela | USD |
|---|---:|
| Comprometimento anterior,272 tentativas | 1,206550975 |
| Reserva integral adicional da tentativa273 | 0,016500000 |
| Inferência incremental conciliada | 0 |
| **Comprometimento acumulado final** | **1,223050975** |
| Inferência conhecida acumulada | 0,488550975 |
| Reserva de inferência desconhecida acumulada | 0,188500000 |
| Provisão hipotética de273 contagens | 0,546000000 |
| **Saldo interno sob teto acumuladoUS$5** | **3,776949025** |

São273 tentativas reservadas,273 contagens marcadas e272 inferências marcadas;13 custos não conciliados (12 anteriores +1 nova tentativa). Ausência de inferência nova não libera automaticamente a reserva: o estado original conservador foi mantido. A provisão de contagem é hipótese de controle interno, não preço publicado nem fatura. A inferência incremental conciliada zero não é alegação de ausência de qualquer cobrança do provedor.

Preços usados pelo código histórico: Standard US$0,10/M entrada,0,01/M leitura de cache,0,125/M escrita30m e0,50/M saída; raciocínio já incluído na saída. A reserva de inferência US$0,0145 por chamada é conservadora para16k entrada/25k saída; a contagem adiciona provisão hipotéticaUS$0,002. Fontes oficiais verificadas pela coordenação nesta sessão: [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [streaming Responses](https://developers.openai.com/api/docs/guides/streaming-responses). Nenhuma consulta a fatura/câmbio.

Foi usado apenas o carregador da chave local configurada, sem exibir/copiar segredo. “TCC-Impacto-Baseline” é o rótulo informado pelo usuário, não inferido da chave. Nenhuma chave alternativa foi adicionada.

## Preservação e entrega

O inventário inicial contém **1049 arquivos rastreados** presentes no checkout (mais que os831 citados inicialmente pela coordenação). `integridade_final.json` verifica que só mudaram, dentro desse conjunto, o ledger por adição autorizada e STATUS/PLANO pela atualização vigente. Código anterior, dados, raw, gabaritos, manifests, outputs e snapshots históricos continuam intactos. Schemas/tabelas antigos e chamadas1–272 conferem integralmente com `ledger_antes.sqlite`; código novo usado pela coleta confere com o adendo. `ledger_apos.sqlite` preserva o estado final.

Artefatos: `adendo_aprovado.json`, `manifesto.json`, `coleta.log`, único JSON do slot B, `testes_integracao.log`, `testes_h_v05.log`, `testes_sse.log`, `normalizacao.json`, `avaliacao_autoral.json`, `referencias_avaliacao_autoral.json`, `contabilidade_e_erros.json`, `integridade_antes.json`, `integridade_final.json`, snapshots antes/depois e resumo de parada. A avaliação lê referências somente pós-coleta e não as incorpora ao preditor.

**Para revisão:** integração pronta, piloto parado legitimamente;89 slots pendentes. Uma continuação exige resolver/verificar conectividade e registrar decisão sobre a parada, preservando a tentativa273 e sem replay automático. Não foi removida a guarda nem iniciado outro lote/carteira para contorná-la. O pedido de commit/push anterior já havia sido concluído pela coordenação; esta execução não fez novo commit/push.
