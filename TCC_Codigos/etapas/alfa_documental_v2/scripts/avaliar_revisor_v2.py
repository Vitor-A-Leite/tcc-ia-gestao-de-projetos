"""Prepara e executa uma comparação versionada do revisor com carteira persistente."""
import argparse
from collections import Counter
from copy import deepcopy
import fcntl
import json
from pathlib import Path
import uuid

from ..src import ROOT
from ..src import lote_ia as lote
from ..src.auditoria import SessaoAuditoriaReal, TransporteRevisaoReal, auditar_resultado
from ..src.ia_real import TransporteReal, MODELO, CONFIG
from ..src.revisao import (RevisorIA, VERSAO, analisar_propostas, montar_pacote,
                          conferir_pacote, _ref_ids)
from ..src.sessoes import gravar
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json
from ..src.evidencias_revisao import CADASTRO_ESCOPO

BASE = ROOT/'outputs/lote_desenvolvimento_revisoes_finais_20261110'
RESERVA_NANO = 15_000_000
TETO_TOTAL_NANO = 20_000_000_000


def ler(path):
    return json.loads(Path(path).read_text())


def localizar_resultado(path):
    caminho = Path(path)
    if caminho.is_file():
        return caminho
    marcador = 'TCC_Codigos/etapas/alfa_documental_v2/'
    exigir(marcador in str(path), 'Resultado fora do projeto')
    caminho = ROOT/str(path).split(marcador, 1)[1]
    exigir(caminho.resolve().is_relative_to(ROOT.resolve()) and caminho.is_file(), 'Resultado ausente')
    return caminho


def hashes_codigo():
    caminhos = list((ROOT/'src').rglob('*.py')) + list((ROOT/'scripts').rglob('*.py')) + [CADASTRO_ESCOPO]
    return {str(p.relative_to(ROOT)): lote.sha(p) for p in sorted(caminhos)}


def pacote_controle(passo, nome, *, magnitude=None, relato=None):
    contexto = deepcopy(passo['contexto'])
    analise = {k: deepcopy(v) for k, v in passo['analise'].items() if k not in ('execucao', 'decisoes')}
    exigir(len(analise['propostas']) == 1, 'Controle exige proposta única')
    contexto['execucao_id'] = 'controle_' + nome
    analise['execucao_id'] = contexto['execucao_id']
    analise['analise_id'] = 'controle_' + nome
    proposta = analise['propostas'][0]
    proposta['id'] = 'controle_' + nome + '_proposta'
    if magnitude is not None:
        proposta['valor'].update(estado='exato', valor=magnitude, lacunas=[], motivo=None)
    if relato is not None:
        contexto['evento']['relato'] = relato
        fonte_evento = proposta['origens_causais'][0]['fato_ref']['fonte_id']
        next(fonte for fonte in contexto['fontes'] if fonte['id'] == fonte_evento)['trecho'] = relato
    contexto['contexto_hash'] = hash_json({k: v for k, v in contexto.items() if k != 'contexto_hash'})
    analise['contexto_hash'] = contexto['contexto_hash']
    deterministica = analisar_propostas(contexto, analise)[0]
    exigir(deterministica['estrutura'] == 'valida' and not deterministica['erro_analise'], 'Controle estruturalmente inválido')
    return montar_pacote(contexto, analise, proposta, deterministica)


