# Contextos compactos e operações incorporadas

Implementação de 10/11/2026, posterior à coleta original. Os pedidos, respostas e resultados do piloto permanecem preservados. Nenhuma inferência ou contagem remota foi executada nesta implementação.

## Objetivo e implementação concluída

1. **Evidências sem perda.** `src/apresentacao.py` interna listas idênticas de pares fonte/localizador usadas mais de uma vez. Cada posição original passa a apontar para um conjunto catalogado. A ordem, as associações por resultado e o conteúdo das fontes são preservados. Listas distintas, inclusive com ordem diferente, não são confundidas. `expandir` reconstrói o pedido lógico integral para auditoria.
2. **Responsabilidades sem cópia integral no contrato textual.** O catálogo permanece em `contexto.responsabilidades_operacionais`; o contrato de resposta usa uma referência quando sua lista é idêntica. O JSON Schema continua expressando as rotas válidas para restringir a saída; essa restrição não foi removida para economizar espaço.
3. **Operações já incorporadas.** O orquestrador registra propostas anteriores aceitas pela política e incorporadas ao estado usado para o cálculo. Cada registro informa evento, ID de proposta, responsável, operação, alvo, atributo, unidade, valor e evidências. As fontes dessas propostas também são incluídas no contexto. Propostas rejeitadas e meros encaminhamentos não alimentam esse registro. O estado é explicitamente `incorporada_operacionalmente`, com suporte semântico `nao_auditado`.
4. **Instrução de encaminhamento.** O pedido real orienta não repetir operações incorporadas para o mesmo fato; permite operações pendentes e fatos novos/conflitantes, exigindo evidência específica e explicação da diferença. Distingue datas calculadas dos predecessores de novas restrições locais e exige evidência específica do atributo local.

A compactação ocorre na fronteira HTTP de `TransporteReal`, antes da contagem e da inferência. Ambas recebem a mesma representação. O adaptador, o JSON Schema e o parser continuam usando o contexto canônico. O pedido compacto efetivamente enviado fica salvo no registro de transporte. A simulação não reproduz a interpretação desse novo formato pela IA.

O contexto canônico inclui a versão da apresentação e o registro de incorporação antes do cálculo de seu hash. Assim, esses campos participam da identidade do contexto/cache. A proteção existente de sessões contra mudança do código continua exigindo uma nova sessão para código alterado.

## Validação realizada

Comando: `python3 -m unittest discover -s TCC_Codigos/etapas/alfa_documental_v2/tests -t . -q`

Resultado: **49 testes passaram**, incluindo as 45 regressões anteriores e quatro testes novos:

- Reconstrução exata, determinismo, ausência de mutação e redução de tamanho nos 13 pedidos locais históricos.
- Preservação da ordem e falha explícita quando uma referência não existe no catálogo.
- Disponibilidade da operação do fornecedor somente depois de incorporada, com valor D25 e evidências visíveis nos sucessores; resultado simulado D45 preservado.
- Transporte HTTP falso com rede bloqueada: contagem e inferência recebem o mesmo pedido compacto; esquema canônico preservado e registro persistido igual ao payload enviado.

Comparação offline de tamanho: reaplicando apenas a representação compacta e suas instruções aos pedidos históricos (incluindo esquema e envelope), montagem passa de 79.281 para 75.022 caracteres (−5,37%); validação, de 77.430 para 67.749 (−12,50%). Medição por `len(json.dumps(payload, ensure_ascii=False))`, com os separadores padrão do Python. Esse ensaio não adiciona retrospectivamente o novo registro de incorporação aos pedidos antigos. Portanto, não estima o saldo completo dos futuros pedidos, tokens faturados ou economia monetária.

## Próxima etapa: avaliação controlada, ainda não executada

Preparar uma comparação prospectiva entre a representação original e a nova, congelando dados, modelo e configuração. Preservar todas as respostas, inclusive falhas, e avaliar:

- Cobertura das fontes e possibilidade de reconstrução integral.
- Propostas locais e suporte específico das evidências, inclusive propostas indevidas sem efeito numérico.
- Encaminhamentos redundantes versus encaminhamentos necessários.
- Casos negativos: operação ainda pendente, informação desconhecida, fato novo e evidência conflitante sobre atributo já tratado.
- Resultados de prazo/custo, tokens oficiais de entrada/saída, latência e custo.

Não retirar rotas do esquema apenas porque houve incorporação anterior: isso poderia impedir o relato legítimo de fato novo ou conflito. Nesta versão, a distinção é uma instrução explícita, não uma garantia automática de interpretação semântica. A redução efetiva de encaminhamentos e a qualidade das respostas precisam ser demonstradas nessa avaliação futura.
