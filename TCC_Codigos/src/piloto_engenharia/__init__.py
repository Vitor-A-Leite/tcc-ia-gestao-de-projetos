"""Piloto de engenharia OFFLINE/PRESCRITO/SEM LLM REAL.

Predição recebe somente entradas e fixture explicitamente prescrita. Não lê
referências. Nenhum transporte concreto, credencial ou chamada de rede.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from condicoes.views import montar_views, auditar_equivalencia
from condicoes.hibrido import executar_h
from orquestracao.simulacao import InterpretadorPrescrito, politica_prescrita
from interpretacao_no.contratos import hash_json

ROTULO = 'OFFLINE/PRESCRITO/SEM LLM REAL'
MODOS_H = (('limite','orquestracao'), ('sem_resolver','suporte'),
           ('sem_fechamento','orquestracao'), ('obsoleto','formato'),
           ('valor_sem_suporte','suporte'), ('resolver_permissivo','suporte'),
           ('ciclo','dados_grafo'), ('unidade','formato'))
SLOTS_CONTRAPROVAS = tuple([dict(id=m,condicao='H',categoria=c) for m,c in MODOS_H] +
    [dict(id=c+'_'+m,condicao=c,categoria='formato' if m=='json_invalido' else 'transporte')
     for c in 'BT' for m in ('json_invalido','timeout')])


def ler(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def preparar_pacote(base, fontes, estado, evento_comum):
    vinculo = dict(base_hash=hash_json(base), grafo_hash=hash_json(estado),
                   versao_base=base['versao_projeto'], versao_grafo=estado['versao'])
    views = montar_views(base, evento_comum, fontes, estado, vinculo=vinculo)
    return views, vinculo, auditar_equivalencia(views)


def executar_prescrito(base, fontes, estado, evento_comum, fixture):
    """Nunca transforma fixture em inferência automática ou recebe gabarito."""
    views, vinculo, auditoria = preparar_pacote(base, fontes, estado, evento_comum)
    i = InterpretadorPrescrito(fixture)
    p = politica_prescrita(fixture, max_chamadas=0)
    resultado = executar_h(base, evento_comum, fontes, estado, fixture['evento'],
                          views['H'], i, p, vinculo=vinculo, origem='simulado')
    return dict(rotulo=ROTULO, views=views, equivalencia=auditoria,
                B=dict(estado='sem_execucao', motivo='Transporte/modelo não definidos'),
                T=dict(estado='sem_execucao', motivo='Transporte/modelo não definidos'),
                H=resultado)


def carregar(dados, *, ampliacao=False):
    """Lista positiva: inputs + fixture atual; nunca glob de referências/outputs."""
    dados = Path(dados)
    if ampliacao:
        raiz = dados/'ampliacao_v1'
        base = ler(raiz/'inputs/base.json')
        fontes = ler(raiz/'inputs/fontes.json')['fontes']
        estado = ler(raiz/'inputs/estado_projeto.json')
        casos = ler(raiz/'inputs/cenarios.json')['casos']
        fixtures = raiz/'fixtures_prescritas'
    else:
        raiz = dados/'projeto_minimo_v1'
        base = ler(raiz/'inputs/base.json')
        fontes = ler(raiz/'inputs/fontes.json')['fontes']
        estado = ler(dados/'projeto_minimo_grafo_v1/estado_projeto.json')
        casos = ler(raiz/'inputs/cenarios.json')['casos']
        fixtures = dados/'orquestracao_simulada_v1'
    for ev in casos:
        # ID do arquivo deriva do catálogo de inputs, não de resultado esperado.
        cid = ev['caso_id']
        if not isinstance(cid, str) or not cid.startswith('k_') or not cid[2:].isalnum():
            raise ValueError('ID de caso inválido')
        yield cid, base, fontes, estado, ev, ler(fixtures/(cid+'.json'))


def contraprovas(estado, fixture, views):
    """Injeções conhecidas; denominador separado de cenários e de desempenho IA."""
    from orquestracao import avaliar
    from condicoes.baseline import Global
    from interpretacao_no.adaptadores import RespostaTransporte
    registros = []
    for modo, categoria in MODOS_H:
        e, f = deepcopy(estado), deepcopy(fixture)
        i = InterpretadorPrescrito(f)
        p = politica_prescrita(f, max_chamadas=0)
        no = next(iter(f['propostas_por_no']))
        if modo == 'limite': p.max_analises = 0
        elif modo == 'sem_resolver': p.resolver = None
        elif modo == 'sem_fechamento': p.fechamento = False
        elif modo == 'obsoleto':
            original = i.analisar
            def obsoleto(c):
                a = original(c); a['contexto_hash'] = 'obsoleto'; return a
            i.analisar = obsoleto
        elif modo in ('valor_sem_suporte','resolver_permissivo','unidade'):
            # Somente resposta injetada muda. Fonte e decisão prescrita ficam iguais.
            i.templates[no][0]['valor']['valor'] = 9
            if modo == 'unidade': i.templates[no][0]['unidade'] = 'BRL_centavo'
            if modo == 'resolver_permissivo': p.resolver = lambda c, a: True
        elif modo == 'ciclo':
            r = deepcopy(next(r for r in e['relacoes'] if r['tipo']=='precede_FS'))
            r.update(id='l_ciclo_contraprova', origem_id=r['destino_id'], destino_id=r['origem_id'])
            e['relacoes'].append(r)
        resultado = avaliar(e, f['evento'], i, p)
        registros.append(dict(id=modo, condicao='H', categoria=categoria, origem=ROTULO,
            injecao='Política deliberadamente falsa autoriza conteúdo sem suporte' if modo=='resolver_permissivo' else modo,
            limitacao_conhecida=modo=='resolver_permissivo',
            proveniencia_injecao=dict(snapshot_hash=hash_json(e),evento_hash=hash_json(f['evento']),
                fixture_hash=hash_json(f),templates_interpretador_hash=hash_json(i.templates),
                fechamento=p.fechamento,max_analises=p.max_analises,max_chamadas=p.max_chamadas,
                resolver='permissivo_deliberadamente_falso' if modo=='resolver_permissivo' else 'ausente' if modo=='sem_resolver' else 'igualdade_prescrita'),
            resultado=resultado))
    for condicao in ('B','T'):
        for modo in ('json_invalido','timeout'):
            def transporte(req):
                if modo == 'timeout': raise TimeoutError('Timeout injetado offline')
                return RespostaTransporte(texto='{inválido', modelo='MOCK_OFFLINE', request_id='mock',
                                          tokens_entrada=10, tokens_saida=2, custo_api_centavos=0)
            r = Global(transporte, modelo='MOCK_OFFLINE', configuracao={}, timeout_s=1,
                       repetir_transporte=False, origem='transporte_mock').prever(views[condicao], execucao_id='falha-'+condicao+'-'+modo)
            registros.append(dict(id=condicao+'_'+modo,condicao=condicao,categoria='formato' if modo=='json_invalido' else 'transporte',
                                  origem='transporte_mock SEM LLM REAL',limitacao_conhecida=False,
                                  proveniencia_injecao=dict(view_hash=views[condicao]['view_hash'],modelo='MOCK_OFFLINE',configuracao={},retry=False),resultado=r))
    return registros


def inventario_codigo():
    raiz = Path(__file__).resolve().parents[1]
    return {str(p.relative_to(raiz)): hashlib.sha256(p.read_bytes()).hexdigest()
            for pacote in ('motor_deterministico','interpretacao_no','orquestracao','condicoes','avaliacao','piloto_engenharia')
            for p in sorted((raiz/pacote).glob('*.py'))}
