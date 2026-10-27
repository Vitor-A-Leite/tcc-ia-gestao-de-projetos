"""Contrato H v05, opt-in; não altera os contratos históricos."""
from copy import deepcopy
from interpretacao_no.contratos import (ContratoInvalido,exigir,campos,texto,numero,lista,strings,refs,selecionar,conhecimento,hash_json,OPS,montar_contexto as contexto_v1)
VERSAO='5.0-h-local-escopado'
SCHEMA='2.0-analise-local'

def escopos(c):
    return [dict(regra_id=r['id'],no_id=r['no_id'],predicado='aplicabilidade_'+r['id'],obrigacao_lacuna_id='lacuna_'+hash_json([c['evento_id'],r['id'],'readequacao'])[:16] if 'readequacao'in r['atributos_alvo'] else None) for r in c['regras'] if 'no_id'in r]

def montar_contexto(*args,**kwargs):
    c=contexto_v1(*args,**kwargs)
    c['schema_version']='2.0-contexto-no-local'
    c['escopos_regras']=escopos(c)
    c['contexto_hash']=hash_json({k:v for k,v in c.items() if k!='contexto_hash'})
    return c

def regra_confirmada(p,c):
    strings(p['regra_refs'])
    exigir(len(p['regra_refs'])==1,'Confirmação exige uma única regra de escopo')
    r=next((r for r in c['regras'] if r['id']==p['regra_refs'][0] and r.get('no_id')==p['alvo_id']),None)
    exigir(r is not None and p['operacao']in r.get('operacoes_permitidas',[]) and p['atributo']in r.get('atributos_alvo',[]),'Confirmação fora do escopo da cláusula')
    exigir(r['clausula']in p['evidencias'],'Confirmação sem referência à cláusula específica')
    pred='aplicabilidade_'+r['id']
    exigir(any(x['predicado']==pred and x['estado']=='confirmada' for x in p['condicoes']),'Condição não vinculada à regra confirmada')
    return r

def verificar_contradicoes(propostas,regras,parcelas,evento_id):
    locais={r['id']:r for r in regras if 'no_id'in r}
    ausencias={p['regra_refs'][0] for p in propostas if p['operacao']=='confirmar_ausencia_parcela_adicional' and len(p['regra_refs'])==1}
    manutencoes={p['alvo_id'] for p in propostas if p['operacao']=='confirmar_manutencao_atributo'}
    base={p['id']:p['valor_centavos'] for p in parcelas}
    for p in propostas:
        op=p['operacao']
        exigir(not(op=='substituir_duracao' and p['alvo_id']in manutencoes),'Manutenção e substituição concorrentes de duração')
        if op not in ('adicionar_parcela','substituir_parcela','registrar_lacuna_custo'):continue
        ligadas=set(p['regra_refs'])&set(locais)
        for rid in locais:
            ob='lacuna_'+hash_json([evento_id,rid,'readequacao'])[:16]
            if p['alvo_id']==ob:
                exigir(rid in p['regra_refs'],'Lacuna de cláusula sem regra correspondente')
                ligadas.add(rid)
        valor=p['valor']
        zero=valor.get('estado')=='exato' and valor.get('valor')==(base.get(p['alvo_id']) if op=='substituir_parcela'else 0)
        exigir(not(ligadas&ausencias)or zero,'Ausência e efeito monetário contraditórios na mesma cláusula')