def preparar(destino):
    destino = Path(destino)
    execucao_base = ler(BASE/'execucao.json')
    casos = []
    anteriores = {}
    origens = {str((BASE/'execucao.json').relative_to(ROOT)): lote.sha(BASE/'execucao.json')}
    resultados = {}
    for cid, path in execucao_base['resultados'].items():
        path = localizar_resultado(path)
        resultado = ler(path)
        resultados[cid] = resultado
        origens[str(path.relative_to(ROOT))] = lote.sha(path)
        arquivo_auditoria = BASE/cid/'auditoria.json'
        origens[str(arquivo_auditoria.relative_to(ROOT))] = lote.sha(arquivo_auditoria)
        registros_antigos = {r['pacote']['proposta_hash']: r for r in ler(arquivo_auditoria)['registros']}
        for indice, registro in enumerate(auditar_resultado(resultado)['registros'], 1):
            pacote = registro.get('pacote')
            exigir(pacote is not None, 'Proposta original inválida')
            caso_id = f'{cid}-{indice:02}'
            antigo = registros_antigos[pacote['proposta_hash']]['revisao_semantica']
            anteriores[caso_id] = dict(estado=antigo['estado'], parecer=(antigo.get('parecer') or {}).get('parecer'),
                erros=antigo['erros'], tokens_entrada=antigo.get('tokens_entrada'), tokens_saida=antigo.get('tokens_saida'),
                latencia_ms=antigo.get('latencia_ms'),
                custo_api_usd=antigo.get('consumo_sessao', {}).get('custo_api_usd'),
                arquivo=str(arquivo_auditoria.relative_to(ROOT)))
            casos.append(dict(id=caso_id, grupo='coleta', pacote=pacote))
    exigir(len(casos) == 19, 'A comparação exige as 19 propostas registradas')
    piloto = ler(lote.PILOTO)
    origens[str(lote.PILOTO.relative_to(ROOT))] = lote.sha(lote.PILOTO)
    marco = next(r['pacote'] for r in auditar_resultado(piloto)['registros']
                 if r.get('pacote') and r['pacote']['proposta']['alvo_id'] == 'release_M_PROTO_READY')
    motor = next(p for p in resultados['D02']['rastro_orquestracao'] if p['no_id'] == 'SUP_MOTOR')
    desconhecido = next(p for p in resultados['D04']['rastro_orquestracao'] if p['no_id'] == 'SUP_MOTOR')
    controles = [
        ('N01', marco, 'suporte_insuficiente', 'Proposta histórica do marco cita disponibilidade do fornecedor e precedência.'),
        ('N02', pacote_controle(motor, 'magnitude_contradita', magnitude=26), 'contradita',
         'Variante sintética propõe D26 diante de aviso explícito de D25.'),
        ('N03', pacote_controle(desconhecido, 'magnitude_ausente', magnitude=25), 'suporte_insuficiente',
         'Variante sintética propõe D25 diante de disponibilidade desconhecida.'),
        ('N04', pacote_controle(motor, 'alternativas', relato=
            'SUP_MOTOR: nova disponibilidade contratada será D25 ou D27. As duas alternativas permanecem possíveis e o fornecedor ainda não confirmou qual delas se aplica. Demais parâmetros contratuais e durações mantidos.'),
         'ambigua', 'Variante sintética oferece duas datas alternativas sem escolha confirmada.')]
    referencias = {}
    for caso_id, pacote, esperado, descricao in controles:
        casos.append(dict(id=caso_id, grupo='controle', pacote=pacote))
        referencias[caso_id] = dict(esperado=esperado, descricao=descricao,
                                   natureza='Referência autoral de controle sintético')
    total_antes = lote.comprometido(lote.HISTORICO) + lote.comprometido(lote.LEDGER)
    teto = len(casos)*RESERVA_NANO
    exigir(total_antes+teto <= TETO_TOTAL_NANO, 'Saldo insuficiente para as reservas')
    destino.mkdir(parents=True, exist_ok=False)
    entradas = []
    for caso in casos:
        conferir_pacote(caso['pacote'])
        path = destino/'entradas'/f"{caso['id']}.json"
        gravar(path, caso)
        entradas.append(dict(id=caso['id'], grupo=caso['grupo'], arquivo=str(path.relative_to(destino)), sha256=lote.sha(path)))
    gravar(destino/'referencias.json', dict(anteriores=anteriores, controles=referencias))
    manifesto = dict(id='revisor-v'+VERSAO.split('-')[0]+'-'+uuid.uuid4().hex, preparado_em=lote.agora(), versao=VERSAO,
        modelo=MODELO, configuracao=CONFIG, entradas=entradas, origens=origens, codigo=hashes_codigo(),
        referencias_sha256=lote.sha(destino/'referencias.json'), historico_externo_sha256=lote.sha(lote.HISTORICO),
        comprometido_antes_nano=total_antes, teto_rodada_nano=teto, teto_total_nano=TETO_TOTAL_NANO,
        interpretacao='Uma tentativa por proposta. Referências autorais e pareceres anteriores são lidos na comparação após as respostas.')
    manifesto['hash'] = hash_json(manifesto)
    gravar(destino/'manifesto.json', manifesto)
    return manifesto


