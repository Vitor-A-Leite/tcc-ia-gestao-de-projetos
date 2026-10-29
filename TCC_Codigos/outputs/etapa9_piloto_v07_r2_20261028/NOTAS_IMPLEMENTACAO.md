# V7 revisão 7.1 — geração restrita ao escopo

Preserva as correções de vínculo, direção, cláusulas, manutenção escopada e dimensões da v7 inicial. Adiciona JSON Schema estrito em `text.format` apenas para H. B/T mantêm seus payloads anteriores. Schema derivado exclusivamente do contexto: permissões, fontes, predicados e cláusulas; nenhum gabarito, valor esperado de impacto ou auditoria entra na geração.

Quando não há permissões, propostas tem maxItems=0. Cada alternativa restante fixa a combinação de operação/alvo/atributo/unidade; encaminhamentos só admitem rotas externas. Conhecimentos indeterminados, direcionais e pendências continuam válidos. O schema limita forma e escopo; não verifica suporte semântico, condições ou a veracidade dos valores. O parser interno continua obrigatório.

Schema conferido com jsonschema 4.25.1 instalado só em /private/tmp/tcc-v07-jsonschema para testes. Não é dependência de produção. 20 testes H R2 passaram, incluindo cinco para o schema e as duas respostas reais problemáticas. Seis testes de carteira/integração passaram; novo teste confirma schema idêntico em contagem oficial e inferência. 112 contextos validados; maior payload básico 44.645 bytes, antes dos metadados correntes. A contagem oficial e o limite de bytes continuam verificados em cada chamada.

A coorte inicial foi parada sem reparar ou repetir as saídas: seis slots, 17 chamadas conciliadas, US$ 0,073249855 comprometidos. Snapshot e relatório parcial preservados em ../etapa9_piloto_v07_20261028/. Esta revisão tem novos IDs, código congelado e a mesma carteira; começa em 790 tentativas / US$ 3,281889545. Não mistura resultados das duas rodadas.

Fonte oficial consultada antes da implementação: [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs). O suporte a schema, streaming e reasoning High foi confirmado na [página GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).
