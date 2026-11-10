# Contratos e decisões da v2

O pipeline recebe estado de projeto preparado e evento preparado. A interface trabalha com os casos cadastrados. Ela não cria eventos a partir de documentos arbitrários.

```text
grafo + documentos + evento
          │
     escolha manual ← sugestão simulada + confirmação
          │
   região conservadora e responsabilidades
          │
   fila topológica com interpretação local
          ├─ resultado vinculado em cache
          ├─ encaminhamento aceito → ampliação → contexto revalidado
          ├─ teto atingido → pendentes → escolha de continuação
          └─ cancelamento → parcial preservado
          │
  fechamento por dimensão + cálculo com grafo integral
          │
  comparação de afirmações do Status Report
```

## Identidades

`VERSION` identifica o software. O estado projetado possui `versao` do projeto, atualmente `1.0.0`, separada da versão `2.0.0` do pacote. A assinatura da sessão reúne grafo, documentos, evento, interpretação de simulação e arquivos de runtime. O contexto local ainda contém fontes, permissões, regras, estado vigente dos predecessores e sua identidade.

`Sessoes.preparar(...)` cria a sessão sem interpretar. `executar(id, ...)` inicia ou continua, `ler(id)` apenas consulta e `cancelar(id)` grava uma intenção independente. `selecionar(...)` permite corrigir entradas de uma sessão pronta, preservando o histórico da sugestão. `sugestao(...)` usa contrato e cache separados.

Uma `acao_id` já registrada não dispara novamente. Um bloqueio de arquivo impede duas execuções simultâneas. As gravações JSON são atômicas. Cada tentativa registra nó, contexto e estado; uma flag separada permite cancelar enquanto o interpretador está em voo. O cancelamento não é aprovação documental nem desfaz trabalho já consumido.

## Cobertura

O alcance inicial usa somente precedências temporais e responsabilidades financeiras explícitas. Arestas documentais e contextuais não viram precedências. O catálogo de responsabilidades global é mantido para validar encaminhamentos, mas cada contexto recebe sua projeção pertinente.

As regras locais exigidas para fechamento são aquelas cujo responsável está na região. Não se inventa uma confirmação de duração da montagem quando a montagem está fora da região do evento. A base matemática completa permanece no cálculo e no contexto dos predecessores externos. A exclusão é justificada pelas dependências cadastradas e não prova completude dos dados no mundo real.

Para retomar, o engenheiro seleciona pendentes. O cálculo mostra dependências adicionais; a falta de escolha de um predecessor exigido impede a interpretação do sucessor. O cache pode reproduzir análises aceitas sem nova solicitação, mas somente quando o hash completo coincide. Reanálises invalidam naturalmente os contextos dos sucessores quando mudam os valores usados.

Os estados de interface são `pronta`, `executando`, `pausada`, `concluida`, `cancelada`, `falha` e `obsoleta`. `concluida` significa fila processada, não que todos os valores sejam exatos: uma mudança sem preço pode concluir a interpretação e manter custo indeterminado. A completude de prazo/custo permanece explícita no resultado.

## Limites e transporte

`limite_nos_analise` aceita 1..N e conta nós distintos interpretados, inclusive entradas. `max_solicitacoes` conta tentativas locais, seletor e reanálises. Os demais campos são `max_tokens_entrada`, `max_tokens_saida`, `max_segundos` e `max_custo_centavos`.

O transporte habilitado nesta entrega é estritamente offline. Seus tokens, chamadas de API e custo são zero. O teto de tempo e o de solicitações são efetivamente exercitados. Os campos monetários/tokens preservam o contrato, mas não constituem validação de um controlador de gastos reais. O runtime bloqueia adapters reais; antes da coleta paga, implementar reserva transacional e reconciliação com a carteira canônica, conferindo a medição do provedor. Nenhuma carteira vazia foi criada para substituir o saldo acumulado.

O seletor é acionado por pedido explícito, registra tentativa antes do envio, aceita zero ou múltiplas sugestões e exige confirmação. Erros ficam vinculados ao mesmo pedido para impedir retries por duplo clique. A demo usa menções cadastradas como resposta manual; não finge inferência automática de IA.

## Autonomia e preservação

Os componentes incorporados usam imports relativos sob `alfa_documental_v2.src.vendor`. Não se adiciona `TCC_Codigos/src` ao caminho de importação. O carregador da entrada direta da pasta adiciona somente o diretório que contém a própria v2 para inicializar seu namespace; ele não importa o pacote anterior.

Dados de runtime ficam em `data/`; respostas de referência ficam em `avaliacao/`. O avaliador salva as previsões antes de ler as referências. Os casos finais reservados não foram copiados. O pacote foi copiado para diretório temporário e testado fora da árvore original, com módulos históricos ausentes de `sys.modules`.
