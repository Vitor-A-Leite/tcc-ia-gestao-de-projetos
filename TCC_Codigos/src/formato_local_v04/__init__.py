"""Formato novo opt-in. Não habilita CLI ou carteira/coleta paga existente."""
from copy import deepcopy
import json
from interpretacao_no.adaptadores import LLM as LLMAnterior
from interpretacao_no.contratos import hash_json
from piloto_real.transporte import Responses
from .contrato import VERSAO,SISTEMA,compilar


def preparar_requisicao(req):
    if req['formato']!='json':raise ValueError('Formato incompatível')
    dados=json.loads(req['mensagens'][1]['conteudo'])
    if set(dados)!={'contexto','efeitos_canonicos'}:raise ValueError('Entrada local inesperada')
    contrato=compilar(dados['contexto'],dados['efeitos_canonicos'])
    novo=deepcopy(req);novo['versao_formato_local']=VERSAO
    novo['mensagens'][0]['conteudo']=SISTEMA
    novo['mensagens'][1]['conteudo']=json.dumps({**dados,'contrato_resposta':contrato},ensure_ascii=False,allow_nan=False)
    return novo


class LocalV04:
    """Mesmo parser/envelope do adaptador anterior; só muda pedido antes de gerar."""
    versao_formato_local=VERSAO
    def __init__(self,transporte,*,modelo,configuracao,timeout_s):
        if getattr(transporte,'versao_formato_local',None)!=VERSAO:raise ValueError('Transporte precisa vincular formato4.0;v03/diagnóstico não são substituídos')
        self.transporte=transporte;self.modelo=modelo;self.configuracao=deepcopy(configuracao);self.timeout_s=timeout_s;self.repetir=False
    def analisar(self,c):
        info={}
        def enviar(req):
            novo=preparar_requisicao(req)
            info.update(versao_formato_local=VERSAO,requisicao_adaptador_hash=hash_json(novo),contrato_resposta_hash=hash_json(json.loads(novo['mensagens'][1]['conteudo'])['contrato_resposta']))
            return self.transporte(novo)
        a=LLMAnterior(enviar,modelo=self.modelo,configuracao=self.configuracao,timeout_s=self.timeout_s,repetir_transporte=False).analisar(c)
        a['execucao'].update(info)
        return a


class ResponsesV04(Responses):
    """Caminho HTTP/contagem existentes, com vínculo de coleta novo obrigatório.

    A próxima carteira/adendo deverá expor manifesto_formato persistido. Esta
    entrega não registra nem altera carteira alguma; os lotes antigos são recusados.
    """
    versao_formato_local=VERSAO
    def __init__(self,ledger,slot,http,*,redator=lambda x:x,timeout_s):
        manifesto=getattr(ledger,'manifesto_formato',None)
        if not isinstance(manifesto,dict) or manifesto.get('versao_formato_local')!=VERSAO or slot not in manifesto.get('slots',[]):raise ValueError('Coleta com formato4.0 precisa de manifesto próprio registrado')
        if slot in {s['execucao_id']for s in getattr(ledger,'plano',{}).get('slots',[])}:raise ValueError('Não usar slots históricos v03 para o formato4.0')
        super().__init__(ledger,slot,http,redator=redator,timeout_s=timeout_s)
    def __call__(self,req):
        if req.get('versao_formato_local')!=VERSAO:raise ValueError('Pedido sem versão4.0 não será enviado')
        dados=json.loads(req['mensagens'][1]['conteudo'])
        if dados.get('contrato_resposta')!=compilar(dados['contexto'],dados['efeitos_canonicos']) or req['mensagens'][0]['conteudo']!=SISTEMA:raise ValueError('Contrato/prompt divergente da versão4.0')
        # O transporte está congelado no v03. Sua nota geral da política2.0 é
        # compatível e continua no payload; não substitui as instruções4.0 acima.
        return super().__call__(req)
