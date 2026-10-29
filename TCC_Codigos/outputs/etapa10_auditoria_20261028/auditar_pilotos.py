"""Auditoria offline independente das agregações: lê registros brutos, não avaliador.

Referências autorais servem apenas para a primeira reconciliação. A derivação
cega é confrontada em um passo separado, após o selo do revisor.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import sqlite3
import statistics

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def ler(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def coorte(pasta):
    manifesto = ler(pasta / 'manifesto.json')
    refs = ler(pasta / 'referencias_avaliacao_autoral.json')
    por_ref = {(r['caso_id'], r['versao_projeto']): r for r in refs}
    exigir(len(refs) == len(por_ref), 'Referências duplicadas')
    normal = {r['slot']['execucao_id']: r for r in ler(pasta / 'normalizacao.json')['linhas']}
    exigir(len(normal) == 90, 'N da normalização')
    linhas, fontes = [], {}
    for s in manifesto['execucoes']:
        arquivo = pasta / (s['execucao_id'] + '.json')
        bruto = ler(arquivo)
        exigir(bruto['metadados'] == s, 'Identidade bruta divergente')
        fontes[str(arquivo.relative_to(ROOT))] = sha(arquivo)
        r = bruto['resultado']
        ref = por_ref[(s['caso_id'], s['versao_projeto'])]['verdade']
        dims = {}
        for dim, campo in [('prazo', 'delta_dias'), ('custo', 'delta_centavos')]:
            q = r.get(campo, {})
            classe = 'invalido' if r['execucao']['estado'] == 'erro' else q['estado']
            exigir(classe == normal[s['execucao_id']]['desfechos'][dim]['classe'], 'Classe normalizada divergente')
            if classe == 'exato':
                exigir(type(q['valor']) is int, 'Valor exato não inteiro')
                exigir(q['valor'] == normal[s['execucao_id']]['desfechos'][dim]['quantidade']['valor'], 'Valor normalizado divergente')
            elegivel = classe == ref[dim]['estado'] == 'exato'
            erro = abs(q['valor'] - ref[dim]['valor']) if elegivel else None
            dims[dim] = dict(classe=classe, valor=q.get('valor'), direcao=q.get('direcao'),
                             referencia=ref[dim], erro_absoluto=erro)
        linhas.append(dict(slot=s, estado=r['execucao']['estado'], dimensoes=dims,
                           latencia_s=r['tempo_slot_s']))
    exigir(len(linhas) == 90, 'Coorte incompleta')
    exigir(len({(r['slot']['caso_id'],r['slot']['condicao'],r['slot']['repeticao']) for r in linhas}) == 90,
           'Slot duplicado')
    resumo = {}
    for cond in 'BHT':
        subset = [r for r in linhas if r['slot']['condicao'] == cond]
        exigir(len(subset) == 30, 'Condição incompleta')
        resumo[cond] = dict(N=30, estados=dict(Counter(r['estado'] for r in subset)),
                            latencia_mediana_s=statistics.median(r['latencia_s'] for r in subset), dimensoes={})
        for dim in ('prazo','custo'):
            erros = [r['dimensoes'][dim]['erro_absoluto'] for r in subset if r['dimensoes'][dim]['erro_absoluto'] is not None]
            resumo[cond]['dimensoes'][dim] = dict(
                classes=dict(Counter(r['dimensoes'][dim]['classe'] for r in subset)),
                n_pares_exatos=len(erros), soma_erros=sum(erros),
                mae_fracao=str(Fraction(sum(erros), len(erros))) if erros else None,
                acertos_exatos=sum(e == 0 for e in erros),
                erros=[dict(caso_id=r['slot']['caso_id'],repeticao=r['slot']['repeticao'],**r['dimensoes'][dim])
                       for r in subset if r['dimensoes'][dim]['erro_absoluto'] not in (None,0)])
    return dict(resumo=resumo,linhas=linhas,fontes_sha256=fontes)


def main():
    pastas={v:OUT.parent / nome for v,nome in [('v6','etapa9_piloto_v06_20261027'),('v7','etapa9_piloto_v07_r3_20261028')]}
    resultados={v:coorte(p) for v,p in pastas.items()}
    campos=['caso_id','repeticao','condicao','projeto_id','evento_id','versao_projeto','view_hash','snapshot_hash','evento_hash','modelo','config_hash','origem']
    for antes,depois in zip(resultados['v6']['linhas'],resultados['v7']['linhas']):
        exigir(all(antes['slot'][c] == depois['slot'][c] for c in campos), 'Pareamento divergente')
    comparacao=ler(pastas['v7']/'comparacao_v06_v07.json')['comparacao']
    for cond in 'BHT':
        for versao,chave in [('v6','v06'),('v7','v07')]:
            resum=resultados[versao]['resumo'][cond]
            exigir(resum['latencia_mediana_s'] == comparacao[cond]['latencia_mediana_slot_'+chave+'_s'], 'Latência divergente')
            for dim in ['prazo','custo']:
                audit=resum['dimensoes'][dim];anterior=comparacao[cond]['desfechos'][dim]
                exigir(audit['classes'].get('exato',0)==anterior['cobertura_'+chave]['n'],'Cobertura divergente')
                exigir(audit['n_pares_exatos']==anterior['erro_'+chave]['n'],'Denominador MAE divergente')
                if audit['mae_fracao'] is not None:
                    exigir(abs(float(Fraction(audit['mae_fracao']))-anterior['erro_'+chave]['MAE'])<1e-9,'MAE divergente')
    db=OUT/'ledger_antes.sqlite'
    with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True) as con:
        n,comprometido,inferencia=con.execute('select count(*),sum(comprometido),sum(custo_inferencia) from chamadas').fetchone()
        desconhecidas=con.execute('select count(*),sum(comprometido) from chamadas where custo_inferencia is null').fetchone()
        incremento=con.execute('select count(*),sum(comprometido),sum(custo_inferencia) from chamadas where id>834').fetchone()
        exigir((n,comprometido)==(1114,4480425665),'Carteira mudou antes da auditoria')
        exigir(incremento==(280,1002764765,442764765),'Custo incremental divergente')
    saida=dict(natureza='Recomputação offline por implementação separada, sem importar avaliador/motor; referências autorais ainda confrontadas separadamente',
               pareamento=dict(slots=90,campos=campos,ordem_igual=True),coortes=resultados,
               carteira=dict(tentativas=n,comprometido_nanoUSD=comprometido,inferencia_conhecida_nanoUSD=inferencia,
                             reservas_desconhecidas=desconhecidas,saldo_nanoUSD=5000000000-comprometido,
                             novas_chamadas_etapa10=0,nota='Compromisso com provisões; não equivale à fatura'),
               conclusao='Agregações, denominadores e pareamento publicados reproduzidos sem divergências')
    (OUT/'auditoria_metricas.json').write_text(json.dumps(saida,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(conclusao=saida['conclusao'],carteira=saida['carteira'],resumos={v:r['resumo'] for v,r in resultados.items()}),ensure_ascii=False))


if __name__=='__main__':
    main()
