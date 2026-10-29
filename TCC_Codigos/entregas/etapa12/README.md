# Entregas da etapa 12

Abra **COMECE_AQUI.html** para acessar os três entregáveis. No macOS, também é possível abrir **ABRIR_DEMONSTRACAO.command**. Extraia o ZIP antes de navegar.

1. **Demonstração reproduzível:** demonstracao/index.html. Compare os três casos B/H/T, percorra os seis nós de cada execução H, abra fontes, cronograma e parcelas. A área de avaliação distingue referências de respostas e mostra falhas, denominadores e consumo.
2. **Material para redação:** material_tcc/Material_para_redacao_TCC.docx, com texto equivalente em Texto_e_tabelas.md. Contém arquitetura, método, resultados, diagnóstico das falhas e limites da evidência.
3. **Revisão do orientador:** revisao_orientador/Pacote_de_revisao.docx, com roteiro equivalente em Markdown. O formulário humano está em branco. As evidências necessárias acompanham a pasta evidencias.

## Como demonstrar

Selecione o primeiro caso e compare B com H/T. Em Acompanhar H, abra Validar leitura conjunta: o maior fim dos ramos é D14, seguido de cinco dias de validação, chegando a D19. No livro de parcelas, confira o apoio adicional de R$ 344,00.

No segundo caso, confira prazo +6 e custo indeterminado. B/T permanecem inválidos por omissão de justificativa; os brutos estão acessíveis apenas para diagnóstico. No terceiro, confira prazo zero e crédito de R$ 116,00. Em Ver avaliação, compare cobertura monetária 2/3 e acerto 2/2 para H.

Os passos são navegação sobre rastros salvos. Nenhuma previsão ou interpretação é executada novamente. A exportação baixa as evidências do caso selecionado; Imprimir usa a função do navegador.

## Verificação e execução local

JavaScript deve estar habilitado no navegador. Não há CDN, login, chave ou dependência de rede. Se uma política do navegador impedir abertura direta, use Python 3.9 ou superior:

```sh
python3 verificar_pacote.py
python3 servir.py --porta 8782
```

Abra http://127.0.0.1:8782. Encerre o servidor com Ctrl+C. Ele atende apenas loopback e não oferece endpoint de modelo. O verificador confere os arquivos do manifesto e a proveniência das cópias; não certifica a conclusão científica.

No repositório original, `python3 TCC_Codigos/entregas/etapa12/construir.py` reconstrói os dados da demonstração a partir dos arquivos congelados. O pacote já contém a projeção pronta e não depende do repositório completo.

## Custos e interpretação

Etapa 12: zero chamadas pagas. Compromisso acumulado preservado: US$ 4,567653865. Saldo sob o teto de US$ 5: US$ 0,432346135. Esses números incluem provisões e reservas; não representam confirmação da fatura.

São três casos sintéticos de um projeto e uma repetição por condição. As condições diferem em informação, cálculo externo, schema e número de chamadas. O resultado não comprova superioridade estatística ou efeito isolado do grafo. A revisão por agentes anterior à coleta não equivale a parecer humano.

As cópias históricas preservam sua redação e caminhos originais; links internos de relatórios históricos podem apontar ao repositório completo. Para navegar nesta entrega use o índice, o mapa de evidências e PROVENIENCIA.json. O pacote não contém credenciais nem o banco financeiro integral.

Consulte ACEITE_ETAPA12.md para os testes realizados e os limites da validação.
