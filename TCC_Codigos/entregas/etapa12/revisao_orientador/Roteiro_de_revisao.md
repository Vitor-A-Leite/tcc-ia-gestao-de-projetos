# Revisão do experimento de prazo e custo

Pacote para o orientador • Etapa 12 • 28 de outubro de 2026

## Decisão solicitada ao revisor

Este pacote reúne o protocolo, as fontes, os resultados e as limitações de um experimento exploratório que compara baseline global (B), arquitetura híbrida (H) e relações textuais (T). Solicita-se avaliar se o método e as conclusões estão adequadamente delimitados para o TCC, registrar discordâncias e indicar ajustes na redação ou necessidades de investigação adicional. Não há aprovação humana preenchida ou presumida.

O experimento final completou nove execuções sobre três casos sintéticos, com uma repetição por condição. H acertou três prazos e dois custos determináveis, preservando o custo desconhecido no terceiro caso. B e T tiveram uma resposta rejeitada cada por ausência do campo obrigatório justificativa, embora o conteúdo bruto estivesse coerente com as fontes. Essas falhas foram mantidas nas métricas.

O compromisso financeiro acumulado permaneceu em US$ 4,567653865, incluindo provisões e reservas históricas; não é confirmação da fatura. A etapa 12 utiliza os registros salvos, sem novas chamadas pagas. Não se solicita ao revisor configurar credenciais, executar coleta ou autorizar despesas.

## Ordem sugerida de leitura

1. Ler evidencias/protocolo_final.md e os quatro JSONs em evidencias/inputs/. Examinar as fontes textuais do subdiretório fontes. Se desejar derivar resultados antes do confronto, evitar abrir referencias.json, relatório e demonstração até registrar a própria derivação.
2. Registrar o que já foi visto. Os resultados existem desde a etapa 11; qualquer revisão humana feita agora é posterior à coleta. Caso o revisor ainda não tenha visto as previsões, pode realizar derivação antes do confronto, mas a data e a exposição devem ser explicitadas.
3. Abrir evidencias/referencias.json e evidencias/revisao_cega/ para confrontar a derivação técnica anterior à coleta.
4. Abrir demonstracao/index.html. Conferir os três casos, rastros H, parcelas e fontes. Consultar as respostas rejeitadas sem recuperá-las nas métricas.
5. Examinar as tabelas do material para redação do TCC e preencher o parecer deste documento. A assinatura deve ser adicionada pelo próprio revisor.

Os documentos da etapa 10 são históricos e podem mencionar que previsões ainda não existiam naquela data. Essa afirmação não descreve o momento atual. Nenhum documento histórico foi reescrito para simular revisão humana prospectiva.

<!-- page -->

## Questões metodológicas prioritárias

### Escopo e tamanho da amostra

Os três eventos pertencem a um único projeto sintético, com cinco atividades e um marco. A seleção intencional cobre alteração temporal, crédito contratual e taxa monetária desconhecida. Não há estimativa de representatividade, poder estatístico ou estabilidade entre execuções. Avaliar se a expressão “experimento exploratório” e a limitação das conclusões são suficientes para os objetivos do TCC.

Parecer e ajustes solicitados: __________________________________________________

____________________________________________________________________________

### Comparabilidade das condições

B não recebe arestas específicas. H possui decomposição local, múltiplas chamadas, motor determinístico e schema estrito. T recebe as relações em texto, mas mantém resposta global. A comparação é entre sistemas completos e não identifica o efeito exclusivo da representação em grafo. Avaliar se o título, a pergunta de pesquisa e a discussão respeitam essa diferença.

Parecer e ajustes solicitados: __________________________________________________

____________________________________________________________________________

### Validade de saída e capacidade de cálculo

No caso da taxa desconhecida, B/T omitiram justificativa no nível superior e foram rejeitados. T apresentou no bruto o prazo correto e a indeterminação monetária correta. As métricas não recuperaram esses resultados. Avaliar se a discussão distingue adequadamente falha de entrega, erro matemático e falta de informação.

Parecer e ajustes solicitados: __________________________________________________

____________________________________________________________________________

### Independência e exposição

As referências foram revistas por agentes distintos antes das previsões. A auditoria das respostas foi posterior, pelo coordenador. Nenhuma etapa equivale a revisão científica humana externa. Registrar relação do revisor com autoria/implementação e qualquer exposição anterior às fontes, gabaritos ou previsões.

Parecer e ajustes solicitados: __________________________________________________

____________________________________________________________________________

<!-- page -->

## Conferência dos casos e das métricas

### Duas durações substituídas

Conferir trilho de 8 dias e mapa de 10 dias; alinhamento até D14 e configuração até D13; validação até D19. Conferir extensão única de quatro dias a 8.600 centavos/dia, delta R$ 344,00. Em B, verificar se a direção de aumento é demonstrável sem arestas e se a magnitude permanece não identificada. Evidências: inputs/fontes/d_b32ce294f2.txt, d_30c2c87610.txt e d_fcaf0bba4d.txt.

Resultado da conferência: _____________________________________________________

### Taxa substituta desconhecida

