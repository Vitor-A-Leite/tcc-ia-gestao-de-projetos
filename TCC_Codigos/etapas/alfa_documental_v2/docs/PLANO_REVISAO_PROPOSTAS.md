# Plano de análise de propostas por código e por IA

Data: 10/11/2026. Escopo: Alfa documental v2. A implementação foi delegada a um subagente GPT-6 Astra com esforço xhigh, conforme solicitação do usuário. Esse modelo é o implementador; não define automaticamente o modelo do revisor em produção.

## Objetivo

Tornar auditável a distinção entre uma proposta estruturalmente válida, uma mudança ainda necessária e uma alteração semanticamente sustentada. Evitar tratar concordância de modelos, citação existente ou resultado numérico correto como certificação semântica.

A primeira entrega opera em **observação opt-in**. As verificações adicionais produzem diagnósticos e pareceres, mas não modificam propostas, aceitação operacional, solver, completude ou documentos oficiais. O comportamento padrão e a coleta histórica permanecem preservados. Bloqueio automático e aprovação humana são etapas futuras, sujeitas a avaliação; não há aprovação humana simulada.

## Fluxo e responsabilidades

1. O agente proponente interpreta o nó.
2. O validador existente confere contrato, permissões e referências.
3. A nova análise por código verifica estado vigente, identidade, duplicidade e conflito.
4. Quando configurado, o revisor IA recebe um pacote próprio e emite um parecer estruturado.
5. O sistema registra ambos os resultados, com identidades e versões.
6. A política operacional original decide a incorporação e o motor calcula consequências. Na fase de observação, o parecer não autoriza nem veta alterações.
7. A comparação documental continua após o cálculo, sobre as afirmações cadastradas; documentos já compatíveis não recebem recomendação redundante.

O significado da fonte é analisado pelo revisor, não deduzido de mera coincidência de palavras. Regras determinísticas verificam correspondências formais. Um atributo de saída como `interpretacao_validada=true` produzido pelo modelo não é aceito como aprovação.

## Entregas e critérios de aceite

| Entrega | Conteúdo | Evidência de conclusão |
|---|---|---|
| Análise determinística | Reuso dos contratos; valor vigente conhecido/desconhecido; comparação por alvo, atributo e unidade; repetição do mesmo fato; conflitos pertinentes; diagnóstico por proposta | Testes positivos e negativos; desconhecido não vira zero; alterações sem efeito global não são descartadas por isso |
| Pacote semântico | Proposta original, definição do atributo, estado vigente, trechos/versões das fontes, regras, dependências e operações incorporadas | Origem em contexto e fontes reais; hash/versão; ausência de gabaritos e totais finais como justificativa |
| Revisor IA | Transporte injetável; instruções de separação entre alteração local e propagação; esquema e parser próprios | Pareceres sustentada, contradita, suporte insuficiente e ambígua; vínculo com proposta/pacote; evidências inventadas ou respostas incoerentes recusadas |
| Integração observacional | Ativação explícita; persistência; identificação de configuração; tratamento de falhas | Resultados quantitativos e política original preservados; erros de revisão não convertidos em aprovação; nenhuma chamada oculta |
| Consumo e auditoria | Pedido/resposta bruta, modelo/configuração, latência e uso informado; orçamento explícito para uso real | Transporte falso testa reservas/limites; falta de uso não é convertida em zero; repetição/reuso identificado |
| Uso e documentação | API e/ou comando offline com artefato separado da coleta | Exemplo reproduzível sem credencial; documentação dos limites e dos modos |

## Conteúdo esperado do parecer

- Identidade da proposta, do contexto e do pacote revisado.
- Parecer semântico e tipo de efeito: alteração local, regra aplicável, propagação ou indeterminado.
- Avaliação separada de entidade, atributo e valor/unidade.
- Referências efetivamente examinadas, justificativa curta e suporte ausente quando aplicável.
- Metadados de execução e falhas separados da conclusão semântica.

Um parecer favorável não substitui auditoria humana nem transforma suporte semântico em certificado. `suporte_insuficiente` não significa necessariamente que a proposta seja falsa: pode faltar informação. Recusa, timeout, resposta truncada ou parser inválido são falhas da revisão, nunca parecer favorável.

## Plano de testes

