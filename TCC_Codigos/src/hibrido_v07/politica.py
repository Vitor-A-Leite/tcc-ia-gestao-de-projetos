"""Política operacional condicional: não interpreta suporte nem lê referências."""
from copy import deepcopy
import re
from .contratos import validar,hash_json
from orquestracao import Politica
from .escopo import catalogar
from .fechamento import fechar
POLITICA='7.0-politica-h-dimensoes'


def normalizar(base,fontes,estado,ev):
    if ev['projeto_id']!=base['projeto_id'] or ev['versao_projeto']!=base['versao_projeto'] or estado['projeto_id']!=base['projeto_id'] or type(ev['instante_observacao'])is not int or ev['instante_observacao']!=0:raise ValueError('Evento/snapshot/D0 incompatíveis')
    ent={n['id']:n for n in estado['entidades']}
    mencionadas=ev['entidades_mencionadas']
    if not mencionadas or len(set(mencionadas))!=len(mencionadas) or not set(mencionadas)<=ent.keys():raise ValueError('Menções ausentes/ambíguas')
    atuais=[f for f in fontes if f['id'] in ev['evidencia_ids']]
    if len(atuais)!=len(ev['evidencia_ids']) or any(f['documento_id']!=ev['documento_evento_vigente'] for f in atuais):raise ValueError('Evidências atuais inválidas')
    if ev['relato'] not in [f['trecho'] for f in atuais]:raise ValueError('Relato não vinculado literalmente ao aviso')
    e={k:deepcopy(ev[k]) for k in ('evento_id','projeto_id','instante_observacao','relato','origem','entidades_mencionadas','escopo','lacunas')}
    e.update(versao_projeto=estado['versao'],evidencias=deepcopy(atuais))
    return e


def _refs(x):
    if isinstance(x,dict):
        if 'fonte_id' in x:yield x['fonte_id']
        for v in x.values():yield from _refs(v)
    elif isinstance(x,list):
        for v in x:yield from _refs(v)


