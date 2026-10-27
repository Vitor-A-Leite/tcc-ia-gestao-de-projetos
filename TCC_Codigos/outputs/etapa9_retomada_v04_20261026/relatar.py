"""Relatório descritivo pós-parada/fim. Nenhuma rede ou reparo de previsão."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import json,sqlite3,hashlib
from interpretacao_no.contratos import hash_json
from piloto_real.runner import gravar_novo
O=Path(__file__).parent;P=O.parent/'etapa9_coorte_v04_20261026';W=O.parent/'etapa9_piloto_real_aprovado_20261026'
def ler(p):return json.loads(p.read_text())
def usd(n):return str(Decimal(n)/10**9).replace('.',',')
def main():
    db=sqlite3.connect('file:'+str((W/'ledger.sqlite').resolve())+'?mode=ro',uri=True)
    before=sqlite3.connect('file:'+str((P/'snapshot_pos_parada/ledger.sqlite').resolve())+'?mode=ro',uri=True)
    rows=db.execute('SELECT * FROM slots_v04 ORDER BY rowid').fetchall();regs=[json.loads(r)for _,_,r in rows if r]
    calls=db.execute('SELECT id,slot,estado,comprometido,custo_inferencia,uso,registro,contagem_iniciada,inferencia_iniciada,request_hash FROM chamadas ORDER BY id').fetchall()
    prop=ler(P/'opcao_retomada_73.json');allowed=set(prop['slots_pendentes']);ad=ler(O/'adendo_retomada.json')
    frozen={t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall()==before.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall()for t in ('meta','slots','parada','adendos','diagnosticos','coorte_v04','parada_v04')}
    frozen['chamadas1a61']=[x for x in db.execute('SELECT * FROM chamadas ORDER BY id')if x[0]<=61]==before.execute('SELECT * FROM chamadas ORDER BY id').fetchall()
    frozen['17slots']=[r for r in rows if r[0]not in allowed]==[r for r in before.execute('SELECT * FROM slots_v04 ORDER BY rowid')if r[0]not in allowed]
    assert all(frozen.values()),frozen
    hs=ler(O/'integridade_17slots_antes.json');changed=[p for p,h in hs.items()if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];assert not changed,changed
    for reg in regs:
        s=reg['metadados']['execucao_id'];target=(O if s in allowed else P)/(s+'.json');assert ler(target)==reg
        if s in allowed:assert reg['resultado']['adendo_retomada']==dict(id=ad['id'],hash=hash_json(ad),codigo=ad['codigo'])
    src=Path(__file__).resolve().parents[2]/'src/retomada_v04'
    assert all(hashlib.sha256((src/p).read_bytes()).hexdigest()==h for p,h in ad['codigo'].items())
    raw=O/'chamadas_originais';raw.mkdir(exist_ok=True);checked=[]
    for id,s,e,comp,custo,uso,r,ct,it,h in calls:
        if id<=61:continue
        rr=json.loads(r)if r else{};p=rr.get('payload');co=rr.get('contagem_payload')
        if p:
            assert h==hash_json(p);assert co=={k:p[k]for k in ('model','input','reasoning','text')}
            assert p['model']=='gpt-6-luna'and p['reasoning']=={'effort':'high'}and p['max_output_tokens']==25000
            assert p['service_tier']=='default'and p['prompt_cache_options']=={'ttl':'30m'}and p['tools']==[]
            checked.append(id)
        gravar_novo(raw/f'call_{id:03}.json',dict(call_id=id,slot=s,estado=e,comprometido_nanoUSD=comp,custo_inferencia_nanoUSD=custo,uso=json.loads(uso)if uso else None,registro=rr,contagem_iniciada=ct,inferencia_iniciada=it,request_hash=h))
    snap=O/'snapshot_pos_execucao';snap.mkdir(exist_ok=True);b=sqlite3.connect(snap/'ledger.sqlite');db.backup(b);b.close()
    states=dict(Counter(e for _,e,_ in rows));phase={}
    for label,pred in [('fase1_17slots',lambda n:15<n<=61),('retomada',lambda n:n>61)]:
        cc=[x for x in calls if pred(x[0])];rr=[r for r in regs if (r['metadados']['execucao_id']in allowed)==(label=='retomada')]
        phase[label]=dict(slots=len(rr),condicoes=dict(Counter(r['metadados']['condicao']for r in rr)),estados=dict(Counter(r['resultado']['execucao']['estado']for r in rr)),chamadas=len(cc),contagens_marcadas=sum(x[7]for x in cc),inferencias_marcadas=sum(x[8]for x in cc),custo_inferencia_conhecida_nanoUSD=sum(x[4]or 0 for x in cc),reserva_inferencia_desconhecida_nanoUSD=sum(x[3]-2000000 for x in cc if x[2]!='conciliado'),provisao_contagem_nanoUSD=len(cc)*2000000,comprometido_nanoUSD=sum(x[3]for x in cc),tempo_slots_s=sum(r['resultado'].get('tempo_slot_s',0)for r in rr),tokens_entrada_conciliados=sum(json.loads(x[5])['input_tokens']for x in cc if x[5]),tokens_saida_total_conciliados=sum(json.loads(x[5])['output_tokens']for x in cc if x[5]))
    total=sum(x[3]for x in calls);known=sum(x[4]or 0 for x in calls);unknown=sum(x[3]-2000000 for x in calls if x[2]!='conciliado');provision=len(calls)*2000000
    assert known+unknown+provision==total and total<=5000000000 and len(calls)<=300
    faults=[]
    for id,s,e,comp,custo,u,rawr,ct,it,h in calls:
        if id<=61:continue
        rr=json.loads(rawr)if rawr else{}
        if rr.get('erro'):faults.append(dict(call_id=id,slot=s,erro=rr['erro'],falha_transporte=rr.get('falha_transporte'),fase_macro='inferencia'if it else 'contagem_ou_antes',contagem_oficial=rr.get('contagem_oficial'),response_presente='response'in rr))
    stop=db.execute('SELECT * FROM paradas_retomada_v04 ORDER BY seq').fetchall()
    summary=dict(coorte='v04_descritiva_com_interrupcao_e_retomada',N_planejado=90,estados_slots=states,fases=phase,paradas_retomada=stop,novas_falhas_transporte=faults,global_=dict(tentativas=len(calls),inferencia_conhecida_nanoUSD=known,reserva_inferencia_desconhecida_nanoUSD=unknown,provisao_contagem_hipotetica_nanoUSD=provision,comprometido_nanoUSD=total,saldo_interno_nanoUSD=5000000000-total))
    (O/'resumo_resultados.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    (O/'integridade_final.json').write_text(json.dumps(dict(congelados=frozen,arquivos_parcial_conferidos=len(hs),arquivos_parcial_alterados=changed,exports_identicos=True,adendo_codigo_vinculado=True,payloads_verificados=checked,limites_globais_conferidos=True),ensure_ascii=False,indent=2))
    metrics=ler(O/'avaliacao_autoral.json');account=ler(O/'contabilidade_e_erros.json')
    lines=['# Etapa9 — estado da coortev04 após retomada','', '26/10/2026,America/Sao_Paulo. Relatório descritivo de duas fases operacionais, com interrupção e retomada autorizada pelo coordenador sob a autorização humana existente. Não é experimento final controlado. N90planejado,N30por condição,15casos×duas repetições. As métricas abaixo consolidam somente a coortev04; v03 e diagnóstico180s ficam separados.','',f"Estado: {states.get('terminado',0)} slots concluídos, {states.get('pendente',0)} não iniciados. Parada nova: "+('RemoteDisconnected na fase de cabeçalho HTTP, chamada71.'if stop else 'nenhuma; passagem autorizada concluída.')+' O relatório original de17slots e a chamada61 permanecem intactos no diretório etapa9_coorte_v04_20261026. Os73IDs da retomada foram registrados antes da geração, sem reabrir17terminados, repetir tentativa61 ou liberar suas reservas.','','|Fase|Slots concluídos|Por condição|Chamadas novas|Tempo dos slots(s)|Inferência conhecida(US$)|','|---|---:|---|---:|---:|---:|']
    for k,v in phase.items():lines.append(f"|{'Fase1'if k=='fase1_17slots'else 'Retomada'}|{v['slots']}|"+'; '.join(f'{c}: {n}'for c,n in v['condicoes'].items())+f"|{v['chamadas']}|{v['tempo_slots_s']:.2f}|{usd(v['custo_inferencia_conhecida_nanoUSD'])}|")
    lines+=['','|Condição|Realizados/30|Não iniciados|Estados da execução|','|---|---:|---:|---|']
    for k,v in account['por_condicao'].items():lines.append(f"|{k}|{v['N_registros']}/30|{v['N_nao_iniciados']}|"+'; '.join(f'{e}: {n}'for e,n in v['estados_execucao'].items())+'|')
    lines+=['','|Condição/desfecho|Cobertura exata|MAE em pares exatos válidos|Estados do desfecho|','|---|---:|---|---|']
    for k,v in metrics['metricas'].items():
        er=v['erro_numerico'];mae='não calculável'if er['MAE']is None else str(er['MAE'])+' '+er['unidade'];lines.append(f"|{k}|{v['cobertura_numerica']['n']}/30|{mae};n={er['n']}/30|"+'; '.join(f'{e}: {n}'for e,n in v['estados'].items()if n)+'|')
    lines+=['','|Par/desfecho|Interseção comparável|MAE na interseção|','|---|---:|---|']
    for p in metrics['pareadas']:lines.append(f"|{'/'.join(p['condicoes'])}: {p['desfecho']}|{p['n_intersecao']}/30|"+('não calculável'if not p['n_intersecao']else str(p['MAE_intersecao']))+'|')
    lines+=['',f"Contabilidade global: {len(calls)}tentativas reservadas/300; US${usd(known)}inferência conhecida +US${usd(unknown)}reserva de inferência desconhecida +US${usd(provision)}provisão hipotética de contagem =US${usd(total)}comprometidos. Saldo interno US${usd(5000000000-total)}sob tetoUS$5. Provisão não é tarifa publicada; não é fatura/saldo da conta. Reservas integrais já incluem sua parcela de provisão; não somar duas vezes.", '', f"Coortev04: {account['contagens_HTTP_marcadas']}contagensHTTP e {account['inferencias_HTTP_marcadas']}inferências marcadas; uso conciliado {account['uso_conciliado']['tokens_entrada']}tokens de entrada/{account['uso_conciliado']['tokens_saida_total']}saída total incluindo reasoning. Custos/tokens desconhecidos não foram estimados como zero. Chamadas anteriores1–15 são só contabilidade global, não entram nas métricasv04.", '', 'Prazo em dias corridos e custo em centavosBRL. MAE cobre somente previsão exata válida e referência exata AUTORAL. Interseções pareadas e denominadores estão explícitos. Repetições não são casos independentes. Nenhuma imputação de zero aos ausentes; sua classe mecânica de erro no normalizador não é erro numérico observado. Referência indeterminada k_d307 conserva limite separadamente conforme adaptação já revisada do avaliador1.0. Valores, direções, intervalos, lacunas e resultados por execução estão em normalizacao.json, sem correção.', '', 'Suporte semântico não auditado; inferibilidade pendente nas referências novas e sem validação independente. Acerto numérico/MAE selecionado não autoriza superioridade científica. H parcial pode resultar de falha de contrato, bloqueio operacional ou lacuna, que não equivale a abstenção semanticamente adequada. Falhas globais e locais estão em contabilidade_e_erros.json. Nenhuma previsão foi reparada ou repetida.', '', '## Parada e telemetria da retomada','']
    if faults:
        for f in faults:lines.append(json.dumps(f,ensure_ascii=False))
    else:lines.append('Nenhuma falha de transporte registrada na retomada.')
    lines+=['', 'A telemetria nova registra somente faseenum/classeallowlisted/errnointeiro; não contém mensagem crua,headers,conteúdo ou segredo. A fase envio pode incluir DNS/TLS pela conexão lazyHTTPS. Classe/fase descrevem a operação onde a exceção foi capturada, sem provar causa externa. Não se reconstruíram detalhes da chamada61. Nova falha não esclarecida mantém a coleta parada, sem retomada automática.', '', 'Integridade:17slots terminados,chamadas1–61,fontes/manifesto/parada/relatório parcial preservados por comparação ao snapshot e hashes. Novos resultados vinculam hash do adendo/código do retomador; não alegam cobertura pelo hash antigo. Payloads contados/gerados e parâmetros conferidos, mesma carteira/lock/caps. Cinco testes offline passaram antes da ativação, sem rede/chave; sem chamada extra de teste. PROTOCOLO.md e adendo_retomada.json documentam a decisão operacional. Sem etapas10/11,commit/push/deploy.']
    lines+=['','## Resultado desta retomada','', 'Foram concluídos somente três dos73slots: B/k_23d8/repetição2 retornou campos incompatíveis com o contrato global (uso conciliado, resultado inválido preservado); B/k_42a9/repetição1 retornou previsão parcial; H/k_42a9/repetição1 ficou parcial após a falha71. Nenhum slot terminado anteriormente foi reaberto. Há70slots não iniciados e nenhum iniciado sem resultado.', '', 'Falha71: nó n_ae50, contagem oficial5281tokens concluída, inferência marcada, RemoteDisconnected na fase cabecalho em60810,171ms totais da tentativa; deadline180s não foi atingido pelo relógio externo. Sem statusHTTP/provider_code/request_id/usage/resposta, errno ausente; reservaUS$0,0165mantida. A implementação local de http.client.HTTPResponse._read_status lança RemoteDisconnected ao receber EOF antes da linha de statusHTTP. Isso distingue a falha de interpretaçãoJSON/contrato do modelo, mas não identifica quem fechou a conexão ou por quê; não prova autenticação/modelo/parâmetro inválido. [Evidência segura da chamada71](falha_call_71.json). A tentativa61 permanece indeterminada, sem acrescentar-lhe telemetria retroativa.', '', 'A nova parada é persistente própria da retomada, além da parada original intacta. Não há segunda liberação ou retry. A entrega volta para revisão do coordenador antes de qualquer nova continuação.']
    import re
    texto='\n'.join(lines)+'\n'
    texto=re.sub(r'(\d+)(slots|casos|tentativas|terminados|pendentes|planejado|por|tokens|contagens|inferências|chamadas|retornos|resultados|pares|IDs)\b',r'\1 \2',texto)
    texto=re.sub(r'(US\$)(?=\d)',r'\1 ',texto)
    texto=re.sub(r'(US\$ [\d.,]+)(?=[A-Za-zÀ-ÿ])',r'\1 ',texto)
    for aa,bb in {'de17':'de 17','reabrir17':'reabrir 17','dos73':'dos 73','Há70':'Há 70','oficial5281':'oficial 5281','deadline180s':'deadline de 180 s','em60810,171ms':'em 60.810,171 ms','Falha71':'Falha 71','métricasv04':'métricas v04','Coortev04':'Coorte v04','contagensHTTP':'contagens HTTP','centavosBRL':'centavos BRL','retomadaUS$':'retomada US$','etapas10/11':'etapas 10/11','chamadas1–61':'chamadas 1–61','anteriores1–15':'anteriores 1–15','Etapa9':'Etapa 9','coortev04':'coorte v04','N90planejado,N30por':'N = 90 planejado, N = 30 por','v03 e diagnóstico180s':'v03 e diagnóstico de 180 s','26/10/2026,America':'26/10/2026, America','15 casos×':'15 casos × ','Fase1':'Fase 1','modeloHigh':'modelo high','suporte semântico/inferibilidade':'suporte semântico e inferibilidade','cabecalhoHTTP':'cabeçalho HTTP','statusHTTP':'status HTTP','classeallowlisted':'classe permitida','faseenum':'fase enumerada','errnointeiro':'errno inteiro','leituraJSON':'leitura JSON','16k':'16 mil','25k':'25 mil','etapas10/11':'etapas 10/11','nos73':'nos 73','Os73':'Os 73','reabrir17':'reabrir 17','chamada71':'chamada 71','chamada61':'chamada 61','tentativa61':'tentativa 61','chamada71':'chamada 71','US$5':'US$ 5','US$0':'US$ 0','na fase cabecalho':'na fase cabeçalho','sem rede/chave':'sem rede ou leitura de chave'}.items():texto=texto.replace(aa,bb)
    (O/'RELATORIO.md').write_text(texto)
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
