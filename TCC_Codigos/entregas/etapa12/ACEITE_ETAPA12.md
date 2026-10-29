# Verificação técnica da etapa 12

Entrega de 28/10/2026. Critério da meta: produzir um entregável para cada um dos três tópicos autorizados, usando somente os resultados salvos e preservando o teto acumulado de US$ 5.

| Tópico | Entregável | Evidência de conclusão |
|---|---|---|
| Demonstração reproduzível | demonstracao/index.html | Três casos, nove respostas, 18 análises H, fontes, precedências, cronograma, parcelas, falhas e avaliação disponíveis na projeção local |
| Material para o TCC | material_tcc/Material_para_redacao_TCC.docx | Oito páginas editáveis e texto equivalente em Markdown, com arquitetura, metodologia, resultados, falhas, limitações e mapa R1–R10 |
| Revisão do orientador | Pacote_orientador.zip | Roteiro de cinco páginas, formulário humano em branco, 33 cópias de evidências, demonstração, material de redação e verificador de integridade |

## Verificações realizadas

- Projeção comparada aos nove registros originais por identidade, conteúdo e hash; métricas, falhas, auditorias e orçamento comparados integralmente às fontes.
- Reconstrução offline determinística, com bloqueio explícito de sockets; nenhuma chamada de inferência. Indeterminação monetária mantida com valor nulo, limite inferior zero e superior desconhecido. As duas falhas B/T permanecem erros.
- Testes de interação em Node com um duplo mínimo do DOM: 12 combinações caso/área, 18 passos H, 27 consultas a fontes, três exportações JSON com seis auditorias cada, abertura/fechamento da fonte e acionamento da impressão. Esse teste executa as funções de apresentação; não renderiza CSS.
- HTTP em loopback: 11 requisições conferiram conteúdo, cabeçalhos sem corpo, bloqueio de acesso fora da pasta, bloqueio de arquivos Python e ausência de endpoint POST. Servidor de teste encerrado automaticamente.
- Dois DOCX renderizados pelo LibreOffice empacotado. Todas as 13 páginas finais foram inspecionadas como imagens, sem cortes, sobreposições ou caracteres ausentes. O material do TCC teve tabelas e paginação ajustadas; o parecer humano permanece sem preenchimento.
- Manifesto SHA-256 por lista positiva; pacote extraído em diretório temporário e conferido com o verificador portátil. Uma alteração deliberada em cópia temporária foi detectada. Imagens de QA, credenciais, bancos financeiros e arquivos pessoais não fazem parte do ZIP.

Os resultados verificáveis estão em verificacao_entrega.json e MANIFESTO_ENTREGA.json. Os scripts de autoria e testes permanecem no repositório original em entregas/etapa12; não alteram o código científico congelado.

## Limitação da conferência de navegador

O host de automação de abas retornou “The browser access host is unavailable”. Pela interface nativa, o Chrome navegou para a URL e exibiu o título do observatório, mas a captura ficou branca e não expôs o conteúdo da página. Isso não permitiu confirmar visualmente navegação, layout responsivo, impressão ou download em navegador real. Não se declara esse teste como aprovado. O comportamento foi exercitado nos testes locais acima; a apresentação usa HTML/CSS/JavaScript locais, sem dependências remotas.

## Preservação e limites do aceite

O banco da carteira manteve exatamente os mesmos bytes. O compromisso acumulado permanece US$ 4,567653865 e o saldo US$ 0,432346135. A etapa 12 adicionou zero chamadas pagas. Provisões e reservas históricas permanecem no compromisso; não se trata de atestado de faturamento.

O congelamento da etapa 10 e os artefatos científicos da etapa 11 foram reconferidos. STATUS.md e PLANO_MESTRE.md são registros vivos e receberam apenas uma nova entrada; seu conteúdo histórico foi preservado. Essa exceção está explícita no verificador de origem.

O aceite corresponde à entrega técnica dos três materiais. A avaliação científica humana continua pendente. N=3, uma repetição e diferenças simultâneas entre B/H/T impedem afirmar superioridade estatística ou efeito exclusivo do grafo. Qualquer ampliação experimental requer protocolo e casos novos.
