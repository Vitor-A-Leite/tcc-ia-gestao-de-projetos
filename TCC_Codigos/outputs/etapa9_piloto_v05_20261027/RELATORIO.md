# Etapa 9 — piloto v05: 90/90 slots encerrados

27/10/2026, America/Sao_Paulo. **Integração v05 e coleta autorizada entregues para revisão.** O primeiro B falhou por DNS no ambiente restrito antes de inferência; os 89 slots pendentes foram continuados em fase separada com rede escalada. A tentativa 273, seu resultado e a parada original permanecem intactos, sem replay. Estado final: {"terminado": 90}. Paradas da fase de rede: []. Etapas 10/11 não iniciadas.

## Escopo e preservação

O usuário aprovou as correções v05 e outro piloto sob o **mesmo teto acumulado de US$ 5**. Nova coorte de 90 IDs: 15 casos × B/H/T × 2, mesma ordem, inputs/views e parâmetros. gpt-6-luna, High, streaming, Standard/cache 30 min, saída total ≤25.000 tokens, entrada por contagem oficial ≤16.000 tokens, deadline total de 180 s contando contagem + geração, H ≤8 análises/chamadas e 1.500 s, zero retries/fallback. Até 300 tentativas novas contando a 273; teto operacional global de 572; guarda monetária prevalece. Nenhum prompt, protocolo científico ou código congelado foi alterado durante a coleta.

H usa formato 5.0/schema 2/política 5/fronteira 2.0-h e avaliação isolada 2.0-manifesto-h05. B/T mantêm contratos/payloads científicos anteriores. Código aditivo em `src/piloto_v05` e `src/retomada_v05`; carteira canônica continua `etapa9_piloto_real_aprovado_20261026/ledger.sqlite`. Os adendos persistidos registram as autorizações, assinaturas e IDs permitidos. Não houve mudança/reclassificação de resultados v04 ou acesso a gabaritos pelo preditor.

## Cobertura e precisão contra referências autorais

| Condição | Registros | Não iniciados | Prazo exato | Custo exato | MAE dias (n) | MAE centavos (n) |
|---|---:|---:|---:|---:|---:|---:|
| B | 30/30 | 0 | 4/30 | 8/30 | 0 (4) | 0 (8) |
| H | 30/30 | 0 | 9/30 | 9/30 | 0 (9) | 0 (9) |
| T | 30/30 | 0 | 23/30 | 21/30 | 0 (23) | 0 (21) |

N=30 por condição. MAE inclui somente previsão exata válida com verdade exata; não mede desempenho nos demais slots e nunca transforma ausência em zero. Dados completos: `normalizacao.json`, `avaliacao_autoral.json` e `referencias_avaliacao_autoral.json`. Slots não iniciados são classe operacional erro no avaliador, não chamadas efetivamente falhadas. Estados `ok`/`parcial` descrevem execução/contrato, não suporte semântico. B teve 8 erros (1 DNS e 7 rejeições de campos); T teve 3 rejeições de campos. H teve 2 erros locais (hash e direção), sem rejeição de justificativa em lista ou acoplamento de ausência ao total do nó nesta amostra. Não se modificou nenhuma saída. Referências autorais sem validação independente e inferibilidade por view pendente limitam qualquer conclusão científica.

## Latência e custo incremental

| Condição | Tentativas | Latências observadas | Mediana por chamada s | Mediana por slot s | Inferência conciliada USD | Comprometido USD |
|---|---:|---:|---:|---:|---:|---:|
| B | 30 | 29 | 39.1254 | 39.0236 | 0,062462700 | 0,136962700 |
| H | 178 | 178 | 19.5422 | 108.952 | 0,279920255 | 0,635920255 |
| T | 30 | 30 | 25.6799 | 25.6809 | 0,057173250 | 0,117173250 |

