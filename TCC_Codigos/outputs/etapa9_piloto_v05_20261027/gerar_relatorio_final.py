"""Apresentação pós-coleta. Nunca altera previsão, carteira ou referências."""
from pathlib import Path
import json,sqlite3
from decimal import Decimal
O=Path(__file__).parent;d=json.loads((O/'resumo_descritivo.json').read_text());b=d['carteira'];acc=json.loads((O/'contabilidade_e_erros.json').read_text())
W=O.parent/'etapa9_piloto_real_aprovado_20261026';db=sqlite3.connect('file:'+str(W/'ledger.sqlite')+'?mode=ro',uri=True)
states=dict(db.execute('SELECT estado,count(*)FROM slots_v05 GROUP BY estado').fetchall());n=states.get('terminado',0);paradas=d['paradas_retomada'];integrity=json.loads((O/'integridade_final.json').read_text())
def usd(x):return f'{Decimal(x)/Decimal(10**9):.9f}'.replace('.',',')
def num(x):return '—'if x is None else f'{x:g}'
rows=[];comparison=[];lat=[]
for c in 'BHT':
 p=d['por_condicao'][c];m=p['metricas'];pr=m['prazo'];co=m['custo'];np=acc['por_condicao'][c]['N_nao_iniciados']
 rows.append(f"| {c} | {p['registros']}/30 | {np} | {pr['cobertura_numerica']['n']}/30 | {co['cobertura_numerica']['n']}/30 | {num(pr['erro_numerico']['MAE'])} ({pr['erro_numerico']['n']}) | {num(co['erro_numerico']['MAE'])} ({co['erro_numerico']['n']}) |")
 lat.append(f"| {c} | {p['chamadas']} | {p['latencia_chamada_s']['n']} | {num(p['latencia_chamada_s']['mediana'])} | {num(p['latencia_slot_s']['mediana'])} | {usd(p['inferencia_conhecida_nanoUSD'])} | {usd(p['comprometido_nanoUSD'])} |")
 cmp=p['comparacao_v04'];comparison.append(f"| {c} | {cmp['prazo']['cobertura_v04']['n']}/30 → {cmp['prazo']['cobertura_v05']['n']}/30 | {cmp['custo']['cobertura_v04']['n']}/30 → {cmp['custo']['cobertura_v05']['n']}/30 | {json.dumps(p['estados'],ensure_ascii=False)} |")
