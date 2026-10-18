# TCC — IA aplicada à gestão de projetos

O repositório é a fonte de código, dados e documentos do projeto. A execução é
local com Python 3.10 ou superior: não depende de Google Drive, Google Colab ou
Jupyter. Os notebooks também podem ser abertos em um editor local, mas não são
necessários para executar os comandos abaixo.

## Arquivos de trabalho

- `ProjetoTCCv01.ipynb`: preparação, conferência dos dados e demonstração local.
- `TCC_Baseline_LLM.ipynb`: baseline V2 com interpretação e previsão pelo LLM.
- `TCC 03_Arquitetura_Hibrida_com_API.ipynb`: interpretação pelo LLM e propagação pelo grafo e regras.
- `TCC_Codigos/src/`: implementação científica e configuração local.
- `TCC_Codigos/data/`: grafo, 36 cenários de referência e artefatos de gestão.
- `Planejamento/` e documentos acadêmicos na raiz: materiais de base.
- `TCC_Codigos/outputs/`: prompts e resultados produzidos localmente.

Os ZIPs são pacotes históricos. Use os arquivos de trabalho acima; extrair o ZIP
antigo de código sobre o projeto pode substituir as correções atuais.

## Preparar e testar sem API

Na raiz do repositório, com Python 3.10+:

```sh
python3 -m venv .venv
source .venv/bin/activate
python TCC_Codigos/scripts/test_offline.py
python TCC_Codigos/scripts/run_local.py setup
```

Os testes não exigem bibliotecas adicionais nem carregam credenciais. A rede é
bloqueada durante os testes. A preparação executa conferências, testes e exemplos
sobre os arquivos locais; não faz chamadas ao modelo.

## Experimentos com API — execução explícita

```sh
python -m pip install -r TCC_Codigos/requirements-experiments.txt
```

Configure `OPENAI_API_KEY` no `.env` da raiz ou exporte a variável no ambiente.
O arquivo local é privado e ignorado pelo Git. Variáveis já exportadas têm
precedência sobre o `.env`. Não coloque a chave em notebooks, saídas ou commits.
O carregador aceita linhas `KEY=value`, sem executar comandos ou expandir variáveis.

Os comandos seguintes **fazem chamadas à API e podem gerar cobrança**:

```sh
# Exemplo inicial e piloto de seis casos de cada condição:
python TCC_Codigos/scripts/run_local.py baseline --allow-api
python TCC_Codigos/scripts/run_local.py hybrid --allow-api

# Após revisar o piloto e congelar o protocolo: piloto e lote completo de 36 casos.
python TCC_Codigos/scripts/run_local.py baseline --allow-api --full
python TCC_Codigos/scripts/run_local.py hybrid --allow-api --full
```

As execuções gravam resultados em `TCC_Codigos/outputs/baseline_v2/` e
`TCC_Codigos/outputs/hybrid_v1/`. Repetir uma execução pode substituir os arquivos
dessa versão; preserve os resultados de cada rodada antes de repetir. Os dados
continuam no disco local entre sessões, sem sincronização com armazenamento externo.

`--full` controla as duas flags de execução completa dos notebooks; sem ele,
somente o exemplo e o piloto são executados. No editor de notebooks, as flags
continuam inicialmente falsas. Os 36 casos simulados dos testes validam a
implementação, não a qualidade do modelo ou a hipótese científica.

## GitHub Actions

O secret de repositório `OPENAI_API_KEY` pode ser usado por um workflow que o
mapeie explicitamente para a variável de ambiente. Ele não é baixado ao clonar o
repositório e não substitui o `.env` local. Cadastrar o secret não dispara
experimentos; nenhum workflow de execução paga foi criado.

## Visualização

Abra `TCC_Codigos/visualizacao/grafo_projeto.html` no navegador, sem servidor.
Instruções específicas em `TCC_Codigos/visualizacao/README.md`.

## Baseline estável V2 e conjuntos experimentais

O piloto usa somente os seis novos casos `DEV001`–`DEV006` em
`TCC_Codigos/data/scenarios_development_pilot.json` (caminho a partir da raiz).
Os 36 casos `S001`–`S036` de `scenarios_ground_truth.json` permanecem no test set
oficial. Prompt, modelo e ground truth não podem mudar após o congelamento
experimental. `RUN_FULL_EXPERIMENT` permanece falso por padrão.

Veja [o protocolo e a revisão do ground truth](TCC_Codigos/docs/baseline_v2_methodology.md), incluindo a limitação
de exposição histórica dos casos oficiais e a distinção entre a tag técnica
`baseline-v2-frozen` e a aprovação experimental pelos autores.
