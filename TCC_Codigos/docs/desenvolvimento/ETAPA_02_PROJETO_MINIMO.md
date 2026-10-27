# Etapa 2 — projeto mínimo e cenários de desenvolvimento

24/10/2026, America/Sao_Paulo. **APROVADA pelo usuário em 24/10/2026, pela instrução “Avance para a próxima etapa”.** Etapa 1 e quatro propostas aprovadas pelo usuário nesta data. Etapa 3 entregue aguardando revisão; etapas 4–11 não iniciadas. O corpo histórico é preservado; consultar nota de vigência ao final. [Especificação aprovada](ETAPA_01_ESPECIFICACAO.md) · [Status](STATUS.md).

## Projeto e fronteira da entrega

Bancada Íris é um projeto mínimo inteiramente fictício; não representa fatos observados do Alfa histórico. Pacote: `TCC_Codigos/data/desenvolvimento/projeto_minimo_v1/`, com README/manifesto, `inputs/` e `referencias/` fisicamente separados. São sete entidades, quatro atividades produtivas e um marco, cinco parcelas, treze documentos primários fictícios, 25 trechos citáveis e oito cenários independentes. Não é benchmark independente nem conjunto final inédito.

A autoria dos documentos e dos gabaritos é do agente de dados da etapa 2. A conferência local usa fontes e aritmética simples, sem futuro motor ou LLM como juiz. O coordenador conferiu fontes, linha base e sete casos em 24/10/2026; a direção do custo de k_23d8 foi corrigida pelo autor após essa revisão. Conferência final dos ajustes e aprovação do usuário pendentes. Essa conferência não equivale à revisão humana independente exigida antes do experimento final.

Calendário aprovado: dias corridos inteiros, D0 e intervalos [início,fim); moeda BRL/centavos; planejamento prospectivo antes de executar; um aviso por rodada; FS0 sem ciclos ou disputa de recursos. Cada caso parte do snapshot v1.0 fixo: nenhum caso herda outro aviso. Não há variante de base.

## Linha base conferível

| Item | Fonte factual | Liberação / duração | Início / fim manual |
|---|---|---|---|
| Cartucho X | d_71ba L02 | disponibilidade D2; não atividade | inaplicável |
| A receber | d_71ba L03/L04 e d_aa83 L01 | max(piso0, X2) / 1 | D2 / D3 |
| B preparar | d_71ba L03/L04 | D0 / 5 | D0 / D5 |
| C montar | d_71ba L03/L04 e d_aa83 L02 | D0; após A e B / 3 | D5 / D8 |
| D testar | mesmas fontes | D0; após C / 2 | D8 / D10 |
| M entregar | mesmas fontes | D0; após D / 0 | D10 / D10 |

Orçamento d_482e L01: A R$1.000 + B R$500 + C R$1.500 + D R$1.000 + AP R$1.000 = **R$5.000**. AP cobre D0–D10 e cobra R$100/dia além de dez dias até M; incidência base zero e política sem_credito. Entregas/custos/requisitos fechados documentalmente; ausência de evidência de evento não é zero.

## Casos e conclusões de referência (fora dos inputs)

| Caso | Situação documental | Delta final dias | Delta total BRL |
|---|---|---:|---:|
| k_b731 | Substituto D4, aceite e garantia | 0 | 0 |
| k_09c2 | Substituto D6, aceite, troca R$200 | +2 | +400 |
| k_e168 | Substituto D2, aceite, taxa R$300 | 0 | +300 |
| k_547a | Substituto D6 em garantia, dispensa de AP até D12 | +2 | 0 |
| k_a92f | Alternativa suficiente D3 já selecionada/contratada e aceita | 0 | +150 |
| k_23d8 | Substituto D6 sem decisão de aceite | indeterminado | aumento sem magnitude exata; ≥200 |
| k_f04b | Preparo com duração 4 e crédito comercial explícito | −1 | −100 |
| k_8c65 | Substituto D6 aceito; aditivo de extensão sem preço definido | +2 | aumento sem magnitude exata; ≥200 |

As seis famílias obrigatórias estão cobertas pelas seis primeiras linhas; os extras verificam antecipação/economia com fonte e estados distintos por desfecho. Não se pretende diversidade estatística. A economia de k_f04b é crédito comercial, não devolução de AP. k_547a tem dispensa expressa; ignorar AP sem fonte seria incorreto. k_8c65 preserva base e substitui expressamente a taxa somente para a extensão do aviso; prazo continua exato, custo não. Os gabaritos completos com cronogramas, seis quantidades finais, contas e lacunas estão em `referencias/gabaritos.json` e `referencias/DERIVACAO_E_COBERTURA.md`.

