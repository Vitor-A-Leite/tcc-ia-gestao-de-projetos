# Etapa 9 — resultados da coorte v04 após R2 SSE

27/10/2026, America/Sao_Paulo. N = 90 planejado: 15 casos, B/H/T e duas repetições; N = 30 por condição. A aprovação humana explícita “Autorizo a continuação com streaming” foi recebida no chat coordenador e registrada em arquivo novo, sem alterar o adendo/IDs de 26/10. Este é um consolidado descritivo de fases operacionais distintas, sem equivalência científica presumida. v03/diagnóstico entram somente no orçamento global.

Estado atual: 90/90 terminados, 0 não iniciados e 0 iniciados sem resultado. R2: passagem autorizada concluída.

|Condição|Realizados/30|Não iniciados|Estados observados da execução|
|---|---:|---:|---|
|B|30/30|0|parcial: 19; erro: 6; ok: 5|
|H|30/30|0|parcial: 28; ok: 2|
|T|30/30|0|ok: 21; parcial: 3; erro: 6|

Não iniciados são cobertura pendente, não erros observados do modelo. Os estados abaixo contam somente registros efetivamente produzidos. Não há imputação de valores zero aos ausentes, inválidos ou indeterminados.

|Condição/desfecho|Estados observados|Cobertura exata /30|MAE em pares exatos válidos|
|---|---|---:|---|
|B/prazo|indeterminado: 19; invalido: 6; exato: 5|5/30|0 dias; n=5/30|
|B/custo|direcao: 8; indeterminado: 9; invalido: 6; exato: 7|7/30|0 centavos BRL; n=7/30|
|H/prazo|indeterminado: 28; exato: 2|2/30|0 dias; n=2/30|
|H/custo|indeterminado: 28; exato: 2|2/30|0 centavos BRL; n=2/30|
|T/prazo|exato: 21; indeterminado: 3; invalido: 6|21/30|0 dias; n=21/30|
|T/custo|exato: 22; direcao: 2; invalido: 6|22/30|0 centavos BRL; n=21/30|

|Par/desfecho|Interseção comparável|MAE na interseção|
|---|---:|---|
|B/H/prazo|1/30|{'B': 0, 'H': 0}|
|B/H/custo|1/30|{'B': 0, 'H': 0}|
|B/T/prazo|5/30|{'B': 0, 'T': 0}|
|B/T/custo|7/30|{'B': 0, 'T': 0}|
|H/T/prazo|2/30|{'H': 0, 'T': 0}|
|H/T/custo|2/30|{'H': 0, 'T': 0}|

## Fases operacionais separadas

|Fase|Slots|Chamadas|Contagens / inferências marcadas|Inferência conhecida US$|Reserva de inferência desconhecida US$|Provisão de contagem US$|
|---|---:|---:|---|---:|---:|---:|
|Primeira|17|46|46 / 46|0,08668216|0,029|0,092|
|R1|3|10|10 / 10|0,01532866|0,0145|0,02|
|R2 SSE|70|201|201 / 201|0,37421964|0|0,402|

|Fase/condição|Realizados|Estados|Chamadas|Tempo por slot: média / mediana / faixa (s)|
|---|---:|---|---:|---|
|Primeira/B|5|parcial: 5|5|35.83 / 34.39 / 32.58–41.79; n=5|
|Primeira/H|6|parcial: 6|35|201.54 / 176.87 / 131.16–355.73; n=6|
|Primeira/T|6|ok: 4; parcial: 1; erro: 1|6|27.18 / 23.22 / 17.17–42.87; n=6|
|R1/B|2|erro: 1; parcial: 1|2|35.85 / 35.85 / 29.60–42.09; n=2|
|R1/H|1|parcial: 1|8|229.64 / 229.64 / 229.64–229.64; n=1|
|R1/T|0|não executado|0|sem medição|
|R2 SSE/B|23|parcial: 13; erro: 5; ok: 5|23|38.12 / 39.84 / 12.15–66.90; n=23|
|R2 SSE/H|23|parcial: 21; ok: 2|154|205.32 / 201.55 / 73.55–293.44; n=23|
|R2 SSE/T|24|ok: 17; erro: 5; parcial: 2|24|26.14 / 24.36 / 15.47–48.76; n=24|

H inclui suas análises locais no tempo do slot; B/T usam uma chamada global. Tempos são de execução local total, não latência isolada de raciocínio/rede. Custos/tokens só usam usage verificável; custos e tempos desconhecidos não viram zero.

