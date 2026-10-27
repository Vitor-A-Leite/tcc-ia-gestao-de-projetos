# Etapa 0 — estado atual e base técnica

Data: 24/10/2026 (America/Sao_Paulo). **APROVADA pelo usuário em 24/10/2026.** Nota posterior ao inventário: [etapa 1 elaborada, aguardando revisão](ETAPA_01_ESPECIFICACAO.md); etapas 2–11 não iniciadas. Os resultados abaixo são o registro histórico da etapa 0. Inventário e recomendação, sem correções ou contratos novos. Consulte [plano aprovado](PLANO_MESTRE.md) e [status](STATUS.md).

## 1. Versão, escopo e integridade

- Worktree executor: `/Users/vaugusto/.codex/worktrees/8f4c/TCC`.
- Pasta principal: `/Users/vaugusto/Desktop/Faculdade/TCC`, branch `main`.
- Ambos estavam no commit `ebcc16c019793ceab2493649c0051a4d571fc8c2`; executor em HEAD destacado (`git branch --show-current` vazio).
- Início: nenhum arquivo rastreado modificado nos dois locais. Havia arquivos pessoais e imagem não rastreados; somente seus nomes foram observados em `git status`, sem ler seus conteúdos.
- Não foram encontrados AGENTS.md pela busca nos projetos e nos ancestrais consultados do executor. Não houve alteração de código, dados, gabaritos, notebooks, resultados históricos ou configurações.
- Mudanças desta entrega: somente os três Markdown em `TCC_Codigos/docs/desenvolvimento/`. A cópia à principal é restrita a esses documentos, com recusa de sobrescrita e comparação de conteúdo.
- Skill graphify consultada. Não existe `graphify-out/graph.json`; o Python padrão não importa graphify. Embora exista executável no PATH, não se construiu um grafo: a autorização limita esta entrega a documentos e proíbe instalação. O inventário usa leitura direta, sem inferir relações ausentes.

Histórico recente observado: `ebcc16c` registra validação e pendências; `3aeface` adiciona avaliador V2.2 e observatório; `a242901` sincroniza versão local; `8c0204b` declara estabilização do baseline e separação piloto/teste. Mensagem de commit e documentação não substituem verificação do conteúdo.

## 2. Arquitetura realmente disponível

| Componente | Evidência local e comportamento | Limite para o objetivo aprovado |
|---|---|---|
| Notebooks raiz | `TCC_Baseline_LLM.ipynb` (36 células), `TCC 03_Arquitetura_Hibrida_com_API.ipynb` (42), `ProjetoTCCv01.ipynb` (30) | Pontos de entrada históricos; não representam o novo experimento concluído. |
| Modelos | `TCC_Codigos/src/tcc_agent/models.py`: Event e ImpactResult | Evento e listas/rastro de impactos; não resultado geral de cronograma/custo total. |
| Grafo | `src/tcc_agent/graph.py`: adjacência direcionada e BFS, visited, primeiro caminho por alvo, profundidade padrão 4 | Alcançabilidade não equivale a impacto causal nem a cálculo de cronograma. Não consolida todos os caminhos convergentes. |
| Híbrido atual | `src/tcc_agent/pipeline.py`: seeds de entidades, BFS max_depth=4 e regras; informational retorna vazio | Uma interpretação LLM anterior à propagação; não análise LLM por nó nem cálculo geral de prazo/custo. |
| Regras documentais | `src/tcc_agent/rules.py`: artefatos por tipo de evento | Pode servir à saída documental, mas não resolve os dois desfechos centrais. |
| Baseline/avaliação legados | `src/tcc_agent/baseline.py`, `evaluate.py`, notebooks, `scripts/run_pilots.py` | Tipos, entidades e artefatos são métricas intermediárias; protocolo e notebooks têm divergências. |
| Evidências V2 | `src/tcc_agent/evidence_assessment.py` | Evidências, condições e indeterminação; limitação explícita para convergência de predecessores. |
| Evidências V2.2 | `src/tcc_agent/scoped_evidence.py` e `docs/protocolo_evidencias_v2_2.md` | Distingue start/delivery/progress_variance/finish/duration/availability, escopo, base de dias e net_cost; não é motor geral de projeto. |
| Referências | `src/tcc_agent/reference_review.py`, `data/reference_sets/alfa_schedule_cost_v2_1_draft.json`, `scripts/audit_schedule_cost_references.py` | Material de auditoria e referências autorais; não presumir validação independente. |
| Runtime local | `src/tcc_agent/local_runtime.py`, `scripts/run_local.py`, `cli.py` | Localiza repositório; carregamento real de ambiente existe, mas não foi acionado sobre credenciais nesta tarefa. |

