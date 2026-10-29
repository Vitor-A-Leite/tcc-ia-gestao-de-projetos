"""Projeção de prazo com fechamento temporal, sem completar custo faltante."""
from copy import deepcopy
from time import perf_counter
from motor_deterministico.motor import (validar_estado,catalogo,referencias,preparar,cronograma,incidencia,resumo,nos_proposta)
from motor_deterministico.conhecimento import EntradaInvalida,Intervalo,exigir,inteiro,ler,maximo
from .contratos import verificar_contradicoes,ContratoInvalido

def _aplicar_para_prazo(e, evento, propostas, politica):
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
        # Obrigações monetárias permanecem pendentes no fechamento de custo.
        # Este caminho nunca publica custo e só é chamado com fechamento temporal.
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



def calcular_prazo(estado, evento, propostas, politica, fechamento):
    """Validação do motor preservada; projeta só prazo após cobertura temporal.

    Cópia versionada de aplicar H05. A única obrigação não exigida aqui é
    readequação monetária. Toda validação de propostas e requisitos temporais
    permanece ativa; não fabrica confirmação nem preço para completar o motor.
    """
    exigir(not fechamento['pendencias_por_dimensao']['prazo'], 'Fechamento temporal pendente')
    exigir(fechamento['nos_com_analise_operacional_valida'] == fechamento['nos_exigidos'], 'Nós não interpretados')
    base, _ = preparar(estado)
    e = deepcopy(estado)
    _aplicar_para_prazo(e, evento, propostas, politica)
    fim = cronograma(e)[e['marco_final_id']]['fim']
    return dict(fim_novo=fim.saida(), delta_dias=fim.menos(base[e['marco_final_id']]['fim'].inferior).saida(True))
