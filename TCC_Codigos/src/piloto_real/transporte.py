"""Responses HTTP concreto, sem SDK/retry/redirect/proxy/ferramentas."""
from copy import deepcopy
import http.client
import json
import multiprocessing
import re
import ssl
from time import monotonic
from interpretacao_no.adaptadores import RespostaTransporte,FalhaTransporte
from interpretacao_no.contratos import hash_json
from . import MODELO,CONFIG
from .ledger import Bloqueio


def inteiro(x):
    if type(x)is not int or x<0:raise ValueError('Usage inválido')
    return x


def custo_usage(u):
    """Categorias de input disjuntas; reasoning já está em output_tokens."""
    i,o=inteiro(u['input_tokens']),inteiro(u['output_tokens'])
    if i>16000 or o>25000 or inteiro(u['total_tokens'])!=i+o:raise ValueError('Usage excede limites/total')
    d=u['input_tokens_details'];cached=inteiro(d['cached_tokens']);write=inteiro(d['cache_write_tokens'])
    w=d.get('cache_write_tokens_details')
    if w is None:
        # ttl30m foi explicitamente enviado; ausência de split não comprova desvio12h.
        w30,w12=write,0
    else:w30,w12=inteiro(w['ttl_30m_tokens']),inteiro(w['ttl_12h_tokens'])
    if w30+w12!=write or cached+write>i or w12:raise ValueError('Cache incoerente ou retenção não autorizada')
    reasoning=inteiro(u['output_tokens_details']['reasoning_tokens'])
    if reasoning>o:raise ValueError('Reasoning maior que output')
    return (i-cached-write)*100+cached*10+w30*125+o*500


def sanitizar(x,chave):
    if isinstance(x,str):
        if chave:x=x.replace(chave,'[SEGREDO_REMOVIDO]')
        return re.sub(r'sk-[A-Za-z0-9_\-]+','[SEGREDO_REMOVIDO]',x)
    if isinstance(x,list):return [sanitizar(v,chave) for v in x]
    if isinstance(x,dict):return {k:sanitizar(v,chave) for k,v in x.items() if k.lower() not in ('authorization','headers','api_key','openai_api_key')}
    return x


def _http_worker(pipe,path,payload,chave,timeout):
    """Processo terminável: deadline inclui DNS/connect/TLS/read."""
    try:
        c=http.client.HTTPSConnection('api.openai.com',timeout=timeout,context=ssl.create_default_context())
        try:
            c.request('POST','/v1/responses'+path,body=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+chave})
            r=c.getresponse()
            if r.status!=200:
                # Preserva só códigos conhecidos; nunca mensagem, corpo ou headers.
                code=None
                try:
                    e=json.loads(r.read(8192)).get('error',{}).get('code')
                    if e in ('invalid_api_key','insufficient_quota','rate_limit_exceeded','context_length_exceeded','model_not_found','invalid_value','unsupported_parameter','invalid_request_error','server_error'):code=e
                except Exception:pass
                pipe.send(dict(erro='http',status=r.status,provider_code=code));return
            bruto=r.read(4*1024*1024+1)
            if len(bruto)>4*1024*1024:pipe.send(dict(erro='resposta_grande'));return
            pipe.send(dict(body=sanitizar(json.loads(bruto),chave)))
        finally:c.close()
    except Exception:pipe.send(dict(erro='http_indisponivel'))
    finally:pipe.close()


class HTTP:
    def __init__(self,chave):self._chave=chave
    def post(self,path,payload,timeout):
        if path not in ('','/input_tokens') or timeout<=0:raise FalhaTransporte('deadline','Deadline sem tempo restante')
        ctx=multiprocessing.get_context('spawn');a,b=ctx.Pipe(duplex=False)
        p=ctx.Process(target=_http_worker,args=(b,path,payload,self._chave,timeout));p.start();b.close()
        try:
            if not a.poll(timeout):raise FalhaTransporte('timeout','Deadline HTTP excedido; custo pode ser desconhecido')
            r=a.recv()
            if 'erro' in r:raise FalhaTransporte(r['erro'],'Falha HTTP sanitizada',metadados={'status_http':r.get('status'),'provider_code':r.get('provider_code')})
            return r['body']
        except (EOFError,OSError):raise FalhaTransporte('http_indisponivel','Resposta HTTP indisponível') from None
        finally:
            if p.is_alive():p.terminate()
            p.join(timeout=1);a.close()