## Interpretação e passagem à etapa 3

A montagem tem trabalho interpretativo real posterior ao componente: deve relacionar aceite específico do lote no aviso à cláusula condicional d_8c23. Existência de laudo não é aceite. Inputs não contêm flag de condição satisfeita, impacto por nó, família ou delta final. O caso sem aceite não recebe outro aviso como contexto.

As fontes relatam dependências; esta entrega não produz grafo operacional nem objetos de arestas. Etapa 3 derivará relações e projeção específica do requisito atividade→componente para disponibilidade componente→restrição da atividade; preservará o piso por ID e criará restrição derivada distinta. Deve normalizar os registros autorais para os cinco contratos, criando catálogos com proveniência sem preencher a aplicação das condições dos avisos. AP é obrigação temporal única vinculada a M, nunca atividade ou custo por caminho.

Os arquivos têm rótulo de pacote pré-normalização: **não se afirma conformidade executável completa com EstadoProjeto**. Não foi necessário alterar decisões aprovadas. Aditivos expressos são documentos de cenário a validar nas etapas posteriores, não autorização para atualização automática de qualquer contrato.

Destinação documental: quatro documentos comuns, ficha relacional d_aa83 para H/T e um aviso por caso. Contratos e avisos comuns contêm vínculos inerentes ao seu significado. Futuras views devem inventariá-los e usar seleção positiva, sem alegar igualdade B/H. `inputs/fontes.json` é índice e não pode ser enviado inteiro; README/manifesto/docs/referencias ficam fora do preditor. Ainda não há serializadores de condição ou auditoria de suporte por view.

## Critérios verificados e limitações

JSON/IDs/unidades, parcelas, referências literais e arquivos, soma base, datas/durações e todos os oito desfechos foram conferidos com script temporário e contas manuais independentes. Convergência usa máximo; obrigações e incidência de AP entram uma vez. Verificados avisos independentes, mudanças expressas, vigência por caso e ausência de campos expected_* e de respostas finais nos inputs. Detalhes em `referencias/VERIFICACAO.md`; hashes do pacote em `referencias/hashes.json`.

Essas verificações não comprovam desempenho de modelo ou sustentação de cada view. Não há casos finais, famílias inéditas, revisão independente, extensão prévia na base ou política de crédito temporal exercitada; isso fica para trabalho posterior. Nenhuma suíte histórica foi executada. Não houve API paga, credenciais, instalação, commits, integração de código textual, grafo/motor/LLM/UI ou notebook novo. Etapa 3 permanece não iniciada; próxima ação é revisar esta entrega.

## Ajustes da revisão documental — 24/10/2026

k_23d8: prazo segue indeterminado, mas custo passa a direcao/aumento, com total e delta exatos null. d_482e L02/L03 preserva parcelas fixas e veda presumir créditos; d_f730 L01 acrescenta R$200 e mantém demais condições; d_59c1 L03 impede economia de apoio por antecipação. Extensão/readequação são acréscimos não negativos no modelo aprovado, sem fonte de redução compensatória. Logo Cnovo≥R$5.200 e delta≥R$200; não há valor total exato. Corrigida a antiga abstinência genérica para direção do custo, antes de qualquer previsão e sem modificar os fatos.

Descrições de parcelas no input agora usam nomes humanos das fontes, preservando IDs e valores. Conferidos somente arquivos afetados, consistência das referências/contagens e hashes; fontes, eventos e sete demais conclusões preservados. Conferência final do coordenador, aprovação do usuário e revisão humana independente pendentes. Etapa 3 não iniciada.

## Vigência da transição para etapa 3 — 24/10/2026

Após revisar a entrega da etapa 2, o usuário declarou “Avance para a próxima etapa”. Isso registra a etapa 2 como **APROVADA pelo usuário** e autoriza somente a etapa 3. Menções históricas a aprovação pendente e etapa 3 não iniciada ficam superadas por esta nota, preservando os achados e a distinção entre aprovação do usuário, conferência autoral/documental e revisão humana independente (ainda pendente).

[Etapa 3 — grafo e dependências](ETAPA_03_GRAFO_DEPENDENCIAS.md) entregue aguardando revisão do coordenador e usuário: sete entidades, seis relações semânticas, cinco arcos causais, uma regra de transferência, uma local e uma de custo. Snapshot etapa 2 preservado; baseline D10/R$5.000 declarada. Validador stdlib passou e rejeitou seis contraprovas. Nenhum motor/LLM/views implementado. Etapas 4–11 não iniciadas; não avançar automaticamente.
