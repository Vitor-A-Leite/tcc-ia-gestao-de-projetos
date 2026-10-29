# Reprodução da validação offline

Executar a partir da raiz do TCC. Nenhum comando abaixo lê credencial ou faz chamadas de inferência. Os testes de carteira criam cópias temporárias do snapshot final da v7 inicial.

```sh
PYTHONPATH=TCC_Codigos/src python3 -m unittest discover -s TCC_Codigos/tests/etapa9_piloto_v07_r2 -v
```

Os testes de schema usam o pacote independente **jsonschema==4.25.1**. Nesta execução, ele foi instalado apenas em `/private/tmp/tcc-v07-jsonschema`; não foi adicionada dependência ao código de produção. Para reproduzir, disponibilizar a mesma versão em um ambiente de testes e executar:

```sh
PYTHONPATH=TCC_Codigos/src:/private/tmp/tcc-v07-jsonschema python3 -m unittest discover -s TCC_Codigos/tests/etapa9_h_v07_r2 -v
```

Resultados: 20 testes H R2 e seis de carteira/integração aprovados. O teste adicional `teste_schema_transporte.log` verifica que a contagem e a geração recebem exatamente o mesmo schema. A rodada anterior conserva 126 testes aprovados e quatro controles vermelhos v6, estes deliberadamente falhando ao reproduzir os defeitos antigos.

O teste de duas respostas reais altera somente a marca de versão da fixture para isolar a restrição de escopo; as operações externas permanecem iguais e são rejeitadas por `maxItems=0`. Isso é contraprova offline, não reparo nem reclassificação das respostas coletadas. A confirmação empírica inicial aparece em `confirmacao_escopo_primeira_resposta.json` (call 792), enquanto calls 775/785 permanecem inválidas na rodada inicial.

Após a coleta encerrar, os scripts `avaliar_coleta.py`, `resumir.py`, `comparar.py`, `auditar_restantes.py`, `verificar_integridade.py` e `gerar_relatorio.py` processam resultados preservados. Não chamam API. O avaliador recusa rodar enquanto o coletor mantém o lock; a normalização confere proveniência e o fechamento por dimensão, sem alterar previsões.

A referência é autoral. A auditoria técnica desta etapa verifica os mecanismos e documenta falhas; a revisão independente continua pertencendo à etapa 10.
