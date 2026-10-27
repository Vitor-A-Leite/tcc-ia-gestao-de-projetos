# Referência autoral — leitura exclusiva de revisão/avaliação

Autoria: agente de dados etapa 2, 24/10/2026. Sem revisão humana independente e sem previsões de modelos. Não disponibilizar ao preditor. `gabaritos.json` contém as seis quantidades finais (prazo/custo base, novo e delta), estados por desfecho e cronogramas locais manuais; valores desconhecidos são null.

## Mapa de leitura e referência base

A = n_42be receber; B = n_915c preparar; C = n_a367 montar; D = n_08df testar; M = n_e659 entregar. V = n_73fa fornecedor; X = n_c820 componente. IDs são opacos nos inputs e não codificam família/caminho.

Fonte d_71ba L02–L04: X disponível D2; durações A1/B5/C3/D2/M0; pisos contratuais D0. Fonte d_aa83 L01–L03: requisito X em A e convergência A/B→C→D→M, FS0. Logo A=[2,3), B=[0,5), C=[max(0,3,5),8)=[5,8), D=[8,10), M=[10,10). Liberação A é max(piso0,disponibilidade2); as duas restrições coexistem.

Fonte d_482e L01: 100000+50000+150000+100000+100000=500000 centavos. Fonte d_59c1: AP fixo 100000; comprimento base 10; incidência base 10000×max(0,10−10)=0. Compromisso AP base já contém fixo mais incidência base, não um custo extra a somar outra vez. Sem crédito por antecipação. Custos fixos não dependem da duração salvo alteração expressa. Base D10/R$5.000 fecha entregas e obrigações por d_71ba L05, d_aa83 L03, d_482e L02 e d_59c1 L02.

## Oito conclusões conferíveis

| Caso | Fonte de aviso | Família principal | Marco novo / delta dias | Custo novo / delta BRL |
|---|---|---|---|---|
| k_b731 | d_82a4 L01 | Atraso absorvido por folga | D10 / 0 | 5.000 / 0 |
| k_09c2 | d_a725 L01 | Atraso final | D12 / +2 | 5.400 / +400 |
| k_e168 | d_3f60 L01 | Aumento de custo sem atraso | D10 / 0 | 5.300 / +300 |
| k_547a | d_047c L01 | Atraso sem aumento de custo | D12 / +2 | 5.000 / 0 |
| k_a92f | d_9b51 L01 | Alternativa disponível e já contratada | D10 / 0 | 5.150 / +150 |
| k_23d8 | d_f730 L01 | Informação insuficiente (aceite) | Indeterminado | Magnitude indeterminada; aumento ≥200 |
| k_f04b | d_6d38 L01 | Antecipação e crédito explícito | D9 / −1 | 4.900 / −100 |
| k_8c65 | d_58e2 L01 | Prazo exato / preço aberto | D12 / +2 | Magnitude indeterminada; aumento ≥200 |

As derivações completas por linha estão no JSON separado. Nos seis avisos de substituição com aceite (todos exceto k_23d8, excluído k_f04b por usar lote original), a montagem exige relacionar o aceite específico do aviso a d_8c23 L01: mantém três dias e não cria custo de readequação. Aceite é evidência textual, não flag já interpretada.

k_b731: D4 é disponibilidade, A termina D5. O máximo com B D5 mantém C D5; não subtrair folga outra vez. Troca em garantia, AP sem extensão: zero com suporte positivo.

k_09c2: A termina D7; C começa max(7,5)=7 e termina D10; D/M terminam D12. Delta final 12−10=2, não quatro dias da disponibilidade nem soma dos atrasos dos sucessores. Parcela nova p_07a4=20000 uma vez; AP final 100000+20000=120000. Total=100000+50000+150000+100000+120000+20000=540000. Os 40000 de delta não são outra parcela a somar.

k_e168: troca 30000=p_765e uma vez, sem mudança de datas; total 530000. k_547a: mesmas datas de k_09c2, mas não sua cobrança: aviso próprio garante troca e dispensa extensão até D12; AP permanece 100000. Não aplicar aditivo aos outros avisos.

k_a92f: Q suficiente/reservado/selecionado/aprovado D3 gera A D3–D4; B domina D5. Somar somente p_f48a=15000; não comprar simultaneamente reposição habitual D9. A seleção é documental, sem otimização automática.

