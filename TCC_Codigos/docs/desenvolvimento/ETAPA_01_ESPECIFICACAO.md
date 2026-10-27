# Etapa 1 — especificação do experimento e das interfaces

24/10/2026, America/Sao_Paulo. **Etapa 1 e suas quatro propostas APROVADAS pelo usuário em 24/10/2026.** Etapa 2 entregue como rascunho autoral, aguardando revisão; etapas 3–11 não iniciadas. A aprovação não é congelamento do experimento final. Nota de vigência: o corpo abaixo preserva a redação e o histórico da proposta/revisão; menções históricas a “não aprovada”, “aguardando revisão” e “etapa 2 não iniciada” foram superadas por esta aprovação. [Plano](PLANO_MESTRE.md) · [Inventário](ETAPA_00_ESTADO_ATUAL.md) · [Status](STATUS.md).

## 1. Compromissos e escopo proposto

O objetivo aprovado é construir e avaliar software que use relações explícitas e interpretação LLM nos nós relevantes para estimar **variação do término final e do custo total do projeto**. Entidades/documentos afetados são intermediários. IA interpreta evidências e propõe alterações; Python valida e calcula. Nenhum modelo ou lote pago foi selecionado/executado aqui.

**Fatos atuais** são os do inventário: base ebcc16c, grafo 40/65, 36 cenários e seis DEV, 34 casos V2.2 conhecidos; motor BFS limitado e ausência de cálculo geral e LLM por nó. **Aprovação existente** abrange a direção e a etapa 0, não os detalhes abaixo. Todas as escolhas técnicas desta especificação são **propostas para revisão**.

V1: projeto fictício pequeno, um acontecimento por execução, simulação prospectiva no instante inicial (sem atividades parcialmente executadas), dependências temporais acíclicas, sem disputa de recursos. Primeiro caso em cadeia; já especificamos convergência para evitar uma interface que precise ser refeita. Calendário contínuo de dias corridos inteiros, origem D0 (sem timezone para aritmética), intervalos [início,fim), término exclusivo. Uma atividade de duração 2 iniciada em D3 termina em D5. Moeda BRL, valores em centavos inteiros; apresentação em R$. Datas civis podem ser rótulos por conversão de D0, nunca uma segunda base de cálculo.

Término do projeto = data do único marco final designado, que deve depender de todas as entregas obrigatórias. Custo total = todas as parcelas do orçamento do escopo declarado mais alterações líquidas autorizadas e regras temporais aplicáveis; não é preço de venda, faturamento nem fluxo de caixa. Referência para variação: estado planejado imutável no D0, recalculado com as mesmas regras; Δfim=Fnovo−Fbase e Δcusto=Cnovo−Cbase. Positivo significa atraso/aumento; negativo, antecipação/economia. A baseline numérica do projeto pode ser comum sem revelar sua rede.

Exclusões por complexidade: dias úteis/feriados, frações de dia, recursos compartilhados, progresso real, múltiplos acontecimentos interativos, probabilidades, juros/tributos/câmbio, otimização de alternativas, ciclos de retrabalho e relações início-início/término-término. Alternativa não contratada exige revisão, não escolha automática pelo menor custo. Ausência dessas capacidades deve ser declarada; não simular solver universal.

## 2. Convenções comuns e cinco contratos

Proposta de serialização: JSON versionado `schema_version="1.0-proposta"`. Campos nas tabelas são obrigatórios salvo `?`. IDs são strings opacas únicas no respectivo catálogo; nenhuma ordem, família de caso ou caminho é codificado nos IDs. Referências devem resolver na mesma versão. Listas vazias são explícitas; `null` significa valor desconhecido ou inaplicável, distinguido pelo campo de estado/motivo. Não usar NaN, número textual monetário ou zero como substituto de ausência.

`Fonte={id, documento_id, versao, localizador, trecho}` identifica passagem verificável. Fontes são fatos/contratos e podem ter autoria fictícia declarada; não incluem resposta esperada. Hash dos arquivos e versão do manifesto acompanham a execução. `EvidenciaRef={fonte_id, localizador}`; uma citação deve apontar a trecho disponibilizado à condição. Referência autoral de avaliação é armazenada separadamente, sem campo `expected_*` em nenhum input.

Um `Conhecimento<T>` tem `estado: exato|direcao|indeterminado|inaplicavel`, `valor:T|null`, `direcao:aumento|reducao|zero|desconhecida`, `evidencias:EvidenciaRef[]`, `lacunas:string[]`, `motivo:string|null`. Exato exige valor; em deltas, direção deve ser compatível com o sinal e exato zero exige suporte positivo à ausência de mudança. Em valores absolutos (data, duração, total), `direcao=desconhecida` significa comparação inaplicável, sem retirar a exatidão do valor. Direção exige valor null e direção diferente de zero/desconhecida; indeterminado exige valor null, direção desconhecida e lacunas. Inaplicável exige valor null, direção desconhecida, lacunas vazias e motivo não vazio (ex.: entidade sem atributo temporal); não representa desconhecimento. Nos outros estados, motivo pode ser null; indeterminação exige lacunas mesmo quando existe motivo. Resultado de execução é separado: `ok|parcial|erro`. Erro inclui código e mensagem; não é conclusão epistêmica. Não se calcula com direção como se fosse magnitude.

### 2.1 EstadoProjeto

