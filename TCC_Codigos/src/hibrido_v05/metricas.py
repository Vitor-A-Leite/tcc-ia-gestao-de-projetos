"""Único módulo consumidor das referências. Avaliação nunca corrige previsão."""
from collections import Counter, defaultdict
from statistics import mean
from .avaliacao import normalizar
from avaliacao.limites import validar_limites, contradiz_limite


def avaliar(manifesto, registros, referencias, auditorias=()):
    """Referência: caso_id, versao_projeto, verdade {prazo,custo}, por_view.

    por_view[condição][desfecho]={estado,derivacao,status,view_hash}; estado
    pendente não sustenta julgamento de falsa certeza/abstenção. Auditorias são
    vinculadas a resultado_hash, desfecho e view_hash e não alteram previsões.
    """
    dados = normalizar(manifesto, registros)
    refs = {}
    for ref in referencias:
        key = (ref['caso_id'], ref['versao_projeto'])
        if key in refs:
            raise ValueError('Referência duplicada')
        for d in ('prazo','custo'):
            v=ref['verdade'][d]
            if v['estado'] not in ('exato','direcao','indeterminado','inaplicavel'):
                raise ValueError('Estado de referência inválido')
            if v['estado']=='exato':
                if type(v['valor']) is not int or v['direcao']!=('aumento' if v['valor']>0 else 'reducao' if v['valor']<0 else 'zero'):
                    raise ValueError('Referência exata inválida')
            elif v.get('valor') is not None:
                raise ValueError('Referência não exata com magnitude')
            if v['estado']=='direcao' and v['direcao'] not in ('aumento','reducao'):
                raise ValueError('Direção de referência inválida')
            validar_limites(v,d,ref.get('referencia_origem_hash'))
        refs[key] = ref
    audits = {}
    for a in auditorias:
        key = (a['execucao_id'], a['resultado_hash'], a['view_hash'], a['desfecho'])
        if key in audits or a['suporte'] not in ('sustentado', 'contradito', 'insuficiente') or not a.get('revisor') or not a.get('justificativa'):
            raise ValueError('Auditoria inválida/duplicada')
        audits[key] = a
    grupos, pares = defaultdict(list), defaultdict(dict)
    detalhes = []
    usados = set()
    for l in dados['linhas']:
        s = l['slot']; ref = refs.get((s['caso_id'], s['versao_projeto']))
        if ref is None:
            raise ValueError('Referência ausente/versão divergente '+s['caso_id'])
        for d, p in l['desfechos'].items():
            v = ref['verdade'][d]
            vis = ref['por_view'][s['condicao']][d]
            if vis['estado'] not in ('exato','direcao','indeterminado','inaplicavel','pendente'):
                raise ValueError('Estado de referência por view inválido')
            if vis['view_hash'] != s['view_hash']:
                raise ValueError('Referência por view obsoleta')
            limite=validar_limites(v,d,ref.get('referencia_origem_hash'))
            limite_visivel=validar_limites(vis,d,ref.get('referencia_origem_hash'))
            classe = p['classe']; q = p.get('quantidade', {})
            chave_audit = (s['execucao_id'], l['resultado_hash'], s['view_hash'], d)
            a = audits.get(chave_audit)
            if a: usados.add(chave_audit)
            pred_dir = q.get('direcao') if classe in ('exato', 'direcao') else None
            ref_dir = v.get('direcao') if v['estado'] in ('exato', 'direcao') else None
            erro = abs(q['valor']-v['valor']) if classe == v['estado'] == 'exato' else None
            certeza = classe == 'exato'
            elegivel_sem = vis['estado'] != 'pendente'
            raw=l.get('resultado_original', {})
            base_k, novo_k, delta_k = ('fim_base','fim_novo','delta_dias') if d=='prazo' else ('custo_base','custo_novo','delta_centavos')
            quant=[raw.get(k,{}) for k in (base_k,novo_k,delta_k)]
            aritmetica = (quant[1]['valor']-quant[0]['valor']!=quant[2]['valor']) if all(x.get('estado')=='exato' and type(x.get('valor')) is int for x in quant) else None
            contradicao = contradiz_limite(q['valor'],limite) if classe=='exato' and limite is not None else None
            contradicao_visivel = contradiz_limite(q['valor'],limite_visivel) if classe=='exato' and limite_visivel is not None else None
            item = dict(contradicao_limite=contradicao, contradicao_limite_visivel=contradicao_visivel,
                compatibilidade_limite=('contradiz' if contradicao else 'compativel_sem_demonstrar_exatidao') if contradicao is not None else 'nao_comparavel',
                inconsistencia_aritmetica=aritmetica, execucao_id=s['execucao_id'], caso_id=s['caso_id'], repeticao=s['repeticao'], condicao=s['condicao'], desfecho=d,
                classe=classe, referencia_estado=v['estado'], referencia_direcao=ref_dir,
                predito_direcao=pred_dir, erro_absoluto=erro,
                direcao_correta=(pred_dir == ref_dir) if ref_dir is not None else None,
                exato_correto=erro == 0 if v['estado'] == 'exato' else None,
                falsa_certeza=(certeza and vis['estado'] in ('direcao', 'indeterminado')) if elegivel_sem else None,
                indeterminacao_adequada=(classe == 'indeterminado') if vis['estado'] == 'indeterminado' else None,
                suporte=a['suporte'] if a else 'nao_auditado',
                zero_sustentado=bool(classe == 'exato' and q['valor'] == 0 and a and a['suporte'] == 'sustentado'))
            grupos[(s['condicao'], d)].append(item)
            pares[(d, s['caso_id'], s['repeticao'])][s['condicao']] = item
            detalhes.append(item)
    metricas = {}
    for (c, d), itens in grupos.items():
        n = len(itens); erros = [x['erro_absoluto'] for x in itens if x['erro_absoluto'] is not None]
        estados = Counter(x['classe'] for x in itens)
        matriz = Counter((x['referencia_estado'], x['referencia_direcao'], x['classe'], x['predito_direcao']) for x in itens)
        sem = [x for x in itens if x['falsa_certeza'] is not None]
        dirs = [x for x in itens if x['direcao_correta'] is not None]
        exatos_ref = [x for x in itens if x['exato_correto'] is not None]
        abst = [x for x in itens if x['indeterminacao_adequada'] is not None]
        metricas[c+':'+d] = dict(N=n, estados={k: estados[k] for k in ('exato', 'direcao', 'indeterminado', 'inaplicavel', 'invalido', 'erro')},
            taxas_estados={k: estados[k]/n for k in ('exato','direcao','indeterminado','inaplicavel','invalido','erro')},
            cobertura_numerica=dict(n=estados['exato'], N=n, taxa=estados['exato']/n),
            erro_numerico=dict(n=len(erros), N=n, MAE=mean(erros) if erros else None,
                unidade='dia_corrido' if d == 'prazo' else 'BRL_centavo',
                MAE_BRL=mean(erros)/100 if erros and d == 'custo' else None,
                selecao='somente predição exata válida e verdade exata'),
            acerto_exato=dict(n=sum(x['exato_correto'] is True for x in exatos_ref), elegiveis=len(exatos_ref), N=n),
            acerto_direcao=dict(n=sum(x['direcao_correta'] is True for x in dirs), elegiveis=len(dirs), N=n),
            falsa_certeza=dict(n=sum(x['falsa_certeza'] is True for x in sem), auditaveis=len(sem), N=n),
            indeterminacao_adequada=dict(n=sum(x['indeterminacao_adequada'] is True for x in abst), elegiveis=len(abst), N=n),
            zero_sustentado=dict(n=sum(x['zero_sustentado'] for x in itens), N=n),
            inconsistencia_aritmetica=dict(n=sum(x['inconsistencia_aritmetica'] is True for x in itens), auditaveis=sum(x['inconsistencia_aritmetica'] is not None for x in itens), N=n),
            contradicao_limite=dict(n=sum(x['contradicao_limite'] is True for x in itens), comparaveis=sum(x['contradicao_limite'] is not None for x in itens), N=n),
            contradicao_limite_visivel=dict(n=sum(x['contradicao_limite_visivel'] is True for x in itens), comparaveis=sum(x['contradicao_limite_visivel'] is not None for x in itens), N=n),
            suporte=dict(Counter(x['suporte'] for x in itens)),
            matriz=[dict(verdade_estado=k[0], verdade_direcao=k[1], predicao_estado=k[2], predicao_direcao=k[3], n=v) for k,v in matriz.items()])
    pareadas = []
    cs = manifesto['condicoes']
    for i, a in enumerate(cs):
        for b in cs[i+1:]:
            for d in ('prazo', 'custo'):
                conjuntos = [p for (dd, _, _), p in pares.items() if dd == d]
                inter = [p for p in conjuntos if p[a]['erro_absoluto'] is not None and p[b]['erro_absoluto'] is not None]
                pareadas.append(dict(condicoes=[a,b], desfecho=d, n_intersecao=len(inter), N=len(conjuntos),
                    MAE_intersecao={c: mean(p[c]['erro_absoluto'] for p in inter) if inter else None for c in (a,b)},
                    pares=[dict(caso_id=p[a]['caso_id'], repeticao=p[a]['repeticao']) for p in inter]))
    return dict(uso=manifesto['uso'], manifesto_hash=dados['manifesto_hash'], anomalias=dados['anomalias'],
                auditorias_nao_vinculadas=len(audits.keys()-usados), metricas=metricas, pareadas=pareadas,
                detalhes=detalhes, consumo=[dict(execucao_id=l['slot']['execucao_id'], origem=l['slot']['origem'], consumo=l['consumo']) for l in dados['linhas']],
                limites=['Valores/formato não provam suporte semântico; auditoria explícita separada',
                        'Menor MAE condicionado à cobertura não implica superioridade global',
                        'B/H compara sistemas; não identifica efeito causal exclusivo da representação'])
