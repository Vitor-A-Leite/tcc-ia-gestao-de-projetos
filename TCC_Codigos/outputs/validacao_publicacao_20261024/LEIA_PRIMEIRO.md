# Validação de publicação — 24/10/2026

Após integrar a main remota a242901, a suíte offline executou 130 testes:
124 passaram e seis falharam. Não foram feitas chamadas à API.

As mesmas seis falhas foram reproduzidas executando test_notebook_baseline.py
sobre uma cópia limpa de origin/main a242901, extraída com git archive, sem
aplicar as alterações V2.2 ou do observatório. Portanto, são inconsistências
preexistentes entre os testes/documentação do baseline e os arquivos publicados.

Pendências do baseline:

- Rótulos atuais não coincidem com todos os registros da revisão de ground truth.
- Exemplos e pilotos dos notebooks ainda não atendem ao isolamento DEV exigido pelos testes.
- Hashes do snapshot não coincidem com os arquivos atuais.
- O prompt atual não coincide com a definição V2 congelada nos testes.
- O pacote ZIP não coincide com o notebook atual.

As inconsistências foram preservadas e registradas; gabaritos, snapshots e
resultados históricos não foram alterados para fazer testes passarem.
Esta publicação não deve ser interpretada como uma suíte inteiramente aprovada.
Os logs completos e summary.json registram as verificações. As validações
anteriores de 118/120 testes são históricas, anteriores à integração dos dez
testes adicionais do baseline vindos do remoto.