class Responses:
    def __init__(self,ledger,slot,http,*,redator=lambda x:x,timeout_s=30):
        self.ledger,self.slot,self.http=ledger,slot,http
        self.redator,self.timeout_s=redator,timeout_s
        self.ultimo=None
    def __call__(self,req):
        if req.get('modelo')!=MODELO or req.get('configuracao')!=CONFIG or req.get('formato')!='json':
            raise FalhaTransporte('configuracao','Modelo/configuração divergem do aprovado')
        mensagens=req['mensagens']
        if len(mensagens)!=2 or [m['papel'] for m in mensagens]!=['sistema','usuario'] or not all(isinstance(m['conteudo'],str) for m in mensagens):raise FalhaTransporte('entrada','Formato de mensagens inválido')
        mensagens=deepcopy(mensagens)
        try:local=json.loads(mensagens[1]['conteudo']).get('contexto')
        except (ValueError,TypeError,AttributeError):local=None
        if local is not None:
            mensagens[0]['conteudo'] += ('\nContrato operacional condicional2.0: IDs de propostas devem ser únicos em toda a execução; prefixe cada id com no_id e um índice local. Use os efeitos_canonicos copiados da mensagem. Interprete todas as cláusulas locais de duração e readequação do catálogo; ausência de proposta não resolve cláusula obrigatória. Aplique confirmação somente se sua interpretação declarar a condição confirmada. Sem resolução, proponha conhecimento indeterminado e lacuna explícita. IDs de obrigação com prefixo lacuna_ servem apenas para registrar_lacuna_custo, nunca para cobrança exata. Não acrescente campos fora do schema. Toda conclusão é original condicional e será auditada depois; não alegue revisão humana.')
        # Mesmo modelo/input/reasoning/text nas duas operações. Nenhum truncamento.
        comum=dict(model=MODELO,input=[dict(role='system' if m['papel']=='sistema' else 'user',content=m['conteudo']) for m in mensagens],reasoning=deepcopy(CONFIG['reasoning']),text={'format':{'type':'json_object'}})
        payload=dict(**comum,max_output_tokens=25000,service_tier='default',prompt_cache_options={'ttl':'30m'},tools=[],store=False,truncation='disabled')
        # Limite de bytes é proteção de memória/HTTP, não estimador de tokens.
        if len(json.dumps(payload,ensure_ascii=False).encode())>100000:raise FalhaTransporte('entrada_grande','Payload excede proteção local de bytes; não foi enviado nem contado')
        try:id=self.ledger.reservar(self.slot,hash_json(payload))
        except Bloqueio:raise FalhaTransporte('orcamento','Teto agregado/per-slot bloqueou tentativa') from None
        registro=dict(call_id=id,payload=self.redator(payload),contagem_payload=self.redator(comum),limite_entrada=16000,limite_saida_total=25000,timeout_s=self.timeout_s,tokenizacao='oficial_responses_input_tokens',retry=0)
        deadline=monotonic()+min(self.timeout_s,req.get('timeout_s',30))
        try:
            self.ledger.iniciar_contagem(id)
            cnt=self.http.post('/input_tokens',comum,deadline-monotonic())
            if cnt.get('object')!='response.input_tokens':raise ValueError('Envelope de contagem inválido')
            n=inteiro(cnt['input_tokens']);registro['contagem_oficial']=n
            self.ledger.contar(id,n)
            if n>16000:
                registro['inadequacao_escopo']='Contagem oficial maior que16k invalida hipótese de entrada/provisão desta tentativa'
                self.ledger.nao_enviado(id,registro)
                self.ledger.parar('Entrada oficial maior que16k; revisar escopo e hipótese da provisão de contagem')
                raise FalhaTransporte('entrada_tokens','Contagem oficial excedeu16.000; inferência não enviada')
            self.ledger.enviar(id)
            bruto=self.redator(self.http.post('',payload,deadline-monotonic()))
            registro['response']=bruto
            self.ultimo=bruto
            # Medição é independente da validade do conteúdo. Falta de usage mantém
            # a reserva, mas não apaga uma previsão entregue pelo provedor.
            custo=None
            registro['modelo_observado']=bruto.get('model')
            registro['modelo_solicitado']=MODELO
            registro['ecos_opcionais_ausentes']=[k for k in ('service_tier','prompt_cache_options') if k not in bruto]
            divergencia=(bruto.get('model') not in (None,MODELO)
                         or bruto.get('service_tier','default')!='default'
                         or bruto.get('prompt_cache_options',{}).get('ttl','30m')!='30m')
            registro['protocolo_provider']='divergente' if divergencia else 'compativel_com_request'
            try:
                if divergencia:raise ValueError('Protocolo observado divergente')
                custo=custo_usage(bruto['usage'])
                self.ledger.concluir(id,custo,bruto['usage'],registro)
            except (ValueError,KeyError,TypeError):
                self.ledger.desconhecido(id,registro)
                u=bruto.get('usage') or {}
                limites_violados=(type(u.get('input_tokens'))is int and u['input_tokens']>16000) or (type(u.get('output_tokens'))is int and u['output_tokens']>25000)
                if divergencia or limites_violados:self.ledger.parar('Modelo/tier/cache observado divergente; revisar sem repetir')
            textos=[];recusa=False
            for item in bruto.get('output',[]):
                if item.get('type')=='message':
                    for cont in item.get('content',[]):
                        if cont.get('type')=='output_text':textos.append(cont['text'])
                        if cont.get('type')=='refusal':recusa=True
            estado='recusa' if recusa else 'completa' if bruto.get('status')=='completed' else 'incompleta'
            return RespostaTransporte(texto=''.join(textos),estado=estado,modelo=bruto.get('model'),request_id=bruto.get('id'),tokens_entrada=bruto.get('usage',{}).get('input_tokens') if custo is not None else None,tokens_saida=bruto.get('usage',{}).get('output_tokens') if custo is not None else None,custo_api_centavos=None,metadados={**registro,'custo_inferencia_nanoUSD':custo,'custo_api_moeda':'USD','provisao_contagem_nao_e_cobranca_comprovada':True})
        except BaseException as exc:
            # Inclui interrupção antes/depois do envio; reserva nunca é liberada sem usage.
            registro['erro']=getattr(exc,'codigo','falha_sanitizada')
            registro['falha_transporte']=self.redator(getattr(exc,'metadados',{}))
            if getattr(exc,'metadados',{}).get('status_http') in (401,403):self.ledger.parar('Autenticação recusada; não repetir o lote')
            self.ledger.desconhecido(id,registro)
            if isinstance(exc,(KeyboardInterrupt,SystemExit)):raise
            if isinstance(exc,FalhaTransporte):raise
            raise FalhaTransporte('transporte','Falha de transporte sanitizada; reserva mantida',metadados={'call_id':id}) from None
