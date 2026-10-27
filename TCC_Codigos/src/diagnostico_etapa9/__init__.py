"""Adendo180s: até duas chamadas; mesma carteira; nenhuma geração ao importar."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from time import monotonic
from interpretacao_no.contratos import hash_json,validar
from interpretacao_no.adaptadores import _json,FalhaTransporte
from condicoes.baseline import validar_resposta
from piloto_real import MODELO,LOTE_ID
from piloto_real.ledger import Ledger,Bloqueio,RESERVA,NANO_USD
from piloto_real.transporte import inteiro,custo_usage
from piloto_real.runner import gravar_novo

ADENDO='etapa9-diagnostico-180s-20261026-v1'
IDS=[ADENDO+'-B',ADENDO+'-H-local']


def fingerprint_original(db):
    return hash_json({t:db.execute(sql).fetchall() for t,sql in {
        'meta':'SELECT * FROM meta ORDER BY id','slots':'SELECT * FROM slots ORDER BY id',
        'parada':'SELECT * FROM parada ORDER BY id',
        'chamadas_originais':'SELECT * FROM chamadas WHERE id<=13 ORDER BY id'}.items()})


def codigo_adendo():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))}


def fontes_diag(db):
    fontes=[]
    for id in (1,4):
        slot,h,estado,raw=db.execute('SELECT slot,request_hash,estado,registro FROM chamadas WHERE id=?',(id,)).fetchone()
        r=json.loads(raw);payload=r['payload'];count=r['contagem_payload']
        if estado!='custo_desconhecido' or r.get('erro')!='timeout' or h!=hash_json(payload):raise Bloqueio('Origem não corresponde ao timeout/payload aprovado')
        if (payload['model']!=MODELO or payload['reasoning']!={'effort':'high'} or payload['max_output_tokens']!=25000
            or payload['service_tier']!='default' or payload['prompt_cache_options']!={'ttl':'30m'}
            or payload['tools']!=[] or payload['store'] is not False or payload['truncation']!='disabled'):raise Bloqueio('Parâmetro original diverge do adendo')
        if count!={k:payload[k] for k in ('model','input','reasoning','text')}:raise Bloqueio('Contagem e inferência originais divergentes')
        fontes.append(dict(call_id_original=id,slot_original=slot,payload_hash=h,payload=payload,contagem_payload=count))
    return fontes


class LedgerDiagnostico(Ledger):
    def __init__(self,pasta):
        pasta=Path(pasta)
        if not (pasta/'ledger.sqlite').is_file():raise Bloqueio('Carteira original ausente; não criar orçamento novo')
        plano=json.loads((pasta/'plano.json').read_text())
        if plano['lote_id']!=LOTE_ID:raise Bloqueio('Lote original incompatível')
        super().__init__(pasta,plano)
        try:
            # Arquivos/módulos originais continuam intactos; adendo fica fora do pacote v03.
            src=Path(__file__).resolve().parents[1]
            for n,h in plano['codigo'].items():
                if hashlib.sha256((src/n).read_bytes()).hexdigest()!=h:raise Bloqueio('Código original alterado')
            self.fontes=fontes_diag(self.db)
            self.manifesto=dict(id=ADENDO,data_aprovacao_usuario='2026-10-26',timezone='America/Sao_Paulo',
                autorizacao='Aprovo o diagnóstico de até duas chamadas com deadline de 180 segundos. Pode executar na etapa 9, preservando os demais parâmetros, os resultados anteriores e o teto acumulado de US$ 5, e trazer a entrega para revisão.',
                plano_original_hash=hash_json(plano),fontes=[{k:v for k,v in f.items() if k not in ('payload','contagem_payload')} for f in self.fontes],
                slots=IDS,deadline_total_s=180,max_inferencias=2,max_retries=0,limite_acumulado_USD='5.00',
                regra_segunda='apenas após primeira completa e formato válido, sem desvio de protocolo',
                comparacao='diagnóstico separado;não substituir90slots nem compor H retrospectivo',codigo=codigo_adendo())
            with self.db:
                self.db.execute('CREATE TABLE IF NOT EXISTS adendos (id TEXT PRIMARY KEY,manifesto TEXT NOT NULL,hash TEXT NOT NULL,original_fingerprint TEXT NOT NULL)')
                self.db.execute('CREATE TABLE IF NOT EXISTS diagnosticos (id TEXT PRIMARY KEY,estado TEXT NOT NULL,resultado TEXT,call_id INTEGER UNIQUE)')
                a=self.db.execute('SELECT hash,original_fingerprint FROM adendos WHERE id=?',(ADENDO,)).fetchone()
                if a:
                    if a[0]!=hash_json(self.manifesto) or a[1]!=fingerprint_original(self.db):raise Bloqueio('Adendo/código/estado original alterado; não retomar')
                    self.original_hash=a[1]
                else:
                    if self.db.execute('SELECT count(*) FROM chamadas').fetchone()[0]!=13:raise Bloqueio('Estado inicial não corresponde às13tentativas revisadas')
                    self.original_hash=fingerprint_original(self.db)
                    self.db.execute('INSERT INTO adendos VALUES(?,?,?,?)',(ADENDO,json.dumps(self.manifesto,ensure_ascii=False),hash_json(self.manifesto),self.original_hash))
                    for s in IDS:self.db.execute('INSERT INTO diagnosticos VALUES(?,?,NULL,NULL)',(s,'pendente'))
        except BaseException:self.close();raise

    def estado_diag(self,slot):return self.db.execute('SELECT estado FROM diagnosticos WHERE id=?',(slot,)).fetchone()[0]
    def iniciar_diag(self,slot):
        if slot not in IDS:raise Bloqueio('Slot não aprovado')
        with self.db:
            if fingerprint_original(self.db)!=self.original_hash:raise Bloqueio('Estado original modificado')
            if slot==IDS[1]:
                raw=self.db.execute('SELECT resultado FROM diagnosticos WHERE id=?',(IDS[0],)).fetchone()[0]
                if not raw or json.loads(raw)['estado']!='completa_valida':raise Bloqueio('Primeira não completa/válida; segunda não autorizada pela regra')
            r=self.db.execute("UPDATE diagnosticos SET estado='iniciado' WHERE id=? AND estado='pendente'",(slot,))
            if r.rowcount!=1:raise Bloqueio('Diagnóstico já iniciado; não repetir')
    def reservar(self,slot,reqhash):
        if slot not in IDS or reqhash!=self.fontes[IDS.index(slot)]['payload_hash']:raise Bloqueio('Payload/slot não aprovado')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if fingerprint_original(self.db)!=self.original_hash:raise Bloqueio('Original alterado')
            n,total=self.db.execute('SELECT count(*),COALESCE(sum(comprometido),0) FROM chamadas').fetchone()
            estado,call_id=self.db.execute('SELECT estado,call_id FROM diagnosticos WHERE id=?',(slot,)).fetchone()
            usados=self.db.execute('SELECT count(*) FROM chamadas WHERE slot IN (?,?)',IDS).fetchone()[0]
            if estado!='iniciado' or call_id is not None or usados>=2 or n>=300 or total+RESERVA>5*NANO_USD:raise Bloqueio('Limite acumulado/per-slot impede diagnóstico')
            cur=self.db.execute('INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES(?,?,?,?)',(slot,reqhash,'reservado',RESERVA))
            self.db.execute('UPDATE diagnosticos SET call_id=? WHERE id=?',(cur.lastrowid,slot));return cur.lastrowid
    def salvar_diag(self,slot,r,*,esperado='iniciado'):
        with self.db:
            q=self.db.execute('UPDATE diagnosticos SET estado=?,resultado=? WHERE id=? AND estado=?',('terminado',json.dumps(r,ensure_ascii=False,allow_nan=False),slot,esperado))
            if q.rowcount!=1:raise Bloqueio('Resultado diagnóstico já persistido')
    def preservar_original(self):
        if fingerprint_original(self.db)!=self.original_hash:raise Bloqueio('Original não preservado')
        return True


def validar_conteudo(bruto,fonte):
    if bruto.get('status')!='completed':return 'incompleta_ou_erro',None
    textos=[]
    for i in bruto.get('output',[]):
        if i.get('type')=='message':
            for c in i.get('content',[]):
                if c.get('type')=='refusal':return 'recusa',None
                if c.get('type')=='output_text':textos.append(c['text'])
    try:
        original=_json(''.join(textos));entrada=json.loads(fonte['payload']['input'][1]['content'])
        if fonte['call_id_original']==1:validar_resposta(original,entrada)
        else:validar(original,entrada['contexto'])
        return 'completa_valida',original
    except (ValueError,TypeError,KeyError):return 'formato_invalido',None


def tentativa(l,slot,fonte,http,redator):
    inicio=monotonic();deadline=inicio+180;id=None;tcont=tinfer=None;fase=None;tfase=None
    r=dict(slot_diagnostico=slot,call_id_original=fonte['call_id_original'],slot_original=fonte['slot_original'],payload_hash=fonte['payload_hash'],
           deadline_total_s=180,retry=0,suporte_semantico='nao_auditado',natureza='diagnostico_separado_nao_substitui_previsao_original')
    registro=dict(payload=fonte['payload'],contagem_payload=fonte['contagem_payload'],timeout_s=180,retry=0,adendo=ADENDO,origem_call_id=fonte['call_id_original'])
    try:
        id=l.reservar(slot,fonte['payload_hash']);r['call_id']=id
        l.iniciar_contagem(id);fase='contagem';tfase=monotonic()
        count=http.post('/input_tokens',deepcopy(fonte['contagem_payload']),deadline-monotonic());tcont=monotonic()-tfase
        if count.get('object')!='response.input_tokens':raise ValueError('Contagem oficial inválida')
        n=inteiro(count['input_tokens']);registro['contagem_oficial']=n;l.contar(id,n)
        if n>16000:raise FalhaTransporte('entrada_tokens','Entrada maior que limite aprovado;sem inferência')
        l.enviar(id);fase='inferencia';tfase=monotonic()
        bruto=redator(http.post('',deepcopy(fonte['payload']),deadline-monotonic()));tinfer=monotonic()-tfase
        registro['response']=bruto;r['response_original']=bruto
        divergente=(bruto.get('model') not in (None,MODELO) or bruto.get('service_tier','default')!='default' or bruto.get('prompt_cache_options',{}).get('ttl','30m')!='30m')
        u=bruto.get('usage') or {};wd=(u.get('input_tokens_details') or {}).get('cache_write_tokens_details') or {}
        divergente=divergente or (type(u.get('input_tokens'))is int and u['input_tokens']>16000) or (type(u.get('output_tokens'))is int and u['output_tokens']>25000) or (type(wd.get('ttl_12h_tokens'))is int and wd['ttl_12h_tokens']>0)
        r['protocolo_provider']='divergente' if divergente else 'compativel_com_request'
        try:
            if divergente:raise ValueError('Desvio de protocolo')
            custo=custo_usage(bruto['usage']);l.concluir(id,custo,bruto['usage'],registro)
            r.update(custo_inferencia_nanoUSD=custo,contabilidade='uso_conciliado_provisao_contagem_mantida')
        except (ValueError,KeyError,TypeError):
            l.desconhecido(id,registro);r.update(custo_inferencia_nanoUSD=None,contabilidade='reserva_integral_mantida')
        estado,parsed=validar_conteudo(bruto,fonte)
        if divergente:estado='desvio_protocolo'
        r.update(estado=estado,conteudo_parseado_original=parsed)
    except BaseException as e:
        if fase=='contagem' and tcont is None:tcont=monotonic()-tfase
        if fase=='inferencia' and tinfer is None:tinfer=monotonic()-tfase
        registro['erro']=getattr(e,'codigo','falha_sanitizada');registro['falha_transporte']=redator(getattr(e,'metadados',{}))
        if id is not None:l.desconhecido(id,registro)
        r.update(estado='interrompida' if isinstance(e,(KeyboardInterrupt,SystemExit)) else 'erro_operacional',erro=registro['erro'],falha_transporte=registro['falha_transporte'])
        if isinstance(e,(KeyboardInterrupt,SystemExit)):raise
    finally:
        r['tempos_ms']=dict(contagem=None if tcont is None else round(tcont*1000,3),inferencia=None if tinfer is None else round(tinfer*1000,3),total=round((monotonic()-inicio)*1000,3))
        # Conciliação pode já estar gravada; atualização só acrescenta tempos ao novo registro.
        if id is not None:
            registro['tempos_ms']=r['tempos_ms']
            with l.db:l.db.execute('UPDATE chamadas SET registro=? WHERE id=? AND slot=?',(json.dumps(redator(registro),ensure_ascii=False),id,slot))
    return redator(r)


def executar(pasta,saida,*,http=None,chave=None,coletar=False,redator=None):
    from piloto_real.transporte import HTTP,sanitizar
    out=Path(saida);out.mkdir(parents=True,exist_ok=True)
    redact=redator or (lambda x:sanitizar(x,chave))
    with LedgerDiagnostico(pasta) as l:
        gravar_novo(out/'adendo_aprovado.json',l.manifesto)
        if not coletar:return dict(estado='adendo_preparado_sem_rede',orcamento_acumulado=l.resumo())
        if http is None and not chave:raise ValueError('Chave local ausente')
        api=http or HTTP(chave)
        for j,s in enumerate(IDS):
            st=l.estado_diag(s)
            if st=='terminado':continue
            if st=='iniciado':
                l.salvar_diag(s,dict(slot_diagnostico=s,estado='interrompida_sem_replay',nota='Tentativa anterior iniciada;reserva mantida'))
                continue
            if j==1:
                raw=l.db.execute('SELECT resultado FROM diagnosticos WHERE id=?',(IDS[0],)).fetchone()[0]
                if not raw or json.loads(raw)['estado']!='completa_valida':
                    l.salvar_diag(s,dict(slot_diagnostico=s,estado='nao_executada_primeira_sem_resposta_valida'),esperado='pendente');continue
            l.iniciar_diag(s)
            r=tentativa(l,s,l.fontes[j],api,redact);l.salvar_diag(s,r)
        resultados=[json.loads(r)for r, in l.db.execute('SELECT resultado FROM diagnosticos ORDER BY rowid')]
        for s,r in zip(IDS,resultados):gravar_novo(out/(s+'.json'),r)
        resumo=dict(adendo=ADENDO,resultados=resultados,original_preservado=l.preservar_original(),orcamento_acumulado=l.resumo())
        gravar_novo(out/'resumo.json',resumo)
        return resumo
