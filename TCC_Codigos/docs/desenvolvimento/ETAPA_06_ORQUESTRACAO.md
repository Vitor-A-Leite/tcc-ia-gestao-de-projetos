# Etapa 6 — orquestração local de prazo e custo

25/10/2026, America/Sao_Paulo. **Entregue pendente de revisão do coordenador e usuário.** Etapa 5 aprovada para progressão pelo usuário (“Faça a etapa 6 agora”). Somente etapa 6; etapas 7–11 não iniciadas. Conferência autoral e simulação não constituem validação científica independente.

## Interface e fluxo

`orquestracao.avaliar(estado, evento, interpretador, politica) -> dict ResultadoFinal`. Objetos em memória, copiados; nenhuma leitura de arquivos, credenciais, referências, outputs anteriores ou outros acontecimentos. Evento deve chegar normalizado para a versão do snapshot, D0. Baseline é recalculada e validada por `preparar`; projeção causal é derivada exclusivamente de `precede_FS` e das regras de transferência catalogadas. Direções, identidades, fontes, pisos e ciclos passam pelos validadores existentes. Não há arquivo de projeção externo aceito implicitamente; o arquivo documental da etapa 3 continua validado pelo seu comando próprio.

`Politica` recebe execução, sementes explícitas (`alvos`), seleção positiva por nó (`plano` com os argumentos de `montar_contexto`), origem, declaração externa de cobertura do evento/obrigações (`fechamento`), decisão semântica injetável (`resolver(contexto, analise) -> bool`), dispensas explícitas e limites. Alvo ausente/desconhecido é erro; não há identificação textual automática de entidades ou obrigações. Seleção normalizada e cobertura permanecem responsabilidade externa e revisável. O padrão sem resolver/fechamento não publica uma previsão completa. Isso concretiza a parte conservadora; não resolve a futura política experimental automática.

Passagem única em ordem topológica de todas as entidades, incluindo predecessores de ramos não alterados. Nós fora dos candidatos e sem seleção explícita reutilizam baseline porque não existe caminho causal nem condição selecionada. Dentro dos candidatos não há corte precoce por igualdade de datas: preservam-se condições, fatos do evento e efeitos monetários. Semântica não percorre `fornece`, `responsavel` ou `pertence` automaticamente. Regras locais candidatas exigem interpretação ou dispensa externa explícita com motivo e fontes; a dispensa é uma alegação de política, não interpretação textual demonstrada pelo código.

Interpretação só ocorre nos nós do plano. A ausência de plano para cláusula local candidata gera pendência. Transferências/FS e consolidação temporal são determinísticas. Fontes locais e relações/regras/permissões usam o construtor da etapa 5. Nenhum módulo anterior foi modificado.

## Contexto corrente e versão

A extensão `entradas_correntes` contém apenas predecessores causais da passagem corrente: execução, nó, revisão, versões de predecessores, quantitativos selecionados (`inicio`, `fim` ou disponibilidade), estado, referências de propostas e fontes/fatos do evento. Nunca recebe ResultadoFinal, livro, delta global, respostas esperadas ou envelope de análise/política. Evidências necessárias desses registros são acrescentadas explicitamente à seleção de fontes local. Os registros são fabricados internamente; não existe argumento para importar uma saída arquivada. `snapshot_original_hash` vincula o snapshot original; `snapshot_hash` local identifica a projeção temporal provisória.

A projeção provisória `_corrente` atualiza somente disponibilidade, duração e restrições temporais aceitas pela política, transfere por regra explícita e usa `cronograma`. Não aplica custos nem contorna validação final: o conjunto completo sempre passa por `calcular/aplicar`, com autorizações técnicas, requisitos locais, identidade de obrigações e reconciliação. Portanto a projeção corrente é condicional às decisões externas e pode ser rejeitada na consolidação; não é um resultado final antecipado.

Cache privado por `(execucao_id, no_id, contexto_hash)`. A assinatura das entradas/seleção e revisões dos predecessores muda a revisão local e o hash; resposta/cache obsoletos falham na revalidação. Reuso sempre repete a validação estrutural e a decisão da política. Não há refinamento automático, reparo de conteúdo ou segunda passagem dentro de uma avaliação. Nova invocação explícita pode reutilizar o mesmo objeto de política/cache. Resultados do motor recebem revisões, versões, hash e motivo de processamento desta agenda; rastro conserva contextos, análises, decisões e consumo observado.

