# Alterações prospectivas H v07

Código congelado em `adendo_aprovado.json` antes da coleta. Implementação aditiva em `src/hibrido_v07` e `src/piloto_v07`; pacotes históricos preservados.

- **Vínculo da resposta:** o modelo retorna apenas conteúdo semântico no contrato `1.0-resposta-h07`. O adaptador gera IDs/revisão/hash/efeitos canônicos usando o pedido atual, conserva o JSON bruto e verifica a correspondência entre bruto, wire e análise interna, inclusive em cache. Campos técnicos devolvidos indevidamente são rejeitados, sem reparo permissivo. A resposta antiga não é convertida para v7.
- **Direção redundante:** a resposta exata contém o valor; o código deriva o sinal do delta e a direção neutra da quantidade absoluta. Direção sem magnitude continua sendo informação do modelo e exige lacuna/evidência. Inteiros negativos absolutos, booleanos, frações e falsos zeros com lacuna são rejeitados.
- **Cláusulas explícitas:** o pedido lista cláusulas locais, atributos, predicados e obrigações sintéticas já existentes. A resposta relaciona cada cláusula aos índices das propostas que a citam. Ausência de proposta não equivale a resolução; checklist vazio permanece pendente. Nenhum valor esperado ou gabarito entra no prompt.
- **Manutenção escopada:** encaminhamento de substituição de duração pode ser resolvido por manutenção aceita do mesmo responsável/alvo/atributo/unidade, somente com uma única cláusula de duração, referência à cláusula e condição confirmada. Ambiguidade, ausência de proposta ou regra diferente mantêm a pendência.
- **Fechamento por dimensão:** pendências novas têm dimensão explícita e evidência. Pendência apenas monetária preserva prazo quando todos os nós e requisitos temporais estão resolvidos; lacuna temporal bloqueia também custo. O caminho temporal preserva as validações do motor e só deixa de exigir o fechamento de readequação monetária. Ele não calcula nem publica custo. Pendências textuais históricas não são reinterpretadas.

As validações estruturais não demonstram suporte semântico. Classificação da pendência, aplicação de condição e escolha dos valores continuam alegações do modelo; resultados são condicionais e sujeitos à auditoria. As referências usadas na comparação são autorais, sem independência científica.

## Verificação antes da coleta

126 testes aprovados: 15 H07 (incluindo os contextos dos 15 casos), seis de carteira/integração, 27 H06, 19 H05, 22 SSE e 37 do motor. Os quatro controles vermelhos de v6 foram preservados em `reproduzir_v06.py`/`repro_v06.log`. São dois replays de respostas reais antigas e duas contraprovas sintéticas. Os testes verdes H07 usam somente fixtures sintéticas; a melhora empírica é aferida exclusivamente pelo novo piloto.

Os testes de carteira usam cópias temporárias do snapshot final v6; não leem credencial, não usam rede e não alteram a carteira real. Antes da coleta, a carteira real permanecia em 773 tentativas e US$ 3,208639690 comprometidos. Todos os 1.368 arquivos inventariados estavam intactos.
