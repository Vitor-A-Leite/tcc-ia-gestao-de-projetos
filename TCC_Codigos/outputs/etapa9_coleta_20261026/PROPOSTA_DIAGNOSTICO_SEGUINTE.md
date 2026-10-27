# Adendo diagnóstico proposto — não executado/não incorporado ao v 03

26/10/2026, America/Sao_Paulo. Objetivo: testar se o deadline 30 s está impedindo obter respostas válidas no modo High, distinguindo tempo de falha de formato/interpretação. Não é nova amostra científica, retentativa automática ou autorização para reiniciar o lote. Original 90 slots e seus resultados/ausências permanecem imutáveis. O teto agregado continua US$ 5, com saldo e reservas anteriores mantidos.

## Hipótese e desenho mínimo

Propor **até 2 inferências diagnósticas**, sequenciais, começando por apenas 1. Alterar somente o deadline HTTP da tentativa para **180 s totais**, incluindo contagem; instrumentar tempos separados de contagem e inferência. Manter modelo gpt-6-luna, High,25 k saída total,16 k entrada por contagem oficial, Standard, cache 30 m, zero retries, nenhuma ferramenta/fallback. Não alterar prompts, dados, seleção H, cláusulas ou respostas esperadas nesta comparação.

1. Reutilizar o payload público sanitizado integral da tentativa 1(B, k_09c2 R 1), que terminou por timeout. Registrar seu hash original e preservar o novo retorno em um **slot de diagnóstico separado**, sem preencher ou substituir o slot B original.
2. **Somente se a primeira terminar e produzir conteúdo completo**, fazer uma chamada local com o payload integral da tentativa 4(H, componente n_c820, k_09c2 R 1), também cortada por timeout. É diagnóstico de transporte/parser local, não uma execução H completa; não compor artificialmente esse nó com análises anteriores para produzir um H retrospectivo.

As identidades copiadas dentro dos payloads pertencem aos contextos originais; um envelope externo de diagnóstico recebe ID novo e origem/payload_hash/vínculo ao original, sem inserir a resposta no avaliador dos 90 slots. Isso permite manter o corpo de entrada idêntico. Essa repetição deliberada só pode ocorrer como **adendo revisado**, nunca através da retomada automática de`--rodar` ou de uma nova pasta/novo orçamento. A variabilidade de geração e estado de cache continuam limitações; duas chamadas não provam causalidade geral do timeout.

## Critérios de parada e leitura

- Timeout/erro de transporte/modelo/parâmetro na primeira: parar o diagnóstico, não executar a segunda, não repetir e manter reserva.
- `incomplete` com uso conhecido: preservar bruto/uso, classificar como truncamento/limite, parar antes da segunda. Não converter em resposta válida nem aumentar tokens automaticamente.
- Completa mas parser inválido: preservar conteúdo e distinguir problema de formato; parar e revisar antes da segunda. Não reparar JSON ou sentido.
- Completa com formato válido em≤30 s: não confirma que o limite antigo era a causa; variabilidade permanece.
- Completa/válida em>30 s e≤180 s: evidência favorável à insuficiência temporal para **essa nova tentativa**, não prova sobre todos os timeouts originais.
- Interpretação/aritmética errada com formato válido: conservar e auditar depois, sem substituição pelo gabarito. Não mudar simultaneamente prompt/modelo/dados.

Medir monotonicamente contagem e inferência separadas; persistir request/hash, retorno bruto,`status/incomplete_details`, modelo solicitado/observado, usage/cache e duração. Não obter ou expor raciocínio privado; usar apenas campos de uso e resposta fornecidos pela API. Uma eventual revisão de seleção dos nós H fica para outra alteração de desenvolvimento, isolada deste teste de tempo.

## Mesmo saldo acumulado, sem zerar ledger

Estado original:13 inferências/13 contagens marcadas, US$ 0,163729825 comprometidos, US$ 4,836270175 de saldo interno. Desconhecidos originais continuam reservados; nenhuma recuperação de cobrança foi demonstrada.

| Proposta | Nova reserva máxima | Comprometido acumulado máximo | Saldo interno mínimo |
|---|---:|---:|---:|
| Só a primeira chamada | US$ 0,0165 | US$ 0,180229825 | US$ 4,819770175 |
| Até duas chamadas | US$ 0,0330 | US$ 0,196729825 | US$ 4,803270175 |

Cada reserva segue o mesmo US$ 0,0145 máximo de inferência+US$ 0,002 de provisão de contagem. O total de tentativas passaria no máximo de 13 para 15, ainda dentro de 300 agregadas; as 2 contagens seriam HTTP adicionais. A tarifa de contagem continua não publicada nas fontes consultadas: provisão é hipótese, não cobrança comprovada. O adendo deve manter a mesma limitação financeira explícita. Não aumentar o teto, zerar custo desconhecido ou tratar ausência de uso como zero.

## Implementação necessária antes de executar

Não usar o CLI atual: ele tem deadline 30 s versionado, hash de plano rígido e parada registrada. Não remover manualmente a parada para “destravar”. Uma implementação revisável deverá:

1. Registrar adendo versionado com 2 IDs diagnósticos, no máximo 1 tentativa por ID, payloads/hashes originais, deadline 180 s e vínculo ao hash do plano/ledger pós-parada.
2. Estender **o mesmo** ledger de forma transacional/append-only para identificar chamadas de diagnóstico sem alterar os 90 slots originais, mantendo o mesmo lock, contador agregado 300 e soma comprometida≤US$ 5. Nenhuma segunda carteira/orçamento em pasta nova.
3. Manter a parada do coletor v 03; permitir somente os IDs do adendo revisado, nunca os 83 slots pendentes nem reenvio do slot interrompido. Planejar no máximo 1 reserva por ID, com custo desconhecido conservado na retomada.
4. Validar offline concorrência/retomada e o saldo anterior preservado, mais exportação separada e classificação de tempo/formato/interpretação. Registrar migração/hash/código novos sem reescrever o manifesto histórico.

Isso requer revisão técnica do adendo e liberação específica das duas chamadas dentro do teto já aprovado; **nenhuma nova rodada foi iniciada nesta entrega**. Só depois dos achados decidir se convém revisar o protocolo do restante da etapa 9. Não iniciar etapas 10/11.
