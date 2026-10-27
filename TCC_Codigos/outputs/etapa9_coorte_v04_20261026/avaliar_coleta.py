"""Pós-coleta somente. Lê resultados/refs; nunca gera previsões nem chama API."""
from copy import deepcopy
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib,json,sqlite3,fcntl
from decimal import Decimal
from avaliacao.referencias import preparar_referencias
from avaliacao.metricas import avaliar
from avaliacao.execucoes import normalizar
from interpretacao_no.contratos import hash_json
from piloto_real.inputs import carregar

ROOT=Path(__file__).resolve().parents[2]
PASTA=ROOT/'outputs/etapa9_piloto_real_aprovado_20261026'
OUT=Path(__file__).parent

def ler(p):return json.loads(p.read_text())
def salvar(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
    with (PASTA/'lote.lock').open() as lock:
        try:fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('Coletor ainda ativo; aguardar término ou parada autorizada') from None
    m=ler(OUT/'manifesto.json');plano={'lote_id':'etapa9-coorte-v04-180s-20261026'}
    db=sqlite3.connect('file:'+str((PASTA/'ledger.sqlite').resolve())+'?mode=ro',uri=True)
    slots=list(db.execute('SELECT id,estado,resultado FROM slots_v04 ORDER BY rowid'))
    if any(e in ('pendente','iniciado') for _,e,_ in slots) and not db.execute('SELECT count(*) FROM parada_v04').fetchone()[0]:raise ValueError('Slots abertos sem parada registrada; não presumir coleta concluída')
    regs=[json.loads(r) for _,_,r in slots if r]
    cs={c['caso_id']:c for c in carregar(ROOT/'data/desenvolvimento')}
    oldpath=ROOT/'data/desenvolvimento/projeto_minimo_v1/referencias/gabaritos.json'
    newpath=ROOT/'data/desenvolvimento/ampliacao_v1/referencias/gabaritos.json'
    old=ler(oldpath);views={cid:c['views'] for cid,c in cs.items()}
    versoes={s['condicao']:s['versao_projeto'] for s in m['execucoes'] if s['caso_id']==old['casos'][0]['caso_id']}
    refs=preparar_referencias(old,views,versoes)
    for g in ler(newpath)['casos']:
        verdade={}
        for d,k in [('prazo','delta_dias'),('custo','delta_centavos')]:
            q=g[k];v={a:q[a] for a in ('estado','valor','direcao')};v['unidade']='dia_corrido' if d=='prazo' else 'BRL_centavo'
            if q.get('limites') and q['estado']=='indeterminado':
                v['limite_indeterminado_preservado_fora_do_schema_v1']=deepcopy(q['limites'])
                v['nota_projecao']='Avaliador v1 só aceita limite em exato/direcao;verdade continua indeterminada sem MAE e limite original é conservado separadamente'
            if q.get('limites') and q['estado']!='indeterminado':
                v['limites']={**q['limites'],'unidade':v['unidade'],'grandeza':'delta','proveniencia':dict(tipo='transcricao_autoral_derivacao',referencia_origem_hash=hash_json(g),derivacao=g['derivacao_manual'],fonte_ids=g['fontes'])}
            verdade[d]=v
        por={c:{d:dict(estado='pendente',valor=None,direcao='desconhecida',unidade=v['unidade'],view_hash=views[g['caso_id']][c]['view_hash'],status='inferibilidade_pendente_autoria_sem_independencia',derivacao='Referência nova conserva inferibilidade pendente; não inferir suporte do acerto numérico') for d,v in verdade.items()} for c in 'BHT'}
        for versao in sorted({s['versao_projeto'] for s in m['execucoes'] if s['caso_id']==g['caso_id']}):
            refs.append(dict(caso_id=g['caso_id'],versao_projeto=versao,verdade=verdade,por_view=por,referencia_origem_hash=hash_json(g),revisores=[],status='autoral_sem_validacao_independente'))
    salvar(OUT/'referencias_avaliacao_autoral.json',refs)
    normal=normalizar(m,regs);rel=avaliar(m,regs,refs,auditorias=[])
    salvar(OUT/'normalizacao.json',normal);salvar(OUT/'avaliacao_autoral.json',rel)
    erros=[];operacionais=[]
    for reg in regs:
        s,r=reg['metadados'],reg['resultado']
        locais=[]
        for t in r.get('rastro_orquestracao',[]):
            for e in t.get('analise',{}).get('execucao',{}).get('erros',[]):locais.append(e)
        es=r.get('execucao',{}).get('erros',[])+locais
        if es or r.get('execucao',{}).get('estado')=='erro':operacionais.append(s['execucao_id'])
        if es:erros.append(dict(execucao_id=s['execucao_id'],condicao=s['condicao'],erros=es))
    chamadas=[];custo=0;comp=0;tokens_i=tokens_o=0
    for row in db.execute('SELECT id,slot,estado,comprometido,contado,custo_inferencia,uso,registro,contagem_iniciada,inferencia_iniciada FROM chamadas WHERE id>15 ORDER BY id'):
        id,slot,estado,comprometido,contado,ci,u,registro,ct,it=row
        raw=json.loads(registro) if registro else{};uso=json.loads(u) if u else None
        item=dict(id=id,slot=slot,estado=estado,comprometido_nanoUSD=comprometido,contagem_oficial=contado,custo_inferencia_nanoUSD=ci,contagem_HTTP_marcada=ct,inferencia_HTTP_marcada=it,erro=raw.get('erro'),falha_transporte=raw.get('falha_transporte'),protocolo_provider=raw.get('protocolo_provider'),modelo_observado=raw.get('modelo_observado'))
        if uso:
            # Contraprova aritmética independente, com Fraction e preços publicados.
            a=uso['input_tokens_details'];w=a.get('cache_write_tokens_details',dict(ttl_30m_tokens=a['cache_write_tokens'],ttl_12h_tokens=0))
            valor=(Fraction(uso['input_tokens']-a['cached_tokens']-a['cache_write_tokens'])*Fraction('0.10')+Fraction(a['cached_tokens'])*Fraction('0.01')+Fraction(w['ttl_30m_tokens'])*Fraction('0.125')+Fraction(w['ttl_12h_tokens'])*Fraction('0.25')+Fraction(uso['output_tokens'])*Fraction('0.50'))/1000000
            if valor*10**9!=ci:raise ValueError('Divergência de conciliação independente')
            custo+=ci;tokens_i+=uso['input_tokens'];tokens_o+=uso['output_tokens']
        comp+=comprometido;chamadas.append(item)
    paradas=[x[0] for x in db.execute('SELECT motivo FROM parada_v04')]
    por={}
    for c in 'BHT':
        rs=[r for r in regs if r['metadados']['condicao']==c]
        por[c]=dict(N_planejado=30,N_registros=len(rs),N_nao_iniciados=sum(db.execute('SELECT estado FROM slots_v04 WHERE id=?',(s['execucao_id'],)).fetchone()[0]=='pendente' for s in m['execucoes'] if s['condicao']==c),N_iniciados_sem_resultado=sum(db.execute('SELECT estado FROM slots_v04 WHERE id=?',(s['execucao_id'],)).fetchone()[0]=='iniciado' for s in m['execucoes'] if s['condicao']==c),estados_execucao=dict(Counter(r['resultado']['execucao']['estado'] for r in rs)),slots_com_falha_operacional=sum(r['metadados']['execucao_id'] in operacionais for r in rs))
    # Validação independente dos denominadores e MAE já computados pelo avaliador.
    for c in 'BHT':
        for d,k in [('prazo','delta_dias'),('custo','delta_centavos')]:
            metric=rel['metricas'][c+':'+d]
            ls=[l for l in normal['linhas'] if l['slot']['condicao']==c]
            if len(ls)!=metric['N'] or metric['N']!=30:raise ValueError('N divergente')
            if sum(l['desfechos'][d]['classe']=='exato' for l in ls)!=metric['cobertura_numerica']['n']:raise ValueError('Cobertura divergente')
            refmap={(r['caso_id'],r['versao_projeto']):r for r in refs};es=[]
            for l in ls:
                q=l['desfechos'][d];g=refmap[(l['slot']['caso_id'],l['slot']['versao_projeto'])]['verdade'][d]
                if q['classe']==g['estado']=='exato':es.append(abs(q['quantidade']['valor']-g['valor']))
            if len(es)!=metric['erro_numerico']['n'] or (sum(es)/len(es) if es else None)!=metric['erro_numerico']['MAE']:raise ValueError('MAE divergente')
    salvar(OUT/'contabilidade_e_erros.json',dict(lote_id=plano['lote_id'],rotulo_chave_informado_usuario='TCC-Impacto-Baseline',nome_da_chave_nao_inferido_da_credencial=True,outra_chave_reservada_pelo_usuario='TCC-Impacto-Grafo-LLM-por-no;nao_adicionada',por_condicao=por,paradas=paradas,chamadas=chamadas,erros=erros,
        inferencias_HTTP_marcadas=sum(x['inferencia_HTTP_marcada'] for x in chamadas),contagens_HTTP_marcadas=sum(x['contagem_HTTP_marcada'] for x in chamadas),
        uso_conciliado=dict(tokens_entrada=tokens_i,tokens_saida_total=tokens_o,custo_inferencia_nanoUSD=custo,custo_inferencia_USD=str(Decimal(custo)/Decimal(10**9))),
        comprometido_nanoUSD=comp,saldo_livre_interno_nanoUSD=5*10**9-comp-172820515,comprometido_global_nanoUSD=comp+172820515,comprometido_anterior_preservado_nanoUSD=172820515,provisao_contagem_hipotetica_nanoUSD=len(chamadas)*2000000,
        reservas_nao_conciliadas_nanoUSD=sum(x['comprometido_nanoUSD'] for x in chamadas if x['estado']!='conciliado'),
        custos_desconhecidos=sum(x['estado']!='conciliado' for x in chamadas),cobranca_real_provedor='nao_confirmada_por_fatura',
        validacao_independente_aritmetica=True,independencia_cientifica=False,metadados_artefatos=dict(manifesto_sha256=hashlib.sha256((OUT/'manifesto.json').read_bytes()).hexdigest(),referencia_iris_sha256=hashlib.sha256(oldpath.read_bytes()).hexdigest(),referencia_nacar_sha256=hashlib.sha256(newpath.read_bytes()).hexdigest())))
    db.close()
    print(json.dumps(dict(N=90,condicoes=por,paradas=paradas,chamadas=len(chamadas),comprometido_nanoUSD=comp,custo_inferencia_conciliada_nanoUSD=custo),ensure_ascii=False))
if __name__=='__main__':main()
