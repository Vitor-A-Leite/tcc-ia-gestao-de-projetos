# Etapa 9 — coorte real v04 para revisão

26/10/2026, America/Sao_Paulo. Coorte separada de v03/diagnóstico: 15 casos × B/H/T × duas repetições =90 slots, N30 por condição. Referências AUTORAIS sem validação independente. Modelo gpt-6-luna high, deadline180s, mesmos parâmetros aprovados; H local4.0, sem correção/retry.

|Condição|Terminados/30|Estados|Chamadas novas|Tempo dos slots(s)|Inferência conhecida(US$)|
|---|---:|---|---:|---:|---:|
|B|5/30|{'parcial': 5}|5|179.13|0.01208175|
|H|6/30|{'parcial': 6}|35|1209.25|0.06184861|
|T|6/30|{'ok': 4, 'parcial': 1, 'erro': 1}|6|163.06|0.0127518|

Restantes: 73 não iniciados e 0 iniciados sem resultado. Parada registrada: Falha transporte/integração: http_indisponivel {'status_http': None, 'provider_code': None}. Ausentes não são imputados como zero ou erro numérico. O normalizador preserva denominador30 e sua classe mecânica de erro para ausentes deve ser lida com esse estado de coleta.

|Condição/desfecho|Cobertura exata|MAE (pares exatos válidos)|Estados dos desfechos|
|---|---:|---|---|
|B:prazo|0/30|não calculável; n=0/30|{'exato': 0, 'direcao': 0, 'indeterminado': 5, 'inaplicavel': 0, 'invalido': 0, 'erro': 25}|
|B:custo|0/30|não calculável; n=0/30|{'exato': 0, 'direcao': 3, 'indeterminado': 2, 'inaplicavel': 0, 'invalido': 0, 'erro': 25}|
|H:prazo|0/30|não calculável; n=0/30|{'exato': 0, 'direcao': 0, 'indeterminado': 6, 'inaplicavel': 0, 'invalido': 0, 'erro': 24}|
|H:custo|0/30|não calculável; n=0/30|{'exato': 0, 'direcao': 0, 'indeterminado': 6, 'inaplicavel': 0, 'invalido': 0, 'erro': 24}|
|T:prazo|4/30|0 dia_corrido; n=4/30|{'exato': 4, 'direcao': 0, 'indeterminado': 1, 'inaplicavel': 0, 'invalido': 1, 'erro': 24}|
|T:custo|4/30|0 BRL_centavo; n=4/30|{'exato': 4, 'direcao': 1, 'indeterminado': 0, 'inaplicavel': 0, 'invalido': 1, 'erro': 24}|

|Condições/desfecho|Interseção comparável|MAE na interseção|
|---|---:|---|
|B/H: prazo|0/30|não calculável|
|B/H: custo|0/30|não calculável|
|B/T: prazo|0/30|não calculável|
|B/T: custo|0/30|não calculável|
|H/T: prazo|0/30|não calculável|
|H/T: custo|0/30|não calculável|

Novas tentativas: 46; agregado: 61/300. Inferência nova conhecida US$ 0.08668216; reservas novas integrais sem conciliação US$ 0.033; provisão hipotética nova de contagem US$ 0.092. Reservas integrais já incluem sua provisão: não somar duas vezes. Comprometimento global US$ 0.380502675; saldo interno US$ 4.619497325, sob tetoUS$5. Custos antigos e nove reservas desconhecidas não foram liberados. Contagem é requisição HTTP adicional; provisão não é tarifa publicada. Não é fatura/saldo da conta.

Uso conciliado da coorte: 212036 tokens de entrada e 129032 de saída total, incluindo reasoning. Tempo somado dos slots 1551.44s, sem imputar duração às tentativas cujo relógio não foi preservado. Detalhes de chamadas, erros e custos em contabilidade_e_erros.json; previsões por execução/desfecho em normalizacao.json.

Falhas de formato e de aceitação operacional são resultados originais e podem bloquear dependentes H. Não equivalem a falhas HTTP. Estados indeterminado/direcional/limites permanecem explícitos. O limite autoral indeterminado de k_d307 é conservado separadamente na projeção do avaliador1.0 já revisada; nenhuma verdade/previsão foi convertida em número.

Suporte semântico não auditado; inferibilidade pendente, especialmente nas referências novas. Acerto numérico não prova sustentação. Cobertura/MAE usam subconjuntos explícitos e repetições dos mesmos casos: não permitem declarar superioridade científica por médias selecionadas. Avaliação externa e etapas10/11 aguardam revisão.

Integridade: tabelas históricas e chamadas1–15 comparadas integralmente ao snapshot; hashes dos arquivos anteriores preservados; exports idênticos aos registros SQLite; payload contado/gerado, parâmetros e hashes conferidos. Adendo persistido antes da geração, mesmo SQLite/lock/limites globais. Sem commit/push/deploy. Testes e protocolo em PROTOCOLO.md.

## Previsões originais disponíveis

