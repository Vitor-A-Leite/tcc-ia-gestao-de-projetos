# Continuação das revisões após inspeção

Depois de concluir as nove coletas, o lote revisou duas propostas de D01 e parou
na primeira proposta de D02. O parser rejeitou a resposta porque o revisor usou
`SUP_MOTOR (Fornecedor MotorTech)` e `valor da restrição local nao_antes`, onde
o contrato exige os identificadores exatos `SUP_MOTOR` e `valor`. O consumo da
chamada foi conciliado. A resposta original permanece com `requer_revisao` e
`parecer=null`; o texto bruto que declara suporte não é tratado como parecer válido.

O assistente inspecionou a falha e, no escopo da instrução de continuar o lote,
preparou `scripts/concluir_revisoes_lote.py`. Essa é uma decisão do assistente,
não uma aprovação humana específica. O adendo registra a mudança de condução:
após a inspeção, uma resposta inválida com consumo conhecido não impede revisar
outras propostas. Não há nova tentativa da proposta que falhou, alteração do
parser, do prompt, do modelo, das fontes ou de qualquer resposta recebida.

Os três registros anteriores são reutilizados por igualdade integral do pacote,
inclusive o inválido. Apenas propostas ainda não tentadas chegam à API. Os
pareceres inválidos são contados e continuam disponíveis como evidência. Uma
revisão terminada com pareceres inválidos tem estado distinto de sucesso pleno.
Problemas de transporte, consumo desconhecido, pacote inválido e orçamento
continuam bloqueando novas chamadas. Os limites de cada cenário descontam o
consumo anterior; a carteira e o teto total de US$20 permanecem os mesmos.

A comparação autoral acontece somente após registrar uma tentativa de revisão
para todas as propostas, incluindo falhas de contrato. Portanto, equivalência
numérica eventual não certifica suporte semântico nem elimina essas falhas.
Esta coleta tem intervenções documentadas e não deve ser descrita como execução
inteiramente automática do protocolo inicial.