k_23d8: A D6–D7 é exato, mas condição de C não resolvida. Não reutilizar duração padrão como duração autorizada após substituição sem aceite. Espera, duração e prazo final permanecem abertos. Para custo, d_482e L02 preserva as cinco parcelas fixas e L03 veda presumir créditos; d_f730 L01 adiciona 20000 e mantém as demais condições; d_59c1 L03 impede redução de AP por eventual antecipação. Pelo modelo aprovado de parcelas não negativas (etapa 1 seção 6), readequação e extensão só podem acrescentar custo, sem cláusula vigente de redução compensatória. Assim Cnovo=500000+20000+extensão_AP+readequação≥520000; delta≥20000. Custo fica direcao/aumento, com magnitude e total exatos null; 520000 é limite inferior sustentado neste caso, não total exato. Nenhum outro aviso pode completar a evidência do aceite.

k_f04b: B D0–D4; A D2–D3; C D4–D7; D/M D9. AP antecipado não gera crédito (delta incidência max(0,0−0)=0). Crédito comercial reduz p_34ad de 100000 a 90000; total 490000. Economia vem da cláusula de crédito, não de diária negativa.

k_8c65: A D6–D7; C D7–D10; D/M D12. Parcelas fixas 500000 e p_b17d=20000 identificadas; AP extensão pendente substitui a taxa antiga. Preço adicional não negativo torna delta ≥20000, direção aumento; não existe total exato. Prazo não depende dessa lacuna financeira. É evidência contraditória com taxa antiga resolvida por precedência expressa, não remoção silenciosa de linha base.

## Preparação da etapa 3 (sem executá-la)

Derivar somente das fontes: identificação fornecedor/componente contextual em d_71ba L02; requisito atividade→componente em d_aa83 L01, com regra específica que projeta disponibilidade componente→restrição em A; quatro precedências FS de d_aa83 L02. Preservar cinco restrições contratuais já identificadas e criar outra identidade para a disponibilidade requerida, sem sobrescrever o piso. Datas base individuais acima são conferência, não novas restrições. Criar catálogos de regra local de C e temporal de AP com fonte; aplicação das condições permanece interpretativa. Fonte temporal aponta M sem criar atividade AP ou aresta temporal reversa. Reconciliar aditivos somente no cenário vigente; mudança contratual requer validação/revisão, não aplicação cega como atraso.

Não foram criados objetos `edges`, grafo normalizado, regras executáveis ou serializadores. O fechamento das relações é documental. Cinco contratos/interface da etapa 1 permanecem a referência; normalização deve preencher estados/motivos/unidades/evidências completos sem afirmar que estes JSON autorais já os satisfazem.

## Cobertura e limites

As seis famílias solicitadas estão presentes; dois casos extras exercitam antecipação/crédito e estados distintos de prazo/custo. Há cadeia e convergência, folga, obrigação única, aditivo de dispensa, alternativa selecionada e lacunas de aceite/preço. Não há representatividade estatística, disputa de recursos, novo tipo temporal, custo em vários caminhos reais, extensão já incorrida na base ou política recalculavel_com_credito; essa última permanece prevista no contrato, sem alegação de cobertura aqui. IDs opacos e fontes neutras não garantem ausência de pistas semânticas: auditoria das views ainda é necessária. Referência do cenário completo não implica sustentação nas views B/H/T. O coordenador conferiu fontes, linha base e sete casos em 24/10/2026 e solicitou a correção da direção do custo de k_23d8; a releitura confirmou o aumento mínimo de R$200 sem alterar fatos. A conferência final deste ajuste e a aprovação do usuário permanecem pendentes. Essa conferência documental não é revisão humana independente.

## Registro da revisão do coordenador — 24/10/2026

Corrigida somente a conclusão de direção do custo em k_23d8 e suas descrições: indeterminação de magnitude não implica desconhecimento da direção quando parcelas fixas, acréscimos não negativos e ausência de créditos estão documentados. Rótulos A/B/C/D/AP das descrições de parcelas no input foram substituídos por nomes humanos; o mapeamento didático acima permanece somente nesta referência. Fontes primárias, eventos, IDs, valores e cronogramas não foram alterados. Conferência final dos ajustes pendente; usuário e revisão humana independente pendentes; etapa 3 não iniciada.
