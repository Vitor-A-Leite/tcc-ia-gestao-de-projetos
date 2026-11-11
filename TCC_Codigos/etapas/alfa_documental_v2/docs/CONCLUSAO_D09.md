# Inspeção da seleção de D09

Na continuação autorizada a partir de D04, D04–D08 terminaram. D09 parou no
filtro de seleção: a IA sugeriu `SUP_MOTOR`, mas preencheu `ambiguidades` com
“O valor da parcela p_10 está desconhecido, aguardando confirmação em centavos
de BRL.” Não houve falha de transporte nessa chamada e seu consumo foi conciliado.

O assistente inspecionou a resposta e `CHANGE.D09 §1`. Ambos identificam
`SUP_MOTOR`; a fonte informa expressamente que o preço está desconhecido.
Portanto, o aviso é uma lacuna do atributo monetário, não uma dúvida sobre a
entrada. No escopo da instrução do usuário para continuar o lote, o assistente
aceitou a entrada já sugerida e preservou o preço desconhecido. Não houve uma
nova autorização humana específica para essa seleção, nem uma segunda sugestão.

Essa é uma **intervenção do assistente após parada do filtro**, registrada como
exceção à aceitação automática sem ambiguidades. Não apresentar o lote como
inteiramente automático ou como uma seleção aprovada por uma pessoa. A resposta
original, o aviso, a interrupção e os resultados D01–D08 permanecem intactos.

`scripts/concluir_lote_d09.py` vincula a inspeção à fonte e à resposta exatas,
rejeita outro aviso ou nó e não altera o filtro geral, o runtime, os prompts ou
o modelo. Copia o checkpoint sem análises locais de D09, desconta a chamada de
sugestão dos tetos e segue com as análises locais e revisões separadas D01–D09.
Não lê a referência autoral antes de salvar todas as previsões e revisões.
Cada nova chamada continua sujeita aos tetos da etapa, do lote e do total de
US$20; qualquer falha para a execução sem repetição automática.

Esse episódio sugere uma futura distinção explícita entre ambiguidades na
identificação das entradas e lacunas dos valores do evento. Tal mudança deve
ser avaliada numa nova versão, preservando esta coleta tal como ocorreu.
