"""MOCKS offline; nunca lê chave ou chama API. Sem gabarito de previsão."""
from copy import deepcopy
import io,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from retomada_v04_sse import *
from retomada_v04_sse.parser import ParserSSE,ErroSSE,ler_sse
from retomada_v04_sse.transporte import ResponsesSSE,LocalSSE
from retomada_v04_sse.http import worker,HTTPStreaming
from interpretacao_no.adaptadores import FalhaTransporte
from piloto_real import MODELO,CONFIG
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/etapa9_retomada_v04_20261026'
USAGE=dict(input_tokens=100,output_tokens=50,total_tokens=150,input_tokens_details=dict(cached_tokens=0,cache_write_tokens=0),output_tokens_details=dict(reasoning_tokens=10))
def response(status='completed',usage=True,refusal=False):
    r=dict(id='resp_mock',object='response',status=status,model=MODELO,output=[dict(type='message',content=[dict(type='refusal',refusal='Recusa MOCK')if refusal else dict(type='output_text',text='{"somente":"terminal MOCK"}')])],error=None,incomplete_details=None)
    if usage:r['usage']=deepcopy(USAGE)
    if status=='failed':r['error']={'code':'server_error','message':'MOCK'}
    if status=='incomplete':r['incomplete_details']={'reason':'max_output_tokens'}
    return r

def evento(r,tipo=None,crlf=False,multiline=False):
    tipo=tipo or 'response.'+r['status'];obj=dict(type=tipo,response=r);s=json.dumps(obj,ensure_ascii=False,indent=2 if multiline else None);nl='\r\n'if crlf else '\n'
    return ('event: '+tipo+nl+''.join('data: '+l+nl for l in s.splitlines())+nl).encode()
def parse(wire,fragment=17):
    p=ParserSSE()
    for i in range(0,len(wire),fragment):
        r=p.feed(wire[i:i+fragment])
        if r is not None:return r,p
    return p.eof(),p
class SSE(unittest.TestCase):
    def test_completed_response_igual_usage_e_sem_remontar_deltas(self):
        r=response();delta=b'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"IGNORAR ISTO"}\n\n'
        got,p=parse(delta+evento(r),1);self.assertEqual(got,r);self.assertEqual(got['usage'],USAGE);self.assertNotIn('IGNORAR',json.dumps(got));self.assertEqual(p.terminal,'response.completed')
    def test_fragmentos_utf8_bom_multilinha_crlf_comentarios(self):
        r=response();r['output'][0]['content'][0]['text']='ação São Paulo'
        wire=b'\xef\xbb\xbf: keepalive\r\n\r\n'+evento(r,crlf=True,multiline=True)
        for n in (1,2,7,16384):self.assertEqual(parse(wire,n)[0],r)
    def test_eof_truncamento_e_utf8_nao_reparam(self):
        for wire in (b'',b'data: {"type":"response.output_text.delta","delta":"parcial"}\n\n',evento(response())[:-1],b'data: \xff\n\n',b'data: \xc3'):
            with self.subTest(wire=wire[:20]):
                with self.assertRaises(ErroSSE):parse(wire)
    def test_failed_incomplete_com_uso_legitimo_sem_sucesso(self):
        for status in ('failed','incomplete'):
            r=response(status);got,p=parse(evento(r));self.assertEqual(got,r);self.assertEqual(p.terminal,'response.'+status)
    def test_refusal_exige_terminal_nao_e_texto_parcial(self):
        delta=b'data: {"type":"response.refusal.delta","delta":"MOCK"}\n\n'
        self.assertEqual(parse(delta+evento(response(refusal=True)))[0]['output'][0]['content'][0]['type'],'refusal')
        with self.assertRaises(ErroSSE):parse(delta)
        with self.assertRaises(ErroSSE):parse(delta+evento(response()))
    def test_error_sanitizado_e_json_malformado(self):
        for wire in (b'event: error\ndata: {"type":"error","message":"SEGREDO_MOCK","code":"server_error"}\n\n',b'data: {\n\n',b'event: response.failed\ndata: {"type":"response.completed"}\n\n',b'data: {"type":"x","type":"x"}\n\n',b'data: [DONE]\n\n'):
            try:parse(wire);self.fail('Deveria falhar')
            except ErroSSE as e:self.assertNotIn('SEGREDO_MOCK',str(e)+json.dumps(e.metadados))
    def test_limites_memoria_e_eventos(self):
        for p,wire in [(ParserSSE(max_total=5),b'abcdef'),(ParserSSE(max_evento=5),b'data:123456\n\n'),(ParserSSE(max_eventos=1),b'data: {"type":"x"}\n\ndata: {"type":"x"}\n\n')]:
            with self.assertRaises(ErroSSE):p.feed(wire)
    def test_prazo_fixo_nao_desliza_com_eventos(self):
        class Reader:
            def __init__(self):self.now=0
            def read1(self,n):self.now+=40;return b': heartbeat\n\n'
        r=Reader()
        with self.assertRaises(ErroSSE)as cm:ler_sse(r,180,agora=lambda:r.now)
        self.assertEqual(cm.exception.codigo,'timeout');self.assertEqual(r.now,200)
        class FinalTardio:
            now=0
            def read1(self,n):self.now=181;return evento(response())
        r=FinalTardio()
        with self.assertRaises(ErroSSE):ler_sse(r,180,agora=lambda:r.now)

