"""Motor H v05: matemática histórica reutilizada; confirmações por cláusula.

calcular/aplicar são fronteiras versionadas para não alterar globals do legado.
Não contém NLP, transportes, referências autorais ou escolha de valores.
"""
from copy import deepcopy
from time import perf_counter
from motor_deterministico.motor import (validar_estado,catalogo,referencias,preparar,cronograma,incidencia,resumo,nos_proposta)
from motor_deterministico.conhecimento import EntradaInvalida,Intervalo,exigir,inteiro,ler,maximo
from .contratos import verificar_contradicoes,ContratoInvalido

def aplicar(e, evento, propostas, politica):
    """Valida propostas de teste/revisadas; sem NLP ou decisão de cláusula textual."""
    atividades, entidades, restricoes, _, _ = validar_estado(e)
    fontes = catalogo(e['fontes'])
    for f in evento['evidencias']:
        exigir(f['id'] not in fontes or fontes[f['id']] == f, 'Fonte conflitante')
        fontes[f['id']] = f
    e['fontes'] = list(fontes.values())
    regras = catalogo(e['regras_custo'])
    locais = catalogo(e['regras_locais'])
    parcelas = catalogo(e['parcelas_base'])
    propostas = list(catalogo(propostas).values())
    try:
        verificar_contradicoes(propostas,e['regras_locais'],e['parcelas_base'],evento['evento_id'])
    except ContratoInvalido as err:
        raise EntradaInvalida(str(err)) from None
    decisoes, efeitos, ajustes, confirmacoes = [], {}, {}, set()
    alvos_escritos = set()
    for p in propostas:
        referencias(p['evidencias'], fontes)
        if isinstance(p['valor'], dict) and 'estado' in p['valor']:
            referencias(p['valor']['evidencias'], fontes)
            exigir(p['valor'].get('unidade', p['unidade']) == p['unidade'], 'Unidades divergentes')
        exigir(p['origens_causais'] and all(o['evento_id'] == evento['evento_id'] for o in p['origens_causais']), 'Origem causal inválida')
        for o in p['origens_causais']:
            referencias([o['fato_ref']], fontes)
        exigir(politica.get('autorizacoes', {}).get(p['id']) == resumo(p), 'Proposta requer_revisao: autorização ausente ou obsoleta')
        op, alvo, atributo = p['operacao'], p['alvo_id'], p['atributo']
        exigir(op in ('substituir_disponibilidade', 'substituir_duracao', 'substituir_restricao', 'adicionar_parcela', 'substituir_parcela', 'aplicar_regra_catalogada', 'confirmar_manutencao_atributo', 'confirmar_ausencia_parcela_adicional', 'registrar_lacuna_custo'), 'Operação requer_revisao: fora de catálogo')
        exigir(all(r in {x['id'] for x in e['relacoes']} for r in p['relacao_refs']), 'Relação inválida')
        exigir(all(r in set(regras) | set(locais) | {x['id'] for x in e['regras_transferencia']} for r in p['regra_refs']), 'Regra inválida')
        exigir(isinstance(p['condicoes'], list), 'Condições inválidas')
        for c in p['condicoes']:
            exigir(c.get('estado') == 'confirmada' and c.get('predicado') in politica.get('predicados', []), 'Condição requer revisão')
            referencias(c['evidencias'], fontes)
        chave = (alvo, atributo, tuple(p['regra_refs']) if op.startswith('confirmar_') else None)
        if op not in ('adicionar_parcela', 'registrar_lacuna_custo'):
            exigir(chave not in alvos_escritos, 'Escritas conflitantes')
            alvos_escritos.add(chave)
        if op in ('substituir_disponibilidade', 'substituir_duracao', 'substituir_restricao'):
            exigir(p['unidade'] == 'dia_corrido', 'Unidade temporal inválida')
            ler(p['valor'], 0)
            if op == 'substituir_disponibilidade':
                exigir(alvo in entidades and atributo == 'disponibilidade' and atributo in entidades[alvo]['atributos'], 'Disponibilidade sem alvo')
                entidades[alvo]['atributos'][atributo]['conhecimento'] = deepcopy(p['valor'])
            elif op == 'substituir_duracao':
                exigir(alvo in atividades and atributo == 'duracao' and alvo != e['marco_final_id'], 'Duração sem alvo')
                atividades[alvo]['duracao'] = deepcopy(p['valor'])
            else:
                exigir(alvo in restricoes and atributo == 'valor' and restricoes[alvo]['tipo'] == 'nao_antes', 'Restrição derivada somente via transferência')
                restricoes[alvo]['valor'] = deepcopy(p['valor'])
        elif op in ('adicionar_parcela', 'substituir_parcela', 'registrar_lacuna_custo'):
            exigir(p['unidade'] == 'BRL_centavo', 'Unidade monetária inválida')
            exigir(alvo not in {r['parcela_id'] for r in regras.values()}, 'Alteração direta/temporal requer reconciliação')
            exigir(p.get('no_id') in entidades, 'Efeito de custo sem nó de origem')
            valor = ler(p['valor'], 0)
            if op == 'substituir_parcela':
                exigir(alvo in parcelas, 'Parcela substituída inexistente')
                valor = valor.menos(parcelas[alvo]['valor_centavos'])
            else:
                exigir(alvo not in parcelas, 'Colisão com obrigação base')
            # Identidade canônica por evento + obrigação, não por caminho/nó/ID inventado de efeito.
            canonico = resumo([evento['evento_id'], alvo])
            registro = dict(no_id=p['no_id'], parcela_id=alvo, efeito_id=canonico, intervalo=valor,
                            fonte_refs=p['evidencias'], proposta_id=p['id'], origens_causais=p['origens_causais'])
            if alvo in efeitos:
                exigir(efeitos[alvo]['intervalo'] == valor and efeitos[alvo]['fonte_refs'] == p['evidencias'], 'Colisão de obrigação com conteúdo diferente')
            else:
                efeitos[alvo] = registro
        elif op == 'aplicar_regra_catalogada':
            exigir(alvo in regras and alvo in p['regra_refs'] and atributo == 'parametros_contratuais', 'Regra de custo inválida')
            exigir(p['unidade'] == 'contrato_temporal' and set(p['valor']) <= {'taxa_centavos_dia', 'base_contratada_dias', 'politica_reducao'}, 'Aditivo fora de escopo')
            ajuste = deepcopy(regras[alvo])
            ajuste.update(p['valor'])
            if ajuste['taxa_centavos_dia'] is not None:
                inteiro(ajuste['taxa_centavos_dia'], 0)
            inteiro(ajuste['base_contratada_dias'], 0)
            exigir(ajuste['politica_reducao'] in ('sem_credito', 'recalculavel_com_credito'), 'Política inválida')
            ajuste['fonte_refs'] = p['evidencias']
            ajustes[alvo] = ajuste
        else:
            exigir(p['regra_refs'] and p['condicoes'], 'Confirmação exige regra/condição')
            exigir(len(p['regra_refs'])==1,'Confirmação exige regra única')
            regra = next((locais[r] for r in p['regra_refs'] if r in locais), None)
            exigir(regra is not None and regra['no_id'] == alvo and op in regra['operacoes_permitidas'] and atributo in regra['atributos_alvo'], 'Confirmação fora do catálogo')
            if op == 'confirmar_manutencao_atributo':
                exigir(p['unidade'] == 'dia_corrido' and p['valor'] == atividades[alvo][atributo]['valor'], 'Manutenção divergente')
            else:
                exigir(p['unidade'] == 'BRL_centavo' and p['valor'] == 0, 'Ausência deve confirmar zero')
            exigir(regra['clausula']in p['evidencias'],'Confirmação sem cláusula específica')
            exigir(any(c['predicado']=='aplicabilidade_'+regra['id'] for c in p['condicoes']),'Condição de outra cláusula')
            confirmacoes.add((alvo,regra['id'],atributo))
        decisoes.append(dict(proposta_id=p['id'], status='aceita', motivos=['Estrutura e autorização conferidas; suporte semântico manual auditável']))
    # Aplica apenas projeções declaradas; preserva todas as outras restrições.
    relacoes = catalogo(e['relacoes'])
    alterados = {p['alvo_id'] for p in propostas if p['operacao'] == 'substituir_disponibilidade'}
    for t in e['regras_transferencia']:
        r = relacoes[t['relacao_id']]
        restricoes[t['restricao_destino_id']]['valor'] = deepcopy(entidades[r['destino_id']]['atributos']['disponibilidade']['conhecimento'])
    # Obrigações de interpretação locais devem estar explicitamente resolvidas pela entrada manual.
    # O chamador define requisitos revisados para o evento; ausência de resolução vira lacuna.
    for requisito in politica.get('requisitos_locais', []):
        alvo = requisito['no_id']
        regra = locais[requisito['regra_id']]
        exigir(regra['no_id'] == alvo, 'Requisito local inválido')
        if 'duracao' in regra['atributos_alvo'] and (alvo,regra['id'],'duracao') not in confirmacoes and not any(p['alvo_id'] == alvo and p['operacao'] == 'substituir_duracao' and regra['id']in p['regra_refs'] for p in propostas):
            raise EntradaInvalida('Condição local de duração não avaliada')
        if 'readequacao' in regra['atributos_alvo']:
            exigir((alvo,regra['id'],'readequacao') in confirmacoes or any(p['operacao']=='registrar_lacuna_custo' and p.get('no_id')==alvo and regra['id']in p['regra_refs'] and p['alvo_id']=='lacuna_'+resumo([evento['evento_id'],regra['id'],'readequacao'])[:16] for p in propostas), 'Condição local de custo não avaliada')
    # Alcançabilidade só seleciona cláusulas que precisam de resolução pelo chamador.
    # Não decide aplicabilidade semântica e não agenda interpretação.
    candidatos = set(alterados)
    arcos = [(r['origem_id'], r['destino_id']) for r in e['relacoes'] if r['tipo'] == 'precede_FS']
    arcos += [(relacoes[t['relacao_id']]['destino_id'], relacoes[t['relacao_id']]['origem_id']) for t in e['regras_transferencia']]
    while True:
        novos = {b for a, b in arcos if a in candidatos} - candidatos
        if not novos:
            break
        candidatos.update(novos)
    pertinentes = {r['id'] for r in locais.values() if r['no_id'] in candidatos}
    declarados = {r['regra_id'] for r in politica.get('requisitos_locais', [])}
    exigir(pertinentes <= declarados, 'Regras locais candidatas exigem resolução explícita')
    return decisoes, efeitos, ajustes