|Fase/condição|Exatos prazo / realizados|MAE prazo; pares / realizados|Exatos custo / realizados|MAE custo; pares / realizados|
|---|---|---|---|---|
|Primeira/B|0/5|não calculável; 0/5|0/5|não calculável; 0/5|
|Primeira/H|0/6|não calculável; 0/6|0/6|não calculável; 0/6|
|Primeira/T|4/6|0.0 dias; 4/6|4/6|0.0 centavos BRL; 4/6|
|R1/B|0/2|não calculável; 0/2|0/2|não calculável; 0/2|
|R1/H|0/1|não calculável; 0/1|0/1|não calculável; 0/1|
|R1/T|não executado|não calculável|não executado|não calculável|
|R2 SSE/B|5/23|0.0 dias; 5/23|7/23|0.0 centavos BRL; 7/23|
|R2 SSE/H|2/23|0.0 dias; 2/23|2/23|0.0 centavos BRL; 2/23|
|R2 SSE/T|17/24|0.0 dias; 17/24|18/24|0.0 centavos BRL; 17/24|

As coberturas por fase acima usam somente os realizados naquela fase e são descritivas de subconjuntos selecionados pela interrupção. A tabela consolidada mantém o denominador planejado 30. Repetições do mesmo caso não são casos independentes; interseções consolidadas podem atravessar fases e não isolam efeito do transporte.

## Contabilidade e integridade

Global: 272/300 tentativas. US$ 0,488550975 de inferência conhecida + US$ 0,174 de reserva de inferência desconhecida + US$ 0,544 de provisão hipotética de contagem = **US$ 1,206550975 comprometidos**. Saldo interno US$ 3,793449025, sob teto acumulado US$ 5. Reservas integrais já incluem sua parcela de provisão: não somar duas vezes. Provisão não é tarifa publicada; comprometimento não é fatura ou saldo da conta.

Coorte v04: 257 requisições de contagem e 257 inferências marcadas; usage conciliado 1231174 tokens de entrada e 696726 de saída total incluindo reasoning. A fase R2 está identificada por adendo/código/transporte em cada resultado. A aprovação explícita e a ativação têm registros próprios; o bloqueio anterior continua preservado como histórico.

Conferidos: âncoras das 20 saídas e chamadas 1–71, tabelas e paradas históricas, fontes e código R2 congelados, exports idênticos ao SQLite, parâmetros/hashes do payload com stream true, contagem JSON correspondente, soma de custos e caps. Snapshot final e chamadas originais R2 foram exportados. A avaliação reutiliza métricas e adaptação do limite indeterminado k_d307 já revisadas, sem alterar referências ou previsões. Referências são AUTORAIS, sem validação científica independente.

## Falhas e limites de interpretação

Nenhuma guarda de parada R2 acionada; os resultados originais ainda podem conter falhas de contrato, incerteza ou recusa.

Falhas de formato e aplicação operacional são resultados preservados, sem reparo/retry. Respostas failed/incomplete, recusa e erros SSE não foram convertidos em previsão parcial válida. Uso verificável em terminal legítimo foi mantido quando disponível. SSE preserva Response terminal e resumo de eventos; texto de deltas não foi remontado em previsão. [Erros e contabilidade](contabilidade_e_erros.json), [previsões observadas por execução](previsoes_observadas.json) e [integridade](integridade_final.json).

Streaming foi uma mitigação operacional autorizada para testar, sem comprovar a causa dos fechamentos anteriores em aproximadamente 60,8 s. Não há equivalência científica presumida entre fases. Suporte semântico não auditado e inferibilidade pendente; coincidência numérica, MAE selecionado ou poucos acertos T com ausências B/H não demonstram superioridade. Indeterminação causada por falha operacional não é abstenção semanticamente validada. Nenhum zero sustentado é presumido.

Entrega para revisão do usuário antes de qualquer avanço. Etapas 10/11 não iniciadas; sem commit, push ou deploy.

|Condição v04|Chamadas|Tempo médio total por slot (s)|Inferência conhecida US$|Reserva de inferência desconhecida US$|Provisão contagem US$|Comprometimento US$|
|---|---:|---:|---:|---:|---:|---:|
|B|30|37.58|0,06816875|0|0,06|0,12816875|
|H|197|205.38|0,35138421|0,0435|0,394|0,78888421|
|T|30|26.34|0,0566775|0|0,06|0,1166775|

## Causas observadas e pontos para revisão antes da etapa 10

A cobertura exata de H foi baixa: 2/30 em cada desfecho. Os dois resultados são **o mesmo caso k_a064, nas duas repetições, com delta zero**; não demonstram previsão quantitativa de impacto não nulo nem zero semanticamente auditado.

Nos 30 H, o fechamento operacional foi parcial em 20 e completo condicional em 10. Desses 10, oito ainda tiveram prazo/custo indeterminados e apenas dois exatos. Houve 197 análises locais: 174 passaram o contrato e 23 falharam. As falhas incluem 20 rejeições de contrato e três falhas de transporte anteriores ao SSE (um timeout e dois http_indisponivel). Passar o contrato não equivale a suporte semântico ou a fechamento completo.