## Fronteira semântica e falhas

Toda análise é revalidada por `interpretacao_no.validar`, mesmo quando o interpretador ou cache alega validade. Só depois o callback externo decide se há suporte suficiente. O hash entregue ao motor vincula a proposta que já passou por essa decisão; **não é o motivo da autorização**. O runtime não consulta gabaritos nem fabrica aceite humano. Uma política automática futura deve ser explicitamente desenhada e congelada; esta entrega não muda a comparação H/B/T nem introduz correção seletiva humana no experimento.

`simulacao.py` é um andaime separado: `InterpretadorPrescrito` preenche identidades correntes em propostas preexistentes e usa o mesmo parser/validador do adaptador Simulado. `politica_prescrita` compara o conteúdo integral das propostas com os templates externos. Os templates JSON foram normalizados das transcrições autorais da etapa 4, sem consulta a referências; IDs de efeito são canônicos, proprietário explicitado, seleção local exposta. Não representam julgamento independente nem qualidade real de LLM. Nenhum parser de relato ou tabela de resposta final por ID existe no algoritmo.

Lacunas epistêmicas legítimas em AnaliseNo são conservadas sem descartar propostas explicitamente desconhecidas: o motor ainda pode produzir prazo exato ou direção/limite de custo. Falha, limite ou revisão não autorizada bloqueiam descendentes e retiram quantitativos vigentes desses registros; datas baseline não são apresentadas aos sucessores como verificadas. Ramos independentes continuam. Pendência operacional impede a previsão final completa e devolve conhecimento indeterminado, sem zero fictício. Erro tardio conserva identidade, baseline validada, rastro e observações; exceção fora do envelope do interpretador deixa chamadas desconhecidas, sem inventar consumo zero.

Limites: número de novas análises, chamadas de transporte (reserva até duas se retry habilitado) e tempo total. Simulado consome zero chamadas API; `max_analises` é separado. Envelopes novos guardam tentativas e consumo; cache conserva histórico no rastro, mas não o cobra novamente. Medição ausente permanece null. Tempo é conferido entre análises e ao final; não há cancelamento forçado de função Python síncrona. Transporte deve cumprir seu próprio timeout. Sem transporte concreto, SDK ou chamadas pagas.

## Reprodução offline

Da raiz, Python 3.9+ e biblioteca padrão:

```sh
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa6 -v
PYTHONPATH=TCC_Codigos/src python3 -O -m unittest discover -s TCC_Codigos/tests/etapa6 -q
PYTHONPATH=TCC_Codigos/src python3 -m orquestracao TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/estado_projeto.json TCC_Codigos/data/desenvolvimento/orquestracao_simulada_v1/k_09c2.json
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa4 -q
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa5 -q
python3 TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/validar.py
```

24 testes da etapa 6 aprovados também sob `python -O` (guardas de produção não usam assert); regressões 37 da etapa 4 e 21 da etapa 5 aprovadas. Validador da etapa 3 aprovado, seis contraprovas rejeitadas. Cobertura: oito fluxos, determinismo sem interpretação, convergência e ramo inalterado, cobrança sem atraso, isenção, alternativa selecionada, falta de aceite/preço, crédito, obrigação por duas origens uma vez, seleção local/imutabilidade/ausência de vazamento, cache/revisões/consumo, conteúdo falso com fonte visível, resposta obsoleta, falha, bloqueio de descendentes, limites e reserva de retry, exceção tardia e IDs trocados. Não foram repetidos os testes legados conhecidos nem implementadas avaliação ou UI.

## Sequência e resultados SIMULADOS

Saídas duráveis em `TCC_Codigos/outputs/etapa6_simulada_20261025/`, exclusivamente artefatos de demonstração, nunca entradas do runtime. No evento k_09c2: fornecedor reutilizado; preparação D0–D5 reutilizada; cartucho interpretado para disponibilidade D6; recebimento interpretado para cobrança identificada e calculado D6–D7; montagem recebe recebimento fim D7 **e preparação fim D5**, interpreta aceite/manutenção e calcula D7–D10; teste determinístico D10–D12; marco D12 e incidência contratual determinística. São três análises simuladas, zero chamadas API, delta +2 dias e +40000 centavos; cobrança 20000 e extensão 20000 entram uma vez cada.