|Caso|Repetição|Condição|Δprazo|Δcusto|
|---|---:|---|---|---|
|k_09c2|1|B|indeterminado|direção aumento|
|k_09c2|1|H|indeterminado|indeterminado|
|k_09c2|1|T|2 dias|R$ 400|
|k_09c2|2|B|indeterminado|direção aumento|
|k_09c2|2|T|2 dias|R$ 400|
|k_09c2|2|H|indeterminado|indeterminado|
|k_0ca7|1|H|indeterminado|indeterminado|
|k_0ca7|1|B|indeterminado|indeterminado|
|k_0ca7|1|T|2 dias|R$ 150|
|k_0ca7|2|H|indeterminado|indeterminado|
|k_0ca7|2|T|2 dias|R$ 150|
|k_0ca7|2|B|indeterminado|indeterminado|
|k_23d8|1|T|indeterminado|direção aumento|
|k_23d8|1|B|indeterminado|direção aumento|
|k_23d8|1|H|indeterminado|indeterminado|
|k_23d8|2|T|invalido|invalido|
|k_23d8|2|H|indeterminado|indeterminado|

Os quatro resultados exatos T são duas repetições dos mesmos dois casos: k_09c2 e k_0ca7. Não são quatro casos independentes. O terceiro caso k_23d8 ficou incompleto na segunda repetição; seus demais resultados mantêm incerteza/invalidade. Todos os demais casos permanecem não iniciados.

Falhas preservadas: H/k_09c2 teve três rejeições locais em duas execuções (duas por ausência sem custo local zero sustentado; uma por texto obrigatório); T/k_23d8/repetição2 falhou no conjunto de campos do contrato global. Esses retornos foram conciliados e não repetidos. H/k_0ca7/repetição1 teve timeout180s; H/k_23d8/repetição2 teve http_indisponivel e acionou a parada. Não houve erro HTTP com status ou código do provedor que permita atribuir a causa. O worker histórico sanitiza exceções de rede/TLS/leitura/processo; a causa técnica específica permanece indeterminada. Não houve tentativa de contornar a guarda ou testar rede novamente.

Decomposição sem dupla soma: novos US$ 0.08668216 de inferência conhecida + US$ 0.029 de reserva de inferência desconhecida + US$ 0.092 de provisão hipotética de contagem = US$ 0.20768216 comprometidos novos. Global: US$ 0.099002675 de inferência conhecida + US$ 0,1595 de reserva de inferência desconhecida + US$ 0,122 de provisão de contagem = US$ 0.380502675. Foram 46 requisições novas de contagem e 46 inferências marcadas, além das15anteriores.

Validação adicional direcionada: cap agregado300 bloqueia reserva mesmo com saldo financeiro disponível. O teste foi feito sobre cópia do snapshot anterior; a primeira preparação do teste usou cópia do ledger já em execução e corretamente encontrou slot iniciado, então o fixture foi corrigido para o snapshot congelado. Produção não foi alterada. Total desta integração: cinco testes novos e dois testes direcionados de payload/validação, sem repetir suítes amplas.

## Falha61 e opção de retomada para revisão

A mensagem persistida “Falha HTTP sanitizada” identifica o caminho em piloto_real/transporte.py:77: o processo pai recebeu um dicionário de erro do worker. O código http_indisponivel é emitido no except Exception do worker (linha64); a alternativa EOFError/OSError do pai (linha79) usa mensagem distinta (“Resposta HTTP indisponível”). O catch do worker cobre HTTPS/DNS/TLS/envio/leitura, json.loads/sanitização e fechamento. Não preserva classe da exceção nem fase interna; por isso não é possível afirmar rede isolada, descartar bug de integração ou identificar autenticação/modelo/parâmetro/protocolo. A mensagem não corresponde a um HTTP401/403/model_not_found/unsupported_parameter registrado, e também não prova a ausência desses problemas. As44respostas conciliadas anteriores não identificam a causa desta falha.

Evidência segura em falha_call_61.json: slot etapa9-coorte-v04-180s-20261026-k_23d8-H-2, nó n_42be, contagem oficial5601tokens concluída, inferência marcada antes de HTTP, sem response/usage/request_id/status/código do provedor. Tempo da tentativa60791,007ms inclui contagem+inferência; não existe divisão persistida. Deadline180s não foi atingido pelo relógio externo. Slot inteiro131,163s. Não há prova de recebimento/processamento remoto; mantém reserva integralUS$0,0165. Nenhum segredo/header foi consultado ou exposto.

Opção técnica NÃO ATIVADA em opcao_retomada_73.json: lista fechada dos73IDs pendentes, hashes das tabelas congeladas e lista de exclusões. Uma retomada deve registrar adendo e evento de autorização técnica append-only, manter parada_v04 original e todos os17resultados/call61, usar o mesmo SQLite/lock/caps e somente os73pendentes. Um retomador novo, com código e proveniência vinculados ao adendo, pode ler eventos stop/resume em tabela nova; cada nova parada também será append-only. O coletor antigo continuará bloqueado pela parada original. Não apagar parada, reabrir slot terminado, completar retrospectivamente H ou liberar reserva. Mesmos prompts/modelo/configuração/deadline; nenhuma mudança no transporte histórico nesta entrega.

Passagem máxima dos73pendentes:229chamadas novas,290agregadas. Reserva adicional máximaUS$3,7785; comprometimento global máximoUS$4,159002675, sob tetoUS$5. É limite conservador, não gasto previsto. A autorização humana dos90slots e do teto já existe; a decisão técnica de ativar essa opção cabe ao coordenador, sem novo pedido financeiro ao usuário. No momento a coleta permanece parada e nenhum retomador foi ativado.
