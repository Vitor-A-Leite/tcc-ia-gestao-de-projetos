"""Monta payloads locais exatos para verificar limite em bytes, sem chave/API."""
import json
from . import ROOT
from .dados import gravar
from .integridade import sha
from hibrido_v07_r3.formato import SISTEMA,compilar
from hibrido_v07_r3.schema import formato
from interpretacao_no.contratos import hash_json


def conferir(resultados):
    rows=[]
    for file in sorted(resultados.glob('D[0-9][0-9].json')):
        r=json.loads(file.read_text())
        for step in r['rastro_orquestracao']:
            c=step['contexto'];effects={p['alvo_id']:hash_json([c['evento_id'],p['alvo_id']]) for p in c['permissoes']}
            data=dict(contexto=c,efeitos_canonicos=effects,contrato_resposta=compilar(c,effects))
            payload=dict(input=[dict(role='system',content=SISTEMA),dict(role='user',content=json.dumps(data,ensure_ascii=False,allow_nan=False))],text={'format':formato(c)},stream=True,truncation='disabled',max_output_tokens=25000)
            count=len(json.dumps(payload,ensure_ascii=False).encode())
            rows.append(dict(cenario=r['cenario_id'],no=c['no_id'],bytes_payload_parcial=count,limite_historico_bytes=100000,dentro_limite_bytes=count<99500,payload_hash=hash_json(payload)))
    return dict(natureza='offline_sem_contagem_de_tokens',contextos=len(rows),max_bytes=max(r['bytes_payload_parcial'] for r in rows),todos_dentro_limite_bytes=all(r['dentro_limite_bytes'] for r in rows),
                tokens_oficiais=None,limite_entrada_tokens=16000,aviso='Modelo/configuração/wrappers HTTP acrescentam bytes; a verificação final usa payload real. Bytes não são tokens. Toda chamada paga exige contagem oficial sem truncamento.',contextos_medidos=rows)
