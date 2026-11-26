# Melhorias do sistema híbrido para a rodada 2

Data: 23/11/2026. Motivação: na rodada final (`docs/AVALIACAO_FINAL_RESULTADOS.md`), o sistema híbrido (B) perdeu para a IA sozinha (D) por fragilidade da leitura, não por julgamento pior. Estas mudanças foram feitas **depois** de ver aqueles resultados e só valem como evidência numa rodada nova, com material inédito.

## Mudanças

| Mudança | Onde | Por quê |
|---|---|---|
| Validação **parcial**: descarta só a afirmação inválida, funde "não mapeados" repetidos e completa trechos sem decisão (`sem_decisao`) | `extracao.validar_extracao(..., modo='parcial')` | Uma citação ruim derrubava o documento inteiro nos 15 eventos |
| Citação tolerante a maiúsculas e espaços, ajustada para o trecho literal | `extracao.casar_citacao` | "A Liberação" em vez de "a Liberação" recusava a leitura |
| Voto entre leituras independentes do mesmo documento | `extracao.combinar_extracoes` | A leitura não depende do evento: ler 3 vezes continua barato |
| Normalização de versão ("revisão 1" = "1") | `conteudo._versao_normal` | Defeito que gerou 15 falsos alertas por repetição |
| Predicado `intervalo` (dias entre o fim de A e o início de B, ou se há espera) | `conteudo._avaliar_intervalo`, contrato v4 | Premissas como "intervalo antes da montagem" e "dois dias antes do redutor" ficavam fora do catálogo |
| Datas do estado atual dentro de frases condicionais passam a ser extraídas | instruções v4 | Ex.: "levaria a validação para depois de D35" supõe a validação hoje em D35 |
| **Condição E: a IA propõe, o código confere** | `avaliacao_final.agregar_e` | Junta o julgamento de D com a conferência numérica do motor |
| Comparação com B, D, E, B-voto e E-voto; análise pós-hoc sem sobrescrever o resultado congelado | `scripts/avaliacao_final.py comparar --posthoc-modo-validacao` | — |

Regra da condição E, por trecho:
- Decision Log: sempre PRESERVAR.
- Se o código achou alguma afirmação desatualizada, vale REVISAR.
- Se a IA disse REVISAR, a marcação é mantida só pelas informações que **não** coincidem com afirmações já conferidas pelo código. Nos números que verificou, o código prevalece.
- Se uma das leituras falhou, vale a outra.

As instruções v3 da rodada final estão preservadas em `SISTEMA_V3`. O manifesto da próxima rodada registra o modo de validação. Testes: 161 aprovados, e os predicados e regras novos foram exercitados só em D01–D09.

## Estimativa pós-hoc nos dados da rodada final (não é resultado)

Respostas brutas já gravadas, sem chamadas novas. As leituras de B foram revalidadas no modo parcial, com o avaliador atual. O arquivo é `outputs/avaliacao_final_tentativa2_20261123/comparacao_posthoc_parcial.json`.

| Média das 3 repetições | Precisão | Revocação | F1 | Acurácia 4 classes | Falhas |
|---|---|---|---|---|---|
| D: IA sozinha | 0,983 | 0,857 | 0,915 | 0,890 | 34 |
| B: validação parcial | 0,985 | 0,935 | 0,959 | 0,941 | 0 |
| B-voto (3 leituras votadas) | 0,985 | 0,938 | 0,961 | 0,943 | 0 |
| E: B + D | 0,975 | 0,957 | **0,966** | 0,937 | 0 |
| E-voto | 0,976 | 0,957 | **0,967** | 0,939 | 0 |

Essa estimativa usa material já visto e ajustes feitos depois de conhecer os erros, e não inclui o predicado `intervalo` nem as instruções v4, que exigem chamadas novas. Ela indica que o sistema tem potencial, mas não é resultado: só uma rodada com material inédito confirma.

## Rodada 2: o que falta

1. **Material novo e mais difícil**, gerado pelo prompt abaixo numa sessão sem acesso ao repositório.
2. **Gabarito** pelo mesmo procedimento: duas IAs com os estados já calculados, divergências decididas e uma amostra conferida pelos autores. Desta vez, de preferência, os autores decidem as divergências.
3. **Preparar o manifesto** com `modo_validacao='parcial'` e as instruções v4, e rodar B, D e E com 3 repetições. O custo é parecido com o da rodada final: cerca de US$ 0,45, com reserva máxima de US$ 2,34.

## Prompt para gerar o material da rodada 2

O prompt é o mesmo da rodada final, com estas instruções no lugar da "Parte 1" e da "Parte 2":

```text
Parte 1: 15 eventos de mudança, cada um aplicado sozinho ao estado inicial, mais
difíceis que um atraso simples. Distribua assim:
- 3 eventos com DOIS atrasos em ramos diferentes que convergem na montagem,
  em que só um deles passa a determinar o prazo (o outro é absorvido);
- 2 eventos que mudam o caminho crítico (o fornecedor crítico deixa de ser e
  outro passa a ser);
- 2 eventos no início do cronograma (requisitos, projeto conceitual, CAD ou
  análise estrutural) que se propagam por toda a cadeia;
- 2 eventos de testes que estouram a franquia do laboratório (custo extra por
  dia) sem ou com mudança do fim do projeto;
- 2 eventos com magnitude desconhecida ou só com faixa ("entre D22 e D24",
  "valor a negociar");
- 2 eventos combinando prazo e preço no mesmo comunicado;
- 1 evento que adianta uma entrega (sem efeito no fim, mas com mudança de folga);
- 1 evento de outro projeto.
Cada evento deve permitir determinar os novos valores sem ambiguidade, exceto
os de magnitude desconhecida ou faixa.

Parte 2: documentos em prosa, mais longos e com mais referências cruzadas:
- 4 Status Reports com 6 a 8 seções, em estilos diferentes; ao menos dois
  devem citar folgas, durações, valores de parcelas, semanas ("fim da quinta
  semana") e relações entre datas ("o sensor chega três dias antes da placa",
  "há uma espera entre compras e montagem");
- 1 Action Log com 6 ações; 1 Risk Register com 6 riscos, alguns com datas de
  referência dentro de frases condicionais ("um atraso levaria a validação
  para depois de D35"); 1 Decision Log com 4 decisões.
Inclua de propósito: paráfrases sem nome de fornecedor; frases sem informação
verificável; uma frase de outro projeto; uma contradição dentro do MESMO
trecho; e um erro já presente no estado inicial (uma data trocada).
Não repita eventos nem frases do material anterior.
```
