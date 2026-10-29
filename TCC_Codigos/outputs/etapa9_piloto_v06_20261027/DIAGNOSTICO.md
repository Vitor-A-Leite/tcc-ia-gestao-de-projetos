# Diagnóstico descritivo v05 → v06

Inspeção pós-coleta, sem alterar código, respostas ou classificação. Evidências extraídas com hashes dos originais em [diagnosticos_comparativos.json](diagnosticos_comparativos.json). Não substitui revisão semântica independente.

## O que mudou no H

A v05 tinha 9/30 valores exatos para prazo e custo; a v06 tem 16/30 para ambos (30% → 53,3%, +23,3 pontos percentuais). O saldo de sete reúne oito ganhos e uma perda, nos mesmos pares caso/repetição. Os 16 valores de cada desfecho coincidem com as referências autorais; o MAE zero usa apenas esses 16 pares, não os 30 planejados.

| Caso/repetição que ganhou cobertura | Delta prazo v06, dias | Delta custo v06, centavos |
|---|---:|---:|
| k_09c2 / 2 | 2 | 40000 |
| k_98f3 / 2 | -2 | 0 |
| k_a92f / 1 | 0 | 15000 |
| k_b5e1 / 1 | 0 | 12345 |
| k_b5e1 / 2 | 0 | 12345 |
| k_e168 / 1 | 0 | 30000 |
| k_e168 / 2 | 0 | 30000 |
| k_f04b / 2 | -1 | -10000 |

Valores negativos indicam redução. O ganho inclui impactos de prazo ou custo diferentes de zero; não se restringe a um caso sem impacto. A única perda é k_a064 / 1, antes exato zero para os dois desfechos, agora indeterminado por rejeição do contexto_hash em n_21dc.

## Casos que esclarecem o mecanismo e seus limites

- **k_09c2 / H / 2:** na v06, 12 encaminhamentos foram reconciliados com propostas aceitas e o fechamento ficou completo, resultando em +2 dias e +R$400. A v05 era parcial. A primeira repetição v06 do mesmo caso continuou parcial por direção incompatível em n_e659, mesmo com os nove encaminhamentos reconciliados. Roteamento resolvido não elimina rejeições locais.
- **k_a064 / H / 1:** houve regressão de cobertura por identidade/revisão divergente do contexto_hash em n_21dc. A resposta foi preservada e não foi reenviada. O erro não é uma nova evidência factual sobre o projeto.
- **k_b731 / H / 1:** todos os sete nós passaram a validação local, mas um encaminhamento pediu substituir_duracao em n_a367. O responsável propôs confirmar_manutencao_atributo (três dias), além de confirmar ausência de parcela adicional no escopo da cláusula. Como as operações não coincidem, o fechamento mantém esse encaminhamento pendente. A evidência aponta uma incompatibilidade entre a ação solicitada e a resolução escolhida; uma possível equivalência exige desenho e revisão próprios, sem afrouxar o protocolo desta coleta.
- **k_f04b / H / 1:** todos os nós passaram localmente e os 11 encaminhamentos foram resolvidos, mas faltou resolução explícita da duração/custo da cláusula u_813c. Em n_a367, a proposta substitui duração por três dias com regra_refs e condicoes vazios. O fechamento conservador permaneceu parcial. Na segunda repetição, houve fechamento completo e resultado de −1 dia/−R$100.
- **k_d307 / H / 1:** o fechamento estrutural ficou completo, mas a duração nova permaneceu indeterminada. O resultado conserva prazo indeterminado e custo com direção de aumento e limite inferior de 2.500 centavos. Isso exemplifica fechamento operacional sem inventar total exato.

Há 249 ocorrências de encaminhamentos resolvidas e 25 pendentes, de um total de 274 nas análises aceitas. Vários nós podem encaminhar a mesma operação; esses números não são contagem de operações únicas. Pendências textuais por nó caíram de 42 para três; a classe lexical de permissão/catálogo caiu de 39 para uma. Essa classificação por palavras não prova solução semântica: parte do trabalho foi representada pelo novo campo tipado.

As 14 execuções H parciais incluem oito com rejeição local, uma com autorização operacional pendente (k_23d8/1), duas com pendências textuais (k_23d8/2 e k_8c65/1), uma com encaminhamento sem correspondência (k_b731/1), uma com regra local sem resolução (k_f04b/1) e uma com fechamento completo mas fato indeterminado (k_d307/1). Essas categorias são descritivas desta amostra.

## Custo e estabilidade

H fez 203 chamadas, contra 178 na v05. A mediana por execução passou de 108,95 s para 230,47 s (+111,5%). A inferência conhecida H passou de US$0,279920255 para US$0,465194260 (+66,2%). Houve oito rejeições em 203 análises (cinco de direção e três de hash), contra duas em 178 na v05. Nenhuma chamada desta coleta ficou sem uso conciliado; uma rejeição de conteúdo não é falha de transporte.

A maior cobertura, portanto, veio acompanhada de maior custo/tempo e menor taxa observada de conformidade local. Não há isolamento causal: contrato e prompt mudaram, e as rodadas ocorreram em momentos diferentes.

## Candidato a falsa precisão em B

**k_d307 / B / 1** declarou aumento exato de 2.500 centavos, justificando com a cobrança direta de R$25. A referência autoral admite apenas aumento com limite inferior de 2.500, pois a duração não definida pode afetar outros custos. O resultado exige revisão de suporte/inferibilidade da view B. Ele permanece entre os oito custos exatos retornados por B, mas fica fora dos sete pares de custo elegíveis ao MAE; não é registrado como acerto numérico nem reparado. Na v05 não havia sinal desse tipo nesta coorte. Não foram sinalizados candidatos H/T nesta v06, o que não prova suporte semântico.

## Próxima revisão na etapa 9

Priorizar rejeições de identidade/direção, compatibilidade entre encaminhamento e resolução por cláusula, obrigações não representadas por permissões e a revisão do candidato B. Manter auditoria independente de referências e inferibilidade antes de congelar protocolo para as etapas 10/11. Não houve novo piloto, reenvio ou correção de respostas após a coleta.
