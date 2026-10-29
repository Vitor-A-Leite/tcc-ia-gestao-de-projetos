# Diagnóstico v6 → v7 por caso

Previsões originais; prazo em dias e custo em centavos. Referências autorais, sem independência científica.

| Caso / repetição | Prazo v6 | Prazo v7 | Custo v6 | Custo v7 |
|---|---:|---:|---:|---:|
| k_09c2 / 1 | indeterminado | 2 | indeterminado | 40000 |
| k_09c2 / 2 | 2 | 2 | 40000 | 40000 |
| k_0ca7 / 1 | 2 | 2 | 15000 | 15000 |
| k_0ca7 / 2 | 2 | 2 | 15000 | 15000 |
| k_23d8 / 1 | indeterminado | indeterminado | indeterminado | indeterminado |
| k_23d8 / 2 | indeterminado | indeterminado | indeterminado | indeterminado |
| k_42a9 / 1 | -2 | -2 | -15000 | -15000 |
| k_42a9 / 2 | -2 | -2 | -15000 | -15000 |
| k_547a / 1 | indeterminado | indeterminado | indeterminado | indeterminado |
| k_547a / 2 | indeterminado | indeterminado | indeterminado | indeterminado |
| k_6d82 / 1 | 2 | 2 | 15000 | 15000 |
| k_6d82 / 2 | 2 | 2 | 15000 | 15000 |
| k_8c65 / 1 | indeterminado | 2 | indeterminado | indeterminado |
| k_8c65 / 2 | indeterminado | 2 | indeterminado | direcao (aumento) |
| k_98f3 / 1 | -2 | -2 | 0 | 0 |
| k_98f3 / 2 | -2 | -2 | 0 | 0 |
| k_a064 / 1 | indeterminado | 0 | indeterminado | 0 |
| k_a064 / 2 | 0 | 0 | 0 | 0 |
| k_a92f / 1 | 0 | 0 | 15000 | 15000 |
| k_a92f / 2 | indeterminado | 0 | indeterminado | 15000 |
| k_b5e1 / 1 | 0 | 0 | 12345 | 12345 |
| k_b5e1 / 2 | 0 | 0 | 12345 | 12345 |
| k_b731 / 1 | indeterminado | 0 | indeterminado | 0 |
| k_b731 / 2 | indeterminado | 0 | indeterminado | 0 |
| k_d307 / 1 | indeterminado | indeterminado | direcao (aumento) | direcao (aumento) |
| k_d307 / 2 | indeterminado | indeterminado | indeterminado | direcao (aumento) |
| k_e168 / 1 | 0 | 0 | 30000 | 30000 |
| k_e168 / 2 | 0 | 0 | 30000 | 30000 |
| k_f04b / 1 | indeterminado | -1 | indeterminado | -10000 |
| k_f04b / 2 | -1 | indeterminado | -10000 | indeterminado |

## Casos sem dois valores exatos

### k_23d8 / 1

Estado: parcial. Referência: prazo indeterminado; custo direcao.

Lacunas finais: ["Autorização operacional pendente: n_a367", "Cobertura operacional incompleta de nós: n_08df, n_a367, n_e659", "Regra local de duração sem resolução operacional: u_813c", "Encaminhamento não resolvido: n_73fa -> n_a367 / substituir_duracao / n_a367", "Encaminhamento não resolvido: n_73fa -> n_a367 / substituir_restricao / r_6b23c0", "Encaminhamento não resolvido: n_c820 -> n_a367 / substituir_duracao / n_a367", "Regra local de custo sem resolução operacional: u_813c", "Encaminhamento não resolvido: n_73fa -> n_a367 / registrar_lacuna_custo / lacuna_1b49c15fa70a7896", "Encaminhamento não resolvido: n_c820 -> n_a367 / registrar_lacuna_custo / lacuna_1b49c15fa70a7896"].

Rejeições locais: [].

Rejeições operacionais: [{"no_id": "n_a367", "analise_id": "n_a367:r1:cc650a3c640cecca", "contexto_hash": "cc650a3c640cecca8d201dbc8a716f451f154bd15e8d8d988de6ac1c77d7e312", "operacao_estrutural": "rejeitada", "suporte_semantico": "nao_auditado", "motivos": ["Condição não confirmada pela interpretação", "Condição não confirmada pela interpretação"]}].

