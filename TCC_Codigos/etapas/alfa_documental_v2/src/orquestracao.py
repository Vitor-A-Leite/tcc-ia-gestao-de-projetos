# Derivada de hibrido_v07_r3/orquestracao.py; original preservado.
# Alfa v1: única mudança funcional na agenda é projetar rotas pertinentes por nó.
# Nenhum nó, predecessor, operação local ou aresta de cálculo é truncado.
"""Agenda H v07: faltas factuais operacionais bloqueiam; notas não substituem o solver."""
from copy import deepcopy
from time import perf_counter
from .vendor.orquestracao import Politica,ordem,_corrente,exigir
from .vendor.interpretacao_no.adaptadores import Simulado
from .vendor.hibrido_v07_r3.contratos import montar_contexto,validar,hash_json
from .vendor.hibrido_v05.motor import calcular
from .vendor.hibrido_v07_r3.temporal import calcular_prazo
from .vendor.hibrido_v07_r3.wire import conferir_vinculo
from .politica import POLITICA
from .apresentacao import registrar_incorporadas, VERSAO as VERSAO_APRESENTACAO
from .vendor.motor_deterministico.motor import preparar,validar_estado,cronograma,resumo

def avaliar(estado, evento, interpretador, politica, *, observador=None):
    """Estado + evento normalizado + interpretador + política -> ResultadoFinal.

    Uma passagem topológica. Pendências impedem publicação de previsão completa;
    estimativas do subconjunto aceito não são apresentadas como resultado final.
    """
    if observador is not None:
        from .revisao import Observador
        exigir(isinstance(observador, Observador), 'Observador inválido')
    inicio = perf_counter()
    e, ev = deepcopy(estado), deepcopy(evento)
    rastro, propostas, analises, pendencias, registros = [], [], [], [], {}
    chamadas = 0
    tempo_revisao = 0.0
    observados, bloqueados, notas_diagnosticas = [], set(), []
    base = None
    try:
        base, custo_base = preparar(e)
        validar_estado(e)
        exigir(politica.versao == POLITICA, 'Política v07 obrigatória')
        politica.iniciar_passagem(e, ev)
        exigir(ev['projeto_id'] == e['projeto_id'] and ev['versao_projeto'] == e['versao'] and type(ev['instante_observacao']) is int and ev['instante_observacao'] == 0, 'Evento incompatível')
        seq, pred = ordem(e)
        configuracao = dict(tipo=getattr(interpretador, 'identidade_runtime', type(interpretador).__module__+'.'+type(interpretador).__qualname__), modelo=getattr(interpretador, 'modelo', None), configuracao=getattr(interpretador, 'configuracao', None), timeout_s=getattr(interpretador, 'timeout_s', None), repetir=getattr(interpretador, 'repetir', False), politica_versao=politica.versao)
        vinculo = (id(interpretador), id(politica.resolver), hash_json(configuracao))
        if politica._vinculo != vinculo:
            politica._geracao += 1
            politica._vinculo = vinculo
        exigir(politica.alvos and set(politica.alvos) <= set(seq), 'Alvos ausentes/ambíguos')
        exigir(set(politica.plano) <= set(seq), 'Plano com nó inexistente')
        exigir(all(type(v) is int and v >= 0 for v in (politica.max_analises, politica.max_chamadas)), 'Limite inválido')
        exigir(politica.max_tempo_s > 0, 'Tempo inválido')
        if not politica.fechamento:
            pendencias.append('Cobertura semântica do evento/obrigações não declarada')
        candidatos = set(politica.alvos)
        for n in seq:
            if pred[n] & candidatos:
                candidatos.add(n)
        locais = [r for r in e['regras_locais'] if r['no_id'] in candidatos and r['id'] not in politica.dispensas]
        for rid, d in politica.dispensas.items():
            exigir(rid in {r['id'] for r in e['regras_locais']} and d.get('motivo') and d.get('evidencias'), 'Dispensa sem suporte explícito')
            fontes = {f['id']: f for f in e['fontes'] + ev['evidencias']}
            for ref in d['evidencias']:
                exigir(ref['fonte_id'] in fontes and fontes[ref['fonte_id']]['localizador'] == ref['localizador'], 'Dispensa com evidência inválida')
        for r in locais:
            if r['no_id'] not in politica.plano:
                pendencias.append('Regra local sem interpretação: ' + r['id'])
                bloqueados.add(r['no_id'])
        for n in seq:
            atual = _corrente(e, propostas, ev)
            datas = cronograma(atual)
            quantitativo = {}
            if n in datas:
                quantitativo = {k: datas[n][k].saida() for k in ('inicio', 'fim')}
            else:
                entidade = next(x for x in atual['entidades'] if x['id'] == n)
                if 'disponibilidade' in entidade['atributos']:
                    quantitativo = {'disponibilidade': deepcopy(entidade['atributos']['disponibilidade']['conhecimento'])}
            registro = dict(execucao_id=politica.execucao_id, no_id=n, revisao=1,
                            predecessores_versoes={p: registros[p]['revisao'] for p in sorted(pred[n])},
                            quantitativo=quantitativo)
            if n in bloqueados or pred[n] & bloqueados:
                bloqueados.add(n)
                registro['quantitativo'] = {}
                registro['estado'] = 'bloqueado_por_predecessor'
                registros[n] = registro
                rastro.append(dict(no_id=n, processamento='nao_avaliado', motivo='Predecessor não validado; baseline não é entrada vigente'))
                continue
            if n in politica.plano:
                selecao = deepcopy(politica.plano[n])
                def fontes_refs(obj):
                    if isinstance(obj, dict):
                        if 'fonte_id' in obj:
                            yield obj['fonte_id']
                        for v in obj.values():
                            yield from fontes_refs(v)
                    elif isinstance(obj, list):
                        for v in obj:
                            yield from fontes_refs(v)
                selecao['fonte_ids'] = sorted(set(selecao['fonte_ids']) | set(fontes_refs([registros[p] for p in pred[n]])) | set(fontes_refs(registrar_incorporadas(propostas, ev['evento_id']))))
                c = montar_contexto(atual, ev, execucao_id=politica.execucao_id, no_id=n, revisao=1,
                                    responsabilidades_operacionais=politica.responsabilidades_para_no(n),
                                    **selecao)
                # Extensão positiva: somente predecessores desta passagem, sem solver global.
                c['versao_apresentacao'] = VERSAO_APRESENTACAO
                c['alteracoes_incorporadas'] = registrar_incorporadas(propostas, ev['evento_id'])
                c['entradas_correntes'] = [deepcopy(registros[p]) for p in sorted(pred[n])]
                c['predecessores_versoes'] = registro['predecessores_versoes']
                c['snapshot_original_hash'] = hash_json(e)
                c['contrato_execucao'] = dict(configuracao=configuracao, geracao=politica._geracao)
                assinatura = hash_json({k: v for k, v in c.items() if k not in ('contexto_hash', 'revisao')})
                anterior = politica.revisoes.get((politica.execucao_id, n))
                revisao = 1 if anterior is None else anterior[1] + (anterior[0] != assinatura)
                politica.revisoes[(politica.execucao_id, n)] = (assinatura, revisao)
                c['revisao'] = registro['revisao'] = revisao
                c['contexto_hash'] = hash_json({k: v for k, v in c.items() if k != 'contexto_hash'})
                chave = (politica.execucao_id, n, c['contexto_hash'])
                a = politica.cache.get(chave)
                if a is None and hasattr(politica, "consultar_cache"): a = politica.consultar_cache(c)
                reuso = a is not None
                if a is None:
                    reserva = (0 if isinstance(interpretador, Simulado) or getattr(interpretador, 'origem', None) == 'simulado' else 2 if getattr(interpretador, 'repetir', False) else 1)
                    motivo_limite = politica.autorizar_passo(c) if hasattr(politica, "autorizar_passo") else None
                    if motivo_limite or len(observados) >= politica.max_analises or chamadas + reserva > politica.max_chamadas or perf_counter() - inicio - tempo_revisao >= politica.max_tempo_s:
                        pendencias.append('Limite de execução: ' + n)
                        rastro.append(dict(no_id=n, processamento='nao_avaliado', motivo=motivo_limite or 'limite', contexto=c))
                        bloqueados.add(n)
                        registro.update(quantitativo={}, estado='nao_avaliado')
                        registros[n] = registro
                        continue
                    try:
                        a = interpretador.analisar(deepcopy(c))
                    except Exception as exc:
                        chamadas = None
                        observados.append(dict(estado='erro', chamadas=None, tokens_entrada=None, tokens_saida=None, custo_api_centavos=None, mensagem=str(exc)))
                        rastro.append(dict(no_id=n, processamento='erro', contexto=c, motivo=str(exc)))
                        raise ValueError('Interpretador violou envelope de falha: ' + str(exc)) from exc
                    chamadas += a['execucao']['chamadas']
                    observados.append(deepcopy(a['execucao']))
                analises.append(deepcopy(a))
                rastro.append(dict(no_id=n, processamento='reuso_cache' if reuso else 'interpretado', motivo='Seleção explícita/condição local', contexto=c, analise=deepcopy(a)))
                if a['execucao']['estado'] != 'ok':
                    pendencias.append('Falha de interpretação: ' + n)
                    bloqueados.add(n)
                else:
                    corpo = {k: v for k, v in a.items() if k not in ('execucao', 'decisoes')}
                    validar(corpo, c)  # nunca confiar no validador alegado pelo interpretador/cache
                    conferir_vinculo(a, c)
                    if observador is not None:
                        # Pareceres não participam do resolver/fechamento/solver.
                        inicio_revisao = perf_counter()
                        try:
                            rastro[-1]['revisao_observacional'] = observador.analisar(deepcopy(c), deepcopy(a))
                        except Exception as exc:
                            rastro[-1]['revisao_observacional'] = [dict(estado='erro_observacao', erro=str(exc), contexto_hash=c['contexto_hash'])]
                        finally:
                            tempo_revisao += perf_counter()-inicio_revisao
                    if any(x['dimensao'] != 'custo' for x in corpo['pendencias_operacionais']):
                        pendencias.extend('Pendência operacional '+n+': '+x['motivo'] for x in corpo['pendencias_operacionais'])
                        bloqueados.add(n)
                    elif politica.resolver is None or not politica.resolver(deepcopy(c), deepcopy(corpo)):
                        pendencias.append(('Autorização operacional pendente: ' if getattr(politica,'modo_condicional',False) else 'Revisão semântica pendente: ') + n)
                        bloqueados.add(n)
                    else:
                        propostas.extend(deepcopy(a['propostas']))
                        notas_diagnosticas.extend(dict(no_id=n,texto=x)for x in a['lacunas'])
                        politica.cache[chave] = deepcopy(a)
                atual = _corrente(e, propostas, ev)
                datas = cronograma(atual)
                if n in datas:
                    registro['quantitativo'] = {k: datas[n][k].saida() for k in ('inicio', 'fim')}
                else:
                    entidade = next(x for x in atual['entidades'] if x['id'] == n)
                    if 'disponibilidade' in entidade['atributos']:
                        registro['quantitativo'] = {'disponibilidade': deepcopy(entidade['atributos']['disponibilidade']['conhecimento'])}
            else:
                rastro.append(dict(no_id=n, processamento='calculado' if n in candidatos else 'reuso_base', motivo='Transferência/FS explícita' if n in candidatos else 'Sem caminho causal nem condição selecionada'))
            if n in bloqueados:
                registro.update(quantitativo={}, estado='requer_revisao')
            else:
                registro['estado'] = ('autorizado_operacional_condicional' if n in politica.plano else 'calculado_sem_interpretacao') if getattr(politica,'modo_condicional',False) else 'validado_pela_politica'
            registro['propostas_refs'] = [p['id'] for p in propostas if p.get('no_id') == n]
            registro['fatos_evento_refs'] = [dict(fonte_id=f['id'], localizador=f['localizador']) for f in ev['evidencias']] if n in candidatos else []
            registro['fonte_refs'] = next(x['fonte_refs'] for x in e['entidades'] if x['id'] == n)
            registros[n] = registro
        if perf_counter() - inicio - tempo_revisao > politica.max_tempo_s:
            pendencias.append('Tempo total excedido; transporte deve cumprir timeout próprio')
        pendencias_execucao = list(pendencias)
        if getattr(politica,'modo_condicional',False):
            pendencias.extend(politica.verificar_fechamento())
        fechamento = politica.registro_operacional['fechamento_final']
        pm = dict(autorizacoes={p['id']: resumo(p) for p in propostas},
                  predicados=sorted({x for s in politica.plano.values() for x in s.get('predicados', [])}),
                  requisitos_locais=[{'no_id': r['no_id'], 'regra_id': r['id']} for r in locais])
        if pendencias:
            resultado = dict(execucao_id=politica.execucao_id, execucao={'estado': 'parcial', 'erros': []},
                             completude={'prazo': 'parcial', 'custo': 'parcial'}, lacunas=list(dict.fromkeys(pendencias)))
            desconhecido = dict(estado='indeterminado', valor=None, direcao='desconhecida', evidencias=[], lacunas=resultado['lacunas'], motivo=None)
            for k in ('fim_novo', 'delta_dias', 'custo_novo', 'delta_centavos'):
                resultado[k] = deepcopy(desconhecido)
            if not pendencias_execucao and not fechamento['pendencias_por_dimensao']['prazo']:
                resultado.update(calcular_prazo(e, ev, propostas, pm, fechamento))
                resultado['completude']['prazo'] = 'completo' if resultado['delta_dias']['estado'] == 'exato' else 'parcial'
                resultado['projecao_temporal'] = 'validada_com_fechamento_por_dimensao'
        else:
            # Compilação de nome, sem mudar valor/condição/evidência. Motor histórico preservado.
            propostas_motor = deepcopy(propostas)
            for proposta in propostas_motor:
                if proposta['operacao'] == 'alterar_parametros_contratuais':
                    proposta['operacao'] = 'aplicar_regra_catalogada'
            pm_motor = dict(pm, autorizacoes={p['id']: resumo(p) for p in propostas_motor})
            resultado = calcular(e, ev, propostas_motor, pm_motor, politica.execucao_id)
            resultado['mapeamento_operacoes_motor'] = [dict(proposta_id=p['id'], operacao_local=p['operacao'], operacao_motor=m['operacao']) for p,m in zip(propostas,propostas_motor)]
        resultado['pendencias_execucao'] = pendencias_execucao
        por_no = {t['no_id']: t for t in rastro}
        if 'resultados_nos' not in resultado:
            resultado['resultados_nos'] = [dict(execucao_id=politica.execucao_id, no_id=n, evento_id=ev['evento_id'], revisao=reg['revisao'], predecessores_versoes=reg['predecessores_versoes'], quantitativo=reg['quantitativo'], execucao={'estado': 'parcial' if n in bloqueados else 'ok'}) for n, reg in registros.items()]
            resultado['resultados_no_refs'] = list(registros)
        for no in resultado.get('resultados_nos', []):
            registro = registros[no['no_id']]
            passo = por_no[no['no_id']]
            no.update(revisao=registro['revisao'], predecessores_versoes=registro['predecessores_versoes'], processamento=('bloqueado' if registro.get('estado') == 'bloqueado_por_predecessor' else 'nao_avaliado' if no['no_id'] in bloqueados else 'calculado_sem_interpretacao' if passo['processamento'] == 'reuso_base' else 'calculado'), acao_orquestracao=passo['processamento'], motivo_deterministico=passo['motivo'], contexto_hash=passo.get('contexto', {}).get('contexto_hash', hash_json(registro)))
        resultado['notas_diagnosticas_locais']=deepcopy(notas_diagnosticas)
        resultado.update(condicao='orquestracao_v07_r3', politica_origem=politica.origem,
                         rastro_orquestracao=rastro, registros_correntes=list(registros.values()),
                         snapshot_hash=hash_json(e), evento_hash=hash_json(ev), dispensas=deepcopy(politica.dispensas))
        resultado['consumo'] = dict(analises=len(analises), chamadas=chamadas, latencia_ms=round((perf_counter()-inicio)*1000, 3))
        for k in ('tokens_entrada', 'tokens_saida', 'custo_api_centavos'):
            vals = [a.get(k) for a in observados if a.get('chamadas', 0)]
            resultado['consumo'][k] = sum(vals) if all(v is not None for v in vals) else None
        resultado['consumo']['observacoes_novas'] = observados
        if observador is not None:
            resultado['revisao_observacional'] = dict(
                configuracao=observador.identidade(), modo='observacao',
                latencia_ms=round(tempo_revisao*1000, 3),
                altera_aceitacao=False, aprovacao_humana=None,
                registros=[deepcopy(r) for passo in rastro for r in passo.get('revisao_observacional', [])])
        resultado['projeto_id'], resultado['versao'], resultado['evento_id'] = e['projeto_id'], e['versao'], ev['evento_id']
        if base is not None:
            resultado['fim_base'] = base[e['marco_final_id']]['fim'].saida()
            resultado['custo_base'] = deepcopy(e['linha_base']['custo_centavos'])
        if getattr(politica,'modo_condicional',False):
            resultado.update(natureza_previsao='condicional_original',suporte_semantico='nao_auditado',contrato_politica=politica.versao,registro_operacional=deepcopy(politica.registro_operacional))
            for decisao in resultado.get('decisoes',[]):
                decisao.update(suporte_semantico='nao_auditado',motivos=['Aplicação operacional condicional; suporte será auditado posteriormente'])
            for no in resultado.get('resultados_nos',[]):
                for decisao in no.get('decisoes',[]):
                    decisao.update(suporte_semantico='nao_auditado',motivos=['Aplicação operacional condicional; suporte será auditado posteriormente'])
        return resultado
    except (ValueError, AssertionError, KeyError, TypeError, StopIteration) as exc:
        resultado = dict(execucao_id=politica.execucao_id, projeto_id=e.get('projeto_id'), versao=e.get('versao'), evento_id=ev.get('evento_id'), execucao={'estado': 'erro', 'erros': [{'codigo': 'INTEGRACAO_INVALIDA', 'mensagem': str(exc)}]}, rastro_orquestracao=rastro, registros_correntes=list(registros.values()), consumo={'chamadas': chamadas, 'analises': len(analises), 'observacoes_novas': observados, 'latencia_ms': round((perf_counter()-inicio)*1000, 3)})
        if base is not None:
            resultado['fim_base'] = base[e['marco_final_id']]['fim'].saida()
            resultado['custo_base'] = deepcopy(e['linha_base']['custo_centavos'])
        return resultado
