"""OpenAI Responses; reservas persistentes, uso real e nenhum fallback/retry."""
from pathlib import Path
import json, sqlite3, time, urllib.request, urllib.error, uuid
from .vendor.hibrido_v07_r3.contratos import VERSAO
from .vendor.hibrido_v07_r3.schema import formato
from .vendor.interpretacao_no.adaptadores import RespostaTransporte, FalhaTransporte

from .apresentacao import compactar, INSTRUCOES

MODELO='gpt-6-luna'
CONFIG={'reasoning':{'effort':'high'}}
# Preços oficiais consultados em 10/11/2026: USD/1M entrada=.10, cache=.01, saída=.50.
# Teto acumulado anterior preservado: USD5. Reserva conservadora USD.015 por chamada.
class TransporteReal:
    origem='openai_real'
    versao_formato_local=VERSAO
    def __init__(self, pasta, chave, historico_nano, *, http=None):
        self.pasta=Path(pasta);self.pasta.mkdir(parents=True,exist_ok=True)
        self._chave=chave;self.http=http or self._http;self.historico=historico_nano
        self.db=sqlite3.connect(self.pasta.parent/'consumo_ia_real.sqlite')
        self.db.execute('CREATE TABLE IF NOT EXISTS chamadas(id TEXT PRIMARY KEY, rodada TEXT, estado TEXT, comprometido INTEGER, entrada INTEGER, saida INTEGER, segundos REAL, arquivo TEXT)')
        self.db.commit();self.rodada=self.pasta.name;self.parado=False
    def _http(self,path,payload):
        req=urllib.request.Request('https://api.openai.com/v1/responses'+path,data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+self._chave,'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
        except urllib.error.HTTPError as e:
            raise FalhaTransporte('http_'+str(e.code),'API respondeu HTTP '+str(e.code)) from None
        except Exception:
            raise FalhaTransporte('rede','Falha de rede; reserva mantida, sem repetição') from None
    def snapshot(self):
        rows=self.db.execute('SELECT estado,comprometido,entrada,saida,segundos FROM chamadas WHERE rodada=?',(self.rodada,)).fetchall()
        return dict(chamadas_api=len(rows),tokens_entrada=sum(r[2] or 0 for r in rows),tokens_saida=sum(r[3] or 0 for r in rows),custo_api_usd=sum(r[1] for r in rows if r[0]=='conciliada')/1e9,segundos=sum(r[4] or 0 for r in rows),uso_desconhecido=any(r[0]!='conciliada' for r in rows),comprometido_usd=sum(r[1] for r in rows)/1e9,historico_comprometido_usd=self.historico/1e9)
    def gerar(self,mensagens,formato_resposta,etiqueta):
        if self.parado:raise FalhaTransporte('parada','Transporte interrompido após falha; nenhuma nova chamada')
        payload=dict(model=MODELO,input=mensagens,reasoning=CONFIG['reasoning'],text={'format':formato_resposta},max_output_tokens=16000,store=False,truncation='disabled',service_tier='default')
        cid=uuid.uuid4().hex;t0=time.monotonic()
        self.db.execute('BEGIN IMMEDIATE')
        total=self.db.execute('SELECT coalesce(sum(comprometido),0) FROM chamadas').fetchone()[0]
        n=self.db.execute('SELECT count(*) FROM chamadas WHERE rodada=?',(self.rodada,)).fetchone()[0]
        rodada=self.db.execute('SELECT coalesce(sum(comprometido),0) FROM chamadas WHERE rodada=?',(self.rodada,)).fetchone()[0]
        if n>=33 or total+self.historico+15_000_000>5_000_000_000 or rodada+15_000_000>400_000_000:
            self.db.rollback();raise FalhaTransporte('orcamento','Teto acumulado atingido')
        self.db.execute('INSERT INTO chamadas VALUES(?,?,?,?,?,?,?,?)',(cid,self.rodada,'reservada',15_000_000,None,None,0,cid+'.json'));self.db.commit()
        record=dict(id=cid,etiqueta=etiqueta,pedido=payload,precos_usd_milhao={'entrada':.1,'cache':.01,'saida':.5})
        try:
            count=self.http('/input_tokens',{k:v for k,v in payload.items() if k not in ('max_output_tokens','store','service_tier','truncation')})
            record['contagem']=count
            if type(count.get('input_tokens')) is not int or count['input_tokens']>64000:raise FalhaTransporte('entrada','Contagem oficial ausente ou acima de64000; inferência não enviada')
            r=self.http('',payload);record['resposta']=r
            u=r.get('usage') or {};i=u.get('input_tokens');o=u.get('output_tokens');cached=u.get('input_tokens_details',{}).get('cached_tokens',0)
            if any(type(x)is not int or x<0 for x in (i,o,cached)) or cached>i or i>64000 or o>16000:raise FalhaTransporte('usage','Uso ausente/incompatível; reserva mantida')
            if r.get('model')!=MODELO or r.get('service_tier','default')!='default':raise FalhaTransporte('modelo','Modelo ou tier divergente; reserva mantida')
            cost=(i-cached)*100+cached*10+o*500
            self.db.execute('UPDATE chamadas SET estado=?,comprometido=?,entrada=?,saida=?,segundos=? WHERE id=?',('conciliada',cost,i,o,time.monotonic()-t0,cid));self.db.commit()
            record['custo_usd_estimado_usage']=cost/1e9
            if r.get('status')!='completed':self.parado=True
            return r,cost
        except BaseException as exc:
            self.parado=True;record['erro']=getattr(exc,'codigo',type(exc).__name__)
            self.db.execute('UPDATE chamadas SET segundos=? WHERE id=?',(time.monotonic()-t0,cid));self.db.commit()
            raise
        finally:
            (self.pasta/(cid+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2))
    def __call__(self,req):
        if req['modelo']!=MODELO or req['configuracao']!=CONFIG:raise ValueError('Configuração real divergente')
        dados=json.loads(req['mensagens'][1]['conteudo'])
        c=dados['contexto']
        mensagens=[{'role':'system', 'content':req['mensagens'][0]['conteudo'] + INSTRUCOES},
                   {'role':'user', 'content':json.dumps(compactar(dados), ensure_ascii=False, allow_nan=False)}]
        r,cost=self.gerar(mensagens,formato(c),c['no_id'])
        txt=''.join(p['text'] for item in r.get('output',[]) for p in item.get('content',[]) if p['type']=='output_text')
        refusal=any(p['type']=='refusal' for item in r.get('output',[]) for p in item.get('content',[]))
        return RespostaTransporte(texto=txt,estado='recusa' if refusal else 'completa' if r['status']=='completed' else 'incompleta',modelo=r['model'],request_id=r['id'],tokens_entrada=r['usage']['input_tokens'],tokens_saida=r['usage']['output_tokens'],custo_api_centavos=None,metadados={'custo_api_usd':cost/1e9,'moeda':'USD'})

class Sugestor:
    origem='openai_real'
    def __init__(self,transporte):self.transporte=transporte
    def snapshot(self):return self.transporte.snapshot()
    def __call__(self,pedido):
        obj=lambda p:dict(type='object',properties=p,required=list(p),additionalProperties=False)
        schema=obj({'sugestoes':{'type':'array','items':obj({'no_id':{'type':'string','enum':[n['id'] for n in pedido['catalogo']]},'justificativa':{'type':'string'}})},'ambiguidades':{'type':'array','items':{'type':'string'}}})
        r,_=self.transporte.gerar([{'role':'system','content':'Selecione os pontos diretamente mencionados pelo evento como entradas de análise. Não liste sucessores apenas por propagação. Use somente IDs do catálogo. Não calcule prazo/custo. Se ambíguo, registre ambiguidades. Retorne JSON.'},{'role':'user','content':json.dumps(pedido,ensure_ascii=False)}],dict(type='json_schema',name='selecao_entrada',strict=True,schema=schema),'sugestao_entrada')
        if r.get('status')!='completed':raise ValueError('Sugestão incompleta')
        return json.loads(''.join(p['text'] for item in r.get('output',[]) for p in item.get('content',[]) if p['type']=='output_text'))
