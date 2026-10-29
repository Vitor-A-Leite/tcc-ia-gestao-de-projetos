"""JSON Schema prospectivo derivado de permissões/fontes, sem gabaritos.

A geração restrita reduz falhas formais; não prova condições nem valores.
O parser independente continua obrigatório e recusa incoerências entre campos.
"""
from copy import deepcopy
from .wire import WIRE
from .contratos import hash_json


def objeto(propriedades):
    return dict(type='object', properties=propriedades, required=list(propriedades), additionalProperties=False)


def enum(valores):
    return dict(type='string', enum=list(valores))


def array(item, minimo=0, maximo=None):
    d=dict(type='array', items=item, minItems=minimo)
    if maximo is not None:d['maxItems']=maximo
    return d


def alternativas(opcoes):
    return opcoes[0] if len(opcoes)==1 else dict(anyOf=opcoes)


def lista_catalogada(opcoes):
    return array(alternativas(opcoes)) if opcoes else array(dict(type='string'),maximo=0)


def gerar(c):
    if c['contexto_hash'] != hash_json({k:v for k,v in c.items() if k!='contexto_hash'}):
        raise ValueError('Contexto adulterado antes do schema')
    texto=dict(type='string',pattern=r'\S')
    nota=dict(type=['string','null'])
    ref={'$ref':'#/$defs/evidencia'}
    refs=lambda minimo=0:array(ref,minimo)
    strings=lambda minimo=0,maximo=None:array(texto,minimo,maximo)
    catalogo=lambda ids:array(enum(ids)) if ids else array(dict(type='string'),maximo=0)
    def conhecimento(absoluto=False, lacuna=False):
        escolhas=[]
        if not lacuna:
            inteiro=dict(type='integer')
            if absoluto:inteiro['minimum']=0
            escolhas.append(objeto(dict(estado=enum(['exato']),valor=inteiro,evidencias=refs(1),lacunas=strings(maximo=0),motivo=nota)))
        escolhas.append(objeto(dict(estado=enum(['indeterminado']),valor=dict(type='null'),evidencias=refs(),lacunas=strings(1),motivo=nota)))
        escolhas.append(objeto(dict(estado=enum(['direcao']),valor=dict(type='null'),evidencias=refs(1),lacunas=strings(1),motivo=nota,direcao=enum(['aumento','reducao']))))
        if not absoluto:
            escolhas.append(objeto(dict(estado=enum(['inaplicavel']),valor=dict(type='null'),evidencias=refs(),lacunas=strings(maximo=0),motivo=texto)))
        return alternativas(escolhas)
    predicados=c['predicados']
    condicao=objeto(dict(predicado=enum(predicados or ['sem_predicado']),estado=enum(['confirmada','nao_confirmada','indeterminada']),evidencias=refs(1)))
    condicoes=array({'$ref':'#/$defs/condicao'}, maximo=None if predicados else 0)
    propostas=[]
    for perm in c['permissoes']:
        op=perm['operacao']
        if op.startswith('confirmar_'):
            v=dict(type='integer',enum=[0 if op=='confirmar_ausencia_parcela_adicional' else c['no']['atributos']['duracao']['valor']])
        elif op=='alterar_parametros_contratuais':
            params=dict(taxa_centavos_dia=dict(type=['integer','null'],minimum=0),base_contratada_dias=dict(type='integer',minimum=0),politica_reducao=enum(['sem_credito','recalculavel_com_credito']))
            nomes=list(params)
            v=alternativas([objeto({nome:params[nome] for j,nome in enumerate(nomes) if mask&(1<<j)}) for mask in range(1,8)])
        else:v={'$ref':'#/$defs/'+('lacuna_absoluta' if op=='registrar_lacuna_custo' else 'absoluto')}
        props={k:enum([perm[k]]) for k in ('operacao','alvo_id','atributo')}
        props.update(valor=v,unidade=enum([perm['unidade']]),evidencias=refs(1),relacao_refs=catalogo([r['id'] for r in c['relacoes']]),regra_refs=catalogo([r['id'] for r in c['regras']]),condicoes=deepcopy(condicoes),origem_ref=ref)
        propostas.append(objeto(props))
    rotas=[]
    for rota in c['responsabilidades_operacionais']:
        if rota['no_id']==c['no_id'] or rota['operacao'].startswith('confirmar_'):continue
        rotas.append(objeto(dict(**{k:enum([v]) for k,v in rota.items()},motivo=texto,evidencias=refs(1))))
    locais=[r['regra_id'] for r in c['escopos_regras']]
    resolucoes=array(objeto(dict(regra_id=enum(locais or ['sem_clausula']),propostas_indices=array(dict(type='integer',minimum=1)))),len(locais),len(locais))
    raiz=objeto(dict(schema_version=enum([WIRE]),
                     propostas=lista_catalogada(propostas),justificativa=texto,lacunas=strings(),
                     pendencias_operacionais=array(objeto(dict(dimensao=enum(['prazo','custo','ambos']),motivo=texto,evidencias=refs(1)))),
                     encaminhamentos=lista_catalogada(rotas),resolucoes_regras=resolucoes))
    pares={(f['id'],f['localizador']) for f in c['fontes']}
    raiz['$defs']=dict(evidencia=alternativas([objeto(dict(fonte_id=enum([fid]),localizador=enum([loc]))) for fid,loc in sorted(pares)]),
                       absoluto=conhecimento(absoluto=True),lacuna_absoluta=conhecimento(absoluto=True,lacuna=True),condicao=condicao)
    return raiz


def formato(c):
    return dict(type='json_schema',name='analise_h07_r3',strict=True,schema=gerar(c))
