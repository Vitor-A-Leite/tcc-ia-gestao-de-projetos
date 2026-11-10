"""Política Alfa v1: cobertura explícita de 32 pontos, custódia monetária única.

Reutiliza contexto, validador, catálogo de responsáveis, reconciliação e fechamento
H 7.2. Aceite é operacional condicional, nunca aprovação humana/semântica.
"""
from copy import deepcopy
import re
from orquestracao import Politica
from hibrido_v07_r3.contratos import validar, hash_json
from hibrido_v07_r3.escopo import catalogar
from hibrido_v07_r3.fechamento import fechar
from hibrido_v07_r3.politica import POLITICA, _refs


def construir(estado, evento, grafo, execucao_id, max_analises=None):
    ents={n['id']:n for n in estado['entidades']}
    kinds={n['id']:n['type'] for n in grafo['nodes']}
    owners={p['id']:p['proprietario'] for p in grafo['parcelas']}
    literal=set(re.findall(r'\bp_[0-9a-f]+\b',evento['relato']))
    # Obrigações novas exigem cadastro anterior à execução. Não inventar custódia.
    if not literal<=owners.keys(): raise ValueError('Obrigação sem proprietário cadastrado')
    temporal={r['parcela_id'] for r in estado['regras_custo']}
    plano={}
    for n in sorted(ents):
        rels=[r for r in estado['relacoes'] if n in (r['origem_id'],r['destino_id'])]
        regras=[r for r in estado['regras_locais'] if r['no_id']==n]
        regras += [r for r in estado['regras_custo'] if r['intervalo']['fim_ref']['atividade_id']==n]
        atividades=[a for a in estado['atividades'] if a['id']==n]
        parcelas=[p for p in estado['parcelas_base'] if owners[p['id']]==n and p['id'] not in temporal]
        ids=set(_refs([ents[n],rels,regras,atividades,parcelas])) | {f['id'] for f in evento['evidencias']}
        plano[n]=dict(fonte_ids=sorted(ids),relacao_ids=[r['id'] for r in rels],regra_ids=[r['id'] for r in regras],obrigacoes=[],parcela_ids=[p['id'] for p in parcelas],
                      predicados=['aplicabilidade_'+r['id'] for r in regras if 'no_id' in r]+['aditivo_explicito_'+r['id'] for r in regras if 'parcela_id' in r])
    vistos, propostas, encaminhamentos, pendencias, decisoes = set(), [], [], [], []
    def operacional(c,a):
        validar(a,c)
        motivos=[]
        if c['responsabilidades_operacionais']!=responsabilidades_para_no(c['no_id']): motivos.append('Responsabilidades divergentes')
        for p in a['propostas']:
            if any(x['estado']!='confirmada' for x in p['condicoes']): motivos.append('Condição não confirmada')
            if p['operacao']=='substituir_duracao' and kinds[p['no_id']] not in ('Task','Test'):
                motivos.append('Ponto de disponibilidade não é atividade com duração editável')
            if p['operacao']=='substituir_parcela' and owners.get(p['alvo_id'])!=c['no_id']:
                motivos.append('Parcela pertence a outro responsável')
        if not motivos:
            vistos.add(c['no_id']);propostas.extend(deepcopy(a['propostas']))
            pendencias.extend(dict(no_id=c['no_id'],**deepcopy(x)) for x in a['pendencias_operacionais'])
            encaminhamentos.extend(dict(no_origem=c['no_id'],analise_id=a['analise_id'],contexto_hash=c['contexto_hash'],encaminhamento=deepcopy(x)) for x in a['encaminhamentos'])
        decisoes.append(dict(no_id=c['no_id'],analise_id=a['analise_id'],operacao_estrutural='rejeitada' if motivos else 'permitida_condicional',motivos=motivos or ['Validação estrutural; suporte semântico não auditado'],suporte_semantico='nao_auditado'))
        return not motivos
    p=Politica(execucao_id=execucao_id,alvos=sorted(ents),plano=plano,origem='ALFA-1.0.0/H7.2',fechamento=True,resolver=operacional,versao=POLITICA,
               max_analises=len(plano) if max_analises is None else max_analises,max_chamadas=len(plano),max_tempo_s=len(plano)*180+60)
    responsabilidades=catalogar(estado,evento,p)
    p.responsabilidades_operacionais=deepcopy(responsabilidades)
    def responsabilidades_para_no(n):
        # Seleção por semântica do modelo, nunca por quantidade/token budget.
        # Todos os responsáveis ainda serão consultados na passagem global.
        alvos={n}|set(evento['entidades_mencionadas'])|{owners[x] for x in literal}
        for r in estado['relacoes']:
            if n in (r['origem_id'],r['destino_id']):
                alvos.update((r['origem_id'],r['destino_id']))
        return deepcopy([r for r in responsabilidades if r['no_id'] in alvos])
    p.responsabilidades_para_no=responsabilidades_para_no
    digest=hash_json([estado,evento,p.plano,p.alvos])
    def iniciar(e,ev):
        if digest!=hash_json([e,ev,p.plano,p.alvos]): raise ValueError('Política de outro snapshot')
        vistos.clear();propostas.clear();encaminhamentos.clear();pendencias.clear();decisoes.clear()
    def fechamento():
        f=fechar(nos=plano,vistos=vistos,regras=estado['regras_locais'],novos=[],propostas=propostas,encaminhamentos=encaminhamentos,pendencias_tipadas=pendencias,evento_id=evento['evento_id'])
        p.registro_operacional['fechamento_final']=f
        return f['pendencias']
    p.iniciar_passagem=iniciar;p.verificar_fechamento=fechamento;p.modo_condicional=True
    p.registro_operacional=dict(versao='ALFA-1.0.0',selecionados=sorted(plano),cobertura_alvo='todos_os_32_pontos_executaveis',decisoes=decisoes,
                               responsabilidades_operacionais=responsabilidades,regras_locais=estado['regras_locais'],suporte_semantico='nao_auditado',
                               custodia=owners,limites=dict(analises=p.max_analises,chamadas=p.max_chamadas,segundos=p.max_tempo_s))
    return p
