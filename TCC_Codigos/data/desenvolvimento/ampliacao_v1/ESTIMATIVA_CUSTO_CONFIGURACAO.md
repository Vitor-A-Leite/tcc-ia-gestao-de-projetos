# Decisões, custo do lote completo e configuração local — 26/10/2026

Vigência desta continuação da etapa 9: supera somente as pendências de decisão metodológica e escolha de modelo nas propostas anteriores. **Nenhuma chamada real foi feita; integração e gasto continuam não autorizados nesta continuação. Etapas 10/11 não iniciadas.** Fontes oficiais e preços abaixo foram consultados pelo coordenador em 26/10/2026 e fornecidos ao executor; não houve nova consulta externa neste registro.

## Decisões aprovadas pelo usuário

1. Preservar as previsões originais sujeitas às verificações operacionais do código e auditar posteriormente seu suporte nas fontes. Contabilizar interpretações/conclusões erradas sem corrigir manualmente a previsão. Isso aprova a alternativa metodológica de previsão original com auditoria posterior; não transforma estrutura, citação ou hash em comprovação semântica. Saídas inválidas, lacunas e erros operacionais continuam nos denominadores. Registrar proposta, decisão operacional e suporte auditado separadamente, conservando resposta bruta. Não é autorização para `resolver=lambda:True`, aplicar operação fora de catálogo, consultar gabarito durante predição ou reparar conteúdo seletivamente.
2. **Modelo do experimento: `gpt-6-luna`, `reasoning.effort="high"`, Responses API**, para B/H/T. Esta escolha não altera o modelo do agente executor. Modelo/configuração ainda precisam ser ligados ao transporte real, manifesto, hashes e logs. A [página oficial do modelo](https://developers.openai.com/api/docs/models/gpt-6-luna) informa suporte a High.

Essas decisões estão aprovadas; a implementação da política operacional/seleção/fechamento, transporte, limites e runner real ainda não existe. A revisão das referências/inferibilidade e auditoria continua necessária. **Não houve aprovação financeira nem aprovação de execução do lote.**

## Uma execução total solicitada = um lote completo

Para esta estimativa, “execução total” significa **15 casos × B/H/T × 2 repetições = 90 execuções individuais**, até **300 chamadas**: B=30, T=30, H≤240 (8 por run H). Uma chamada é diferente de um run H e do lote completo. Entrada≤16.000 tokens por chamada, sem retry, sem ferramentas/serviços pagos adicionais. Normalização dos inputs autorais permanece estrutural, sem LLM adicional; interpretação de relatos livres exigiria outra decisão e contagem.

A [tabela oficial de preços Standard](https://developers.openai.com/api/docs/pricing), contexto curto, informa entrada US$0,10/M, saída US$0,50/M, entrada em cache US$0,01/M; escrita30m US$0,125/M e escrita12h US$0,25/M. Preços são de API, separados dos custos dos projetos fictícios. Não há taxa de câmbio adotada nem conversão para BRL.

Conforme o [guia de raciocínio](https://developers.openai.com/api/docs/guides/reasoning), tokens de raciocínio são cobrados como saída e `max_output_tokens` abrange **raciocínio + resposta visível**. A reserva inicial de pelo menos25.000 recomendada pelo guia é orientação de planejamento, não consumo esperado nem garantia de resposta completa. O limite histórico de2.000 pode truncar raciocínio/resposta; ele não significa2.000 tokens visíveis mais raciocínio gratuito.

| Cenário de orçamento | Entrada máxima do lote | Saída total máxima | Base sem escrita de cache | Conservador: toda entrada como escrita30m | Comparação: toda entrada como escrita12h |
|---|---:|---:|---:|---:|---:|
| Limite histórico2.000/chamada | 4,8M | 0,6M | US$0,78 | **US$0,90** | US$1,50 |
| Alternativa High25.000/chamada, não aprovada financeiramente | 4,8M | 7,5M | US$4,23 | **US$4,35** | US$4,95 |

Contas: 4,8×0,10+0,6×0,50=0,78;4,8×0,125+0,6×0,50=0,90;4,8×0,10+7,5×0,50=4,23;4,8×0,125+7,5×0,50=4,35;4,8×0,25+7,5×0,50=4,95. O cenário12h com2k resulta4,8×0,25+0,6×0,50=1,50.

O [guia de prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) informa cache implícito habilitado por padrão e escrita default30m a1,25×entrada em GPT5.6+. Assim, **US$4,23 e US$0,78 não são tetos conservadores do comportamento padrão**. O orçamento básico sem escrita serve só de referência. A proposta atual considera **default30m** e, conservadoramente, toda entrada cobrada como escrita, sem descontar possíveis economias de reutilização.12h fica apenas como comparação; não foi escolhida. Desligar cache local de respostas entre runs não desliga automaticamente cache de prompts do provedor.

Decomposição no cenário25k, por limite de300 chamadas:

| Unidade/condição | Base sem escrita | Conservador30m |
|---|---:|---:|
| Uma chamada de16k entrada+25k saída total | US$0,0141 | US$0,0145 |
| B:30 chamadas | US$0,423 | US$0,435 |
| T:30 chamadas | US$0,423 | US$0,435 |
| H:até240 chamadas | US$3,384 | US$3,480 |
| Lote completo | US$4,230 | US$4,350 |

**Reserva sugerida: US$5, ainda não aprovada**, antes de impostos/câmbio e cobranças extras. É suficiente apenas sob as hipóteses declaradas: Standard,300 tentativas,16k entrada,25k saída total,default30m,sem serviços adicionais. Não é promessa de fatura, gasto autorizado ou consumo esperado; o consumo real ainda não foi medido. Teto em BRL permanece desconhecido. Parâmetros/cache efetivamente aplicados, tokenização e reserva global deverão ser conferidos e implementados antes da execução; os adaptadores atuais não impõem esses tetos reais.

## Configuração documental e histórico preservado

O arquivo original `proposta_lote_real.json` permanece intacto como proposta0.1 histórica, com modelo/configuração ausentes e2.000 de saída. Os novos arquivos distinguem atualização de modelo e alternativa de saída:

- `proposta_lote_real_v02_modelo_high_2k.json`: modelo/aplicação escolhidos, limite histórico2k explicitamente conservado para comparação; não autoriza execução.
- `proposta_lote_real_v02_alternativa_high_25k.json`: mesmo modelo com25k de saída total e cache proposto30m; **alternativa orçamentária não aprovada**.

Campos `api` e `politica_cache_proposta` são metadados de planejamento, não parâmetros que o runner quantitativo já saiba aplicar. A configuração conceitual Responses é `model="gpt-6-luna"`, `reasoning={"effort":"high"}`, `max_output_tokens=2000` ou25000 conforme variante aprovada futuramente. Não se inventou parâmetro de API para retenção30m: o transporte deverá confirmar a configuração suportada e registrar o comportamento efetivo. A aprovação de preservação/auditoria está anotada como **decisão aprovada, código não implementado**; não como requisito técnico “verificado”. Orçamento/aprovação de lote continuam null em ambos os novos arquivos.

## A chave precisa ser enviada no chat?

**Não. Configure `OPENAI_API_KEY` localmente no ambiente do processo**, conforme o [quickstart oficial](https://developers.openai.com/api/docs/quickstart). Não envie a chave nesta conversa. Não foi lido `.env`, valor de variável ou segredo; somente o código público foi inspecionado.

O novo caminho quantitativo (`piloto_engenharia`, `interpretacao_no`, `condicoes`, `orquestracao`) **não carrega `.env`, não lê `OPENAI_API_KEY` e não possui transporte concreto**. Exportar a variável prepara o ambiente para a integração futura; não habilita execução de IA no runner atual. Não se confirmou se alguma chave já está configurada.

A função legada `src/tcc_agent/local_runtime.py::load_local_env(root)` lê `root/.env`; `scripts/run_pilots.py` a chama apenas no modo real legado, busca `OPENAI_API_KEY` e cria o cliente. Isso não equivale a suporte do piloto quantitativo. Não executar esse runner legado para coletar o experimento novo. Sua implementação existente não foi alterada nem chamada.

Para preparar a variável apenas na sessão zsh local, sem colocá-la no texto do comando/histórico, o usuário pode executar manualmente:

```zsh
read -rs 'tcc_openai_key?Chave da API OpenAI (entrada oculta): '
export OPENAI_API_KEY="$tcc_openai_key"
unset tcc_openai_key
```

Executar a integração futura no mesmo terminal/processo que recebeu a variável. Um terminal com variável exportada não a transfere automaticamente a um aplicativo desktop já aberto ou a outra sessão; o mecanismo de execução deverá ser explicitado na implementação. Este registro não cria `.env` nem pede que o usuário revele a chave.


## Vigência posterior: integração autorizada

Em 26/10/2026, o usuário aprovou US$5 e 25.000 tokens totais e autorizou implementação. As pendências financeiras históricas acima foram superadas para o lote único. Integração, controles e guia estão em `docs/desenvolvimento/ETAPA_09_INTEGRACAO_REAL.md`. Sem coleta real pelo executor; tarifa de contagem continua uma hipótese de provisão, não cobrança comprovada. Variantes 0.1/0.2 preservadas e `lote_aprovado_v03.json` registra a aprovação atual.
