"""Cálculo offline sobre cópias; nenhuma leitura de arquivos ou referências autorais.

A política é revisão humana de operações específicas, não autorização da própria IA.
O motor verifica estrutura/proveniência, não interpreta a semântica de um trecho.
"""
from copy import deepcopy
import hashlib
import json
from time import perf_counter
from .conhecimento import EntradaInvalida, Intervalo, exigir, inteiro, ler, maximo


def resumo(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def catalogo(itens):
    exigir(isinstance(itens, list), 'Catálogo deve ser lista')
    exigir(all(isinstance(x.get('id'), str) and x['id'] for x in itens), 'ID inválido')
    resultado = {x['id']: x for x in itens}
    exigir(len(resultado) == len(itens), 'ID duplicado')
    return resultado


def referencias(refs, fontes):
    exigir(isinstance(refs, list) and refs, 'Evidência obrigatória')
    for r in refs:
        exigir(r.get('fonte_id') in fontes and
               r.get('localizador') == fontes[r['fonte_id']]['localizador'], 'Referência não visível/inválida')


def validar_estado(e):
    exigir(e['schema_version'] == '1.0-proposta', 'Versão incompatível')
    exigir(e['moeda'] == 'BRL' and e['calendario']['unidade'] == 'dia_corrido'
           and e['calendario']['indice_inicial'] == 0, 'Unidade/calendário incompatível')
    fontes = catalogo(e['fontes'])
    entidades = catalogo(e['entidades'])
    atividades = catalogo(e['atividades'])
    relacoes = catalogo(e['relacoes'])
    parcelas = catalogo(e['parcelas_base'])
    regras = catalogo(e['regras_custo'])
    transferencias = catalogo(e['regras_transferencia'])
    catalogo(e['regras_locais'])
    exigir(e['marco_final_id'] in atividades and entidades[e['marco_final_id']]['tipo'] == 'marco', 'Marco inválido')
    exigir(ler(atividades[e['marco_final_id']]['duracao'], 0).inferior == 0 and
           ler(atividades[e['marco_final_id']]['duracao'], 0).superior == 0, 'Marco deve ter duração zero')
    # Todas as referências de entrada são resolvidas, incluindo conhecimentos aninhados.
    def conferir(obj):
        if isinstance(obj, dict):
            exigir(not any(k.startswith('expected_') or k in ('gabaritos', 'afetados_esperados') for k in obj), 'Referência de avaliação em entrada')
            if 'fonte_id' in obj:
                referencias([obj], fontes)
            if 'estado' in obj and 'valor' in obj:
                ler(obj)
                if obj.get('unidade') is not None:
                    exigir(obj['unidade'] in ('dia_corrido', 'BRL_centavo'), 'Unidade inválida')
            for v in obj.values():
                conferir(v)
        elif isinstance(obj, list):
            for v in obj:
                conferir(v)
    conferir(e)
    restricoes = {}
    for a in atividades.values():
        exigir(a['id'] == a['entidade_id'] and a['id'] in entidades and entidades[a['id']]['tipo'] in ('atividade', 'marco'), 'Atividade inválida')
        ler(a['duracao'], 0)
        referencias(a['fonte_refs'], fontes)
        for r in a['restricoes_liberacao']:
            exigir(r['id'] not in restricoes and r['atividade_id'] == a['id'], 'Restrição inválida/duplicada')
            exigir(r['tipo'] in ('nao_antes', 'disponibilidade_requerida'), 'Tipo de restrição inválido')
            ler(r['valor'], 0)
            referencias(r['fonte_refs'], fontes)
            restricoes[r['id']] = r
    predecessores = {k: [] for k in atividades}
    causal = {k: [] for k in entidades}
    for r in relacoes.values():
        exigir(r['origem_id'] in entidades and r['destino_id'] in entidades, 'Endpoint inválido')
        exigir(r['tipo'] in ('precede_FS', 'requer', 'fornece', 'responsavel', 'pertence'), 'Relação desconhecida')
        referencias(r['fonte_refs'], fontes)
        if r['tipo'] == 'precede_FS':
            exigir(r.get('lag_dias') == 0 and r['origem_id'] in atividades and r['destino_id'] in atividades, 'FS incompatível')
            predecessores[r['destino_id']].append(r['origem_id'])
            causal[r['destino_id']].append(r['origem_id'])
    for t in transferencias.values():
        exigir(t['operacao'] == 'disponibilidade_para_restricao' and t['origem_atributo'] == 'disponibilidade', 'Transferência fora de catálogo')
        exigir(t['relacao_id'] in relacoes and t['restricao_destino_id'] in restricoes, 'Transferência sem alvo')
        r = relacoes[t['relacao_id']]
        alvo = restricoes[t['restricao_destino_id']]
        exigir(r['tipo'] == 'requer' and r['origem_id'] in atividades and entidades[r['destino_id']]['tipo'] == 'componente', 'Direção requer inválida')
        exigir(alvo['tipo'] == 'disponibilidade_requerida' and alvo['atividade_id'] == r['origem_id'] and alvo.get('regra_transferencia_id') == t['id'] and
               alvo.get('atributo_origem_ref') == {'entidade_id': r['destino_id'], 'atributo': 'disponibilidade'}, 'Projeção inválida')
        disponibilidade = entidades[r['destino_id']]['atributos']['disponibilidade']
        exigir(disponibilidade['unidade'] == 'dia_corrido', 'Unidade de disponibilidade')
        exigir(ler(disponibilidade['conhecimento'], 0) == ler(alvo['valor'], 0) or
               (ler(disponibilidade['conhecimento'], 0).inferior, ler(disponibilidade['conhecimento'], 0).superior) ==
               (ler(alvo['valor'], 0).inferior, ler(alvo['valor'], 0).superior), 'Restrição derivada inconsistente')
        causal[r['origem_id']].append(r['destino_id'])
    for r in restricoes.values():
        if r['tipo'] == 'disponibilidade_requerida':
            exigir(r.get('regra_transferencia_id') in transferencias, 'Restrição sem regra')
            t = transferencias[r['regra_transferencia_id']]
            rel = relacoes[t['relacao_id']]
            exigir(t['restricao_destino_id'] == r['id'] and rel['origem_id'] == r['atividade_id'], 'Restrição órfã/reciprocidade inválida')
    ordenar(causal)
    ordem = ordenar(predecessores)
    # Fechamento topológico de todas as atividades obrigatórias no marco.
    alcancados = set()
    def ancestrais(k):
        if k not in alcancados:
            alcancados.add(k)
            for p in predecessores[k]:
                ancestrais(p)
    ancestrais(e['marco_final_id'])
    exigir(alcancados == set(atividades), 'Atividade fora do marco final')
    temporais = set()
    for p in parcelas.values():
        inteiro(p['valor_centavos'], 0)
        exigir(p['moeda'] == 'BRL' and p['escopo_id'] == e['projeto_id'], 'Parcela fora de escopo')
        referencias(p['fonte_refs'], fontes)
    for r in regras.values():
        exigir(r['parcela_id'] in parcelas and r['parcela_id'] not in temporais, 'Regra temporal duplicada/sem parcela')
        temporais.add(r['parcela_id'])
        inteiro(r['taxa_centavos_dia'], 0)
        inteiro(r['base_contratada_dias'], 0)
        exigir(r['unidade_taxa'] == 'BRL_centavo/dia_corrido' and r['politica_reducao'] in ('sem_credito', 'recalculavel_com_credito'), 'Regra temporal incompatível')
        referencias(r['fonte_refs'], fontes)
        for ref in r['intervalo'].values():
            exigir(ref == 'D0' or isinstance(ref, dict) and ref.get('atividade_id') in atividades and ref.get('atributo') in ('inicio', 'fim'), 'Intervalo inválido')
    exigir(set(e['declaracoes_completude']) == {'entregas', 'custos', 'relacoes'}, 'Declarações de completude ausentes')
    for c in e['declaracoes_completude'].values():
        exigir(type(c['completa']) is bool, 'Completude inválida')
        referencias(c['fonte_refs'], fontes)
    return atividades, entidades, restricoes, predecessores, ordem


def ordenar(pred):
    restantes = {k: set(v) for k, v in pred.items()}
    ordem = []
    while restantes:
        livres = sorted(k for k, v in restantes.items() if not v)
        exigir(livres, 'Ciclo na projeção executável')
        for k in livres:
            ordem.append(k)
            del restantes[k]
        for v in restantes.values():
            v.difference_update(livres)
    return ordem


def cronograma(e):
    atividades, _, _, pred, ordem = validar_estado(e)
    datas = {}
    for k in ordem:
        a = atividades[k]
        inicio = maximo([Intervalo(0, 0)] + [ler(r['valor'], 0) for r in a['restricoes_liberacao']] + [datas[p]['fim'] for p in pred[k]])
        datas[k] = {'inicio': inicio, 'fim': inicio.somar(ler(a['duracao'], 0))}
    return datas


def incidencia(r, datas):
    def data(ref):
        return Intervalo(0, 0) if ref == 'D0' else datas[ref['atividade_id']][ref['atributo']]
    fim = data(r['intervalo']['fim_ref'])
    inicio = data(r['intervalo']['inicio_ref'])
    lo = None if fim.inferior is None or inicio.superior is None else fim.inferior - inicio.superior
    hi = None if fim.superior is None or inicio.inferior is None else fim.superior - inicio.inferior
    exigir(hi is None or hi >= 0, 'Intervalo temporal invertido')
    lacunas = fim.lacunas + inicio.lacunas
    if lo is None or lo < 0:
        lacunas += ('Ordem/magnitude do intervalo temporal não determinada',)
    dias = r['base_contratada_dias']
    taxa = r['taxa_centavos_dia']
    if taxa == 0:
        return Intervalo(0, 0, tuple(r['fonte_refs']))
    if taxa is None:
        return Intervalo(0, 0 if hi is not None and hi <= dias else None, tuple(r['fonte_refs']), ('Preço da extensão desconhecido',))
    return Intervalo(max(0, (lo if lo is not None else 0) - dias) * taxa, None if hi is None else max(0, hi - dias) * taxa,
                     fim.evidencias + inicio.evidencias + tuple(r['fonte_refs']), lacunas)


def preparar(estado):
    """Valida e recalcula a baseline; inconsistência impede qualquer previsão."""
    e = deepcopy(estado)
    datas = cronograma(e)
    fim = datas[e['marco_final_id']]['fim']
    exigir(ler(e['linha_base']['fim'], 0).inferior == ler(e['linha_base']['fim'], 0).superior and fim.inferior == fim.superior == ler(e['linha_base']['fim'], 0).inferior, 'Baseline de prazo inconsistente')
    custo = sum(p['valor_centavos'] for p in e['parcelas_base'])
    exigir(ler(e['linha_base']['custo_centavos'], 0).inferior == ler(e['linha_base']['custo_centavos'], 0).superior and custo == ler(e['linha_base']['custo_centavos'], 0).inferior, 'Baseline de custo inconsistente')
    for r in e['regras_custo']:
        inc = incidencia(r, datas)
        d = r['decomposicao_base']
        fixo_k = ler(d['fixo_centavos'], 0)
        declarado_k = ler(d['incidencia_centavos'], 0)
        exigir(fixo_k.inferior == fixo_k.superior and declarado_k.inferior == declarado_k.superior, 'Decomposição base exige conhecimento exato')
        fixo = fixo_k.inferior
        declarado = declarado_k.inferior
        parcela = next(p for p in e['parcelas_base'] if p['id'] == r['parcela_id'])
        exigir(inc.inferior == inc.superior == declarado and fixo + declarado == parcela['valor_centavos'], 'Decomposição temporal base inconsistente')
    exigir(all(x['completa'] for x in e['declaracoes_completude'].values()), 'Baseline sem fechamento declarado')
    return datas, custo


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
        chave = (alvo, atributo)
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
            regra = next((locais[r] for r in p['regra_refs'] if r in locais), None)
            exigir(regra is not None and regra['no_id'] == alvo and op in regra['operacoes_permitidas'] and atributo in regra['atributos_alvo'], 'Confirmação fora do catálogo')
            if op == 'confirmar_manutencao_atributo':
                exigir(p['unidade'] == 'dia_corrido' and p['valor'] == atividades[alvo][atributo]['valor'], 'Manutenção divergente')
            else:
                exigir(p['unidade'] == 'BRL_centavo' and p['valor'] == 0, 'Ausência deve confirmar zero')
            confirmacoes.add((alvo, atributo))
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
        if 'duracao' in regra['atributos_alvo'] and (alvo, 'duracao') not in confirmacoes and not any(p['alvo_id'] == alvo and p['operacao'] == 'substituir_duracao' for p in propostas):
            raise EntradaInvalida('Condição local de duração não avaliada')
        if 'readequacao' in regra['atributos_alvo']:
            exigir((alvo, 'readequacao') in confirmacoes or any(p['operacao'] == 'registrar_lacuna_custo' and p.get('no_id') == alvo for p in propostas), 'Condição local de custo não avaliada')
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


def nos_proposta(proposta, estado):
    """Resolve proprietário por identidade, sem depender de IDs específicos do fixture."""
    alvo = proposta['alvo_id']
    entidades = {e['id'] for e in estado['entidades']}
    if proposta['operacao'] == 'substituir_restricao':
        return {a['id'] for a in estado['atividades'] for r in a['restricoes_liberacao'] if r['id'] == alvo}
    if proposta['operacao'] == 'aplicar_regra_catalogada':
        regra = next(r for r in estado['regras_custo'] if r['id'] == alvo)
        return {ref['atividade_id'] for ref in regra['intervalo'].values() if isinstance(ref, dict)} or {estado['marco_final_id']}
    return ({alvo} if alvo in entidades else set()) | ({proposta['no_id']} if proposta.get('no_id') in entidades else set())


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
