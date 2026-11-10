"""Sessões persistentes: execução única, orçamento e retomada verificável.

Cada passo é validado pelo contrato local incorporado. O cache guarda a resposta
original, ligada ao contexto exato; reler/recalcular não constitui nova análise.
Modo offline é o padrão; IA real requer transporte e orçamento explícitos.
"""
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import json
from pathlib import Path
import re
from time import perf_counter
import uuid

from . import ROOT, DATA
from . import alcance, selecao
from .modelo import carregar, projetar, normalizar, grafo_documental
from .pipeline import ler_cenario, executar
from .politica import construir as politica
from .documentos import verificar
from .vendor.interpretacao_no.contratos import hash_json
from .vendor.orquestracao import ordem
from .vendor.hibrido_v07_r3.adaptador import LocalV07R3


def gravar(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False))
    temp.replace(path)


def assinatura(g, docs, cenario, fixture):
    codigo = {str(p.relative_to(ROOT)): hash_json(p.read_text()) for p in (ROOT/'src').rglob('*.py')}
    return hash_json([g, docs, cenario, fixture, codigo])


def orcamento(config=None):
    # 32 é configuração do protocolo comparativo inicial, não limite do grafo.
    b = dict(max_solicitacoes=32, max_tokens_entrada=1000000, max_tokens_saida=100000,
             max_segundos=600.0, max_custo_centavos=0.0)
    if config:
        if set(config)-set(b): raise ValueError('Controle de orçamento desconhecido.')
        b.update(config)
    for k, v in b.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v < float('inf'):
            raise ValueError('Orçamento inválido: '+k)
    for k in ('max_solicitacoes', 'max_tokens_entrada', 'max_tokens_saida'):
        if type(b[k]) is not int: raise ValueError('Orçamento inteiro obrigatório: '+k)
    return b


def dados_sessao(s):
    c=deepcopy(s['cenario_snapshot']) if s.get('cenario_snapshot') is not None else ler_cenario(s['cenario_id'])
    f=None if s.get('modo','simulacao_offline')=='ia_real' else json.loads((DATA/'simulacoes/dev'/(c['id']+'.json')).read_text())
    return c,f


def snapshot_real(transporte):
    if getattr(transporte,'origem',None)!='openai_real' or not callable(getattr(transporte,'snapshot',None)):
        raise ValueError('Transporte real exige identidade e snapshot de consumo.')
    q=deepcopy(transporte.snapshot())
    for k in ('chamadas_api','tokens_entrada','tokens_saida','custo_api_usd','segundos'):
        v=q.get(k)
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<float('inf'):
            raise ValueError('Consumo real desconhecido ou inválido: '+k)
    for k in ('chamadas_api','tokens_entrada','tokens_saida'):
        if type(q[k]) is not int:raise ValueError('Contador real deve ser inteiro: '+k)
    return q


def contabilizar_real(s, antes, transporte):
    """Deltas permitem retomar com o ledger persistente sem cobrar duas vezes."""
    try:
        depois=snapshot_real(transporte)
        campos=('chamadas_api','tokens_entrada','tokens_saida','custo_api_usd')
        delta={k:depois[k]-antes[k] for k in campos}
        if any(v<0 for v in delta.values()):raise ValueError('Contador real retrocedeu.')
        for k,v in delta.items():s['consumo'][k]=s['consumo'].get(k,0)+v
        s['consumo']['custo_api_centavos']=100*s['consumo']['custo_api_usd']
        s['consumo']['segundos_api']=s['consumo'].get('segundos_api',0)+max(0,depois['segundos']-antes['segundos'])
        s['consumo']['comprometido_api_usd']=s['consumo'].get('comprometido_api_usd',0)+max(0,depois.get('comprometido_usd',depois['custo_api_usd'])-antes.get('comprometido_usd',antes['custo_api_usd']))
        s['consumo']['moeda_custo_api']='USD'
        s['consumo']['uso_desconhecido']=bool(s['consumo'].get('uso_desconhecido') or depois.get('uso_desconhecido'))
        s['ultimo_snapshot_real']=depois
        return delta
    except Exception as exc:
        s['consumo']['uso_desconhecido']=True
        s['erro_contabilizacao']=str(exc)
        return None


