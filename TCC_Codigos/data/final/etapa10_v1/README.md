# Etapa 10 — conjunto final prospectivo v1

Projeto fictício inédito **Estação de leitura Sálvia** (`q_c1ef1393c8`). O pacote contém três avisos isolados, todos observados em D0, com cinco atividades e um marco final (seis nós quantitativos, abaixo do limite H8). Os identificadores são opacos e foram gerados para este pacote. Valores monetários são inteiros em centavos de BRL; tempos são dias corridos inteiros.

## Uso e isolamento

- `inputs/base.json`: catálogo comum, linha base declarada e segregação de documentos.
- `inputs/estado_projeto.json`: estado normalizado, seis precedências explicitamente fundamentadas, regras de custo e fontes comuns/relacionais, sem avisos.
- `inputs/fontes.json`: catálogo documental comum, relacional e de avisos, distinguido por `documento_id`; os espelhos textuais ficam em `inputs/fontes/`.
- `inputs/cenarios.json`: os três avisos; carregar somente o aviso corrente com os documentos comuns e relacionais vigentes. Não acumular os avisos.
- `referencias/gabaritos_autorais.json`: derivação manual do autor, separada dos inputs. Proibida sua inclusão nas views, prompts, normalização ou revisão cega. O revisor independente deve resolver os inputs antes de confrontar referências.

Os inputs não têm rótulos de família nem respostas esperadas dos avisos. A linha base fixa é dado do problema. Documentos comuns são `d_00804cfe59`, `d_5f330471d9`, `d_fcaf0bba4d`; o relacional é `d_30c2c87610`; cada aviso possui seu próprio documento, sem sobreposição. Não há seleção de nós por gabarito.

## Proveniência e limites

Autoria prospectiva de casos novos. Para compatibilidade, foram consultados apenas os schemas/fontes presentes nos inputs de desenvolvimento `projeto_minimo_v1` e `ampliacao_v1`, o estado da ampliação e os módulos `src/condicoes/views.py` e `src/piloto_real/politica.py`. Não houve consulta a previsões, outputs, gabaritos ou resultados anteriores; não houve execução do motor, de candidato, rede, credencial ou chamada paga durante a autoria.

A topologia tem duas raízes: uma delas bifurca; o segundo ramo recebe a outra raiz; ambos convergem antes da validação e do marco. É uma estrutura nova de seis nós e seis arestas, com orçamento e durações próprios. Os avisos usam apenas alterações de dados e parâmetros já presentes, sem acrescentar nós ou relações. Toda relação tem fonte e justificativa operacional no documento relacional.

A seleção dos três avisos é **intencional e limitada pelo orçamento**, em um único projeto sintético. Não é amostra representativa, prova externa nem estimativa de desempenho em projetos reais. O nome FINAL registra a reserva prospectiva para a etapa 10, não uma alegação de validação independente. O autor dos casos e o revisor cego devem ser distintos.

A autoria verificou serialização, referências documentais, segregação e contas manuais. A revisão cega e o congelamento oficial pertencem à coordenação da etapa; a estabilidade dos inputs deve ser registrada antes da revisão. Resultados não devem orientar substituição posterior dos casos.
