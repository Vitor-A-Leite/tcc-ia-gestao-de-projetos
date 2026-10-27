"""Leitura positiva de15 avisos quantitativos; não lê fixtures/referências/outputs."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
from interpretacao_no.contratos import hash_json
from condicoes.views import montar_views,auditar_equivalencia
from .politica import normalizar


def carregar(dados):
    dados=Path(dados);casos=[]
    for nome,grafo in [('projeto_minimo_v1','projeto_minimo_grafo_v1/estado_projeto.json'),('ampliacao_v1','ampliacao_v1/inputs/estado_projeto.json')]:
        raiz=dados/nome
        paths=dict(base=raiz/'inputs/base.json',fontes=raiz/'inputs/fontes.json',cenarios=raiz/'inputs/cenarios.json',estado=dados/grafo)
        objetos={};hashes={}
        for k,p in paths.items():
            bruto=p.read_bytes();objetos[k]=json.loads(bruto);hashes[k]=dict(path=str(p.resolve()),sha256=hashlib.sha256(bruto).hexdigest())
        b,fs,e=objetos['base'],objetos['fontes']['fontes'],objetos['estado']
        for ev in objetos['cenarios']['casos']:
            cid=ev['caso_id']
            if not isinstance(cid,str) or not cid.startswith('k_') or not cid[2:].isalnum():raise ValueError('ID inválido')
            evento=normalizar(b,fs,e,ev)
            v=dict(base_hash=hash_json(b),grafo_hash=hash_json(e),versao_base=b['versao_projeto'],versao_grafo=e['versao'])
            views=montar_views(b,ev,fs,e,vinculo=v);equiv=auditar_equivalencia(views)
            # Somente fontes vigentes, inclusive no objeto que entra no H.
            vigentes=set(b['documentos_comuns']+b['documentos_relacionais']+[ev['documento_evento_vigente']])
            casos.append(dict(caso_id=cid,base=deepcopy(b),fontes=[deepcopy(f) for f in fs if f['documento_id'] in vigentes],estado=deepcopy(e),evento_comum=deepcopy(ev),evento=evento,views=views,vinculo=v,equivalencia=equiv,hashes_inputs=deepcopy(hashes)))
    if len(casos)!=15 or len({x['caso_id'] for x in casos})!=15:raise ValueError('O escopo aprovado requer exatamente15 avisos distintos')
    return casos
