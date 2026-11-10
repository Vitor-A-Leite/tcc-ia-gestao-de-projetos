# Alfa documental v1.0.0

Etapa separada do TCC: preserva o Alfa original e a Sálvia e demonstra mudança documental → interpretação local → coordenação → cálculo → comparação documental → recomendação para validação humana.

## Abrir a demonstração

Na raiz do repositório, use o Python 3.10+ do ambiente existente:

```sh
.venv/bin/python -m TCC_Codigos.etapas.alfa_documental_v1 servir
```

Abra **http://127.0.0.1:8766**. No macOS, também pode executar [ABRIR_DEMONSTRACAO.command](ABRIR_DEMONSTRACAO.command). Se o servidor já estiver aberto, basta acessar o endereço. Ctrl+C encerra o servidor.

O [HTML local](web/index.html) abre diretamente no navegador para **reprodução de resultados salvos**. O modo **simulação offline** precisa do servidor Python e realiza novamente as 32 análises manuais simuladas, a validação H, o cálculo e a verificação. Cada execução interativa é salva em `runs/interativo/`, com nome único. O modo **IA real** está desabilitado, identificado como não autorizado. Não há dependência de CDN nem instalação adicional para a demo.

Roteiro sugerido:

1. D02: veja o aviso do fornecedor, D40 → D45, +R$ 1.500 e três recomendações. Reproduza os 32 passos ou avance pelo controle.
2. Clique em SUP_MOTOR, C_MOTOR, T_ASSEMBLY, TEST_LIFE e M_RELEASE. Inspecione fontes, entradas, efeitos, propostas e folgas. Ramos menores são dominados na convergência; o motor usa máximo.
3. Clique em DOC_CAD@1 e compare com T_CAD. O documento tem versão, trechos e relação `produz`; não é uma atividade temporal.
4. D01: atraso de um dia no motor é absorvido pela folga; o marco e o custo permanecem, mas o campo de disponibilidade do fornecedor precisa ser revisado.
5. D06: dois ensaios se alongam, mas o laboratório compartilhado é cobrado uma vez. D04: prazo/custo indeterminados. D09: custo indeterminado com prazo exato.
6. D07: o relatório já atualizado recebe zero recomendações. D08: mudança sem efeito também recebe zero. Abra a triagem de outros artefatos para ver as regras e pendências próprias.

## Executar e verificar

```sh
# Testes novos, com rede bloqueada:
.venv/bin/python -m TCC_Codigos.etapas.alfa_documental_v1 testar

# Novo resultado; caminho existente é recusado:
.venv/bin/python -m TCC_Codigos.etapas.alfa_documental_v1 simular D02 --saida /tmp/alfa-D02-novo.json

# Nove casos de desenvolvimento; resultados persistidos antes da avaliação:
.venv/bin/python -m TCC_Codigos.etapas.alfa_documental_v1 avaliar --saida /tmp/alfa-nova-rodada

# Histórico, carteira e entradas seladas:
.venv/bin/python -m TCC_Codigos.etapas.alfa_documental_v1 integridade

# Protocolo e orçamento, sem chamar API:
.venv/bin/python -m TCC_Codigos.etapas.alfa_documental_v1 protocolo-pago
```

`avaliar --particao final` está disponível para uma avaliação futura explicitamente decidida. **Não foi executado nesta entrega.** Os oito casos finais são autorais e reservados em outra pasta. Não usá-los para ajustar o algoritmo nem apresentá-los como revisão independente. A aplicação e as rotas HTTP só listam desenvolvimento.

## Arquivos e arquitetura

