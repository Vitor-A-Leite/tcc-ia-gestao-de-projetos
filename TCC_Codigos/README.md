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