| Evento | Delta dias | Delta centavos | Análises simuladas |
|---|---:|---:|---:|
| k_b731 | 0 | 0 | 2 |
| k_09c2 | 2 | 40000 | 3 |
| k_e168 | 0 | 30000 | 3 |
| k_547a | 2 | 0 | 3 |
| k_a92f | 0 | 15000 | 3 |
| k_23d8 | indeterminado | aumento ≥20000 | 3 |
| k_f04b | −1 | −10000 | 2 |
| k_8c65 | 2 | aumento ≥20000 | 4 |

k_f04b tem dispensa prescrita explícita da regra de lote substituto, com aviso corrente e cláusula de lote original; não é uma dispensa inferida da ausência de atraso. k_8c65 interpreta adicionalmente o contrato no proprietário do fim do intervalo. Nenhum caso escolhe ou otimiza alternativas. A mesma obrigação em dois nós é testada por variação sintética, sem duplicação no livro.

## Integridade, integração e revisão pendente

67 arquivos preexistentes de dados/documentos/módulos/outputs anteriores foram comparados por SHA256 entre principal e worktree antes da implementação. Integração seletiva somente dos novos pacote, fixtures, testes, outputs e documento da etapa 6, mais STATUS/PLANO_MESTRE; hashes de destinos são reconferidos antes de copiar. Dados originais, módulos anteriores e outputs da etapa 4 permanecem por hash. Sem instalação, credenciais, API, commit/push/PR ou alteração do legado.

Revisar antes de aprovar: responsabilidade externa pela resolução/cobertura e dispensas; suficiência da projeção corrente local e da política futura; conservadorismo de bloquear previsão final completa diante de falha operacional; limites síncronos; fixtures prescritas não independentes. A integração automática sem decisões externas suficientes permanece parcial/revisão por desenho. Aprovação científica de referências, transporte real, modelo/orçamento, baselines/avaliador e observatório continuam futuros. **Etapa 6 não aprovada; etapa 7 não iniciada.**


## Revisão preliminar do coordenador incorporada

ResultadoNo mantém processamento no catálogo calculado|inalterado_verificado|nao_avaliado|bloqueado; a ação de interpretação/cache consta separadamente em acao_orquestracao. Saídas parciais conservam registros e referências dos nós percorridos. Regra local sem plano bloqueia o nó e os descendentes; não fornece duração baseline como entrada vigente.

Lacunas gerais de AnaliseNo são comparadas às lacunas representadas no resultado do motor. Uma lacuna residual não coberta torna a previsão indeterminada/parcial; autorização das propostas não demonstra cobertura desse efeito. Propostas explicitamente desconhecidas continuam permitindo as direções e limites que o motor sustenta. A comparação literal é conservadora: redações distintas de uma mesma lacuna podem exigir revisão.

O vínculo de cache inclui tipo/modelo/configuração/timeout/retry e Politica.versao. Troca de instância do interpretador ou callback de validação incrementa a geração privada da execução, alterando o hash; não representa revisão humana. Estado interno mutável invisível de um callback exige atualização explícita de Politica.versao. Cache antigo não contabiliza tokens/custo novamente.

A v1 recalcula conservadoramente todo o cronograma temporal na projeção e consolidação; não há poda matemática dos ramos candidatos. O reuso registrado fora dos candidatos tem prova estrutural de ausência de caminho causal e condição selecionada sob a declaração externa de cobertura, sem promessa de evitar recálculo. Igualdade de datas dentro dos candidatos nunca dispensa aceite ou custo pendente. Uma declaração externa falsa de fechamento/ausência de efeitos não é detectada semanticamente pelo algoritmo; o teste determinístico sem interpretação usa evento sintético que declara preservação real do projeto.

Total revisado: 24 testes da etapa 6 aprovados, também com Python -O; regressões 37+21 aprovadas. Cinco contraprovas da revisão incluídas: enum, descendente após regra não resolvida, lacuna residual, mudança de configuração/validador, evento sintético sem alteração. Etapa 6 continua pendente de aceite; etapa 7 não iniciada.