Caminhos abreviados `src/`, `data/`, `docs/`, `scripts/` na tabela são relativos a `TCC_Codigos/`.

O motor V2.2 só autoriza transferência sob hipóteses explícitas. Em `EvidenceEngine._model`, vários predecessores produzem lacuna `per_predecessor_schedule`; ciclos/revisitas não são solução de cronograma. A regra de custo diário exige `net_model_complete`; não se deve transformar cálculo local em custo total do projeto sem um modelo de composição. Essas proteções são reaproveitáveis, mas não substituem a implementação futura.

## 3. Dados e natureza dos resultados

Contagem atual por leitura de JSON: `data/project_graph.json` tem **40 nós e 65 arestas**; `data/scenarios_ground_truth.json` tem **36 cenários**; `data/scenarios_development_pilot.json` tem **6 DEV**; `data/evidence_protocol_v2_2_cases.json` tem **34 casos**. O nome Alfa e o termo histórico “grafo real” designam o projeto de referência legado; não comprovam dados observacionais de um empreendimento real.

| Evidência | Natureza e leitura correta |
|---|---|
| `outputs/validacao_local_20261018_170009/05_pilotos_reais/summary.json` | Piloto histórico marcado real: seis casos por condição. Baseline acurácia tipo 1,0/F1 artefatos 0,8421; híbrido 0,8333/0,88. Híbrido F1 entidades 0,3571. Resultados mistos, sobre desfechos intermediários. Não medem erro de término ou custo total. |
| Pasta `05_pilotos_reais/` e contexto histórico recebido | 12 chamadas históricas reportadas (6 por condição); o summary confirma os 12 registros previstos, não foi feita reconciliação forense com cobrança/provedor nem nova chamada. |
| `outputs/validacao_local_20261018_170009/03_pilotos_simulados/` e `04_simulacao_completa/` | Simulações, inclusive 36 casos. Validam execução, não desempenho LLM. |
| `outputs/protocolo_v2_2_validacao_20261022/LEIA_PRIMEIRO.md` | 34 casos hipotéticos, 92 perguntas por condição/184 total. 68 registros demonstrativos com respostas injetadas pelo motor; 118 testes históricos. Não são previsões de IA ou revisão independente. |
| `outputs/protocolo_v2_2_validacao_20261022/contraprova_previsoes_sinteticas.jsonl` e subpasta `contraprova_troca_inicio_termino/` | Contraprovas sintéticas com erro deliberado; não novas coletas empíricas. |
| `outputs/protocolo_v2_*` | Demonstrações, ingestão e validação de protocolos anteriores; preservar proveniência e versão. Não agregar automaticamente à avaliação final. |
| `outputs/validacao_publicacao_20261024/summary.json` | Registro histórico: 130 testes, 124 aprovados, seis falhas, zero API; commit testado `3aeface...`. Não é a execução atual abaixo. |

Não foi localizado/confirmado experimento final completo com coleta LLM e desfechos de prazo final/custo total. Não se conclui inexistência universal: o levantamento cobre os arquivos pertinentes locais, sem executar notebooks nem consultar conta externa.

Os 36 originais e 34 adicionais já foram conhecidos no desenvolvimento. A existência de seis DEV não recupera ineditismo dos conjuntos expostos. Gabaritos e referências autorais precisam de revisão independente de previsões e do motor.

## 4. Observatório existente

`TCC_Codigos/visualizacao/observatorio3d/` contém a interface e `TCC_Codigos/scripts/serve_graph3d.py` o servidor. Em `execute`:

- Modo reference injeta `expected_*` do cenário, deixando claro que não é resposta IA.
- Modo real chama `call_interpreter_llm` uma vez e passa o evento à mesma pipeline BFS; exige habilitação de API.
- Emite input, processing, interpretation, transfer e result, com NDJSON (JSON por linha); persiste execuções JSON. A interface oferece consulta/replay.
- Não importa o motor V2.2. Não exibe ainda análise LLM, regras de cálculo e consolidação por nó do software pretendido.

É uma base de visualização/rastreio a adaptar, não evidência de que o novo fluxo está implementado. Servidor e modo real não foram iniciados nesta tarefa.

## 5. Testes atuais e ambiente

