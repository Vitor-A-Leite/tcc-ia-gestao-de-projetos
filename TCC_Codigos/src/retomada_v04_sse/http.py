"""Um deadline externo fixo. Contagem JSON intacta; geração SSE sem retries."""
import http.client,json,multiprocessing,ssl
from time import monotonic
from piloto_real.transporte import HTTP,sanitizar
from retomada_v04.http import seguro
from interpretacao_no.adaptadores import FalhaTransporte
from .parser import ler_sse,ErroSSE,CODIGOS

def worker(pipe,path,payload,chave,timeout):
    fase='conexao';deadline=monotonic()+timeout
    try:
        c=http.client.HTTPSConnection('api.openai.com',timeout=timeout,context=ssl.create_default_context())
        try:
            fase='envio';c.request('POST','/v1/responses'+path,body=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+chave})
            fase='cabecalho';r=c.getresponse()
            if r.status!=200:
                code=None
                try:
                    fase='leitura';bruto=r.read(8192);fase='JSON';code=json.loads(bruto).get('error',{}).get('code')
                except Exception:pass
                pipe.send(dict(erro='http',status=r.status,provider_code=code if isinstance(code,str)and code in CODIGOS else None));return
            if path=='/input_tokens':
                fase='leitura';bruto=r.read(4*1024*1024+1)
                if len(bruto)>4*1024*1024:raise ErroSSE('resposta_grande')
                fase='JSON';body=json.loads(bruto);telemetria=None
            else:
                if r.getheader('Content-Type','').split(';')[0].strip().lower()!='text/event-stream':raise ErroSSE('sse_content_type')
                fase='SSE';body,telemetria=ler_sse(r,deadline,agora=monotonic)
            if monotonic()>=deadline:raise ErroSSE('timeout')
            pipe.send(dict(body=sanitizar(body,chave),sse=telemetria))
        finally:c.close()
    except ErroSSE as e:pipe.send(dict(erro=e.codigo,telemetria=e.metadados))
    except Exception as e:pipe.send(dict(erro='http_indisponivel',telemetria=seguro(e,fase)))
    finally:pipe.close()
class HTTPStreaming(HTTP):
    def __init__(self,chave):super().__init__(chave);self.ultimo_sse=None
    def post(self,path,payload,timeout):
        if path not in ('','/input_tokens')or timeout<=0:raise FalhaTransporte('deadline','Deadline sem tempo restante')
        if (path==''and payload.get('stream')is not True)or(path=='/input_tokens'and 'stream'in payload):raise FalhaTransporte('stream_config','Stream fora do escopo aprovado')
        self.ultimo_sse=None;deadline=monotonic()+timeout
        # Uma única espera pelo processo; eventos não renovam este timeout.
        ctx=multiprocessing.get_context('spawn');a,b=ctx.Pipe(duplex=False)
        p=ctx.Process(target=worker,args=(b,path,payload,self._chave,timeout));p.start();b.close()
        try:
            restante=deadline-monotonic()
            if restante<=0 or not a.poll(restante):raise FalhaTransporte('timeout','Deadline total HTTP/SSE excedido')
            r=a.recv()
            if monotonic()>=deadline:raise FalhaTransporte('timeout','Deadline total HTTP/SSE excedido')
            self.ultimo_sse=r.get('sse')or r.get('telemetria',{}).get('sse')
            if 'erro'in r:raise FalhaTransporte(r['erro'],'Falha HTTP/SSE sanitizada',metadados={'status_http':r.get('status'),'provider_code':r.get('provider_code'),**r.get('telemetria',{})})
            return r['body']
        except (EOFError,OSError)as e:raise FalhaTransporte('http_indisponivel','Resposta HTTP indisponível',metadados=seguro(e,'processo'))from None
        finally:
            if p.is_alive():p.terminate()
            p.join(timeout=1);a.close()
