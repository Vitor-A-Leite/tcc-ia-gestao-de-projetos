"""Preparação autoral de referências por view, isolada de qualquer preditor."""
from copy import deepcopy
from interpretacao_no.contratos import hash_json
from .limites import validar_limites


def preparar_referencias(gabaritos, casos_views, versoes):
    """Não lê previsões. Conserva verdade autoral; não declara revisão independente.

    Inferibilidade B conservadora: a ausência das precedências não determina
    toda informação possível por inferência. Casos controversos ficam pendentes.
    """
    resultado = []
    for g in gabaritos['casos']:
        views = casos_views[g['caso_id']]
        verdade = {}
        for d,k in (('prazo','delta_dias'), ('custo','delta_centavos')):
            x = g[d]
            verdade[d] = dict(estado=x['estado'], valor=x.get(k), direcao=x['direcao'],
                               unidade='dia_corrido' if d=='prazo' else 'BRL_centavo')
            # Os gabaritos originais guardam estes limites SOMENTE na derivação
            # textual. Transcrição autoral explícita, localizada no avaliador.
            if d=='custo' and g['caso_id'] in ('k_23d8','k_8c65'):
                if 'delta≥20000' not in g['derivacao_manual'].replace(' ',''):
                    raise ValueError('Derivação original mudou; rever transcrição do limite')
                verdade[d]['limites']=dict(inferior=20000,superior=None,unidade='BRL_centavo',grandeza='delta',
                    proveniencia=dict(tipo='transcricao_autoral_derivacao',referencia_origem_hash=hash_json(g),
                        derivacao=g['derivacao_manual'],fonte_ids=deepcopy(g['fontes_conferir'])))
            validar_limites(verdade[d],d,hash_json(g))
        por_view = {}
        for c,v in views.items():
            por_view[c] = {}
            for d in ('prazo','custo'):
                estado = verdade[d]['estado'] if c in ('H','T') else 'pendente'
                derivacao = g['derivacao_manual'] if c in ('H','T') else (
                    'Precedências e requisito exclusivo ausentes. Nomes, disponibilidade, cláusulas, '
                    'baseline e evento permitem inferências legítimas, cuja suficiência deve ser '
                    'auditada; não equiparar automaticamente desconhecimento da rede à indeterminação.')
                # Casos identificados somente nesta referência autoral, nunca no preditor.
                if c == 'B' and g['caso_id'] == 'k_e168':
                    estado = verdade[d]['estado']
                    derivacao = 'Disponibilidade D2 e demais condições preservadas; aceite mantém montagem e ausência de readequação. Prazo permanece baseline, taxa adicional única 30000; nenhum aumento temporal, sem incidência extra. Não requer reconstruir rede.'
                if c == 'B' and g['caso_id'] == 'k_23d8':
                    estado = 'indeterminado' if d == 'prazo' else 'direcao'
                    derivacao = 'Cláusula comum exige aceite para duração/custo de readequação; aviso explicitamente sem aceite/preço. Cobrança adicional 20000 e domínio não negativo sustentam aumento, sem total exato. Não há prazo global exato demonstrado.'
                if c == 'B' and g['caso_id'] == 'k_8c65' and d == 'custo':
                    estado = 'direcao'
                    derivacao = 'Adicional único 20000; extensão não negativa de preço desconhecido e regra antiga inaplicável. Aumento sustentado sem total exato; duração global não resolvida nesta view.'
                por_view[c][d] = dict(estado=estado, valor=verdade[d]['valor'] if estado == 'exato' else None,
                    direcao=verdade[d]['direcao'] if estado in ('exato','direcao') else 'desconhecida',
                    derivacao=derivacao, view_hash=v['view_hash'],
                    fontes=[dict(fonte_id=f['id'], localizador=f['localizador'], hash=hash_json(f)) for f in v['comum']['fontes']+(views['H']['relacional']['fontes'] if c in ('H','T') else [])],
                    relacoes_hash=hash_json(views['H']['relacional']) if c in ('H','T') else None,
                    status='autoral_pendente_revisao_independente',
                    alcance='união informacional da condição; seleção/contextos efetivamente recebidos por H exigem auditoria própria')
        for c in por_view:
            for d in ('prazo','custo'):
                por_view[c][d]['unidade']=verdade[d]['unidade']
                if 'limites' in verdade[d] and por_view[c][d]['estado']!='pendente':
                    limite=deepcopy(verdade[d]['limites'])
                    visiveis={f['fonte_id'] for f in por_view[c][d]['fontes']}
                    limite['proveniencia']['fonte_ids']=[f for f in limite['proveniencia']['fonte_ids'] if f in visiveis]
                    por_view[c][d]['limites']=limite
                    validar_limites(por_view[c][d],d,hash_json(g))
        for versao in sorted(set(versoes.values())):
            resultado.append(dict(caso_id=g['caso_id'], versao_projeto=versao, verdade=deepcopy(verdade),
                por_view=deepcopy(por_view), derivacao=g['derivacao_manual'], referencia_origem_hash=hash_json(g),
                revisores=[], status='autoral_desenvolvimento_sem_validacao_independente'))
    return resultado
