# Entrega Alfa documental v1.0.0 — 10/11/2026

Foi implementado um ciclo funcional de análise de impacto e consistência documental em pacote separado. A demonstração usa o grafo Alfa, executa o motor híbrido com interpretações manuais simuladas e produz recomendações para revisão do Status Report. **Não houve execução paga nem avaliação de desempenho da IA nesta etapa.**

## O que está entregue

- 40 entidades originais preservadas: cinco fornecedores, dez componentes, oito atividades, cinco testes, quatro marcos, quatro áreas e quatro pessoas. Nove entidades documentais/versionamentos por cenário usual (49 nós na demonstração; 50 quando STATUS@2 está presente).
- Projeção executável com 32 pontos e 39 precedências. Documentos, pessoas e áreas são contexto; as 65 relações originais continuam no grafo. Não se presume impacto a partir de mera conexão.
- Durações, disponibilidades, restrições de liberação, dez parcelas e dois contratos temporais explícitos. Todos esses parâmetros novos são sintéticos, com autoria fictícia, versão e trecho citável. Datas do Status Report histórico não foram convertidas silenciosamente.
- Cadastro JSON de trechos, três papéis documentais, relações descreve/estabelece condição/registra situação, histórico de versões e separação T_CAD ↔ DOC_CAD.
- Reutilização de parser, schema, adaptador local, reconciliação de encaminhamentos, fechamento por dimensão e solver H7.2/H05. Agenda derivada com catálogo de responsabilidades projetado por nó. Todos os 32 responsáveis são processados; limites insuficientes geram incompletude explícita.
- Cálculo por máximo nas convergências, folga total da baseline, obrigações únicas e laboratório compartilhado. Custos são resultados de contratos/parcelas, não somas de caminhos.
- Status Report comparado em cinco afirmações registradas. Recomendações trazem versão, campo, trecho, texto atual, alteração, justificativa, cálculo e evidências. Aprovação humana é registrada separadamente; **nenhum documento oficial é atualizado pelo sistema**.
- Demonstração com cenários, replay, nova simulação Python, animação do rastro, clique em nós/documentos, fontes, efeitos, parcelas e recomendações. Execução real com IA é explicitamente indicada como não autorizada.

Arquivos e comandos: [README](README.md). Leitura do sistema anterior: [auditoria inicial](AUDITORIA_INICIAL.md). Demonstração: [HTML](web/index.html) ou `http://127.0.0.1:8766` enquanto o servidor local estiver aberto.

## Validação da rodada entregue

As referências autorais foram gravadas e seladas antes da primeira previsão. Há nove casos de desenvolvimento e oito reservados em diretórios separados. O preditor não lê referências; a simulação injeta operações preparadas em arquivo próprio. Resultados completos são persistidos antes da abertura das referências pelo avaliador.

| Dimensão | Resultado offline de desenvolvimento |
|---|---|
| Prazo | 9/9 estados/valores corretos; oito referências numéricas e uma indeterminação |
| Custo | 9/9 estados/valores corretos; sete referências numéricas e duas indeterminações |
| Documental | 45 unidades; TP=14, TN=31, FP=0, FN=0 |
| Precision / recall / F1 documental | 1,00 / 1,00 / 1,00 |
| Rastreabilidade das recomendações | 14/14 com fontes e vínculo ao cálculo |
| Sustentação conferida pelo autor | 14/14, com critérios e contas registrados; auditoria independente pendente |
| Testes novos | 27 aprovados, com sockets bloqueados |
| Preflight de pedidos | 288 contextos; maior payload parcial 84.131 bytes, sem truncamento |

Evidências: [métricas](runs/dev_05/metricas.json), [testes](qa/testes_finais.txt), [conferência manual](QA_MANUAL.md), [preflight](qa/preflight_payloads_final.json). Contagem oficial de tokens não foi executada: ficar abaixo do limite em bytes não garante entrada abaixo de 16.000 tokens.

Os casos cobrem atraso absorvido, atraso crítico, preço sem atraso, ausência de informação temporal/monetária, fornecedor compartilhado, múltiplos caminhos e ensaios paralelos. Documentos incorretos, corretos e relacionados sem necessidade de alteração estão presentes. Precisão documental é medida por afirmação, não por documento selecionado.

**Essas métricas descrevem software e interpretações preparadas, após iterações de desenvolvimento. Não medem capacidade de interpretação de um LLM, não são resultado final reservado e não sustentam superioridade geral.** Os oito casos finais não foram executados; suas referências são autorais, sem revisão externa e sem cegamento em relação ao autor.

## Falhas e resultados parciais preservados

