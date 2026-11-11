# Alfa documental v2

Motor híbrido com seleção de pontos de entrada, limite livre de nós, pausa, retomada e recomendações documentais. **Versão experimental com regressão offline e piloto D02 executado com GPT-6 Luna high real.** O piloto acertou os totais e as classificações documentais, mas revelou uma proposta local sem suporte explícito. Leia o [relatório real](docs/RELATORIO_IA_REAL_20261110.md). A demonstração no navegador permanece em simulação.

Esta pasta reúne o código próprio necessário, os dados do Alfa, documentos preparados, eventos de desenvolvimento, simuladores, testes e interface. Não importa módulos nem lê dados de versões anteriores. Python 3.12 ou superior; runtime somente com biblioteca padrão. A instalação por `pip` é opcional: os comandos abaixo executam a pasta diretamente.

## Abrir e executar

Na raiz do repositório:

```sh
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 servir --porta 8767
```

Abra **http://127.0.0.1:8767**. Se o ambiente não oferece `python3.12`, o intérprete já verificado nesta máquina é `/Users/vaugusto/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3`.

1. Escolha um dos nove documentos de mudança de desenvolvimento.
2. Abra **Entradas e limites da análise** para selecionar pontos pela lista e busca. No grafo 3D, clique no nó para inspecioná-lo e use **Selecionar como entrada** no painel lateral. A lista **Inspecionar entidade** também alcança nós sobrepostos.
3. Digite qualquer inteiro entre 1 e o máximo exibido. As entradas contam. O Alfa atual contém 32 pontos executáveis; com documentos há 49 ou 50 nós. Esses totais são calculados a partir dos dados.
4. Confirme as entradas para visualizar a região e o consumo previsto. A opção **Sugerir entradas (simulação)** usa as menções preparadas, permite correções e exige confirmação. Consome uma solicitação simulada, preservada na mesma sessão.
5. Execute. Ao atingir o limite, no painel **Continuação da análise**, marque os nós pendentes, ajuste o novo limite total e use **Prosseguir com selecionados** ou **Cancelar análise**.

A interface utiliza o layout e o grafo 3D da versão 1, incorporados nesta pasta. Arraste para girar, role sobre o grafo para aproximar e use Shift/⌘ + arrastar para deslocar. Há botões equivalentes, reenquadramento e ampliação do painel. Os anéis indicam entradas (azul), região de análise (verde) e pendências (ocre tracejado). A reprodução do rastro não faz novas chamadas. Veja os detalhes em [Frontend 3D](docs/FRONTEND_3D.md).

“Usar todos” permite alcançar o máximo, mas continua analisando apenas a região pertinente. Um predecessor necessário não selecionado permanece como bloqueio explícito. Cancelar preserva os resultados já obtidos e impede novos passos; a resposta de um passo já em andamento pode ser registrada antes do encerramento. Nenhuma recomendação altera o documento oficial.

Também é possível operar pelo terminal:

```sh
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 simular D02 --entradas SUP_MOTOR --limite 1
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 continuar ID_DA_SESSAO --nos C_MOTOR T_ASSEMBLY --limite 3
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 cancelar ID_DA_SESSAO
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 testar
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 comparar
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 integridade
```

O comando `comparar` salva uma nova rodada em `outputs/`, sem sobrescrever rodadas anteriores. Não consulta cenários finais. Uma cópia desta pasta fora do repositório também pode executar `python3.12 -B alfa_documental_v2 testar`.

## O que mudou

A versão anterior interpretava todos os pontos. A v2 parte das entradas confirmadas, inclui seus descendentes temporais e os responsáveis por obrigações financeiras pertinentes, e mantém interpretação local em cada nó dessa região. O cálculo conserva o grafo integral, inclusive predecessores de outros ramos. Não se descarta um impacto porque uma folga absorveu o atraso ou porque não houve mudança no prazo.

Encaminhamentos aceitos podem ampliar a região. Se alcançarem um predecessor que altera o contexto já usado, as análises dependentes são refeitas dentro dos limites acumulados. Reanálises gastam solicitações, mas não contam como novos nós distintos. Respostas reutilizadas permanecem ligadas ao contexto exato; não são novas evidências nem repetições experimentais.

O fechamento exige todos os responsáveis da região, regras pertinentes e encaminhamentos resolvidos. Nós fora do alcance são explicitamente dispensados sob as relações cadastradas; não recebem falsa confirmação semântica. Um teste que exclui menções do evento permanece globalmente parcial. Prazo e custo podem ter completudes diferentes quando falta uma informação factual.

## Arquivos principais

