"""Limites de referência em deltas; validação não transforma desigualdade em valor."""


def validar_limites(q, desfecho, referencia_hash=None):
    limite=q.get('limites')
    if limite is None:
        return None
    if not isinstance(limite,dict) or set(limite)!={'inferior','superior','unidade','grandeza','proveniencia'}:
        raise ValueError('Contrato de limites inválido')
    unidade='dia_corrido' if desfecho=='prazo' else 'BRL_centavo'
    if q.get('unidade')!=unidade or limite['unidade']!=unidade or limite['grandeza']!='delta':
        raise ValueError('Unidade/grandeza de limite inválida')
    inferior,superior=limite['inferior'],limite['superior']
    if (inferior is None and superior is None) or any(v is not None and type(v) is not int for v in (inferior,superior)):
        raise ValueError('Limites devem ser inteiros, com ao menos uma fronteira conhecida')
    if inferior is not None and superior is not None and inferior>superior:
        raise ValueError('Limites invertidos')
    if q['estado']=='exato':
        if type(q.get('valor')) is not int or (inferior is not None and q['valor']<inferior) or (superior is not None and q['valor']>superior):
            raise ValueError('Valor exato contradiz limite da referência')
    elif q['estado']=='direcao':
        if q.get('valor') is not None or q['direcao'] not in ('aumento','reducao'):
            raise ValueError('Direção com limite incoerente')
        if (q['direcao']=='aumento' and superior is not None and superior<=0) or (q['direcao']=='reducao' and inferior is not None and inferior>=0):
            raise ValueError('Direção contradiz limite da referência')
        if inferior is not None and inferior==superior:
            raise ValueError('Referência direcional com limites iguais exige revisão de exatidão')
    else:
        raise ValueError('Limites nesta versão exigem referência exata ou direcional')
    p=limite['proveniencia']
    if not isinstance(p,dict) or set(p)!={'tipo','referencia_origem_hash','derivacao','fonte_ids'}:
        raise ValueError('Proveniência de limite inválida')
    if p['tipo'] not in ('transcricao_autoral_derivacao','teste_prescrito') or not isinstance(p['derivacao'],str) or not p['derivacao'].strip():
        raise ValueError('Derivação de limite obrigatória')
    h=p['referencia_origem_hash']
    if not isinstance(h,str) or len(h)!=64 or any(c not in '0123456789abcdef' for c in h) or (referencia_hash is not None and h!=referencia_hash):
        raise ValueError('Hash de proveniência de limite inválido')
    if not isinstance(p['fonte_ids'],list) or not p['fonte_ids'] or any(not isinstance(x,str) or not x for x in p['fonte_ids']) or len(set(p['fonte_ids']))!=len(p['fonte_ids']):
        raise ValueError('Fontes de limite inválidas')
    return limite


def contradiz_limite(valor, limite):
    return ((limite['inferior'] is not None and valor<limite['inferior']) or
            (limite['superior'] is not None and valor>limite['superior']))
