# Rodada 2: resultados

Datas: 24 e 25/11/2026. Manifesto `final2-bc816e3fe6174e5ba0c02c54f294f819`, pasta `outputs/avaliacao_rodada2_tentativa2_20261124/`.

## Desenho

- **Material novo**, gerado por IA sem acesso ao repositório e mais difícil que o da rodada 1: 15 eventos (G01–G15) e 7 documentos com 44 trechos. Os eventos incluem atrasos que convergem, mudança de caminho crítico, propagação desde o início do cronograma, estouro da franquia do laboratório, magnitudes desconhecidas e antecipação de entrega.
- **Gabarito:** duas IAs independentes (IA2: ChatGPT; IA1: a confirmar), com concordância de 93,9% e kappa de 0,896. A amostra de 50 concordâncias foi conferida pelos autores. As 40 divergências (7 padrões) foram decididas pelo agente por regra explícita, porque os autores aprovaram sem indicar escolha (`data/projetos/alfa/final2/DIVERGENCIAS_PARA_DECIDIR.md`). O gabarito tem 386 REVISAR em 660 pares.
- **Condições:**
  - B: sistema híbrido, com validação parcial, citação tolerante, versão normalizada e instruções v4;
  - D: IA sozinha, sem o estado calculado;
  - E: a IA propõe e o código confere;
  - E-voto e B-voto.
- 3 repetições, com uma tentativa por chamada.

## Execução

- **Tentativa 1** (`avaliacao_rodada2_20261124`): interrompida depois de 3 chamadas cortadas em ~61 s pela VPN.
- **Tentativa 2:** 103 tarefas, uma queda de conexão e processos presos. Foi encerrada e retomada com o mesmo manifesto, mas a rede seguiu instável e ela foi pausada de novo.
- **Retomada técnica** (`scripts/retomada_tecnica.py`):
  - executou as 37 tarefas pendentes;
  - refez **uma vez** as 17 tarefas que caíram por rede ou ficaram presas (as tentativas originais estão em `casos/_tentativas_originais/`);
  - falhas do modelo não foram refeitas;
  - o código congelado ficou intacto: só o script de retomada foi acrescentado.
- **Resultado final:** as 156 tarefas têm resposta. B teve **0 falhas** em 21 leituras. D teve 10 falhas de contrato, todas por citação não literal.

## Resultado principal (média das 3 repetições; mín.–máx.)

| | B: sistema híbrido | D: IA sozinha | **E: IA propõe, código confere** |
|---|---|---|---|
| Precisão de REVISAR | 0,959 (0,943–0,969) | **0,985** (0,979–0,988) | 0,960 (0,944–0,969) |
| Revocação de REVISAR | 0,896 (0,878–0,912) | 0,856 (0,832–0,886) | **0,967** (0,961–0,972) |
| **F1 de REVISAR** | 0,926 (0,920–0,937) | 0,916 (0,899–0,934) | **0,963** (0,957–0,969) |
| Acurácia em 4 classes | 0,893 | 0,892 | **0,940** |
| Falsos alertas em trechos corretos (de 196) | 11–18 | 1–4 | 12–19 |
| Pares sem resposta válida | 0 | 42–58 | 0 |

Variantes com voto: B-voto teve F1 de 0,914 e E-voto, de 0,962 (média).

**Leitura:**
- **E supera as duas outras condições** em revocação, F1 e acurácia, e é a mais estável entre as repetições.
- **B ficou ligeiramente acima de D** (0,926 contra 0,916), mas só porque D perdeu respostas por citações não literais.
- **D é a mais conservadora:** quase não dá alarme falso, mas deixa mais frases desatualizadas passarem.

## Comparação justa de robustez (pós-hoc, não substitui o resultado principal)

B usa citação tolerante (maiúsculas e espaços), e D usa citação estrita. Aplicando a D a mesma tolerância sobre as respostas brutas, sem novas chamadas, 5 das 10 falhas de D são recuperadas. O arquivo é `comparacao_posthoc_D_tolerante.json`.

| | Precisão | Revocação | F1 | Acurácia 4 classes | Falhas |
|---|---|---|---|---|---|
| D tolerante | 0,986 | 0,896 | **0,938** | 0,915 | 24 |
| B (principal) | 0,959 | 0,896 | 0,926 | 0,893 | 0 |
| E com D tolerante | 0,960 | 0,967 | **0,963** | 0,940 | 0 |

Com a mesma tolerância, **D fica acima de B**, e **E continua a melhor condição.** Isso também aparece nos 1.090 pares em que D respondeu nas três repetições: B 0,929, D 0,956 e E 0,970.

## Interpretação para o TCC

1. **O sistema híbrido sozinho (B)** fica no mesmo patamar da IA sozinha. Ele é mais robusto (0 falhas) e entrega explicação verificável, com valor calculado e caminho no grafo, mas deixa escapar premissas que não cabem no catálogo de predicados.
2. **A combinação (E)** é o resultado mais forte: o código confere os números e corrige a IA, e a IA cobre o que o código não representa. Ela recupera cerca de 11 pontos de revocação em relação a D, com precisão de 0,96.
3. **Em relação à rodada 1:** com material inédito e as melhorias congeladas antes, B passou de F1 0,64 para 0,93 e de 170 para 0 falhas por repetição.

## Consumo

| | Chamadas | Custo conciliado (USD) |
|---|---|---|
| B | 21 | 0,103 |
| D (incluindo as tentativas refeitas) | 135 + 17 originais | 0,521 + tentativas e reservas anteriores |
| Comprometido no histórico ao final | — | **6,693** (teto de US$ 20) |

## Limites

- **Projeto único e sintético.** O material foi gerado por IA, e o gabarito foi pré-anotado por IAs. As divergências foram decididas pelo agente que construiu o sistema, embora os autores tenham conferido a amostra.
- **O modelo de D é o mesmo da extração de B,** e uma das anotadoras é da mesma família. As regras dadas a D são as mesmas das anotadoras.
- **A retomada técnica refez 17 tarefas** derrubadas pela rede. Isso está documentado e preservado, mas é um desvio do protocolo de "uma tentativa", aceitável apenas para falhas de infraestrutura.
- **3 repetições** não permitem teste estatístico. As diferenças entre B e D (cerca de 1 ponto de F1) estão dentro da variação entre repetições. A vantagem de E (4 a 5 pontos) é maior que essa variação.
