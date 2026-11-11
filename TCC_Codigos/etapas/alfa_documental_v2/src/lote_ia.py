"""Preparação offline e executor de lote autorizado separadamente, sem retries.

Um manifesto congela D01–D09, código, fontes e tetos. Preparar não lê credencial,
não abre carteira para escrita e não chama API. A coleta exige autorização futura.
"""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import stat
import uuid

from . import ROOT, DATA
from .ia_real import TransporteReal, Sugestor, MODELO, CONFIG
from .pipeline import ler_cenario
from .sessoes import Sessoes, gravar
from .vendor.hibrido_v07_r3.adaptador import LocalV07R3
from .vendor.interpretacao_no.contratos import exigir, hash_json
from .auditoria import auditar_arquivo, TransporteRevisaoReal
from .revisao import RevisorIA

CENARIOS = tuple(f'D{i:02}' for i in range(1, 10))
REPO = ROOT.parents[2]
HISTORICO = REPO/'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
LEDGER = ROOT/'outputs/consumo_ia_real.sqlite'
PILOTO = ROOT/'outputs/ia_real_20261110T050151Z/resultado.json'
REFERENCIA = ROOT/'avaliacao/equivalencia_v1.json'
CREDENCIAL = REPO/'.env.piloto'
VERSAO = '1-lote-desenvolvimento-observacional'


def agora():
    return datetime.now(timezone.utc).isoformat()


def protocolo():
    return dict(versao=VERSAO, cenarios=list(CENARIOS), particao='dev', repeticoes=1,
                modelo=MODELO, configuracao=deepcopy(CONFIG), nos='todos',
                selecao='sugestao_ia_sem_ambiguidade_igual_as_mencoes_cadastradas',
                revisor='observacao_separada_mesmo_modelo',
                preflight_alvo='release_M_PROTO_READY',
                teto_total_nano=20_000_000_000, teto_lote_nano=14_325_000_000,
                limites_coleta=dict(max_solicitacoes=65, max_custo_centavos=99,
                    max_tokens_entrada=4160000, max_tokens_saida=1040000, max_segundos=28800),
                limites_revisao=dict(max_solicitacoes=40, max_custo_centavos=60,
                    max_tokens_entrada=2560000, max_tokens_saida=640000, max_segundos=18000),
                limites_preflight=dict(max_solicitacoes=1, max_custo_centavos=1.5,
                    max_tokens_entrada=64000, max_tokens_saida=16000, max_segundos=600),
                precos_estimativa_usd_milhao=dict(entrada=.1, cache=.01, saida=.5),
                reserva_por_tentativa_nano=15_000_000,
                parada='falha_tecnica_ambiguidade_limite_ou_uso_desconhecido',
                retries=False, retomada_automatica=False,
                autorizacao_coleta=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def arquivos_congelados():
    # Não abre simulações ou casos finais; referências autorais só são lidas
    # pelo avaliador após persistir todas as previsões e revisões.
    arquivos = list((ROOT/'src').rglob('*.py')) + [ROOT/'__init__.py', ROOT/'__main__.py',
        DATA/'grafo.json', DATA/'documentos.json', PILOTO, REFERENCIA]
    arquivos += [DATA/'cenarios/dev'/f'{cid}.json' for cid in CENARIOS]
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(arquivos)}


def comprometido(path, *, obrigatorio=True):
    path = Path(path)
    if not path.exists():
        exigir(not obrigatorio, 'Ledger histórico ausente; não presumir saldo zero')
        return 0
    with sqlite3.connect(path.resolve().as_uri()+'?mode=ro', uri=True) as db:
        return db.execute('SELECT coalesce(sum(comprometido),0) FROM chamadas').fetchone()[0]