Python padrão `/Applications/Xcode.app/Contents/Developer/usr/bin/python3`: **3.9.6**, sem pytest; runner requer Python >=3.10. Usado runtime já instalado `/Users/vaugusto/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3` (**3.12**), sem instalar pacotes.

Comando executado uma vez, na raiz do worktree:

```sh
/Users/vaugusto/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 TCC_Codigos/scripts/test_offline.py > /private/tmp/tcc_etapa00_tests.log 2>&1
```

Resultado: **130 testes, 123 aprovados, seis falhas e um erro**. O processo de testes retorna 1. O runner bloqueia `socket.socket`; mocks impedem API real. Os testes de .env usam somente arquivos fictícios temporários. Nenhum .env/chave real foi lido. O log integral é temporário no executor; os diagnósticos duráveis estão abaixo (não foi incorporado às saídas históricas).

```
ERROR: test_real_adapter_with_simulated_api (test_observatorio3d.ObservatoryTests.test_real_adapter_with_simulated_api)
FAIL: test_all_reviewed_labels_use_catalog_and_explicit_participant_roles (test_notebook_baseline.BaselineV2Tests.test_all_reviewed_labels_use_catalog_and_explicit_participant_roles)
FAIL: test_hybrid_example_and_pilot_also_keep_official_cases_out (test_notebook_baseline.BaselineV2Tests.test_hybrid_example_and_pilot_also_keep_official_cases_out)
FAIL: test_notebook_example_and_pilot_send_only_dev_ids (test_notebook_baseline.BaselineV2Tests.test_notebook_example_and_pilot_send_only_dev_ids)
FAIL: test_snapshot_and_original_functions_have_not_drifted (test_notebook_baseline.BaselineV2Tests.test_snapshot_and_original_functions_have_not_drifted)
FAIL: test_v2_prompt_has_general_definitions_without_scenario_answers (test_notebook_baseline.BaselineV2Tests.test_v2_prompt_has_general_definitions_without_scenario_answers)
FAIL: test_zip_matches_current_notebook (test_notebook_baseline.BaselineV2Tests.test_zip_matches_current_notebook)
```

As seis falhas correspondem a: revisão de rótulos (`C_MOTOR` versus `SUP_MOTOR`); seleção de exemplo/piloto híbrido; piloto baseline ainda S001/S003/S007/S009/S024/S035 versus DEV001–DEV006; hashes de snapshot; definição esperada do prompt; ZIP versus notebook atual.

O erro adicional é `ModuleNotFoundError: No module named 'openai'` em `test_real_adapter_with_simulated_api`: o teste precisa importar o pacote mesmo com API simulada. É limitação do runtime usado, não nova falha demonstrada da lógica de cálculo. Não foi contornado nem omitido do denominador.

O relatório histórico `outputs/validacao_publicacao_20261024/LEIA_PRIMEIRO.md` registra reprodução das mesmas seis falhas em cópia limpa de `origin/main a242901`. Essa reprodução em commit antigo não foi repetida agora. A execução atual confirma as seis categorias e mostra o erro de ambiente; portanto, não declarar “124 passaram agora” nem “suíte verde”.

## 6. Documentação conflitante

`docs/baseline_v2_methodology.md` afirma que ambos os notebooks usam DEV001 e DEV001–DEV006; o teste atual do baseline encontra os seis IDs oficiais acima e o teste híbrido também falha. O mesmo documento descreve revisão de rótulos e snapshot técnico; rótulos atuais, prompt, hashes e ZIP não satisfazem os testes dessa definição. `README.md` e o README de códigos apresentam instruções e resultados de momentos diferentes; a ressalva histórica de exposição do conjunto oficial deve acompanhar qualquer comparação.

O plano mestre desta entrega define a direção futura e não reclassifica o legado como implementação do plano. Resolver divergências requer decisão e tarefa posterior autorizada, preservando registros antigos. Nenhum documento legado foi editado para eliminar inconsistências.

## 7. Condição de relações textuais isolada

Worktree acessível: `/Users/vaugusto/.codex/worktrees/8cc4/TCC`, chat de origem informado `01a17009-b97d-7ca1-8724-05b441526e6a`. `git status --short` confirma README modificado e quatro arquivos novos pertinentes:

- `TCC_Baseline_Relacoes_Textuais.ipynb`;
- `TCC_Codigos/src/tcc_agent/text_relations.py`;
- `TCC_Codigos/docs/baseline_text_relations_v1.md`;
- `TCC_Codigos/tests/test_text_relations.py`.