| Campo / tipo | Conteúdo e invariantes |
|---|---|
| `projeto_id, versao, escopo:string` | Identificação e descrição dos custos/entregas incluídos. |
| `calendario:{id,origem_label,unidade:"dia_corrido",indice_inicial:0}`; `moeda:"BRL"` | Base única. |
| `fontes:Fonte[]`; `entidades:Entidade[]` | Fatos e proveniência, sem gabaritos. |
| `atividades:Atividade[]`; `marco_final_id:string` | Atividade aponta entidade do tipo atividade ou marco. Campos mínimos de Atividade e restrições identificadas definidos abaixo; marco tem duração exata 0. `fonte_refs` por atributo. |
| `relacoes:Relacao[]` | Conhecimento explícito reservado às condições autorizadas. `{id,origem_id,destino_id,tipo,fonte_refs}`; tipos `fornece`, `requer`, `responsavel`, `pertence`, `precede_FS`. `precede_FS` liga predecessor→sucessor temporal (lag v1=0). `requer` liga atividade→componente; não é FS e só gera requisito de liberação pela regra específica abaixo. Tipos não são intercambiáveis. |
| `regras_transferencia:RegraTransferencia[]` | Catálogo explícito de projeção causal e restrições derivadas, definido abaixo; sem inferência genérica pela orientação da aresta. |
| `regras_locais:RegraLocal[]` | `{id,no_id,clausula:EvidenciaRef,operacoes_permitidas:string[],atributos_alvo:string[]}`. Catálogo autoriza operações, sem preencher se a condição se aplica ao evento. |
| `parcelas_base:Parcela[]`; `regras_custo:RegraCusto[]` | IDs únicos e fontes; composição na seção 6. |
| `declaracoes_completude:{entregas,custos,relacoes}: {completa:boolean,fonte_refs}` | Fechamento do escopo com fonte; lista vazia não prova ausência. |
| `linha_base:{fim:Conhecimento<int>,custo_centavos:Conhecimento<int>}` | Calculada e conferida; inconsistência com regras impede execução até revisão. |

`Entidade={id,tipo:fornecedor|componente|atividade|marco|pessoa|area,nome,atributos,fonte_refs}`. Atributos têm tipo, unidade, valor/conhecimento e fontes. Fornecedor/pessoa/área não têm duração; componente pode ter disponibilidade, não duração de tarefa. Disponibilidade vira liberação de uma atividade somente por regra explícita `requer`, com fonte. Relação responsável/pertence é contextual, não transmite atraso. Entidades podem existir apenas para identificação/interpretação.

`Atividade={id:string,entidade_id:string,duracao:Conhecimento<int≥0>,restricoes_liberacao:RestricaoLiberacao[],fonte_refs:EvidenciaRef[]}`. Na v1 `id=entidade_id`, para evitar dois namespaces de endpoints: é o identificador usado por precede_FS e marco_final_id e resolve para uma única entidade atividade/marco. `RestricaoLiberacao={id,atividade_id,tipo:nao_antes|disponibilidade_requerida,valor:Conhecimento<int≥0>,fonte_refs,regra_transferencia_id?:string,atributo_origem_ref?:{entidade_id,atributo}}`. Restrições têm identidade própria e permanecem simultaneamente ativas. Ausência de restrições significa apenas piso D0 se o fechamento de requisitos estiver declarado; não significa dados completos por padrão.

Convenção semântica: `fornece` é fornecedor→componente, `requer` é atividade→componente, `responsavel` é pessoa→atividade, `pertence` é entidade→área; estas três relações contextuais (fornece/responsavel/pertence) não transferem efeito automaticamente. `RegraTransferencia={id,relacao_id,operacao:"disponibilidade_para_restricao",origem_atributo:"disponibilidade",restricao_destino_id,fonte_refs}` é a única transformação requer v1: valida que a origem da relação é atividade e destino é componente; lê a disponibilidade no **destino** componente e materializa/atualiza a restrição identificada na **origem** atividade. A projeção causal executável tem, portanto, componente→atividade, com IDs da relação e da regra preservados. Não se invertem todas as arestas requer indiscriminadamente: sem esta regra e fonte, requer é conhecimento contextual e há lacuna se a atividade precisar de disponibilidade. FS mantém direção predecessor→sucessor; outras transferências ficam fora de catálogo/requerem revisão.

### 2.2 Acontecimento

| Campo / tipo | Conteúdo |
|---|---|
| `evento_id, projeto_id, versao_projeto:string`; `instante_observacao:int` | V1 instante 0; a data de disponibilidade futura pode ser maior. |
| `relato:string`; `origem:{autor,documento_id,data_registro}` | Relato original preservado; autor pode ser fictício declarado. |
| `evidencias:Fonte[]`; `entidades_mencionadas:string[]` | Menções resolvidas ou lista vazia + lacuna; não são lista de impactos. |
| `escopo:string`; `lacunas:string[]` | Um acontecimento pode conter várias consequências, sem transformá-las em eventos independentes. |

Não exige que o usuário forneça deltas calculados, caminhos afetados ou classificação esperada. Quantidade e unidade no relato são fatos a interpretar; o interpretador não recebe resposta final escondida no evento.

### 2.3 AnaliseNo — proposta do interpretador, sem efeito automático

| Campo / tipo | Conteúdo |
|---|---|
| `analise_id, execucao_id, evento_id, no_id:string`; `revisao:int` | Vínculo inequívoco. |
| `contexto_hash:string`; `predecessores_versoes:map<string,int>` | Snapshot efetivamente visível; permite invalidar análise obsoleta. |
| `avaliacao:{prazo:Conhecimento<int>,custo:Conhecimento<int>}` | Conclusão interpretativa local, distinta do cálculo final. |
| `propostas:Proposta[]` | `{id,operacao,alvo_id,atributo,valor,unidade,evidencias,relacao_refs,regra_refs,condicoes,origens_causais}`. Operações permitidas: substituir disponibilidade/duração ou valor de restrição de liberação identificada, adicionar ou substituir parcela, aplicar regra catalogada, confirmar manutenção de atributo ou ausência de parcela adicional sob condição identificada. Confirmar manutenção não altera valor; confirmar ausência registra zero sustentado em avaliação.custo, sem criar item no livro. Todas as operações exigem alvo e evidência; confirmações exigem também regra_refs e condição verificável. |
| `justificativa:string`; `lacunas:string[]` | Explicação curta verificável; sem exigir cadeia de pensamento privada. |
| `execucao:{estado,codigo_erro?,mensagem?,modelo?,config_hash?,chamadas,tokens?,latencia_ms}` | Adaptador simulado identifica `modelo=null` e origem simulada; nunca rotulado experimento real. |

Origens causais são `{evento_id,fato_ref,efeito_id}`; `efeito_id` estável é atribuído/confirmado pelo validador, não aceito só porque a IA inventou um ID. Condições são predicados de catálogo sobre atributos disponíveis, não código Python ou fórmula livre. Nova relação/regra, mudança de escopo ou operação fora de catálogo retorna `requer_revisao`; não executa. Confiança autodeclarada não autoriza aplicação.

