"""Clone versionado mínimo do adaptador histórico: geração acrescenta stream:true."""
from copy import deepcopy
import json
from time import monotonic
from piloto_real.transporte import Responses,inteiro,custo_usage
from piloto_real import MODELO,CONFIG
from piloto_real.ledger import Bloqueio
from interpretacao_no.adaptadores import RespostaTransporte,FalhaTransporte
from interpretacao_no.contratos import hash_json
from formato_local_v04 import ResponsesV04
class ResponsesSSE(Responses):
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
        payload=dict(**comum,stream=True,max_output_tokens=25000,service_tier='default',prompt_cache_options={'ttl':'30m'},tools=[],store=False,truncation='disabled')
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
            registro['transporte_sse']=deepcopy(getattr(self.http,'ultimo_sse',None))
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
            if bruto.get('status')in ('failed','incomplete'):self.ledger.parar('Terminal SSE '+bruto['status']+'; sem previsão parcial/retry')
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
            registro['transporte_sse']=deepcopy(getattr(self.http,'ultimo_sse',None))
            registro['falha_transporte']=self.redator(getattr(exc,'metadados',{}))
            if getattr(exc,'metadados',{}).get('status_http') in (401,403):self.ledger.parar('Autenticação recusada; não repetir o lote')
            self.ledger.desconhecido(id,registro)
            if isinstance(exc,(KeyboardInterrupt,SystemExit)):raise
            if isinstance(exc,FalhaTransporte):raise
            raise FalhaTransporte('transporte','Falha de transporte sanitizada; reserva mantida',metadados={'call_id':id}) from None

class LocalSSE(ResponsesV04,ResponsesSSE):
    """Validação v04 anterior passa ao __call__ SSE via MRO; mesmo contexto/prompt."""
    pass
