# Alfa v2 com IA real — execução e avaliação

Data: 10/11/2026. Modelo: **GPT-6 Luna (`gpt-6-luna`), reasoning high**. Entrada e documentos preparados em JSON. Credencial local reutilizada, sem inclusão do segredo no código ou nos resultados.

**O fluxo integrado concluiu o cenário D02 e acertou os valores finais e as classificações documentais da referência de desenvolvimento. A revisão das propostas intermediárias identificou uma alteração local sem suporte explícito, que não afetou os totais. Portanto, houve sucesso operacional e equivalência dos resultados finais, com uma fragilidade semântica a corrigir.**

Este é um piloto de desenvolvimento em um caso, com uma tentativa interrompida e uma rodada concluída. Não é uma validação conclusiva de todos os cenários ou de projetos reais. Os quantitativos e o evento do Alfa são sintéticos, mas as interpretações desta coleta foram produzidas pela API real.

## O que foi executado

O evento D02 informa que o fornecedor do motor passou a estar disponível em D25, mantendo os demais parâmetros contratuais e durações. A referência inicial era D18 para o fornecedor, D40 para o projeto e R$152.000 de custo total.

A IA recebeu o relato e o catálogo compacto e sugeriu **SUP_MOTOR**, sem ambiguidades. O agente aceitou essa sugestão conforme a delegação expressa do usuário; o registro não apresenta essa escolha como revisão humana independente. O máximo permitido foi configurado em **32 nós executáveis**, entre49 entidades visuais com documentos. O alcance cadastrado exigiu13 nós. Os outros19 mantiveram seus dados no cálculo integral, com dispensa explícita de interpretação.

Foram analisados: SUP_MOTOR, C_MOTOR, T_ASSEMBLY, M_PROTO_READY, TEST_EMC, TEST_LIFE, TEST_LOAD, TEST_SEAL, TEST_THERMAL, M_VALIDATION, T_DOC, T_RELEASE e M_RELEASE. A seleção automática não forneceu os impactos; cada contexto local foi interpretado e o motor determinístico calculou os resultados.

## Resultado do projeto

| Medida | Antes | Depois | Diferença |
|---|---:|---:|---:|
| Disponibilidade do fornecedor | D18 | D25 | +7 dias |
| Conclusão do projeto | D40 | D45 | +5 dias |
| Custo total | R$152.000 | R$153.500 | +R$1.500 |

O atraso total é menor que o deslocamento da disponibilidade porque a rede já possuía folga. A montagem manteve sua duração de5 dias. A parcela de gestão `p_19`, regida por `OVERHEAD`, passou de R$12.000 para R$13.500: cinco dias além da base contratada, a R$300 por dia. Não foi observado custo adicional indevido de laboratório neste caso.

O resultado tem prazo e custo classificados como completos. A comparação automática, realizada **após salvar a previsão**, confirmou equivalência dos valores/estados, das cinco classificações documentais e das recomendações com a referência autoral existente.

## Recomendações documentais

Todas se referem ao documento **STATUS, versão1**. São recomendações pendentes de validação, não edições executadas.

| Trecho/localizador | Conteúdo vigente | Recomendação |
|---|---|---|
| §SR.FINISH | Conclusão D40 | Atualizar para D45 |
| §SR.COST | R$152.000 | Atualizar para R$153.500 |
| §SR.MOTOR | Fornecedor disponível D18 | Atualizar para D25 |
| §SR.FREEZE | Informação compatível | Manter |
| §SR.CAD | Versão compatível | Manter |

A recomendação contém documento, versão, localizador, valor atual/proposto, referências a trechos e cálculo de origem. Action Log, Risk Register e Decision Log permanecem no escopo de triagem já implementado; não houve avaliação geral da prosa desses documentos.

## O que deu certo

- Sugestão de entrada real, válida e coerente com a menção explícita do evento.
- Interpretação de13 nós com o mesmo modelo/configuração e sem respostas manuais de simulação.
- Respostas locais aceitas pelos validadores de estrutura e permissões; fechamento completo de prazo/custo.
- Integração entre interpretação, dependências, cálculo e localização de trechos documentais.
- Distinção entre três campos a revisar e dois já compatíveis, sem editar documentos oficiais.
- Registro dos pedidos, respostas, uso informado, seleção, sessão e resultados antes da avaliação.
- Controles financeiros preservaram o comprometimento histórico e impediram avanço do primeiro piloto além do limite técnico.

## O que falhou ou exige refinamento

### 1. Teto inicial de contexto inadequado

A primeira tentativa parou em T_ASSEMBLY: a contagem oficial retornou20.530 tokens, acima do teto inicial16.000. Essa inferência não foi enviada. A sugestão e duas análises locais anteriores haviam terminado.

O teto passou a64.000 tokens de entrada, sem truncar fatos ou alterar prompts, dados ou modelo. A reserva por tentativa passou a US$0,015, suficiente para64k de entrada e16k de saída aos preços usados. A segunda rodada concluiu. São duas tentativas com configurações técnicas diferentes, não duas repetições científicas do mesmo protocolo. A primeira permanece preservada.

### 2. Proposta intermediária questionável apesar dos totais corretos

Em M_PROTO_READY, a IA propôs trocar a restrição própria `release_M_PROTO_READY` de0 para25. Citou o evento de disponibilidade do fornecedor e a relação E026, que liga a montagem ao marco. Essas fontes sustentam a propagação pelas dependências, mas não uma alteração explícita da restrição própria do marco.

