"""Triagem descritiva de cada desfecho B/H/T, sem reescrever previsões."""
from pathlib import Path
from collections import Counter
import json
O=Path(__file__).parent

def main():
    normal=json.loads((O/'normalizacao.json').read_text())
    refs={(r['caso_id'],r['versao_projeto']):r['verdade'] for r in json.loads((O/'referencias_avaliacao_autoral.json').read_text())}
    linhas=[]
    for l in normal['linhas']:
        s=l['slot'];r=l.get('resultado_original',{});g=refs[(s['caso_id'],s['versao_projeto'])]
        for d,q in l['desfechos'].items():
            v=g[d];ex=q['classe']=='exato';refex=v['estado']=='exato'
            if q['classe'] not in ('exato','indeterminado','direcao'):
                categoria='falha_operacional_ou_contrato'
            elif ex and not refex:
                categoria='falsa_precisao_candidata'
            elif ex and q['quantidade']['valor']!=v['valor']:
                categoria='divergencia_numerica'
            elif ex:
                categoria='coincidencia_numerica_sem_auditoria_semantica'
            elif refex:
                categoria='nao_quantificado_com_referencia_exata'
            else:
                categoria='magnitude_nao_exata_preservada'
            linhas.append(dict(execucao_id=s['execucao_id'],caso=s['caso_id'],repeticao=s['repeticao'],condicao=s['condicao'],desfecho=d,categoria=categoria,direcao_excessiva_ou_contraditoria=q['classe']=='direcao' and (v['direcao']=='desconhecida' or q['quantidade']['direcao']!=v['direcao']),direcao_sustentada_nao_recuperada=v['estado']=='direcao' and q.get('quantidade',{}).get('direcao')!=v['direcao'],previsao=q,referencia=v,resultado_hash=l.get('resultado_hash'),execucao=r.get('execucao'),lacunas_finais=r.get('lacunas',[])))
    resumo={c:dict(Counter(l['categoria']for l in linhas if l['condicao']==c))for c in 'BHT'}
    resultado=dict(natureza='Triagem técnica do mesmo autor; categorias não certificam suporte semântico nem inferibilidade por view.',N_desfechos=len(linhas),resumo=resumo,direcoes_excessivas_ou_contraditorias=[l for l in linhas if l['direcao_excessiva_ou_contraditoria']],linhas=linhas)
    (O/'triagem_todas_condicoes.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resumo,ensure_ascii=False))

if __name__=='__main__':main()
