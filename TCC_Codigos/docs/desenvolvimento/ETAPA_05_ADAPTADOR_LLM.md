# Etapa 5 — adaptador de interpretação LLM por nó

24/10/2026, America/Sao_Paulo. **Entregue pendente de revisão do coordenador e usuário.** O usuário aprovou a etapa 4 ao dizer “Aprovado, passe para a 5”. Somente etapa 5 executada; etapas 6–11 não iniciadas. Aprovação de entrega não constitui validação científica independente.

## Arquitetura e fronteira

Pacote stdlib isolado `TCC_Codigos/src/interpretacao_no/`: `contratos.py` projeta contexto e valida análise; `adaptadores.py` oferece `Simulado.analisar(contexto_no)` e `LLM.analisar(contexto_no)`; `__main__.py` demonstra uma análise prescrita. Nenhuma dependência do motor, legado, política manual, referências ou outputs. Não há agenda, alcance causal, baseline B/T, avaliador ou chamada automática de nós.

Fluxo: snapshot/evento normalizados + seleção explícita → ContextoNo versionado/hash → interpretador → AnaliseNo + execução observada → decisões estruturais `requer_revisao`. Não aplica proposta, não gera autorização por hash e não chama `calcular`. Uma citação válida pode sustentar uma interpretação falsa: todas as decisões conservam `suporte_semantico=nao_auditado`. Confiança autodeclarada nem sequer é campo aceito. Python deverá calcular somente após política de validação semântica/condições aprovada na integração, sem consultar gabaritos nem corrigir seletivamente previsões.

## Entradas e saídas

`montar_contexto(estado, evento, *, execucao_id, no_id, revisao, fonte_ids, relacao_ids=(), regra_ids=(), predecessores=(), obrigacoes=(), predicados=(), parcela_ids=()) -> dict` recebe objetos em memória e não lê arquivos. Exige evento na mesma versão do snapshot (a normalização de v1.0 para versão grafo é responsabilidade explícita do chamador), D0 e IDs resolvidos. A seleção positiva define fontes e relações visíveis; não percorre o diretório nem carrega todos os cenários. A lista deve incluir as fontes dos atributos/regras selecionados; fonte omitida causa erro, sem ampliação silenciosa. A cláusula local preserva as duas referências, texto condicional e operações permitidas, sem predeterminar aceite.

Contexto `1.0-contexto-no`: execução/projeto/evento/nó/revisão, hash canônico do snapshot e do contexto, nó/atributos locais, relato/origem/escopo, passagens literais, relações, regras, permissões, IDs de obrigações/parcelas, predicados e mapa de versões dos predecessores. Metadados livres de documentos e campos como gabaritos/outputs/políticas não são serializados. Hash do snapshot identifica o objeto recebido; não é prova externa de integridade nem de semântica. Fontes são dados e continuam literais; nenhuma instrução de documento é promovida a papel de sistema.

Predecessores nesta versão são `{no_id,revisao,fatos,fonte_refs}`; `fatos` deve ser passagem literal visível. A escolha do predecessor é explícita do chamador, não inferida pelo adaptador. Não aceita ResultadosNo arbitrários, deltas ou saídas arquivadas da etapa 4. Esta concretização conservadora ainda não transporta resultados quantitativos estruturados da execução corrente: extensão por lista positiva e vínculo de execução pertence à integração da etapa 6. Catálogos/condições são entradas confiáveis revisáveis do chamador; o construtor não demonstra relevância semântica da seleção nem imunidade contra conteúdo malicioso.

`validar(analise, contexto) -> decisoes` confere campos estritos, versão, vínculo de snapshot via contexto, revisões, fontes/localizadores, unidades, conhecimento, inteiros (sem bool/fração/negativo), permissões locais, regras/relações visíveis, condições, origens e colisões de escrita. IDs de efeito são canônicos por evento+alvo; o request fornece os hashes para evitar que o modelo tenha de calculá-los. IDs novos de obrigação devem ser resolvidos explicitamente pelo chamador em `obrigacoes`, nunca inventados pela resposta. Essa resolução e sua sustentação semântica continuam auditáveis, não são uma autorização científica por passar uma string.

Contexto também registra `restricoes` locais com ID/valor/fontes, `parcelas` selecionadas com valor base/fontes e mapa `proprietarios` explícito para restrições, parcelas e contratos. Para parcelas sem proprietário normalizado no snapshot, o mapa registra a atribuição do chamador e não afirma extração semântica automática. Testes com fontes correntes de k_f04b/k_547a/k_8c65 exercitam crédito, cobertura e tarifa desconhecida, sem calcular seus desfechos finais.

Operações habilitadas: substituir disponibilidade/duração; restrição contratual identificada; adicionar/substituir parcela; registrar custo pendente; confirmar manutenção/ausência sob regra/condição; propor parâmetros de regra temporal catalogada. Custos temporais são expostos somente no nó proprietário do fim do intervalo, sem cálculo global. Alteração direta de parcela temporal é bloqueada. `parcela_ids` seleciona compromissos existentes explicitamente; sua atribuição ao nó requer revisão do chamador. Nenhum catálogo é ampliado pelo LLM. Condições confirmadas na resposta são alegações, não validação externa.