Latência observada por chamada inclui contagem+inferência+adaptação, não velocidade pura do modelo. H agrega várias chamadas por slot. Valores ausentes não foram imputados. O B inicial inclui falha DNS~0,38s sem inferência; seu tempo não é latência do modelo. O custo comprometido inclui provisões e reservas desconhecidas; só uso conciliado sustenta custo de inferência conhecido. `resumo_descritivo.json` conserva medidas e denominadores; `contabilidade_e_erros.json` contém conferência monetária independente.

## Comparativo descritivo v04→v05

| Condição | Cobertura exata prazo | Cobertura exata custo | Estados v05 |
|---|---:|---:|---|
| B | 5/30 → 4/30 | 7/30 → 8/30 | {"erro": 8, "parcial": 18, "ok": 4} |
| H | 2/30 → 9/30 | 2/30 → 9/30 | {"parcial": 21, "ok": 9} |
| T | 21/30 → 23/30 | 22/30 → 21/30 | {"ok": 21, "parcial": 6, "erro": 3} |

B/T foram executados novamente com algoritmos e contextos preservados: suas diferenças são novas realizações do modelo, sem atribuição às correções H. Mudaram contrato/prompt/fechamento H; coleta ocorreu em outro momento e inclui falha DNS e diferenças de geração/cache. O comparativo é descritivo, sem teste causal ou alegação de superioridade. Resultados v04 originais continuam intactos: H exato 2/30 correspondia ao mesmo caso de impacto zero em duas repetições. Custo T v04 tinha 22 exatos mas 21 pares elegíveis: T/k_d307/rep1 previu 2.500 centavos exatos frente a referência de aumento/limite inferior de 2.500 sem total exato, uma questão de falsa precisão para revisão.

## Diagnóstico H e falsa precisão

Análises H: `{"total": 178, "ok": 176, "erro": 2, "erro:Identidade/revisão divergente: contexto_hash": 1, "erro:Direção incompatível": 1}`. Fechamentos: `{"parcial": 20, "completo_operacional_condicional": 10}`. Entre os 9 H exatos, 7 são de impacto não zero: k_0ca7, k_42a9 e k_6d82 nas duas repetições, e k_98f3 na primeira; os outros 2 são k_a064. Isso amplia a variedade observada além do único caso de impacto zero do v04, sem demonstrar causalidade ou superioridade. Notas diagnósticas locais preservadas: 1. Erros por execução e registros originais estão nos JSON; nenhum foi reparado, convertido ou reenviado.

O primeiro H/k_09c2/rep1 ilustra uma limitação de escopo: 4 análises passaram o contrato, mas n_73fa e n_42be declararam pendências por não terem permissão para alterar a disponibilidade do componente ou lançar p_07a4. Os contextos confirmam essas permissões locais ausentes. Ao mesmo tempo n_c820 tinha as permissões e propôs D6 e 20.000 centavos; o fechamento reconciliou p_07a4. As fontes já continham data, valor e aceite. Portanto, essa pendência não comprova falta factual global: há possível atribuição de responsabilidade de outro nó ao nó corrente, que o fechamento conservador não resolve. Isso bloqueou downstream e a cláusula u_813c. `diagnostico_primeiro_H.json` preserva contexto, permissões, propostas e hashes para revisão. Não se alterou o protocolo para melhorar esse resultado.

Dos 10 fechamentos completos operacionais, 9 resultaram em prazo/custo exatos. O outro, H/k_d307/rep1, preservou duração nova indeterminada: prazo indeterminado e custo com direção de aumento e limite inferior de 2.500 centavos, sem total exato. Assim, fechamento estrutural completo não força certeza numérica. As pendências H estão preservadas por nó em `resumo_descritivo.json/pendencias_H`. Classes lexicais: `{"alegacao_limite_permissao_ou_catalogo": 39, "alegacao_fato_ausente_ou_outra_pendencia_a_auditar": 3}`; esse agrupamento por palavras não é auditoria semântica. Revisar separadamente fato realmente ausente, limite local de permissão e atribuição de obrigação alheia ao nó.

