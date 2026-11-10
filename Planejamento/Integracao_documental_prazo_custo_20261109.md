# Integração da rastreabilidade documental com impactos em prazo e custo

Parecer técnico de 9 de novembro de 2026 para a reunião de orientação. A rastreabilidade documental permanece no escopo, conforme decisão do usuário. A proposta anterior de retirar essa dimensão do trabalho não é mais a recomendação vigente. Este parecer especifica a integração e a avaliação necessárias; não registra implementação ou coleta adicional.

## Conclusão executiva

Há uma base documental implementada e um piloto histórico com chamadas de IA registradas. Há também uma arquitetura quantitativa posterior com avaliação final congelada. Ainda não há evidência de um experimento integrado que compare o conteúdo dos registros, calcule impactos e recomende alterações localizadas. O caminho recomendado é conectar as duas frentes numa extensão delimitada, mantendo separados os resultados históricos e os novos.

A contribuição pretendida passa a ser avaliar a cadeia evento → entidades afetadas → impactos de prazo e custo → registros a revisar → recomendação sustentada por fontes e relações. Trata-se de recomendação para validação humana, não edição automática dos documentos.

## Inventário verificado

| Componente | Evidência local | O que permite afirmar |
|---|---|---|
| Quatro artefatos | `TCC_Codigos/data/artifacts/*.json` | Action Log, Risk Register, Decision Log e Status Report, com identificadores e vínculos a entidades |
| Regras documentais | `TCC_Codigos/src/tcc_agent/rules.py` | Mapeia oito tipos de evento para categorias de artefato; evento informativo retorna vazio |
| Propagação | `TCC_Codigos/src/tcc_agent/pipeline.py` e `graph.py` | Percorre relações e registra caminhos; não compara conteúdo documental |
| Baseline documental | `TCC_Codigos/src/tcc_agent/baseline.py` | Solicita classificação e indicação de artefatos; o prompt desta implementação recebe evento e dicionário de entidades |
| Avaliador | `TCC_Codigos/src/tcc_agent/evaluate.py` | Precision, recall e F1 por pares cenário e categoria de documento |
| Cenários antigos | `TCC_Codigos/data/scenarios_ground_truth.json` | 36 referências autorais já expostas no desenvolvimento |
| Piloto documental | `TCC_Codigos/outputs/validacao_local_20261018_170009/05_pilotos_reais/` | Seis registros por abordagem, prompts, respostas e metadados de uso; sem nova reconciliação com o provedor nesta inspeção |
| Arquitetura quantitativa | `TCC_Codigos/src/hibrido_v07_r3/` | Interpretação local, validação, coordenação e integração com motor determinístico |
| Avaliação quantitativa final | `TCC_Codigos/outputs/etapa11_final_20261028/RELATORIO.md` | Três casos, três condições, nove execuções; não mede recomendação de alterações nos quatro registros |

Os registros documentais legados pertencem ao projeto Alfa, enquanto o conjunto quantitativo final usa a Estação de leitura Sálvia. Não se pode conectar seus IDs automaticamente. A integração exige documentos coerentes com um mesmo projeto-base e um mapeamento explícito das entidades.

## Resultados documentais existentes

Recontagem realizada diretamente de `records.jsonl` das duas condições contra `scenarios_ground_truth.json`; os valores reproduzem os resumos salvos.

| Medida no piloto histórico | Baseline global | Híbrido legado |
|---|---:|---:|
| Casos | 6 | 6 |
| Indicações corretas | 8 | 11 |
| Alertas extras | 0 | 3 |
| Omissões | 3 | 0 |
| Precision | 100% | 78,57% |
| Recall | 72,73% | 100% |
| F1 | 84,21% | 88% |

A unidade é o par cenário e categoria de documento; não são 11 documentos distintos nem 11 cenários. O híbrido recuperou mais categorias esperadas ao custo de alertas adicionais. Seu F1 de entidades registrado é 35,71%, sinalizando que propagação ampla merece atenção. Não há demonstração de superioridade geral. As regras e referências autorais precisam de revisão quanto à independência: se o gabarito apenas reproduzir a regra por tipo de evento, o teste não valida necessidade real de revisão documental.

As pastas `03_pilotos_simulados` e `04_simulacao_completa` contêm simulações; seus 36 casos não constituem coleta real de desempenho. O piloto antigo e o experimento quantitativo posterior devem aparecer como estudos distintos, com versões, tarefas e condições explicitadas.

## Lacuna funcional no projeto

A função `artifacts_for_event(event_type)` não recebe o conteúdo dos documentos, seus estados ou o delta calculado. Assim, dois registros já atualizados e desatualizados podem receber a mesma recomendação. O sistema legado indica onde procurar; não demonstra qual afirmação está incorreta ou qual atualização deve ser proposta.

A extensão precisa localizar item ou campo, comparar o estado atual com o evento e o impacto, justificar a revisão ou a manutenção e conservar a evidência. Uma dependência alcançável no grafo é candidata à inspeção, não prova automática de que o registro deve mudar.

## Integração mínima proposta

1. Criar cópias versionadas dos quatro registros para um único projeto coerente com o motor quantitativo. Cada item deve ter ID, entidades vinculadas, conteúdo, estado, versão e fonte. Documentos introduzidos agora são dados de uma nova etapa, não parte retroativa da coleta final.
2. Consumir as saídas quantitativas por um adaptador separado, com leitura das evidências, impactos por entidade e estados exato, direcional ou indeterminado. Não modificar o preditor congelado para apresentar melhora retrospectiva.
3. Usar entidades e relações para selecionar registros candidatos. Aplicar verificação do conteúdo para distinguir desatualização, informação já incorporada, ausência de efeito e informação insuficiente.
4. Produzir uma recomendação estruturada: documento, item, campo, versão, afirmação atual, ação proposta, valor ou texto sugerido, motivo, fontes, caminho de relações e pendências.
5. Exibir proposta para revisão humana. Registrar aprovar, rejeitar ou corrigir como decisão de revisão; aplicação efetiva e edição automática podem permanecer fora deste MVP.

