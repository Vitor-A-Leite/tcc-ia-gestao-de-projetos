# Etapa 9 — diagnóstico de até duas chamadas com deadline de 180 s

26/10/2026, America/Sao_Paulo. **Diagnóstico executado e entregue para revisão.** Não houve retomada do coletor v03 nem avanço às etapas 10/11.

O usuário aprovou até duas chamadas com deadline maior, preservando os demais parâmetros e o teto acumulado de US$ 5. Foram usados exatamente os payloads das tentativas originais 1 (B global) e 4 (H local, componente `n_c820`): hashes e objetos enviados conferem. Modelo `gpt-6-luna`, High, 25.000 tokens máximos de saída total, entrada por contagem oficial ≤16.000, Standard, cache30m, zero retries/fallback. O corpo dos contextos, inclusive identidades/metadados originais, não foi reescrito; o deadline HTTP efetivo é registrado no envelope externo do adendo.

A segunda chamada só foi liberada após a primeira completar com formato válido. As novas tentativas são 14 e 15 no **mesmo ledger**, em slots diagnósticos separados. A parada original continua registrada. Os 90 slots, os seis resultados anteriores e os registros das 13 tentativas originais foram comparados ao snapshot anterior e estão inalterados. Não se substituiu B R1 nem se compôs um H retrospectivo.

## Resultados

| Diagnóstico | Contagem | Inferência | Total | Resultado |
|---|---:|---:|---:|---|
| B global, payload da tentativa 1 | 0,737 s | 38,776 s | **39,523 s** | Completa, JSON e contrato válidos; prazo indeterminado, custo aumenta sem magnitude exata |
| H local, payload da tentativa 4 | 0,531 s | 54,802 s | **55,344 s** | API completou; JSON válido, mas contrato operacional inválido |

As duas respostas chegaram depois dos 30 s antigos. Isso dá evidência favorável à insuficiência temporal **para estas novas tentativas**, sem provar a causa de todos os timeouts anteriores: geração e cache variam entre chamadas. A contagem consumiu menos de um segundo em cada diagnóstico; o restante foi predominantemente a espera pela inferência. Não é comparação de desempenho B/H/T nem evidência de superioridade.

“Completa” descreve o término da resposta da API, não certeza numérica. B manteve a indeterminação expressa pela falta de relações e declarou aumento de custo sem total exato. A resposta foi preservada, sem ajuste ao gabarito. O diagnóstico H é uma análise de nó, não previsão final de prazo/custo do projeto, e não foi aplicado ao motor.

## Causa exata da rejeição local

A resposta **não tem JSON sintaticamente inválido**. Identidades de execução/evento/nó, revisão, versões de predecessores e hash do contexto conferem. A primeira rejeição do validador é `ContratoInvalido: Condição fora de catálogo`, no campo:

`propostas[0].condicoes[0].predicado`

O contexto fornecido tinha `contexto.predicados=[]`. O modelo devolveu frases livres em vez de referências permitidas:

| Campo | Conteúdo devolvido | Permitido |
|---|---|---|
| `propostas[0].condicoes[0].predicado` | “O lote original tem disponibilidade de referência em D2 e o lote substituto foi comunicado como disponível em D6.” | catálogo vazio |
| `propostas[1].condicoes[0].predicado` | “A obrigação p_07a4 é uma cobrança adicional única de R$200,00 pela troca e foi expressamente indicada como não incluída no orçamento.” | catálogo vazio |

Observação estrutural adicional: `propostas[0].valor=6` e `propostas[1].valor=20000` são inteiros escalares. Para `substituir_disponibilidade` e `adicionar_parcela`, o contrato exige objeto Conhecimento com estado/valor/direção/evidências/lacunas/motivo. Esta observação é estática; não se removeram condições ou converteram valores para tentar fazer o original passar.

**Comparação com o adaptador normal:** reaplicou-se offline `LLM.analisar` com transporte mock que devolve o mesmo texto recebido, no mesmo contexto original. Ele chama os mesmos `_json` e `validar` e reproduziu `saida_invalida / Condição fora de catálogo`. Portanto a rejeição não nasceu de contexto/parser diferente no novo diagnóstico. Essa revalidação derivada não é uma nova execução de IA e não substitui o registro pago.

