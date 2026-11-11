"""Recuperação explícita e única de D04, sem alterar o runtime congelado.

Reutiliza respostas pelo contexto exato. A reserva inconciliada continua no
ledger e nos tetos; a autorização libera apenas uma nova tentativa do nó que
falhou. Qualquer nova falha interrompe a continuação, sem retry automático.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile

from ..src import lote_ia as lote
from ..src.ia_real import TransporteReal, Sugestor, MODELO, CONFIG
from ..src.sessoes import Sessoes, gravar
from ..src.vendor.hibrido_v07_r3.adaptador import LocalV07R3
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json
from ..src.auditoria import auditar_arquivo, TransporteRevisaoReal
from ..src.revisao import RevisorIA


def ler(path):
    return json.loads(Path(path).read_text())


def hashes_originais(pasta):
    return {str(p.relative_to(pasta)): lote.sha(p)
            for p in sorted(pasta.rglob('*.json'))}


def copiar_checkpoint(original, autorizacao):
    exigir(bool(autorizacao.strip()), 'Retomada exige autorização explícita')
    exigir(original['cenario_id'] == 'D04' and original['estado'] == 'pausada'
           and original.get('falha_real_bloqueante') and not original.get('em_voo'),
           'Checkpoint não corresponde à interrupção de D04')
    erros = [(h, a) for h, a in original['cache'].items() if a['execucao']['estado'] != 'ok']
    exigir(len(erros) == 1 and erros[0][1]['no_id'] == 'TEST_THERMAL'
           and erros[0][1]['execucao']['erros'][0]['codigo'] == 'rede'
           and original['pendentes'][0] == 'TEST_THERMAL', 'Falha diferente da autorizada')
    s = deepcopy(original)
    h, falha = erros[0]
    s['retomada'] = dict(autorizacao=autorizacao, origem_checkpoint_hash=hash_json(original),
        falha_original=deepcopy(falha), consumo_anterior=deepcopy(original['consumo']),
        reserva_anterior_mantida=True,
        escopo_uso_desconhecido_durante_execucao='Somente novas chamadas; uso anterior permanece pendente no ledger e em consumo_anterior')
    del s['cache'][h]  # Somente a resposta de erro; original permanece intacto.
    s['falha_real_bloqueante'] = False
    s['consumo']['uso_desconhecido_anterior'] = bool(s['consumo'].get('uso_desconhecido'))
    s['consumo']['uso_desconhecido'] = False
    return s, falha


def restaurar_incerteza_financeira(s):
    s['retomada']['novo_uso_desconhecido'] = bool(s['consumo'].get('uso_desconhecido'))
    s['consumo']['uso_desconhecido'] = bool(s['consumo'].get('uso_desconhecido')
                                         or s['consumo'].get('uso_desconhecido_anterior'))
    if s.get('resultado'):
        s['resultado']['consumo_acumulado'] = deepcopy(s['consumo'])
        s['resultado']['retomada'] = deepcopy(s['retomada'])


class BarreiraRetomada:
    """Bloqueia reenvio de respostas válidas antes de reservar ou chamar API."""
    def configurar_barreira(self, s, falha):
        self.permitidos = set(s['pendentes'])
        self.falha = falha
        self.novos = []

    def conferir(self, req):
        c = json.loads(req['mensagens'][1]['conteudo'])['contexto']
        exigir(c['no_id'] in self.permitidos and c['no_id'] not in self.novos,
               'Retomada tentou repetir nó válido ou nova tentativa')
        if not self.novos:
            exigir(c['no_id'] == 'TEST_THERMAL' and c['contexto_hash'] == self.falha['contexto_hash']
                   and hash_json(req) == self.falha['execucao']['requisicao_adaptador_hash'],
                   'Primeira chamada não reproduz o pedido original que falhou')
        self.novos.append(c['no_id'])


class TransporteRetomada(BarreiraRetomada, TransporteReal):
    def __call__(self, req):
        self.conferir(req)
        return super().__call__(req)


class ProbeConcluido(BaseException):
    pass


class Probe(BarreiraRetomada):
    origem = 'openai_real'
    versao_formato_local = TransporteReal.versao_formato_local

    def snapshot(self):
        return dict(chamadas_api=0, tokens_entrada=0, tokens_saida=0,
                    custo_api_usd=0, segundos=0, uso_desconhecido=False, comprometido_usd=0)

    def __call__(self, req):
        self.conferir(req)
        raise ProbeConcluido()  # Interrompe antes de qualquer HTTP/credencial/ledger.


def verificar_reuso(s, falha):
    with tempfile.TemporaryDirectory(prefix='tcc-probe-retomada-') as tmp:
        manager = Sessoes(Path(tmp))
        manager.salvar(s)
        t = Probe(); t.configurar_barreira(s, falha)
        try:
            manager.executar(s['id'], selecionados=s['pendentes'],
                adaptador_real=LocalV07R3(t, modelo=MODELO, configuracao=CONFIG, timeout_s=180))
        except ProbeConcluido:
            return dict(primeiro_no=t.novos[0], pedido_original_identico=True,
                        respostas_validas_preservadas=len(s['cache']), chamadas_api=0)
        raise ValueError('Probe não chegou ao ponto de retomada; contexto/cache divergente')


def validar_origem(manifesto, autorizacao):
    m = ler(manifesto); lote.validar_manifesto(m)
    pasta = Path(manifesto).parent
    registro = ler(pasta/'execucao.json')
    exigir(registro['estado'] == 'interrompido' and registro['fase'] == 'coleta:D04'
           and registro['preflight'] == 'concluido', 'Execução de origem incompatível')
    for cid, r in registro['cenarios'].items():
        esperado = 'concluida' if cid < 'D04' else 'interrompida' if cid == 'D04' else 'nao_executada'
        exigir(r['coleta'] == esperado and r['revisao'] == 'nao_executada', 'Fases divergentes')
    original = ler(pasta/'D04/sessao.json')
    exigir(original == ler(pasta/'D04/sessoes'/f"{original['id']}.json"), 'Checkpoints divergem')
    s, falha = copiar_checkpoint(original, autorizacao)
    with sqlite3.connect(lote.LEDGER.resolve().as_uri()+'?mode=ro', uri=True) as db:
        rows = db.execute('SELECT id,estado,comprometido FROM chamadas WHERE rodada=?',
                          (m['lote_id']+':D04-coleta',)).fetchall()
        prefixo = m['lote_id']+':retomada-D04:'
        exigir(db.execute('SELECT count(*) FROM chamadas WHERE substr(rodada,1,?)=?',
                          (len(prefixo), prefixo)).fetchone()[0] == 0,
               'Continuação já tentou chamadas; não repetir automaticamente')
    reservas = [r for r in rows if r[1] != 'conciliada']
    exigir(len(rows) == original['consumo']['chamadas_api'] and len(reservas) == 1
           and reservas[0][2] == m['protocolo']['reserva_por_tentativa_nano'],
           'Carteira não corresponde à interrupção')
    comprometido = sum(r[2] for r in rows)
    exigir(comprometido == round(original['consumo']['comprometido_api_usd']*1e9), 'Consumo divergente')
    probe = verificar_reuso(s, falha)
    return m, registro, s, falha, dict(probe=probe, reservas_pendentes=reservas,
        comprometido_d04_anterior_nano=comprometido, chamadas_d04_anteriores=len(rows))


def executar(manifesto, destino, autorizacao, *, autorizar=False):
    exigir(autorizar is True, 'Execução paga exige autorização')
    manifesto = Path(manifesto).resolve(); destino = Path(destino).resolve()
    m, antigo, s, falha, verificacao = validar_origem(manifesto, autorizacao)
    origem = manifesto.parent; p = m['protocolo']
    exigir(not destino.is_relative_to(origem), 'Destino deve ser separado da coleta original')
    destino.mkdir(parents=True, exist_ok=False)
    # Trava persistente também impede dois executores simultâneos com destinos distintos.
    with (origem.parent/(m['lote_id']+'-retomada-D04.json')).open('x') as claim:
        json.dump(dict(destino=str(destino), autorizacao=autorizacao), claim, ensure_ascii=False)
    adendo = dict(origem=str(manifesto), manifesto_hash=m['manifesto_hash'],
        autorizado_em=lote.agora(), autorizacao=autorizacao, hashes_originais=hashes_originais(origem),
        executor_sha256=lote.sha(__file__), protocolo=p, verificacao=verificacao,
        alteracao='Uma continuação explicitamente autorizada; sem repetir respostas válidas ou preflight; sem retries automáticos')
    gravar(destino/'adendo.json', adendo)
    r = dict(lote_id=m['lote_id'], adendo_hash=hash_json(adendo), estado='em_andamento',
             inicio=lote.agora(), fase='coleta:D04', erro=None, cenarios=deepcopy(antigo['cenarios']),
             preflight_original=str(origem/'preflight_auditoria.json'), transportes={})
    transportes = []
    fontes = {cid: (origem if cid < 'D04' else destino)/cid/'resultado.json' for cid in lote.CENARIOS}
    r['resultados'] = {cid: str(path) for cid, path in fontes.items()}
    chave = None

    def salvar():
        r['transportes'] = {etapa: t.snapshot() for etapa, t in transportes}
        r['comprometido_total_nano'] = lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER)
        gravar(destino/'execucao.json', r)

    def transporte(etapa, limites, *, retomada=False):
        gasto = verificacao['comprometido_d04_anterior_nano'] if retomada else 0
        chamadas = verificacao['chamadas_d04_anteriores'] if retomada else 0
        cls = TransporteRetomada if retomada else TransporteReal
        t = cls(destino/'chamadas'/etapa, chave, m['financeiro']['historico_externo_nano'],
            ledger=lote.LEDGER, rodada=m['lote_id']+':retomada-D04:'+etapa,
            teto_total_nano=p['teto_total_nano'],
            teto_rodada_nano=round(limites['max_custo_centavos']*10_000_000)-gasto,
            max_chamadas=limites['max_solicitacoes']-chamadas,
            grupo=m['lote_id'], teto_grupo_nano=p['teto_lote_nano'])
        transportes.append((etapa, t))
        if retomada: t.configurar_barreira(s, falha)
        return t

    def persistir(manager, sid, dest, *, retomada=False):
        final = manager.ler(sid)
        if retomada:
            restaurar_incerteza_financeira(final)
            manager.salvar(final)
        gravar(dest/'sessao.json', final)
        if final.get('resultado') is not None: gravar(dest/'resultado.json', final['resultado'])
        salvar()
        return final

    try:
        salvar(); chave = lote.ler_chave()
        for cid in lote.CENARIOS[3:]:
            r['fase'] = 'coleta:'+cid; r['cenarios'][cid]['coleta'] = 'em_andamento'; salvar()
            dest = destino/cid; dest.mkdir()
            manager = Sessoes(dest/'sessoes')
            if cid == 'D04':
                manager.salvar(s)
                gravar(dest/'checkpoint_entrada.json', s)
                t = transporte(cid+'-coleta', p['limites_coleta'], retomada=True)
                try:
                    s = manager.executar(s['id'], selecionados=s['pendentes'],
                        adaptador_real=LocalV07R3(t, modelo=MODELO, configuracao=CONFIG, timeout_s=180))
                finally:
                    s = persistir(manager, s['id'], dest, retomada=True)
                exigir(all(s['cache'].get(h) == a for h, a in ler(origem/'D04/sessao.json')['cache'].items()
                           if a['execucao']['estado'] == 'ok'), 'Respostas válidas não foram preservadas')
            else:
                c = lote.ler_cenario(cid); gravar(dest/'evento.json', c)
                t = transporte(cid+'-coleta', p['limites_coleta'])
                s = manager.preparar(cid, c['entidades_mencionadas'], 'todos', modo='ia_real',
                                     cenario=c, limites=p['limites_coleta'])
                try:
                    sugestao = manager.sugestao(s['id'], 'entrada-unica', Sugestor(t))
                    gravar(dest/'sugestao.json', sugestao)
                    ids = lote.conferir_selecao(sugestao, c)
                    s = manager.selecionar(s['id'], ids, 'todos', origem='ia_autorizada_pelo_usuario')
                    gravar(dest/'selecao.json', dict(entradas=ids, regra=p['selecao'], autorizacao=autorizacao))
                    s = manager.executar(s['id'], adaptador_real=LocalV07R3(t, modelo=MODELO, configuracao=CONFIG, timeout_s=180))
                finally:
                    s = persistir(manager, s['id'], dest)
            exigir(s['estado'] == 'concluida' and s['resultado']['execucao']['estado'] != 'erro'
                   and not s.get('falha_real_bloqueante') and not t.snapshot()['uso_desconhecido'],
                   'Nova falha ou coleta incompleta; continuação interrompida, sem retry')
            r['cenarios'][cid].update(coleta='concluida', estado_previsao=s['resultado']['execucao']['estado'],
                                     completude=deepcopy(s['resultado']['completude']))
            salvar()
        for cid in lote.CENARIOS:
            r['fase'] = 'revisao:'+cid; r['cenarios'][cid]['revisao'] = 'em_andamento'; salvar()
            t = transporte(cid+'-revisao', p['limites_revisao'])
            revisor = RevisorIA(TransporteRevisaoReal(t), modelo=MODELO, configuracao=CONFIG, modo='ia_real')
            a = auditar_arquivo(fontes[cid], destino/cid/'auditoria.json', revisor=revisor,
                                limites=p['limites_revisao'], parar_em_falha=True)
            lote.conferir_auditoria(a)
            r['cenarios'][cid]['revisao'] = 'concluida'; salvar()
        r['fase'] = 'avaliacao'; salvar()
        from ..src.avaliacao import resumo
        refs = ler(lote.REFERENCIA)
        for cid in lote.CENARIOS:
            got = resumo(ler(fontes[cid]))
            comparacao = dict(equivalente=got == refs[cid], observado=got, referencia=refs[cid],
                             natureza='Referência autoral de desenvolvimento; não revisão independente')
            gravar(destino/cid/'comparacao.json', comparacao)
            r['cenarios'][cid]['equivalente_referencia_autoral'] = comparacao['equivalente']
        exigir(hashes_originais(origem) == adendo['hashes_originais'], 'Artefatos originais mudaram')
        r.update(estado='concluido', fase='encerrado', originais_preservados=True)
    except BaseException as exc:
        mensagem = str(exc).replace(chave, '[REDACTED]') if chave else str(exc)
        r.update(estado='interrompido', erro=dict(tipo=type(exc).__name__, mensagem=mensagem))
        fase = r['fase'].split(':')
        if len(fase) == 2 and fase[0] in ('coleta', 'revisao'):
            r['cenarios'][fase[1]][fase[0]] = 'interrompida'
        if isinstance(exc, (KeyboardInterrupt, SystemExit)): raise
    finally:
        r['fim'] = lote.agora()
        r['originais_preservados'] = hashes_originais(origem) == adendo['hashes_originais']
        salvar()
        for _, t in transportes: t.db.close()
    return r


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifesto'); parser.add_argument('--destino')
    parser.add_argument('--autorizacao', required=True)
    parser.add_argument('--autorizar-coleta', action='store_true')
    args = parser.parse_args()
    if not args.autorizar_coleta:
        *_, verificacao = validar_origem(args.manifesto, args.autorizacao)
        print(json.dumps(verificacao, ensure_ascii=False)); return
    exigir(bool(args.destino), 'Destino obrigatório')
    r = executar(args.manifesto, args.destino, args.autorizacao, autorizar=True)
    print(json.dumps({k: r[k] for k in ('estado', 'fase', 'erro', 'comprometido_total_nano')}, ensure_ascii=False))
    if r['estado'] != 'concluido': raise SystemExit(1)


if __name__ == '__main__': main()