status='90/90 slots encerrados'if n==90 else f'parada com {n}/90 slots encerrados'
text=f'''# Etapa 9 — piloto v05: {status}

27/10/2026, America/Sao_Paulo. **Integração v05 e coleta autorizada entregues para revisão.** O primeiro B falhou por DNS no ambiente restrito antes de inferência; os89slots pendentes foram continuados em fase separada com rede escalada. A tentativa273, seu resultado e a parada original permanecem intactos, sem replay. Estado final: {json.dumps(states,ensure_ascii=False)}. Paradas da fase de rede: {json.dumps(paradas,ensure_ascii=False)}. Etapas10/11 não iniciadas.

## Escopo e preservação

O usuário aprovou as correções v05 e outro piloto sob o **mesmo teto acumuladoUS$5**. Nova coorte90IDs:15casos×B/H/T×2, mesma ordem, inputs/views e parâmetros. gpt-6-luna, High, streaming, Standard/cache30m, saída total≤25000, entrada por contagem oficial≤16000, deadlineTOTAL180s contando contagem+geração, H≤8análises/chamadas e1500s, zero retries/fallback. Até300tentativas novas contando273; teto operacional global572; guarda monetária prevalece. Nenhum prompt, protocolo científico ou código congelado foi alterado durante a coleta.

H usa formato5.0/schema2/política5/fronteira2.0-h e avaliação isolada2.0-manifesto-h05. B/T mantêm contratos/payloads científicos anteriores. Código aditivo em `src/piloto_v05` e `src/retomada_v05`; carteira canônica continua `etapa9_piloto_real_aprovado_20261026/ledger.sqlite`. Os adendos persistidos registram as autorizações, assinaturas e IDs permitidos. Não houve mudança/reclassificação de resultados v04 ou acesso a gabaritos pelo preditor.

## Cobertura e precisão contra referências autorais

| Condição | Registros | Não iniciados | Prazo exato | Custo exato | MAE dias (n) | MAE centavos (n) |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

N=30 por condição. MAE inclui somente previsão exata válida com verdade exata; não mede desempenho nos demais slots e nunca transforma ausência em zero. Dados completos: `normalizacao.json`, `avaliacao_autoral.json` e `referencias_avaliacao_autoral.json`. Slots não iniciados são classe operacional erro no avaliador, não chamadas efetivamente falhadas. Estados `ok`/`parcial` descrevem execução/contrato, não suporte semântico. Referências autorais sem validação independente e inferibilidade por view pendente limitam qualquer conclusão científica.

## Latência e custo incremental

| Condição | Tentativas | Latências observadas | Mediana por chamada s | Mediana por slot s | Inferência conciliadaUSD | ComprometidoUSD |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(lat)}

Latência observada por chamada inclui contagem+inferência+adaptação, não velocidade pura do modelo. H agrega várias chamadas por slot. Valores ausentes não foram imputados. O B inicial inclui falhaDNS~0,38s sem inferência; seu tempo não é latência do modelo. O custo comprometido inclui provisões e reservas desconhecidas; só uso conciliado sustenta custo de inferência conhecido. `resumo_descritivo.json` conserva medidas e denominadores; `contabilidade_e_erros.json` contém conferência monetária independente.

## Comparativo descritivo v04→v05

| Condição | Cobertura exata prazo | Cobertura exata custo | Estados v05 |
|---|---:|---:|---|
{chr(10).join(comparison)}

B/T foram executados novamente com algoritmos e contextos preservados: suas diferenças são novas realizações do modelo, sem atribuição às correções H. Mudaram contrato/prompt/fechamento H; coleta ocorreu em outro momento e inclui falhaDNS e diferenças de geração/cache. O comparativo é descritivo, sem teste causal ou alegação de superioridade. Resultados v04 originais continuam intactos: Hexato2/30 correspondia ao mesmo caso de impactozero em duas repetições. CustoTv04 tinha22exatos mas21pares elegíveis: T/k_d307/rep1 previu2500centavos exatos frente a referência de aumento/limite inferior2500 sem totalexato, uma questão de falsa precisão para revisão.

## Diagnóstico H e falsa precisão

Análises H: `{json.dumps(d['analises_H'],ensure_ascii=False)}`. Fechamentos: `{json.dumps(d['fechamentos_H'],ensure_ascii=False)}`. Notas diagnósticas locais preservadas: {d['notas_diagnosticas_H']}. Erros por execução e registros originais estão nos JSON; nenhum foi reparado, convertido ou reenviado.

O primeiro H/k_09c2/rep1 ilustra uma limitação de escopo:4análises passaram o contrato, mas n_73fa e n_42be declararam pendências por não terem permissão para alterar a disponibilidade do componente ou lançar p_07a4. Os contextos confirmam essas permissões locais ausentes. Ao mesmo tempo n_c820 tinha as permissões e propôs D6 e20000centavos; o fechamento reconciliou p_07a4. As fontes já continham data,valor eaceite. Portanto, essa pendência não comprova falta factual global: há possível atribuição de responsabilidade de outro nó ao nó corrente, que o fechamento conservador não resolve. Isso bloqueou downstream e a cláusula u_813c. `diagnostico_primeiro_H.json` preserva contexto, permissões, propostas e hashes para revisão. Não se alterou o protocolo para melhorar esse resultado.

As pendências H estão preservadas por nó em `resumo_descritivo.json/pendencias_H`. Classes lexicais: `{json.dumps(d['classes_lexicais_pendencias'],ensure_ascii=False)}`; esse agrupamento por palavras não é auditoria semântica. Revisar separadamente fato realmente ausente, limite local de permissão e atribuição de obrigação alheia ao nó.

Há **{len(d['suspeitas'])} previsões exatas divergentes ou diante de referência nãoexata** sinalizadas em `resumo_descritivo.json/suspeitas`. São candidatas à revisão de erro/falsa precisão, não adjudicação semântica automática. Ausência de candidato não prova suporte. O contrato exige stringpara justificativa e não converte listas; confirma ausência no escopo da cláusula, preservando outras obrigações; incidência temporal usa cronograma final. `lacunas` local virou nota, e fatos realmente ausentes precisam de propostas tipadas ou `pendencias_operacionais`. Omissão/má classificação pelo modelo pode gerar falsa precisão; citação/hash e contrato válido não comprovam a conclusão.

## Carteira global final

| Parcela | USD |
|---|---:|
| Comprometido anterior (272tentativas) | 1,206550975 |
| Comprometimento incremental desta coorte | {usd(b['comprometido_nanoUSD']-1206550975)} |
| Inferência incremental conhecida | {usd(b['inferencia_conhecida_nanoUSD']-488550975)} |
| Inferência conhecida acumulada | {usd(b['inferencia_conhecida_nanoUSD'])} |
| Reserva de inferência desconhecida acumulada | {usd(b['reserva_inferencia_desconhecida_nanoUSD'])} |
| Provisão hipotética de contagem acumulada | {usd(b['provisao_contagem_nanoUSD'])} |
| **Comprometido acumulado** | **{usd(b['comprometido_nanoUSD'])}** |
| **Saldo interno sobUS$5** | **{usd(b['saldo_nanoUSD'])}** |

{b['tentativas']}tentativas acumuladas; {b['custos_desconhecidos']}custos não conciliados. As12reservas desconhecidas anteriores e a reserva integral da273 permanecem. Provisão de contagem não é tarifa publicada/cobrança comprovada. Preços históricos Standard: US$0,10/M entrada,0,01/M cacheleitura,0,125/M escrita30m e0,50/M saída; raciocínio já incluído na saída. Reserva máxima de inferênciaUS$0,0145+provisãoUS$0,002 antes de cada chamada; guarda em nanoUSD. Fontes oficiais verificadas pela coordenação: [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [streaming](https://developers.openai.com/api/docs/guides/streaming-responses). Não é fatura e não se inferiu câmbio.

A chave local foi acessada somente pelo carregador autorizado, sem exibição/cópia ou chave alternativa. O rótuloTCC-Impacto-Baseline foi informado pelo usuário; não é inferência da credencial.

## Testes e integridade

**50testes offline aprovados:**6integração,19H,22SSE e3retomada. Cincointegração+19H+22SSE passaram antes da primeira ativação; o teste adicionalrunnerH foi concluído após a paradaDNS, antes da continuação89. O pipelineMOCK usa análises locais válidas e vai do runner à carteira/fronteira/normalização; também verifica falhaH anterior a qualquer análise. As3contraprovas da retomada verificam89IDs, preservação da273/primeiroresultado/parada e bloqueio de replay/tamper. MOCKs vivem em carteiras temporárias, sem gasto real ou alegação semântica.

Inventário inicial: {integrity['arquivos_antes']}arquivos rastreados presentes no checkout. Só ledger e resumos STATUS/PLANO tiveram alterações permitidas entre os rastreados; tabelas/schemas antigos e chamadas1–272 preservados, assim como códigos, dados, raw, manifests e snapshotsv04. Código v05 confere com adendo congelado. A assinatura da retomada, a273 e o primeiroresultado são conferidos antes de cada reserva. `integridade_final.json` documenta as verificações. Snapshots: `ledger_antes.sqlite` pré-v05, `ledger_apos.sqlite` após paradaDNS; `retomada_89/ledger_antes_rede.sqlite` e `retomada_89/ledger_final.sqlite` delimitam a fase de rede.

Artefatos principais: adendos/manifestos, logs de coleta das duas fases, JSONoriginais por slot, avaliações, contabilidade, resumo descritivo, diagnósticoH, logsdetestes e integridade. `retomada_89/RELATORIO_PARADA_DNS.md` preserva a entrega intermediária. A execução escalada de rede foi aprovada pela revisão automática; não houve rejeição contornada. Nenhum novo commit/push nesta rodada; a coordenação já havia concluído o pedido anterior.

**Próximo passo:** revisão dos resultados, pendências de escopo e candidatos a falsa precisão, antes de qualquer mudança metodológica ou avanço. Nenhum resultado foi corrigido para coincidir com referência. Etapas10/11 permanecem não iniciadas.
'''
import re
ajustes={
'os89slots':'os 89 slots','tentativa273':'tentativa 273','Etapas10/11':'Etapas 10/11','acumuladoUS$5':'acumulado de US$ 5','coorte90IDs:15casos×B/H/T×2':'coorte de 90 IDs: 15 casos × B/H/T × 2','Standard/cache30m':'Standard/cache 30 min','saída total≤25000':'saída total ≤25.000 tokens','oficial≤16000':'oficial ≤16.000 tokens','deadlineTOTAL180s':'deadline total de 180 s','contagem+geração':'contagem + geração','H≤8análises/chamadas e1500s':'H ≤8 análises/chamadas e 1.500 s','Até300tentativas novas contando273':'Até 300 tentativas novas contando a 273','global572':'global de 572','formato5.0/schema2/política5/fronteira2.0-h':'formato 5.0/schema 2/política 5/fronteira 2.0-h','isolada2.0-manifesto-h05':'isolada 2.0-manifesto-h05','conciliadaUSD':'conciliada USD','ComprometidoUSD':'Comprometido USD','falhaDNS':'falha DNS','Hexato2/30':'H exato 2/30','impactozero':'impacto zero','CustoTv04':'Custo T v04','tinha22exatos mas21pares':'tinha 22 exatos mas 21 pares','previu2500centavos':'previu 2.500 centavos','inferior2500':'inferior de 2.500','totalexato':'total exato','escopo:4análises':'escopo: 4 análises','e20000centavos':'e 20.000 centavos','data,valor eaceite':'data, valor e aceite','nãoexata':'não exata','stringpara':'string para','sobUS$5':'sob US$ 5','As12reservas':'As 12 reservas','da273':'da 273','cacheleitura':'leitura de cache','escrita30m':'escrita 30 min','e0,50':'e 0,50','inferênciaUS$0,0145+provisãoUS$0,002':'inferência US$ 0,0145 + provisão US$ 0,002','rótuloTCC':'rótulo TCC','50testes':'50 testes','6integração,19H,22SSE e3retomada':'6 de integração, 19 H, 22 SSE e 3 de retomada','Cincointegração+19H+22SSE':'Cinco de integração + 19 H + 22 SSE','adicionalrunnerH':'adicional do runner H','continuação89':'continuação dos 89 pendentes','pipelineMOCK':'pipeline MOCK','falhaH':'falha H','As3contraprovas':'As 3 contraprovas','verificam89IDs':'verificam 89 IDs','da273/primeiroresultado/parada':'da 273, do primeiro resultado e da parada','chamadas1–272':'chamadas 1–272','snapshotsv04':'snapshots v04','primeiroresultado':'primeiro resultado','pré-v05':'antes da v05','JSONoriginais':'JSON originais','logsdetestes':'logs de testes'}
for a,z in ajustes.items():text=text.replace(a,z)
text=re.sub(r'(\d)(?=(?:tentativas|custos|reservas|pares|centavos|análises|testes)\b)',r'\1 ',text)
text=text.replace('Estados `ok`/`parcial` descrevem execução/contrato, não suporte semântico.', 'Estados `ok`/`parcial` descrevem execução/contrato, não suporte semântico. B teve 8 erros (1 DNS e 7 rejeições de campos); T teve 3 rejeições de campos. H teve 2 erros locais (hash e direção), sem rejeição de justificativa em lista ou acoplamento de ausência ao total do nó nesta amostra. Não se modificou nenhuma saída.')
text=text.replace('Notas diagnósticas locais preservadas:', 'Entre os 9 H exatos, 7 são de impacto não zero: k_0ca7, k_42a9 e k_6d82 nas duas repetições, e k_98f3 na primeira; os outros 2 são k_a064. Isso amplia a variedade observada além do único caso de impacto zero do v04, sem demonstrar causalidade ou superioridade. Notas diagnósticas locais preservadas:')
text=text.replace('As pendências H estão preservadas por nó', 'Dos 10 fechamentos completos operacionais, 9 resultaram em prazo/custo exatos. O outro, H/k_d307/rep1, preservou duração nova indeterminada: prazo indeterminado e custo com direção de aumento e limite inferior de 2.500 centavos, sem total exato. Assim, fechamento estrutural completo não força certeza numérica. As pendências H estão preservadas por nó')
for a,z in {'1049arquivos':'1.049 arquivos','a273':'a 273','paradaDNS':'parada DNS','diagnósticoH':'diagnóstico H','aprovados:**6':'aprovados:** 6','US$0,10/M entrada,0,01/M leitura de cache,0,125/M escrita 30 min e 0,50/M saída':'US$ 0,10/M de entrada, US$ 0,01/M de leitura de cache, US$ 0,125/M de escrita com retenção de 30 min e US$ 0,50/M de saída'}.items():text=text.replace(a,z)
(O/'RELATORIO.md').write_text(text);db.close()
print(status)
