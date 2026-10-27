"""Adaptador H v05 injetável; sem HTTP/chave, sem retries ou normalização permissiva."""
from copy import deepcopy
from time import perf_counter
import json
from interpretacao_no.adaptadores import LLM as Anterior,RespostaTransporte,FalhaTransporte,_json
from interpretacao_no.contratos import exigir,numero,texto,ContratoInvalido,hash_json
from .contratos import validar,VERSAO
from .formato import SISTEMA,compilar
class LocalV05(Anterior):
    versao_formato_local=VERSAO
    def __init__(self,transporte,*,modelo,configuracao,timeout_s):
        if getattr(transporte,'versao_formato_local',None)!=VERSAO:raise ValueError('Transporte não vinculado ao contrato H v05; carteira paga v04 não é compatível')
        super().__init__(transporte,modelo=modelo,configuracao=configuracao,timeout_s=timeout_s,repetir_transporte=False)
    def analisar(self, contexto_no):
        c = deepcopy(contexto_no)
        exigir(c['contexto_hash'] == hash_json({k: v for k, v in c.items() if k != 'contexto_hash'}), 'Contexto adulterado')
        inicio, tentativas, resultado = perf_counter(), [], None
        erro = None
        alvos = {p['alvo_id'] for p in c['permissoes']}
        dados = dict(contexto=c, efeitos_canonicos={a: hash_json([c['evento_id'], a]) for a in sorted(alvos)})
        dados['contrato_resposta']=compilar(c,dados['efeitos_canonicos'])
        request = dict(versao_formato_local=VERSAO,modelo=self.modelo, configuracao=deepcopy(self.configuracao),
                       timeout_s=self.timeout_s, formato='json',
                       mensagens=[dict(papel='sistema', conteudo=SISTEMA),
                                  dict(papel='usuario', conteudo=json.dumps(dados, ensure_ascii=False, allow_nan=False))])
        for tentativa in range(1):
            t0 = perf_counter()
            registro = dict(tentativa=tentativa + 1, tokens_entrada=None, tokens_saida=None,
                            custo_api_centavos=None, modelo=None, request_id=None)
            try:
                r = self.transporte(deepcopy(request))
                exigir(isinstance(r, RespostaTransporte), 'Envelope de transporte inválido')
                for k in ('tokens_entrada', 'tokens_saida', 'custo_api_centavos'):
                    v = getattr(r, k)
                    if v is not None:
                        numero(v, 0)
                    registro[k] = v
                registro.update(modelo=r.modelo, request_id=r.request_id, metadados=deepcopy(r.metadados),
                                estado=r.estado, resposta_bruta=r.texto)
                exigir(r.estado in ('completa', 'recusa', 'incompleta'), 'Estado de transporte inválido')
                if r.estado != 'completa':
                    erro = dict(codigo=r.estado, mensagem='Transporte não entregou análise completa')
                    break
                exigir(isinstance(r.texto, str), 'Conteúdo ausente')
                resultado = _json(r.texto)
                decisoes = validar(resultado, c)
                break
            except (FalhaTransporte, TimeoutError) as exc:
                codigo = exc.codigo if isinstance(exc, FalhaTransporte) else 'timeout'
                erro = dict(codigo=codigo, mensagem=str(exc))
                registro.update(estado='erro', erro=deepcopy(erro), metadados=getattr(exc, 'metadados', {}))
                transitoria = isinstance(exc, TimeoutError) or exc.transitoria
                if tentativa == 0 and self.repetir and transitoria:
                    erro = None
                    continue
                break
            except (ContratoInvalido, ValueError, TypeError, KeyError) as exc:
                erro = dict(codigo='saida_invalida', mensagem=str(exc))
                registro['estado'] = 'saida_invalida'
                break
            except Exception as exc:
                # Falha não classificada do transporte não admite repetição automática.
                erro = dict(codigo='transporte_erro', mensagem=str(exc))
                registro.update(estado='erro', erro=deepcopy(erro))
                break
            finally:
                registro['latencia_ms'] = round((perf_counter() - t0) * 1000, 3)
                tentativas.append(registro)
        execucao = dict(estado='erro' if erro else 'ok', modelo=self.modelo,
                        config_hash=hash_json(self.configuracao), configuracao=deepcopy(self.configuracao),
                        origem='llm_transporte_injetado',versao_formato_local=VERSAO,requisicao_adaptador_hash=hash_json(request),chamadas=len(tentativas), tentativas=tentativas,
                        latencia_ms=round((perf_counter() - inicio) * 1000, 3),
                        timeout_s=self.timeout_s, repetir_transporte=self.repetir,
                        erros=[erro] if erro else [])
        for k in ('tokens_entrada', 'tokens_saida', 'custo_api_centavos'):
            valores = [x[k] for x in tentativas]
            execucao[k] = sum(valores) if all(v is not None for v in valores) else None
        if erro:
            return dict(analise_id=None, execucao_id=c['execucao_id'], evento_id=c['evento_id'],
                        no_id=c['no_id'], revisao=c['revisao'], contexto_hash=c['contexto_hash'],
                        predecessores_versoes=deepcopy(c['predecessores_versoes']),
                        avaliacao=None, propostas=[], decisoes=[], execucao=execucao)
        resultado['decisoes'] = decisoes
        resultado['execucao'] = execucao
        return resultado


class SimuladoV05:
    origem='simulado'
    def __init__(self,resposta):self.resposta=resposta
    def analisar(self,c):
        a=self.resposta(deepcopy(c))if callable(self.resposta)else deepcopy(self.resposta)
        class Transporte:
            versao_formato_local=VERSAO
            def __call__(self,req):return RespostaTransporte(json.dumps(a,allow_nan=False))
        r=LocalV05(Transporte(),modelo='mock-v05',configuracao={},timeout_s=1).analisar(c)
        r['execucao'].update(origem='simulado',modelo=None,config_hash=None,configuracao={},chamadas=0,tokens_entrada=0,tokens_saida=0,custo_api_centavos=0,tentativas=[])
        return r