class HTTPFake:
    def __init__(self,r):self.r=r;self.calls=[];self.ultimo_sse=None
    def post(self,path,payload,timeout):
        self.calls.append((path,deepcopy(payload),timeout))
        if path:return dict(object='response.input_tokens',input_tokens=100)
        if isinstance(self.r,Exception):raise self.r
        rr,p=parse(evento(self.r));self.ultimo_sse=p.resumo();return rr
class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name);shutil.copy(OUT/'snapshot_pos_execucao/ledger.sqlite',self.p/'ledger.sqlite');(self.p/'lote.lock').touch()
        self.pl,self.a,_=preparar_coorte(ROOT/'data/desenvolvimento');self.pro=preparar_offline(ROOT/'data/desenvolvimento',self.p,self.p/'preparo')
    def tearDown(self):self.tmp.cleanup()
    def abrir(self):return CarteiraSSE(self.p,self.pl,self.a,self.pro,liberacao_coordenador=True)
    def slot(self,l):return next(s for s in l.permitidos if l.novos[s]['condicao']=='B')
    def req(self):return dict(modelo=MODELO,configuracao=CONFIG,formato='json',timeout_s=180,mensagens=[dict(papel='sistema',conteudo='MOCK'),dict(papel='usuario',conteudo='{}')])
    def test_20_71_70_concorrencia_replay_e_liberacao(self):
        with self.assertRaises(Bloqueio):CarteiraSSE(self.p,self.pl,self.a,self.pro)
        self.assertEqual(self.pro['max_chamadas_novas'],219);self.assertEqual(self.pro['max_agregado'],290);self.assertEqual(self.pro['comprometido_max_nanoUSD'],4043831335)
        with self.abrir()as l:
            with self.assertRaises(Bloqueio):self.abrir()
            old=next(s for s,e,_ in l.resultados()if e=='terminado')
            with self.assertRaises(Bloqueio):l.iniciar(old)
            with self.assertRaises(Bloqueio):l.salvar(old,{})
            s=self.slot(l);l.iniciar(s)
            with self.assertRaises(Bloqueio):l.iniciar(s)
            l.conferir();l.parar('mock_stop')
        with self.abrir()as l:self.assertEqual(l.parada()[0],'mock_stop');l.conferir()
    def test_saldo_payload_stream_contagem_integra_e_hash(self):
        with self.abrir()as l:
            s=self.slot(l);l.iniciar(s);h=HTTPFake(response());t=ResponsesSSE(l,s,h,timeout_s=180);r=t(self.req())
            self.assertEqual(r.texto,'{"somente":"terminal MOCK"}');self.assertEqual(r.tokens_entrada,100)
            ct,p=h.calls[0][1],h.calls[1][1];self.assertNotIn('stream',ct);self.assertIs(p['stream'],True)
            self.assertEqual(ct,{k:p[k]for k in ('model','input','reasoning','text')});self.assertEqual(p['max_output_tokens'],25000);self.assertEqual(p['prompt_cache_options'],{'ttl':'30m'})
            id,hashr=l.db.execute('SELECT id,request_hash FROM chamadas ORDER BY id DESC LIMIT 1').fetchone();self.assertEqual(id,72);self.assertEqual(hashr,hash_json(p));self.assertNotEqual(hashr,hash_json({k:v for k,v in p.items()if k!='stream'}))
            self.assertEqual(l.resumo()['comprometido_nanoUSD'],430331335+2035000);l.conferir()
            with self.assertRaises(Bloqueio):l.reservar(s,'m')
    def test_terminais_e_usage_conservam_custos_sem_sucesso(self):
        # Uma cópia isolada por subcaso; nunca reenviar uma tentativa.
        for status,use in [('failed',True),('incomplete',True),('incomplete',False),('completed',False)]:
            with self.subTest(status=status,use=use):
                pp=self.p/(status+str(use));pp.mkdir();shutil.copy(OUT/'snapshot_pos_execucao/ledger.sqlite',pp/'ledger.sqlite')
                with CarteiraSSE(pp,self.pl,self.a,self.pro,liberacao_coordenador=True)as l:
                    s=self.slot(l);l.iniciar(s);r=ResponsesSSE(l,s,HTTPFake(response(status,use)),timeout_s=180)(self.req())
                    self.assertEqual(r.estado,'completa'if status=='completed'else 'incompleta');self.assertTrue(l.parada())
                    state,cost=l.db.execute('SELECT estado,custo_inferencia FROM chamadas ORDER BY id DESC LIMIT 1').fetchone();self.assertEqual(state,'conciliado'if use else 'custo_desconhecido');self.assertEqual(cost,35000 if use else None)
    def test_erro_sem_terminal_preserva_reserva_e_stop(self):
        with self.abrir()as l:
            s=self.slot(l);l.iniciar(s);h=HTTPFake(FalhaTransporte('sse_eof_sem_terminal','Falha SSE sanitizada'))
            with self.assertRaises(FalhaTransporte):ResponsesSSE(l,s,h,timeout_s=180)(self.req())
            self.assertEqual(len(h.calls),2);self.assertEqual(l.resumo()['comprometido_nanoUSD'],430331335+16500000);self.assertTrue(l.parada());l.conferir()
    def test_orcamento_e_cap300_bloqueiam(self):
        with self.abrir()as l:
            s=self.slot(l);l.iniciar(s)
            with l.db:l.db.execute("INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES('mock','m','reservado',5000000000)")
            with self.assertRaises(Bloqueio):l.reservar(s,'m')
            with l.db:
                l.db.execute('DELETE FROM chamadas WHERE id>71')
                l.db.executemany("INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES('mock','m','reservado',0)",[()for _ in range(229)])
            with self.assertRaises(Bloqueio):l.reservar(s,'m')
    def test_ancora_impede_mutacao_e_lista_alterada(self):
        with self.abrir()as l:
            with l.db:l.db.execute("UPDATE chamadas SET request_hash='mock_adulterado' WHERE id=71")
            with self.assertRaises(Bloqueio):l.iniciar(l.permitidos[0])
        self.pro['slots']=self.pro['slots'][:-1]
        with self.assertRaises(Bloqueio):self.abrir()
    def test_deadline_contagem_consume_mesmo_total180(self):
        clock=[0]
        class ClockHTTP(HTTPFake):
            def post(self,path,payload,timeout):
                r=super().post(path,payload,timeout)
                if path:clock[0]+=50
                return r
        with self.abrir()as l:
            s=self.slot(l);l.iniciar(s);h=ClockHTTP(response())
            with patch('retomada_v04_sse.transporte.monotonic',side_effect=lambda:clock[0]):ResponsesSSE(l,s,h,timeout_s=180)(self.req())
            self.assertEqual([x[2]for x in h.calls],[180,130])

