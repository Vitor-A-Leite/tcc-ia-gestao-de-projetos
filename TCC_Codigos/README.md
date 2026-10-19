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

## Piloto isolado com acompanhamento

O executor abaixo reutiliza as funções e prompts dos notebooks, mas roda apenas
os seis casos do piloto por condição, sem repetir o S001 como teste extra. Não
modifica os prompts nem o protocolo. Ele exige uma pasta de saída nova e salva
cada resposta imediatamente. Em caso de falha da API, para sem repetir a chamada.

```sh
# Validação com respostas de referência injetadas e rede bloqueada:
python TCC_Codigos/scripts/run_pilots.py --mode simulated --output caminho/novo_simulado

# Exatamente seis chamadas por condição; pode gerar cobrança:
python TCC_Codigos/scripts/run_pilots.py --mode real --allow-api --output caminho/novo_real
```

São preservados manifestos com versões de pacotes, hashes dos arquivos,
modelo, prompt, IDs de resposta, uso de tokens e métricas do piloto. Os seis
casos não substituem o experimento completo de 36 cenários. Métricas simuladas
não são evidência de desempenho do LLM. O modo simulado requer as dependências
de experiments para gerar as tabelas, mas não usa credenciais nem rede.

## Protocolo V2 de suficiência de evidência

Há uma implementação separada para avaliar impacto em prazo e custo, distinguindo
impacto sustentado, ausência sustentada e informação insuficiente. As duas
condições usam o mesmo contrato e avaliador, com controle das evidências visíveis.
Veja [regras, limites científicos e execução](docs/protocolo_evidencias_v2.md).
Os exemplos são de desenvolvimento e aguardam revisão independente. A demonstração
não chama a API nem substitui os resultados do piloto anterior.

### Revisão de prazo e custo V2.1

Os [critérios revisados e limites da avaliação](docs/revisao_criterios_gabaritos_v2_1.md)
e os [gabaritos autorais dos 36 cenários](data/reference_sets/alfa_schedule_cost_v2_1_draft.json)
estão preparados para revisão independente. A auditoria é local, sem API:

```sh
.venv/bin/python TCC_Codigos/scripts/audit_schedule_cost_references.py --output TCC_Codigos/outputs/nova_revisao
```

O pacote exporta perguntas sem respostas e um caderno de revisão. Os custos permanecem
indeterminados por ausência de evidência; o conjunto ainda não é um benchmark equilibrado.
Esses arquivos não devem ser enviados ao runner V2.0 sem adaptação para medida e escopo.
