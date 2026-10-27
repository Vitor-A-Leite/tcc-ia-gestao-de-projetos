# Etapa 8 — observatório explicável de prazo e custo

25/10/2026, America/Sao_Paulo. **ENTREGUE, PENDENTE de revisão do coordenador e usuário.** A instrução “Inicie a etapa 8”, após a revisão da entrega 7, registra a etapa 7 como aprovada para progressão. Somente etapa 8 executada; **etapas 9–11 não iniciadas**. Aprovação de software não equivale a revisão científica independente.

## Escopo e inventário de reutilização

O plano mestre pede entradas, análises, regras e resultados por nó, explicando o resultado final. O contrato vigente mantém Python como fonte dos cálculos, a separação entre execução e conhecimento, e gabaritos fora do preditor.

Inventário curto: `scripts/serve_graph3d.py` e `visualizacao/observatorio3d/{index.html,app.js,style.css}` pertencem ao legado Projeto Alfa e `tcc_agent`: identificação de entidades e alcance de regras/documentos, com modo de referência que usa campos esperados e opção de API. Não são adaptadores do novo contrato quantitativo. `visualizacao/grafo_template.html` e `grafo_projeto.html` são outras visualizações históricas. Todos foram preservados. A implementação nova é isolada, sem framework, CDN, instalação ou correção incidental do legado.

## Implementação e fronteiras

- `src/observatorio/__init__.py`: catálogo positivo dos oito avisos, integração explícita com `montar_views` e `executar_h`, projeção de apresentação e formatação de inteiros/limites. A integração H, a política prescrita, o adaptador e o motor são os módulos existentes; nenhuma fórmula de prazo, custo ou métrica foi reimplementada na UI.
- `src/observatorio/__main__.py`: servidor stdlib exclusivamente em `127.0.0.1`; rotas fixas de assets e JSON. Não oferece importação de caminho arbitrário, transporte real, credenciais, publicação nem execução B/T.
- `visualizacao/observatorio_quantitativo/`: interface HTML/CSS/JS sem bibliotecas externas. Os dados entram como texto/DOM; não usa `innerHTML` para inserir conteúdo dos artefatos.
- `tests/etapa8/`: integração de dados, identidade, semântica da apresentação, isolamento e HTTP.
- `outputs/etapa8_verificacao/`: capturas reais do navegador, exportação conferida, testes e registro de integridade.

Fluxo: selecionar aviso e contraprova → Python lê apenas inputs, snapshot e fixture prescrita correspondente → constrói views B/H/T → executa somente H com interpretação/política prescritas → entrega resultado original, rastro e campos de apresentação → navegador permite inspeção por nó e exportação. É uma **reprodução calculada de fixtures prescritas**, não reprodução de chamadas reais, simulação de IA autônoma nem streaming de execução. A navegação manual pela agenda é didática; não representa tempos de chamadas.

Cada clique gera identidade nova e recalcula pelo motor. Não há persistência automática de histórico nem cache de replays no servidor; o botão de download preserva o registro integral no computador. O resultado original fica em `resultado`, com hash próprio; dados formatados e layout ficam separados. O arquivo de fixture original e sua cópia com ID da execução têm hashes distintos identificados. A apresentação rejeita evento/projeto/versão/snapshot/view/condição incompatíveis. Hashes vinculam conteúdo, não certificam sua correção semântica.

`GET /api/catalogo`: avisos com resumo neutro extraído literalmente do relato e disponibilidade de condições. `GET /api/replay?caso=...&modo=normal|parcial|erro`: execução offline e pacote de apresentação; não consulta gabaritos ou outputs. `GET /api/avaliacao`: leitura separada e explícita da demonstração sintética da etapa 7. Paths fora da lista retornam 404, seleções inválidas 400 e falha de carregamento 500; nenhuma falha vira previsão zero.

## O que inspecionar

1. Relato integral, evento, projeto, versão, condição H, origem simulada, execução e hashes. Modelo real não foi executado; análises e política são autorais prescritas.
2. Antes/depois/deltas finais em dias e reais, completude por desfecho, conhecimento, limites, lacunas e estado operacional separados. Um aumento conhecido mínimo continua desigualdade, nunca total exato. Erro mostra indisponibilidade; zero só aparece quando o resultado contém zero exato.
3. Grafo SVG da projeção causal do snapshot, com precedências e transferência específica identificadas. A relação contextual de fornecimento fica visível em linha separada, sem propagação temporal automática. Setas/posição não são impacto nem prova causal automática. A tabela de todas as relações e fontes fica em detalhes. Todos os nós são selecionáveis também por botões, seletor e anterior/próximo, inclusive os não avaliados/bloqueados.
4. Por nó: início/fim/duração antes/depois quando aplicáveis; disponibilidade base/atual do componente; não aplicabilidade de datas para fornecedor/componente sustentada pelo tipo; todos os predecessores de cálculo com quantitativos/estado/revisão realmente registrados, inclusive ramo inalterado; restrições, regras, propostas, condições, decisões e efeitos de custo. Seleção documental efetivamente fornecida, justificativa prescrita e links de evidência são legíveis. JSON original continua disponível em detalhes e download.
5. Livro de parcelas únicas, base/novo/delta e fontes. Os termos contratuais do snapshot estão rotulados **BASE**; alterações do evento vêm das propostas e decisões do rastro. Não se apresenta taxa antiga como vigente quando substituída por desconhecida. No caso de dispensa, aparecem base contratada de 12 dias aceita e delta de apoio zero; no de tarifa desconhecida, aparece a substituição sem estimar tarifa.
6. B/T mostram **sem execução; view disponível**. Não se copiou H. A área de avaliação só abre explicitamente, identificada como dataset sintético distinto dos oito avisos Íris, com cobertura e MAE n/N e falhas/invalidade preservadas. Referências sintéticas, manifesto e auditorias permanecem nessa área. Não existe placar científico entre condições nem demonstração de superioridade.
7. Consumo observado (análises, API, tokens, latência e custo de API) está separado do custo do projeto, nos detalhes da execução. Valores ausentes permanecem ausentes. Modelos, transporte concreto, seleção/fechamento/suporte automáticos H e auditoria independente permanecem pendentes.