**Orientação disponível:** o catálogo vazio estava explicitamente no JSON de entrada. O prompt descrevia condições e permissões, mas não dizia explicitamente que `predicado` deve copiar um ID de `contexto.predicados` nem que catálogo vazio exige `condicoes=[]`. O formato da API era `json_object`, sem schema restritivo por campo. Assim, há não conformidade objetiva da resposta e uma lacuna de orientação/estruturação a melhorar; não cabe atribuir exclusivamente ao modelo ou declarar uma proposta semanticamente errada sem auditoria. O suporte continua não auditado.

## Custo incremental e acumulado

As duas inferências tiveram uso conhecido: 6.565 tokens de entrada e 10.049 de saída total; os 7.504 tokens de raciocínio **já estão incluídos** na saída. Custo reconferido com aritmética independente, sem duplicar cache ou raciocínio.

| Parcela | USD |
|---|---:|
| Inferência B deste diagnóstico | 0,001950880 |
| Inferência H local deste diagnóstico | 0,003139810 |
| **Inferência incremental conciliada** | **0,005090690** |
| Provisão hipotética adicional de duas contagens | 0,004000000 |
| Comprometimento incremental | 0,009090690 |
| Inferência conciliada acumulada (lote + diagnóstico) | 0,012320515 |
| Reserva de inferência antiga ainda desconhecida | 0,130500000 |
| Provisão hipotética acumulada de 15 contagens | 0,030000000 |
| **Comprometimento interno acumulado** | **0,172820515** |
| **Saldo interno livre do teto de US$ 5** | **4,827179485** |

As nove reservas integrais antigas de US$ 0,1485 continuam mantidas; incluem US$ 0,018 de provisão e não são somadas novamente à tabela. São 15 inferências e 15 contagens marcadas acumuladas, sem terceira chamada neste adendo. A provisão de contagem não é tarifa publicada/cobrança comprovada; não se consultou fatura nem se inventou câmbio. O saldo é do controle interno, não da conta do provedor.

O programa carregou a chave local existente. O rótulo TCC-Impacto-Baseline é informação anterior do usuário, não inferência da credencial. Nenhum segredo foi exibido/inventariado ou chave trocada.

## Implementação, validação e próximo ajuste

O pacote novo `src/diagnostico_etapa9/` acrescenta o adendo e seus dois slots em tabelas separadas do mesmo SQLite. Usa o lock, a reserva, a contagem agregada e a conciliação da carteira original. Não altera os módulos/payloads/manifesto v03, não remove a parada e não abre outra carteira. Retomada não repete diagnóstico iniciado; primeira inválida/incompleta/timeout impede a segunda. Sete testes offline passaram, também sob Python `-O`, cobrindo essas fronteiras. Os testes usaram cópias temporárias e mocks, sem gasto real.

**Próximo ajuste concreto para revisão, não implementado aqui:** tornar o contrato local explícito no prompt/schema: predicados somente do catálogo, `condicoes=[]` quando vazio e `valor` como Conhecimento nas operações quantitativas, distinguindo confirmações escalares. Validar offline com esta resposta original como contraprova e com respostas válidas novas; nenhuma conversão automática que “conserte” a previsão. Uma futura mudança para schema restritivo deve ser versionada e ter tokens recontados. Não mudar simultaneamente modelo, dados ou seleção H, nem retomar os 90 slots ou fazer novas chamadas sem a próxima decisão de revisão.

Etapa 9 permanece parcial: o diagnóstico resolveu a dúvida de disponibilidade temporal para estas chamadas e revelou uma incompatibilidade de contrato local. Não completou o piloto, a auditoria semântica, a inferibilidade por view ou a validação científica independente.

## Artefatos

- `execucao/adendo_aprovado.json`: autorização, vínculo aos payloads e hashes de código.
- `execucao/resumo.json` e os dois JSON diagnósticos: respostas originais sanitizadas e estados preservados.
- `revalidacao_offline_local.json`: campos, catálogos e comparação com o adaptador normal, sem rede/reparo.
- `diagnostico_formato_local.json`: primeira causa e observações estruturais derivadas.
- `contabilidade_verificacao.json`: aritmética independente, saldo e preservação do original.
- `testes_offline.log` / `testes_offline_otimizado.log`: sete testes aprovados em cada execução.
- Ledger canônico: `../etapa9_piloto_real_aprovado_20261026/ledger.sqlite`, agora acrescido das duas chamadas e das tabelas de diagnóstico, sem alterar seus registros originais.
