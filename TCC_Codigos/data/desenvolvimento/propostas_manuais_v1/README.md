# Entradas estruturadas manuais — etapa 4

Oito transcrições autorais de fatos dos avisos em `../projeto_minimo_v1/inputs/`, para exercitar somente o cálculo. Não são extração automática, saída de LLM, previsão experimental ou referências de avaliação. Não contêm datas finais, deltas esperados nem listas de nós afetados. Cada execução parte do mesmo snapshot do grafo; nenhum aviso de outro caso é carregado.

`evento` preserva relato/fontes e normaliza apenas `versao_projeto` para a versão do EstadoProjeto da etapa 3; `versao_evento_origem` guarda v1.0. `propostas` usa campos de Proposta da etapa 1 e a extensão `no_id` para localizar no rastro uma alteração de custo. Identidades de cobranças vêm dos avisos. A alternativa escolhida D3 é transcrita, não otimizada. Laudo aceito é confirmação manual sob u_813c; sem aceite, duração fica indeterminada e há item pendente não negativo para custo de readequação, sem preço inventado.

`politica` registra autorização autoral por SHA256 de cada proposta inteira, predicados manuais e requisitos locais a resolver. Alterar proposta invalida a autorização até revisão explícita. Isso não é assinatura criptográfica, análise semântica automática ou proteção contra um chamador que controla a política. Não gerar política automaticamente de saída de LLM. Aditivos de cobertura/taxa são autorizados individualmente somente neste ambiente manual.

Pequenas concretizações internas: operação `registrar_lacuna_custo` representa um item pendente de custo, com conhecimento e domínio não negativo documentado; não afirma que já exista obrigação de preço definido. `aplicar_regra_catalogada` parametriza aditivo explícito validado, sem fórmula livre. Não se propõe ampliar automaticamente o catálogo do futuro interpretador. Limites de conhecimento são metadados opcionais de prova, não estimativas. Revisão humana independente continua pendente.

A política de escopo declara que o restante se mantém, conforme cada aviso. O motor valida suas autorizações e requisitos; ele não descobre requisitos semânticos omitidos pelo chamador. Um futuro adaptador deve construir contextos e requisitos de forma revisada na etapa própria.

Revisão delimitada: regras locais só são exigidas como candidatas quando alcançáveis a partir do componente alterado na projeção declarada. Sem regra local, a transferência determinística segue normalmente. O chamador revisa condições e fornece resolução/lacuna; cláusulas fora dos candidatos não são exigidas automaticamente. Decisões globais e nos_alvo conservam o proprietário de alterações de restrição e regra temporal.
