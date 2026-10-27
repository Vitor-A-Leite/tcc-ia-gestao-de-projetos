"""Contraprovas simétricas prescritas: comprova métricas, não compara IA."""
from copy import deepcopy
from pathlib import Path
import json
from interpretacao_no.contratos import hash_json
from .execucoes import registrar, hash_implementacao
from .metricas import avaliar


def q(estado='exato', valor=0, unidade='dia_corrido'):
    return dict(estado=estado, valor=valor if estado == 'exato' else None,
        direcao=('aumento' if valor > 0 else 'reducao' if valor < 0 else 'zero') if estado == 'exato' else 'aumento' if estado == 'direcao' else 'desconhecida',
        evidencias=[dict(fonte_id='f_demo', localizador='L1')] if estado in ('exato','direcao') else [],
        lacunas=[] if estado == 'exato' else ['magnitude ausente'], motivo=None, unidade=unidade)


def montar_demo():
    m = dict(schema_version='1.0-manifesto', uso='teste_prescrito', condicoes=['B','H','T'], execucoes=[])
    registros, refs, audits = [], [], []
    # Verdades/saídas simétricas em todas condições, incluindo falhas e abstinência.
    casos = [('exato',0,'exato',0), ('exato',2,'exato',5), ('exato',2,'indeterminado',0),
             ('exato',2,'invalido',0), ('exato',2,'erro',0), ('direcao',None,'direcao',1),
             ('indeterminado',None,'indeterminado',0), ('indeterminado',None,'exato',7)]
    for i,(estado_ref, valor_ref, classe, valor) in enumerate(casos):
        verdade = {d: dict(estado=estado_ref, valor=valor_ref*(100 if d=='custo' else 1) if valor_ref is not None else None,
            direcao='desconhecida' if estado_ref=='indeterminado' else 'aumento' if estado_ref=='direcao' or valor_ref > 0 else 'zero') for d in ('prazo','custo')}
        ref = dict(caso_id='demo_'+str(i), versao_projeto='demo-v1', verdade=verdade, por_view={})
        for c in m['condicoes']:
            slot = dict(projeto_id='demo', evento_id='e_'+str(i), execucao_id=c+str(i), caso_id=ref['caso_id'], repeticao=1,
                condicao=c, versao_projeto='demo-v1', versao_protocolo='demo-1', view_hash=hash_json([i,c]),
                snapshot_hash=hash_json('snapshot'), evento_hash=hash_json(i), codigo_hash=hash_implementacao(),
                modelo=None, config_hash=hash_json({}), origem='simulado')
            m['execucoes'].append(slot)
            ref['por_view'][c] = {d: dict(estado=estado_ref, view_hash=slot['view_hash'], derivacao='contraprova prescrita', status='teste') for d in ('prazo','custo')}
            r = dict(execucao_id=slot['execucao_id'], projeto_id='demo', evento_id=slot['evento_id'], versao='demo-v1', condicao=c,
                view_hash=slot['view_hash'], snapshot_hash=slot['snapshot_hash'], evento_hash=slot['evento_hash'],
                delta_dias=q(classe if classe not in ('erro','invalido') else 'exato',valor),
                delta_centavos=q(classe if classe not in ('erro','invalido') else 'exato',valor*100,'BRL_centavo'),
                execucao=dict(estado='erro' if classe=='erro' else 'ok', erros=[dict(codigo='timeout')] if classe=='erro' else [],
                    origem='simulado', modelo=None, configuracao={}, config_hash=hash_json({})),
                politica_origem='prescrita_teste_metricas', consumo=dict(chamadas=0,tokens_entrada=0,tokens_saida=0,custo_api_centavos=0,latencia_ms=0,analises=0,observacoes_novas=[]))
            if c=='H':
                r.update(contrato_h='1.0-h',condicao_orquestracao='prescrito_sem_execucao',rastro_orquestracao=[])
            if classe == 'invalido':
                r['delta_dias']['valor'] = 'zero'; r['delta_centavos']['valor'] = 'zero'
            reg = registrar(slot,r); registros.append(reg)
            if i == 0:
                for d in ('prazo','custo'):
                    audits.append(dict(execucao_id=slot['execucao_id'], resultado_hash=reg['resultado_hash'], view_hash=slot['view_hash'],
                        desfecho=d, suporte='sustentado', revisor='auditoria_prescrita_teste', justificativa='zero prescrito explicitamente, não auditoria de IA'))
        refs.append(ref)
    return m, registros, refs, audits