Leitura do módulo confirma whitelist de evento e catálogo id/name/type, relações source/type/target completas em JSONL, sem executar BFS para produzir a previsão. A documentação registra cinco testes novos aprovados e suíte 128/135 (seis falhas e um erro por openai ausente); esse resultado é histórico do outro executor, não repetido aqui. Não houve experimento real nessa implementação segundo seu relatório.

Os quatro arquivos estão ausentes da principal e deste worktree na inspeção; não foram copiados. Trata-se de controle complementar de conhecimento disponível, ainda orientado às saídas legadas, e não substitui baseline principal nem motor prazo/custo. Maior contexto, regras e execução diferentes impedem atribuir diferenças exclusivamente à representação.

## 8. Recomendação de base e reaproveitamento

Recomenda-se `ebcc16c019793ceab2493649c0051a4d571fc8c2` como **base de trabalho identificada**, comum à principal e ao executor, pois reúne runtime local, protocolos, testes e observatório, com pendências explícitas. Não é baseline científico congelado nem versão integralmente validada. Não escolher o worktree textual como base silenciosamente; sua integração futura deve ser revisada separadamente.

| Destino | Elementos e motivo |
|---|---|
| Reaproveitar | Organização `src/tcc_agent`, carregamento local, grafo/IDs como material conhecido, logs e persistência, bloqueio de rede em testes, fixtures e rastreabilidade; preservar históricos. |
| Adaptar | Contratos Event/ImpactResult; evidências/indeterminação V2.2; grafo para dependências válidas e múltiplos caminhos; avaliação para prazo/custo; observatório por nó; baseline sob contrato comum; condição textual se aprovada. |
| Novo | Projeto mínimo com fontes de cronograma/custo/calendário, cálculo geral de término e custo total, análise LLM por nó, coordenação de predecessores, consolidação sem duplicação causal, casos finais independentes e protocolo experimental congelado. |

Não se presume que reutilizar BFS ou o motor local resolva convergência, paralelismo ou custo causal único. Testes existentes são úteis como proteção do legado, mas a futura aritmética terá de ser conferida independentemente.

## 9. Pontos para decisão na etapa 1 — apenas pauta

Definir os cinco registros do plano, marco final e custo total; calendário/moeda/unidades; fontes comuns e relações derivadas; hipóteses e limites do primeiro caso; indeterminação versus zero; propagação/convergência e origem causal; validação de mudanças propostas; orçamento e falhas da IA; equivalência das perguntas e assimetria de conhecimento; métricas e denominadores; separação dos conjuntos e revisão de domínio. Decidir tratamento das divergências legadas e eventual uso da condição textual, sem fazer ajustes para favorecer resultados.

Não há contratos finais, parâmetros de calendário, novos dados, arquitetura definitiva ou seleção de modelo nesta entrega. Naquele encerramento, a etapa 1 dependia da revisão desta etapa; a aprovação posterior está registrada no cabeçalho.

## 10. Reprodução do inventário sem segredos

Na raiz do projeto:

```sh
git status --short
git branch --show-current
git rev-parse HEAD
git log -5 --format='%h %s'
rg --files TCC_Codigos/src/tcc_agent TCC_Codigos/docs TCC_Codigos/tests TCC_Codigos/scripts
```

Contagens podem ser reproduzidas sem executar notebooks:

```python
import json
from pathlib import Path
base = Path('TCC_Codigos/data')
g = json.loads((base / 'project_graph.json').read_text())
print(len(g['nodes']), len(g['edges']))
for name in ['scenarios_ground_truth.json', 'scenarios_development_pilot.json']:
    print(name, len(json.loads((base / name).read_text())))
c = json.loads((base / 'evidence_protocol_v2_2_cases.json').read_text())
print(len(c['cases']))
```

Para inventariar a condição isolada: `git -C /Users/vaugusto/.codex/worktrees/8cc4/TCC status --short` e ler somente os quatro arquivos pertinentes acima e o diff de README se necessário. Não executar notebook/runner de modo real, nem carregar .env.

## 11. Limitações e aceitação da entrega

Levantamento estático e uma suíte offline; sem nova coleta IA, auditoria de conta externa, renderização/execução integral de notebooks, inspeção de conteúdo pessoal ou certificação científica dos gabaritos. O inventário confirma os componentes e limites centrais, a base comum, as contagens e falhas atuais, a natureza dos resultados e a localização das mudanças isoladas. Isso conclui tecnicamente a etapa de consolidação; a revisão estava pendente ao encerrar o inventário. Aprovação posterior registrada no cabeçalho; nenhuma etapa seguinte havia sido executada naquele encerramento.