Conferir configuração D7–D16 e validação D16–D21. Confirmar a revogação da taxa antiga e que apuração do preço não bloqueia a execução. O delta monetário é 6r centavos, r inteiro não negativo, sem limite superior. Zero é possível, mas não identificado. Avaliar se manter somente o limite inferior zero, sem congruência explícita, é suficiente ao escopo. Evidência: inputs/fontes/d_77935f5c87.txt.

Resultado da conferência: _____________________________________________________

### Crédito definitivo

Conferir manutenção de D15, crédito aplicado uma vez e parcela de alinhamento reduzida de 138.600 para 127.000 centavos. Total R$ 5.088,00; delta −R$ 116,00. Evidência: inputs/fontes/d_51bc5a176a.txt e livro H em etapa11/registros.json.

Resultado da conferência: _____________________________________________________

### Denominadores e falhas

| Item a conferir | Referência de leitura |
|---|---|
| N=3 em cada condição, incluindo falhas | etapa11/manifesto.json |
| Três prazos e dois custos com referência exata | referencias.json |
| Cobertura de custo H 2/3 e acerto 2/2 | etapa11/metricas_auditadas.json |
| MAE condicionado a pares exatos válidos | etapa11/recontagem_metricas.json |
| Duas rejeições sem reparo | etapa11/falhas_formato.json |
| Provisões e 13 reservas históricas preservadas | etapa11/auditoria_uso.json |

Os caminhos desta página estão dentro de evidencias/. Registrar divergências concretas por arquivo, caso, condição e dimensão; evitar apenas um julgamento agregado de “correto” ou “incorreto”.

<!-- page -->

## Formulário de parecer humano

Nome do revisor: _____________________________________________________________

Papel e instituição: ___________________________________________________________

Data da revisão: _____________________________________________________________

Relação com autoria e implementação: ___________________________________________

Exposição anterior às fontes, referências e previsões: ______________________________

____________________________________________________________________________

Derivação própria anexada e data, quando houver: __________________________________

____________________________________________________________________________

### Julgamento

[ ] Adequado ao escopo exploratório delimitado

[ ] Adequado após as revisões especificadas abaixo

[ ] Requer investigação adicional antes da conclusão

[ ] Inadequado ao objetivo declarado

### Fundamentação e alterações exigidas

____________________________________________________________________________

____________________________________________________________________________

____________________________________________________________________________

____________________________________________________________________________

### Divergências entre fontes e referências ou resultados

____________________________________________________________________________

____________________________________________________________________________

Assinatura ou registro verificável do revisor: ______________________________________

Este formulário está sem preenchimento. A existência do pacote não constitui aceite científico, assinatura, autorização de gasto ou aprovação do TCC.

<!-- page -->

## Inventário e reprodução sem API

O arquivo COMECE_AQUI.html é o ponto de entrada do pacote. A demonstração funciona por abertura direta de demonstracao/index.html em navegador com JavaScript habilitado. Seus arquivos HTML, CSS, JavaScript e dados estão incluídos; não há CDN, login, serviço remoto ou chave de API.

O material_tcc contém texto e tabelas em Word e Markdown. A pasta revisao_orientador contém este roteiro em Word e Markdown, com espaço para parecer. A pasta evidencias inclui os inputs, as views, referências, derivação cega técnica e 15 arquivos de resultados/auditoria da etapa 11. O índice de proveniência associa cada cópia ao caminho original e SHA-256.

Para verificar a integridade do pacote extraído, executar na pasta etapa12 com Python 3.9 ou superior:

python3 verificar_pacote.py

Esse comando usa apenas a biblioteca padrão, verifica os hashes do manifesto da entrega e não faz chamadas ao modelo. O comando não reavalia cientificamente os resultados; verifica que os arquivos correspondem à entrega.

Para navegar por HTTP local, se necessário:

python3 servir.py --porta 8782

Abrir http://127.0.0.1:8782 e encerrar com Ctrl+C no terminal. O servidor só escuta em loopback e serve arquivos desta entrega. Nenhuma opção de coleta está presente.

Para reconstruir a projeção da demonstração dentro do repositório original, executar python3 TCC_Codigos/entregas/etapa12/construir.py. Isso lê arquivos congelados da etapa 10/11 e copia evidências permitidas. Não executa novamente o experimento. O pacote distribuído já contém os resultados dessa construção.

## Arquivos preservados e elementos não incluídos

O pacote usa cópias de evidências, preservando os originais. Não inclui credenciais, arquivos .env, os bancos SQLite completos da carteira, informações pessoais de documentos administrativos nem os experimentos legados. As duas respostas brutas rejeitadas relevantes ao diagnóstico estão incluídas em falhas_formato.json. Os registros normalizados H contêm os contextos, análises, propostas e resultados usados na explicação.

O banco financeiro completo e o código científico congelado permanecem disponíveis no repositório de trabalho para auditoria técnica aprofundada. Os hashes e a memória de cálculo incluídos permitem localizar essa evidência sem distribuir o histórico integral. A revisão do orientador pode solicitar acesso adicional ao autor, se necessário.

As verificações locais e de navegador da entrega são documentadas em ACEITE_ETAPA12.md. Elas comprovam funcionamento e integridade no ambiente testado; não substituem a avaliação metodológica solicitada neste formulário.
