# Etapa 4 — motor determinístico de prazo e custo

24/10/2026, America/Sao_Paulo. **Entregue, pendente de revisão do coordenador e usuário.** O usuário aprovou implicitamente a etapa 3 ao dizer “Prossiga para a etapa 4”. Etapas 5–11 não iniciadas; aprovação não certifica validação científica independente.

## Escopo e arquitetura

Pacote novo e isolado `TCC_Codigos/src/motor_deterministico/`, sem importação de `tcc_agent`, dependências externas, LLM, heurísticas de relato, views B/H/T, agenda de interpretação ou alteração do observatório/legado. `conhecimento.py` contém validação de Conhecimento e intervalos conservadores; `motor.py` valida estado/propostas, recalcula baseline, cronograma, livro e ResultadoFinal/ResultadoNo; `__main__.py` oferece CLI offline. Nenhum módulo de runtime lê arquivo de referência, gabarito ou identifica cenário pelo ID.

`preparar(estado) -> (datas_base, custo_base)` valida e recalcula baseline; lança EntradaInvalida se inconsistente. `calcular(estado, evento=None, propostas=(), politica=None, execucao_id='offline') -> dict` devolve as seis quantidades do ResultadoFinal, livro, rastro por entidade e diagnósticos. Erro de entrada devolve execução erro sem campos de previsão; desconhecimento legítimo retorna parcial, com magnitudes null e lacunas. Entrada é copiada, nunca alterada. Baseline sem evento é calculada pelo mesmo caminho.

Esta é a parte pura de cálculo das interfaces conceituais da etapa 1. Não implementa `avaliar(...interpretador...)`, AnaliseNo completo, revisões/contextos de LLM nem orquestração. Propostas manuais representam apenas alterações já interpretadas/revisadas. O hash do contexto inclui snapshot, evento, propostas e política. `manifesto_hash` identifica o snapshot canônico recebido, sem afirmar hash de um manifesto externo não recebido. Fontes e localizadores ficam nos conhecimentos, parcelas e decisões. Chamadas API/custo API são zero; latência local é medida.

## Equações e validação

`S=max(0, restrições simultâneas, fins dos predecessores); F=S+D`, FS0, DAG e dias inteiros. Cada transferência catalogada lê disponibilidade no componente destino de requer e atualiza somente a restrição identificada na atividade origem. Pisos contratuais preservados; fornece não participa. Todas as atividades devem alcançar o marco. Nunca somar deltas de caminhos.

`I=taxa*max(0,fim-início-cobertura)`. A parcela base deve ser igual a fixo+incidência base recalculada. Delta temporal é `I_novo-I_base`, ou máximo desse delta e zero para sem_credito. Custo final é orçamento base mais deltas únicos. A mesma obrigação repetida com conteúdo idêntico entra uma vez; colisão divergente é erro. Alteração direta e temporal da mesma parcela exige reconciliação/revisão. Crédito direto substitui valor da parcela com fonte, sem criar parcela base negativa.

Limites inteiros opcionais permitem somar/convergir com segurança. Se um ramo tem limite superior abaixo do predecessor dominante, o máximo é exato; sem limite suficiente permanece desconhecido. Limites aparecem como extensão de Conhecimento, mantendo estados/campos aprovados. Intervalos temporais com ordem início/fim não garantida preservam lacuna e limites conservadores; intervalo definitivamente invertido é erro. Tarifa conhecida zero garante incidência zero mesmo sem data exata. Não é solver universal de correlações.

Validação inclui referências visíveis, IDs únicos, endpoints, tipos/unidades, FS0, ciclos nas projeções, duração de marco zero, números inteiros (rejeita bool/fração/negativo), fechamento e baseline/decomposição consistentes. Fonte existente não prova interpretação correta: decisões dizem que o suporte semântico é manual e auditável. Operações não autorizadas/fora de catálogo, condições pendentes e colisões retornam erro/requer_revisao sem aplicar parcialmente.

Política manual contém autorizações por hash da proposta, predicados revisados e requisitos locais. Não é gerada pelo runtime nem prova criptográfica de revisão. Disponibilidade alterada exige resolução explícita das regras locais candidatas alcançáveis pelas transferências/FS, quando existentes; montagem exige manutenção confirmada sob condição ou duração desconhecida explícita, e custo resolvido ou lacuna. O chamador continua responsável por fornecer todos os requisitos semânticos: o motor não os extrai do texto.

## Entradas manuais e decisões conservadoras

`data/desenvolvimento/propostas_manuais_v1/` tem oito entradas estruturadas apartadas de `referencias/`, transcritas dos avisos. Não há NLP nem adaptador simulado rotulado como LLM. As parcelas e IDs aprovados são preservados; as cobranças usam IDs dos avisos. A versão do evento pré-normalização v1.0 é registrada e vinculada explicitamente à versão do snapshot grafo. Nenhum dado anterior mudou.

Concretizações locais, sem mudança científica: `no_id` localiza efeitos monetários; `limites` registra domínio demonstrado; `registrar_lacuna_custo` cria item pendente sem preço, não obrigação confirmada; `aplicar_regra_catalogada` recebe parâmetros de aditivo autorizado. Não são fórmulas executáveis ou permissão geral para futuras propostas LLM. A política e os predicados manuais deverão ser revistos ao integrar interpretação, sem autorizar automaticamente uma saída de IA pelo seu próprio hash.

## Reprodução