AnaliseNo segue os campos da etapa 1, com `schema_version=1.0-proposta`; proposta inclui `no_id` para origem monetária e valor Conhecimento absoluto, exceto confirmações escalares e parâmetros catalogados. Avaliações são deltas locais em dia corrido/BRL centavo. Inaplicabilidade requer motivo; desconhecimento requer lacuna; zero exato exige evidência e ausência de lacuna. Ausência de aceite permite duração indeterminada, sem confirmação automática. Para representar custo pendente, o chamador precisa resolver uma identidade de item pendente em `obrigacoes`. JSON com NaN ou chave duplicada é rejeitado. A análise bruta não aceita campos de execução/consumo; o adaptador os acrescenta junto às decisões depois de validar.

## Transporte e erros

`LLM(transporte, *, modelo, configuracao, timeout_s, repetir_transporte=False)` exige parâmetros explícitos, sem escolher modelo/protocolo definitivo. Transporte é função injetada `request -> RespostaTransporte`; request contém mensagens de sistema/dados separadas, configuração, timeout e solicitação JSON. O prompt descreve o contrato e recebe permissões, sem resultados prescritos. O transporte deve cumprir timeout e traduzir falhas para `FalhaTransporte` ou `TimeoutError`. Não há SDK, cliente OpenAI, credencial, acesso de rede ou teste real. Implementar um transporte de provedor exigirá consultar documentação primária atual e validar parâmetros/recusas/truncamento/consumo do provedor. A interface não promete compatibilidade direta com um endpoint.

`RespostaTransporte(texto, estado, modelo, request_id, tokens_entrada, tokens_saida, custo_api_centavos, metadados)` representa observações do transporte. Estado é completa/recusa/incompleta. Retém texto bruto, ID/modelo observado, metadados, configuração/hash, latências e cada tentativa. Tokens/custo não observados ficam null. Totais com qualquer tentativa sem medição permanecem null. Modelo solicitado e observado ficam separados; consumo do corpo da resposta é rejeitado. Custo API não é custo do projeto.

Uma tentativa de conteúdo, sem reparo. Opcionalmente uma repetição idêntica somente para timeout/falha transitória, com ambas as tentativas contabilizadas. Recusa, truncamento, JSON inválido ou violação de contrato não repetem. Falha devolve identidade e execução erro, avaliação null e nenhuma proposta/decisão aplicável. `Simulado` cruza o mesmo parser/validador e envelope de erro, identifica origem simulada/modelo null e zero chamadas/tokens/custo API. Configuração de limites totais por execução e agenda é etapa 6; modelo, timeout científico, limites e orçamento de piloto serão definidos antes de coleta autorizada.

## Reprodução offline e evidência

Python 3.9+ e biblioteca padrão, a partir da raiz:

```sh
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa5 -v
PYTHONPATH=TCC_Codigos/src python3 -m interpretacao_no TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/estado_projeto.json
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa4 -q
python3 TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/validar.py
```

21 testes passaram, com subcasos de contraprovas: componente, montagem/aceite e desconhecimento, confirmação, simulado/imutabilidade, operações monetárias, aditivo/preço desconhecido, crédito, invisibilidade/colisão de fontes, IDs/versões/unidades/valores, origens, catálogo, chave extra/duplicada/NaN, zero sem sustentação, texto instrucional como dado, recusa/incompletude/JSON, timeout/falha transitória/definitiva, consumo e repetição. Um teste usa valor semanticamente falso com referência visível: permanece revisão, demonstrando que validação estrutural não é auditoria semântica. O teste de fonte instrucional verifica separação de mensagens, não resistência empírica de modelo à injeção.

O exemplo é um único componente com aviso fictício ilustrativo D4 e resposta prescrita fora do contexto, rotulado simulado. Produz contexto e análise validada, sem cálculo final. Testes consultam somente inputs autorais e selecionam o evento corrente; expectativas/respostas simuladas ficam nos testes, fora do contexto e do runtime LLM. Não executado experimento dos oito casos nem avaliação científica de interpretação. Regressão etapa 4: 37 testes passaram; validador etapa 3 passou com seis contraprovas rejeitadas. Suíte legada não repetida, problemas históricos preservados.

## Integridade, revisão e etapa 6

Antes das alterações documentais, 63 arquivos dos pacotes/documentação das etapas anteriores foram comparados entre worktree e principal por SHA256 e registrados. Integração seletiva somente do novo pacote, testes, deste documento e STATUS/PLANO_MESTRE. Destinos existentes são reconferidos contra os hashes capturados antes de qualquer substituição; dados, motor, testes e outputs anteriores permanecem por hash. Nenhuma alteração de módulo anterior, instalação, segredo, API, commit/push/PR.

Revisar: suficiência do contexto de predecessores, resolução das identidades de obrigação e proprietário de parcela, fronteira entre validação estrutural e semântica, campos adicionais de rastreio e transporte concreto futuro. O código está pronto para uso offline/injeção; não há evidência empírica de qualidade LLM nem autorização de coleta real.

Etapa 6, somente após aprovação: selecionar nós relevantes e fontes locais, normalizar evento, aguardar predecessores, definir contexto quantitativo corrente seguro/revisões, limites de execução, critérios de validação semântica sem gabaritos, converter propostas revisadas para o motor, deduplicar e consolidar. Não usar a política manual de hashes como autorização automática. Baselines/avaliação permanecem etapa 7; UI etapa 8. Etapas 6–11 não iniciadas.

Revisão preliminar incorporada: contexto local para restrição/parcela/contrato com proprietário explícito; paridade de falhas Simulado/LLM; projeção positiva aninhada e contraprovas; fronteira de transporte abstrato e timeout documentada. Total final: 21 testes etapa 5 e 37 etapa 4 aprovados.