Estados recomendados: manter, revisar, acrescentar e solicitar informação. Responsáveis, datas e valores ausentes não devem ser inventados. Uma magnitude de custo desconhecida deve continuar desconhecida também no relatório proposto.

Exemplo proposto, ainda não executado: se o motor identifica mais seis dias e custo indeterminado, um relatório que ainda afirma término em D15 e custo final fechado deve ser candidato à revisão. Um item que já declara D21 e custo pendente deve ser mantido. Uma taxa ausente não autoriza criar uma decisão gerencial que nunca ocorreu; pode justificar uma solicitação de informação ou ação proposta, claramente marcada como sugestão.

## Protocolo complementar recomendado

Pergunta: em que medida a combinação de interpretação textual, relações estruturadas e regras quantitativas identifica registros gerenciais que precisam de revisão e produz recomendações sustentadas, inclusive sob informação incompleta?

Separar dois níveis de avaliação:

- Documental isolado: fornecer a todas as condições o mesmo evento, documentos e impacto quantitativo validado. Medir seleção dos registros e qualidade da recomendação. Isso investiga a camada documental sem confundir seus erros com os cálculos anteriores.
- Ponta a ponta: fornecer o evento e o estado inicial; medir toda a cadeia. Reportar erros de interpretação, cálculo e revisão documental separadamente. Os desempenhos dos dois níveis não devem ser misturados.

Para o nível documental, comparar no mínimo LLM global com as relações em texto versus híbrido que usa os mesmos fatos em estrutura e regras. Usar o mesmo contrato de saída e política de rejeição nas duas condições. Uma condição sem relações pode ser controle secundário, mas não isola o efeito da arquitetura. Mesmo com informação equivalente, múltiplas chamadas e cálculo externo continuam diferenças que precisam ser descritas.

Proposta de tamanho viável para discutir com o orientador: 12 a 18 cenários novos, com duas execuções por condição se orçamento e prazo permitirem. Isso é uma proposta de cobertura exploratória, não cálculo de poder estatístico. Repetições não aumentam o número de cenários independentes. Primeiro fazer poucos casos de desenvolvimento distintos; depois congelar sistema, protocolo e referências antes dos novos casos finais.

Cobrir atraso direto e indireto, mudança local sem alteração do término global, crédito sem atraso, custo indeterminado, decisão explícita, compromisso de ação, documento já atualizado e evento sem efeito. Incluir registros irrelevantes plausíveis e versões desatualizadas. Pares com mesmo evento e estados documentais diferentes são essenciais para verificar se o sistema realmente compara conteúdo em vez de aplicar apenas uma tabela fixa.

Os três casos finais antigos podem ser demonstrações de integração e desenvolvimento; já estão expostos e não devem ser apresentados como novos testes cegos. Os 36 casos antigos também não recuperam ineditismo.

## Avaliação das recomendações

- Precision, recall e F1 no nível documento e no nível item, com denominadores e contagens TP, FP e FN.
- Taxa de mudanças desnecessárias em registros já corretos e negativos, para evitar que muitos verdadeiros negativos escondam omissões.
- Correção da operação e do conteúdo proposto, incluindo números, estados e restrições.
- Rastreabilidade estrutural e sustentação semântica separadas: um ID de fonte válido não garante que a fonte sustente a recomendação.
- Preservação da indeterminação e ausência de fatos gerenciais inventados.
- Validade do formato, custo, latência e falhas operacionais, mantendo rejeições nos denominadores previstos.

Referências devem ser elaboradas a partir dos documentos e política explícita de gestão, revisadas por humano antes das previsões sempre que possível. Aceitar alternativas justificadas por uma rubrica; não exigir apenas igualdade literal do texto. Avaliar tempo ou utilidade para gestores exige estudo humano próprio e não pode ser inferido do tempo de API.

## Plano até a defesa

Na reunião, validar contribuição, extensão mínima, responsável pela revisão das referências e data de entrega à banca. Nos dias seguintes, preparar dados, adaptador e rubrica; executar um piloto separado; congelar; realizar a coleta complementar somente após dimensionar custo e prazo. A redação deve ocorrer em paralelo, aproveitando arquitetura e resultados existentes.

O saldo conservador registrado ao final da coleta anterior era aproximadamente US$ 0,43 sob teto de US$ 5. Não há base para afirmar que a nova avaliação cabe nesse saldo. Medir custo do plano antes de autorizar nova coleta; nenhuma chamada paga foi realizada nesta investigação.

A implementação adicional tem dependências reais e não está concluída. Recomenda-se limitar o fluxo a recomendações inspecionáveis, evitando integrações com sistemas externos, edição automática de arquivos ou funcionalidades novas de interface sem necessidade experimental.

## Relação com a literatura

Consultar o parecer complementar `Literatura_rastreabilidade_20261109.md`, com fontes primárias e distinção entre trabalhos próximos e possíveis lacunas. Nenhuma contagem desta busca deve ser tratada como estimativa do total de publicações da área. A relevância do TCC depende da pergunta delimitada, da comparação justa e da avaliação verificável; não da afirmação de que LLM com grafo é uma técnica inédita.