def validar_manifesto(pasta):
    manifesto = ler(pasta/'manifesto.json')
    exigir(manifesto['hash'] == hash_json({k: v for k, v in manifesto.items() if k != 'hash'}), 'Manifesto adulterado')
    exigir(manifesto['codigo'] == hashes_codigo() and manifesto['versao'] == VERSAO, 'Implementação mudou desde o preparo')
    exigir(manifesto['modelo'] == MODELO and manifesto['configuracao'] == CONFIG, 'Configuração mudou')
    exigir(manifesto['historico_externo_sha256'] == lote.sha(lote.HISTORICO), 'Histórico financeiro mudou')
    exigir(manifesto['referencias_sha256'] == lote.sha(pasta/'referencias.json'), 'Referências mudaram')
    for path, esperado in manifesto['origens'].items():
        exigir(lote.sha(ROOT/path) == esperado, 'Arquivo de origem mudou')
    for entrada in manifesto['entradas']:
        exigir(lote.sha(pasta/entrada['arquivo']) == entrada['sha256'], 'Entrada mudou')
    return manifesto


def avaliar_caso(pasta, caso, manifesto, chave, *, http=None):
    destino = pasta/'casos'/f"{caso['id']}.json"
    pacote = caso['pacote']
    if destino.exists():
        existente = ler(destino)
        exigir(existente['pacote_hash'] == pacote['pacote_hash'] and existente['manifesto_hash'] == manifesto['hash'],
               'Checkpoint de outra entrada ou versão')
        return existente
    transporte = TransporteReal(pasta/'chamadas'/caso['id'], chave, lote.comprometido(lote.HISTORICO),
        http=http, ledger=lote.LEDGER, rodada=manifesto['id']+':'+caso['id'],
        teto_total_nano=manifesto['teto_total_nano'], teto_rodada_nano=RESERVA_NANO, max_chamadas=1,
        grupo=manifesto['id'], teto_grupo_nano=manifesto['teto_rodada_nano'])
    try:
        # Reserva de um processo interrompido impede reenviar a mesma proposta.
        exigir(transporte.snapshot()['chamadas_api'] == 0, 'Carteira já possui tentativa para este caso')
        revisor = RevisorIA(TransporteRevisaoReal(transporte), modelo=MODELO, configuracao=CONFIG, modo='ia_real')
        registro = dict(caso_id=caso['id'], grupo=caso['grupo'], manifesto_hash=manifesto['hash'],
            pacote_hash=pacote['pacote_hash'], pacote=pacote, estado='em_andamento', revisao=None,
            modo='ia_real' if http is None else 'teste_http_injetado')
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open('x', encoding='utf8') as arquivo:
            json.dump(registro, arquivo, ensure_ascii=False, indent=2)
        sessao = SessaoAuditoriaReal(registro, destino, dict(max_solicitacoes=1,
            max_tokens_entrada=64000, max_tokens_saida=16000, max_segundos=600, max_custo_centavos=1.5))
        registro['revisao'] = revisor.revisar(pacote, sessao=sessao)
        registro['estado'] = 'concluido' if registro['revisao']['estado'] == 'parecer_recebido' else 'falha_revisao'
        sessao.salvar()
        return registro
    finally:
        transporte.db.close()