class RevisaoDirecionada(unittest.TestCase):
    setUp=LedgerTests.setUp
    tearDown=LedgerTests.tearDown
    def test_runner_gated_isolado_marca_adendo_e_para_sem_retry(self):
        out=self.p/'runner'
        with self.assertRaises(Bloqueio):executar(ROOT/'data/desenvolvimento',self.p,out,self.pro,http=HTTPFake(response()),coletar=True)
        h=HTTPFake(FalhaTransporte('sse_eof_sem_terminal','Falha SSE sanitizada'))
        r=executar(ROOT/'data/desenvolvimento',self.p,out,self.pro,http=h,coletar=True,liberacao_coordenador=True)
        self.assertEqual(r['estados']['terminado'],21);self.assertEqual(r['estados']['pendente'],69);self.assertTrue(r['parada']);self.assertEqual(len(h.calls),2)
        paths=list(out.glob('etapa9-coorte-*.json'));self.assertEqual(len(paths),1);reg=json.loads(paths[0].read_text());self.assertEqual(reg['resultado']['adendo_transporte_sse']['transporte'],TRANSPORTE)
        self.assertIn(reg['metadados']['execucao_id'],self.pro['slots']);self.assertTrue(h.calls[-1][1]['stream'])
    def test_local_sse_mesmo_payload_menos_unica_chave_stream(self):
        import sys
        sys.path.insert(0,str(ROOT/'tests/etapa9_formato_v04'))
        from test_formato import contextos,base,WalletMock,HTTPMock
        from formato_local_v04 import LocalV04,ResponsesV04
        _,c=contextos([]);a=base(c);resp=response();resp['output'][0]['content'][0]['text']=json.dumps(a)
        old_h=HTTPMock(json.dumps(a));new_h=HTTPFake(resp);wo=WalletMock();wn=WalletMock()
        old=LocalV04(ResponsesV04(wo,'slot_formato_v04',old_h,timeout_s=180),modelo=MODELO,configuracao=CONFIG,timeout_s=180).analisar(c)
        new=LocalV04(LocalSSE(wn,'slot_formato_v04',new_h,timeout_s=180),modelo=MODELO,configuracao=CONFIG,timeout_s=180).analisar(c)
        self.assertEqual(new['execucao']['estado'],'ok');self.assertEqual(new['avaliacao'],old['avaliacao']);self.assertEqual(new['propostas'],old['propostas'])
        self.assertEqual(new_h.calls[0][1],old_h.calls[0][1]);gp=deepcopy(new_h.calls[1][1]);self.assertIs(gp.pop('stream'),True);self.assertEqual(gp,old_h.calls[1][1])
    def test_telemetria_anterior_limpa_antes_de_timeout_contagem(self):
        clock=[0];polls=[]
        class Pipe:
            def poll(self,timeout):polls.append(timeout);return False
            def close(self):pass
        class Process:
            def start(self):clock[0]+=2
            def is_alive(self):return True
            def terminate(self):pass
            def join(self,timeout):pass
        class Ctx:
            def Pipe(self,duplex):return Pipe(),Pipe()
            def Process(self,**kw):return Process()
        h=HTTPStreaming('DUMMY_SEM_CHAVE_REAL');h.ultimo_sse={'terminal':'anterior'}
        with patch('retomada_v04_sse.http.multiprocessing.get_context',return_value=Ctx()),patch('retomada_v04_sse.http.monotonic',side_effect=lambda:clock[0]):
            with self.assertRaises(FalhaTransporte):h.post('/input_tokens',{'model':MODELO},5)
        self.assertIsNone(h.ultimo_sse);self.assertEqual(polls,[3])

