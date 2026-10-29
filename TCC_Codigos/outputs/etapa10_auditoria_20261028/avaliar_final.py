"""Pós-processamento offline prospectivo; não contém código de inferência.

Complementa o avaliador congelado com limites e conjuntos discretos auditados.
Compatibilidade nunca vira identificação: exato contra verdade indeterminada
continua falsa precisão, mesmo quando pertence ao domínio de valores possíveis.
"""
from pathlib import Path
import argparse,json,sys
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'TCC_Codigos/src'))
from hibrido_v07_r3.metricas import avaliar
from hibrido_v07_r3.avaliacao import normalizar


def checar_dominio(valor,referencia):
    if type(valor) is not int:raise ValueError('Valor deve ser inteiro')
    if referencia['estado']=='exato':return valor!=referencia['valor']
    valores=referencia.get('valores_admissiveis_auditados')
    if valores is not None:return valor not in valores
    congruencia=referencia.get('congruencia_auditada')
    if congruencia and valor%congruencia['modulo']!=congruencia['resto']:return True
    lim=referencia.get('limites_auditados_suplementares')
    if lim is None:return None
    return ((lim['inferior'] is not None and valor<lim['inferior']) or
            (lim['superior'] is not None and valor>lim['superior']))


def executar(registros):
    m=json.loads((OUT/'preparacao_final_v2/manifesto.json').read_text())
    refs=json.loads((ROOT/'TCC_Codigos/data/final/etapa10_v2/referencias/referencias_avaliacao.json').read_text())
    rel=avaliar(m,registros,refs)
    refidx={(r['caso_id'],r['versao_projeto']):r for r in refs}
    rel['dominios_auditados_suplementares']=[]
    for linha in normalizar(m,registros)['linhas']:
        s=linha['slot'];ref=refidx[(s['caso_id'],s['versao_projeto'])]
        for dim,p in linha['desfechos'].items():
            if p['classe']!='exato':continue
            valor=p['quantidade']['valor'];vis=ref['por_view'][s['condicao']][dim];v=ref['verdade'][dim]
            rel['dominios_auditados_suplementares'].append(dict(execucao_id=s['execucao_id'],desfecho=dim,
                contradiz_verdade=checar_dominio(valor,v),contradiz_dominio_visivel=checar_dominio(valor,vis),
                magnitude_identificada_no_contexto=vis['estado']=='exato',
                nota='Pertencer ao domínio não autoriza resposta exata quando há mais de um valor admissível.'))
    rel['revisao_humana']=False
    rel['aviso']='Aplicação das referências técnicas; suporte semântico de cada resposta requer auditoria vinculada ao resultado e à view.'
    return rel


def contraprovas():
    ind=dict(estado='indeterminado',limites_auditados_suplementares=dict(inferior=0,superior=None))
    discreto=dict(estado='direcao',valores_admissiveis_auditados=[3,4,6])
    checks=[checar_dominio(-1,ind) is True,checar_dominio(0,ind) is False,
            ind['estado']=='indeterminado',checar_dominio(5,discreto) is True,
            checar_dominio(4,discreto) is False,checar_dominio(0,dict(estado='exato',valor=-11600)) is True]
    seis=dict(ind,congruencia_auditada=dict(modulo=6,resto=0))
    checks += [checar_dominio(7,seis) is True,checar_dominio(6,seis) is False]
    vazio=executar([])
    checks += [len(vazio['detalhes'])==18,all(v['N']==3 and v['erro_numerico']['n']==0 for v in vazio['metricas'].values())]
    if not all(checks):raise ValueError('Falhou contraprova do avaliador')
    return dict(contraprovas=len(checks),aprovadas=True,previsoes_geradas=0,
                nota='Testes de domínio e ausência, sem execução preditiva dos casos finais.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registros',type=Path)
    parser.add_argument('--saida',type=Path)
    args=parser.parse_args()
    if args.registros:
        if not args.saida:parser.error('--saida é obrigatório com --registros')
        if args.saida.exists():parser.error('Saída existente; escolha novo destino para preservar evidências')
        result=executar(json.loads(args.registros.read_text()))
        args.saida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    else:
        result=contraprovas()
        (OUT/'contraprovas_avaliador_final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False))