Há **0 previsões exatas divergentes ou diante de referência não exata** sinalizadas em `resumo_descritivo.json/suspeitas`. São candidatas à revisão de erro/falsa precisão, não adjudicação semântica automática. Ausência de candidato não prova suporte. O contrato exige string para justificativa e não converte listas; confirma ausência no escopo da cláusula, preservando outras obrigações; incidência temporal usa cronograma final. `lacunas` local virou nota, e fatos realmente ausentes precisam de propostas tipadas ou `pendencias_operacionais`. Omissão/má classificação pelo modelo pode gerar falsa precisão; citação/hash e contrato válido não comprovam a conclusão.

## Carteira global final

| Parcela | USD |
|---|---:|
| Comprometido anterior (272 tentativas) | 1,206550975 |
| Comprometimento incremental desta coorte | 0,890056205 |
| Inferência incremental conhecida | 0,399556205 |
| Inferência conhecida acumulada | 0,888107180 |
| Reserva de inferência desconhecida acumulada | 0,188500000 |
| Provisão hipotética de contagem acumulada | 1,020000000 |
| **Comprometido acumulado** | **2,096607180** |
| **Saldo interno sob US$ 5** | **2,903392820** |

510 tentativas acumuladas; 13 custos não conciliados. As 12 reservas desconhecidas anteriores e a reserva integral da 273 permanecem. Provisão de contagem não é tarifa publicada/cobrança comprovada. Preços históricos Standard: US$ 0,10/M de entrada, US$ 0,01/M de leitura de cache, US$ 0,125/M de escrita com retenção de 30 min e US$ 0,50/M de saída; raciocínio já incluído na saída. Reserva máxima de inferência US$ 0,0145 + provisão US$ 0,002 antes de cada chamada; guarda em nanoUSD. Fontes oficiais verificadas pela coordenação: [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [streaming](https://developers.openai.com/api/docs/guides/streaming-responses). Não é fatura e não se inferiu câmbio.

A chave local foi acessada somente pelo carregador autorizado, sem exibição/cópia ou chave alternativa. O rótulo TCC-Impacto-Baseline foi informado pelo usuário; não é inferência da credencial.

## Testes e integridade

**50 testes offline aprovados:** 6 de integração, 19 H, 22 SSE e 3 de retomada. Cinco de integração + 19 H + 22 SSE passaram antes da primeira ativação; o teste adicional do runner H foi concluído após a parada DNS, antes da continuação dos 89 pendentes. O pipeline MOCK usa análises locais válidas e vai do runner à carteira/fronteira/normalização; também verifica falha H anterior a qualquer análise. As 3 contraprovas da retomada verificam 89 IDs, preservação da 273/primeiro resultado/parada e bloqueio de replay/tamper. MOCKs vivem em carteiras temporárias, sem gasto real ou alegação semântica.

Inventário inicial: 1.049 arquivos rastreados presentes no checkout. Só ledger e resumos STATUS/PLANO tiveram alterações permitidas entre os rastreados; tabelas/schemas antigos e chamadas 1–272 preservados, assim como códigos, dados, raw, manifests e snapshots v04. Código v05 confere com adendo congelado. A assinatura da retomada, a 273 e o primeiro resultado são conferidos antes de cada reserva. `integridade_final.json` documenta as verificações. Snapshots: `ledger_antes.sqlite` antes da v05, `ledger_apos.sqlite` após parada DNS; `retomada_89/ledger_antes_rede.sqlite` e `retomada_89/ledger_final.sqlite` delimitam a fase de rede.

Artefatos principais: adendos/manifestos, logs de coleta das duas fases, JSON originais por slot, avaliações, contabilidade, resumo descritivo, diagnóstico H, logs de testes e integridade. `retomada_89/RELATORIO_PARADA_DNS.md` preserva a entrega intermediária. A execução escalada de rede foi aprovada pela revisão automática; não houve rejeição contornada. Nenhum novo commit/push nesta rodada; a coordenação já havia concluído o pedido anterior.

**Próximo passo:** revisão dos resultados, pendências de escopo e candidatos a falsa precisão, antes de qualquer mudança metodológica ou avanço. Nenhum resultado foi corrigido para coincidir com referência. Etapas 10/11 permanecem não iniciadas.