def preparar_lote(destino):
    destino = Path(destino)
    antigo = comprometido(HISTORICO)
    atual = comprometido(LEDGER)
    p = protocolo()
    exigir(antigo+atual+p['teto_lote_nano'] <= p['teto_total_nano'], 'Saldo não comporta os tetos do lote')
    cenarios = [ler_cenario(cid) for cid in CENARIOS]
    exigir(all(c['id'] == cid and c['particao'] == 'dev' for cid,c in zip(CENARIOS,cenarios)), 'Cenário fora do protocolo')
    m = dict(lote_id='lote-'+uuid.uuid4().hex, preparado_em=agora(),
             estado='aguardando_autorizacao', protocolo=p,
             cenarios=[dict(id=c['id'], titulo=c['titulo'], mencoes=c['entidades_mencionadas']) for c in cenarios],
             hashes=arquivos_congelados(), historico_externo_sha256=sha(HISTORICO),
             financeiro=dict(historico_externo_nano=antigo, carteira_v2_nano=atual,
                             comprometido_preparo_nano=antigo+atual,
                             margem_total_nano=p['teto_total_nano']-antigo-atual),
             natureza='Preparação offline; não autoriza chamadas nem valida desempenho de IA')
    m['manifesto_hash'] = hash_json(m)
    destino.mkdir(parents=True, exist_ok=False)
    gravar(destino/'manifesto.json', m)
    return m


def validar_manifesto(m):
    exigir(m['manifesto_hash'] == hash_json({k:v for k,v in m.items() if k!='manifesto_hash'}), 'Manifesto adulterado')
    exigir(m['protocolo'] == protocolo(), 'Protocolo mudou; preparar novo lote')
    exigir(m['estado'] == 'aguardando_autorizacao', 'Manifesto inválido')
    exigir(m['hashes'] == arquivos_congelados(), 'Código/dados mudaram; preparar novo lote')
    exigir(m['historico_externo_sha256'] == sha(HISTORICO), 'Histórico externo mudou; preparar novo lote')
    exigir(m['financeiro']['historico_externo_nano'] == comprometido(HISTORICO), 'Histórico financeiro divergente')
    exigir(comprometido(HISTORICO)+comprometido(LEDGER)+m['protocolo']['teto_lote_nano'] <= m['protocolo']['teto_total_nano'],
           'Saldo atual não comporta o lote congelado')


def ler_chave():
    # Só chamado pelo executor após autorização explícita e validações offline.
    exigir(not CREDENCIAL.is_symlink() and stat.S_IMODE(CREDENCIAL.stat().st_mode) == 0o600, 'Credencial local requer arquivo regular protegido 0600')
    exigir(CREDENCIAL.is_file(), 'Credencial não é arquivo regular')
    chave = CREDENCIAL.read_text().split('=', 1)[1].strip()
    exigir(bool(chave), 'Credencial ausente')
    return chave


def conferir_selecao(sugestao, cenario):
    ids = [s['no_id'] for s in sugestao['sugestoes']]
    exigir(not sugestao['ambiguidades'] and bool(ids) and len(set(ids)) == len(ids), 'Sugestão ambígua/vazia/duplicada; revisão humana necessária')
    exigir(set(ids) == set(cenario['entidades_mencionadas']), 'Sugestão diverge das menções; sem correção ou nova tentativa automática')
    return ids


def conferir_auditoria(a, *, minimo=0):
    registros = a['registros']
    exigir(len(registros) >= minimo, 'Revisão sem proposta para verificar')
    for r in registros:
        exigir(r.get('pacote') is not None, 'Proposta/vínculo inválido na auditoria')
        revisao = r.get('revisao_semantica') or {}
        exigir(revisao.get('estado') == 'parecer_recebido', 'Revisão incompleta ou inválida; inspecionar auditoria')
    # Um parecer semanticamente desfavorável válido não é falha técnica.