def limite_consumo(s, *, real=False):
    u=s['consumo'];b=s['limites']
    total=u.get('solicitacoes_reais',0)+u['solicitacoes_simuladas']
    if u.get('uso_desconhecido'):return 'Consumo real desconhecido; novas chamadas bloqueadas'
    if total>=b['max_solicitacoes']:return 'Limite acumulado de solicitações'
    if real and (any(u[k]>=b['max_'+k] for k in ('tokens_entrada','tokens_saida')) or 100*u.get('comprometido_api_usd',u.get('custo_api_usd',0))>=b['max_custo_centavos']):
        return 'Limite acumulado de tokens ou custo (centavos de USD)'
    return None


class Sessoes:
    def __init__(self, pasta=None):
        self.pasta = Path(pasta) if pasta else ROOT/'outputs/sessoes'
        self.pasta.mkdir(parents=True, exist_ok=True)

    def caminho(self, sid, suffix='.json'):
        if not isinstance(sid, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,90}', sid):
            raise ValueError('Identificador de sessão inválido.')
        return self.pasta/(sid+suffix)

    def salvar(self, s):
        gravar(self.caminho(s['id']), s)

    def ler(self, sid):
        s = json.loads(self.caminho(sid).read_text())
        if self.caminho(sid, '.cancelar').exists(): s['cancelamento_solicitado'] = True
        return s

    @contextmanager
    def lock(self, sid):
        with self.caminho(sid, '.lock').open('a') as f:
            try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError: raise ValueError('Execução já em andamento; acompanhe a sessão.') from None
            try: yield
            finally: fcntl.flock(f, fcntl.LOCK_UN)

    def preparar(self, cenario_id, entradas, max_nos, *, escopo='impacto_do_evento',
                 versao=None, limites=None, sid=None, confirmar_divergencia=False,
                 modo='simulacao_offline', cenario=None):
        if modo not in ('simulacao_offline','ia_real'):raise ValueError('Modo inválido.')
        g, docs = carregar(); c=deepcopy(cenario) if cenario is not None else ler_cenario(cenario_id)
        if c['id']!=cenario_id:raise ValueError('Identidade do cenário JSON divergente.')
        e = projetar(g, docs); ev = normalizar(c, e)
        f = None if modo=='ia_real' else json.loads((DATA/'simulacoes/dev'/(cenario_id+'.json')).read_text())
        budget=orcamento(limites)
        if modo=='ia_real' and budget['max_custo_centavos']<=0:raise ValueError('IA real exige teto financeiro explícito, em centavos de USD.')
        sel = selecao.validar(g, ev, entradas, max_nos, versao or e['versao'], escopo)
        if sel['mencoes_fora_da_selecao'] and not confirmar_divergencia:
            raise ValueError('Seleção diverge das menções do evento: '+', '.join(sel['mencoes_fora_da_selecao'])+'. Confirme teste delimitado ou inclua as entradas.')
        if sel['mencoes_fora_da_selecao'] and escopo != 'teste_delimitado':
            raise ValueError('Análise do evento exige incluir todas as menções; use teste delimitado explicitamente.')
        regiao = alcance.construir(e, ev, g, sel['nos_entrada'])
        sel['total_nos_grafo'] = len(grafo_documental(g, docs, c)['nodes'])
        s = dict(id=sid or uuid.uuid4().hex, cenario_id=cenario_id, modo=modo,
                 cenario_snapshot=deepcopy(c) if modo=='ia_real' or cenario is not None else None, selecao=sel, regiao=regiao,
                 assinatura=assinatura(g, docs, c, f), versao_projeto=e['versao'], estado='pronta', revisao=0,
                 limites=budget, cache={}, visitados=[], tentativas=[], acoes=[],
                 consumo=dict(solicitacoes_simuladas=0, solicitacoes_reais=0, chamadas_api=0, tokens_entrada=0,
                              tokens_saida=0, custo_api_centavos=0, custo_api_usd=0, moeda_custo_api='USD', segundos=0.0),
                 pendentes=list(regiao['nos']), resultado=None, cancelamento_solicitado=False,
                 ambiguidades=[], expansoes=[], sugestoes={},
                 selecao_confirmada=True, historico_selecoes=[dict(origem='engenheiro',selecao=deepcopy(sel),sugestoes_consideradas=[])],
                 financeiro='IA real explicitamente selecionada; transporte deve manter reservas e conciliação com a carteira histórica. Limite monetário da sessão em centavos de USD.' if modo=='ia_real' else 'Modo offline: nenhuma despesa nova; carteira histórica permanece externa e intacta.')
        with self.lock(s['id']):
            if self.caminho(s['id']).exists(): raise ValueError('Sessão já existe; não sobrescrever.')
            self.salvar(s)
        return s

    def cancelar(self, sid):
        s = self.ler(sid)
        if s['estado'] == 'concluida': raise ValueError('Sessão já concluída; não há chamadas a cancelar.')
        self.caminho(sid, '.cancelar').touch(exist_ok=True)
        # Flag independente não pode ser perdida por gravação da chamada em voo.
        try:
            with self.lock(sid):
                s=self.ler(sid);s['estado']='cancelada';s['revisao']+=1
                if s['resultado']: self._parcial(s['resultado'], 'Análise cancelada pelo engenheiro.')
                self.salvar(s)
        except ValueError:
            pass
        return self.ler(sid)

    @staticmethod
    def _parcial(r, motivo):
        r.setdefault('pendencias_execucao', []).append(motivo)
        r['execucao']['estado']='parcial';r['completude']={'prazo':'parcial','custo':'parcial'}
        for k in ('fim_novo','delta_dias','custo_novo','delta_centavos'):
            r[k]=dict(estado='indeterminado',valor=None,evidencias=[],lacunas=[motivo],motivo=motivo)
        if 'verificacao_documental' in r:
            vd=r['verificacao_documental']
            vd['recomendacoes']=[x for x in vd['recomendacoes'] if x['trecho_id'] not in ('SR.COST','SR.FINISH')]
            for a in vd['afirmacoes']:
                if a['trecho_id'] in ('SR.COST','SR.FINISH'):
                    a.update(estado='nao_verificavel',calculado=None,motivo=motivo)

    def executar(self, sid, *, selecionados=None, max_nos=None, limites=None,
                 acao_id=None, revisao=None, adaptador_teste=None, adaptador_real=None):
        if adaptador_teste is not None and getattr(adaptador_teste,'origem',None)!='simulado':
            raise ValueError('Somente adaptador de teste offline.')
        acao_id = acao_id or uuid.uuid4().hex
        with self.lock(sid):
            s=self.ler(sid)
            if acao_id in s['acoes']: return s
            if s['cancelamento_solicitado'] or s['estado']=='cancelada': raise ValueError('Análise cancelada; crie uma nova sessão para outro teste.')
            if s['estado']=='concluida': return s
            if not s.get('selecao_confirmada',True): raise ValueError('Confirme ou corrija as entradas sugeridas antes de executar.')
            if revisao is not None and revisao!=s['revisao']: raise ValueError('Sessão mudou; atualize a tela antes de prosseguir.')
            real=s.get('modo','simulacao_offline')=='ia_real'
            if real:
                if adaptador_teste is not None or not isinstance(adaptador_real,LocalV07R3):raise ValueError('Sessão real exige adaptador_real LocalV07R3, sem simulação.')
                if getattr(adaptador_real,'repetir',False):raise ValueError('Repetições automáticas não são permitidas.')
                estado_transporte=snapshot_real(adaptador_real.transporte)
                if estado_transporte.get('uso_desconhecido') or getattr(adaptador_real.transporte,'parado',False):raise ValueError('Transporte real interrompido ou com uso desconhecido.')
            elif adaptador_real is not None:raise ValueError('Adaptador real incompatível com sessão offline.')
            inner_config=adaptador_real if real else adaptador_teste
            g,docs=carregar();c,f=dados_sessao(s);e=projetar(g,docs);ev=normalizar(c,e)
            if assinatura(g,docs,c,f)!=s['assinatura']:
                s['estado']='obsoleta';s['invalidacao']='Dados/fontes/código mudaram; refazer todas as análises. Consumo histórico preservado.';self.salvar(s)
                raise ValueError(s['invalidacao'])
            config = dict(tipo='fixture' if inner_config is None else type(inner_config).__module__+'.'+type(inner_config).__qualname__,
                          parametros=getattr(inner_config,'configuracao',{}), modelo=getattr(inner_config,'modelo',None),
                          identidade=getattr(inner_config,'cache_identidade',None))
            if s.get('configuracao_interpretador') is not None and s['configuracao_interpretador'] != config:
                s['estado']='obsoleta';s['invalidacao']='Adaptador/modelo/configuração mudou; crie nova sessão. Consumo preservado.';self.salvar(s)
                raise ValueError(s['invalidacao'])
            s['configuracao_interpretador']=config
            if limites is not None:
                s['limites']=orcamento({**s['limites'],**limites})
            if max_nos is not None:
                s['selecao']['limite_nos_analise']=selecao.limite(max_nos,s['selecao']['maximo_disponivel'],max(len(s['visitados']),len(s['selecao']['nos_entrada'])))
            if selecionados is None:
                if s['estado']!='pronta': raise ValueError('Escolha explicitamente os pendentes para prosseguir.')
                permitidos=set(s['regiao']['nos'])
            else:
                if not isinstance(selecionados,list) or not selecionados or len(set(selecionados))!=len(selecionados) or not set(selecionados)<=set(s['pendentes']):
                    raise ValueError('Selecione nós pendentes válidos, sem duplicação.')
                permitidos=set(selecionados)
            s['estado']='executando';s['revisao']+=1;s['acoes'].append(acao_id);self.salvar(s)
            t0=perf_counter();antes=s['consumo']['segundos']; novos_alvos=set()
            seq,pred=ordem(e)
            def cache(c): return deepcopy(s['cache'].get(c['contexto_hash']))
            def gate(ctx):
                n=ctx['no_id'];b=s['limites'];u=s['consumo']
                if self.caminho(sid,'.cancelar').exists():return 'Cancelamento solicitado'
                if n not in permitidos:return 'Pendente não selecionado para esta continuação'
                if n not in s['visitados'] and len(s['visitados'])>=s['selecao']['limite_nos_analise']:return 'Limite de nós distintos'
                bloqueio=limite_consumo(s,real=real)
                if bloqueio:return bloqueio
                if real and (s.get('falha_real_bloqueante') or getattr(adaptador_real.transporte,'parado',False)):return 'Falha real anterior; nenhuma chamada seguinte'
                if antes+perf_counter()-t0>=b['max_segundos']:return 'Limite acumulado de tempo'
                # Reservas por pedido e preços são verificados pelo transporte;
                # a sessão mantém tetos cumulativos separados dos nós distintos.
                if any(u[k]>b['max_'+k] for k in ('tokens_entrada','tokens_saida')) or u['custo_api_centavos']>b['max_custo_centavos']:
                    return 'Orçamento acumulado insuficiente'
                return None
            def factory(st,event,graph,execution,max_analises):
                p=politica(st,event,graph,sid,regiao=s['regiao']['nos'],sementes=s['regiao']['nos'])
                p.consultar_cache=cache;p.autorizar_passo=gate
                p.max_analises=len(seq)+s['limites']['max_solicitacoes'];p.max_chamadas=s['limites']['max_solicitacoes'];p.max_tempo_s=max(s['limites']['max_segundos'],.001)
                return p
            class Captura:
                origem='simulado';modelo='fixture-local';configuracao={};timeout_s=1;repetir=False
                identidade_runtime='alfa_documental_v2.sessao_offline'
                def __init__(self,inner):
                    self.inner=inner;self.configuracao=config
                    if real:
                        self.origem='openai_real';self.modelo=inner.modelo;self.timeout_s=inner.timeout_s
                        self.identidade_runtime='alfa_documental_v2.sessao_ia_real'
                def analisar(self,ctx):
                    if ctx['no_id'] not in s['visitados']:s['visitados'].append(ctx['no_id'])
                    s['consumo']['solicitacoes_reais' if real else 'solicitacoes_simuladas']+=1
                    s['em_voo']=dict(no_id=ctx['no_id'],contexto_hash=ctx['contexto_hash']);self_outer.salvar(s)
                    snap=snapshot_real(self.inner.transporte) if real else None
                    try: a=self.inner.analisar(deepcopy(ctx))
                    except Exception as exc:
                        if real:s['falha_real_bloqueante']=True
                        s['tentativas'].append(dict(no_id=ctx['no_id'],erro=str(exc)));self_outer.salvar(s);raise
                    finally:
                        if real:
                            contabilizar_real(s,snap,self.inner.transporte)
                            self_outer.salvar(s)
                    if not real and a['execucao'].get('chamadas')!=0:raise ValueError('Transporte não offline rejeitado.')
                    if real and a['execucao'].get('estado')!='ok':s['falha_real_bloqueante']=True
                    s['cache'][ctx['contexto_hash']]=deepcopy(a)
                    s['tentativas'].append(dict(no_id=ctx['no_id'],contexto_hash=ctx['contexto_hash'],estado=a['execucao']['estado']))
                    s.pop('em_voo',None)
                    # Encaminhamento só é considerado após validação do adaptador;
                    # o fechamento da passagem revalida vínculo/autorizações.
                    self_outer.salvar(s)
                    return a
            self_outer=self
            def envelope(adapter,p):return Captura(adaptador_teste or adapter)
            try:
                while True:
                    novos_alvos.clear()
                    r=executar(c,fixture=f,adapter=adaptador_real,modo='ia_real' if real else 'simulacao_offline',fabrica_politica=factory,envelopar=envelope)
                    aceitos={x['analise_id'] for x in r.get('registro_operacional',{}).get('decisoes',[]) if x['operacao_estrutural']=='permitida_condicional'}
                    for passo in r.get('rastro_orquestracao',[]):
                        a=passo.get('analise',{})
                        if a.get('analise_id') in aceitos:
                            novos_alvos.update(x['no_id'] for x in a.get('encaminhamentos',[]))
                    fora=novos_alvos-set(s['regiao']['nos'])
                    if not fora:break
                    if not fora<=set(seq):
                        self._parcial(r,'Encaminhamento para entidade sem cadastro.');break
                    ampliado=alcance.construir(e,ev,g,list(set(s['regiao']['nos'])|fora))
                    adicionados=set(ampliado['nos'])-set(s['regiao']['nos'])
                    s['expansoes'].append(dict(motivo='Encaminhamento validado',alvos=sorted(fora),incluidos=sorted(adicionados)))
                    s['regiao']=ampliado
                    if selecionados is None: permitidos.update(adicionados)
                    # Caches permanecem sujeitos à identidade completa do contexto;
                    # predecessores alterados invalidam naturalmente os sucessores.
                    self.salvar(s)
                if s['selecao']['mencoes_fora_da_selecao']:self._parcial(r,'Teste delimitado: menções fora da seleção impedem conclusão global.')
                if self.caminho(sid,'.cancelar').exists():self._parcial(r,'Análise cancelada pelo engenheiro.')
                if s['consumo'].get('uso_desconhecido'):self._parcial(r,'Consumo real desconhecido; execução interrompida sem novas chamadas.')
                steps={x['no_id']:x for x in r.get('rastro_orquestracao',[])}
                validos=set(r.get('registro_operacional',{}).get('fechamento_final',{}).get('nos_com_analise_operacional_valida',[]))
                s['pendentes']=[n for n in s['regiao']['nos'] if n not in validos]
                r['selecao']=deepcopy(s['selecao']);r['regiao']=deepcopy(s['regiao'])
                r['estados_selecao']={n: ('reutilizado_com_vinculo' if steps.get(n,{}).get('processamento')=='reuso_cache' else 'interpretado') if n in validos else 'bloqueado_por_limite' if steps.get(n,{}).get('motivo','').startswith('Limite') else 'pendente' if n in s['regiao']['nos'] else 'fora_do_escopo_justificado' for n in seq}
                r['cobertura']['nos_exigidos']=len(s['regiao']['nos']);r['cobertura']['pendentes']=deepcopy(s['pendentes'])
                s['dependencias_pendentes']={n:sorted(pred[n]&set(s['pendentes'])) for n in s['pendentes']}
                s['resultado']=r
                s['estado']='cancelada' if self.caminho(sid,'.cancelar').exists() else 'pausada' if s['pendentes'] else 'concluida'
                if r['execucao']['estado']=='erro':s['estado']='falha'
            finally:
                s['consumo']['segundos']=antes+perf_counter()-t0
                if s.get('resultado'):s['resultado']['consumo_acumulado']=deepcopy(s['consumo'])
                s['revisao']+=1;self.salvar(s)
            return s

    def sugestao(self,sid,pedido_id,transporte):
        with self.lock(sid):
            s=self.ler(sid)
            if s['estado']!='pronta':raise ValueError('Peça sugestão antes de iniciar a análise.')
            if s['cancelamento_solicitado']:raise ValueError('Análise cancelada.')
            real=s.get('modo','simulacao_offline')=='ia_real'
            if getattr(transporte,'origem',None)!=('openai_real' if real else 'simulado'):raise ValueError('Transporte incompatível com modo da sessão.')
            g,d=carregar();e=projetar(g,d);c,f=dados_sessao(s);ev=normalizar(c,e)
            if assinatura(g,d,c,f)!=s['assinatura']:raise ValueError('Dados/fontes/código mudaram; crie nova sessão.')
            # Cache consultado primeiro não reserva uma segunda solicitação.
            pedido=dict(evento_id=ev['evento_id'],versao=ev['versao_projeto'],relato=ev['relato'],catalogo=selecao.catalogo(g))
            key=hash_json([pedido_id,pedido])
            if key not in s['sugestoes'] and limite_consumo(s,real=real):raise ValueError(limite_consumo(s,real=real)+'; inclui a sugestão.')
            # A tentativa conta mesmo se o transporte/formato falhar.
            novo=key not in s['sugestoes']
            if novo and s['consumo']['segundos']>=s['limites']['max_segundos']:
                raise ValueError('Limite acumulado de tempo inclui a sugestão.')
            snap=snapshot_real(transporte) if real and novo else None
            if snap and snap.get('uso_desconhecido'):raise ValueError('Uso real desconhecido; sugestão bloqueada.')
            s['selecao_confirmada']=False
            if novo:s['consumo']['solicitacoes_reais' if real else 'solicitacoes_simuladas']+=1;self.salvar(s)
            inicio=perf_counter()
            try:r,_=selecao.sugerir(ev,g,transporte,cache=s['sugestoes'],pedido_id=pedido_id,modo='ia_real' if real else 'simulacao_offline')
            finally:
                s['consumo']['segundos']+=perf_counter()-inicio
                if snap is not None:contabilizar_real(s,snap,transporte)
                self.salvar(s)
            return r

    def selecionar(self,sid,entradas,max_nos,*,escopo='impacto_do_evento',confirmar_divergencia=False,origem='engenheiro'):
        with self.lock(sid):
            s=self.ler(sid)
            if s['estado']!='pronta' or s['cancelamento_solicitado']:raise ValueError('Seleção inicial já encerrada.')
            if origem not in ('engenheiro','ia_autorizada_pelo_usuario'):raise ValueError('Origem da seleção inválida.')
            g,d=carregar();e=projetar(g,d);c,f=dados_sessao(s);ev=normalizar(c,e)
            if assinatura(g,d,c,f)!=s['assinatura']:raise ValueError('Dados/fontes/código mudaram; crie nova sessão.')
            sel=selecao.validar(g,ev,entradas,max_nos,e['versao'],escopo)
            if sel['mencoes_fora_da_selecao'] and (escopo!='teste_delimitado' or not confirmar_divergencia):
                raise ValueError('Confirme teste delimitado ou inclua todas as menções do evento.')
            sel['total_nos_grafo']=len(grafo_documental(g,d,c)['nodes'])
            s['selecao']=sel;s['regiao']=alcance.construir(e,ev,g,entradas);s['pendentes']=s['regiao']['nos'];s['revisao']+=1
            s['selecao_confirmada']=True
            s.setdefault('historico_selecoes',[]).append(dict(origem=origem,selecao=deepcopy(sel),sugestoes_consideradas=sorted(s['sugestoes'])))
            self.salvar(s);return s
