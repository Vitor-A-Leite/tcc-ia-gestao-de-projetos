"""Política operacional condicional: não interpreta suporte nem lê referências."""
from copy import deepcopy
import re
from .contratos import validar,hash_json
from orquestracao import Politica
POLITICA='5.0-politica-h-escopada'


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
    def operacional(c,a):
        validar(a,c)
        motivos=list(a['pendencias_operacionais'])
        for p in a['propostas']:
            if any(x['estado']!='confirmada' for x in p['condicoes']):motivos.append('Condição não confirmada pela interpretação')
            if p['alvo_id'] in sinteticas and p['operacao']!='registrar_lacuna_custo':motivos.append('Identificador de lacuna não autoriza cobrança exata')
            if p['operacao']=='adicionar_parcela' and p['alvo_id'] not in novos:motivos.append('Obrigação nova sem ID literal no aviso')
        if c['no_id']==custodio:
            cobertas={p['alvo_id'] for p in a['propostas'] if p['operacao'] in ('adicionar_parcela','registrar_lacuna_custo')}
            if not novos<=cobertas:motivos.append('Obrigação nova explícita não reconciliada')
        if not motivos:
            vistos.add(c['no_id']);propostas_aceitas.extend(deepcopy(a['propostas']))
        decisoes.append(dict(no_id=c['no_id'],analise_id=a['analise_id'],contexto_hash=c['contexto_hash'],
            operacao_estrutural='rejeitada' if motivos else 'permitida_condicional',suporte_semantico='nao_auditado',motivos=motivos or ['Schema, identidade, permissões e cobertura operacional; não é auditoria semântica']))
        return not motivos
    p=Politica(execucao_id=execucao_id,alvos=sorted(ents),plano=plano,origem=POLITICA,
               fechamento=True,resolver=operacional,versao=POLITICA,max_analises=8,max_chamadas=8,max_tempo_s=1500)
    def verificar_fechamento():
        pendencias=[]
        if vistos!=set(plano):pendencias.append('Cobertura operacional incompleta de nós: '+', '.join(sorted(set(plano)-vistos)))
        for regra in estado['regras_locais']:
            ps=[q for q in propostas_aceitas if q['no_id']==regra['no_id']]
            if 'duracao' in regra['atributos_alvo'] and not any(q['operacao'] in ('confirmar_manutencao_atributo','substituir_duracao') and q['alvo_id']==regra['no_id'] and regra['id']in q['regra_refs'] for q in ps):pendencias.append('Regra local de duração sem resolução operacional: '+regra['id'])
            if 'readequacao' in regra['atributos_alvo'] and not any((q['operacao']=='confirmar_ausencia_parcela_adicional' and q['regra_refs']==[regra['id']])or(q['operacao']=='registrar_lacuna_custo' and regra['id']in q['regra_refs'] and q['alvo_id']=='lacuna_'+hash_json([evento['evento_id'],regra['id'],'readequacao'])[:16])for q in ps):pendencias.append('Regra local de custo sem resolução operacional: '+regra['id'])
        cobertas={q['alvo_id'] for q in propostas_aceitas if q['operacao'] in ('adicionar_parcela','registrar_lacuna_custo')}
        if not novos<=cobertas:pendencias.append('Obrigação literal sem reconciliação final')
        p.registro_operacional['fechamento_final']=dict(estado='parcial' if pendencias else 'completo_operacional_condicional',nos_com_analise_operacional_valida=sorted(vistos),nos_exigidos=sorted(plano),obrigacoes_literais_novas_exigidas=sorted(novos),obrigacoes_reconciliadas=sorted(novos&cobertas),pendencias=list(pendencias),suporte_semantico='nao_auditado')
        return pendencias
    p.verificar_fechamento=verificar_fechamento
    p.modo_condicional=True
    p.registro_operacional=dict(versao=POLITICA,selecionados=sorted(ents),cobertura_alvo='todos_os_nos_e_catalogos',
        custodia=dict(no_id=custodio,criterio='primeiro_ID_mencionado_preferindo_entidade_quantitativa;custodia_tecnica_nao_causal',obrigacoes_literais=sorted(literal),lacunas_catalogadas=sorted(sinteticas)),
        suporte_semantico='nao_auditado',decisoes=decisoes)
    return p
