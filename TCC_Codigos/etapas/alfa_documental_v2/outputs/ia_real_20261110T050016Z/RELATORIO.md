# Piloto real Alfa v2 — GPT-6 Luna high



Data UTC: 2026-11-10T05:00:52.102054+00:00. Cenário D02; N=1, uma execução.



Estado da sessão: pausada.

Erro do fluxo: nenhum.

Equivalência com referência autoral: False.



## Resultado observado



Prazo: {'estado': 'indeterminado', 'valor': None, 'evidencias': [], 'lacunas': ['Consumo real desconhecido; execução interrompida sem novas chamadas.'], 'motivo': 'Consumo real desconhecido; execução interrompida sem novas chamadas.'}

Custo do projeto (centavos BRL): {'estado': 'indeterminado', 'valor': None, 'evidencias': [], 'lacunas': ['Consumo real desconhecido; execução interrompida sem novas chamadas.'], 'motivo': 'Consumo real desconhecido; execução interrompida sem novas chamadas.'}

Recomendações documentais: 1.



## Consumo real



```json

{
  "chamadas_api": 4,
  "tokens_entrada": 13507,
  "tokens_saida": 2279,
  "custo_api_usd": 0.0024902,
  "segundos": 35.708148916004575,
  "uso_desconhecido": true,
  "comprometido_usd": 0.0124902,
  "historico_comprometido_usd": 4.567653865,
  "tempo_total_s": 35.983
}

```



Custo em USD calculado pelo uso retornado e preços oficiais; não é uma fatura. Reservas desconhecidas não são tratadas como consumo zero. O histórico financeiro anterior permanece intacto e integra o teto.



## O que funcionou e o que falhou



A execução usa o serviço OpenAI, com saída estruturada e validação independente; não lê respostas manuais de simulação. Sugestão, seleção, resultado e chamadas ficam registrados separadamente.

Os números acima e os arquivos comparacao.json/erro.json determinam o sucesso deste piloto. Respostas inválidas ou pendências não foram reparadas silenciosamente.



## Melhorias e próximos passos



- Auditar semanticamente justificativas e evidências com o orientador; equivalência numérica não prova validade de toda justificativa.

- Expandir a coleta aos demais eventos, com repetições e referências revisadas, sem alterar prompts a partir dos casos finais reservados.

- Comparar seleção manual, sugestão por IA e cobertura completa com os mesmos fatos; medir qualidade e custo em conjunto.

- Testar falhas reais de rede, cancelamento em voo e retomada sem cobranças duplicadas em piloto separado.

- Integrar a visualização das sessões reais no frontend e distinguir simulação de execução real em todos os rótulos.

- Ampliar a avaliação documental além das cinco afirmações preparadas do Status Report; manter ausência de dados explícita.



## Limites



JSON estruturado e grafo previamente cadastrado. Não importa ata livre/áudio/PDF, não altera documentos oficiais e não constitui uma validação de todos os cenários. Nenhum fallback de modelo ou retry automático foi usado.



[Documentação oficial do modelo](https://developers.openai.com/api/docs/models/gpt-6-luna).
