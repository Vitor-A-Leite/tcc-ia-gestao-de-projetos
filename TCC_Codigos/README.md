# Códigos do TCC — Semanas 1 a 4

Protótipo experimental para analisar impactos de eventos não estruturados em artefatos de gestão de projetos.

## Estrutura

- `src/tcc_agent/`: núcleo do protótipo.
- `data/`: Projeto Alfa, artefatos e 36 cenários de ground truth.
- `scripts/`: demonstração, geração de prompts e avaliação.
- `tests/`: testes automatizados.
- `outputs/`: local para prompts, respostas do LLM e métricas.

## Requisitos

Python 3.10 ou superior.

Opcional para testes:

```bash
pip install -r requirements.txt
```

## 1. Executar a demonstração da arquitetura híbrida

Na pasta raiz:

```bash
python scripts/demo_hybrid.py
```

## 2. Gerar os 36 prompts do baseline

```bash
python scripts/generate_prompts.py
```

Os prompts serão gravados em `outputs/prompts/`.

## 3. Salvar respostas de um LLM

Crie `outputs/predictions/` e salve um JSON por cenário, por exemplo `S001.json`.

Formato esperado:

```json
{
  "event_type": "delay",
  "primary_entity": "SUP_MOTOR",
  "related_entities": ["C_MOTOR"],
  "affected_artifacts": ["risk_register", "status_report"],
  "impacted_entities": ["C_MOTOR", "T_ASSEMBLY"],
  "responsible": null,
  "due_date": null,
  "effective_date": null
}
```

## 4. Avaliar o baseline

```bash
python scripts/evaluate_predictions.py
```

O resultado será salvo em `outputs/evaluation.json`.

## 5. Rodar testes

```bash
pytest -q
```

## Observação metodológica

O código do baseline não chama automaticamente nenhuma API. Isso é intencional: permite escolher o LLM, registrar versão/modelo/parâmetros e preservar a reprodutibilidade do experimento.

## Visualizar o grafo do projeto

Abra [o explorador interativo offline](visualizacao/grafo_projeto.html) no navegador.
Há busca, zoom, legenda e exploração de relações direcionadas. Para regenerar e
entender a navegação, veja [as instruções da visualização](visualizacao/README.md).

## Testes offline do notebook 3 e do pipeline

Com Python 3.10 ou superior, sem instalar pacotes e sem usar a chave da API,
a partir da raiz deste projeto:

```bash
python3 TCC_Codigos/scripts/test_offline.py
```

O comando executa os testes originais e as regressões do notebook 3. A rede é
bloqueada durante os testes. As funções são extraídas diretamente das células do
notebook; a instalação de pacotes e a configuração real da API não são executadas. Respostas do cliente OpenAI são simuladas, inclusive para os
36 cenários de referência. A apresentação em DataFrame é substituída por uma
lista nos testes; isso valida a lógica, mas não a interface do Colab nem o LLM.

Eventos `informational` não geram entidades impactadas, documentos ou caminhos.
A avaliação completa exige um registro por ID de cenário, sem faltantes,
duplicatas ou IDs desconhecidos; tentativas que falharam não são removidas.
A validação da interpretação rejeita listas nulas, IDs inválidos, responsáveis
que não sejam pessoas, datas inválidas e confiança fora do contrato.
Registros de erro de interpretação preservam a resposta bruta, o ID da resposta,
o tempo e a etapa da falha para auditoria.

## Credenciais locais

A chave local fica em `.env` na raiz superior do projeto TCC, fora do notebook e
ignorada pelo Git. O arquivo deve permanecer privado. Os testes offline não o
carregam. Os experimentos locais carregam esse arquivo automaticamente. A execução e os
resultados usam apenas a cópia local do repositório. O secret de GitHub Actions
é separado e só fica disponível a workflows que o referenciem explicitamente.

## Execução exclusivamente pelo repositório

Consulte o README da raiz para preparar o ambiente local. Não é necessário
usar Drive, Colab ou Jupyter. O comando `scripts/run_local.py` executa os notebooks
como Python comum e resolve os caminhos relativos ao repositório. Os experimentos
requerem `requirements-experiments.txt`; chamadas reais exigem `--allow-api`.

## Baseline estável V2 e conjuntos experimentais

O piloto usa somente os seis novos casos `DEV001`–`DEV006` em
`TCC_Codigos/data/scenarios_development_pilot.json` (caminho a partir da raiz).
Os 36 casos `S001`–`S036` de `scenarios_ground_truth.json` permanecem no test set
oficial. Prompt, modelo e ground truth não podem mudar após o congelamento
experimental. `RUN_FULL_EXPERIMENT` permanece falso por padrão.

Veja [o protocolo e a revisão do ground truth](docs/baseline_v2_methodology.md), incluindo a limitação
de exposição histórica dos casos oficiais e a distinção entre a tag técnica
`baseline-v2-frozen` e a aprovação experimental pelos autores.
