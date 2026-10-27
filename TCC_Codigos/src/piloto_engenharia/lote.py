"""Lote com slots anteriores à execução e falhas preservadas; sem avaliação."""
from copy import deepcopy
from collections import Counter
import hashlib
import json
from pathlib import Path
from . import executar_prescrito, contraprovas, inventario_codigo, ROTULO, SLOTS_CONTRAPROVAS


def gravar(path, obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def ler_vinculado(path):
    bruto=path.read_bytes()
    return json.loads(bruto),dict(path=str(path.resolve()),sha256=hashlib.sha256(bruto).hexdigest())


def descobrir_slots(dados):
    """Descobre todos os catálogos antes de ler fixtures ou executar qualquer caso."""
    dados=Path(dados)
    slots=[]
    for novo in (False,True):
        raiz=dados/('ampliacao_v1' if novo else 'projeto_minimo_v1')
        obj,hash_catalogo=ler_vinculado(raiz/'inputs/cenarios.json')
        casos=obj['casos']
        if not isinstance(casos,list) or not casos: raise ValueError('Catálogo vazio/inválido')
        estado=raiz/'inputs/estado_projeto.json' if novo else dados/'projeto_minimo_grafo_v1/estado_projeto.json'
        for ev in casos:
            cid=ev['caso_id']
            if not isinstance(cid,str) or not cid.startswith('k_') or not cid[2:].isalnum(): raise ValueError('ID de caso inválido')
            for campo in ('evento_id','projeto_id','versao_projeto'):
                if not isinstance(ev[campo],str) or not ev[campo]: raise ValueError('Identidade ausente no catálogo')
            fixture=(raiz/'fixtures_prescritas' if novo else dados/'orquestracao_simulada_v1')/(cid+'.json')
            slots.append(dict(slot_id='etapa9-'+cid+'-H-1',caso_id=cid,evento_id=ev['evento_id'],projeto_id=ev['projeto_id'],
                repeticao=1,condicao='H',origem='simulado',rotulo=ROTULO,evento_comum=deepcopy(ev),
                arquivos=dict(base=raiz/'inputs/base.json',fontes=raiz/'inputs/fontes.json',estado=estado,fixture=fixture),
                catalogo=hash_catalogo,versao_catalogo=obj['versao'],versao_projeto_comum=ev['versao_projeto']))
    if len({s['slot_id'] for s in slots})!=len(slots): raise ValueError('Slots duplicados')
    return slots


def carregar_slot(slot):
    objetos={};arquivos={}
    # Cada arquivo é lido uma vez: hash e JSON correspondem aos mesmos bytes.
    for nome,path in slot['arquivos'].items():
        try:
            bruto=path.read_bytes()
        except OSError as exc:
            arquivos[nome]=dict(path=str(path.resolve()),sha256=None,erro=str(exc))
            continue
        arquivos[nome]=dict(path=str(path.resolve()),sha256=hashlib.sha256(bruto).hexdigest())
        try: objetos[nome]=json.loads(bruto)
        except (ValueError,UnicodeError) as exc: arquivos[nome]['erro']=str(exc)
    return objetos,arquivos


def executar_lote(dados,saida,*,executor=executar_prescrito):
    saida=Path(saida);saida.mkdir(parents=True,exist_ok=False)
    try: slots=descobrir_slots(dados)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        gravar(saida/'erro_lote.json',dict(estado='erro',codigo='CATALOGO_INDISPONIVEL',mensagem=str(exc),
            N_planejado=None,rotulo=ROTULO,motivo='Não foi possível descobrir o plano integral; nenhuma execução iniciada'))
        raise ValueError('Falha de catálogo; consulte erro_lote.json') from exc
    codigo=inventario_codigo()
    plano=[{k:v for k,v in s.items() if k not in ('evento_comum','arquivos')} | {'arquivos':{k:str(p.resolve()) for k,p in s['arquivos'].items()}} for s in slots]
    gravar(saida/'plano_slots.json',dict(versao='1.0-engenharia',N_H=len(plano),N_B_executados=0,N_T_executados=0,
        rotulo=ROTULO,hashes_codigo=codigo,slots=plano))
    gravar(saida/'plano_contraprovas.json',dict(N=12,rotulo=ROTULO,slots=SLOTS_CONTRAPROVAS))
    normais=[];falhas=None;views_geradas=0
    for s in slots:
        objetos,hashes=carregar_slot(s)
        proveniencia=dict(slot_id=s['slot_id'],caso_id=s['caso_id'],evento_id=s['evento_id'],
            projeto_id=s['projeto_id'],condicao='H',repeticao=1,origem='simulado',
            catalogo=s['catalogo'],versao_catalogo=s['versao_catalogo'],hashes_arquivos=hashes,
            versao_projeto_comum=s['versao_projeto_comum'],versao_snapshot=objetos['estado'].get('versao') if isinstance(objetos.get('estado'),dict) else None,
            hashes_codigo=codigo)
        pacote=None
        try:
            if len(objetos)!=4: raise ValueError('Input/fixture ausente ou JSON inválido: '+', '.join(k for k in s['arquivos'] if k not in objetos))
            b,fs,e,f=objetos['base'],objetos['fontes']['fontes'],objetos['estado'],objetos['fixture']
            pacote=executor(b,fs,e,s['evento_comum'],f)
            r=pacote['H']
            if r['execucao']['estado'] not in ('ok','parcial','erro'): raise ValueError('Envelope operacional inválido')
            views_geradas+=len(pacote['views'])
        except Exception as exc:
            # Exceção inesperada é registro do slot, nunca exclusão/zero. KeyboardInterrupt/SystemExit passam.
            r=dict(execucao_id=s['slot_id'],projeto_id=s['projeto_id'],evento_id=s['evento_id'],condicao='H',
                execucao=dict(estado='erro',origem='simulado',erros=[dict(codigo='SLOT_INDISPONIVEL',tipo=type(exc).__name__,mensagem=str(exc))]),
                consumo=dict(chamadas=None,analises=None),motivo_quantidades_ausentes='Execução não entregou ResultadoFinal')
            pacote=dict(rotulo=ROTULO,H=r,B=dict(estado='sem_execucao'),T=dict(estado='sem_execucao'))
        if s['caso_id']=='k_98f3' and 'views' in pacote:
            try: falhas=contraprovas(e,f,pacote['views'])
            except Exception as exc:
                gravar(saida/'erro_preparacao_contraprovas.json',dict(tipo=type(exc).__name__,mensagem=str(exc)))
        pacote['proveniencia_slot']=proveniencia
        gravar(saida/(s['caso_id']+'.json'),pacote)
        consumo=r.get('consumo',{})
        normais.append(dict(slot_id=s['slot_id'],caso_id=s['caso_id'],projeto_id=s['projeto_id'],
            execucao=r['execucao'],delta_dias=r.get('delta_dias'),delta_centavos=r.get('delta_centavos'),
            motivo_quantidades_ausentes=r.get('motivo_quantidades_ausentes'),
            analises=consumo.get('analises'),chamadas_api=consumo.get('chamadas')))
    if falhas is None:
        # Contraprovas também não desaparecem se seu caso de suporte não puder ser lido.
        falhas=[dict(id=i,condicao=c,origem=ROTULO,categoria='preparacao',limitacao_conhecida=i=='resolver_permissivo',
            resultado=dict(execucao=dict(estado='erro',erros=[dict(codigo='CONTRAPROVA_NAO_EXECUTADA',mensagem='Caso de suporte indisponível')]))) for c,i in [(s['condicao'],s['id']) for s in SLOTS_CONTRAPROVAS]]
    gravar(saida/'contraprovas.json',falhas)
    denominadores={c:dict(N=sum(x['condicao']==c for x in falhas),estados=dict(Counter(x['resultado']['execucao']['estado'] for x in falhas if x['condicao']==c))) for c in 'BHT'}
    resumo=dict(rotulo=ROTULO,uso='piloto_engenharia_desenvolvimento',piloto_cientifico_concluido=False,
        normais=dict(N_H=len(slots),N_B_executados=0,N_T_executados=0,views_geradas=views_geradas,
            estados_H=dict(Counter(x['execucao']['estado'] for x in normais)),registros=normais),
        contraprovas=dict(N=len(falhas),por_condicao=denominadores,limitacoes_conhecidas=sum(x['limitacao_conhecida'] for x in falhas)),
        chamadas_api_reais=0,hashes_codigo=codigo)
    gravar(saida/'resumo.json',resumo)
    return resumo
