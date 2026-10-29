"""Preparação exclusivamente offline. Não possui transporte nem opção de coleta.

Carrega somente quatro arquivos permitidos; não conhece gabaritos nem interpreta
eventos. As views e a política usam o preditor 7.2 já congelado.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'TCC_Codigos/src'))
from condicoes.views import montar_views,auditar_equivalencia
from hibrido_v07_r3 import construir,montar_contexto
from hibrido_v07_r3.politica import normalizar,POLITICA
from hibrido_v07_r3.schema import gerar
from hibrido_v07_r3.avaliacao import validar_manifesto
from interpretacao_no.contratos import hash_json
from motor_deterministico.motor import validar_estado
from piloto_real import MODELO,CONFIG

ID='etapa11-final-v1-3-BHT-R1'


def exigir(c,m):
    if not c:raise ValueError(m)


def carregar(raiz):
    nomes=('base.json','fontes.json','estado_projeto.json','cenarios.json')
    objetos={n:json.loads((raiz/n).read_text()) for n in nomes}
    b=objetos['base.json'];fs=objetos['fontes.json']['fontes'];e=objetos['estado_projeto.json']
    validar_estado(e)
    cenarios=objetos['cenarios.json']['casos']
    exigir(len(cenarios)==3 and len({x['caso_id'] for x in cenarios})==3,'Exatamente três casos inéditos')
    exigir(len(e['entidades'])<=8,'Limite de nós')
    casos=[]
    for ev in sorted(cenarios,key=lambda c:c['caso_id']):
        evento=normalizar(b,fs,e,ev)
        v=dict(base_hash=hash_json(b),grafo_hash=hash_json(e),versao_base=b['versao_projeto'],versao_grafo=e['versao'])
        views=montar_views(b,ev,fs,e,vinculo=v)
        equiv=auditar_equivalencia(views)
        vigentes=set(b['documentos_comuns']+b['documentos_relacionais']+[ev['documento_evento_vigente']])
        casos.append(dict(caso_id=ev['caso_id'],base=deepcopy(b),estado=deepcopy(e),evento=evento,
                          evento_comum=deepcopy(ev),fontes=[deepcopy(f) for f in fs if f['documento_id'] in vigentes],
                          views=views,vinculo=v,equivalencia=equiv))
    hashes={str((raiz/n).relative_to(ROOT)):hashlib.sha256((raiz/n).read_bytes()).hexdigest() for n in nomes}
    return casos,hashes


def rejeitar(operacao,motivo):
    try:operacao()
    except (ValueError,KeyError):return motivo
    raise ValueError('Contraprova não rejeitada: '+motivo)


def main():
    raiz=ROOT/'TCC_Codigos/data/final/etapa10_v1/inputs'
    casos,hashes=carregar(raiz)
    congelado=json.loads((OUT/'codigo_pre_dados_finais.json').read_text())['arquivos']
    atual={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'TCC_Codigos/src').rglob('*.py'))}
    exigir(congelado==atual,'Código alterado durante autoria/revisão final')
    antigos=[]
    for nome in ['projeto_minimo_v1','ampliacao_v1']:
        antigos+=json.loads((ROOT/'TCC_Codigos/data/desenvolvimento'/nome/'inputs/cenarios.json').read_text())['casos']
    exigir(not {c['caso_id'] for c in casos}&{c['caso_id'] for c in antigos},'Caso reutilizado')
    exigir(not {c['estado']['projeto_id'] for c in casos}&{c['projeto_id'] for c in antigos},'Projeto reutilizado')
    exigir(not {c['evento']['relato'] for c in casos}&{c['relato'] for c in antigos},'Evento copiado')
    slots=[];contextos=[];contraprovas=[]
    for idx,c in enumerate(casos):
        ev=c['evento_comum'];b=c['base'];e=c['estado']
        for cond in ('BHT','HTB','TBH')[idx]:
            sid=ID+'-'+c['caso_id']+'-'+cond+'-1'
            slots.append(dict(execucao_id=sid,caso_id=c['caso_id'],repeticao=1,condicao=cond,projeto_id=e['projeto_id'],
                evento_id=ev['evento_id'],versao_projeto=e['versao'] if cond=='H' else b['versao_projeto'],
                versao_protocolo=POLITICA if cond=='H' else ID,view_hash=c['views'][cond]['view_hash'],
                snapshot_hash=hash_json(e),evento_hash=hash_json(c['evento']),codigo_hash=hash_json(congelado),
                modelo=MODELO,config_hash=hash_json(CONFIG),origem='llm_transporte_injetado'))
        # Somente construir contextos/schema; não executar interpretador ou motor.
        p=construir(e,c['evento'],execucao_id=ID+'-'+c['caso_id']+'-H-1')
        for no,selecao in p.plano.items():
            ctx=montar_contexto(e,c['evento'],execucao_id=p.execucao_id,no_id=no,revisao=1,
                 responsabilidades_operacionais=p.responsabilidades_operacionais,**selecao)
            schema=gerar(ctx)
            exigir(len(json.dumps(schema,ensure_ascii=False).encode())<50000,'Schema excede tamanho verificado')
            contextos.append(dict(caso_id=c['caso_id'],no_id=no,contexto=ctx,schema=schema))
        for cond,v in c['views'].items():
            # Os únicos documentos nos fatos comuns são os comuns e o aviso corrente.
            exigir({f['documento_id'] for f in v['comum']['fontes']}==set(b['documentos_comuns']+[ev['documento_evento_vigente']]),'Outro aviso visível')
            exigir('caso_id' not in v['comum']['evento'],'Rótulo de caso no evento visível')
            if cond=='B':exigir('relacional' not in v and 'relacoes_texto' not in v,'Relações exclusivas em B')
        adulterado=deepcopy(b);adulterado['linha_base_declarada']['fim_dia']+=1
        vb=dict(c['vinculo'],base_hash=hash_json(adulterado))
        contraprovas.append(rejeitar(lambda:montar_views(adulterado,ev,c['fontes'],e,vinculo=vb),'baseline divergente '+c['caso_id']))
        outro=deepcopy(ev);outro['relato']='Texto sem fonte vigente'
        contraprovas.append(rejeitar(lambda:normalizar(b,c['fontes'],e,outro),'aviso sem vínculo literal '+c['caso_id']))
    manifesto=dict(schema_version='4.2-manifesto-h07',uso='final',condicoes=['B','H','T'],execucoes=slots)
    validar_manifesto(manifesto)
    destino=OUT/'preparacao_final';destino.mkdir(exist_ok=True)
    for nome,obj in [('manifesto.json',manifesto),('views.json',{c['caso_id']:c['views'] for c in casos}),('contextos_iniciais.json',contextos)]:
        (destino/nome).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    verificacao=dict(estado='preparado_offline_sem_execucao_preditiva',slots=len(slots),casos=len(casos),contextos=len(contextos),
        arquivos_lidos_pelo_carregador=hashes,referencias_lidas_pelo_carregador=[],codigo_preservado=True,
        equivalencias=[dict(caso_id=c['caso_id'],**c['equivalencia']) for c in casos],contraprovas_rejeitadas=contraprovas,
        nenhuma_chamada=True,nenhuma_previsao=True,modelo=MODELO,configuracao=CONFIG,
        limite='Contextos iniciais conferidos; contextos com resultados predecessores só existem na coleta. Tokens oficiais serão contados antes de envio autorizado.')
    (destino/'validacao.json').write_text(json.dumps(verificacao,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in verificacao.items() if k not in ['equivalencias','arquivos_lidos_pelo_carregador']},ensure_ascii=False))


if __name__=='__main__':main()