| Caminho | Conteúdo |
|---|---|
| `src/selecao.py`, `src/alcance.py` | Seleção, validação e propagação conservadora. |
| `src/sessoes.py` | Estado persistente, cache, orçamento acumulado, continuação e cancelamento. |
| `src/politica.py`, `src/orquestracao.py` | Permissões, interpretação local e fechamento seletivo. |
| `src/pipeline.py`, `src/documentos.py` | Cálculo e recomendações por afirmação documental. |
| `src/vendor/` | Subconjunto incorporado dos contratos, adaptadores e motor anteriores, com namespace próprio. |
| `data/projetos/alfa/` | Grafo, documentos, nove eventos e interpretações manuais simuladas. |
| `avaliacao/` | Referências exclusivamente do avaliador; não entram nos contextos da interpretação. |
| `web/` | Interface local com o visual da v1, grafo 3D e controles seletivos da v2, sem serviços externos. |
| `tests/` | Testes funcionais e adversos com rede bloqueada. |
| `outputs/` | Sessões e resultados novos. Não é banco de preços ou fonte de planejamento. |
| `MANIFESTO_ORIGENS.json` | Origem, hash de entrada e hash entregue dos componentes. |
| `docs/RELATORIO.md` | Resultados, limites da evidência e próximos passos. |

## Limites explícitos

- Na demonstração do navegador, interpretações e sugestões continuam simuladas. O modo real está disponível no backend e no executor delimitado descrito em [Piloto IA real](docs/PILOTO_IA_REAL.md), com registro de consumo e reservas. Ainda não há comparação experimental real de economia entre os modos.
- O orçamento de solicitações é separado do máximo de nós. O padrão 32 pertence ao protocolo Alfa. Sugestão, falha e reanálise entram no acumulado. Tokens e custo de API são zero no transporte offline; bytes não são apresentados como tokens. O executor real contabiliza uso em USD e conserva o comprometimento histórico no teto agregado.
- A verificação documental compara cinco afirmações preparadas do Status Report. Action Log, Risk Register e Decision Log recebem triagem. Não há extração geral de prosa, áudio, Word, PDF ou CAD geométrico.
- Os parâmetros quantitativos e os eventos do Alfa são sintéticos. A projeção contém regras específicas desse projeto; usar outro projeto exige cadastrar e validar sua projeção, relações, fontes e responsabilidades.
- Cada cenário começa no mesmo estado inicial. A saída não é uma nova versão oficial pronta para receber cumulativamente outra mudança.
- Mudança de código, fontes, dados ou configuração invalida a retomada. O consumo anterior permanece registrado; é preciso iniciar outra sessão. A versão atual usa bloqueio de arquivo POSIX, validado em macOS/Linux.

Os testes, limites e resultados são detalhados no [relatório](docs/RELATORIO.md). A versão histórica continua disponível na pasta irmã `alfa_documental_v1`; esta v2 não depende dela para executar.

## Revisão observacional de propostas

A revisão opt-in separa checagem determinística e parecer semântico, preservando o cálculo e o suporte original `nao_auditado`. A CLI `auditar resultado.json --saida auditoria-nova.json` cria auditoria determinística offline sem sobrescrever a coleta. A API aceita revisor injetável; revisão real exige auditoria separada com orçamento persistente e o transporte com reservas existente. O comando `testar` agora executa a suíte inteira.

Veja [uso, contratos, exemplos offline e limites financeiros](docs/REVISAO_OBSERVACIONAL.md). Parecer de IA e resposta prescrita de teste não constituem aprovação humana nem verdade de avaliação.

## Lote de desenvolvimento D01–D09

O executor `src.lote_ia` separa preparo offline e início explicitamente autorizado de D01–D09. Suporta múltiplas entradas, revisão observacional, manifesto congelado e teto acumulado de US$20 com histórico preservado. Veja [protocolo, orçamento e comandos](docs/LOTE_IA_REAL.md).

A coleta de 10/11/2026 foi concluída com intervenções documentadas. Os nove resultados coincidiram com a referência autoral de desenvolvimento. Das 19 tentativas de revisão, 10 produziram pareceres válidos e 9 foram rejeitadas pelo contrato: seis por identificadores divergentes e três por citações não literais. As falhas foram preservadas, sem repetir pareceres para substituí-las. O custo estimado do lote foi US$0,196578, mais US$0,015 de reserva inconciliada; o total histórico comprometido ficou em US$4,812657675.

O [resumo final](outputs/lote_desenvolvimento_revisoes_finais_20261110/resumo_final.json) e o [registro de execução](outputs/lote_desenvolvimento_revisoes_finais_20261110/execucao.json) apontam para os resultados e auditorias. As decisões de continuação estão descritas em [retomada de D04](docs/RETOMADA_D04.md), [inspeção de D09](docs/CONCLUSAO_D09.md) e [revisões restantes](docs/REVISOES_RESTANTES_LOTE.md). Esta coleta não representa execução inteiramente automática nem certificação independente de suporte semântico.
