# Bancada Íris — pacote autoral de desenvolvimento v1.0

24/10/2026. Rascunho revisável da etapa 2. Projeto e documentos inteiramente fictícios, de autoria do agente de dados. Não são fatos do Alfa histórico, casos finais inéditos, benchmark independente ou previsões coletadas. A conferência autoral não substitui revisão humana independente.

São sete entidades (fornecedor, componente, quatro atividades e marco), cinco parcelas base, treze documentos primários e oito acontecimentos independentes. Cada execução futura parte do mesmo snapshot v1.0 e lê exatamente um aviso. A linha base é D10 e 500000 centavos (R$5.000). Não há variantes de linha base.

| Arquivo | Propósito / fronteira |
|---|---|
| `inputs/base.json` | Cadastro autoral de atributos, parcelas, restrições contratuais e linha base declarada; preparado para normalização. |
| `inputs/cenarios.json` | Somente avisos e metadados de evidência/vigência, sem impactos finais ou classificações de família. |
| `inputs/fontes.json` | Registro de 25 trechos literais com documento, versão e localizador. É índice de armazenamento; nunca enviar integralmente ao preditor. |
| `inputs/fontes/*.txt` | Treze fontes primárias fictícias. Quatro comuns, uma relacional e oito avisos isolados. |
| `manifesto.json` | Controle de autoria, destinação e lista positiva de carregamento, fora do contexto preditivo. |
| `referencias/gabaritos.json` | Conclusões e cronogramas manuais autorais, exclusivamente para revisão/avaliação. |
| `referencias/DERIVACAO_E_COBERTURA.md` | Contas, cobertura, mapeamento de IDs, limites e preparação da etapa 3; proibido ao preditor. |
| `referencias/VERIFICACAO.md` | Evidência de verificações locais e limitações. |
| `referencias/hashes.json` | Integridade SHA-256 dos demais arquivos do pacote, sem autorreferência. |

`inputs/` contém fontes com destinação distinta, não uma view experimental pronta. O carregador futuro deve usar lista positiva por caso/documento/trecho e condição, sem varredura recursiva. Não carregar outros avisos, referências, README, manifesto ou documentos de desenvolvimento. As referências estão fisicamente separadas, mas essa separação não implementa controle de acesso: a integração futura precisa impor a fronteira.

A fonte relacional `d_aa83` destina-se a H/T. As fontes comuns contêm vínculos necessários ao significado de contratos/avisos e o vínculo contextual fornecedor/componente; devem ser inventariados, sem alegar igualdade de conhecimento. Etapa 3 deverá decidir a decomposição auditável de trechos mistos e produzir relações/regras das mesmas fontes, preservando o que é genuinamente comum. Nenhum serializador de views foi criado.

Não há `EstadoProjeto` executável completo: faltam normalização de Conhecimento, relações, restrição derivada da disponibilidade e catálogos operacionais. Campos autorais não são nova versão dos cinco contratos aprovados; são material de entrada para conversão posterior. Não há grafo operacional, motor, API, notebook ou integração com o legado.

A montagem exige interpretar o aceite do laudo em cada aviso de substituição junto à instrução técnica. Não há flag de condição satisfeita nem duração pós-evento preenchida. No aviso sem aceite, os demais avisos não podem fornecer o aceite ausente. No aditivo de preço aberto, a taxa original continua no snapshot base, mas está expressamente sem vigência para a extensão desse cenário; não há taxa substituta em outro atributo.
