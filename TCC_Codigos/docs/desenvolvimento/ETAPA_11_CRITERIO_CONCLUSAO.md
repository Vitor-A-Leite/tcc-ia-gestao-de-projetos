# Critério de conclusão — etapa 11

28/10/2026. O usuário autorizou iniciar os três casos inéditos, criar uma meta e prosseguir até concluir o experimento final sob o teto acumulado de US$ 5. Esta autorização sucede o protocolo prospectivo v2 da etapa 10; não equivale a parecer científico humano.

## Aceite

1. Integrar um executor exclusivo e aditivo para o manifesto congelado de três casos × B/H/T × uma repetição, nove slots. Testar carteira, ordem, execução única, limites e tratamento de falhas sem rede, em cópias descartáveis da carteira.
2. Congelar a integração antes da coleta. Preservar os 253 artefatos selados na etapa 10, inclusive os 141 arquivos do preditor, inputs, views e referências. Não ajustar qualquer preditor ou gabarito após observar os resultados.
3. Executar os nove slots uma única vez, na ordem prospectiva; manter falhas e resultados parciais. Sem retry, reparo ou fallback. As referências não entram nos prompts. Uma parada prevista impede afirmar coleta completa e conserva slots ausentes no denominador.
4. Normalizar, avaliar e auditar os nove resultados e as 18 dimensões. Separar validade, cobertura, acerto, suporte na view e indeterminação. Apresentar erros individuais, denominadores, limites suplementares, custo e latência. A auditoria posterior pelo coordenador não será apresentada como revisão cega ou humana.
5. Recalcular o custo das novas chamadas a partir do uso observado, preservar as chamadas 1–1114 e as 13 reservas históricas desconhecidas, e verificar a integridade dos artefatos anteriores. Entregar relatório e atualizar o estado do projeto.

Concluir a etapa significa completar e documentar o experimento, incluindo resultados desfavoráveis; não exige acerto perfeito nem autoriza transformar incertezas reais em valores exatos.

## Orçamento e execução

Carteira única: `outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite`. Base: 1.114 tentativas e US$ 4,480425665 comprometidos. Reserva de US$ 0,0165 por tentativa; máximo de 30 novas tentativas, reserva incremental máxima de US$ 0,495 e compromisso máximo previsto de US$ 4,975425665. O limite absoluto permanece US$ 5. Provisão de contagem não é fatura; reservas desconhecidas não são liberadas.

Manter gpt-6-luna, reasoning high, Standard/default, stream, cache 30m, entrada oficial até 16.000 tokens, saída total até 25.000 tokens, 180 segundos por chamada e até oito chamadas/1.500 segundos por slot H. B/T fazem uma chamada cada. Configuração, preços verificados, manifesto, hashes e autorização ficam no adendo imutável da etapa 11.

Dados: `data/final/etapa10_v2`. H: revisão 7.2 congelada. Integração nova: `experimentos/etapa11/executor.py`, fora de `src`. Resultados: `outputs/etapa11_final_20261028`. O teste é exploratório: três casos sintéticos, uma repetição por condição, sem inferência de superioridade estatística ou atribuição causal exclusiva ao grafo.