class WorkerSeguro(unittest.TestCase):
    class Pipe:
        def __init__(self):self.result=[]
        def send(self,x):self.result.append(x)
        def close(self):pass
    def test_contagem_http_json_identica_ao_worker_anterior(self):
        from piloto_real.transporte import _http_worker
        calls=[]
        class Conn:
            status=200
            def request(self,*a,**kw):calls.append((a,kw))
            def getresponse(self):return self
            def read(self,n):return b'{"object":"response.input_tokens","input_tokens":123}'
            def close(self):pass
        old=self.Pipe();new=self.Pipe();payload={'model':MODELO,'input':[]}
        with patch('retomada_v04_sse.http.http.client.HTTPSConnection',return_value=Conn()):
            _http_worker(old,'/input_tokens',payload,'DUMMY_NAO_REAL',180)
            worker(new,'/input_tokens',payload,'DUMMY_NAO_REAL',180)
        self.assertEqual(old.result[0]['body'],new.result[0]['body']);self.assertEqual(calls[0],calls[1])
    def test_worker_sse_sanitiza_terminal_e_erro_sem_vazar(self):
        r=response();r['output'][0]['content'][0]['text']='DUMMY_PRIVADO';wire=evento(r)
        class Conn:
            status=200
            def __init__(self,w):self.reader=io.BytesIO(w)
            def request(self,*a,**kw):pass
            def getresponse(self):return self
            def getheader(self,k,default):return 'text/event-stream; charset=utf-8'
            def read1(self,n):return self.reader.read(n)
            def close(self):pass
        p=self.Pipe()
        with patch('retomada_v04_sse.http.http.client.HTTPSConnection',return_value=Conn(wire)):worker(p,'',{'stream':True},'DUMMY_PRIVADO',180)
        self.assertNotIn('DUMMY_PRIVADO',json.dumps(p.result));self.assertEqual(p.result[0]['body']['usage'],USAGE);self.assertEqual(p.result[0]['sse']['terminal'],'response.completed')
        p=self.Pipe();bad=b'data: {"type":"error","message":"DUMMY_PRIVADO","code":"server_error"}\n\n'
        with patch('retomada_v04_sse.http.http.client.HTTPSConnection',return_value=Conn(bad)):worker(p,'',{'stream':True},'DUMMY_PRIVADO',180)
        self.assertNotIn('DUMMY_PRIVADO',json.dumps(p.result));self.assertEqual(p.result[0]['erro'],'sse_error');self.assertEqual(p.result[0]['telemetria']['provider_code'],'server_error')

class GuardaR2(unittest.TestCase):
    setUp=LedgerTests.setUp
    tearDown=LedgerTests.tearDown
    def test_cinco_timeouts_nao_relaxa_paradas_anteriores(self):
        with LedgerTests.abrir(self)as l:
            ss=[s for s in l.permitidos if l.novos[s]['condicao']!='H'][:5]
            for s in ss:l.iniciar(s);i=l.reservar(s,'mock');l.desconhecido(i,{'erro':'timeout'})
            self.assertIn('Cinco',l.parada()[0]);l.conferir()
        with LedgerTests.abrir(self)as l:self.assertIn('Cinco',l.parada()[0]);l.conferir()

class AdendoFinal(unittest.TestCase):
    setUp=LedgerTests.setUp
    tearDown=LedgerTests.tearDown
    def test_limites_e_stream_do_adendo_nao_podem_mudar(self):
        for campo,valor in [('deadline_total_s',181),('max_agregado',301),('teto_nanoUSD',6000000000),('geracao_diff',{'stream':False})]:
            pro=deepcopy(self.pro);pro[campo]=valor
            with self.assertRaises(Bloqueio):CarteiraSSE(self.p,self.pl,self.a,pro,liberacao_coordenador=True)
