"""Conferência independente do custo das 280 chamadas finais, a partir de usage."""
from pathlib import Path
import json,sqlite3

OUT=Path(__file__).resolve().parent


def main():
    linhas=[]
    with sqlite3.connect((OUT/'ledger_antes.sqlite').as_uri()+'?mode=ro',uri=True) as c:
        for cid,estado,custo,comprometido,raw in c.execute('select id,estado,custo_inferencia,comprometido,registro from chamadas where id>834 order by id'):
            r=json.loads(raw);q=r['payload'];u=r['response']['usage'];d=u['input_tokens_details']
            entrada=u['input_tokens'];cache=d.get('cached_tokens',0);escrita=d.get('cache_write_tokens',0)
            simples=entrada-cache-escrita
            if simples<0 or d.get('cache_write_tokens_details',{}).get('ttl_12h_tokens',0):raise ValueError('Composição inesperada')
            # Tarifas do snapshot de preços, expressas em nanoUSD/token.
            calculado=simples*100+cache*10+escrita*125+u['output_tokens']*500
            if calculado!=custo or comprometido!=calculado+2000000:raise ValueError('Valor divergente '+str(cid))
            if not (estado=='conciliado' and r['contagem_oficial']<=16000 and q['model']=='gpt-6-luna'
                    and q['reasoning']=={'effort':'high'} and q['max_output_tokens']==25000
                    and q['prompt_cache_options']=={'ttl':'30m'} and q['tools']==[] and q['store'] is False
                    and q['service_tier']=='default' and q['stream'] is True and r['retry']==0):raise ValueError('Configuração divergente')
            linhas.append(dict(call_id=cid,input_simples=simples,input_cache=cache,input_escrita30m=escrita,
                              output_total=u['output_tokens'],calculado_nanoUSD=calculado,comprometido_nanoUSD=comprometido))
    o=dict(chamadas=len(linhas),inferencia_nanoUSD=sum(r['calculado_nanoUSD'] for r in linhas),
           compromisso_nanoUSD=sum(r['comprometido_nanoUSD'] for r in linhas),linhas=linhas,
           fonte_precos='../etapa9_piloto_v07_r3_20261028/precos_verificados.json',
           conclusao='280 custos reproduzidos do usage, incluindo tokens de raciocínio no total de saída e cache de escrita.',
           limite='Conferência contra tarifário registrado na coleta; não prova faturamento nem atualiza preços do provedor.')
    (OUT/'auditoria_uso.json').write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in o.items() if k!='linhas'},ensure_ascii=False))


if __name__=='__main__':main()
