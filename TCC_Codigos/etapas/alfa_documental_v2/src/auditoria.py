"""Auditoria de coleta já existente, sem sobrescrever coleta ou reexecutar solver.

CLI somente offline. A API real exige orçamento próprio, arquivo novo e o mesmo
TransporteReal (carteira/reservas persistentes); nenhuma credencial é carregada aqui.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from time import perf_counter

from .revisao import VERSAO, RevisorIA, analisar_propostas, montar_pacote
from .sessoes import orcamento, gravar, snapshot_real, contabilizar_real
from .vendor.hibrido_v07_r3.wire import conferir_vinculo
from .vendor.interpretacao_no.contratos import exigir, hash_json
from .vendor.interpretacao_no.adaptadores import RespostaTransporte, FalhaTransporte


class TransporteRevisaoReal:
    """Usa gerar(), preservando integralmente as reservas/tetos de TransporteReal."""
    origem = 'openai_real'

    def __init__(self, transporte):
        from .ia_real import TransporteReal
        exigir(isinstance(transporte, TransporteReal), 'Revisão real exige TransporteReal com ledger persistente')
        self.transporte = transporte

    def snapshot(self):
        return self.transporte.snapshot()

    def __call__(self, pedido):
        from .ia_real import MODELO, CONFIG
        exigir(pedido['modelo'] == MODELO and pedido['configuracao'] == CONFIG, 'Configuração real divergente')
        r, custo = self.transporte.gerar(pedido['mensagens'], pedido['formato_resposta'], 'revisao_semantica')
        partes = [p for item in r.get('output', []) for p in item.get('content', [])]
        recusa = any(p.get('type') == 'refusal' for p in partes)
        return RespostaTransporte(
            texto=''.join(p['text'] for p in partes if p.get('type') == 'output_text'),
            estado='recusa' if recusa else 'completa' if r.get('status') == 'completed' else 'incompleta',
            modelo=r.get('model'), request_id=r.get('id'),
            tokens_entrada=r.get('usage', {}).get('input_tokens'), tokens_saida=r.get('usage', {}).get('output_tokens'),
            metadados={'custo_api_usd': custo/1e9, 'moeda': 'USD', 'resposta_api': deepcopy(r),
                       'ledger_rodada': self.transporte.rodada})


class SessaoAuditoriaReal:
    """Gate cumulativo de auditoria separado das sessões de interpretação.

    Criado por auditar_arquivo; o destino exclusivo é persistido antes da chamada.
    Reservas conservadoras iguais ao máximo do transporte: 64k/16k, USD .015.
    Interrupção/falha com uso desconhecido bloqueia novos pedidos, sem retomada.
    """
    def __init__(self, registro, destino, limites):
        exigir(isinstance(limites, dict) and bool(limites), 'Revisão real exige orçamento explícito')
        self.limites = orcamento(limites)
        exigir(self.limites['max_custo_centavos'] > 0, 'Revisão real exige teto positivo em centavos de USD')
        self.registro, self.destino = registro, Path(destino)
        exigir(self.destino.is_file(), 'Arquivo de auditoria deve ser reservado antes das chamadas')
        self.inicio = perf_counter()
        self.estado = dict(limites=deepcopy(self.limites), consumo=dict(solicitacoes_reais=0,
            solicitacoes_simuladas=0, chamadas_api=0, tokens_entrada=0, tokens_saida=0,
            custo_api_usd=0.0, custo_api_centavos=0.0, comprometido_api_usd=0.0,
            moeda_custo_api='USD', segundos=0.0, uso_desconhecido=False), tentativas=[])
        self.registro['sessao_revisao'] = self.estado
        self.salvar()

    def salvar(self):
        self.estado['consumo']['segundos'] = perf_counter()-self.inicio
        gravar(self.destino, self.registro)

    def chamar(self, transporte, pedido, pacote):
        u, b = self.estado['consumo'], self.limites
        snap = snapshot_real(transporte)
        if u['uso_desconhecido'] or snap.get('uso_desconhecido') or getattr(transporte.transporte, 'parado', False):
            raise FalhaTransporte('uso_desconhecido', 'Consumo desconhecido ou transporte interrompido; revisão bloqueada')
        if (u['solicitacoes_reais'] >= b['max_solicitacoes']
                or u['tokens_entrada']+64000 > b['max_tokens_entrada']
                or u['tokens_saida']+16000 > b['max_tokens_saida']
                or u['comprometido_api_usd']+.015 > b['max_custo_centavos']/100
                or perf_counter()-self.inicio+pedido['timeout_s'] > b['max_segundos']):
            raise FalhaTransporte('orcamento_revisao', 'Orçamento não comporta reserva máxima da próxima revisão')
        tentativa = dict(pacote_hash=pacote['pacote_hash'], pedido=deepcopy(pedido), estado='reservada',
                         reserva=dict(tokens_entrada=64000, tokens_saida=16000, custo_api_usd=.015))
        u['solicitacoes_reais'] += 1
        self.estado['tentativas'].append(tentativa)
        self.estado['em_voo'] = pacote['pacote_hash']
        self.salvar()  # uma interrupção não apaga o pedido já autorizado
        try:
            resposta = transporte(deepcopy(pedido))
            tentativa.update(estado='respondida', estado_resposta=resposta.estado)
            return resposta
        except BaseException as exc:
            tentativa.update(estado='erro', erro=getattr(exc, 'codigo', type(exc).__name__))
            raise
        finally:
            delta = contabilizar_real(self.estado, snap, transporte)
            tentativa['consumo_observado'] = deepcopy(delta)
            tentativa['uso_desconhecido'] = u['uso_desconhecido']
            self.estado.pop('em_voo', None)
            self.salvar()


def _registros(resultado, revisor=None, sessao=None):
    for passo in resultado.get('rastro_orquestracao', []):
        c, a = passo.get('contexto'), passo.get('analise')
        if c is None or a is None or a.get('execucao', {}).get('estado') != 'ok':
            continue
        try:
            conferir_vinculo(a, c)
        except Exception as exc:
            yield dict(no_id=passo.get('no_id'), estado='vinculo_invalido', erro=str(exc), propostas=[])
            continue
        for p, d in zip(a['propostas'], analisar_propostas(c, a)):
            registro = dict(no_id=passo['no_id'], deterministica=d, pacote=None, revisao_semantica=None)
            if d['estrutura'] == 'valida' and not d['erro_analise']:
                registro['pacote'] = montar_pacote(c, a, p, d)
                if revisor:
                    registro['revisao_semantica'] = revisor.revisar(registro['pacote'], sessao=sessao)
            yield registro


def _cabecalho(resultado, revisor):
    # Somente afirmações já cadastradas e resultados da verificação documental;
    # esta informação não entra no pacote de evidências do revisor de propostas.
    documental = [dict(unidade=a['unidade'], estado=a['estado'], motivo=a.get('motivo'))
                   for a in resultado.get('verificacao_documental', {}).get('afirmacoes', [])]
    return dict(versao=VERSAO, modo='observacao', resultado_original_hash=hash_json(resultado),
                execucao_original_id=resultado.get('execucao_id'),
                identidade_revisor=revisor.identidade() if revisor else None,
                data_auditoria=datetime.now(timezone.utc).isoformat(), estado='em_andamento',
                aprovacao_humana=None, alteracoes_aplicadas=[], suporte_semantico_original=resultado.get('suporte_semantico'),
                verificacao_documental_cadastrada=documental, registros=[])


def auditar_resultado(resultado, *, revisor=None):
    """API em memória, somente offline; não altera o objeto de origem."""
    exigir(revisor is None or isinstance(revisor, RevisorIA) and revisor.modo == 'offline', 'Auditoria real exige auditar_arquivo com orçamento e destino novo')
    registro = _cabecalho(resultado, revisor)
    registro['registros'] = list(_registros(resultado, revisor))
    registro['estado'] = 'concluida'
    return registro


def auditar_arquivo(origem, destino, *, revisor=None, limites=None, parar_em_falha=False):
    """Audita arquivo existente e cria outro; repetir o destino nunca gera gasto.

    Revisor real é opt-in programático. Não carrega chave, cria transporte ou usa
    cache implícito. Uma nova auditoria exige novo destino e novo teto explícito.
    """
    origem, destino = Path(origem), Path(destino)
    exigir(origem.resolve() != destino.resolve(), 'Destino deve ser distinto da coleta')
    exigir(revisor is None or isinstance(revisor, RevisorIA), 'Revisor inválido')
    real = revisor is not None and revisor.modo == 'ia_real'
    if real:
        exigir(isinstance(limites, dict) and bool(limites), 'Auditoria real exige orçamento explícito')
        exigir(orcamento(limites)['max_custo_centavos'] > 0, 'Teto financeiro explícito obrigatório')
    bruto = origem.read_bytes()
    resultado = json.loads(bruto)
    registro = _cabecalho(resultado, revisor)
    registro.update(arquivo_origem=str(origem.resolve()), arquivo_origem_sha256=hashlib.sha256(bruto).hexdigest())
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open('x', encoding='utf8') as f:
        json.dump(registro, f, ensure_ascii=False, indent=2, allow_nan=False)
    sessao = SessaoAuditoriaReal(registro, destino, limites) if real else None
    try:
        for item in _registros(resultado, revisor, sessao):
            registro['registros'].append(item)
            gravar(destino, registro)
            if parar_em_falha:
                exigir(item.get('pacote') is not None, 'Vínculo/proposta inválido na auditoria')
                if revisor:
                    exigir((item.get('revisao_semantica') or {}).get('estado') == 'parecer_recebido',
                           'Revisão falhou; nenhuma proposta seguinte será enviada')
        registro['estado'] = 'concluida'
    except BaseException as exc:
        registro.update(estado='interrompida', erro=str(exc))
        raise
    finally:
        if sessao:
            sessao.salvar()
        else:
            gravar(destino, registro)
    return registro
