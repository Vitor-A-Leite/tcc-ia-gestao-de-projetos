"""Manifesto e normalização pós-previsão; nenhuma consulta a referência."""
from copy import deepcopy
from pathlib import Path
import hashlib
from condicoes.baseline import validar_quantidade
from interpretacao_no.contratos import hash_json

CAMPOS = ('projeto_id', 'evento_id', 'execucao_id', 'caso_id', 'repeticao', 'condicao', 'versao_projeto',
          'versao_protocolo', 'view_hash', 'snapshot_hash', 'evento_hash',
          'codigo_hash', 'modelo', 'config_hash', 'origem')


def hash_implementacao():
    raiz=Path(__file__).resolve().parents[1]
    return hash_json({str(p.relative_to(raiz)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for pacote in ('condicoes','avaliacao','orquestracao','interpretacao_no','motor_deterministico')
                      for p in sorted((raiz/pacote).glob('*.py'))})


def validar_manifesto(m):
    if m.get('schema_version') != '1.0-manifesto' or m.get('uso') not in ('teste_prescrito', 'desenvolvimento', 'piloto', 'final'):
        raise ValueError('Manifesto incompatível')
    if set(m['condicoes']) not in ({'B', 'H'}, {'B', 'H', 'T'}) or len(set(m['condicoes'])) != len(m['condicoes']):
        raise ValueError('Comparação principal B/H obrigatória')
    ids, pares = set(), set()
    for s in m['execucoes']:
        if set(s) != set(CAMPOS) or s['condicao'] not in m['condicoes'] or type(s['repeticao']) is not int or s['repeticao'] < 1:
            raise ValueError('Slot inválido')
        if s['execucao_id'] in ids or (s['caso_id'], s['repeticao'], s['condicao']) in pares:
            raise ValueError('Slot duplicado')
        ids.add(s['execucao_id']); pares.add((s['caso_id'], s['repeticao'], s['condicao']))
        for k in CAMPOS:
            if k in ('repeticao', 'modelo'):
                continue
            if not isinstance(s[k], str) or not s[k]:
                raise ValueError('Metadado ausente '+k)
        if s['origem'] not in ('simulado', 'transporte_mock', 'llm_transporte_injetado'):
            raise ValueError('Origem inválida')
        if s['modelo'] is not None and not isinstance(s['modelo'], str):
            raise ValueError('Modelo inválido')
        if s['origem'] == 'llm_transporte_injetado' and not s['modelo']:
            raise ValueError('Modelo solicitado ausente')
    grupos = {(s['caso_id'], s['repeticao']) for s in m['execucoes']}
    for caso, repeticao in grupos:
        if {c for a, b, c in pares if a == caso and b == repeticao} != set(m['condicoes']):
            raise ValueError('Condições sem pareamento no manifesto')
    for c in m['condicoes']:
        if len({s['origem'] for s in m['execucoes'] if s['condicao']==c})>1:
            raise ValueError('Origens diferentes exigem manifestos/relatórios separados')
    if not ids:
        raise ValueError('Manifesto vazio')
    return hash_json(m)


def registrar(slot, resultado):
    """Vincula saída original preservada; não altera valores, origem ou modelo."""
    return dict(metadados=deepcopy(slot), resultado=deepcopy(resultado), resultado_hash=hash_json(resultado))


def _conferir_execucao(e, slot, *, local=False):
    if not isinstance(e,dict) or not isinstance(e.get('configuracao'),dict):
        raise ValueError('Configuração H ausente')
    if e.get('modelo')!=slot['modelo'] or hash_json(e['configuracao'])!=slot['config_hash']:
        raise ValueError('Modelo/configuração H divergente')
    # Simulado da etapa 5 registra config_hash=None, configuração={} e modelo=None.
    esperado_hash = None if local and e.get('origem')=='simulado' else slot['config_hash']
    if e.get('config_hash')!=esperado_hash:
        raise ValueError('Hash de configuração H divergente')
    origens = {'simulado': {'simulado'}, 'llm_transporte_injetado': {'llm_transporte_injetado'},
               'transporte_mock': {'llm_transporte_injetado','transporte_mock'}}
    # A etapa 5 não distingue transporte mock; o envelope H registra essa declaração
    # explícita do chamador. Isso não autoriza reclassificar uma análise simulada.
    permitidas = origens[slot['origem']] if local else {slot['origem']}
    if e.get('origem') not in permitidas:
        raise ValueError('Origem H divergente')


def conferir_proveniencia_h(r, slot, *, uso):
    """Verifica análises realmente usadas, novas ou cacheadas; não soma consumo."""
    if r.get('contrato_h')!='1.0-h' or not isinstance(r.get('rastro_orquestracao'),list):
        raise ValueError('Envelope H ausente')
    origem_condicao=r.get('condicao_orquestracao')
    prescrito=(origem_condicao=='prescrito_sem_execucao')
    if prescrito:
        if uso!='teste_prescrito' or slot['origem']!='simulado' or r.get('politica_origem')!='prescrita_teste_metricas' or r['rastro_orquestracao'] or r.get('consumo',{}).get('chamadas')!=0:
            raise ValueError('Envelope H prescrito fora da demonstração offline')
    elif origem_condicao!='orquestracao_v1' and not (origem_condicao is None and r.get('execucao',{}).get('estado')=='erro'):
        raise ValueError('Condição de origem H inválida')
    _conferir_execucao(r['execucao'],slot)
    usadas=[]
    for passo in r['rastro_orquestracao']:
        if passo.get('processamento') in ('interpretado','reuso_cache') and 'analise' not in passo:
            raise ValueError('Análise usada ausente do rastro H')
        if 'analise' not in passo:
            continue
        a=passo['analise']; c=passo['contexto']
        if passo.get('processamento') not in ('interpretado','reuso_cache'):
            raise ValueError('Análise fora de processamento H')
        if any(a.get(k)!=slot[k] for k in ('execucao_id','evento_id')) or a.get('no_id')!=passo.get('no_id'):
            raise ValueError('Identidade da análise H divergente')
        if c.get('contexto_hash')!=hash_json({k:v for k,v in c.items() if k!='contexto_hash'}) or a.get('contexto_hash')!=c['contexto_hash']:
            raise ValueError('Contexto da análise H divergente')
        if c.get('execucao_id')!=slot['execucao_id'] or c.get('evento_id')!=slot['evento_id'] or c.get('no_id')!=a.get('no_id'):
            raise ValueError('Identidade do contexto H divergente')
        if c.get('snapshot_original_hash')!=slot['snapshot_hash'] or c.get('projeto_id')!=slot['projeto_id'] or c.get('versao_projeto')!=slot['versao_projeto']:
            raise ValueError('Snapshot da análise H divergente')
        contrato=c['contrato_execucao']['configuracao']
        config_contexto=contrato.get('configuracao')
        if config_contexto is None and slot['origem']=='simulado':
            config_contexto={}
        if not isinstance(config_contexto,dict) or contrato.get('modelo')!=slot['modelo'] or hash_json(config_contexto)!=slot['config_hash']:
            raise ValueError('Configuração do contexto H divergente')
        _conferir_execucao(a['execucao'],slot,local=True)
        usadas.append(a)
    if type(r.get('consumo',{}).get('analises')) is not int or r['consumo']['analises']!=len(usadas):
        raise ValueError('Contagem de análises H divergente')
    # Observações novas continuam separadas; cache não exige chamada nova.
    for o in r.get('consumo',{}).get('observacoes_novas',[]):
        if 'origem' in o:
            _conferir_execucao(o,slot,local=True)
    if ('prescrit' in r.get('politica_origem','').lower() or 'simulad' in r.get('politica_origem','').lower()) and slot['origem']!='simulado':
        raise ValueError('Política H prescrita rotulada real')


def normalizar(manifesto, registros):
    validar_manifesto(manifesto)
    por_id, anomalias, linhas = {}, [], []
    for r in registros:
        eid = r.get('metadados', {}).get('execucao_id')
        por_id.setdefault(eid, []).append(r)
    previstos = {s['execucao_id'] for s in manifesto['execucoes']}
    for eid in por_id.keys()-previstos:
        anomalias.append(dict(tipo='execucao_extra', execucao_id=eid, quantidade=len(por_id[eid])))
    for s in manifesto['execucoes']:
        rs = por_id.get(s['execucao_id'], [])
        linha = dict(slot=deepcopy(s), desfechos={}, consumo=None, resultado_hash=None)
        problema = None
        if len(rs) != 1:
            problema = 'ausente' if not rs else 'duplicada'
        else:
            registro, r = rs[0], rs[0].get('resultado', {})
            if registro.get('metadados') != s or registro.get('resultado_hash') != hash_json(r):
                problema = 'metadados_hash_divergentes'
            else:
                # H mantém versão grafo; B/T versão comum. Slot declara a versão real da saída.
                esperado = dict(execucao_id=s['execucao_id'], projeto_id=s['projeto_id'], evento_id=s['evento_id'], versao=s['versao_projeto'])
                if any(r.get(k) != v for k, v in esperado.items()):
                    problema = 'identidade_versao_divergente'
                elif r.get('view_hash') != s['view_hash']:
                    problema = 'view_divergente'
                elif r.get('condicao') != s['condicao']:
                    problema = 'condicao_divergente'
                elif (r.get('execucao', {}).get('origem') != s['origem'] or r.get('execucao', {}).get('modelo') != s['modelo'] or r.get('execucao', {}).get('config_hash') != s['config_hash']):
                    problema = 'origem_modelo_config_divergentes'
                elif s['condicao'] == 'H':
                    if r.get('snapshot_hash') != s['snapshot_hash'] or r.get('evento_hash') != s['evento_hash']:
                        problema = 'hash_entrada_H_divergente'
                    if problema is None:
                        try:
                            conferir_proveniencia_h(r,s,uso=manifesto['uso'])
                        except (ValueError,KeyError,TypeError) as exc:
                            problema = 'proveniencia_H_invalida: '+str(exc)
                if problema is None:
                    linha['consumo'] = deepcopy(r.get('consumo'))
                    linha['resultado_hash'] = registro['resultado_hash']
                    linha['resultado_original'] = deepcopy(r)
        if problema:
            anomalias.append(dict(tipo=problema, execucao_id=s['execucao_id'], quantidade=len(rs)))
        for desfecho, k, unidade in (('prazo', 'delta_dias', 'dia_corrido'), ('custo', 'delta_centavos', 'BRL_centavo')):
            if problema:
                q = dict(classe='erro' if problema == 'ausente' else 'invalido', motivo=problema)
            elif r.get('execucao', {}).get('estado') == 'erro':
                erros = r['execucao'].get('erros', [])
                q = dict(classe='invalido' if any(e.get('codigo') == 'saida_invalida' for e in erros) else 'erro', motivo='falha_registrada')
            elif r.get('execucao', {}).get('estado') not in ('ok', 'parcial'):
                q = dict(classe='invalido', motivo='estado_execucao_invalido')
            else:
                try:
                    if s['condicao'] in ('B','T') and r[k].get('unidade') != unidade:
                        raise ValueError('Unidade ausente/inválida')
                    valor = validar_quantidade(r[k], unidade=unidade)
                    q = dict(classe=valor['estado'], quantidade=valor)
                except (ValueError, TypeError, KeyError):
                    q = dict(classe='invalido', motivo='quantidade_invalida')
            linha['desfechos'][desfecho] = q
        linhas.append(linha)
    return dict(manifesto_hash=hash_json(manifesto), linhas=linhas, anomalias=anomalias)