def calcular(estado, evento=None, propostas=(), politica=None, execucao_id='offline'):
    """ResultadoFinal e resultados_nos; erros nunca se tornam previsão de impacto zero.

    Propostas são o subconjunto aritmético de AnaliseNo; agenda e adaptador ficam futuros.
    """
    inicio_execucao = perf_counter()
    try:
        base, custo_base = preparar(estado)
        e = deepcopy(estado)
        politica = politica or {}
        decisoes, efeitos, ajustes = [], {}, {}
        evento_id = 'baseline'
        if evento is not None:
            inteiro(evento['instante_observacao'], 0)
            exigir(evento['projeto_id'] == e['projeto_id'] and evento['versao_projeto'] == e['versao'] and evento['instante_observacao'] == 0, 'Evento incompatível com snapshot')
            evento_id = evento['evento_id']
            decisoes, efeitos, ajustes = aplicar(e, evento, propostas, politica)
        else:
            exigir(not propostas, 'Propostas sem evento')
        datas = cronograma(e)
        livro = []
        total = Intervalo(custo_base, custo_base, tuple(e['linha_base']['custo_centavos']['evidencias']))
        parcial = custo_base
        for p in e['parcelas_base']:
            livro.append(dict(parcela_id=p['id'], base_centavos=p['valor_centavos'],
                              novo=Intervalo(p['valor_centavos'], p['valor_centavos'], tuple(p['fonte_refs'])).saida(),
                              delta=Intervalo(0, 0, tuple(p['fonte_refs'])).saida(True), fonte_refs=p['fonte_refs']))
        por_id = {p['parcela_id']: p for p in livro}
        for r in e['regras_custo']:
            ib = incidencia(r, base)
            nova_regra = ajustes.get(r['id'], r)
            inc = incidencia(nova_regra, datas)
            delta = inc.menos(ib.inferior)
            if nova_regra['politica_reducao'] == 'sem_credito':
                delta = maximo([Intervalo(0, 0), delta])
            total = total.somar(delta)
            if delta.inferior == delta.superior:
                parcial += delta.inferior
            item = por_id[r['parcela_id']]
            item.update(novo=delta.somar(Intervalo(item['base_centavos'], item['base_centavos'])).saida(),
                        delta=delta.saida(True), incidencia_base=ib.saida(), incidencia_nova=inc.saida(),
                        regra_id=r['id'], efeito_id=resumo([evento_id, r['parcela_id'], r['id']]), fonte_refs=nova_regra['fonte_refs'])
        for alvo, ef in efeitos.items():
            delta = ef['intervalo']
            total = total.somar(delta)
            if delta.inferior == delta.superior:
                parcial += delta.inferior
            item = por_id.get(alvo)
            if item is None:
                item = dict(parcela_id=alvo, base_centavos=0)
                livro.append(item)
            novo = delta.somar(Intervalo(item['base_centavos'], item['base_centavos']))
            exigir(novo.inferior is None or novo.inferior >= 0, 'Obrigação negativa')
            item.update(novo=novo.saida(), delta=delta.saida(True), efeito_id=ef['efeito_id'],
                        fonte_refs=ef['fonte_refs'], origens_causais=ef['origens_causais'])
        fim_base = base[e['marco_final_id']]['fim'].inferior
        fim = datas[e['marco_final_id']]['fim']
        _, _, _, pred, _ = validar_estado(e)
        contexto_hash = resumo([estado, evento, propostas, politica])
        for decisao in decisoes:
            proposta = next(p for p in propostas if p['id'] == decisao['proposta_id'])
            decisao['nos_alvo'] = sorted(nos_proposta(proposta, e))
            exigir(decisao['nos_alvo'], 'Proposta aplicada sem proprietário auditável')
        nos = []
        for entidade in e['entidades']:
            k = entidade['id']
            comum = dict(execucao_id=execucao_id, no_id=k, evento_id=evento_id, revisao=1,
                         contexto_hash=contexto_hash, predecessores_versoes={p: 1 for p in pred.get(k, [])},
                         processamento='calculado', execucao={'estado': 'ok'}, decisoes=[d for d in decisoes if k in d['nos_alvo']],
                         efeitos_custo=[], origens_causais=[o for p in propostas if k in nos_proposta(p, e) for o in p['origens_causais']],
                         regras_aplicadas=(['FS0'] if pred.get(k) else []) + [r['id'] for r in e['regras_transferencia'] if r['restricao_destino_id'] in {x['id'] for a in e['atividades'] if a['id'] == k for x in a['restricoes_liberacao']}],
                         evidencias=entidade['fonte_refs'], lacunas=[], motivo_deterministico='Recálculo offline sem interpretador; entrada manual revisada')
            comum['regras_aplicadas'] += [r for p in propostas if k in nos_proposta(p, e) for r in p['regra_refs']]
            for t in e['regras_transferencia']:
                rel = next(r for r in e['relacoes'] if r['id'] == t['relacao_id'])
                if rel['origem_id'] == k:
                    comum['predecessores_versoes'][rel['destino_id']] = 1
            for ef in efeitos.values():
                if ef['no_id'] == k:
                    comum['efeitos_custo'].append(dict(parcela_id=ef['parcela_id'], efeito_id=ef['efeito_id'], delta_centavos=ef['intervalo'].saida(True), fonte_refs=ef['fonte_refs']))
            for rc in e['regras_custo']:
                if isinstance(rc['intervalo']['fim_ref'], dict) and rc['intervalo']['fim_ref']['atividade_id'] == k:
                    item = por_id[rc['parcela_id']]
                    comum['regras_aplicadas'].append(rc['id'])
                    comum['efeitos_custo'].append(dict(parcela_id=rc['parcela_id'], efeito_id=item['efeito_id'], delta_centavos=item['delta'], fonte_refs=item['fonte_refs']))
            if k in datas:
                atividade = next(a for a in e['atividades'] if a['id'] == k)
                comum['restricoes_usadas'] = deepcopy(atividade['restricoes_liberacao'])
                comum['duracao_usada'] = deepcopy(atividade['duracao'])
                comum.update(inicio=datas[k]['inicio'].saida(), fim=datas[k]['fim'].saida(), delta_fim=datas[k]['fim'].menos(base[k]['fim'].inferior).saida(True))
                comum['lacunas'] = comum['fim']['lacunas']
                if comum['fim']['estado'] != 'exato':
                    comum['execucao'] = {'estado': 'parcial'}
            else:
                na = dict(estado='inaplicavel', valor=None, direcao='desconhecida', evidencias=entidade['fonte_refs'], lacunas=[], motivo='Entidade não temporal')
                comum.update(inicio=na, fim=na, delta_fim=na)
            nos.append(comum)
        completo_p = fim.inferior == fim.superior
        completo_c = total.inferior == total.superior
        return dict(execucao_id=execucao_id, projeto_id=e['projeto_id'], versao=e['versao'], evento_id=evento_id,
                    condicao='motor_offline_manual', manifesto_hash=resumo(estado), contexto_hash=contexto_hash,
                    fim_base=base[e['marco_final_id']]['fim'].saida(), fim_novo=fim.saida(), delta_dias=fim.menos(fim_base).saida(True),
                    custo_base=Intervalo(custo_base, custo_base, tuple(e['linha_base']['custo_centavos']['evidencias'])).saida(),
                    custo_novo=total.saida(), delta_centavos=total.menos(custo_base).saida(True),
                    completude={'prazo': 'completo' if completo_p else 'parcial', 'custo': 'completo' if completo_c else 'parcial'},
                    parcial_identificado_centavos=parcial, decisoes=decisoes, resultados_no_refs=[n['no_id'] for n in nos], resultados_nos=nos,
                    livro_parcelas=livro, lacunas=list(dict.fromkeys(fim.lacunas + total.lacunas)),
                    execucao={'estado': 'ok' if completo_p and completo_c else 'parcial', 'erros': []},
                    consumo={'chamadas': 0, 'custo_api_centavos': 0, 'latencia_ms': round((perf_counter() - inicio_execucao) * 1000, 3)})
    except (EntradaInvalida, KeyError, TypeError, AttributeError, StopIteration) as erro:
        return dict(execucao_id=execucao_id, execucao={'estado': 'erro', 'erros': [{'codigo': 'ENTRADA_INVALIDA', 'mensagem': str(erro)}]},
                    decisoes=[{'status': 'requer_revisao', 'motivos': [str(erro)]}])
