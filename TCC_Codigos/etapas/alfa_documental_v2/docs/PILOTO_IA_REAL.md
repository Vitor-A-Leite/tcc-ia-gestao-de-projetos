# Piloto com IA real

Autorização: mensagem do usuário de 10/11/2026, solicitando GPT-6 Luna com raciocínio high, evento JSON, entrada sugerida pela IA e máximo de nós. O executor do primeiro piloto é:

```sh
python3.12 -B -m TCC_Codigos.etapas.alfa_documental_v2.src.piloto_ia --rodar
```

Executar novamente gera outra rodada e pode gerar consumo; não é necessário repetir para consultar resultados existentes. O relatório e os JSON ficam em `outputs/ia_real_<data>/`.

O primeiro recorte é D02, atraso crítico do fornecedor de motor. O seletor recebe apenas evento e catálogo. A escolha inequívoca de um único nó sugerido é aceita pelo agente conforme a delegação expressa do usuário; ambiguidades interrompem o fluxo. A sessão mantém o teto de todos os 32 nós elegíveis. A região efetivamente percorrida depende das relações e dos encaminhamentos validados.

A nova execução não utiliza respostas prontas de simulação. O prompt, o JSON Schema por nó e os validadores H7.2 existentes são preservados. Os documentos e eventos continuam preparados em JSON. O resultado é salvo antes da leitura da referência autoral de D02. Casos finais reservados não entram neste piloto.

O modo real foi acrescentado ao backend e ao executor de piloto. A demonstração no navegador continua em simulação offline; seus botões não disparam chamadas pagas. Os controles de sessão podem ser exercitados pelo backend com o adaptador real, mas falhas reais de cancelamento/retomada ainda exigem avaliação própria.

## Consumo

Modelo `gpt-6-luna`, `reasoning.effort=high`, Responses API, sem fallback, retries ou ferramentas externas. Até 33 tentativas de inferência: sugestão mais até32 análises. Até64000 tokens de entrada contados pelo endpoint oficial e16000 tokens de saída por inferência. A contagem de entrada é uma requisição HTTP adicional, não uma segunda inferência.

Credencial reutilizada do arquivo local protegido `.env.piloto`; o segredo não é registrado nos resultados. O transporte envia a credencial somente à API oficial da OpenAI.

O ledger histórico é lido sem alterações. A v2 registra as reservas novas em `outputs/consumo_ia_real.sqlite`, preserva o comprometimento histórico e aplica teto acumulado de USD5. A sessão tem teto adicional de USD0,40. Uma reserva de USD0,015 precede cada tentativa; uso desconhecido mantém a reserva e impede novas chamadas. Valores de custo da API são em USD; valores de custo do projeto continuam em centavos de BRL.

Preços usados, consultados em10/11/2026: USD0,10/1M tokens de entrada, USD0,01/1M em cache e USD0,50/1M de saída. A estimativa usa o consumo informado pelo provedor e não substitui sua fatura. [Fonte oficial](https://developers.openai.com/api/docs/models/gpt-6-luna).

## Limites

Uma execução real de desenvolvimento não constitui validação científica geral. É necessário revisar o suporte semântico das recomendações, repetir casos, incluir eventos distintos e comparar alternativas com referências independentes. A interface3D não altera os resultados do motor.
