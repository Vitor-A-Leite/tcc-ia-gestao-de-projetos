from copy import deepcopy
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from piloto_real import MODELO,CONFIG
from piloto_real.ledger import Ledger,Bloqueio,RESERVA,PROVISAO_CONTAGEM
from piloto_real.transporte import Responses,custo_usage,sanitizar
from piloto_real.runner import preparar,executar
from piloto_real.politica import construir
from interpretacao_no import LLM
from interpretacao_no.contratos import hash_json,montar_contexto
from interpretacao_no.adaptadores import FalhaTransporte
from orquestracao import avaliar
from condicoes.baseline import Global
from piloto_real.chave import configurar,presente,carregar

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/desenvolvimento'


def uso(i=100,o=10,cached=0,write=0,reasoning=2):
    return dict(input_tokens=i,output_tokens=o,total_tokens=i+o,input_tokens_details=dict(cached_tokens=cached,cache_write_tokens=write),output_tokens_details=dict(reasoning_tokens=reasoning))


def plano_min(n=40):return dict(slots=[dict(execucao_id='s'+str(j),condicao='H') for j in range(n)])


def envelope(texto='{}',status='completed',usage=True):
    d=dict(model=MODELO,status=status,id='resp_mock',output=[dict(type='message',content=[dict(type='output_text',text=texto)])])
    if usage:d['usage']=uso()
    return d


class HTTPFake:
    def __init__(self,response=None,n=100,fail=None):self.calls=[];self.response=response or envelope();self.n=n;self.fail=fail
    def post(self,path,payload,timeout):
        self.calls.append((path,deepcopy(payload),timeout))
        if self.fail==path:raise FalhaTransporte('timeout','Timeout sintético')
        return dict(object='response.input_tokens',input_tokens=self.n) if path else deepcopy(self.response)


def req():return dict(modelo=MODELO,configuracao=deepcopy(CONFIG),formato='json',timeout_s=30,mensagens=[dict(papel='sistema',conteudo='Responda JSON'),dict(papel='usuario',conteudo='{}')])