A montagem termina em D30. Assim, a restrição proposta deD25 fica dominada pelo predecessor e não muda o cronograma. Uma auditoria posterior por código, **sem nova chamada de IA**, comparou os cronogramas com e sem essa proposta: todos os tempos permaneceram iguais; o marco ficou emD30 nos dois casos. [Evidência da auditoria](auditoria_semantica_ia_real.json).

Essa é a principal oportunidade científica observada: avaliar propostas e suporte das evidências, além dos números finais. O validador estrutural não certifica que a fonte autoriza semanticamente aquela alteração. A recomendação é exigir evidência específica de mudança do atributo local e deixar a propagação temporal com o motor. Não corrigimos essa resposta retrospectivamente nem repetimos a coleta para obter um resultado mais favorável.

### 3. Contextos e encaminhamentos redundantes

Montagem e validação usaram cerca de20,6mil tokens de entrada cada. Alguns nós finais encaminharam novamente a alteração ao fornecedor, que já havia sido interpretado. Isso sugere testar uma representação mais compacta das fontes/responsabilidades e a distinção explícita entre fato já incorporado, efeito propagado e nova alteração local. Qualquer redução precisa preservar cobertura e qualidade, sem cortar informações apenas para caber em um limite.

### 4. Contabilização e apresentação

O campo legado `chamadas_api` conta registros de tentativa/reserva. Na primeira rodada, seu valor4 não significa quatro inferências: foram três inferências e uma contagem que barrou o envio. Este relatório separa esses números. A interface3D continua explicitamente em simulação; o piloto real é executado pelo backend/CLI e seus resultados estão nos arquivos vinculados abaixo.

A revisão também identificou duas melhorias operacionais já aplicadas **depois da coleta**: reservar o custo da próxima chamada contra o teto específico da rodada, além do teto agregado; recuperar o checkpoint persistido se o executor lançar exceção. Essas alterações não modificaram os resultados coletados nem geraram nova inferência. O manifesto da rodada preserva os hashes do código realmente usado.

## Consumo e duração

| Medida | Tentativa1 interrompida | Rodada2 concluída | Total do esforço |
|---|---:|---:|---:|
| Consultas de contagem de entrada | 4 | 14 | 18 |
| Inferências com resposta | 3 | 14 | 17 |
| Tokens de entrada das inferências | 13.507 | 159.125 | 172.632 |
| Tokens de saída das inferências | 2.279 | 11.418 | 13.697 |
| Custo estimado pelo uso retornado, USD | 0,00249020 | 0,02093561 | **0,02342581** |
| Tempo do fluxo, segundos | 35,983 | 168,378 | 204,361 |

A rodada concluída usou uma inferência para sugestão e13 para análises locais. Houve28 requisições HTTP nela:14 contagens e14 inferências. Uma consulta prévia de acesso ao modelo ficou fora desses totais. O tempo total da tabela soma execuções, não inclui implementação, testes e intervalo entre rodadas.

Mantém-se uma reserva conservadora de **US$0,01** da tentativa1, embora o registro indique que a montagem não foi enviada à inferência. Ela não é apresentada como gasto comprovado. Assim, o novo comprometimento é US$0,03342581; somado ao histórico de US$4,567653865, resulta em **US$4,601079675 comprometidos** sob o teto acumulado de US$5. Nenhum saldo histórico foi reiniciado.

Preços: US$0,10/1M entrada, US$0,01/1M entrada em cache e US$0,50/1M saída, conforme a [documentação oficial consultada](https://developers.openai.com/api/docs/models/gpt-6-luna). A conta respeita os tokens de cache informados. É uma estimativa com uso do provedor, não conciliação de fatura. Não inferir economia real contra32 nós: essa comparação completa com IA real ainda não foi executada.

## Verificação e próximos passos

**45 testes locais passaram** após os ajustes, incluindo35 regressões anteriores, cinco testes da integração de sessões reais com transporte controlado e cinco testes de transporte/orçamento. Testes simulados de falhas não substituem avaliação de falhas reais de rede, retomada ou cancelamento.

Prioridades propostas:

1. Revisar com o orientador a proposta de M_PROTO_READY e definir gabarito por alteração local, incluindo alterações indevidas que não mudam os totais.
2. Fortalecer a relação entre evidência e atributo alterado; testar casos negativos e documentos já atualizados.
3. Comparar os modos de seleção com o mesmo modelo e fatos, medindo tokens, latência, cobertura e qualidade conjuntamente.
4. Expandir aos demais eventos de desenvolvimento e, após congelar protocolo, realizar coleta reservada e repetições. A referência atual é autoral, sem revisão humana independente.
5. Melhorar compactação de contextos, métricas por requisição e visualização das sessões reais, mantendo o modo de simulação separado.

O piloto demonstra que o fluxo integrado consegue funcionar com IA real neste caso. Não demonstra generalização, superioridade sobre outras arquiteturas nem ausência de propostas sem sustentação.

## Arquivos para conferência

- [Resultado completo da rodada concluída](../outputs/ia_real_20261110T050151Z/resultado.json)
- [Sugestão original da IA](../outputs/ia_real_20261110T050151Z/sugestao.json)
- [Sessão e histórico de seleção](../outputs/ia_real_20261110T050151Z/sessao.json)
- [Comparação com a referência](../outputs/ia_real_20261110T050151Z/comparacao.json)
- [Consumo da rodada concluída](../outputs/ia_real_20261110T050151Z/consumo.json)
- [Manifesto e configuração da coleta](../outputs/ia_real_20261110T050151Z/manifesto.json)
- [Primeira tentativa preservada](../outputs/ia_real_20261110T050016Z/RELATORIO.md)
- [Instruções e limites de execução](PILOTO_IA_REAL.md)