Pendências tipadas: [].

### k_23d8 / 2

Estado: parcial. Referência: prazo indeterminado; custo direcao.

Lacunas finais: ["Autorização operacional pendente: n_a367", "Cobertura operacional incompleta de nós: n_08df, n_a367, n_e659", "Regra local de duração sem resolução operacional: u_813c", "Encaminhamento não resolvido: n_73fa -> n_a367 / substituir_duracao / n_a367", "Encaminhamento não resolvido: n_915c -> n_a367 / substituir_duracao / n_a367", "Encaminhamento não resolvido: n_c820 -> n_a367 / substituir_duracao / n_a367", "Encaminhamento não resolvido: n_c820 -> n_a367 / substituir_restricao / r_6b23c0", "Regra local de custo sem resolução operacional: u_813c", "Encaminhamento não resolvido: n_73fa -> n_a367 / registrar_lacuna_custo / lacuna_1b49c15fa70a7896", "Encaminhamento não resolvido: n_915c -> n_a367 / registrar_lacuna_custo / lacuna_1b49c15fa70a7896", "Encaminhamento não resolvido: n_c820 -> n_a367 / registrar_lacuna_custo / lacuna_1b49c15fa70a7896"].

Rejeições locais: [].

Rejeições operacionais: [{"no_id": "n_a367", "analise_id": "n_a367:r1:59704096471957c2", "contexto_hash": "59704096471957c2179fa22827320d88103960583bcaa327f741e567fadf3525", "operacao_estrutural": "rejeitada", "suporte_semantico": "nao_auditado", "motivos": ["Condição não confirmada pela interpretação", "Condição não confirmada pela interpretação"]}].

Pendências tipadas: [].

### k_547a / 1

Estado: parcial. Referência: prazo exato; custo exato.

Lacunas finais: ["Encaminhamento não resolvido: n_73fa -> n_e659 / substituir_restricao / r_08f271"].

Rejeições locais: [].

Rejeições operacionais: [].

Pendências tipadas: [].

### k_547a / 2

Estado: parcial. Referência: prazo exato; custo exato.

Lacunas finais: ["Encaminhamento não resolvido: n_73fa -> n_e659 / substituir_restricao / r_08f271"].

Rejeições locais: [].

Rejeições operacionais: [].

Pendências tipadas: [].

### k_8c65 / 1

Estado: parcial. Referência: prazo exato; custo direcao.

Lacunas finais: ["Pendência operacional n_e659: O preço total da extensão não foi informado; a taxa anterior não vigora e não há taxa substituta conhecida."].

Rejeições locais: [].

Rejeições operacionais: [].

Pendências tipadas: [{"no_id": "n_e659", "dimensao": "custo", "motivo": "O preço total da extensão não foi informado; a taxa anterior não vigora e não há taxa substituta conhecida.", "evidencias": [{"fonte_id": "f_6ffaeeffa7", "localizador": "L01"}]}].

### k_8c65 / 2

Estado: parcial. Referência: prazo exato; custo direcao.

Lacunas finais: ["Preço da extensão desconhecido"].

Rejeições locais: [].

Rejeições operacionais: [].

Pendências tipadas: [].

### k_d307 / 1

Estado: parcial. Referência: prazo indeterminado; custo direcao.

Lacunas finais: ["A nova duração não foi fixada; pode ser qualquer inteiro não negativo."].

Rejeições locais: [].

Rejeições operacionais: [].

Pendências tipadas: [].

### k_d307 / 2

Estado: parcial. Referência: prazo indeterminado; custo direcao.

Lacunas finais: ["A nova duração não foi fixada; pode ser qualquer inteiro não negativo."].

Rejeições locais: [].

Rejeições operacionais: [].

Pendências tipadas: [].

### k_f04b / 2

Estado: parcial. Referência: prazo exato; custo exato.

Lacunas finais: ["Regra local de duração sem resolução operacional: u_813c", "Regra local de custo sem resolução operacional: u_813c"].

Rejeições locais: [].

Rejeições operacionais: [].

Pendências tipadas: [].
