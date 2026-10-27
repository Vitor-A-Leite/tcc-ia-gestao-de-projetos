"""Mesma sequência HTTP histórica; telemetria de erro limitada a enums seguros."""
import http.client,json,multiprocessing,ssl
from piloto_real.transporte import sanitizar,HTTP
from interpretacao_no.adaptadores import FalhaTransporte
CLASSES={'SSLError','SSLCertVerificationError','TimeoutError','gaierror','OSError','ConnectionError','ConnectionResetError','ConnectionAbortedError','BrokenPipeError','RemoteDisconnected','IncompleteRead','BadStatusLine','JSONDecodeError','UnicodeDecodeError','ValueError','TypeError'}
def seguro(exc,fase):
    n=type(exc).__name__;e=getattr(exc,'errno',None)
    return dict(fase=fase,classe_excecao=n if n in CLASSES else 'nao_catalogada',errno=e if type(e)is int else None)
def worker(pipe,path,payload,chave,timeout):
    fase='conexao'
    try:
        c=http.client.HTTPSConnection('api.openai.com',timeout=timeout,context=ssl.create_default_context())
        try:
            fase='envio'
            c.request('POST','/v1/responses'+path,body=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+chave})
            fase='cabecalho';r=c.getresponse()
            if r.status!=200:
                code=None
                try:
                    fase='leitura';bruto=r.read(8192);fase='JSON';e=json.loads(bruto).get('error',{}).get('code')
                    if e in ('invalid_api_key','insufficient_quota','rate_limit_exceeded','context_length_exceeded','model_not_found','invalid_value','unsupported_parameter','invalid_request_error','server_error'):code=e
                except Exception:pass
                pipe.send(dict(erro='http',status=r.status,provider_code=code));return
            fase='leitura';bruto=r.read(4*1024*1024+1)
            if len(bruto)>4*1024*1024:pipe.send(dict(erro='resposta_grande'));return
            fase='JSON';pipe.send(dict(body=sanitizar(json.loads(bruto),chave)))
        finally:
            # Não perder a fase do erro anterior caso close também falhe.
            import sys
            if sys.exc_info()[0]is None:fase='fechamento'
            c.close()
    except Exception as exc:pipe.send(dict(erro='http_indisponivel',telemetria=seguro(exc,fase)))
    finally:pipe.close()
class HTTPSeguro(HTTP):
    def post(self,path,payload,timeout):
        if path not in ('','/input_tokens')or timeout<=0:raise FalhaTransporte('deadline','Deadline sem tempo restante')
        ctx=multiprocessing.get_context('spawn');a,b=ctx.Pipe(duplex=False)
        p=ctx.Process(target=worker,args=(b,path,payload,self._chave,timeout));p.start();b.close()
        try:
            if not a.poll(timeout):raise FalhaTransporte('timeout','Deadline HTTP excedido; custo pode ser desconhecido')
            r=a.recv()
            if 'erro'in r:raise FalhaTransporte(r['erro'],'Falha HTTP sanitizada',metadados={'status_http':r.get('status'),'provider_code':r.get('provider_code'),**r.get('telemetria',{})})
            return r['body']
        except (EOFError,OSError)as exc:raise FalhaTransporte('http_indisponivel','Resposta HTTP indisponível',metadados=seguro(exc,'processo'))from None
        finally:
            if p.is_alive():p.terminate()
            p.join(timeout=1);a.close()
