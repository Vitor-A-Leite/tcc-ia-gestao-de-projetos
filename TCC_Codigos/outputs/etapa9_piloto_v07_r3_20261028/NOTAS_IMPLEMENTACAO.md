# V7 revisão 7.2 — fatos locais e operações explícitas

Mantém as correções de vínculo técnico, direção redundante, checklist de cláusulas, manutenção escopada, fechamento por dimensão e geração com schema restrito. Acrescenta duas correções de interface motivadas pelas respostas reais da revisão 7.1:

- A LLM não recebe mais solicitação de `avaliacao.prazo/custo`. Retorna fatos, condições, propostas, encaminhamentos e pendências locais. O campo diagnóstico interno legado é preenchido pelo adaptador como inaplicável, com motivo explícito; não participa da previsão. Nenhum valor ou lacuna factual é preenchido por esse mecanismo. Os desfechos/deltas continuam calculados pelo motor.
- `alterar_parametros_contratuais` substitui o nome ambíguo `aplicar_regra_catalogada` no contrato local. Serve somente para mudança expressa de taxa, base contratada ou política de crédito; cálculo da incidência existente não é encaminhamento. Antes de chamar o motor H05 preservado, o compilador traduz apenas o nome da operação. Valores, condições, evidências e IDs não mudam. O resultado registra o mapeamento e a normalização o confere.

JSON Schema continua derivado apenas de permissões/fontes/predicados/cláusulas, sem gabaritos. Geração restrita reduz erros formais; não garante veracidade de fatos ou suporte semântico. Conhecimento indeterminado/direcional e pendências explícitas continuam disponíveis. Sem retries, fallback ou reparo de respostas.

23 testes H e seis de carteira/integração aprovados, incluindo schema independente (jsonschema 4.25.1, somente ambiente temporário), todos os 112 contextos, provas negativas, crédito com incidência positiva na base, deltas negativos, compilação de operação e proveniência. B/T mantêm payloads anteriores. Pacotes e coortes históricos preservados.

As rodadas de desenvolvimento anteriores encerraram seis e 15 slots, consumindo juntas US$ 0,269021210 comprometidos, com todas as 61 chamadas conciliadas. Seus resultados e snapshots permanecem separados. Esta coorte completa parte de 834 tentativas / US$ 3,477660900 na mesma carteira, com saldo US$ 1,522339100 e teto absoluto US$ 5.

A comparação principal será v6 versus esta coorte completa, declarando as alterações conjuntas de interface, prompt, schema e coordenação. As duas coortes interrompidas serão relatadas como desenvolvimento e incluídas no custo, sem misturar resultados. Etapas 10/11 não iniciadas.
