"""Transcreve referências após os selos cegos e confere contra autoria separada.

Não modifica inputs, revisões seladas ou código do preditor.
"""
from pathlib import Path
from copy import deepcopy
import json,hashlib,sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'TCC_Codigos/src'))
from hibrido_v07_r3.metricas import avaliar


def ler(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exigir(c,m):
    if not c:raise ValueError(m)


def quantidade(valor,dim,*,inferior=None,superior=None):
    unidade='dia_corrido' if dim=='prazo' else 'BRL_centavo'
    if valor is not None:return dict(estado='exato',valor=valor,direcao='aumento' if valor>0 else 'reducao' if valor<0 else 'zero',unidade=unidade)
    estado='direcao' if inferior is not None and inferior>0 else 'indeterminado'
    q=dict(estado=estado,valor=None,direcao='aumento' if estado=='direcao' else 'desconhecida',unidade=unidade)
    # O schema congelado rejeita limites em indeterminado; preservá-los fora dele.
    q['limites_auditados_suplementares']=dict(inferior=inferior,superior=superior,unidade=unidade,grandeza='delta')
    return q


def main():
    pasta=OUT/'revisao_final_v2_cega';selo=ler(pasta/'selo.json')
    for item in selo['artefatos']+[x for grupo in selo['inputs'].values() for x in grupo]:
        p=ROOT/item['path']
        if not p.is_file():p=ROOT/'TCC_Codigos'/item['path']
        exigir(sha(p)==item['sha256'],'Selo final alterado: '+str(p))
    audit=ler(pasta/'derivacoes.json');aud={c['caso_id']:c for c in audit['casos_H_T']}
    brefs={c['caso_id']:c for c in audit['enumeracao_B']['resultados']}
    autoral=ler(ROOT/'TCC_Codigos/data/final/etapa10_v1/referencias/gabaritos_autorais.json')
    for caso in autoral['casos']:
        rev=aud[caso['caso_id']]
        for campo in ['fim_dia','delta_prazo_dias','custo_centavos','delta_custo_centavos']:
            exigir(caso[campo]==rev[campo],'Derivação autoral/cega diverge: '+campo)
    base=ler(ROOT/'TCC_Codigos/data/final/etapa10_v2/inputs/base.json')
    m=ler(OUT/'preparacao_final_v2/manifesto.json');views=ler(OUT/'preparacao_final_v2/views.json')
    refs=[]
    for cid,c in sorted(aud.items()):
        verdade=dict(prazo=quantidade(c['delta_prazo_dias'],'prazo'),
                      custo=quantidade(c['delta_custo_centavos'],'custo',inferior=c.get('delta_custo_minimo_centavos')))
        if c['delta_custo_centavos'] is None:
            verdade['custo']['congruencia_auditada']=dict(modulo=c['extensao_dias'],resto=0,
                derivacao='Delta = dias de extensão × taxa inteira não negativa; derivação cega selada.')
        b=brefs[cid];bt=b['delta_prazo_dias_possiveis'];bc=b.get('delta_custo_centavos_possiveis')
        visb=dict(prazo=quantidade(bt[0] if len(bt)==1 else None,'prazo',inferior=min(bt),superior=max(bt)),
                  custo=quantidade(bc[0] if bc and len(bc)==1 else None,'custo',inferior=min(bc) if bc else 0,superior=max(bc) if bc else None))
        visb['prazo']['valores_admissiveis_auditados']=bt
        if bc:visb['custo']['valores_admissiveis_auditados']=bc
        por={}
        for cond in 'BHT':
            por[cond]=deepcopy(visb if cond=='B' else verdade)
            for dim,q in por[cond].items():
                q.update(view_hash=views[cid][cond]['view_hash'],status='revisao_tecnica_cega_com_confronto_pos_selo',
                         derivacao='revisao_final_v2_cega/derivacoes.json; enumeração completa do domínio B e cálculo próprio H/T',
                         suporte_semantico_de_previsao='nao_aplicavel_sem_previsoes')
        refs.append(dict(caso_id=cid,versao_projeto=base['versao_projeto'],verdade=verdade,por_view=por,
                         referencia_origem_hash=sha(pasta/'derivacoes.json'),revisao_humana=False,
                         escopo='União documental H/T; suficiência dos contextos locais efetivos requer auditoria de rastros após coleta.'))
    # Verifica contrato e retenção dos 9 slots ausentes, sem fabricar resposta.
    vazio=avaliar(m,[],refs)
    exigir(len(vazio['detalhes'])==18,'N errado com slots ausentes')
    exigir(all(x['N']==3 and x['erro_numerico']['n']==0 for x in vazio['metricas'].values()),'Ausência virou exclusão/erro numérico')
    destino=ROOT/'TCC_Codigos/data/final/etapa10_v2/referencias';destino.mkdir(exist_ok=True)
    (destino/'referencias_avaliacao.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
    (destino/'confronto_autoria_revisao.json').write_text(json.dumps(dict(
        autoral_sha256=sha(ROOT/'TCC_Codigos/data/final/etapa10_v1/referencias/gabaritos_autorais.json'),
        revisao_sha256=sha(pasta/'derivacoes.json'),selo_sha256=sha(pasta/'selo.json'),casos=3,
        campos_conferidos=['fim_dia','delta_prazo_dias','custo_centavos','delta_custo_centavos'],
        divergencias=[],nota='null permanece null; domínio r>=0 e contraprovas r=0/r=1 preservados. V2 esclarece convenções, sem mudar os números H/T.'),ensure_ascii=False,indent=2)+'\n')
    resultado=dict(referencias=3,quantidades_por_view=18,confronto_sem_divergencias=True,
        contraprova_sem_coleta=dict(slots_ausentes=9,dimensoes=18,N_por_condicao=3,MAE=None),
        limites_indeterminados_preservados=True,observacao='Não são resultados do experimento; nenhuma previsão foi gerada.')
    (OUT/'validacao_referencias_finais.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resultado,ensure_ascii=False))


if __name__=='__main__':main()