1. Disponibilidade do fornecedor explicitamente alterada para D25.
2. Proposta para outra entidade ou outro atributo usando a mesma fonte.
3. Fonte inexistente, localizador inválido ou contexto adulterado.
4. Valor já vigente e mesma operação já incorporada para o mesmo fato.
5. Informação conflitante ou novo fato, sem supressão automática por haver uma operação anterior.
6. Valor desconhecido, unidade incompatível e operações financeiras.
7. Alteração local válida sem efeito global: necessidade local não depende do delta final.
8. Marco M_PROTO_READY: transporte falso devolve parecer desfavorável à restrição própria D25, sem alegar que isso prova desempenho de IA real.
9. Parecer favorável incoerente, evidência inventada, falha de transporte e saída malformada.
10. Observação desativada versus ativada: mesmo resultado operacional; parecer e consumo separados.
11. Documento já atualizado: manter a classificação existente sem recomendação redundante.
12. Regressões de seleção, pausa/retomada, orçamento e compactação.

A suíte anterior tinha 49 testes locais. Novos testes usam transportes controlados, sem executar inferência paga. Gabaritos de avaliação não entram no pedido do revisor.

## Avaliação científica posterior

Congelar protocolo, dados, modelos, configurações e critérios de avaliação. Comparar proponente sozinho e proponente com revisão, preservando respostas originais. Preparar referências humanas para mudanças locais e casos de abstenção; separar desenvolvimento e avaliação reservada.

Medir aceitação indevida, contestação indevida, ambiguidade/abstenção, validade das referências, detecção de propostas sem suporte mesmo sem efeito nos totais, custo/latência/uso e mudanças nos resultados finais. A comparação de caracteres de prompt não mede economia real de tokens nem qualidade semântica.

Somente após essa avaliação decidir se uma classe delimitada de pareceres pode participar de uma política de bloqueio. Casos pendentes relevantes ao cálculo deverão preservar a indicação de previsão parcial/condicional, em vez de serem silenciosamente descartados.

## Estado da execução

Implementação concluída e revisada em modo de observação:

- `src/revisao.py`: análise determinística, pacote de fontes, esquema/parser do parecer, revisor injetável e observador offline.
- `src/auditoria.py`: auditoria de resultados existentes com destino novo obrigatório e integração real programática com orçamento persistente próprio, reutilizando as reservas do transporte existente.
- `src/orquestracao.py` e `src/pipeline.py`: gancho opcional após validação estrutural e antes da incorporação; o modo observação não modifica os contextos do proponente nem usa seus pareceres para decidir o aceite.
- `__main__.py`: comando `auditar` exclusivamente offline; `testar` passou a descobrir a suíte completa.
- `tests/test_revisao.py`: 22 novos testes de contrato, integração, falhas e orçamento, além das 49 regressões anteriores.

Verificação independente: **71 testes passaram**, usando `python3 -B -m unittest discover -s TCC_Codigos/etapas/alfa_documental_v2/tests -t . -q`. Também foi exercitada a descoberta completa pelo comando `testar` e a auditoria CLI do piloto D02. A auditoria determinística reconheceu três propostas: fornecedor candidato, confirmação de montagem com valor já vigente e marco candidato que ainda exige interpretação semântica. O parecer desfavorável ao marco foi exercitado apenas por transporte prescrito em teste; não é evidência de desempenho de IA real.

Foram conferidos os hashes de **50 arquivos** das duas rodadas originais e das referências avaliativas: nenhum foi alterado. Nenhuma nova chamada paga de inferência ou contagem foi executada.

### Limites desta entrega

- A integração ao fluxo de cálculo admite observador determinístico e revisor simulado. Revisão real fica em auditoria separada de arquivo via API, com destino exclusivo e teto explícito; não foi adicionada à UI nem ao orçamento das sessões de interpretação.
- O revisor não usa cache. Cada nova auditoria executa novas revisões, com identidade e consumo registrados; destino existente é recusado antes de gastar. Isso evita reuso sem vínculo e cobrança oculta.
- Registros legados sem origem causal explícita não permitem certificar duplicidade de um mesmo fato. Nesses casos há comparação de valores e diagnóstico conservador, sem fabricar proveniência.
- O modo real reutiliza o modelo/configuração já suportados por `TransporteReal`. GPT-6 Astra xhigh foi usado para implementar, não foi implicitamente escolhido como revisor de produção.
- Suporte semântico continua não certificado. Não há veto automático por parecer, aprovação humana fictícia ou alteração de documento oficial. A coleta real comparativa continua pendente.
