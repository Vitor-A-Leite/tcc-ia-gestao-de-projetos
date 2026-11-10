# Versão atual do sistema

**Versão mais recente validada offline: [Alfa documental v2](etapas/alfa_documental_v2/README.md).** Código, motor incorporado, dados do Alfa, interface, testes e resultados próprios estão nessa pasta. A demonstração usa interpretações simuladas. O backend também executou um piloto real D02 com GPT-6 Luna high: totais equivalentes à referência, com uma proposta intermediária indevida identificada. Ver [relatório real](etapas/alfa_documental_v2/docs/RELATORIO_IA_REAL_20261110.md).

Na raiz do repositório:

```sh
python3.12 -B TCC_Codigos/etapas/alfa_documental_v2 servir --porta 8767
```

Abra `http://127.0.0.1:8767`. Para testar: substitua `servir --porta 8767` por `testar`. Nesta máquina, o intérprete verificado também está em `/Users/vaugusto/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3`.

Entrega: frontend e grafo 3D baseados na versão 1, seleção manual/assistida em simulação, quantidade livre de nós, pausa/continuação/cancelamento, cálculo integral e recomendações do Status Report. Os 45 testes atuais e os nove casos de desenvolvimento passaram offline; a autonomia foi conferida numa cópia isolada da pasta. A redução medida é de interpretações simuladas, não de custo ou latência real de API.

Versão anterior preservada e validada offline: [Alfa documental v1](etapas/alfa_documental_v1/README.md), com interpretação de todos os pontos. Sálvia e as demais etapas permanecem históricas. A v2 não depende dessas pastas para executar.

Resultados e limites: [relatório v2](etapas/alfa_documental_v2/docs/RELATORIO.md). Não mover pastas históricas nem ativar coleta paga com base apenas neste índice.
