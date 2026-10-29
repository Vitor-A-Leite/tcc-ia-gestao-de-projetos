"""Comparação de magnitude e direção, separada da cobertura/MAE."""
from pathlib import Path
import json
O=Path(__file__).parent

def resumir(p):
 n=json.loads((p/'normalizacao.json').read_text());refs={(r['caso_id'],r['versao_projeto']):r['verdade']for r in json.loads((p/'referencias_avaliacao_autoral.json').read_text())}
 resumo={};flags=[]
 for c in 'BHT':
  resumo[c]={}
  for d in ('prazo','custo'):
   out=dict(N=30,referencias_nao_exatas=0,magnitude_nao_exata_valida=0,magnitude_exata_indevida=0,direcao_sustentada_nao_recuperada=0,direcao_excessiva_ou_contraditoria=0)
   for l in n['linhas']:
    s=l['slot']
    if s['condicao']!=c:continue
    g=refs[(s['caso_id'],s['versao_projeto'])][d];q=l['desfechos'][d];direcao=q.get('quantidade',{}).get('direcao')
    if g['estado']!='exato':
     out['referencias_nao_exatas']+=1
     out['magnitude_nao_exata_valida']+=q['classe']in('indeterminado','direcao')
     out['magnitude_exata_indevida']+=q['classe']=='exato'
    out['direcao_sustentada_nao_recuperada']+=g['estado']=='direcao'and direcao!=g['direcao']
    if q['classe']=='direcao'and(g['direcao']=='desconhecida'or direcao!=g['direcao']):
     out['direcao_excessiva_ou_contraditoria']+=1
     flags.append(dict(execucao_id=s['execucao_id'],condicao=c,desfecho=d,previsao=q,referencia=g))
   resumo[c][d]=out
 return dict(resumo=resumo,flags_direcao=flags)

if __name__=='__main__':
 r=dict(natureza='Comparação técnica com referências autorais; direções não são magnitudes e invalidade não é preservação de conhecimento.',v6=resumir(O.parent/'etapa9_piloto_v06_20261027'),v7=resumir(O))
 (O/'comparacao_incerteza.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({v:r[v]['resumo']for v in('v6','v7')},ensure_ascii=False))