### 2.4 ResultadoNo — validado/calculado

| Campo / tipo | Conteúdo |
|---|---|
| `execucao_id,no_id,evento_id:string`; `revisao:int`; `contexto_hash:string` | Mesma revisão da análise usada, se houver. |
| `predecessores_versoes:map<string,int>` | Revisões dos resultados de entrada usados no cálculo, inclusive reutilizados da baseline; mapa vazio quando não há entradas causais. |
| `processamento:calculado|inalterado_verificado|nao_avaliado|bloqueado` | Inalterado exige verificação registrada; não avaliado não autoriza zero. |
| `execucao:{estado,codigo_erro?,mensagem?}` | Falha operacional separada. |
| `decisoes: {proposta_id,status:aceita|rejeitada|requer_revisao,motivos}[]` | Validação auditável. |
| `inicio,fim,delta_fim:Conhecimento<int>` | Conhecimento com estado inaplicavel e motivo em entidade não temporal; indeterminado para data aplicável desconhecida. Datas não inventadas. |
| `efeitos_custo: {parcela_id,efeito_id,delta_centavos,fonte_refs}[]` | Referências ao livro de parcelas; não soma de custos acumulados dos predecessores. |
| `origens_causais:[]`; `regras_aplicadas:string[]`; `evidencias:[]`; `lacunas:string[]`; `analise_id?:string` | Rastro e limitação; análise ausente exige motivo determinístico registrado. |

### 2.5 ResultadoFinal

| Campo / tipo | Conteúdo |
|---|---|
| `execucao_id,projeto_id,versao,evento_id,condicao,manifesto_hash:string` | Identifica execução reproduzível. |
| `fim_base,fim_novo,delta_dias:Conhecimento<int>` | Mesmo marco; não somar deltas locais. |
| `custo_base,custo_novo,delta_centavos:Conhecimento<int>` | Mesmo escopo e moeda; custo final não negativo. |
| `completude:{prazo:completo|parcial,custo:completo|parcial}`; `parcial_identificado_centavos:int?` | Parcial é montante identificado, com lista de parcelas e lacunas; não é automaticamente limite inferior. |
| `resultados_no_refs:string[]`; `livro_parcelas:[]`; `lacunas:string[]`; `execucao:{estado,erros:[]}` | Deduplicação e suporte dos resultados. |
| `consumo:{chamadas,tokens_entrada?,tokens_saida?,custo_api_centavos?,latencia_ms}` | Custo API separado do custo do projeto. Ausência de preço/token fica desconhecida. |

Para baseline, as seis quantidades (fim base/novo/delta e custo base/novo/delta) seguem o mesmo formato de saída; rastro por nó pode ser vazio com motivo `condicao_sem_motor`. Não fabricar ResultadoNo para aparentar execução de grafo. Valores de linha base também são conhecimento: base desconhecida impede delta exato mesmo se novo total for conhecido.

## 3. Interfaces dos módulos e divisão de trabalho

Interfaces conceituais propostas; não são implementação ou lista de novos serviços. Módulos retornam dados e diagnóstico, preservam entrada imutável e recebem dependências explicitamente.

| Interface | Responsabilidade / saída / erros |
|---|---|
| `preparar(estado,evento,condicao) -> Contextos + Diagnosticos` | Valida IDs, unidades, fontes, completude, DAG temporal e baseline; projeta dados visíveis. Erros: referência inválida, ciclo, unidade/escopo incompatível, baseline inconsistente. Sem LLM para consertar silenciosamente. |
| `analisar(contexto_no) -> AnaliseNo` | Seam do interpretador; dois adapters futuros: LLM e simulado com respostas prescritas. Não calcula cronograma geral; interpreta cláusulas, condições, alvos e mudanças locais. Erros: timeout, indisponibilidade, saída inválida. |
| `validar(analise,contexto,politica) -> Decisoes` | Confere permissão, evidência existente, trecho visível, relação/tipo/direção, unidade, condição resolvida, causalidade e escopo. Não executa código vindo da IA. |
| `avaliar(estado,evento,interpretador,politica) -> ResultadoFinal` | Módulo profundo que agenda, interpreta quando necessário, calcula datas/livro e consolida. Modo simulado cruza a mesma interface. Falhas parciais preservadas. |
| `prever_baseline(contexto_comum,adaptador) -> ResultadoFinal` | Uma previsão global sob política da seção 7, sem acesso ao módulo de grafo. |
| `avaliar_resultados(previsoes,referencias,manifesto) -> Relatorio` | Único módulo que lê referências de avaliação; nunca chamado pelo preditor. |

Python confere estrutura e executa aritmética. Estrutura válida e citação existente **não provam correspondência semântica**: trecho pode não sustentar a interpretação. Registrar duas verificações: automática estrutural e suporte semântico auditável. Antes do congelamento, revisar catálogo/regras e interpretações ambíguas; durante avaliação não consultar gabaritos nem fazer correção humana seletiva. Ambiguidade não resolvida retorna indeterminação/revisão. Auditoria semântica posterior pontua a previsão original, sem reescrevê-la. Não usar a própria confiança da IA ou uma segunda aprovação idêntica como prova.

IA não deve receber “o nó atrasa exatamente três dias” como gabarito intermediário. Recebe fatos como disponibilidade e cláusulas de espera/diária, decide o que estes significam e propõe atributos/regras. Dependências FS e aritmética catalogada podem ser resolvidas sem IA quando não há interpretação nova; a qualidade da interpretação é avaliada separadamente da matemática.

## 4. Propagação, agenda e parada

