"""Verificação pós-coleta, com comparação do banco e arquivos preexistentes."""
from collections import Counter
from pathlib import Path
import fcntl,hashlib,json,sqlite3

OUT=Path(__file__).parent
ROOT=OUT.parents[2]
PASTA=OUT.parent/'etapa9_piloto_real_aprovado_20261026'

def conectar(p):return sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True)
def main():
    with (PASTA/'lote.lock').open()as lock:
        fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
        with conectar(OUT/'ledger_antes.sqlite')as antes,conectar(PASTA/'ledger.sqlite')as agora:
            nomes=[r[0]for r in antes.execute("select name from sqlite_master where type='table'and name not like 'sqlite_%'")]
            for nome in nomes:
                sql='SELECT * FROM '+nome+(' WHERE id<=510'if nome=='chamadas'else'')+' ORDER BY rowid'
                if antes.execute(sql).fetchall()!=agora.execute(sql).fetchall():raise ValueError('Tabela histórica alterada: '+nome)
                if antes.execute('select sql from sqlite_master where name=?',(nome,)).fetchone()!=agora.execute('select sql from sqlite_master where name=?',(nome,)).fetchone():raise ValueError('Schema histórico alterado: '+nome)
            stats=agora.execute('select count(*),sum(comprometido),sum(custo_inferencia)from chamadas').fetchone()
            if stats[0]>810 or stats[1]>5000000000:raise ValueError('Teto excedido')
            slots=agora.execute('select id,estado,resultado from slots_v06 order by rowid').fetchall()
            manifesto=json.loads((OUT/'manifesto.json').read_text())
            if [s for s,_,_ in slots]!=[s['execucao_id']for s in manifesto['execucoes']]:raise ValueError('IDs/ordem divergentes')
            for sid,estado,r in slots:
                if r and json.loads((OUT/(sid+'.json')).read_text())!=json.loads(r):raise ValueError('Arquivo/ledger divergentes: '+sid)
            por=Counter();estados=Counter();maior_entrada=0;quantidade=0
            for i,s,estado,raw in agora.execute('select id,slot,estado,registro from chamadas where id>510 order by id'):
                quantidade+=1;por[s]+=1;estados[estado]+=1
                reg=json.loads(raw)if raw else{};q=reg.get('payload')
                if q:
                    checks=[q['model']=='gpt-6-luna',q['reasoning']=={'effort':'high'},q['stream']is True,q['max_output_tokens']==25000,q['service_tier']=='default',q['prompt_cache_options']=={'ttl':'30m'},q['tools']==[],q['store']is False,q['truncation']=='disabled',reg['retry']==0,reg['timeout_s']==180]
                    if not all(checks):raise ValueError('Configuração divergente: '+str(i))
                if reg.get('contagem_oficial')is not None:maior_entrada=max(maior_entrada,reg['contagem_oficial'])
                if reg.get('response'):
                    if reg.get('contagem_oficial',16001)>16000:raise ValueError('Inferência acima do limite de entrada')
            if any(n>(8 if '-H-'in s else 1)for s,n in por.items()):raise ValueError('Limite per-slot excedido')
            permitidos={'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite','TCC_Codigos/docs/desenvolvimento/STATUS.md','TCC_Codigos/docs/desenvolvimento/PLANO_MESTRE.md'}
            inventario=json.loads((OUT/'integridade_antes.json').read_text())
            alterados=[s for s,h in inventario.items()if not(ROOT/s).is_file()or hashlib.sha256((ROOT/s).read_bytes()).hexdigest()!=h]
            indevidos=set(alterados)-permitidos
            if indevidos:raise ValueError('Arquivos protegidos alterados: '+str(sorted(indevidos)))
            from piloto_v06 import codigo
            if codigo()!=json.loads((OUT/'adendo_aprovado.json').read_text())['codigo']:raise ValueError('Código congelado alterado')
            if not(OUT/'ledger_final.sqlite').exists():
                with sqlite3.connect(str(OUT/'ledger_final.sqlite'))as fim:agora.backup(fim)
            res=dict(tabelas_historicas_preservadas=nomes,chamadas_1_a_510_preservadas=True,arquivos_inventariados=len(inventario),alteracoes_permitidas=alterados,alteracoes_indevidas=[],codigo_congelado_preservado=True,slots=dict(Counter(e for _,e,_ in slots)),tentativas_novas=quantidade,estados_chamadas=dict(estados),max_contagem_oficial=maior_entrada,carteira=dict(tentativas=stats[0],comprometido_nanoUSD=stats[1],inferencia_conhecida_nanoUSD=stats[2]),parada=agora.execute('select motivo from parada_v06').fetchall())
            (OUT/'integridade_final.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps(res,ensure_ascii=False))
if __name__=='__main__':main()