class Transporte(unittest.TestCase):
    def rodar(self,http):
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,plano_min()) as l:
            l.iniciar('s0');t=Responses(l,'s0',http)
            r=t(req());return r,l.resumo()
    def test_payload_e_contagem_oficial_antes(self):
        h=HTTPFake();r,c=self.rodar(h)
        self.assertEqual([x[0] for x in h.calls],['/input_tokens',''])
        count,payload=h.calls[0][1],h.calls[1][1]
        for k in ('model','input','text','reasoning'):self.assertEqual(count[k],payload[k])
        self.assertEqual(payload['max_output_tokens'],25000)
        self.assertEqual(payload['prompt_cache_options'],dict(ttl='30m'))
        self.assertEqual(payload['tools'],[]);self.assertFalse(payload['store'])
        self.assertEqual(r.estado,'completa');self.assertEqual(c['tentativas_reservadas'],1)
    def test_envelope_sem_echo_opcional_preserva_conteudo(self):
        r,c=self.rodar(HTTPFake(envelope('{"resposta":1}')))
        self.assertEqual(r.texto,'{"resposta":1}');self.assertEqual(c['custos_desconhecidos'],0)
        self.assertEqual(set(r.metadados['ecos_opcionais_ausentes']),{'service_tier','prompt_cache_options'})
    def test_usage_ausente_nao_apaga_resposta(self):
        r,c=self.rodar(HTTPFake(envelope('original',usage=False)))
        self.assertEqual(r.texto,'original');self.assertIsNone(r.tokens_saida)
        self.assertEqual(c['comprometido_nanoUSD'],RESERVA)
    def test_modelo_diferente_preserva_original_paralisa_novas(self):
        e=envelope('original');e['model']='outro-modelo'
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,plano_min()) as l:
            l.iniciar('s0');r=Responses(l,'s0',HTTPFake(e))(req())
            self.assertEqual(r.texto,'original');self.assertEqual(r.modelo,'outro-modelo')
            l.iniciar('s1')
            with self.assertRaises(Bloqueio):l.reservar('s1','h')
            self.assertEqual(l.resumo()['custos_desconhecidos'],1)
    def test_incomplete_e_recusa_conservam_usage_e_bruto(self):
        e=envelope('parcial',status='incomplete');r,c=self.rodar(HTTPFake(e))
        self.assertEqual(r.estado,'incompleta');self.assertEqual(r.metadados['response']['status'],'incomplete')
        self.assertEqual(c['custos_desconhecidos'],0)
        e=envelope();e['output'][0]['content']=[dict(type='refusal',refusal='não')]
        r,_=self.rodar(HTTPFake(e));self.assertEqual(r.estado,'recusa')
    def test_contagem_excessiva_nao_infere(self):
        h=HTTPFake(n=16001)
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,plano_min()) as l:
            l.iniciar('s0')
            with self.assertRaisesRegex(FalhaTransporte,'16.000'):Responses(l,'s0',h)(req())
            self.assertEqual([x[0] for x in h.calls],['/input_tokens'])
            self.assertEqual(l.resumo()['comprometido_nanoUSD'],RESERVA)
    def test_timeout_sem_retry_retencao_persistente(self):
        with tempfile.TemporaryDirectory() as tmp:
            h=HTTPFake(fail='')
            with Ledger(tmp,plano_min()) as l:
                l.iniciar('s0')
                with self.assertRaises(FalhaTransporte):Responses(l,'s0',h)(req())
                self.assertEqual(l.resumo()['comprometido_nanoUSD'],RESERVA)
            with Ledger(tmp,plano_min()) as l:self.assertEqual(l.resumo()['comprometido_nanoUSD'],RESERVA)
            self.assertEqual(len(h.calls),2)
    def test_uso_detalhado_sem_dupla_contagem(self):
        u=uso(i=12000,o=1000,cached=4000,write=7000,reasoning=800)
        u['input_tokens_details']['cache_write_tokens_details']=dict(ttl_30m_tokens=7000,ttl_12h_tokens=0)
        self.assertEqual(custo_usage(u),1000*100+4000*10+7000*125+1000*500)
        for change in ('12h','overlap','reasoning'):
            v=deepcopy(u)
            if change=='12h':v['input_tokens_details']['cache_write_tokens_details']=dict(ttl_30m_tokens=0,ttl_12h_tokens=7000)
            if change=='overlap':v['input_tokens_details']['cached_tokens']=6000
            if change=='reasoning':v['output_tokens_details']['reasoning_tokens']=2000
            with self.assertRaises(ValueError):custo_usage(v)