1. Validar projeto e registrar baseline completo. Toda atividade requerida pelo marco final e toda parcela de escopo devem ser verificáveis; erro estrutural global impede resultado completo. Grafo contextual pode ter ciclos de associação, mas apenas tipos com regra causal participam da propagação; v1 exige aciclicidade também na projeção causal executável.
2. Resolver menções do evento; ambiguidade de alvo é lacuna, não escolha arbitrária. A partir dos alvos formar candidatos na projeção causal por relações com regra de transferência autorizada (seção 2.1). Em particular X→A decorre da regra associada a A requer X; não da orientação bruta da aresta. Alcançabilidade é filtro de candidatos, não prova de impacto; relações contextuais não propagam por padrão.
3. Expandir a dependência de cálculo: incluir todos os predecessores necessários, mesmo os ramos não alterados fora dos descendentes do evento. Podem reutilizar estado baseline verificado. Uma convergência só é exata se os limites relevantes forem conhecidos ou houver prova de que uma lacuna não pode dominar.
4. Ordenar topologicamente a projeção executável e processar quando os predecessores necessários estiverem disponíveis. Chamar LLM se evento/evidência mudou um atributo ou há condição local a interpretar diante de entrada alterada. Transformação determinística já catalogada pode dispensar chamada, com motivo no rastro. Não chamar indiscriminadamente em todos os nós; não usar BFS com limite quatro para concluir término.
5. Para cada nó validar propostas antes de aplicar a uma cópia do estado. Recalcular datas absolutas/livro. Guardar chave `(execucao,no,hash_contexto)`; o mesmo contexto não é analisado duas vezes. Um mesmo efeito de custo usa ID canônico único, mesmo alcançado por dois caminhos.
6. Se saída relevante para sucessores não mudou e não há condição pendente, encerrar aquele ramo por prova de invariância. Atividades posteriores ainda necessárias ao fechamento recebem reutilização baseline verificada, não `nao_avaliado`. Se há lacuna, propagar dependência da lacuna até os desfechos que ela possa afetar; não interromper declarando zero.
7. V1 usa snapshot e uma passagem topológica, sem laço de autoaperfeiçoamento. Regras de custo são avaliadas depois que as datas que referenciam estão disponíveis; não criam aresta temporal reversa. Mudança de contexto invalida revisão anterior e seus descendentes e gera nova revisão registrada; mudança de topologia/regra exige revisão fora da execução, não inserção tardia. Versões antigas ficam no log, só a vigente compõe o resultado.
8. Parar quando agenda vazia e todos os desfechos tiverem prova de fechamento ou lacuna/erro explícito. Limite de chamadas/tempo excedido retorna parcial/erro, nunca resultado completo. Ciclo, referência inexistente e dependência incompatível são diagnósticos operacionais, distintos da falta legítima de evidência.

## 5. Modelo temporal pequeno

Somente FS com lag zero. Para atividade i: `S_i=max(0,R_i,max(F_p para todos p predecessores))`; `F_i=S_i+D_i`. `R_i=max(0,valor de cada restrição de liberação ativa de i)` é a liberação efetiva **derivada**, não um atributo substituível. Inclui as restrições contratuais e as disponibilidades requeridas materializadas por regra identificada; duração D não negativa. O máximo só é exato quando restrições são conhecidas ou existe prova de dominância documentada. Sem predecessor, máximo interno é omitido. Marco final tem duração zero. Baseline aplica as mesmas equações; datas planejadas fornecidas são conferidas, não restrições implícitas.

Evento pode propor substituição de D, de disponibilidade ou do valor de uma restrição identificada, com fonte e permissão. Nunca substitui R efetiva apagando a lista de restrições. Disponibilidade X=D6 altera somente o requisito derivado de X; se existir também contrato não antes de D8, R continua max(6,8)=8. Remoção de restrição não é operação v1 automática: exige revisão. Antecipação é permitida somente se a fonte autoriza menor liberação/duração e não existe restrição inferior adicional. Restrição contratual “não antes de D8” entra em R e continua valendo. V1 não modela prazo rígido como impedimento de atraso: data-alvo contratual é informativa e eventual multa só existe por regra de custo explícita. Prazo final projetado pode superar a meta.

Convergência usa `max` de datas, nunca soma de atrasos dos ramos. Folga surge das liberações e predecessores: não subtrair uma variável folga outra vez. Duração desconhecida ou predecessor sem data pode impedir cálculo. Só inferir zero/direção apesar de lacuna se houver prova registrada (por exemplo limite superior documentado do ramo desconhecido abaixo de predecessor dominante). V1 pode abster-se conservadoramente; não exige solver de intervalos. Direção final sem magnitude exige suporte para efeito em término final, não mera tendência local.

## 6. Livro de custo e composição

`Parcela={id,escopo_id,descricao,valor_centavos:int≥0,moeda:"BRL",fonte_refs}`. Livro base contém cada compromisso de custo uma vez, inclusive valor base de contrato temporal. Parcela de desconto/crédito é alteração assinada sobre item identificado, não custo base negativo. Cada alteração tem `efeito_id,parcela_id,origem_causal,operacao,valor,fonte_refs`; colisão de IDs com conteúdo diferente é erro. Mesma obrigação vista no fornecedor e na atividade é referência, não duas parcelas.

Regra temporal v1 catalogada: `{id,parcela_id,taxa_centavos_dia,intervalo:{inicio_ref,fim_ref},base_contratada_dias,politica_reducao:sem_credito|recalculavel_com_credito,condicao,fonte_refs}`. Referências de intervalo são D0, início/fim de atividade ou marco conforme contrato; não são atrasos locais somados. Para cada estado t (base ou novo), `L_t=fim_t−inicio_t` e `E_t=max(0,L_t−base_contratada_dias)`. A incidência calculável é `I_t=taxa×E_t`. O livro base **já inclui I_base** na parcela temporal, além do valor fixo contratado: a conferência da baseline deve demonstrar essa decomposição. Não adicionar extensão preexistente outra vez.

Delta temporal com cláusula `recalculavel_com_credito`: `I_novo−I_base`, inclusive negativo se a fonte garante estorno da extensão base ainda não incorrida nesta simulação prospectiva. Com cláusula `sem_credito`: `max(0,I_novo−I_base)`, porque o valor da parcela base permanece comprometido sem devolução; redução da duração não gera economia. Cláusula ausente/ambígua deixa o delta indeterminado quando a incidência cai. Não inferir a política só do sinal do atraso. Alterar taxa, base contratada ou política exige fonte e revisão de alteração contratual; não é transferência automática de prazo.

