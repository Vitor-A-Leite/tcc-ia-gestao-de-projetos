# Validação e reprodução offline — v7 revisão 7.2

Executar os comandos na raiz `TCC`. Nenhum dos comandos abaixo chama a API. O coletor usa apenas biblioteca padrão; `jsonschema` é dependência de teste independente, fixada em `tests/etapa9_h_v07_r3/requirements.txt`. Versões efetivamente usadas estão em `ambiente_testes.json`.

## Testes executados antes da coleta

23 testes H e seis de carteira/integração aprovados. Logs: `testes_h07_r3.log` e `testes_carteira.log`.

```sh
python3 -m pip install --target /tmp/tcc-v07-jsonschema -r TCC_Codigos/tests/etapa9_h_v07_r3/requirements.txt
PYTHONPATH=TCC_Codigos/src:/tmp/tcc-v07-jsonschema python3 -m unittest discover -s TCC_Codigos/tests/etapa9_h_v07_r3 -v
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9_piloto_v07_r3 -v
```

Os testes cobrem vínculo de contexto, cache, escopo, checklist de cláusulas, manutenção com condição confirmada, bloqueio de condições incertas, independência entre prazo e pendência de custo, conhecimento indeterminado/direcional, redução de prazo, crédito contratual, tradução de operações e 112 contextos de desenvolvimento. Fixtures prescritas verificam o código; não constituem previsões reais.

## Encerramento e reprodução dos artefatos

Depois do término do coletor, `verificar_integridade.py` compara a carteira com `ledger_antes.sqlite`, confere arquivos e código congelado e cria `ledger_final.sqlite`. Não executar a avaliação antes desse snapshot. O verificador confronta o estado vivo no momento do encerramento; a análise usa exclusivamente o snapshot final preservado.

```sh
PYTHONPATH=TCC_Codigos/src python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/verificar_integridade.py
PYTHONPATH=TCC_Codigos/src python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/avaliar_coleta.py
python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/resumir.py
python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/comparar.py
python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/auditar_restantes.py
python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/triagem_todas_condicoes.py
python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/comparar_incerteza.py
PYTHONPATH=TCC_Codigos/src python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/auditar_erros_globais.py
python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/consolidar_auditoria.py
python3 TCC_Codigos/outputs/etapa9_piloto_v07_r3_20261028/gerar_relatorio.py
```

As etapas derivadas podem ser reproduzidas com o snapshot final e os inputs originais preservados. Normalização reconstrói as validações do contrato e a autorização, incluindo proveniência das respostas e mapeamento de operações. Denominadores, MAE e custo de inferência são conferidos também por cálculo separado; custos usam aritmética racional com os preços registrados. Isso é independência de cálculo, não independência científica de autoria.

`notas_auditoria_manual.json` e `auditoria_lacunas_fontes.json` registram a inspeção técnica das evidências. A revisão independente das referências, inferibilidade por view e suporte semântico continua reservada à etapa 10.