A partir da raiz do repositório, Python 3.9+ e biblioteca padrão:

```sh
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa4 -v
PYTHONPATH=TCC_Codigos/src python3 -m motor_deterministico TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/estado_projeto.json
PYTHONPATH=TCC_Codigos/src python3 -m motor_deterministico TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/estado_projeto.json --entrada-manual TCC_Codigos/data/desenvolvimento/propostas_manuais_v1/k_09c2.json
python3 TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/validar.py
```

37 testes passaram (o teste dos oito casos possui oito subcasos). Cobertura: baseline/imutabilidade, absorção, convergência simultânea, piso, cobrança única/colisão, custo fixo/temporal, extensão base sem dupla contagem, crédito explícito/sem crédito, isenção, ausência de aceite/preço, dominância com limite e sem limite, IDs opacos/ordem, fontes/unidades/números inválidos, baseline/decomposição inconsistentes, ciclo, endpoint, fechamento e zero com lacuna. Testes autorais e aritmética documental não equivalem a avaliação independente. Expectativas ficam somente nos testes, fora do runtime.

| Caso | Fim novo | Delta dias | Custo novo centavos | Delta centavos |
|---|---:|---:|---:|---:|
| baseline recalculada | 10 | 0 | 500000 | 0 |
| k_b731 | 10 | 0 | 500000 | 0 |
| k_09c2 | 12 | 2 | 540000 | 40000 |
| k_e168 | 10 | 0 | 530000 | 30000 |
| k_547a | 12 | 2 | 500000 | 0 |
| k_a92f | 10 | 0 | 515000 | 15000 |
| k_23d8 | desconhecido | indeterminado | desconhecido, ≥520000 | direção aumento, ≥20000 |
| k_f04b | 9 | −1 | 490000 | −10000 |
| k_8c65 | 12 | 2 | desconhecido, ≥520000 | direção aumento, ≥20000 |

k_23d8 não presume aceite pelo laudo. k_8c65 não reutiliza taxa inaplicável; desconhecido não negativo preserva direção, sem preço exato. Montante identificado 520000 nos dois casos não é tratado genericamente como limite inferior; aqui o limite é demonstrado separadamente por domínios não negativos explícitos. k_f04b mantém apoio100000; economia10000 vem do crédito comercial. Resultados completos auditáveis estão em `TCC_Codigos/outputs/etapa4_motor_20261024/`.

## Integridade, integração e revisão

Antes de integrar, os 38 arquivos anteriores dos dois pacotes e documentação foram comparados entre principal e worktree por SHA256. Apenas PLANO_MESTRE/STATUS recebem notas de vigência; dados e documentos das etapas 0–3 permanecem por conteúdo. Cópia seletiva verifica novamente hashes originais dos destinos, recusa conflitos e verifica igualdade final. A suíte da etapa 4 e o validador da etapa 3 são executados na principal após cópia.

Nenhuma instalação, API, segredo, commit, push, PR, reparo do legado ou etapa 5. A suíte histórica não foi repetida: permanecem os problemas documentados na etapa 0. Revisão deve conferir política manual, extensões mínimas dos contratos, suportes dos limites e representação de item pendente; validação humana independente continua pendente. Datas úteis, recursos, progresso, otimização de alternativas, vários eventos interativos, ciclos e outros tipos de precedência ficam fora da v1.

## Ajustes da revisão preliminar do coordenador

Exigidas baseline e decomposição exatas (limite inferior coincidente não basta), três declarações de completude com suporte e reciprocidade regra/restrição/atividade. Rastro por nó agora filtra decisões/origens por alvo/no_id, associa cobranças ao nó de origem e incidência temporal ao marco, registra regras, restrições e duração usadas. Disponibilidade causal consta nos predecessores de receber. Origens dos predecessores não são fabricadas como decisões locais; ficam rastreáveis pelos IDs de entrada e pelos próprios resultados. Intervalos sem ordem suficiente permanecem indeterminados; taxa zero sustenta zero; inversão demonstrada é erro. Seis testes adicionais focam esses pontos; total após revisão preliminar: 32 aprovados.

## Segunda revisão delimitada do coordenador

Corrigida a exigência indevida de existir requisito local em qualquer alteração de disponibilidade. Um fixture sintético derivado, sem regras_locais e com transferência válida, calcula +2 dias/+40000 centavos. Uma cláusula fora dos candidatos alcançáveis não é exigida. Cláusulas locais candidatas existentes devem constar nos requisitos revisados e ter resolução explícita; alcançabilidade é filtro conservador, não interpretação de aplicabilidade ou agenda LLM. Cabe ao chamador revisar condições e fornecer resolução/lacuna, inclusive para requisitos adicionais pertinentes ao evento.

Decisões aceitas agora aparecem também no ResultadoFinal, com nos_alvo resolvidos por identidade. substituir_restricao associa à atividade proprietária; aplicar_regra_catalogada associa aos endpoints de atividade do intervalo temporal (ao marco final para intervalo inteiramente constante). Decisões, origens e referências de regras seguem o mesmo mapa nos ResultadoNo. k_547a/k_8c65 conservam as decisões dos aditivos em n_e659; substituição autorizada do piso r_559aea registra decisão/origem em n_42be e produz início D8. Nenhuma proposta aplicada pode ficar sem proprietário auditável. Cinco testes focados adicionais: 37 testes aprovados; oito resultados numéricos/epistêmicos preservados, rastros regenerados.