class Orçamento(unittest.TestCase):
    def test_300_reservas_agregadas_e_retomada(self):
        p=plano_min()
        with tempfile.TemporaryDirectory() as tmp:
            with Ledger(tmp,p) as l:
                for j in range(38):l.iniciar('s'+str(j))
                for j in range(300):l.reservar('s'+str(j//8),'hash')
                self.assertEqual(l.resumo()['comprometido_nanoUSD'],4_950_000_000)
                with self.assertRaises(Bloqueio):l.reservar('s37','mais')
            with Ledger(tmp,p) as l:
                self.assertEqual(l.resumo()['tentativas_reservadas'],300)
                with self.assertRaises(Bloqueio):l.reservar('s37','mais')
    def test_concorrencia_plano_e_conciliacao_duplicada(self):
        with tempfile.TemporaryDirectory() as tmp:
            with Ledger(tmp,plano_min()) as l:
                with self.assertRaises(Bloqueio):Ledger(tmp,plano_min())
                l.iniciar('s0');i=l.reservar('s0','h');l.contar(i,100);l.enviar(i);l.concluir(i,10000,uso(),{})
                with self.assertRaises(Bloqueio):l.concluir(i,10000,uso(),{})
                self.assertEqual(l.resumo()['comprometido_nanoUSD'],PROVISAO_CONTAGEM+10000)
            with self.assertRaises(Bloqueio):Ledger(tmp,{'slots':[]})


def analise(c,propostas=()):
    q=dict(estado='indeterminado',valor=None,direcao='desconhecida',evidencias=[],lacunas=['Magnitude local não fornecida'],motivo=None)
    a={k:deepcopy(c[k]) for k in ('execucao_id','evento_id','no_id','revisao','contexto_hash','predecessores_versoes')}
    a.update(schema_version='1.0-proposta',analise_id='a_'+c['no_id'],avaliacao=dict(prazo=q,custo=deepcopy(q)),propostas=list(propostas),justificativa='Interpretação mock sem correção por gabarito',lacunas=[])
    return a


class Politica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plano,_,cls.casos=preparar(DATA)
    def test_90_slots_pares_modelo_e_contextos_positivos(self):
        self.assertEqual(len(self.plano['slots']),90)
        for caso in self.casos.values():
            p=construir(caso['estado'],caso['evento'],execucao_id='t')
            self.assertEqual(set(p.plano),{n['id'] for n in caso['estado']['entidades']})
            for n,sel in p.plano.items():
                c=montar_contexto(caso['estado'],caso['evento'],execucao_id='t',no_id=n,revisao=1,**sel)
                text=json.dumps(c)
                for proibido in ('gabaritos','propostas_por_no','derivacao_manual','familia_id'):self.assertNotIn(proibido,text)
                self.assertEqual(c['evento']['relato'],caso['evento']['relato'])
    def test_H_valido_sem_fixtures_calcula_e_preserva_interpretacao_errada(self):
        # Mock muda duração de acordo com operação permitida, sem buscar referência.
        caso=self.casos['k_98f3'];p=construir(caso['estado'],caso['evento'],execucao_id='s0')
        def transporte(request):
            c=json.loads(request['mensagens'][1]['conteudo'])['contexto'];a=analise(c)
            if c['no_id']=='n_21dc':
                evref=next(dict(fonte_id=f['id'],localizador=f['localizador']) for f in c['fontes'] if f['trecho']==c['evento']['relato'])
                v=dict(estado='exato',valor=9,direcao='desconhecida',evidencias=[evref],lacunas=[],motivo=None)
                a['propostas']=[dict(id='z1',no_id=c['no_id'],operacao='substituir_duracao',alvo_id=c['no_id'],atributo='duracao',valor=v,unidade='dia_corrido',evidencias=[evref],relacao_refs=[],regra_refs=[],condicoes=[],origens_causais=[dict(evento_id=c['evento_id'],fato_ref=evref,efeito_id=hash_json([c['evento_id'],c['no_id']]))])]
            from interpretacao_no.adaptadores import RespostaTransporte
            return RespostaTransporte(json.dumps(a),modelo=MODELO,tokens_entrada=100,tokens_saida=100)
        i=LLM(transporte,modelo=MODELO,configuracao=CONFIG,timeout_s=30)
        r=avaliar(caso['estado'],caso['evento'],i,p)
        self.assertEqual(r['execucao']['estado'],'ok')
        self.assertEqual((r['delta_dias']['valor'],r['delta_centavos']['valor']),(6,45000))
        self.assertEqual(r['suporte_semantico'],'nao_auditado')
        self.assertEqual(r['natureza_previsao'],'condicional_original')
        self.assertFalse(p.verificar_fechamento())
        self.assertEqual(p.registro_operacional['fechamento_final']['estado'],'completo_operacional_condicional')
        self.assertNotIn('manual auditável',json.dumps(r,ensure_ascii=False))
    def test_omissao_no_ou_obrigacao_impede_fechamento(self):
        from orquestracao.simulacao import InterpretadorPrescrito
        # Simulado é só transporte de teste, sem fixture/IDs-resposta externos.
        for cid in ('k_b5e1','k_98f3'):
            caso=self.casos[cid];p=construir(caso['estado'],caso['evento'],execucao_id='x')
            from interpretacao_no import Simulado
            class Mock:
                origem='simulado'
                def analisar(_,c):return Simulado(analise(c)).analisar(c)
            if cid=='k_98f3':p.plano.pop(next(iter(p.plano)))
            r=avaliar(caso['estado'],caso['evento'],Mock(),p)
            self.assertEqual(r['execucao']['estado'],'parcial')
            self.assertIsNone(r['delta_dias']['valor'])
            self.assertTrue(p.verificar_fechamento())


def resposta_mock(payload):
    """Contrato dinâmico de teste, sem leitura de gabaritos ou fixtures."""
    entrada=json.loads(payload['input'][1]['content'])
    if 'contexto' in entrada:
        c=entrada['contexto'];a=analise(c)
        fonte=next(f for f in c['fontes'] if f['trecho']==c['evento']['relato']);evref=dict(fonte_id=fonte['id'],localizador=fonte['localizador'])
        def prop(op,alvo,attr,v,un,regras=(),conds=()):
            return dict(id='prop_'+c['no_id']+'_'+str(len(a['propostas'])),operacao=op,alvo_id=alvo,atributo=attr,valor=v,unidade=un,evidencias=[evref],relacao_refs=[],regra_refs=list(regras),condicoes=list(conds),no_id=c['no_id'],origens_causais=[dict(evento_id=c['evento_id'],fato_ref=evref,efeito_id=entrada['efeitos_canonicos'][alvo])])
        for r in c['regras']:
            if 'operacoes_permitidas' in r:
                cond=[dict(predicado='aplicabilidade_'+r['id'],estado='confirmada',evidencias=[evref])]
                for op in r['operacoes_permitidas']:
                    ausencia=op=='confirmar_ausencia_parcela_adicional';a['propostas'].append(prop(op,c['no_id'],'readequacao' if ausencia else 'duracao',0 if ausencia else c['no']['atributos']['duracao']['valor'],'BRL_centavo' if ausencia else 'dia_corrido',[r['id']],cond))
                    if ausencia:a['avaliacao']['custo']=dict(estado='exato',valor=0,direcao='zero',evidencias=[evref],lacunas=[],motivo=None)
        for ob in c['obrigacoes']:
            if not ob.startswith('lacuna_'):
                valor=dict(estado='indeterminado',valor=None,direcao='desconhecida',evidencias=[evref],lacunas=['Preço não determinado pelo mock'],motivo=None)
                a['propostas'].append(prop('registrar_lacuna_custo',ob,'valor_centavos',valor,'BRL_centavo'))
        return a
    c=entrada;view=c['view'];b=view['comum']['linha_base_declarada'];f=view['comum']['fontes'][0];ref=dict(fonte_id=f['id'],localizador=f['localizador'])
    a={k:c[k] for k in ('execucao_id','projeto_id','versao','evento_id','view_hash')}
    for campo,v in [('fim_base',b['fim_dia']),('fim_novo',b['fim_dia']),('delta_dias',0),('custo_base',b['custo_centavos']),('custo_novo',b['custo_centavos']),('delta_centavos',0)]:
        a[campo]=dict(estado='exato',valor=v,direcao='zero' if campo.startswith('delta_') else 'desconhecida',evidencias=[ref],lacunas=[],motivo=None,unidade='dia_corrido' if campo in ('fim_base','fim_novo','delta_dias') else 'BRL_centavo')
    a['justificativa']='MOCK: respostas originais sem correção por referência'
    return a


class HTTPDinamico(HTTPFake):
    def post(self,path,payload,timeout):
        self.calls.append((path,None,timeout))
        if path:return dict(object='response.input_tokens',input_tokens=100)
        return envelope(json.dumps(resposta_mock(payload)))


class Runner(unittest.TestCase):
    def test_integra_90_slots_validos_sem_IA_real_e_sem_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            h=HTTPDinamico();r=executar(DATA,tmp,http=h,coletar=True)
            for c in 'BHT':
                self.assertEqual(r['por_condicao'][c]['N'],30)
                self.assertEqual(r['por_condicao'][c]['persistidos'],30)
                self.assertNotIn('erro',r['por_condicao'][c]['estados'])
            self.assertLessEqual(r['orcamento']['tentativas_reservadas'],300)
            self.assertLess(r['orcamento']['comprometido_nanoUSD'],5*10**9)
            n=len(h.calls);depois=executar(DATA,tmp,http=h,coletar=True)
            self.assertEqual(len(h.calls),n)
            self.assertEqual(r,depois)
            arquivos=list(Path(tmp).glob('etapa9-*.json'));self.assertEqual(len(arquivos),90)
            k=next(json.loads(p.read_text()) for p in arquivos if '-k_98f3-B-' in p.name)
            # Erro semântico do mock permanece original; o runner não troca por−2.
            self.assertEqual(k['resultado']['delta_dias']['valor'],0)
            self.assertEqual(k['resultado']['suporte_semantico'],'nao_auditado')
    def test_slot_iniciado_interrompido_nao_reenvia(self):
        plano,_,_=preparar(DATA)
        with tempfile.TemporaryDirectory() as tmp:
            with Ledger(tmp,plano) as l:l.iniciar(plano['slots'][0]['execucao_id'])
            h=HTTPDinamico();r=executar(DATA,tmp,http=h,coletar=True)
            slot=json.loads((Path(tmp)/(plano['slots'][0]['execucao_id']+'.json')).read_text())
            self.assertEqual(slot['resultado']['execucao']['erros'][0]['codigo'],'INTERROMPIDO_SEM_REPLAY')
            self.assertEqual(sum(v['persistidos'] for v in r['por_condicao'].values()),90)
    def test_preparar_sem_chave_e_sem_rede(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=executar(DATA,tmp,coletar=False)
            self.assertEqual(r['slots'],90)
            self.assertEqual(r['orcamento']['tentativas_reservadas'],0)


class Segredo(unittest.TestCase):
    def test_configurador_oculto_0600_nao_sobrescreve_e_check_sem_ler(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'.env.piloto'
            with patch('sys.stdin.isatty',return_value=True),patch('getpass.getpass',return_value='sk-SINTETICA_NAO_REAL'),patch('builtins.print') as saida:
                configurar(p)
            self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
            self.assertNotIn('sk-SINTETICA',str(saida.call_args_list))
            with patch.dict(os.environ,{},clear=True):
                with patch.object(Path,'read_text',side_effect=AssertionError('não ler valor no check')):self.assertTrue(presente(p))
                self.assertEqual(carregar(p),'sk-SINTETICA_NAO_REAL')
            with patch('sys.stdin.isatty',return_value=True),patch('getpass.getpass',return_value='outro'):
                with self.assertRaises(FileExistsError):configurar(p)
            p.chmod(0o644)
            with patch.dict(os.environ,{},clear=True):
                with self.assertRaises(ValueError):carregar(p)
    def test_sem_tty_e_symlink_recusados(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'.env.piloto'
            with patch('sys.stdin.isatty',return_value=False):
                with self.assertRaises(ValueError):configurar(p)
            target=Path(tmp)/'target';target.write_text('OPENAI_API_KEY=sk-FAKE');target.chmod(0o600);p.symlink_to(target)
            with patch.dict(os.environ,{},clear=True):
                with self.assertRaises(ValueError):carregar(p)
    def test_gitignore_protege_caminho_sem_criar_segredo(self):
        repo=ROOT.parent
        r=subprocess.run(['git','check-ignore','--no-index',str(repo/'.env.piloto')],cwd=repo,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
    def test_redacao_em_bruto_usage_e_headers(self):
        segredo='chave-SINTETICA-nao-real';body=envelope(segredo)
        body['headers']={'Authorization':'Bearer '+segredo};body['outro']=segredo
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,plano_min()) as l:
            l.iniciar('s0');r=Responses(l,'s0',HTTPFake(body),redator=lambda x:sanitizar(x,segredo))(req())
            self.assertNotIn(segredo,json.dumps(r.metadados))
            self.assertNotIn(segredo,(Path(tmp)/'ledger.sqlite').read_bytes().decode('latin1'))
            self.assertNotIn('Authorization',json.dumps(r.metadados))


def _worker_lento(pipe,path,payload,chave,timeout):
    import time
    time.sleep(5)


class Deadline(unittest.TestCase):
    def test_deadline_inclui_worker_bloqueado_sem_rede(self):
        from piloto_real.transporte import HTTP
        from time import monotonic
        inicio=monotonic()
        with patch('piloto_real.transporte._http_worker',_worker_lento):
            with self.assertRaises(FalhaTransporte):HTTP('SINTETICA').post('/input_tokens',{},0.05)
        self.assertLess(monotonic()-inicio,2)


class FechamentoEParada(unittest.TestCase):
    def test_regra_local_sem_proposta_nao_vira_zero(self):
        _,_,casos=preparar(DATA);c=casos['k_b731'];p=construir(c['estado'],c['evento'],execucao_id='x')
        from interpretacao_no import Simulado
        class Mock:
            origem='simulado'
            def analisar(_,ctx):return Simulado(analise(ctx)).analisar(ctx)
        r=avaliar(c['estado'],c['evento'],Mock(),p)
        self.assertEqual(r['execucao']['estado'],'parcial')
        self.assertIsNone(r['delta_dias']['valor'])
        self.assertTrue(any('Regra local' in x for x in p.verificar_fechamento()))
        self.assertEqual(p.registro_operacional['fechamento_final']['estado'],'parcial')
    def test_teto_por_slot_e_usd_efetivo(self):
        p=plano_min()
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,p) as l:
            l.iniciar('s0')
            for _ in range(8):l.reservar('s0','x')
            with self.assertRaises(Bloqueio):l.reservar('s0','x')
            # Ledger inteiro em custo desconhecido próximo ao teto: recusa antes de HTTP.
            l.iniciar('s1')
            with l.db:l.db.execute('UPDATE chamadas SET comprometido=? WHERE id=1',(4_990_000_000,))
            h=HTTPFake()
            with self.assertRaises(FalhaTransporte):Responses(l,'s1',h)(req())
            self.assertEqual(h.calls,[])
    def test_orcamento_bloqueado_preserva_todos_os90_slots(self):
        p,_,_=preparar(DATA)
        with tempfile.TemporaryDirectory() as tmp:
            with Ledger(tmp,p) as l:l.parar('Teste sintético de bloqueio')
            h=HTTPDinamico();r=executar(DATA,tmp,http=h,coletar=True)
            self.assertFalse(h.calls)
            self.assertEqual(sum(v['persistidos'] for v in r['por_condicao'].values()),90)
            for v in r['por_condicao'].values():self.assertTrue(v['estados'].get('erro',0)+v['estados'].get('parcial',0)==30)
    def test_payload_config_errada_nao_reserva_nem_envia(self):
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,plano_min()) as l:
            l.iniciar('s0');h=HTTPFake();r=req();r['configuracao']['max_output_tokens']=26000
            with self.assertRaises(FalhaTransporte):Responses(l,'s0',h)(r)
            self.assertFalse(h.calls);self.assertEqual(l.resumo()['tentativas_reservadas'],0)


class FalhaProvider(unittest.TestCase):
    def test_erro_provider_sanitizado_e_modelo_ausente_preserva_texto(self):
        class Negado:
            def post(self,*args):raise FalhaTransporte('http','Falha HTTP sanitizada',metadados={'status_http':401,'provider_code':'invalid_api_key'})
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,plano_min()) as l:
            l.iniciar('s0')
            with self.assertRaises(FalhaTransporte):Responses(l,'s0',Negado())(req())
            registro=json.loads(l.db.execute('SELECT registro FROM chamadas').fetchone()[0])
            self.assertEqual(registro['falha_transporte']['provider_code'],'invalid_api_key')
            l.iniciar('s1')
            with self.assertRaises(Bloqueio):l.reservar('s1','outra')
        e=envelope('resposta');del e['model']
        with tempfile.TemporaryDirectory() as tmp,Ledger(tmp,plano_min()) as l:
            l.iniciar('s0');r=Responses(l,'s0',HTTPFake(e))(req())
            self.assertEqual(r.texto,'resposta');self.assertIsNone(r.modelo)