def validar(a, c):
    """Estrutura/proveniência apenas. Todas as propostas requerem revisão semântica."""
    exigir(c.get('schema_version')=='2.0-contexto-no-local' and c.get('escopos_regras')==escopos(c),'Contexto v05 obrigatório')
    exigir(c['contexto_hash'] == hash_json({k: v for k, v in c.items() if k != 'contexto_hash'}), 'Contexto adulterado')
    campos(a, 'schema_version analise_id execucao_id evento_id no_id revisao contexto_hash predecessores_versoes avaliacao propostas justificativa lacunas pendencias_operacionais')
    exigir(a['schema_version'] == SCHEMA, 'Versão de análise inválida')
    texto(a['analise_id'])
    for k in ('execucao_id', 'evento_id', 'no_id', 'revisao', 'contexto_hash', 'predecessores_versoes'):
        exigir(a[k] == c[k] and type(a[k]) is type(c[k]), 'Identidade/revisão divergente: ' + k)
    exigir(isinstance(a['predecessores_versoes'], dict), 'Mapa de revisões obrigatório')
    for revisao in a['predecessores_versoes'].values():
        numero(revisao, 1)
    campos(a['avaliacao'], 'prazo custo')
    for v in a['avaliacao'].values():
        conhecimento(v, c)
    exigir(isinstance(a['justificativa'],str) and bool(a['justificativa'].strip()),'justificativa deve ser string não vazia; array não é aceito')
    strings(a['pendencias_operacionais'])
    strings(a['lacunas'])
    lista(a['propostas'])
    ids, escritas, decisoes = set(), set(), []
    for p in a['propostas']:
        campos(p, 'id operacao alvo_id atributo valor unidade evidencias relacao_refs regra_refs condicoes origens_causais no_id')
        texto(p['id'])
        exigir(p['id'] not in ids, 'Proposta duplicada')
        ids.add(p['id'])
        exigir(p['no_id'] == c['no_id'], 'Proposta de outro nó')
        d = selecionar(p, 'operacao alvo_id atributo unidade')
        exigir(d in c['permissoes'], 'Operação/alvo/unidade fora de catálogo: requer_revisao')
        chave = (p['alvo_id'], p['atributo'], tuple(p['regra_refs']) if p['operacao'].startswith('confirmar_') else None)
        exigir(chave not in escritas, 'Escritas conflitantes')
        escritas.add(chave)
        refs(p['evidencias'], c)
        for k, catalogo in (('regra_refs', c['regras']), ('relacao_refs', c['relacoes'])):
            strings(p[k])
            exigir(set(p[k]) <= {x['id'] for x in catalogo}, 'Referência de catálogo invisível')
        lista(p['condicoes'])
        for cond in p['condicoes']:
            campos(cond, 'predicado estado evidencias')
            exigir(cond['predicado'] in c['predicados'] and cond['estado'] in ('confirmada', 'nao_confirmada', 'indeterminada'), 'Condição fora de catálogo')
            refs(cond['evidencias'], c)
        lista(p['origens_causais'])
        exigir(p['origens_causais'], 'Origem obrigatória')
        canonico = hash_json([c['evento_id'], p['alvo_id']])
        for o in p['origens_causais']:
            campos(o, 'evento_id fato_ref efeito_id')
            exigir(o['evento_id'] == c['evento_id'] and o['efeito_id'] == canonico, 'Origem/efeito não canônico')
            refs([o['fato_ref']], c)
            exigir(o['fato_ref'] in p['evidencias'], 'Origem sem evidência da proposta')
        op = p['operacao']
        if op.startswith('confirmar_'):
            regra_confirmada(p,c)
            regras = [r for r in c['regras'] if r['id'] in p['regra_refs'] and r.get('no_id') == c['no_id'] and op in r.get('operacoes_permitidas', []) and p['atributo'] in r.get('atributos_alvo', [])]
            exigir(regras and p['condicoes'] and all(x['estado'] == 'confirmada' for x in p['condicoes']), 'Confirmação sem condição/regra resolvida')
            numero(p['valor'], 0)
            esperado = 0 if op == 'confirmar_ausencia_parcela_adicional' else c['no']['atributos']['duracao']['valor']
            exigir(p['valor'] == esperado, 'Confirmação divergente')
            # Zero refere-se somente à regra explicitamente identificada, não ao total do nó.
        elif op == 'aplicar_regra_catalogada':
            exigir(p['alvo_id'] in p['regra_refs'], 'Aditivo sem regra')
            v = p['valor']
            exigir(isinstance(v, dict) and v and set(v) <= {'taxa_centavos_dia', 'base_contratada_dias', 'politica_reducao'}, 'Aditivo fora de catálogo')
            for k, x in v.items():
                if k == 'politica_reducao':
                    exigir(x in ('sem_credito', 'recalculavel_com_credito'), 'Política inválida')
                elif k != 'taxa_centavos_dia' or x is not None:
                    numero(x, 0)
        else:
            conhecimento(p['valor'], c, absoluto=True, minimo=0)
            exigir(p['valor']['estado'] != 'inaplicavel', 'Atributo quantitativo obrigatório')
            if op == 'registrar_lacuna_custo':
                exigir(p['valor']['estado'] != 'exato', 'Lacuna não é preço exato')
        decisoes.append(dict(proposta_id=p['id'], status='requer_revisao',
                             efeito_id=canonico, estrutura='valida', suporte_semantico='nao_auditado',
                             motivos=['Citação visível não prova suporte semântico; nenhuma aplicação autorizada']))
    verificar_contradicoes(a['propostas'],c['regras'],c['parcelas'],c['evento_id'])
    return deepcopy(decisoes)