Entre as 20 rejeições locais: 15 mensagens “Texto obrigatório”, três “Ausência exige zero local sustentado”, uma divergência de contexto_hash e uma “Direção incompatível”. A revalidação offline das 15 respostas originais localizou justificativa retornada como lista/array, em vez da string não vazia exigida, em todos os 15 casos, no mesmo validador. Isso identifica a rejeição mecânica; não explica por que o modelo escolheu esse tipo de saída. [Rastros dessa revalidação](texto_obrigatorio_revalidacao_offline.json).

Exemplo de contrato: H/k_09c2/repetição 1/n_a367 propôs confirmar_ausencia_parcela_adicional com valor 0 e simultaneamente avaliou custo local exato +20000 centavos. O contrato exige custo local zero sustentado para essa confirmação, então rejeitou a análise. A consistência/granularidade entre confirmação de uma cláusula e custo total do nó precisa revisão semântica e de contrato; não foi declarada causa-raiz ou corrigida nesta coleta. Em H/k_0ca7/repetição 2, houve fechamento operacional completo mas permaneceu a lacuna original sobre data final/aditivo: é indeterminação registrada, não falha HTTP e tampouco abstenção adequada já validada.

Globais: seis erros de contrato em B e seis em T. Dez rejeições foram por conjunto de campos incompatível; uma T por view_hash divergente e uma T por fonte/localizador não visível. Não são erros numéricos imputados; são saídas inválidas observadas. Todas as 201 chamadas R2 tiveram uso conciliado e nenhuma falha de transporte ou guarda de parada nessa fase.

**Falsa precisão frente à referência autoral:** T/k_d307/repetição 1, na fase R2, apresentou custo total exato +2500 centavos (R$ 25,00), justificando pela cobrança direta única. A referência conserva direção aumento e apenas limite inferior 2500, sem total exato, pois o prazo/apoio permanece indeterminado. A previsão coincidiu com o limite inferior e o apresentou como total. Ela permanece original; integra a cobertura de 22 exatos, mas não os 21 pares elegíveis do MAE e não é o 22º acerto confirmado de custo. Isso é um achado da revisão numérica, sem afirmar auditoria semântica independente.

|Fase/condição|Casos distintos / pares caso-repetição|Inferência conhecida US$|Reserva de inferência desconhecida US$|Provisão contagem US$|Comprometimento US$|
|---|---|---:|---:|---:|---:|
|Primeira/B|3 / 5|0,01208175|0|0,01|0,02208175|
|Primeira/H|3 / 6|0,06184861|0,029|0,07|0,16084861|
|Primeira/T|3 / 6|0,0127518|0|0,012|0,0247518|
|R1/B|2 / 2|0,0047071|0|0,004|0,0087071|
|R1/H|1 / 1|0,01062156|0,0145|0,016|0,04112156|
|R1/T|0 / 0|0|0|0|0|
|R2 SSE/B|12 / 23|0,0513799|0|0,046|0,0973799|
|R2 SSE/H|12 / 23|0,27891404|0|0,308|0,58691404|
|R2 SSE/T|12 / 24|0,0439257|0|0,048|0,0919257|

Casos por fase não devem ser somados como independentes: a primeira fase contém 3 casos/6 pares caso-repetição, R1 contém 2 casos/2 pares e R2 contém 12 casos/24 pares, com sobreposição entre fases. O consolidado tem 15 casos únicos, duas repetições por condição.

|Fase|Latências por chamada preservadas / chamadas|Média / mediana / faixa (s)|
|---|---|---|
|Primeira|44/46|29.78 / 28.07 / 9.39–57.37|
|R1|9/10|26.72 / 26.30 / 17.90–42.09|
|R2 SSE|201/201|30.97 / 25.55 / 9.36–81.05|

Latência por chamada inclui contagem, inferência e adaptação local; somente IDs/tempos preservados, sem estimar ausentes. As três falhas de transporte anteriores não entram nessa tabela por falta do vínculo call_id no envelope de erro, mas seus tempos originais e reservas permanecem nos rastros/snapshots.

Antes da etapa 10, recomenda-se revisar: (1) evidências, confirmações e lacunas de H e a granularidade da regra de ausência; (2) exigências de interface, justificativas de tipo incompatível e cópia de hashes/referências, com eventual mudança futura versionada e nunca reparo seletivo destas respostas; (3) referências autorais e inferibilidade por view; (4) a falsa precisão de T e os denominadores de avaliação. Essa revisão não foi executada como auditoria semântica e nenhuma melhoria metodológica foi implementada. A entrega aguarda revisão do usuário; etapas 10/11 permanecem não iniciadas.


Evidências para inspeção: [referências autorais e projeção](referencias_avaliacao_autoral.json), [avaliação e interseções](avaliacao_autoral.json), [resumo estruturado](resumo_resultados.json), [diagnóstico descritivo](diagnostico_descritivo.json), [aprovação humana SSE](../aprovacao_humana_streaming_20261027.json), [ativação versionada](../ativacao_r2.json). As 201 chamadas R2 originais estão em `chamadas_originais_R2/`; o SQLite final está em `snapshot_pos_execucao/ledger.sqlite`.
