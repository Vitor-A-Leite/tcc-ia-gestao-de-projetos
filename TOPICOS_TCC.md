# Tópicos para investigar e implementar no TCC

Criado em 10/11/2026. Lista viva de pendências técnicas e metodológicas, baseada nas decisões discutidas com o usuário. Implementações parciais e verificações offline são registradas explicitamente; não equivalem à conclusão da avaliação científica com IA real.

**Atualização de contexto:** a etapa `TCC_Codigos/etapas/alfa_documental_v1` já demonstra offline 32 pontos executáveis e comparação de campos preparados do Status Report. As descrições abaixo sobre oito nós e ausência de integração documental referem-se à versão histórica; a nova etapa ainda usa interpretações simuladas e não encerra a avaliação com IA real. Ver [relatório Alfa](TCC_Codigos/etapas/alfa_documental_v1/RELATORIO.md).

Prioridades: **essencial** para o escopo integrado de custo, prazo e documentos; **investigação** para avaliar uma alternativa; **extensão** para evolução futura do produto. Esta lista não significa que todas as extensões precisam entrar no TCC.

## 1. Consultar a IA em todos os nós ou apenas nos potencialmente afetados?

- [ ] **Investigação — definir seleção de nós e comparar com a política atual.**
- [x] **Primeiro incremento offline, 10/11/2026:** [Alfa documental v2](TCC_Codigos/etapas/alfa_documental_v2/README.md) implementa seleção manual, sugestão simulada confirmável, alcance conservador, limite livre, pausa, retomada e cancelamento. Nos nove casos dev, 115 interpretações simuladas contra 288 na v1 preservaram os resultados comparados. Ainda falta avaliar seleção e interpretação com IA real e medir custo/latência de API.
- **Plano escrito:** [análise seletiva por pontos de entrada](PLANO_ANALISE_SELETIVA_TCC.md), com critérios e escopo; [verificação independente](TCC_Codigos/etapas/alfa_documental_v2/docs/REVISAO_ORQUESTRADOR.md). As descrições históricas abaixo contextualizam a motivação.
- **Situação atual:** `hibrido_v07_r3/politica.py` seleciona todos os nós, com limite de oito. Cada contexto recebe o relato do evento e informações locais. Em Sálvia foram seis chamadas por evento.
- **Pergunta:** é possível reduzir chamadas, custo e tempo sem perder alterações relevantes, cláusulas financeiras ou lacunas?
- **Proposta:** partir das entidades mencionadas e percorrer dependências pertinentes. Incluir regras financeiras e referências indiretas que não sejam capturadas apenas por sucessores temporais. Definir o que fazer quando o vínculo do evento é ambíguo ou incompleto.
- **Comparação:** mesma base, eventos, fontes, modelo e contrato de resposta; variar a política de seleção. O motor pode continuar calculando toda a rede mesmo quando menos nós consultam a IA.
- **Verificação:** medir cobertura dos efeitos necessários, erros, alterações indevidas, chamadas, consumo e latência. Incluir mudanças locais, múltiplas entidades, efeitos indiretos e ausência de impacto.
- **Cuidado:** não presumir que todos os sucessores mudam, nem que a seleção é superior antes de experimentar. Usar novos casos para avaliação final; os casos já expostos podem servir ao desenvolvimento.

## 2. Recomendar quais documentos e trechos devem ser revisados

- [ ] **Essencial — implementar a camada documental integrada ao cálculo.**
- **Situação atual:** regras legadas indicam categorias de documentos, mas não comparam seu conteúdo com os impactos calculados. Os artefatos antigos pertencem ao Projeto Alfa; os experimentos finais usam Sálvia.
- **Implementação:** preparar documentos coerentes com Sálvia, com identificadores de item/seção/campo, versões, conteúdo e vínculos a entidades. Começar pelo relatório de situação e ampliar para registros de ações, decisões e riscos.
- **Saída:** documento, versão, localização, conteúdo atual, ação (`manter`, `revisar`, `acrescentar`, `solicitar informação`), proposta, motivo, evidências e pendências.
- **Verificação:** identificar revisões necessárias e preservar itens já corretos; distinguir previsão atual de referência aprovada; não inventar decisões, responsáveis, datas ou valores.
- **Referência:** [proposta de integração](Planejamento/Integracao_documental_prazo_custo_20261109.md).

## 3. Mudança sem dados suficientes para calcular o impacto

- [ ] **Essencial — especificar e testar o tratamento de mudanças não quantificadas.**
- **Exemplo:** a ata diz “vamos trocar a tinta”, sem identificar o novo material, preço, disponibilidade ou duração.
- **Situação atual:** há suporte a indeterminação e pendências, mas esse evento genérico não foi validado. Ausência de proposta ou pendência pode conservar os valores anteriores; isso não demonstra ausência de impacto.
- **Implementação:** diferenciar informação desconhecida, ausência de efeito sustentada e pendência de interpretação. Preservar a referência histórica sem apresentá-la como nova previsão confirmada.
- **Verificação:** procurar dados nas fontes disponíveis antes de declarar falta; impedir que falta de informação vire zero; localizar quais parâmetros precisam ser esclarecidos. Uma pendência exclusivamente financeira não deve bloquear um prazo que seja calculável.

## 4. Avaliar a recomendação documental com comparação justa

