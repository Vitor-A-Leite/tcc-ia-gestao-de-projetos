"""Integridade final e congelamento explícito, sempre offline e sem tocar a carteira."""
from pathlib import Path
import argparse,datetime,hashlib,json,sqlite3

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ler(p):return json.loads(p.read_text())
def exigir(c,m):
    if not c:raise ValueError(m)


def main(congelar=False):
    anterior=ler(OUT/'integridade_antes.json')
    permitidos={'TCC_Codigos/docs/desenvolvimento/STATUS.md','TCC_Codigos/docs/desenvolvimento/PLANO_MESTRE.md'}
    mudados=[p for p,h in anterior.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    exigir(set(mudados)<=permitidos,'Arquivo anterior alterado: '+str(set(mudados)-permitidos))
    ledger=ROOT/'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
    with sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True) as c:
        n,comp,inf=c.execute('select count(*),sum(comprometido),sum(custo_inferencia) from chamadas').fetchone()
        desconhecidas=c.execute('select count(*) from chamadas where custo_inferencia is null').fetchone()[0]
        exigir((n,comp,inf,desconhecidas)==(1114,4480425665,2063925665,13),'Carteira divergente')
    codigo=ler(OUT/'codigo_pre_dados_finais.json')['arquivos']
    exigir(all(sha(ROOT/p)==h for p,h in codigo.items()),'Preditor alterado')
    exigir(len(list((ROOT/'TCC_Codigos/src').rglob('*.py')))==len(codigo),'Novo código no preditor')
    exigir(ler(OUT/'reproducao_cega.json')['reproduzido'],'Reprodução desenvolvimento ausente')
    exigir(ler(OUT/'reproducao_final_v2.json')['reproducao_integral_identica'],'Reprodução final ausente')
    exigir(ler(OUT/'preparacao_final_v2/validacao.json')['nenhuma_previsao'],'Previsão final indevida')
    exigir(ler(OUT/'validacao_referencias_finais.json')['confronto_sem_divergencias'],'Confronto pendente')
    exigir(ler(OUT/'contraprovas_avaliador_final.json')['aprovadas'],'Avaliador pendente')
    for p in (OUT/'preparacao_final_v2').glob('*'):
        exigir(p.name in {'manifesto.json','views.json','contextos_iniciais.json','validacao.json'},'Resultado inesperado na preparação')
    maximo_incremental=3*(1+8+1)*16500000
    exigir(comp+maximo_incremental<=5000000000,'Plano excede orçamento')
    freeze=OUT/'congelamento.json'
    if congelar:
        exigir(not freeze.exists(),'Congelamento já existe; não substituir')
        paths=set((ROOT/'TCC_Codigos/src').rglob('*.py'))
        paths.update((ROOT/'TCC_Codigos/data/final').rglob('*'))
        paths.update((ROOT/'TCC_Codigos/docs/desenvolvimento').glob('ETAPA_10*.md'))
        paths.update(OUT.rglob('*'))
        paths.update((ROOT/'outputs/etapa10_auditoria_20261028/revisao_final_cega').glob('*'))
        paths={p for p in paths if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'
               and p.name not in ('congelamento.json','verificacao_final.json')}
        dados=dict(versao='2.0-congelamento-etapa10',data_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            natureza='Pré-coleta: código/prompt/configuração, fontes, gabaritos, protocolo e auditoria; revisão técnica, sem parecer humano',
            artefatos={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)},
            carteirabase=dict(tentativas=n,comprometido_nanoUSD=comp),
            codigo_congelado_pre_dados_finais=True,nenhuma_previsao_final=True,
            limite='Runner pago final ainda será integrado na etapa 11; qualquer novo artefato de execução exige vinculação a este congelamento antes de envio.')
        with freeze.open('x') as f:json.dump(dados,f,ensure_ascii=False,indent=2);f.write('\n')
    exigir(freeze.is_file(),'Congelamento ausente')
    frozen=ler(freeze)
    for p,h in frozen['artefatos'].items():exigir((ROOT/p).is_file() and sha(ROOT/p)==h,'Congelamento divergente: '+p)
    res=dict(aceite_tecnico=True,criterios_tecnicos_atendidos=6,parecer_humano=False,
        arquivos_anteriores_inventariados=len(anterior),mudancas_permitidas=mudados,alteracoes_indevidas=[],
        arquivos_congelados=len(frozen['artefatos']),codigo_preditor_preservado=len(codigo),
        congelamento_sha256=sha(freeze),carteira=dict(tentativas=n,comprometido_nanoUSD=comp,
        inferencia_conhecida_nanoUSD=inf,reservas_desconhecidas=desconhecidas,saldo_nanoUSD=5000000000-comp,
        chamadas_novas=0),plano_futuro=dict(slots=9,max_tentativas=30,max_incremental_nanoUSD=maximo_incremental,
        max_acumulado_nanoUSD=comp+maximo_incremental),etapa11_iniciada=False)
    (OUT/'verificacao_final.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(res,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--congelar',action='store_true')
    main(parser.parse_args().congelar)