1. `qa/primeira_execucao_D02.json`: integração falhou após 21 análises por permissão de duração duplicada na regra local. A projeção nova foi corrigida; o registro original não foi alterado.
2. `qa/segunda_execucao_D02.json`: cálculo correto, mas somente duas das três recomendações; a primeira leitura documental esperava um campo aninhado, enquanto o motor completo retorna datas no nível principal. O acesso foi corrigido prospectivamente. Essa saída permanece como falha documental de desenvolvimento.
3. `qa/testes_primeira_rodada.txt`: um erro e uma falha nos próprios testes (nome do livro de parcelas e expectativa de suprimir também uma recomendação local já sustentada numa execução global parcial). As expectativas foram corrigidas e o log preservado.
4. `qa/preflight_payloads.json`: contexto máximo de 124.621 bytes excedia a proteção histórica. A nova política passou a selecionar responsabilidades locais, vizinhas e explicitamente mencionadas, mantendo o catálogo global e todos os nós/arestas. A rodada posterior ficou em 84.131 bytes. Não foi cortado texto por limite nem ajustado gabarito.
5. `qa/regressoes_historicas_py312.txt`: 130 testes históricos executados, seis falhas em baseline/notebooks (rótulos/participantes, pilotos dev, snapshot/prompt e ZIP). Esses arquivos não foram alterados nesta etapa. Não se declara a suíte histórica inteiramente aprovada.
6. `qa/regressao_H72.txt`: 15 testes de vínculo/dimensões passaram; o módulo de schema não carregou por ausência de `jsonschema` no ambiente. Não foi mascarado como sucesso. O contrato customizado H7.2 foi exercitado pelos 27 testes novos e pelas 288 análises da rodada entregue.
7. Tentativas com Python 3.9 e abertura de socket sob sandbox foram registradas na sessão; a verificação suportada e o servidor usam o ambiente existente Python 3.12.14. A primeira abertura do navegador embutido falhou; o Safari nativo permitiu a validação visual.

As rodadas `dev_02`, `dev_03`, `dev_04`, `dev_05`, os brutos de QA e os resultados interativos coexistem. Não se repara uma resposta antiga nem se reclassificam as tentativas iniciais para elevar a métrica da rodada entregue. Mudanças de desenvolvimento devem ser consideradas ao interpretar os resultados.

## Preservação e orçamento

[Integridade conferida](integridade_depois.json): **1.914 arquivos anteriores sem alteração** e carteira canônica idêntica em bytes. Inputs novos: 53 arquivos selados. As mudanças preexistentes em Planejamento e a entrega grafo_salvia foram preservadas. Nenhum experimento da Sálvia foi substituído, nenhuma referência congelada foi reescrita e nenhuma credencial foi carregada por esta etapa.

Carteira: 1.138 tentativas históricas, US$4,567653865 comprometidos, US$0,432346135 de saldo sob teto US$5; 13 reservas desconhecidas mantidas. **Zero novas chamadas de API**, inclusive contagem de tokens.

O [protocolo pago](PROTOCOLO_PAGO.md) propõe primeiro duas execuções H de desenvolvimento, até 64 chamadas locais, provisão histórica de US$1,056 e compromisso acumulado máximo de US$5,623653865. Isso excede o teto existente e o escopo autorizado da Sálvia; exige autorização específica. A coleta final de 16 execuções/512 chamadas exige autorização separada. Modelo/preços atuais, contagem oficial e ativação transacional da nova coorte ainda devem ser conferidos antes de qualquer envio.

## Pendências e conclusões admissíveis no TCC

Implementado e avaliado: comparação de **campos preparados do Status Report**. Implementado parcialmente: triagem de Action Log, Risk Register e Decision Log, com preservação e sem criação automática a partir de atraso. Pendentes nesses três artefatos: extração semântica, regras positivas de alteração, geração específica de recomendações e avaliação própria.

Não implementado: importação automática de Word/PDF/OCR, extração geral de afirmações de prosa, escrita em documentos oficiais, calendário útil, recursos compartilhados com capacidade limitada, relações SS/FF/lag não zero, eventos durante execução real do projeto ou memória cumulativa de múltiplas mudanças. O CAD cadastrado é texto preparado de descrição/versionamento, não leitura geométrica de um arquivo CAD.

A política atual consulta todos os 32 pontos quantitativos; portanto esta entrega não demonstra economia de chamadas por seleção inteligente. Vínculos e cenários são preparados manualmente. A origem do transporte injetado permanece a auditar até existir resposta real/uso registrado; nenhum mock recebe valor de evidência sobre IA.

Pode-se sustentar: **viabilidade técnica do ciclo integrado, rastreabilidade de recomendações e correção dos cálculos/verificações nos nove casos sintéticos testados**. A indeterminação é preservada e seleção documental é distinta de recomendação. Não se pode sustentar: generalização, superioridade sobre baselines, precisão de IA no Alfa, causalidade exclusiva do grafo ou validação científica independente. A próxima etapa é revisar as referências com avaliadores independentes e, se autorizada, coletar previsões reais com protocolo congelado.
