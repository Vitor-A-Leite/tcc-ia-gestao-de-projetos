# Protocolo prospectivo — etapa 10, versão 2

Data: 28/10/2026. Preparação e auditoria offline autorizadas. **Coleta da etapa 11 não iniciada.** O manifesto de congelamento registra os hashes efetivos dos artefatos desta versão.

## Pergunta e unidade

Comparar as variações do término e do custo total estimadas por B, H e T em três eventos fictícios inéditos de um novo projeto, cada evento isolado e prospectivo no D0. Dias corridos inteiros; BRL em centavos; deltas positivos significam atraso/aumento. Não confundir custo do projeto com custo da API.

São **3 casos × 3 condições × 1 repetição = 9 slots**, N=3 por condição. A unidade de evidência é o caso, não o número de chamadas locais. A seleção intencional abrange alteração temporal calculável, ajuste de custo calculável e magnitude monetária realmente desconhecida. O conjunto é um teste prospectivo exploratório, sem representatividade estatística, poder calculado ou estimativa confiável da variabilidade entre execuções. Não permite alegar generalização para projetos reais nem superioridade estatística.

Dados vigentes: `data/final/etapa10_v2`. A versão 1 e sua revisão cega estão preservadas. A revisão 2 explicita em uma fonte comum, fornecida a B/H/T, que a rede é acíclica, só possui precedências fim-início de defasagem zero, todas as entregas convergem no marco e o cálculo usa início mais cedo, sem ociosidade deliberada. Essas convenções não revelam arestas específicas. Portanto o desfecho temporal é o menor término factível no modelo. O campo `lacunas` registra lacunas expressas do evento; uma lista vazia não certifica ausência global de lacunas, e a evidência literal continua prevalecendo. O aviso com taxa desconhecida contém essa lacuna também no campo estruturado.

Os 15 casos usados no piloto, os cenários legados e todas as suas repetições ficam exclusivamente em desenvolvimento. Dados finais são novos e não serão enviados ao modelo durante a etapa 10. Autores e revisores técnicos podem ler as fontes para preparar gabaritos; essa exposição será registrada e não é confundida com teste externo independente.

## Condições e congelamento

- B: contexto comum e evento, sem relações exclusivas; uma resposta global.
- H: versão 7.2 (`hibrido_v07_r3`), contexto local, relações, coordenação e motor determinístico; até oito chamadas.
- T: mesmos fatos relacionais de H, serializados em texto neutro, além do comum; uma resposta global.

Manter modelo solicitado `gpt-6-luna`, reasoning high, Standard/default, stream, cache TTL 30m, máximo oficial de 16.000 tokens de entrada e 25.000 de saída, 180 s por chamada e 1.500 s por slot H. Sem retries, reparo de resposta ou fallback. Preservar modelo observado e usage por chamada. Congelar todo `src/**/*.py`, prompts derivados, configuração, inputs, views, referências, scripts desta auditoria e ordem antes da coleta. Não ajustar H ou B/T olhando respostas finais.

Ordenar casos por ID opaco e distribuir posições como **B/H/T**, **H/T/B**, **T/B/H**, respectivamente. Uma repetição impede medir estabilidade; a ordem balanceada não elimina cache ou efeitos temporais. Gabaritos ficam em diretório separado, nunca são carregados por preditores nem entram nos prompts. O carregador final é isolado e só recebe os quatro arquivos de inputs; o carregador histórico de 15 casos permanece intacto.

As assimetrias são deliberadas e limitam inferência: B dispõe de menos relações; H dispõe de decomposição, múltiplas chamadas, cálculo externo e schema estrito; B/T mantêm o contrato global existente. Logo, a comparação é entre sistemas completos. Nenhuma diferença será atribuída exclusivamente ao grafo. Uma ablação de mecanismos exigiria outro protocolo e orçamento.

## Referências e avaliação

Derivar referências a partir das fontes, sem previsões e sem importar o motor. Selar a derivação cega antes de confrontar referências autorais. Avaliar dois eixos: verdade no projeto completo e suporte no contexto efetivamente visível. Referências por view não são automaticamente iguais à verdade completa. H com informação suficiente na união das fontes ainda pode perder fatos no contexto local; o rastro efetivo precisa ser auditado.

Para cada dimensão, relatar estados exato/direção/indeterminado/inválido, n/N e valores individuais. **Cobertura exata não é acurácia.** MAE e erros individuais apenas quando previsão válida e referência são ambas exatas, sempre com o denominador elegível e unidade. Relatar também acerto exato sobre referências exatas, erros de direção, falsa precisão, zeros sustentados e indeterminação apropriada. Compatibilidade com um limite não demonstra igualdade. Uma magnitude desconhecida não entra no MAE; ausência de evidência não vira zero. Se a auditoria de suporte não puder decidir, marcar pendente, sem contar como aprovado.

O avaliador histórico só serializa limites estruturados em estados exato/direção. Limites de referências indeterminadas são preservados em campo suplementar próprio e conferidos separadamente; não se converterá um intervalo que inclui zero em direção de aumento para satisfazer esse schema. O relatório final deve expor esses limites e verificar contradições sem confundir valor compatível com valor identificado.

Falhas, recusas, truncamentos e slots não iniciados permanecem no N planejado. Não selecionar a melhor resposta, excluir casos difíceis nem substituir falha por outra execução. Se houver interrupção, publicar coorte incompleta e razão; não fazer comparação como se todos os slots tivessem ocorrido. Preservar brutos, normalização, manifestos, hashes, rastros, relógios e reservas. Resultados por condição e pares de casos serão descritivos, sem testes de significância nesta amostra.

## Orçamento e execução futura

Carteira canônica: `outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite`; nunca reiniciar. Compromisso antes da etapa 10: **US$ 4,480425665**, saldo **US$ 0,519574335**. Etapa 10 usa zero chamadas pagas.

Com a reserva conservadora vigente de **US$ 0,0165 por tentativa**, cada caso B/H/T admite até 10 tentativas; os três casos admitem **30**, reservando no máximo **US$ 0,495**. Compromisso máximo projetado **US$ 4,975425665**, folga **US$ 0,024574335**. A reserva inclui inferência máxima de US$ 0,0145 e provisão hipotética de contagem de US$ 0,002; provisão não é tarifa confirmada. Manter as 13 reservas desconhecidas históricas.

Antes de uma coleta autorizada na etapa 11, reconferir carteira, preços/limites do provedor, hashes, consentimento de escopo e compatibilidade do transporte com o manifesto final. Se preço/configuração mudar, não usar silenciosamente a reserva antiga: recalcular e versionar antes de enviar. Reserva atômica antes de cada tentativa; bloqueio se compromisso + reserva superar US$ 5; timeout/usage desconhecido mantém reserva. Erro de transporte/protocolo interrompe o lote conforme política vigente; não reciclar reservas desconhecidas para liberar gasto. O teto acumulado prevalece sobre completar a amostra.

## Parecer e mudança

A auditoria por agentes separados é técnica e assistida por IA. Uma ficha de parecer humano acompanha a entrega, sem assinatura preenchida. O orientador/especialista pode revisar fontes e referências sem acesso às previsões finais, pois elas ainda não existem. Ajuste científico antes da coleta gera versão nova de dados/referências/protocolo e outro congelamento; ajuste depois de olhar resultados transforma esses casos em desenvolvimento e exige novos casos finais.
