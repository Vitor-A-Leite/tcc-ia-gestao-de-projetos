# Alfa documental v1 — leitura da implementação anterior

Leitura em 09–10/11/2026, antes da implementação desta etapa. Alterações existentes em `Planejamento/`, a entrega `grafo_salvia/` e o cache Graphify não foram tocados. A skill Graphify foi consultada; não havia `graphify-out/graph.json`, apenas cache de índice. A inspeção foi feita diretamente nos arquivos, sem gerar grafo de código nem executar extração paga.

| Elemento | Local anterior | Situação encontrada |
|---|---|---|
| Alfa | `../../data/project_graph.json` | 40 entidades, 65 relações. Fornecedores, componentes, tarefas, testes, marcos, pessoas e áreas. Sem durações, disponibilidade ou contratos suficientes para cálculo monetário. |
| Visualização Alfa | `../../visualizacao/grafo_projeto.html`, `observatorio3d/` | Exploração do grafo; não implementava a comparação do conteúdo documental com o estado quantitativo. |
| Protótipo histórico | `../../src/tcc_agent/`, notebooks e scripts de baseline/hybrid | Classificação, seleção de artefatos e propagação de entidades; outro contrato. Não confundir com o preditor final da Sálvia. |
| H vigente | `../../src/hibrido_v07_r3/` | Revisão 7.2: respostas wire, schema estrito, validação local, propostas, condições e indeterminação. |
| Agenda/coordenação | `hibrido_v07_r3/orquestracao.py`, `politica.py`, `escopo.py`, `fechamento.py` | Passagem topológica, catálogo de responsáveis, reconciliação de encaminhamentos e fechamento por dimensão. Política construtora recusa mais de oito entidades; limite de oito chamadas. |
| Motor | `../../src/hibrido_v05/motor.py`, `motor_deterministico/` | Cópias do estado, intervalos, máximo nas convergências, livro por obrigação, contratos temporais, conservação de desconhecidos. O H7.2 reutiliza esse motor. |
| Fontes | `data/final/etapa10_v2/inputs/fontes.json` + trechos TXT | Fontes preparadas, localizadores e versões. Não é importador automático de Word/PDF. |
| Registros Alfa | `../../data/artifacts/` | JSON de Status Report, Action Log, Risk Register e Decision Log. Não existe reconciliação campo a campo com o H7.2. Datas históricas não são a baseline sintética desta etapa. |
| Coleta final Sálvia | `../../outputs/etapa11_final_20261028/` | Finalizada; dados/preditor/gabaritos congelados e parecer humano pendente. Nenhuma substituição autorizada. |

O contrato quantitativo aceita `1.0-proposta`, BRL em centavos inteiros, dias corridos desde D0, marcos de duração zero, FS com lag zero, regras explícitas de transferência e custo. O evento é prospectivo em D0 e tem versão de projeto, menções cadastradas e evidências. O adaptador local exige contexto hash, permissões por nó, referências visíveis e resolução de cláusulas. Uma citação estruturalmente válida não demonstra suporte semântico.

O transporte histórico conta tokens oficialmente, recusa entrada acima de 16.000 tokens, protege payloads acima de 100.000 bytes e permite até 25.000 tokens de saída/180 segundos. A carteira histórica tem limites por coorte e não pode ser reutilizada como se fosse uma carteira nova. A ampliação exige política/catálogo próprios; aumentar apenas o número oito não resolveria a integração documental nem o crescimento do contexto.

A nova etapa usa projeção explícita de fornecedores/componentes como pontos temporais de duração zero, mantendo seus tipos de domínio no grafo. Pessoas, áreas e documentos não entram como atividades no solver. Relações documentais e contextuais ficam fora da projeção causal. O desenho CAD é um documento separado de T_CAD.