def montar_demo_limites(valor):
    """Mesmo teste nas três condições: limite inferior não é valor exato."""
    m,registros,refs,auditorias=montar_demo()
    limite=dict(inferior=20000,superior=None,unidade='BRL_centavo',grandeza='delta',
        proveniencia=dict(tipo='teste_prescrito',referencia_origem_hash=hash_json('limite-prescrito'),
            derivacao='delta >= 20000 centavos; total exato não conhecido',fonte_ids=['f_demo']))
    refs[5]['verdade']['custo'].update(unidade='BRL_centavo',limites=deepcopy(limite))
    for c in m['condicoes']:
        refs[5]['por_view'][c]['custo'].update(estado='direcao',valor=None,direcao='aumento',unidade='BRL_centavo',limites=deepcopy(limite))
        idx=next(i for i,r in enumerate(registros) if r['metadados']['caso_id']=='demo_5' and r['metadados']['condicao']==c)
        registros[idx]['resultado']['delta_centavos']=q(valor=valor,unidade='BRL_centavo')
        registros[idx]=registrar(m['execucoes'][idx],registros[idx]['resultado'])
    return m,registros,refs,auditorias


def main(destino):
    m,r,refs,a = montar_demo()
    relatorio = avaliar(m,r,refs,a)
    p=Path(destino); p.mkdir(parents=True,exist_ok=True)
    for nome,obj in [('manifesto',m),('previsoes_prescritas',r),('referencias_sinteticas',refs),('auditorias_prescritas',a),('metricas',relatorio)]:
        (p/(nome+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    for valor in (10000,20000,30000):
        ml,rl,fl,al=montar_demo_limites(valor)
        (p/('limite_'+str(valor)+'.json')).write_text(json.dumps(dict(uso='teste_prescrito',
            manifesto=ml,previsoes_prescritas=rl,referencias_sinteticas=fl,auditorias_prescritas=al,
            metricas=avaliar(ml,rl,fl,al)),ensure_ascii=False,indent=2)+'\n')
    (p/'RELATORIO.md').write_text('''# Demonstração offline prescrita — não é experimento\n\nO mesmo conjunto de respostas, erros e falhas foi aplicado a B/H/T. Nenhuma IA foi executada e não há vencedor. São contraprovas sintéticas independentes dos oito avisos autorais.\n\nEm cada condição/desfecho N=8: 3 exatos válidos (incluindo um numericamente errado e uma falsa certeza), 1 direção, 2 indeterminações, 1 inválido e 1 erro. Cobertura 3/8=37,5%. Apenas 2/8 têm predição e verdade exatas: erros 0 e 3 dias (ou 0 e 300 centavos), MAE=1,5 dia / 150 centavos = R$1,50. Acerto exato 1/5 referências exatas; 1/8 total. Direção correta 3/6 elegíveis; 3/8 total.\n\nUma das duas referências indeterminadas recebe abstinência apropriada; a outra, falsa certeza exata. Zero sustentado 1/8 por auditoria PRESCRITA explícita; demais suporte não auditado. Interseção numérica pareada 2/8 em todos pares. Custo API e latência são zero prescritos, não medições de modelo. Auditoria autoral de testes não valida cientificamente sustentação.\n\nJSON conserva todos registros, hashes, matriz de estados/direções, falhas e denominadores. Não imputar erro zero aos seis registros fora do MAE. As contagens de teste demonstram o avaliador e não sustentam superioridade de H/B/T.\n\nRevisão final: envelopes H sintéticos estão explicitamente prescritos, sem execução da orquestração, com rastro vazio e zero análises. Não simulam chamadas ou cache real; estes são exercitados pelos testes de integração.\n\nContraprovas de limites em limite_10000.json, limite_20000.json e limite_30000.json: uma referência de custo direcional tem delta >=20000 centavos. Predição exata 10000 contradiz o mínimo; 20000 e 30000 são compatíveis com o limite, sem demonstrar exatidão. O diagnóstico separado é 1/1 ou 0/1, N=8 por condição. Nos três casos MAE continua 150 centavos sobre os mesmos 2/8 pares exatos; a predição não entra no MAE. Falsa certeza aumenta para 2/8, pois limite conhecido não justifica total exato. Nenhum teste altera a verdade para favorecer uma condição.\n''')
    return relatorio


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
