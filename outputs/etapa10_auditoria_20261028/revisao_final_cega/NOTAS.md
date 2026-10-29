# Auditoria técnica cega independente — etapa 10

Esta é uma revisão por agente separado, não um parecer humano. Foram lidos apenas os arquivos de `inputs/` autorizados. Nenhum motor, resultado, referência, README, saída anterior, rede, credencial ou outro agente foi consultado. `estado_projeto.json` foi tratado como representação a conferir, nunca como oráculo. Os números abaixo foram reconstruídos da fonte literal. `calcular.py` usa somente a biblioteca padrão, lê apenas o corpus autorizado e produz `derivacoes.json`.

## Reconstrução da fonte e conferência

Convenção operacional usada nas contas: atividades iniciam no instante factível mais cedo. Assim, os números temporais são os **menores términos factíveis**, sem ociosidade deliberada. A fonte define D0, dias corridos inteiros e intervalos [início,fim); não explicita literalmente a regra de início mais cedo. Esse ponto deve constar do protocolo se as respostas forem chamadas de previsões exatas.

Para facilitar a leitura, A = fixar trilho, B = preparar mapa, C = alinhar cabeçote, D = configurar aquisição, E = validar leitura, M = aceitar estação. As durações são 4, 7, 6, 3, 5 e 0 dias, respectivamente [d_00804cfe59.txt L01 / f_30ebc9d46a]. Todos têm liberação contratual D0; cada aviso parte isoladamente da referência D15 e 520400 centavos [d_00804cfe59.txt L02 / f_2702245368].

A ficha registra exatamente seis arcos FS0: A→C, A→D, B→D [d_30c2c87610.txt L01 / f_f0babac4b4]; C→E, D→E, E→M [mesmo documento L02 / f_db8a874f25]. Não há arco A↔B nem C↔D, e a convergência exige o máximo dos ramos. As durações, os seis arcos e seus tipos/defasagens, as liberações e as parcelas estruturadas coincidem com essas fontes. As transcrições de `fontes.json` coincidem literalmente com os documentos. Não foi encontrada divergência factual nesses dados.

As seis obrigações somam 63500 + 47200 + 138600 + 81900 + 97500 + 91700 = **520400 centavos**. As cinco primeiras somam 428700; o apoio fixo de 91700 já está incluído, uma única vez [d_5f330471d9.txt L01 / f_e631c91e32]. Seu adicional ordinário é 8600 × max(0, fim−15), sem crédito por antecipação; apuração financeira não condiciona execução [d_fcaf0bba4d.txt L01 / f_6e0d1bf111].

## Derivações da união completa H/T

| Situação | A | B | C | D | E | M | Custo total, centavos | Δ prazo | Δ custo, centavos |
|---|---|---|---|---|---|---|---:|---:|---:|
| Referência | [0,4) | [0,7) | [4,10) | [7,10) | [10,15) | D15 | 520400 | 0 | 0 |
| k_1671298a5a | [0,8) | [0,10) | [8,14) | [10,13) | [14,19) | D19 | 554800 | +4 | +34400 |
| k_ec2826cc2a | [0,4) | [0,7) | [4,10) | [7,10) | [10,15) | D15 | 508800 | 0 | −11600 |
| k_c23705f4ea | [0,4) | [0,7) | [4,10) | [7,16) | [16,21) | D21 | 520400 + 6r | +6 | 6r |

A referência possui dois caminhos críticos: A–C–E–M e B–D–E–M, ambos com 15 dias. A–D–E–M dura 12 dias.

No primeiro aviso, A passa a 8 dias e B a 10; não se somam os atrasos dos ramos [d_b32ce294f2.txt L01 / f_24700c5514]. C termina em 14 e D em 13; E termina em max(14,13)+5 = 19. Extensão de 4 dias × 8600 = 34400; custo 520400+34400 = 554800. Caminho crítico A–C–E–M. Todos os valores e deltas são exatos sob a convenção temporal declarada.

No segundo aviso, o crédito de 11600 reduz a obrigação existente de C de 138600 para 127000; não cria outra obrigação [d_51bc5a176a.txt L01 / f_366c4be785]. Todas as variáveis temporais e do apoio são preservadas. Portanto o prazo permanece D15, o impacto temporal é **zero demonstrado** e o custo é 520400−11600 = 508800.

No terceiro aviso, D passa de 3 para 9 dias e sua conclusão passa a D16; E e M chegam a D21 [d_77935f5c87.txt L01 / f_8c614977df]. A mesma fonte revoga expressamente a taxa antiga para toda a extensão desse aviso. O domínio de r é o dos inteiros não negativos em centavos/dia, sem teto. Logo o custo pertence exatamente a {520400 + 6r : r ∈ Z, r ≥ 0}; delta pertence a {6r}. Limite inferior inclusivo 520400 para o total e zero para o delta; nenhum limite superior finito. Exemplos r=0 e r=1 geram 520400 e 520406, respectivamente. Aumento estrito não está demonstrado, nem custo igual ao baseline: **zero é possível, não identificado**. Reutilizar 8600 é inválido. A lacuna financeira não altera o prazo, porque a execução é explicitamente independente da apuração.