def comparar(pasta, manifesto):
    referencias = ler(pasta/'referencias.json')
    linhas = []
    contagens = {'coleta': Counter(), 'controle': Counter()}
    codigos = Counter()
    consumo = Counter()
    consumo_por_grupo = {'coleta': Counter(), 'controle': Counter()}
    for entrada in manifesto['entradas']:
        registro = ler(pasta/'casos'/f"{entrada['id']}.json")
        revisao = registro.get('revisao') or {}
        parecer = (revisao.get('parecer') or {}).get('parecer')
        valido = revisao.get('estado') == 'parecer_recebido'
        contagens[entrada['grupo']]['validos' if valido else 'invalidos'] += 1
        if valido:
            contagens[entrada['grupo']][parecer] += 1
        codigos.update(erro['codigo'] for erro in revisao.get('erros', []))
        uso = registro.get('sessao_revisao', {}).get('consumo', {})
        for campo in ('chamadas_api', 'tokens_entrada', 'tokens_saida', 'custo_api_usd', 'comprometido_api_usd', 'segundos_api'):
            consumo[campo] += uso.get(campo, 0)
            consumo_por_grupo[entrada['grupo']][campo] += uso.get(campo, 0)
        linha = dict(caso_id=entrada['id'], grupo=entrada['grupo'], estado=revisao.get('estado', 'interrompida'),
                     parecer=parecer, erros=revisao.get('erros', []))
        if entrada['grupo'] == 'coleta':
            linha['anterior'] = referencias['anteriores'][entrada['id']]
        else:
            referencia = referencias['controles'][entrada['id']]
            linha['referencia_autoral'] = referencia
            linha['concordante'] = valido and parecer == referencia['esperado']
        linhas.append(linha)
        if valido:
            fontes_citadas = {ref['fonte_id'] for ref in _ref_ids(registro['pacote']['proposta'])}
            fontes_examinadas = set(revisao['parecer']['fontes_selecionadas'])
            linha['cobertura'] = dict(aspectos_avaliados=len(revisao['parecer']['aspectos']),
                fontes_citadas=len(fontes_citadas), fontes_citadas_examinadas=len(fontes_citadas & fontes_examinadas),
                fontes_examinadas=len(fontes_examinadas))
    anteriores = list(referencias['anteriores'].values())
    resumo = dict(versao=VERSAO, casos=linhas, resultados={k: dict(v) for k, v in contagens.items()},
        erros=dict(codigos), consumo=dict(consumo),
        consumo_por_grupo={grupo: dict(uso) for grupo, uso in consumo_por_grupo.items()},
        anterior=dict(validos=sum(r['estado'] == 'parecer_recebido' for r in anteriores), total=19,
            tokens_entrada=sum(r['tokens_entrada'] or 0 for r in anteriores),
            tokens_saida=sum(r['tokens_saida'] or 0 for r in anteriores),
            custo_api_usd=sum(r['custo_api_usd'] or 0 for r in anteriores)),
        concordancia_pareceres_validos=dict(
            comparaveis=sum(linha['estado'] == 'parecer_recebido' and linha['anterior']['estado'] == 'parecer_recebido'
                            for linha in linhas if linha['grupo'] == 'coleta'),
            concordantes=sum(linha['estado'] == 'parecer_recebido' and linha['anterior']['estado'] == 'parecer_recebido'
                             and linha['parecer'] == linha['anterior']['parecer']
                             for linha in linhas if linha['grupo'] == 'coleta')),
        controles_concordantes=sum(linha.get('concordante', False) for linha in linhas),
        referencias='Controles sintéticos com referência autoral. A coleta principal mede validade e concordância com pareceres anteriores.',
        comprometido_historico_total_usd=(lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER))/1e9,
        originais_preservados=all(lote.sha(ROOT/path) == sha for path, sha in manifesto['origens'].items()))
    gravar(pasta/'comparacao.json', resumo)
    return resumo


def executar(pasta, *, autorizacao, http=None):
    exigir(isinstance(autorizacao, str) and bool(autorizacao.strip()), 'Autorização obrigatória')
    pasta = Path(pasta)
    with (pasta/'execucao.lock').open('a') as arquivo_lock:
        fcntl.flock(arquivo_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifesto = validar_manifesto(pasta)
        registro = dict(manifesto_hash=manifesto['hash'], estado='em_andamento', autorizacao=autorizacao,
                        inicio=lote.agora(), casos={}, modo='ia_real' if http is None else 'teste_http_injetado')
        chave = None
        try:
            for entrada in manifesto['entradas']:
                caso = ler(pasta/entrada['arquivo'])
                registro['caso_atual'] = caso['id']
                gravar(pasta/'execucao.json', registro)
                if chave is None and not (pasta/'casos'/f"{caso['id']}.json").exists():
                    chave = lote.ler_chave() if http is None else 'chave-ficticia-teste'
                resultado = avaliar_caso(pasta, caso, manifesto, chave, http=http)
                registro['casos'][caso['id']] = resultado['estado']
                gravar(pasta/'execucao.json', registro)
            resumo = comparar(pasta, manifesto)
            registro['estado'] = 'concluido_com_falhas' if any(
                grupo.get('invalidos', 0) for grupo in resumo['resultados'].values()) else 'concluido'
        except BaseException as exc:
            mensagem = str(exc).replace(chave, '[REDACTED]') if chave else str(exc)
            registro.update(estado='interrompido', erro=dict(tipo=type(exc).__name__, mensagem=mensagem))
            raise
        finally:
            registro['fim'] = lote.agora()
            gravar(pasta/'execucao.json', registro)
    return registro


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('acao', choices=('preparar', 'executar'))
    parser.add_argument('pasta')
    parser.add_argument('--autorizacao', default='')
    argumentos = parser.parse_args()
    if argumentos.acao == 'preparar':
        manifesto = preparar(argumentos.pasta)
        print(json.dumps(dict(casos=len(manifesto['entradas']), reserva_maxima_usd=manifesto['teto_rodada_nano']/1e9)))
    else:
        resultado = executar(argumentos.pasta, autorizacao=argumentos.autorizacao)
        print(json.dumps(dict(estado=resultado['estado'], casos=len(resultado['casos']))))


if __name__ == '__main__':
    main()