def construir(estado,evento,*,execucao_id):
    """Todos os nós interpretados, no máximo8. Custódia monetária técnica explícita.

    Custódia é desempate de serialização, não propriedade econômica inferida nem
    identificação causal semântica. Origem substantiva permanece alegação do modelo.
    """
    estado, evento = deepcopy(estado), deepcopy(evento)
    ents={n['id']:n for n in estado['entidades']}
    if len(ents)>8:raise ValueError('Projeto excede o limite aprovado de8 análises')
    literal=set(re.findall(r'\bp_[0-9a-f]+\b',evento['relato']))
    baseids={p['id'] for p in estado['parcelas_base']}
    novos=literal-baseids;existentes=literal&baseids
    mencionados=evento['entidades_mencionadas']
    custodio=sorted(mencionados,key=lambda n:(ents[n]['tipo'] not in ('atividade','componente','marco'),n))[0]
    temporal={r['parcela_id'] for r in estado['regras_custo']}
    fontes_evento=[f['id'] for f in evento['evidencias']]
    plano={};sinteticas=set()
    for n in sorted(ents):
        rels=[r for r in estado['relacoes'] if n in (r['origem_id'],r['destino_id'])]
        regras=[r for r in estado['regras_locais'] if r['no_id']==n]
        regras += [t for t in estado['regras_transferencia'] if any(r['id']==t['relacao_id'] and r['destino_id']==n for r in rels)]
        regras += [r for r in estado['regras_custo'] if isinstance(r['intervalo']['fim_ref'],dict) and r['intervalo']['fim_ref']['atividade_id']==n]
        locais=[r for r in estado['regras_locais'] if r['no_id']==n]
        # Identificador de lacuna da cláusula, não obrigação comercial inventada pelo LLM.
        lacunas=['lacuna_'+hash_json([evento['evento_id'],r['id'],'readequacao'])[:16] for r in locais if 'readequacao' in r['atributos_alvo']]
        sinteticas.update(lacunas)
        fonteids=set(_refs([ents[n],rels,regras]))|set(fontes_evento)
        # Contratos/fontes comuns em todos os contextos; ficha relacional só incidente.
        fonteids|={f['id'] for f in estado['fontes'] if f['documento_id'] not in {ff['documento_id'] for rr in estado['relacoes'] for ff in estado['fontes'] if ff['id'] in set(_refs(rr))}}
        for a in estado['atividades']:
            if a['id']==n:fonteids.update(_refs(a))
        parcelas=sorted((existentes-temporal) if n==custodio else ())
        plano[n]=dict(fonte_ids=sorted(fonteids),relacao_ids=[r['id'] for r in rels],regra_ids=[r['id'] for r in regras],
                      obrigacoes=sorted(novos) + lacunas if n==custodio else lacunas,parcela_ids=parcelas,
                      predicados=['aplicabilidade_'+r['id'] for r in locais]+['aditivo_explicito_'+r['id'] for r in regras if 'parcela_id' in r])
    decisoes=[]
    vistos=set()
    propostas_aceitas=[]
    encaminhamentos=[]
    pendencias_tipadas=[]
    def operacional(c,a):
        validar(a,c)
        if c['responsabilidades_operacionais'] != responsabilidades:
            raise ValueError('Catálogo de responsabilidades divergente da política')
        motivos=[x['motivo'] for x in a['pendencias_operacionais'] if x['dimensao'] != 'custo']
        for p in a['propostas']:
            if any(x['estado']!='confirmada' for x in p['condicoes']):motivos.append('Condição não confirmada pela interpretação')
            if p['alvo_id'] in sinteticas and p['operacao']!='registrar_lacuna_custo':motivos.append('Identificador de lacuna não autoriza cobrança exata')
            if p['operacao']=='adicionar_parcela' and p['alvo_id'] not in novos:motivos.append('Obrigação nova sem ID literal no aviso')
        if not motivos:
            vistos.add(c['no_id']);propostas_aceitas.extend(deepcopy(a['propostas']))
            pendencias_tipadas.extend(dict(no_id=c['no_id'], **deepcopy(x)) for x in a['pendencias_operacionais'])
            encaminhamentos.extend(dict(
                no_origem=c['no_id'], analise_id=a['analise_id'], contexto_hash=c['contexto_hash'],
                encaminhamento=deepcopy(pedido),
            ) for pedido in a['encaminhamentos'])
        decisoes.append(dict(no_id=c['no_id'],analise_id=a['analise_id'],contexto_hash=c['contexto_hash'],
            operacao_estrutural='rejeitada' if motivos else 'permitida_condicional',suporte_semantico='nao_auditado',motivos=motivos or ['Schema, identidade, permissões e cobertura operacional; não é auditoria semântica']))
        return not motivos
    p=Politica(execucao_id=execucao_id,alvos=sorted(ents),plano=plano,origem=POLITICA,
               fechamento=True,resolver=operacional,versao=POLITICA,max_analises=8,max_chamadas=8,max_tempo_s=1500)
    responsabilidades = catalogar(estado, evento, p)
    p.responsabilidades_operacionais = deepcopy(responsabilidades)
    vinculo = hash_json([estado, evento, p.plano, p.alvos, p.dispensas, p.execucao_id])
    def iniciar_passagem(e, ev):
        if hash_json([e, ev, p.plano, p.alvos, p.dispensas, p.execucao_id]) != vinculo:
            raise ValueError('Política vinculada a outro snapshot/evento/plano')
        if p.responsabilidades_operacionais != responsabilidades:
            raise ValueError('Catálogo de responsabilidades adulterado')
        # O cache pode ser revalidado; decisões/fechamento pertencem só à passagem atual.
        vistos.clear()
        propostas_aceitas.clear()
        encaminhamentos.clear()
        pendencias_tipadas.clear()
        decisoes.clear()
        p.registro_operacional.pop('fechamento_final', None)
    p.iniciar_passagem = iniciar_passagem
    def verificar_fechamento():
        fechamento = fechar(nos=plano, vistos=vistos, regras=estado['regras_locais'], novos=novos,
                            propostas=propostas_aceitas, encaminhamentos=encaminhamentos,
                            pendencias_tipadas=pendencias_tipadas, evento_id=evento['evento_id'])
        p.registro_operacional['fechamento_final'] = fechamento
        return fechamento['pendencias']
    p.verificar_fechamento=verificar_fechamento
    p.modo_condicional=True
    p.registro_operacional=dict(versao=POLITICA,selecionados=sorted(ents),cobertura_alvo='todos_os_nos_e_catalogos',
        custodia=dict(no_id=custodio,criterio='primeiro_ID_mencionado_preferindo_entidade_quantitativa;custodia_tecnica_nao_causal',obrigacoes_literais=sorted(literal),lacunas_catalogadas=sorted(sinteticas)),
        suporte_semantico='nao_auditado',decisoes=decisoes)
    p.registro_operacional['regras_locais'] = deepcopy(estado['regras_locais'])
    p.registro_operacional['responsabilidades_operacionais'] = deepcopy(responsabilidades)
    return p