No aviso k_09c2, sem explicação codificada pelo ID do caso: o rastro mostra cartucho D6, receber D6–D7, preparação D0–D5; a montagem recebe **os dois** fins D7/D5, começa D7 e termina D10 com duração 3; teste D10–D12 e marco D12. A regra geral visível usa máximo dos predecessores/restrições, não soma deltas locais. O livro mostra obrigação adicional R$200 e apoio R$200, totalizando delta calculado R$400. Esses números vêm do resultado real do motor sob interpretação prescrita, não de gabarito.

## Abrir e parar

Da raiz `/Users/vaugusto/Desktop/Faculdade/TCC`, Python 3.9+ e biblioteca padrão:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -m observatorio --porta 8768
```

Abra [http://127.0.0.1:8768](http://127.0.0.1:8768). Escolha um aviso e “Calcular e abrir replay”. Para parar, **Ctrl+C no terminal que iniciou o servidor**. Para reiniciar, execute o mesmo comando. Se a porta já estiver ocupada, use `--porta 8769` e a URL correspondente, ou confira a instância antes de pará-la.

A instância deixada para revisão nesta entrega usa PID **12223**, porta 8768, sessão de ferramenta **41762**. Se não houver acesso ao terminal original, confira `lsof -nP -iTCP:8768 -sTCP:LISTEN`; somente se ainda corresponder à instância desta entrega, `kill -TERM 12223` a encerra. PID não é identidade durável: não reutilizar esse comando depois de o processo encerrar. A disponibilidade depende de a sessão local permanecer ativa; não há serviço instalado em segundo plano.

## Verificação efetivamente feita

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa8 -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=TCC_Codigos/src python3 -O -m unittest discover -s TCC_Codigos/tests/etapa8 -q
```

**16 testes aprovados**, também com Python -O. Testes HTTP abrem portas temporárias exclusivamente locais. Cobrem oito avisos via integração H; serialização sem NaN; convergência e parcelas; falta de dados sem imputação; redução; estados parcial/erro reais da agenda; identidade/versão/view/hash; isolamento de referências/outputs na predição; seleção inválida; termos BASE distintos das alterações aceitas; imutabilidade do resultado original; denominadores sintéticos e rotas/assets/cabeçalhos. O teste estático de DOM é apenas uma proteção adicional, não substitui conferência visual.

Regressões executadas: **49 etapa 7 + 24 etapa 6 + 21 etapa 5 + 37 etapa 4 = 131 aprovadas**. Validador etapa 3 aprovado, seis contraprovas rejeitadas. Nenhum teste legado conhecido foi corrigido ou reexecutado.

Conferência manual no navegador real IAB: seleção e carregamento normal; inspeção da montagem e seus dois predecessores; fornecedor com datas inaplicáveis; apresentação de limite inferior; parcial por teto de uma análise; erro por alvo inválido; indeterminação legítima k_23d8; prazo exato/custo direcional k_8c65; dispensa k_547a; link de evidência abrindo o trecho e rolando; avaliação sintética com N=8/cobertura3/8/pares2/8 e falhas preservadas; download JSON realmente salvo e conferido por identidade/hash/delta; teste de tela estreita por override solicitado de 390×844, largura útil observada de 341px. Foi corrigido o seletor que excedia a tela; verificação final: largura do documento = viewport (341px), com rolagem interna intencional do grafo/tabelas. Override restaurado. Não foram feitos testes exaustivos com leitor de tela, todos os navegadores ou todos os gestos móveis.

Capturas reais: `normal_montagem.png`, `convergencia.png`, `grafo.png`, `fonte_aberta.png`, `parcial.png`, `erro.png`, `indeterminado_limite.png`, `dispensa.png`, `taxa_desconhecida.png`, `tela_estreita.png`, `avaliacao.png`. Algumas capturas mostram uma região da página, não toda a interface. `exportacao_verificada.json` é cópia do download real; `testes.log` conserva a rodada final. Nenhuma captura foi fabricada.

## Integridade, limites e revisão

186 arquivos preexistentes de módulos, dados, fontes/gabaritos, docs, legado, testes e outputs anteriores foram capturados por SHA256 antes da implementação e conferidos sem divergência antes de editar STATUS/PLANO_MESTRE. Somente esses dois documentos existentes receberam a transição autorizada; arquivos novos ficam nos diretórios específicos desta etapa. Registro final `integridade.json` guarda os hashes anteriores, exceções documentais previstas e os hashes finais. Nenhum reset, limpeza, commit, push, PR, alteração de .git ou substituição de diretórios anteriores.

Revisar antes de aprovar: clareza da cadeia e dos termos contratuais, separação entre fixtures autorais e IA, estado de nós bloqueados e leitura de limites, campos em detalhes e área sintética separada. Esta entrega é um observatório offline honesto dos contratos existentes. Não inclui transporte real, política automática H, piloto, congelamento, avaliação científica ou prova de suporte semântico. Fontes locais exibidas e decisões prescritas não resolvem a revisão independente pendente. **Etapa 8 aguarda revisão; não avançar automaticamente.**
