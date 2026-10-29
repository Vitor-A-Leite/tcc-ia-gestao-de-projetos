# Parecer técnico independente do delta v1 → v2

**Conclusão: v2 está apta ao congelamento quanto à coerência documental, às contas e à inferibilidade auditadas.** As três ambiguidades levantadas em v1 foram resolvidas: o término solicitado é explicitamente o menor término factível; DAG, FS0 e convergência estão agora no corpus comum de B; a taxa indefinida consta em `lacunas` do terceiro cenário. A ausência de taxa continua sendo uma lacuna legítima do problema, não um erro a preencher.

Esta é uma revisão por agente separado após seu próprio parecer de v1, não uma revisão sem memória nem um parecer humano. Foram lidos somente os inputs autorizados de v1/v2. Nenhum gabarito, previsão, motor, código do sistema, referência externa, outro agente, rede ou credencial foi consultado. O raciocínio e a enumeração independentes de v1 foram reaproveitados em um script próprio novo. Nenhum arquivo de v1 foi modificado.

## Delta verificado

Os dois pacotes têm os mesmos 11 arquivos. Mudaram somente `base.json`, `cenarios.json`, `estado_projeto.json`, `fontes.json` e `fontes/d_00804cfe59.txt`:

- Atualização da versão do projeto e do status do pacote.
- Acréscimo literal das convenções em **d_00804cfe59.txt L02 / f_2702245368**, replicado em `fontes.json` e `estado_projeto.json`; nenhum par de precedência foi revelado no acréscimo.
- Anotação da taxa substituta indefinida em `lacunas` do terceiro cenário.

Não houve alteração de durações, valores monetários, avisos, entidades, relações, regras de custo ou documentos relacionais. As transcrições estruturadas e literais conferem. O script registra todos os campos alterados, suas versões anterior e nova, e 59 verificações aprovadas em `derivacoes.json`.

## Reconstrução H/T

A = fixar trilho, B = preparar mapa, C = alinhar cabeçote, D = configurar aquisição, E = validar leitura, M = aceitar estação. Durações de referência: 4, 7, 6, 3, 5, 0 [d_00804cfe59.txt L01 / f_30ebc9d46a]. Relações FS0: A→C, A→D, B→D [d_30c2c87610.txt L01 / f_f0babac4b4], C→E, D→E, E→M [mesmo documento L02 / f_db8a874f25]. Liberação D0 e início mais cedo [d_00804cfe59.txt L02 / f_2702245368].

A referência resulta em A [0,4), B [0,7), C [4,10), D [7,10), E [10,15), M D15. Os caminhos A–C–E–M e B–D–E–M empatam em 15. As parcelas somam 63500+47200+138600+81900+97500+91700 = **520400 centavos** [d_5f330471d9.txt L01 / f_e631c91e32]. O fixo do apoio já está incluído; cobra-se adicional único de 8600×max(0,fim−15), salvo aditivo expresso [d_fcaf0bba4d.txt L01 / f_6e0d1bf111].

| Caso | Cálculo do término | Fim | Δ prazo | Custo total, centavos | Δ custo, centavos |
|---|---|---:|---:|---:|---:|
| k_1671298a5a | max(8+6, max(8,10)+3)+5 | 19 | +4 | 554800 | +34400 |
| k_ec2826cc2a | Cronograma preservado | 15 | 0 | 508800 | −11600 |
| k_c23705f4ea | max(4+6, max(4,7)+9)+5 | 21 | +6 | 520400+6r | 6r |

No primeiro aviso, a revisão altera A para 8 e B para 10 dias, sem cobrança direta [d_b32ce294f2.txt L01 / f_24700c5514]. C termina em 14; D em 13; E em 19. O adicional é 4×8600 = 34400. O atraso dos ramos não se soma.

No segundo, o crédito de 11600 reduz a parcela existente de C de 138600 para 127000; nenhuma variável temporal ou do apoio muda [d_51bc5a176a.txt L01 / f_366c4be785]. Portanto 520400−11600 = 508800 e delta prazo **zero demonstrado**.

