"""Comparação descritiva pós-coleta. Nunca envia inferências nem altera respostas."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import csv,json

OUT=Path(__file__).parent
OLD=OUT.parent/'etapa9_piloto_v05_20261027'

def ler(p):return json.loads(p.read_text())
def salvar(nome,obj):(OUT/nome).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def main():
    atual=ler(OUT/'resumo_descritivo.json');anterior=ler(OLD/'resumo_descritivo.json')
    novos=ler(OUT/'normalizacao.json');velhos=ler(OLD/'normalizacao.json')
    chave=lambda l:(l['slot']['caso_id'],l['slot']['repeticao'],l['slot']['condicao'])
    mapa_anterior={chave(l):l for l in velhos['linhas']}
    if set(mapa_anterior)!={chave(l)for l in novos['linhas']}:raise ValueError('Pareamento de casos/condições/repetições divergente')
    pares=[];encaminhamentos=[];resumos=[]
    for l in novos['linhas']:
        old=mapa_anterior[chave(l)];s=l['slot']
        for k in ('caso_id','repeticao','condicao','view_hash','snapshot_hash','evento_hash','modelo','config_hash','versao_projeto'):
            if s[k]!=old['slot'][k]:raise ValueError('Input/configuração divergente '+k)
        for d in ('prazo','custo'):
            a,b=old['desfechos'][d],l['desfechos'][d]
            pares.append(dict(caso_id=s['caso_id'],repeticao=s['repeticao'],condicao=s['condicao'],desfecho=d,
                classe_v05=a['classe'],classe_v06=b['classe'],valor_v05=a.get('quantidade',{}).get('valor'),valor_v06=b.get('quantidade',{}).get('valor'),
                exato_nas_duas=a['classe']==b['classe']=='exato',ganhou_cobertura=a['classe']!='exato'and b['classe']=='exato',perdeu_cobertura=a['classe']=='exato'and b['classe']!='exato',
                resultado_hash_v05=old.get('resultado_hash'),resultado_hash_v06=l.get('resultado_hash')))
        if s['condicao']=='H':
            r=l.get('resultado_original',{})
            fechamento=r.get('registro_operacional',{}).get('fechamento_final',{})
            for e in fechamento.get('encaminhamentos',[]):encaminhamentos.append(dict(execucao_id=s['execucao_id'],caso_id=s['caso_id'],repeticao=s['repeticao'],**deepcopy(e)))
            resumos.append(dict(caso_id=s['caso_id'],repeticao=s['repeticao'],estado_v05=old.get('resultado_original',{}).get('execucao',{}).get('estado'),estado_v06=r.get('execucao',{}).get('estado'),fechamento=fechamento.get('estado'),encaminhamentos=len(fechamento.get('encaminhamentos',[])),pendentes=sum(x['estado']=='pendente'for x in fechamento.get('encaminhamentos',[])),lacunas=r.get('lacunas',[])))
    agregado={}
    for c in 'BHT':
        a,b=anterior['por_condicao'][c],atual['por_condicao'][c]
        agregado[c]=dict(estados_v05=a['estados'],estados_v06=b['estados'],latencia_mediana_slot_v05_s=a['latencia_slot_s']['mediana'],latencia_mediana_slot_v06_s=b['latencia_slot_s']['mediana'],inferencia_v05_nanoUSD=a['inferencia_conhecida_nanoUSD'],inferencia_v06_nanoUSD=b['inferencia_conhecida_nanoUSD'],tentativas_v05=a['chamadas'],tentativas_v06=b['chamadas'],desfechos={})
        for d in ('prazo','custo'):
            ps=[p for p in pares if p['condicao']==c and p['desfecho']==d]
            agregado[c]['desfechos'][d]=dict(cobertura_v05=a['metricas'][d]['cobertura_numerica'],cobertura_v06=b['metricas'][d]['cobertura_numerica'],erro_v05=a['metricas'][d]['erro_numerico'],erro_v06=b['metricas'][d]['erro_numerico'],ganharam=sum(p['ganhou_cobertura']for p in ps),perderam=sum(p['perdeu_cobertura']for p in ps),exatos_nas_duas=sum(p['exato_nas_duas']for p in ps),transicoes=dict(Counter(p['classe_v05']+' -> '+p['classe_v06']for p in ps)))
    result=dict(natureza='Comparação descritiva entre novas realizações; sem inferência causal ou superioridade científica',comparacao=agregado,pareamento=pares,resumos_H=resumos,encaminhamentos_H=encaminhamentos,estados_encaminhamentos=dict(Counter(e['estado']for e in encaminhamentos)),analises_H_v05=anterior['analises_H'],analises_H_v06=atual['analises_H'],fechamentos_H_v05=anterior['fechamentos_H'],fechamentos_H_v06=atual['fechamentos_H'],suspeitas_v05=anterior['suspeitas'],suspeitas_v06=atual['suspeitas'],carteira=atual['carteira'],limites=['Referências autorais e inferibilidade não auditadas independentemente','MAE só inclui pares exatos elegíveis','B/T são novas realizações, sem atribuição de sua variação à v06','Contrato e prompt H mudaram; resultados originais preservados'])
    salvar('comparacao_v05_v06.json',result)
    with (OUT/'comparacao_por_caso.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(pares[0]));w.writeheader();w.writerows(pares)
    print(json.dumps(dict(comparacao=agregado,estados_encaminhamentos=result['estados_encaminhamentos']),ensure_ascii=False))

if __name__=='__main__':main()