Intervalo incidente e base contratada devem ter mesma unidade/calendário. A parcela final é seu valor base mais o delta autorizado; o histórico conserva I_base/I_novo e o cálculo do delta. Regra e alteração direta da mesma obrigação devem ser reconciliadas pelo validador ou bloqueadas como potencial dupla contagem. Uma regra não pode incluir novamente o valor fixo nem uma extensão já representada em outra parcela.

`Cnovo = soma(parcelas_base) + soma(alteracoes_liquidas_unicas)`; `ΔC=Cnovo−Cbase`. Somar apenas deltas diretos por obrigação e deltas temporais contratuais. Não multiplicar todo atraso por diária genérica. Recursos ociosos, multas, frete ou desconto só entram com fonte, taxa, período, condição e escopo. Não somar custos acumulados de cada ResultadoNo. Uma alteração não pode deixar o custo da obrigação negativo sem suporte a crédito separado e revisão do escopo.

Fechamento completo exige orçamento exaustivo declarado e todas as regras aplicáveis resolvidas. Soma de valores conhecidos com lacuna vira `parcial_identificado`, não total. Não é necessariamente limite inferior: pode faltar desconto. Estado de prazo e custo são independentes: é possível prazo exato e custo indeterminado.

## 7. Condições experimentais e informação visível

Pergunta comum: “Em relação ao plano D0 deste escopo, qual é a variação do término do marco final em dias corridos e do custo total em BRL? Informe magnitude quando sustentada, direção quando sustentada sem magnitude, zero sustentado, lacunas e erros.” Todos recebem calendário, escopo, baseline de término/custo, catálogo de entidades e atributos não relacionais, fontes comuns, acontecimento e definições de saída. A pergunta não pede só entidades atingidas.

| Condição | Relações e execução propostas |
|---|---|
| B — baseline principal | LLM global com dados comuns, sem arestas explícitas ou listas de predecessores. Uma chamada lógica global, sem ferramentas externas de cálculo/execução. Pode raciocinar e calcular na resposta. |
| H — sistema híbrido | Mesmos fatos comuns, mais relações explícitas e suas fontes exclusivas de relacionamento; LLM local sob agenda + cálculo determinístico Python. N chamadas lógicas no máximo, uma por nó interpretativo/contexto vigente; N depende do caso e é registrado. |
| T — controle opcional recomendado | Mesmo contexto de B mais a mesma lista completa de relações de H em texto neutro e suas fontes. Uma chamada global, sem motor/agenda Python. Diagnostica acesso às relações, sem isolar todos os efeitos. |

Política recomendada é comparar sistemas completos; não fingir igualdade de execução ou informação. Diferenças B/H podem decorrer de conhecimento adicional, decomposição, número de chamadas, contexto e cálculo, além do grafo. T ajuda, mas H/T ainda difere em agenda e cálculo. Nenhuma diferença permite causalidade exclusiva do grafo. Conclusão aceitável: desempenho das configurações sob estas condições. Se objetivo mudar para isolar representação, aprovar outro desenho experimental antes da coleta.

Montar views por lista positiva de campos, não retirar apenas `edges`. IDs opacos, ordem neutra e ausência de `predecessores`, `afetados`, nomes de caminho, comentários, regras com endpoints ou fontes relacionais exclusivas em B. Datas base individuais podem permitir inferências legítimas; registrar isso. Relações genuinamente presentes no relato comum ou cláusula necessária ao significado do evento permanecem em todas as condições e são inventariadas como conhecimento comum. Não apagar fatos de maneira seletiva para prejudicar B. Auditoria manual das views verifica vazamento e perda indevida de evidência. Relações derivadas de fontes excluídas de B são a assimetria declarada, não informação “igual”.

Regras gerais de calendário/custo e fatos de contrato não relacionais são comuns; vínculo específico entre entidades é informação relacional inventariada. Não fornecer a B a saída do solver, ranking de impactos, caminho crítico ou contexto escolhido pelo grafo. O serializador de B não chama o motor de H para completar resposta. Parser pode validar formato e unidades, sem recalcular/corrigir previsão.

Modelo/configuração: propor a mesma versão de modelo para B/H/T, com prompt de papel apropriado, mesmos parâmetros de geração disponíveis e teto de saída por chamada. Modelo, parâmetros concretos, teto total por execução, timeout e orçamento em BRL serão definidos no piloto autorizado, antes de coleta; sem seleção agora. As condições não têm orçamento total de chamadas igual e devem reportar consumo observado. Truncamento de contexto é erro registrado, não omissão silenciosa. Proposta: uma tentativa sem reparo de conteúdo; no máximo uma repetição de transporte para timeout/falha transitória, registrada e contabilizada. Resposta inválida não recebe dica de gabarito. Teto total impede chamadas ilimitadas; atingi-lo gera execução incompleta. Mudança da política de ferramentas ou retentativas exige nova versão do protocolo.

## 8. Avaliação, cobertura e independência

Referência separada: `{caso_id,familia_id,versao,escopo,fontes,delta_dias,delta_centavos,estado_conhecimento_por_view,derivacao_manual,revisores,divergencias}`. Não é sexto input do sistema. Verdade do cenário e suporte no contexto visível são eixos diferentes: B pode acertar por palpite algo não inferível; ou abster-se adequadamente por falta de relações. Revisores devem julgar ambos sem premiar inferência sem evidência.

Por desfecho, registrar em todos os N casos/repetições: exato (inclui zero), direção sem magnitude, indeterminação, inválido e erro operacional. Reportar cobertura numérica `n_exatos_validos/N`, taxa de indeterminação, inválidos, erros e proporção de zero sustentado. Uma saída numericamente errada ainda conta na cobertura de saída válida; “válida” aqui significa formato e unidade, não acerto. Classificar suporte semântico separadamente.

Erro absoluto em dias = `abs(predito−referencia)`; em BRL = `abs(centavos_pred−centavos_ref)/100`. MAE por desfecho só sobre pares numericamente válidos e referência exata, com n/N explícito. Comparação pareada apresenta também interseção de casos válidos nas duas condições e cobertura de cada uma; não anunciar menor MAE como superioridade global se cobertura difere. Referência indeterminada não tem erro numérico. Não imputar zero ou penalidade monetária arbitrária a abstinência/erro. Relatar número de previsões corretas sobre todos os casos elegíveis junto aos condicionais, evitando seleção favorável de denominador.