- [ ] **Essencial — definir protocolo, casos e rubrica antes da nova coleta.**
- **Nível documental:** fornecer os mesmos impactos validados, eventos e documentos às abordagens, isolando a qualidade da recomendação.
- **Nível completo:** avaliar interpretação, cálculo e recomendação em sequência, registrando separadamente a origem dos erros.
- **Comparadores principais:** IA global com relações em texto e sistema híbrido com os mesmos fatos relacionais. A condição sem ficha relacional pode ser controle adicional, explicitamente com menos informação.
- **Casos:** documentos desatualizados/já atualizados, efeitos indiretos, crédito sem atraso, taxa ausente, versões conflitantes e informação nova sem representação anterior.
- **Métricas:** precisão/recall/F1 por documento e item, alterações desnecessárias, correção numérica e textual, sustentação das fontes, abstenção adequada, validade da resposta, custo e latência.
- **Verificação:** gabaritos e critérios revisados antes das respostas, idealmente pelo orientador; mesmo contrato de saída e tratamento de falhas; desenvolvimento separado da avaliação final. Dimensionar quantidade e repetições conforme prazo e orçamento.

## 5. Transformar atas em eventos estruturados

- [ ] **Extensão — desenvolver ingestão documental e identificação das entidades.**
- **Situação atual:** o híbrido recebe estado e evento previamente estruturados; não converte automaticamente uma ata arbitrária nesse evento.
- **Implementação:** extrair o trecho, identificar projeto/versão, resolver as entidades mencionadas e gerar o JSON com fontes e lacunas. Identificar atividades inexistentes ou ambíguas sem criar vínculos silenciosamente.
- **Verificação:** distinguir decisão aprovada, sugestão e hipótese; manter localização na fonte; testar extrações incorretas e referências ambíguas. Definir se entra no escopo do TCC ou permanece evolução futura.

## 6. Reutilizar o motor em outro projeto e ampliar seu domínio

- [ ] **Investigação — documentar o contrato de dados e validar um segundo projeto.**
- **Situação atual:** dependências são cadastradas previamente; o motor não descobre o grafo a partir de documentos. A configuração atual trabalha com até oito nós, dias corridos inteiros, BRL/centavos, precedências fim–início sem defasagem, rede executável acíclica, marco final e eventos prospectivos em D0.
- **Preparação:** cadastrar atividades, dependências, fontes versionadas, durações, restrições, parcelas, regras financeiras e referência inicial consistente.
- **Possível extensão:** modelar “substituição de material” como evento e traduzi-lo em mudanças suportadas de duração e parcelas. Cálculo por quantidade, preço unitário e produtividade exige representação e regras adequadas; cadastrar apenas o nome do evento não basta.
- **Verificação:** separar reutilização do motor de mudanças na implementação; não alegar aplicação a qualquer projeto com base nos testes atuais. Novas entidades/arestas, calendários, recursos compartilhados e projetos em execução exigem avaliação própria.

## 7. Encadear mudanças e persistir versões do projeto

- [ ] **Extensão — converter resultados aprovados em novo estado consistente.**
- **Situação atual:** cada caso parte da mesma referência; a saída contém impactos e rastros, não uma versão completa persistida e validada para o evento seguinte.
- **Implementação:** produzir estado proposto, permitir revisão/aprovação e salvar nova versão com histórico. Definir se e quando muda a referência aprovada, sem confundi-la com a previsão atual.
- **Verificação:** processar eventos sequenciais, evitar aplicação duplicada, identificar versões obsoletas e preservar as evidências de cada alteração.

## 8. Conectar o motor a um portal ou SaaS

- [ ] **Extensão — carregar estado e documentos pelo identificador do projeto.**
- **Fluxo proposto:** receber evento → carregar versão correta → analisar → apresentar impactos e recomendações → aprovar → persistir atualização.
- **Situação atual:** entradas e resultados experimentais são arquivos locais; não há integração validada do motor com SharePoint ou leitura automática de preços externos.
- **Verificação:** associação correta entre projeto, documentos e versões; tratamento de fontes conflitantes; distinção entre análise, aprovação e aplicação. A integração externa não é pré-requisito para avaliar o motor no TCC.

## 9. Consolidar a contribuição em relação à literatura

- [ ] **Essencial — concluir a comparação com os trabalhos mais próximos.**
- **Leituras prioritárias:** Filius, BIM-Change/Moayeri, Cassandro e PTMR-ECM, buscando texto integral onde a consulta ficou limitada ao resumo.
- **Objetivo:** delimitar o que a avaliação integrada acrescenta, sem apresentar integração genérica de IA, grafos, prazo, custo e documentos como novidade comprovada.
- **Verificação:** matriz de funcionalidades, tarefas avaliadas, dados, limitações e acesso às fontes. Comparações numéricas entre estudos só são diretas quando tarefas e protocolos forem compatíveis.
- **Referência:** [mapeamento bibliográfico](Planejamento/Mapa_literatura_integrada_TCC_20261109.md).

## Ordem de trabalho sugerida

1. Confirmar com o orientador documentos, contribuição e critérios de avaliação.
2. Preparar documentos e implementar recomendação localizada com tratamento de informação ausente — itens 2 e 3.
3. Definir e executar piloto do protocolo integrado — item 4; amadurecer a revisão bibliográfica em paralelo — item 9.
4. Avaliar a seleção de nós — item 1 — se couber no prazo, mantendo a comparação isolada da mudança documental.
5. Tratar ingestão, generalização e SaaS — itens 5 a 8 — conforme prioridade acordada, sem transformá-los automaticamente em exigência para concluir o TCC.

Ao avançar em um tópico, registrar aqui a data, os arquivos alterados, a evidência de verificação e as limitações restantes. Não marcar como concluído apenas por haver uma proposta escrita.
