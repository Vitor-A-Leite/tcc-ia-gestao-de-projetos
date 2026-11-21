"""Avalia a correção de escopo e conhecimento com comparação histórica v2."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import uuid

from . import avaliar_revisor_v2 as executor
from ..src import ROOT
from ..src import lote_ia as lote
from ..src.ia_real import MODELO, CONFIG
from ..src.revisao import VERSAO, atualizar_pacote, conferir_pacote
from ..src.sessoes import gravar
from ..src.vendor.interpretacao_no.contratos import exigir, hash_json

ANTERIOR = ROOT/'outputs/avaliacao_revisor_v2_20261111'
REGRESSOES_ESCOPO = ('D03-01', 'D05-01', 'D09-01', 'D09-02')


def preparar(destino):
    destino = Path(destino)
    anterior = executor.ler(ANTERIOR/'manifesto.json')
    referencias_v2 = executor.ler(ANTERIOR/'referencias.json')
    origens = dict(anterior['origens'])
    origens.update({str(p.relative_to(ROOT)): lote.sha(p) for p in ANTERIOR.rglob('*.json')})
    for caminho, esperado in anterior['origens'].items():
        exigir(lote.sha(ROOT/caminho) == esperado, 'Origem histórica divergente')
    fontes_resultados = executor.ler(executor.BASE/'execucao.json')['resultados']
    originais = {cid: executor.ler(executor.localizar_resultado(fontes_resultados[cid])) for cid in ('D02', 'D04')}
    motor = next(p for p in originais['D02']['rastro_orquestracao'] if p['no_id'] == 'SUP_MOTOR')
    desconhecido = next(p for p in originais['D04']['rastro_orquestracao'] if p['no_id'] == 'SUP_MOTOR')
    casos, anteriores = [], {}
    for entrada in anterior['entradas']:
        historico = executor.ler(ANTERIOR/entrada['arquivo'])
        exigir(lote.sha(ANTERIOR/entrada['arquivo']) == entrada['sha256'], 'Entrada v2 divergente')
        caso = dict(id=entrada['id'], grupo=entrada['grupo'], pacote=atualizar_pacote(historico['pacote']))
        # IDs de execução dos controles são neutros quanto à classificação esperada.
        if caso['id'] == 'N02':
            caso['pacote'] = executor.pacote_controle(motor, 'N02', magnitude=26)
        elif caso['id'] == 'N03':
            caso['pacote'] = executor.pacote_controle(desconhecido, 'N03', magnitude=25)
        elif caso['id'] == 'N04':
            caso['pacote'] = executor.pacote_controle(motor, 'N04', relato=historico['pacote']['evento']['relato'])
        if caso['grupo'] == 'coleta':
            registro = executor.ler(ANTERIOR/'casos'/f"{caso['id']}.json")['revisao']
            anteriores[caso['id']] = dict(estado=registro['estado'], parecer=registro['parecer']['parecer'],
                erros=registro['erros'], tokens_entrada=registro['tokens_entrada'], tokens_saida=registro['tokens_saida'],
                latencia_ms=registro['latencia_ms'], custo_api_usd=registro['consumo_sessao']['custo_api_usd'],
                arquivo=str((ANTERIOR/'casos'/f"{caso['id']}.json").relative_to(ROOT)))
        casos.append(caso)
    relato_base = motor['contexto']['evento']['relato']
    adicionais = [
        ('N05', relato_base+' Este comunicado aplica-se exclusivamente ao projeto PROJETO-B. A aplicação ao projeto ALFA-AMPLIADO está expressamente excluída.',
         'contradita', 'Documento restringe a aplicação a outro projeto.'),
        ('N06', relato_base+' Este comunicado aplica-se exclusivamente à versão 2.0.0 do projeto ALFA-AMPLIADO. A versão 1.0.0 está expressamente excluída.',
         'contradita', 'Documento restringe a aplicação a outra versão.'),
        ('N07', relato_base+' O início de vigência deste comunicado é D10. A aplicação prospectiva desde D0 está expressamente excluída. A referência D0 usada para medir disponibilidade permanece como origem do calendário.',
         'contradita', 'Documento explicita início de vigência divergente da política cadastrada.'),
        ('N08', relato_base+' O comunicado se aplica ao universo sintético Alfa v1, versão v1, com vigência prospectiva desde D0.',
         'sustentada', 'Aliases cadastrados e vigência compatível com confirmação explícita.'),
        ('N09', 'SUP_MOTOR: a data D18 corresponde exclusivamente à disponibilidade contratada anterior. A nova disponibilidade está pendente de confirmação. Demais parâmetros contratuais e durações mantidos.',
         'suporte_insuficiente', 'Data anterior isolada e magnitude vigente desconhecida diante da proposta D25.')]
    controles = deepcopy(referencias_v2['controles'])
    for cid, relato, esperado, descricao in adicionais:
        casos.append(dict(id=cid, grupo='controle', pacote=executor.pacote_controle(motor, cid, relato=relato)))
        controles[cid] = dict(esperado=esperado, descricao=descricao, natureza='Referência autoral de controle sintético')
    exigir(len(casos) == 28, 'Avaliação exige 19 propostas e nove controles')
    total_antes = lote.comprometido(lote.HISTORICO)+lote.comprometido(lote.LEDGER)
    teto = len(casos)*executor.RESERVA_NANO
    exigir(total_antes+teto <= executor.TETO_TOTAL_NANO, 'Saldo insuficiente para as reservas')
    destino.mkdir(parents=True, exist_ok=False)
    entradas = []
    for caso in casos:
        conferir_pacote(caso['pacote'])
        arquivo = destino/'entradas'/f"{caso['id']}.json"
        gravar(arquivo, caso)
        entradas.append(dict(id=caso['id'], grupo=caso['grupo'], arquivo=str(arquivo.relative_to(destino)), sha256=lote.sha(arquivo)))
    gravar(destino/'referencias.json', dict(anteriores=anteriores, controles=controles,
        regressoes_escopo={cid: 'sustentada' for cid in REGRESSOES_ESCOPO}))
    manifesto = dict(id='revisor-v3-'+uuid.uuid4().hex, preparado_em=lote.agora(), versao=VERSAO,
        modelo=MODELO, configuracao=CONFIG, entradas=entradas, origens=origens, codigo=executor.hashes_codigo(),
        referencias_sha256=lote.sha(destino/'referencias.json'), historico_externo_sha256=lote.sha(lote.HISTORICO),
        comprometido_antes_nano=total_antes, teto_rodada_nano=teto, teto_total_nano=executor.TETO_TOTAL_NANO,
        avaliacao_anterior=str(ANTERIOR.relative_to(ROOT)),
        interpretacao='Avaliação de desenvolvimento com uma tentativa por caso. IDs de controles neutros. Referências autorais fora do pedido da IA.')
    manifesto['hash'] = hash_json(manifesto)
    gravar(destino/'manifesto.json', manifesto)
    return manifesto


def executar(pasta, *, autorizacao, http=None):
    resultado = executor.executar(pasta, autorizacao=autorizacao, http=http)
    pasta = Path(pasta)
    comparacao = executor.ler(pasta/'comparacao.json')
    referencias = executor.ler(pasta/'referencias.json')['regressoes_escopo']
    comparacao['regressoes_escopo'] = [dict(caso_id=c['caso_id'], parecer=c['parecer'],
        esperado=referencias[c['caso_id']], concordante=c['parecer'] == referencias[c['caso_id']])
        for c in comparacao['casos'] if c['caso_id'] in referencias]
    comparacao['referencias'] = 'Comparação v2/v3 em desenvolvimento, com controles e regressões de referência autoral.'
    gravar(pasta/'comparacao.json', comparacao)
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('acao', choices=('preparar', 'executar'))
    parser.add_argument('pasta')
    parser.add_argument('--autorizacao', default='')
    args = parser.parse_args()
    if args.acao == 'preparar':
        manifesto = preparar(args.pasta)
        print(json.dumps(dict(casos=len(manifesto['entradas']), reserva_maxima_usd=manifesto['teto_rodada_nano']/1e9)))
    else:
        resultado = executar(args.pasta, autorizacao=args.autorizacao)
        print(json.dumps(dict(estado=resultado['estado'], casos=len(resultado['casos']))))


if __name__ == '__main__':
    main()