Direção: redução/zero/aumento para referência exata; direção sustentada sem magnitude pode ser correta neste eixo sem entrar no MAE. Para referência indeterminada, avaliar abstenção apropriada e suporte por rubrica, sem transformar desconhecido em classe zero. Publicar matriz de estados/direções, contagens e denominadores. Exigir exatidão no dia inteiro/centavo para acerto numérico v1; tolerância diferente teria de ser justificada e congelada antes. Rubrica de suporte: sustentado, contradito, insuficiente; revisão humana da ligação entre evidência visível, condição e conclusão. Erro operacional e indeterminação nunca agregados numa única “falha da IA”.

Medir chamadas, tokens, custo API separado do projeto, latência ponta a ponta (inclui validação/retentativas) e variabilidade entre repetições. Se preço indisponível, reportar tokens e custo desconhecido. Plano de repetições e tamanho amostral fica para piloto: estimar variância, custo e viabilidade antes de fixar n e R; todas as condições usam os mesmos casos e número R aprovado. Pares por caso/repetição, ordem de condições alternada/aleatorizada com seed registrada; sem escolher melhor resposta. Estatística posterior deve respeitar agrupamento por família/caso, não tratar repetições como projetos independentes.

Congelar antes do final: casos e famílias, views/fontes, referências revisadas, prompts, schemas, código/hash, modelo/versão, parâmetros, ferramentas, tetos/retentativas, R/n, métricas e critérios de exclusão. Caso final não pode ser variante numérica trivial de família já usada no ajuste. Separar desenvolvimento, piloto e final por famílias e documentos; impedir leitura dos finais por autores de prompts/motor durante ajuste. Os 36 e 34 conhecidos e seis DEV continuam desenvolvimento. Modelo de geração pode auxiliar autoria, mas gerador/motor não é juiz único: derivação manual, conferência por pessoa independente da implementação e revisão de domínio/orientador quando disponível. Agentes distintos não garantem independência. Registrar autores/revisores, conflitos, divergências resolvidas antes de ver previsões; nenhuma correção de referência para fazer o motor parecer correto.

Legado preservado com versões/rótulos históricos. As seis falhas e erro de ambiente do inventário não foram corrigidos ou reexecutados. Não misturar métricas de artefatos/entidades, respostas injetadas e novos desfechos; integração do baseline textual isolado exige tarefa posterior, nunca cópia silenciosa.

## 9. Exemplo didático completo — somente contrato, sem dataset

Todos os fatos a seguir são fictícios, criados para leitura desta especificação. IDs descritivos aqui facilitam a explicação; a implementação experimental usará IDs opacos. Não é amostra da etapa 2 nem previsão LLM coletada. As análises abaixo são respostas ilustrativas prescritas.

Na serialização, campos `execucao.estado` aceitam `ok|parcial|erro`; `requer_revisao` é decisão de validação, com processamento bloqueado e resultado epistêmico indeterminado quando necessário.

Fontes: F1 ficha de planejamento com liberações/durações e dependências; F2 orçamento fechado das quatro atividades; F3 contrato de apoio exclusivo do projeto; F4 aviso de fornecedor; F5 instrução técnica local de montagem. F1 declara entregas exaustivas; F2/F3 declaram todas as obrigações do escopo. Cada linha/tópico funciona como localizador neste exemplo.

Entidades: fornecedor V, componente X, atividades A (receber X), B (preparar carcaça), C (montar), D (testar), marco M (entregar). Pessoa P e área Q só têm `responsavel/pertence`, sem duração/custo temporal automático. Relações: V fornece X; A requer X (disponibilidade de X impõe liberação de A); A e B precedem C; C precede D; D precede M. A relação `RX={origem_id:A,destino_id:X,tipo:requer,fonte_refs:[F1.requisito]}` tem regra `TX={relacao_id:RX,operacao:disponibilidade_para_restricao,origem_atributo:disponibilidade,restricao_destino_id:RA_X,fonte_refs:[F1.requisito]}`. TX materializa em A a restrição RA_X e projeta X→A; não se presume que todo componente funcione assim. A também tem restrição RA_0 não antes de D0, preservada. Assim R_A=max(RA_0,RA_X); a tabela mostra o valor efetivo, não um campo gravável.

| Registro de F1 | Liberação base | Duração | Predecessores | Início/fim base |
|---|---:|---:|---|---|
| X disponibilidade | D2 | inaplicável | — | não é atividade |
| A | D2 | 1 | nenhum | D2/D3 |
| B | D0 | 5 | nenhum | D0/D5 |
| C | D0 | 3 | A e B | D5/D8 |
| D | D0 | 2 | C | D8/D10 |
| M | D0 | 0 | D | D10/D10 |

F2: parcelas A=R$1.000, B=R$500, C=R$1.500, D=R$1.000. F3: parcela AP=R$1.000 cobre apoio de D0 até D10 exclusivo (10 dias contratados a R$100/dia); extensão além dos 10 dias custa R$100/dia até M. Sem crédito por antecipação e sem outras incidências. Base completa: R$5.000 e término D10. Taxa de AP não se aplica a cada atividade.

Acontecimento E1 no D0, F4: “A inspeção do lote X foi reprovada. O fornecedor confirma que o lote substituto estará disponível no D6. Haverá cobrança única adicional de R$200 pela substituição, não incluída no orçamento; O lote substituto vem com laudo de equivalência técnica aceito pela engenharia; demais condições permanecem.” F4 identifica X/V e a obrigação A. O relato não contém o efeito final nem o caminho. Proposta interpretativa em X: substituir disponibilidade D2 por D6, evidência F4; adicionar obrigação única `SUB`=20.000 centavos, efeito canônico E1/substituicao. TX/F1 autoriza atualizar somente RA_X pela disponibilidade de X, preservando RA_0. Aumento de 4 dias é de disponibilidade, não duração nem acréscimo automático ao término final.

