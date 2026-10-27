# Bancada Íris — grafo normalizado de desenvolvimento v1

Derivação autoral da etapa 3, em 24/10/2026, entregue aguardando revisão. Fontes fictícias da etapa 2 aprovada; sem revisão humana independente. O snapshot de origem permanece intacto.

- `estado_projeto.json`: único input positivo da base normalizada; fontes de cinco documentos, entidades, atividades, relações e catálogos. Contém conhecimento relacional reservado H/T; não é contexto de baseline.
- `fontes/`: cópias literais somente dos cinco documentos base para auditoria das citações.
- `projecao_causal.json`: vista derivada para auditoria estrutural, sem cálculos, sem fatos adicionais.
- `manifesto.json`: proveniência SHA-256 dos nove arquivos efetivamente usados da etapa 2, autoria e fronteiras; fora do preditor. O registro de fontes original foi lido e filtrado positivamente por documento; nenhum aviso foi incorporado.
- `validar.py`: script específico stdlib, fora do preditor. Verifica estrutura e contraprovas, sem API, agenda ou cálculo por evento.

Executar da raiz do repositório:

```sh
python3 TCC_Codigos/data/desenvolvimento/projeto_minimo_grafo_v1/validar.py
```

O validador usa o snapshot irmão para conferir hashes, pisos e parcelas preservados. Não varrer recursivamente este pacote para preparar contexto. README, manifesto, script e projeção são documentação/validação, não inputs adicionais. Não há avisos, gabaritos ou datas pós-evento neste pacote. Nenhuma view B/H/T foi implementada: quatro fontes comuns preservam vínculos próprios dos contratos; d_aa83 é exclusiva H/T. O grafo não torna o conhecimento do baseline equivalente.

D10 e 500000 centavos são linha base declarada, ainda sem conferência por motor. Somente a soma das cinco parcelas é verificada automaticamente aqui. Conhecimento acrescenta `unidade` como metadado estrutural ao contrato aprovado; referências são objetos fonte/localizador. IDs novos são opacos, fixados nesta versão e rastreados nas fontes dos próprios objetos. Não há AnaliseNo, ResultadoNo ou ResultadoFinal executados. Liberação efetiva é máximo das restrições ativas, sem campo sobrescrevível.
