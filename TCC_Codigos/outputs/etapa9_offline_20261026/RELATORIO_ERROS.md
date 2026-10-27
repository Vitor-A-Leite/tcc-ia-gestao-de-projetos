# Relatório de engenharia — 26/10/2026, America/Sao_Paulo

**OFFLINE/PRESCRITO/SEM LLM REAL.** Lote vigente: `lote_consolidado/`. `lote/` é a primeira rodada exploratória do runner, anterior à correção de denominadores; `lote_final/` é rodada intermediária. Não somar rodadas/reexecuções como novos cenários ou repetições científicas. Nenhuma demonstra desempenho de IA. A única correção de módulo preexistente foi a lista de tipos em `condicoes/views.py`.

## Achados e correções

| Categoria | Evidência | Tratamento e contraprova |
|---|---|---|
| Dados/grafo→serialização | Primeiro aviso Nácar calculou +2/+15000, mas `montar_views` levantou `Endpoint/tipo inválido` na relação responsável | Adicionados `responsavel` e `pertence` à lista v1 já normativa. Testes mostram relação presente em H/T, ausente como arco causal; tipo inventado continua rejeitado. Não foi retirada a relação para contornar o erro. |
| Avaliação/denominador do runner novo | Revisão identificou lista formada só após sucesso e acesso direto a deltas possivelmente ausentes | Plano normal anterior às execuções. Falta de fixture/JSON malformado/exceção inesperada guarda slot, motivo e hash possível; continua casos independentes. Testes N_H=15 e casos seguintes preservados. Catálogo global indisponível produz erro de lote com N desconhecido e nenhum resumo fictício. |
| Isolamento de fases | Contraprovas originalmente estavam no mesmo bloco da execução normal | Fase isolada; exceção nela não substitui k_98f3. Plano de 12 contraprovas salvo antes das execuções; indisponibilidade fica nos 12 slots próprios. Teste dedicado preserva normal −2/0 e N15. |
| Diagnóstico de prontidão | Revisão identificou aprovação false/vazia e requisitos removidos potencialmente tratados como completos | Conjunto obrigatório de requisitos; modelo não vazio; configuração objeto; orçamento positivo; aprovação declarada explicitamente verdadeira, identificada e vinculada ao hash do plano. Contraprovas passam. JSON autoafirmado não prova aprovação humana, execução ou suporte. |
| Suporte semântico | Fonte de k_98f3 diz duração1; proposta injetada duração9 é recusada pela igualdade prescrita, mas passa por callback deliberadamente permissivo | Limitação exposta, **não corrigida com falsa auditoria**. Sem resolver suficientemente válido não há H real apto. Caso permissivo produz indevidamente +6 dias/+45000 centavos; hashes/citações são válidos, suporte não é. Proposta metodológica revisável no pacote real. |
| Matemática | Restrição positiva/dupla convergência/incidência base/centavos/deduplicação | Nenhum erro novo identificado nos sete avisos prescritos; conformidade com referências autorais e contas manuais, não validação independente ou acurácia de IA. Motor permaneceu inalterado. |
| Interpretação real | Nenhuma chamada a modelo | Não mensurada; não atribuir falhas injetadas ou acertos prescritos a modelos. |
| Ambiente de teste | Primeira regressão etapa 8 bloqueou bind em127.0.0.1 no sandbox | 13 testes passaram e setup HTTP falhou por PermissionError; log preservado. Reexecução autorizada com porta temporária local:16/16 passaram. Nenhum servidor anterior foi encerrado. |

Na primeira autoria dos testes9, duas asserções presumiam envelope mínimo exato e presença de delta em erro. A implementação vigente adiciona proveniência e pode omitir quantitativos quando não houve resultado. Corrigidas as asserções para conferir estado/erros e ausência sem zero; nenhum gabarito ou contrato foi alterado. Resultado exploratório:19 testes,1 falha+1 erro; a rodada final tem27 aprovados. Não se apagaram os resultados exploratórios apresentados nas ferramentas.

## Denominadores observados no lote consolidado

**Normais H: N=15**, oito Íris preservados e sete Nácar. 12 `ok`,3 `parcial`,0 erro operacional. Parciais por lacuna legítima: k_23d8, k_8c65, k_d307; seus resultados conhecidos/direcionais e limites continuam nos artefatos. Prazo:13 exatos/15 e2 indeterminados/15; custo:12 exatos/15 e3 direcionais/15. Essas contagens descrevem saídas de **fixtures prescritas**, não acurácia nem cobertura de IA. B/T:0 runs normais executados;45 views produzidas. Não há MAE ou placar B/H/T neste lote.

**Contraprovas: N=12**, separado do normal. H/orquestração:8 slots (5 parciais,2 erros,1 ok sob política deliberadamente falsa). B:2 erros; T:2 erros. Nas quatro contraprovas globais foram chamadas funções mock, sem rede/provedor; contagem de transporte mock=1 por slot. Tokens do mock JSON são números injetados de teste, e timeout sem medição mantém tokens desconhecidos. **Chamadas API reais:0.** Custo real de API:nenhum gasto nesta entrega.

| Contraprova | Condição/fronteira | Categoria | Resultado |
|---|---|---|---|
| limite | H/orquestração | teto de análises0 | parcial, sem delta exato |
| sem_resolver | H/orquestração | suporte externo ausente | parcial, sem delta exato |
| sem_fechamento | H/orquestração | cobertura não declarada | parcial, sem delta exato |
| obsoleto | H/orquestração | contexto/hash incompatível | erro de integração, sem zero |
| valor_sem_suporte | H/orquestração | proposta9 em vez de1 | parcial por política prescrita, não auditoria automática |
| resolver_permissivo | H/orquestração | callback propositalmente falso | ok operacional, previsão sem suporte; limitação conhecida |
| ciclo | H/orquestração | ciclo FS injetado | erro de integração, quantitativos podem estar ausentes |
| unidade | H/orquestração | unidade monetária em duração | parcial, proposta inválida não aplicada |
| B_json_invalido / T_json_invalido | Global mock | JSON inválido | erro saida_invalida, uma tentativa cada |
| B_timeout / T_timeout | Global mock | timeout | erro timeout, sem retry/medição inventada |

As contraprovas H chamam a fronteira de orquestração diretamente, não simulam envelope experimental H normalizado. Categorizá-las como H nesta tabela só indica o subsistema exercitado. Não entram no avaliador científico nem no denominador dos15 avisos. O único `ok` não é sucesso semântico: é uma demonstração de dependência da política externa. Testes de regressão do avaliador preservam separadamente denominadores, falhas, limites e interseções pareadas.

## Proveniência e reprodução

Cada slot normal tem catálogo/versão, identidade, hash dos bytes efetivamente lidos de base, fontes, snapshot, fixture, evento e view no envelope H, código e origem. Arquivo ausente guarda hash null e erro; JSON malformado guarda hash dos bytes, mesmo sem objeto. O runner não consulta referências. Cada contraprova conserva saída bruta/envelope quando disponível e hashes dos objetos injetados, configuração e descrição da mutação; código versionado por hash permite reproduzi-la. Outputs são destinos, não inputs do preditor.

`plano_slots.json` e `plano_contraprovas.json` precedem a execução; `resumo.json` mantém o N planejado. Testes de falta de fixture/erro inesperado e fase de contraprovas usam diretórios temporários e não alteram dados originais. `integridade_inicial.json` capturou337 arquivos anteriores. `integridade_final.json` confere a preservação e registra exceções intencionais: views, STATUS e PLANO_MESTRE. Sem ajuste de referência após previsão, limpeza, commit/push/PR ou chamadas externas.