A regra local `RC={no_id:C,clausula:F5.procedimento,operacoes_permitidas:[confirmar manutenção de atributo,confirmar ausência de parcela adicional],atributos_alvo:[duracao,readequacao]}` é catalogada, mas sua aplicabilidade a este lote não vem preenchida: exige interpretação dos trechos visíveis. F5, disponível no contexto local de C: “Na montagem com lote substituto, se houver laudo de equivalência aceito pela engenharia, mantém-se o procedimento padrão de três dias, sem cobrança de readequação. Sem essa aceitação, a montagem deve aguardar definição técnica; não estimar duração nem custo de readequação.” A baseline usa lote original e duração padrão 3. Esta cláusula não entrega o atraso final: a LLM de C deve relacionar o efeito recebido (lote substituto) à condição documental de F4/F5. O contexto contém trechos originais, dados de A/B e referências, não um booleano `condicao_satisfeita` ou instrução de “manter resultado”. A validação de citações/estrutura é automática; a correspondência semântica continua auditável, como na seção 3.

| Nó / contexto recebido | Análise/decisão ilustrativa | Resultado vigente |
|---|---|---|
| V | Aviso identifica fornecedor, sem mudança de atributo temporal próprio | Inalterado verificado como entidade contextual; sem datas. Sem LLM extra. |
| X: F4 e regra TX/RX de F1 | LLM interpreta D6 como disponibilidade e R$200 como obrigação adicional única; validador verifica alvos/fontes/unidades | Disponibilidade D6; referência à parcela SUB; fato do lote substituto e trecho do laudo preservados no contexto causal de A e C. |
| A: X D6, RA_0=D0, duração 1 | TX atualiza RA_X=D6; R=max(0,6)=6, preserva RA_0 e carrega proveniência do lote/laudo; dispensa nova chamada | S=6,F=7, ΔF=4; SUB só referenciada, não adicionada novamente. |
| B: F1, nenhum efeito do evento | Reutilização baseline verificada, fora do ramo alterado mas necessária à convergência | S=0,F=5, ΔF=0; não é nó não avaliado. |
| C: A F7, B F5, lote substituto e trechos F4/F5 | **LLM local** interpreta que a aceitação do laudo satisfaz a condição da montagem; propõe manter duração padrão 3 e ausência de nova parcela de readequação, com F4.laudo/F5.procedimento. Validador aceita a operação catalogada e registra suporte a ser auditado; Python calcula FS. | S=max(0,7,5)=7,F=10, ΔF=2; custo local adicional de readequação zero sustentado (não soma uma parcela zero ao livro). |
| D: C F10, duração 2 | FS determinística | S=10,F=12, ΔF=2. |
| M: D F12 | FS determinística | S=F=12, ΔF=2. |
| AP (regra de custo, não tarefa) | F3 requer interpretar cobertura/ausência de crédito se não catalogadas; análise local de custo ligada ao marco confirma regra AP | 12−10=2 dias de extensão; efeito E1/AP = R$200. |

Para contratos, AP é parcela vinculada a M, não entidade temporal adicional. **Neste exemplo, F3 já está catalogada/validada**, logo AP é determinística e há exatamente **duas chamadas lógicas ilustrativas: X e C**, sem retentativa. A/D/M usam regras determinísticas; B é reutilizado após verificação; V/P/Q são contextuais, sem chamadas artificiais. Em outro caso que exigisse interpretar F3, a chamada local em M e seu consumo seriam registrados; isso não é necessário neste exemplo. As duas análises descritas são respostas prescritas para leitura do contrato, não chamadas realizadas. Em C, “manter duração” é resultado de interpretação condicionada ao efeito recebido, não dispensa de interpretação por o número permanecer 3.

Cálculo manual: A atrasou quatro dias, mas B já terminava D5; a convergência desloca C de D5 para D7. Os dois dias absorvidos não são subtraídos outra vez. Final D12−D10=**+2 dias**, não 4+2+2. Livro: base 500.000 centavos + SUB 20.000 + extensão AP 20.000 = **540.000 centavos (R$5.400)**; Δ=**40.000 centavos (R$400)**. Nenhum sucessor adiciona novamente SUB ou AP. Origens causais se repetem no rastro, não na soma.

Exemplos compactos coerentes com os contratos (campos de identificação comuns omitidos só nesta exibição):

- `AnaliseNo(X)`: proposta `substituir disponibilidade=6 dia_corrido`, refs `[F4.aviso]`, relação `[RX]`, regra `[TX]`, condições `lote_substituto_confirmado`; proposta `adicionar parcela SUB=20000 BRL_centavo`, origem `E1/substituicao`. Suporte depende de F4, não de confiança.
- `AnaliseNo(C)`: contexto A/B e F4.laudo/F5.procedimento; propostas `confirmar manutenção de atributo duracao=3 dia_corrido` e `confirmar ausência de parcela adicional readequacao`, regra_refs `[RC]` (fonte F5.procedimento), condição `laudo_equivalencia_aceito`, origens `[E1/lote_substituto]`; custo local adicional exato zero sustentado. Não propõe o delta final.
- `ResultadoNo(C)`: processamento calculado, execução ok, início exato 7, fim exato 10, delta_fim exato +2, predecessores_versoes `{A:1,B:1}`, analise_id `analise_C`, regras `[RC,FS]`, efeitos_custo `[]`, lacunas `[]`.
- `ResultadoFinal`: prazo completo/exato `{base:10,novo:12,delta:2}`, custo completo/exato `{base:500000,novo:540000,delta:40000}`, livro com IDs A/B/C/D/AP/SUB (AP final 120000), rastro da alteração de AP 20000 e de SUB 20000, execução ok. Livro final e deltas são duas visões das mesmas obrigações, não parcelas somáveis entre si.