def executar_lote(manifesto, *, autorizar=False, autorizacao='', http=None):
    exigir(autorizar is True and isinstance(autorizacao,str) and bool(autorizacao.strip()),
           'Coleta não autorizada: preparar não autoriza execução; aguarde confirmação do usuário')
    manifesto = Path(manifesto)
    m = json.loads(manifesto.read_text())
    validar_manifesto(m)
    pasta = manifesto.parent
    p = m['protocolo']
    registro = dict(lote_id=m['lote_id'], manifesto_hash=m['manifesto_hash'], estado='em_andamento',
                    autorizacao=autorizacao, inicio=agora(), fase='preflight', preflight=None,
                    cenarios={cid:dict(coleta='nao_executada', revisao='nao_executada') for cid in CENARIOS},
                    transportes={}, erro=None, modo='ia_real' if http is None else 'teste_http_injetado_nao_mede_ia')
    # Exclusividade impede duplo clique, repetição e retomada acidental.
    with (pasta/'execucao.json').open('x',encoding='utf8') as f:
        json.dump(registro,f,ensure_ascii=False,indent=2)
    transportes=[]
    chave=None

    def salvar():
        for etapa, t in transportes:
            registro['transportes'][etapa] = t.snapshot()
        gravar(pasta/'execucao.json',registro)

    def transporte(etapa, limites):
        t=TransporteReal(pasta/'chamadas'/etapa, chave, m['financeiro']['historico_externo_nano'],
            http=http, ledger=LEDGER, rodada=m['lote_id']+':'+etapa,
            teto_total_nano=p['teto_total_nano'], teto_rodada_nano=round(limites['max_custo_centavos']*10_000_000),
            max_chamadas=limites['max_solicitacoes'], grupo=m['lote_id'], teto_grupo_nano=p['teto_lote_nano'])
        transportes.append((etapa,t))
        return t

    def revisor(etapa, limites):
        return RevisorIA(TransporteRevisaoReal(transporte(etapa,limites)),modelo=MODELO,configuracao=CONFIG,modo='ia_real')

    try:
        chave=ler_chave()
        # Testa contrato/serviço em uma proposta existente; não exige parecer
        # favorável e não recalcula nem modifica a coleta anterior.
        antigo=json.loads(PILOTO.read_text())
        passos=[s for s in antigo['rastro_orquestracao'] if any(
            q['alvo_id']==p['preflight_alvo'] for q in s.get('analise',{}).get('propostas',[]))]
        exigir(len(passos)==1 and len(passos[0]['analise']['propostas'])==1, 'Preflight exige exatamente uma proposta histórica')
        entrada=dict(execucao_id=antigo['execucao_id'], rastro_orquestracao=passos,
                     suporte_semantico=antigo.get('suporte_semantico'), origem_sha256=sha(PILOTO))
        gravar(pasta/'preflight_entrada.json',entrada)
        a=auditar_arquivo(pasta/'preflight_entrada.json',pasta/'preflight_auditoria.json',
                         revisor=revisor('preflight',p['limites_preflight']),limites=p['limites_preflight'],parar_em_falha=True)
        registro['preflight']='registrado';salvar()
        conferir_auditoria(a,minimo=1)
        registro['preflight']='concluido'
        for cid in CENARIOS:
            registro['fase']='coleta:'+cid;registro['cenarios'][cid]['coleta']='em_andamento';salvar()
            dest=pasta/cid;dest.mkdir()
            c=ler_cenario(cid);gravar(dest/'evento.json',c)
            t=transporte(cid+'-coleta',p['limites_coleta'])
            manager=Sessoes(dest/'sessoes')
            s=manager.preparar(cid,c['entidades_mencionadas'],'todos',modo='ia_real',cenario=c,limites=p['limites_coleta'])
            try:
                sugestao=manager.sugestao(s['id'],'entrada-unica',Sugestor(t));gravar(dest/'sugestao.json',sugestao)
                ids=conferir_selecao(sugestao,c)
                s=manager.selecionar(s['id'],ids,'todos',origem='ia_autorizada_pelo_usuario')
                gravar(dest/'selecao.json',dict(entradas=ids,regra=p['selecao'],autorizacao=autorizacao))
                adapter=LocalV07R3(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180)
                s=manager.executar(s['id'],adaptador_real=adapter)
            finally:
                s=manager.ler(s['id']);gravar(dest/'sessao.json',s)
                if s.get('resultado') is not None: gravar(dest/'resultado.json',s['resultado'])
                salvar()
            exigir(s['estado']=='concluida' and s['resultado']['execucao']['estado']!='erro'
                   and not s.get('falha_real_bloqueante') and not t.snapshot()['uso_desconhecido'],
                   'Coleta interrompida/parcial; preservar e revisar antes de outra execução')
            registro['cenarios'][cid].update(coleta='concluida', estado_previsao=s['resultado']['execucao']['estado'],
                completude=deepcopy(s['resultado']['completude']))
            salvar()
        # Revisões nunca retroalimentam o proponente ou os resultados salvos.
        for cid in CENARIOS:
            registro['fase']='revisao:'+cid;registro['cenarios'][cid]['revisao']='em_andamento';salvar()
            a=auditar_arquivo(pasta/cid/'resultado.json',pasta/cid/'auditoria.json',
                revisor=revisor(cid+'-revisao',p['limites_revisao']),limites=p['limites_revisao'],parar_em_falha=True)
            conferir_auditoria(a)
            registro['cenarios'][cid]['revisao']='concluida';salvar()
        registro['fase']='avaliacao';salvar()
        # Referência autoral só após persistência de todas as previsões/revisões.
        from .avaliacao import resumo
        refs=json.loads(REFERENCIA.read_text())
        for cid in CENARIOS:
            r=json.loads((pasta/cid/'resultado.json').read_text());got=resumo(r)
            comparacao=dict(equivalente=got==refs[cid],observado=got,referencia=refs[cid],
                           natureza='Referência autoral de desenvolvimento; não revisão independente')
            gravar(pasta/cid/'comparacao.json',comparacao)
            registro['cenarios'][cid]['equivalente_referencia_autoral']=comparacao['equivalente']
        registro['estado']='concluido';registro['fase']='encerrado'
    except BaseException as exc:
        mensagem=str(exc)
        if chave: mensagem=mensagem.replace(chave,'[REDACTED]')
        registro.update(estado='interrompido',erro=dict(tipo=type(exc).__name__,mensagem=mensagem))
        fase=registro['fase'].split(':')
        if len(fase)==2 and fase[0] in ('coleta','revisao'):
            registro['cenarios'][fase[1]][fase[0]]='interrompida'
        if isinstance(exc,(KeyboardInterrupt,SystemExit)):raise
    finally:
        registro['fim']=agora()
        salvar()
        registro['comprometido_total_nano']=comprometido(HISTORICO)+comprometido(LEDGER)
        gravar(pasta/'execucao.json',registro)
        for _, t in transportes:t.db.close()
    return registro


def main():
    parser=argparse.ArgumentParser(description='Lote D01–D09: preparar offline; executar só após autorização')
    sub=parser.add_subparsers(dest='acao',required=True)
    preparar=sub.add_parser('preparar');preparar.add_argument('--destino',required=True)
    rodar=sub.add_parser('executar');rodar.add_argument('manifesto');rodar.add_argument('--autorizar-coleta',action='store_true')
    rodar.add_argument('--autorizacao',default='')
    a=parser.parse_args()
    if a.acao=='preparar':
        m=preparar_lote(a.destino)
        print(json.dumps(dict(estado=m['estado'],manifesto=str(Path(a.destino)/'manifesto.json'),
            teto_total_usd=m['protocolo']['teto_total_nano']/1e9,teto_lote_usd=m['protocolo']['teto_lote_nano']/1e9),ensure_ascii=False))
    else:
        r=executar_lote(a.manifesto,autorizar=a.autorizar_coleta,autorizacao=a.autorizacao)
        print(json.dumps(dict(estado=r['estado'],fase=r['fase'],erro=r['erro']),ensure_ascii=False))
        if r['estado']!='concluido':raise SystemExit(1)


if __name__=='__main__':main()