| Arquivo/pasta | Função |
|---|---|
| [AUDITORIA_INICIAL.md](AUDITORIA_INICIAL.md) | Localização do legado, capacidades e lacunas anteriores |
| [inputs/](inputs/) | Grafo, documentos, nove casos dev, oito reservados, simulações e referências separadas; hashes em SELO.json |
| [modelo.py](modelo.py) | Projeção tipada do grafo para o motor e normalização do aviso |
| [politica.py](politica.py) | Responsáveis, seleção de fontes e cobertura dos 32 pontos executáveis |
| [orquestracao.py](orquestracao.py) | Agenda H7.2 derivada, com projeção de responsabilidades por nó; legado intacto |
| [pipeline.py](pipeline.py) | Integração, rastros, folgas, efeitos financeiros e documentais |
| [simulacao.py](simulacao.py) | Operações manuais injetadas; nunca lê gabaritos |
| [cadastro.py](cadastro.py) | Cadastro de fontes textuais preparadas e versões imutáveis |
| [documentos.py](documentos.py) | Verificação do Status Report e decisão humana separada |
| [avaliacao.py](avaliacao.py) | Métricas por dimensão e por afirmação; falhas nos denominadores |
| [runs/dev_05/](runs/dev_05/) | Rodada offline entregue, brutos e métricas |
| [qa/](qa/) | Tentativas anteriores, falhas, testes e preflight em bytes |
| [RELATORIO.md](RELATORIO.md) | Resultados, limitações e conclusões admissíveis |
| [PROTOCOLO_PAGO.md](PROTOCOLO_PAGO.md) | Escopo, número de execuções, reserva e necessidade de autorização |

O contrato, parser, schema, adaptação `LocalV07R3`, reconciliação de encaminhamentos, fechamento e matemática de intervalos são reutilizados de `src/hibrido_v07_r3`, `hibrido_v05` e `motor_deterministico`. O fork da agenda muda a seleção do catálogo por nó; não altera o solver nem elimina nós/caminhos. Cada contexto recebe suas operações, vizinhos, entidades mencionadas e proprietários das parcelas citadas. O catálogo global completo continua no rastro. Limites insuficientes produzem resultado parcial e nós não consultados explícitos.

Fornecedores/componentes são pontos de disponibilidade no solver; os tipos de domínio permanecem no grafo. `supplies`, `required_for` e `precedes` são precedências FS0 na projeção sintética. `validated_by`, pessoas e áreas são contexto. Relações `descreve`, `estabelece_condicao`, `registra_situacao`, `comunica_mudanca`, `produz` e `revisa_versao` não propagam datas. Custos vêm de obrigações únicas e regras contratuais, não da quantidade de caminhos.

## Documentos e revisão humana

Disponível: **JSON UTF-8 de texto preparado**, com ID, versão, papel, autoria, flag sintético, trechos, localizadores e vínculos explícitos. O campo `afirmacao` registra entidade, campo, valor e unidade para comparar o Status Report. A extração de afirmações de prosa livre não foi implementada. TXT deve ser preparado/copiado para esse contrato; Word, PDF e OCR **não são importados automaticamente**.

```sh
.venv/bin/python -m TCC_Codigos.etapas.alfa_documental_v1 cadastrar-documento /tmp/documento-preparado.json --destino /tmp/registro-alfa
```

Use um documento de `inputs/documentos.json` ou `inputs/cenarios/dev/D02.json` como exemplo de contrato. O cadastro não modifica a baseline congelada nem inicia análise automaticamente. Novos cenários devem ligar explicitamente um aviso cadastrado, suas menções e a versão vigente dos registros. O motor rejeita versões incompatíveis e baseline inconsistente. Todos os parâmetros quantitativos desta extensão são sintéticos; fatos históricos do Alfa não foram reescritos.

Recomendações preservam valor/texto atual, alteração sugerida, justificativa, evidências, cálculo e versão base. `documentos.registrar_decisao(...)` permite registrar aprovação/rejeição em um **novo arquivo**, exigindo revisor e justificativa e recusando versão/trecho obsoleto. Não existe rotina de atualização do documento oficial: a decisão aprovada ainda deve ser executada por uma pessoa e cadastrada como nova versão. Nenhuma decisão humana foi emitida nesta entrega.

Status Report: comparação implementada e avaliada. Action Log, Risk Register e Decision Log: triagem e preservação implementadas; extração semântica, atualizações específicas e avaliação positiva permanecem pendentes. Atraso não cria automaticamente ação, risco ou decisão.
