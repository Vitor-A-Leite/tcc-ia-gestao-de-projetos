"""SSE limitado e incremental. Somente o Response terminal é resultado."""
import codecs,json,re
from collections import Counter
from interpretacao_no.adaptadores import _json
MAX_TOTAL=8*1024*1024
MAX_EVENTO=4*1024*1024
MAX_EVENTOS=100000
CODIGOS={'invalid_api_key','insufficient_quota','rate_limit_exceeded','context_length_exceeded','model_not_found','invalid_value','unsupported_parameter','invalid_request_error','server_error'}
class ErroSSE(Exception):
    def __init__(self,codigo,**meta):
        super().__init__('Falha SSE sanitizada');self.codigo=codigo;self.metadados=meta
class ParserSSE:
    def __init__(self,*,max_total=MAX_TOTAL,max_evento=MAX_EVENTO,max_eventos=MAX_EVENTOS):
        self.decoder=codecs.getincrementaldecoder('utf-8')('strict');self.buffer='';self.data=[];self.evento=None;self.event_bytes=0
        self.total=0;self.eventos=Counter();self.n=0;self.refusal=False;self.response=None;self.terminal=None
        self.max_total=max_total;self.max_evento=max_evento;self.max_eventos=max_eventos;self.inicio=True
    def resumo(self):return dict(bytes_recebidos=self.total,eventos=dict(self.eventos),terminal=self.terminal,refusal_evento=self.refusal)
    def _linha(self,line):
        self.event_bytes+=len(line.encode('utf-8'))+1
        if self.event_bytes>self.max_evento:raise ErroSSE('sse_limite_evento')
        if line=='':
            self._despachar();self.data=[];self.evento=None;self.event_bytes=0;return
        if line.startswith(':'):return
        field,sep,value=line.partition(':')
        if value.startswith(' '):value=value[1:]
        if field=='data':self.data.append(value)
        elif field=='event':self.evento=value
        # id/retry/campos desconhecidos não alteram a resposta nem o deadline.
    def _despachar(self):
        if not self.data:return
        self.n+=1
        if self.n>self.max_eventos:raise ErroSSE('sse_limite_eventos')
        try:obj=_json('\n'.join(self.data))
        except (ValueError,TypeError,RecursionError):raise ErroSSE('sse_json_malformado')from None
        if not isinstance(obj,dict)or not isinstance(obj.get('type'),str):raise ErroSSE('sse_evento_malformado')
        tipo=obj['type']
        if self.evento and self.evento!=tipo:raise ErroSSE('sse_tipo_divergente')
        # Não acumular tipos arbitrários enviados pelo servidor em metadados.
        grupo=tipo if tipo in ('response.created','response.in_progress','response.completed','response.failed','response.incomplete','response.refusal.delta','response.refusal.done','error')else 'outros'
        self.eventos[grupo]+=1
        if tipo in ('response.refusal.delta','response.refusal.done'):self.refusal=True
        if tipo=='error':
            code=obj.get('code');raise ErroSSE('sse_error',provider_code=code if isinstance(code,str)and code in CODIGOS else None)
        finais={'response.completed':'completed','response.failed':'failed','response.incomplete':'incomplete'}
        if tipo not in finais:return
        r=obj.get('response')
        if not isinstance(r,dict)or r.get('status')!=finais[tipo]or r.get('object')!='response'or not isinstance(r.get('id'),str)or not r['id']or not isinstance(r.get('output'),list):raise ErroSSE('sse_terminal_malformado')
        if tipo=='response.completed'and (r.get('error')is not None or r.get('incomplete_details')is not None):raise ErroSSE('sse_terminal_divergente')
        if self.refusal and tipo=='response.completed'and not any(c.get('type')=='refusal'for i in r['output']if isinstance(i,dict)for c in i.get('content',[])if isinstance(c,dict)):raise ErroSSE('sse_recusa_divergente')
        self.response=r;self.terminal=tipo
    def feed(self,chunk):
        if self.response is not None:return self.response
        if not isinstance(chunk,bytes):raise ErroSSE('sse_chunk_invalido')
        self.total+=len(chunk)
        if self.total>self.max_total:raise ErroSSE('sse_limite_total')
        try:part=self.decoder.decode(chunk,final=False)
        except UnicodeError:raise ErroSSE('sse_utf8_invalido')from None
        if self.inicio and part:
            part=part.removeprefix('\ufeff')if hasattr(part,'removeprefix')else part.lstrip('\ufeff');self.inicio=False
        self.buffer+=part
        while self.response is None:
            m=re.search('[\r\n]',self.buffer)
            if m is None:break
            n=m.start()
            if self.buffer[n]=='\r'and n+1==len(self.buffer):break
            size=2 if self.buffer[n:n+2]=='\r\n'else 1
            line=self.buffer[:n];self.buffer=self.buffer[n+size:];self._linha(line)
        if len(self.buffer.encode('utf-8'))>self.max_evento:raise ErroSSE('sse_limite_linha')
        return self.response
    def eof(self):
        if self.response is not None:return self.response
        try:self.decoder.decode(b'',final=True)
        except UnicodeError:raise ErroSSE('sse_utf8_truncado')from None
        # CR isolado é delimitador SSE legítimo; demais bytes sem separador
        # não formam evento terminal completo e nunca são "reparados".
        if self.buffer.endswith('\r'):
            line=self.buffer[:-1];self.buffer='';self._linha(line)
            if self.response is not None:return self.response
        raise ErroSSE('sse_eof_sem_terminal')

def ler_sse(reader,deadline,*,agora,parser=None):
    p=parser or ParserSSE()
    while True:
        if agora()>=deadline:raise ErroSSE('timeout',sse=p.resumo())
        chunk=reader.read1(16384)
        if agora()>=deadline:raise ErroSSE('timeout',sse=p.resumo())
        try:r=p.feed(chunk)if chunk else p.eof()
        except ErroSSE as e:
            e.metadados['sse']=p.resumo();raise
        if r is not None:return r,p.resumo()