No terceiro, D passa a 9 dias e termina em 16; E termina em 21. A taxa antiga é expressamente revogada; r é inteiro não negativo, sem teto [d_77935f5c87.txt L01 / f_8c614977df]. O conjunto exato de custos é **{520400+6r : r ∈ Z, r≥0}**, e o conjunto de deltas é {6r}. Limite inferior inclusivo: 520400 para custo, 0 para delta; sem limite superior finito. r=0 e r=1 produzem 520400 e 520406, respectivamente. O custo não pode diminuir; aumento estrito não está demonstrado. A lacuna financeira não altera o prazo, pois a fonte exclui condicionamento da execução à apuração do preço.

H e T, com a união completa, possuem os mesmos fatos e devem ter os mesmos resultados matemáticos. Não foi avaliado o comportamento de qualquer motor ou preditor.

## Inferibilidade de B com o domínio agora explícito

B recebe os documentos comuns e apenas o aviso corrente. A referência D15/520400 é estipulada na fonte comum. Agora DAG, FS0, convergência e início mais cedo também são fatos disponíveis a B. O script enumera todos os **29281 DAGs rotulados** das cinco atividades; ligar cada sumidouro ao marco garante convergência. Arestas adicionais ao marco são temporalmente redundantes. Dos DAGs enumerados, **1268** reproduzem D15. Nenhuma das seis arestas reais é usada como restrição dessa enumeração.

| Caso | Fins compatíveis com B | Deltas de prazo | Custos compatíveis, centavos | Deltas de custo, centavos |
|---|---|---|---|---|
| k_1671298a5a | {18,19,21} | {3,4,6} | {546200,554800,572000} | {25800,34400,51600} |
| k_ec2826cc2a | {15} | {0} | {508800} | {−11600} |
| k_c23705f4ea | {15,16,18,19,20,21} | {0,1,3,4,5,6} | Todos os inteiros ≥520400 | Todos os inteiros ≥0 |

No **primeiro aviso**, B não identifica um valor único, mas demonstra atraso de pelo menos 3 e no máximo 6 dias, com aumento de custo entre 25800 e 51600 centavos. Os conjuntos discretos acima são mais informativos que os intervalos: por exemplo, D20 não é compatível. Uma prova curta do limite inferior é que uma cadeia original de 15 dias precisa usar A+C+E (4+6+5) ou B+D+E (7+3+5), as únicas somas de subconjuntos iguais a 15. Ambas são afetadas, em 4 ou 3 dias. A enumeração fornece testemunhas para todos os fins possíveis.

Exemplos de topologias que provam a não unicidade, com todos os sumidouros ligados a M: B→D→E, com A e C independentes, produz D18; A→C→E, com B e D independentes, produz D19; A→B→D junto de A→C→E produz D21. Todos possuem baseline D15. As contraprovas com lag4 usadas em v1 **deixam de ser admissíveis em v2**, porque agora FS0 é comum.

No **segundo aviso**, B identifica tudo sem obter as arestas: o aviso preserva o cronograma e o apoio, alterando unicamente uma parcela. A enumeração confirma a invariância em todos os 1268 DAGs. Exigir abstenção de B nesse caso seria incorreto.

No **terceiro aviso**, B não identifica prazo único. A cadeia A→C→E com D independente admite fim D15, mesmo após D passar a 9. Acrescentar B→D fornece outro modelo com baseline D15 e fim D16 após o aviso. Este último tem extensão de um dia; como r pode ser qualquer inteiro não negativo, o conjunto monetário de B contém todos os inteiros ≥520400. Portanto B conhece os limites inferiores de custo e delta, mas nenhum teto. Zero temporal e zero monetário são possíveis, não determinados. Em H/T, o tempo é determinado e o conjunto monetário é mais estreito: os incrementos são múltiplos de 6 centavos.

## Decisão de congelamento

As correções de v2 resolvem as condições documentais do parecer v1. Não resta ambiguidade impeditiva de congelamento no corpus e no escopo desta revisão. A avaliação deve preservar três distinções: **indeterminação com limites** no primeiro caso de B; **inferência exata por invariância** no segundo; **prazo exato e custo indeterminado** no terceiro de H/T. Indeterminação não equivale a zero, e ausência de arestas não equivale a ausência de toda informação quantitativa.

O selo foi gerado após concluir o script, as derivações e este parecer, antes de qualquer confronto externo. Ele contém SHA256 dos artefatos e de todos os inputs v1/v2 lidos. Nenhum selo ou artefato v1 foi alterado.