Contraprovas de lacuna, sem gerar novos casos: retirando a aceitação do laudo de F4, C não pode assumir o procedimento padrão; F5 exige aguardar definição, deixando duração/custo de readequação e os desfechos dependentes indeterminados, mesmo que A continue terminando D7. Não confundir esse bloqueio semântico com erro operacional. Nas contraprovas seguintes o laudo continua aceito. Retirando a taxa de F3, prazo continua +2 exato; custo fica indeterminado com R$200 de alteração direta identificada, AP pendente, total novo null. Retirando a confirmação D6 de F4 (com os demais fatos preservados), não converter disponibilidade desconhecida em D2 nem atraso zero: prazo pode ficar indeterminado. Só afirmar direção final se houver limite que prove ultrapassar D5 de B. Retirando a cláusula que confirma custo adicional e mantendo só “cobrança R$200”, não concluir se valor já estava incluído: SUB exige revisão/indeterminação. Se uma futura evidência confirmar X disponível D4, mantendo o laudo aceito, A termina D5, C mantém D5 e o prazo zero seria sustentado pela convergência, mesmo havendo mudança local.

## 10. Aceitação futura e decisões de revisão

Critérios verificáveis para implementação posterior:

- Contratos rejeitam IDs sem resolução, unidade errada, enum inválido, referência de avaliação em input e zero com lacuna; ambos os adapters cruzam a mesma interface e identificam simulação.
- Agenda inclui B na convergência do exemplo, fecha dependências sem limite de profundidade e detecta ciclo; nenhum ramo ignorado vira inalterado sem prova. Resultado do exemplo: +2 dias e +R$400.
- Substituição D2→D6 afeta liberação, não duração. FS usa datas absolutas; antecipação respeita R e crédito contratual. Casos manuais de cadeia, convergência, zero, ausência de taxa e múltiplos caminhos ao mesmo custo devem ser conferidos independentemente.
- Livro deduplica obrigação, detecta colisão de ID e separa custo completo de parcial. AP custa uma extensão de dois dias, sem multiplicar atrasos locais.
- LLM não executa fórmula/código livre; proposta fora de catálogo e evidência contraditória não são aplicadas; validade estrutural não é rotulada automaticamente suporte semântico.
- Views B/H/T são inspecionáveis; parser não corrige baseline com motor. Falha API, saída inválida e teto excedido permanecem nos denominadores. Avaliador não é dependência do preditor.
- Logs permitem reproduzir contexto, revisões, decisões, custos/latência; arquivos de gabarito ficam fora do acesso dos adaptadores. Nenhum resultado legado é promovido a experimento novo.

Sequência preservada: após revisão desta proposta, etapa 2 produzirá **somente projeto mínimo e fontes/casos de desenvolvimento resolúveis manualmente**, incluindo orçamento fechado e regras com proveniência. Etapa 3 derivará grafo das fontes; etapa 4 implementará cálculo; etapas 5–8 integrarão interpretação, agenda, baseline/avaliador e observatório. Piloto, congelamento e final permanecem nas etapas 9–11. Aceitar esta especificação não equivale a autorizar lote pago nem congelar modelo/amostra.

Quatro decisões essenciais propostas ao usuário, com recomendação:

1. **Modelo v1:** aprovar dias corridos inteiros, BRL/centavos, planejamento no D0 e FS sem recursos compartilhados. Recomendação: sim; reduz ambiguidades e permite conferência manual.
2. **Experimento:** aceitar B/H como comparação de sistemas com assimetria declarada, sem ferramentas externas em B/T, e incluir T como controle complementar. Recomendação: sim; informar ganho da configuração sem atribuição exclusiva ao grafo.
3. **Custo/completude:** exigir escopo fechado e regras de incidência explícitas, permitindo prazo exato/custo indeterminado. Recomendação: sim; lacunas não podem virar zero ou total parcial virar completo.
4. **Referências finais:** reservar famílias inéditas e revisão humana independente da implementação antes de ver previsões. Recomendação: sim; se indisponível, reduzir alcance das conclusões e declarar validação autoral, sem chamar independente.

Demais escolhas rotineiras aqui propostas podem ser refinadas na revisão mantendo versões. Riscos: baseline com menos conhecimento pode abster-se mais; catálogo excessivamente completo pode reduzir o papel interpretativo da IA a extração trivial; catálogo insuficiente produz indeterminação; fechamento artificial de custo pode limitar validade externa. O projeto mínimo deve conter condições textuais que exijam interpretação real, sem entregar deltas/gabaritos, e exemplos de lacuna para evitar validação circular.

## 11. Revisão desta entrega

- [x] Objetivo central fiel: término final/custo total, não preço ou lista de documentos.
- [x] Cinco contratos e exemplo consistentes; entidades contextuais não viraram tarefas.
- [x] Revisão documental do coordenador recebida em 24/10/2026 e tratada: interpretação local em C além de X; requer/TX com projeção X→A; restrições de liberação por ID; inaplicável distinto; campos mínimos de Atividade e revisões de predecessores; seis quantidades finais; delta temporal novo menos base com política de crédito. Sem aprovação do usuário nesta revisão.
- [x] Comparação principal explicita assimetria de informação, chamadas e cálculo.
- [x] Indeterminação, zero sustentado, direção e erro operacional separados.
- [x] Contas conferidas com aritmética local simples; nenhuma suíte/API/modelo executado.
- [x] Etapa 0 registrada como aprovada; etapa 1 aguarda revisão; etapa 2 não iniciada.

Os ajustes atendem aos cinco pontos da revisão do coordenador e permanecem sujeitos à conferência dele e à revisão do usuário. Não alteram a conta principal (+2 dias, +R$400), não constituem aprovação do usuário e não substituem validação de domínio ou aprovação das quatro propostas.

## 12. Aprovação posterior e vigência — 24/10/2026

O usuário declarou: “Aprovo a etapa 1 e as quatro propostas. Pode iniciar a etapa 2 com um agente separado para criar o projeto mínimo e os cenários de desenvolvimento. Traga a entrega para revisarmos antes de avançar.” A aprovação abrange o modelo v1, a comparação B/H com assimetrias declaradas e T complementar, o fechamento de custos/completude e a reserva de famílias inéditas com revisão humana independente. Preservadas as correções do coordenador: interpretação em X/C, requer e projeção causal específica, restrições por ID, inaplicabilidade e custo temporal incremental. [Etapa 2](ETAPA_02_PROJETO_MINIMO.md) entregue como rascunho para revisão, sem iniciar etapa 3. Nenhuma escolha técnica foi modificada por esta nota.