H e T, recebendo a união completa, têm a mesma informação factual para essas contas. Não há base documental para limites distintos entre eles.

## O que B pode e não pode inferir

Aqui B significa apenas documentos comuns e o aviso corrente; o documento relacional, a estrutura de relações e seus enunciados exclusivos não podem ser usados como se estivessem disponíveis. Os nomes das atividades tampouco autorizam reconstruir precedências.

O baseline D15 e 520400 é declarado em fonte comum. A soma monetária também pode ser reconstruída sem relações. Para o **segundo aviso**, a ausência expressa de alteração temporal, a referência fixa e a alteração monetária única bastam: B pode identificar D15, delta prazo 0, custo 508800 e delta custo −11600. A ficha relacional não é necessária para essa invariância.

Para os avisos primeiro e terceiro, um término único não decorre de B. O script enumera todos os 29281 DAGs de cinco atividades, com sumidouros ligados ao marco, assumindo adicionalmente FS0, início mais cedo e baseline recalculado D15. Há 1268 DAGs compatíveis. Os términos possíveis são:

- Primeiro aviso: **{18,19,21}**, portanto delta {3,4,6} e, sob essas premissas, custos {546200,554800,572000} centavos.
- Segundo aviso: **{15}**. A invariância é confirmada em todos os DAGs.
- Terceiro aviso: **{15,16,18,19,20,21}**, portanto delta {0,1,3,4,5,6}. A extensão pode ser zero ou positiva. Seu custo global tem limite inferior 520400 e nenhum teto: existe um modelo com extensão de 1 dia e r pode ser qualquer inteiro não negativo.

Esses são conjuntos **condicionais**, não limites justificados apenas pelo texto de B: FS0 e a convergência explícita estão na ficha que B não recebe. A enumeração mostra indeterminação mesmo após conceder mais informação a B. Ela não autoriza a avaliação a penalizar B por não deduzir um limite que usa uma premissa oculta.

Para tornar essa diferença verificável, o script inclui ainda dois modelos de precedências FS com lag fixo de 4 dias, ambos compatíveis com os textos comuns e baseline D15: (i) C→E com lag4, demais atividades independentes convergindo em M, mantém D15 após o primeiro aviso; (ii) A→B com lag4, demais atividades independentes convergindo em M, chega a D22 após o primeiro aviso. Lags de precedência são fatos relacionais possíveis da ficha ausente, não liberações contratuais adicionais. Portanto nem o intervalo [18,21] nem aumento estrito do prazo/custo do primeiro aviso podem ser atribuídos ao corpus B sem acrescentar convenções. As testemunhas são verificáveis em `derivacoes.json`.

No terceiro aviso, B sabe que não há redução monetária: parcelas e fixo persistem, extensão não é negativa e r não é negativo. Isso sustenta limite inferior, não custo exato nem aumento estrito. A antiga taxa está revogada também para B.

## Condições antes do congelamento

Não foi encontrada incoerência entre valores/topologia estruturados e fontes. Os cálculos H/T são reprodutíveis. As seguintes condições precisam ser decididas pelo responsável pelo protocolo, sem consulta a gabaritos:

1. **Definição temporal:** explicitar que o resultado é o término factível mais cedo. Só restrições não antes de D0 e precedências permitem ociosidade arbitrária; sem a convenção, D19 e D21 são mínimos, não datas inevitáveis. Se a convenção já estiver no protocolo externo, esta ressalva estará resolvida — não o li por força da cegueira.
2. **Corpus de B:** não transportar FS0, convergência ou relações da ficha ausente para o julgamento de sua inferibilidade. O caso de crédito é plenamente inferível por B; abstenção obrigatória nele seria incorreta. Os limites enumerados acima dependem de premissas explicitadas e não são um gabarito incondicional de B.
3. **Metadado de lacunas:** `cenarios.json` mantém `lacunas: []` no terceiro aviso, embora a taxa indefinida esteja expressa no relato. Isso não contradiz a evidência literal se o campo significar apenas uma lista não preenchida/auxiliar; contradiz uma leitura de lista exaustiva de lacunas. Definir essa semântica ou registrar a taxa nesse campo evita ambiguidade de avaliação.

Estas são condições de clareza experimental, não motivo para preencher a taxa desconhecida. O congelamento é recomendável após resolver a definição temporal e a semântica do corpus B/metadado, ou confirmar que já estão resolvidas em protocolo externo. O selo foi produzido após finalizar os artefatos e antes de qualquer confronto.
