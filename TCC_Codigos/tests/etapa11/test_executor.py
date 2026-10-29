"""Testes da fronteira de execução em cópias descartáveis, sem chave/rede."""
from pathlib import Path
from copy import deepcopy
import contextlib,io,json,shutil,sqlite3,sys,tempfile,unittest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'TCC_Codigos/experimentos/etapa11'))
import executor as ex
from hibrido_v07_r3.avaliacao import normalizar
from hibrido_v07_r3.wire import WIRE
from interpretacao_no.adaptadores import FalhaTransporte


class HTTPMock:
    def __init__(self,falhar=False):self.calls=[];self.falhar=falhar
    def post(self,path,payload,timeout):
        self.calls.append((path,deepcopy(payload)))
        if self.falhar:raise FalhaTransporte('http','MOCK falha',metadados={'status_http':500})
        if path:return dict(object='response.input_tokens',input_tokens=100)
        d=json.loads(payload['input'][1]['content'])
        if 'contexto' in d:
            c=d['contexto'];f=c['fontes'][0]
            resposta=dict(schema_version=WIRE,propostas=[],justificativa='MOCK de integração; nenhum fato interpretado',lacunas=[],
                pendencias_operacionais=[dict(dimensao='ambos',motivo='MOCK não interpreta fato',evidencias=[dict(fonte_id=f['id'],localizador=f['localizador'])])],encaminhamentos=[],
                resolucoes_regras=[dict(regra_id=x['regra_id'],propostas_indices=[]) for x in c['escopos_regras']])
        else:resposta={}
        return dict(id='MOCK_NAO_E_PREVISAO',model=ex.MODELO,status='completed',
            usage=dict(input_tokens=100,output_tokens=10,total_tokens=110,input_tokens_details=dict(cached_tokens=0,cache_write_tokens=0),output_tokens_details=dict(reasoning_tokens=0)),
            output=[dict(type='message',content=[dict(type='output_text',text=json.dumps(resposta))])])


class ExecutorFinal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.a,cls.casos=ex.preparar()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='tcc-etapa11-teste-');self.p=Path(self.tmp.name)
        shutil.copyfile(ex.OUT/'ledger_antes.sqlite',self.p/'ledger.sqlite')
        self.l=ex.CarteiraFinal(self.p,self.a)
    def tearDown(self):self.l.close();self.tmp.cleanup()
    def slot(self,cond):return next(s['execucao_id'] for s in self.a['manifesto']['execucoes'] if s['condicao']==cond)
    def iniciar_h(self):
        b=self.slot('B');self.l.iniciar(b);self.l.salvar(b,{'MOCK':True});h=self.slot('H');self.l.iniciar(h);return h
    def test_carteira_mesma_historico_immutavel_e_nao_replay(self):
        self.assertEqual(self.l.resumo()['tentativas_reservadas'],1114)
        b=self.slot('B');self.l.iniciar(b);i=self.l.reservar(b,'MOCK');self.assertEqual(i,1115)
        self.l.desconhecido(i,{'erro':'timeout'})
        self.assertEqual(self.l.resumo()['comprometido_nanoUSD'],ex.BASE_USD+ex.RESERVA)
        with self.assertRaises(ex.Bloqueio):self.l.iniciar(b)
        with self.assertRaises(ex.Bloqueio):self.l.reservar(b,'MOCK2')
        with self.assertRaises(ex.Bloqueio):self.l.desconhecido(1,{'erro':'MOCK'})
        self.l.conferir_historico()
    def test_ordem_e_limite_h(self):
        with self.assertRaises(ex.Bloqueio):self.l.iniciar(self.slot('H'))
        h=self.iniciar_h()
        for n in range(8):self.l.reservar(h,'MOCK'+str(n))
        with self.assertRaises(ex.Bloqueio):self.l.reservar(h,'NONA')
    def test_limite_USD_e_numero_total(self):
        h=self.iniciar_h()
        with self.l.db:self.l.db.execute("insert into chamadas(slot,request_hash,estado,comprometido) values('MOCK','MOCK','reservado',?)",(5000000000-ex.BASE_USD,))
        with self.assertRaises(ex.Bloqueio):self.l.reservar(h,'nao enviar')
        with self.l.db:
            self.l.db.execute('delete from chamadas where id>1114')
            self.l.db.executemany("insert into chamadas(slot,request_hash,estado,comprometido) values('MOCK',?,'reservado',0)",[(str(i),) for i in range(30)])
        with self.assertRaises(ex.Bloqueio):self.l.reservar(h,'trigesima primeira')
    def test_falha_protocolo_para_sem_proxima_tentativa(self):
        b=self.slot('B');self.l.iniciar(b);i=self.l.reservar(b,'MOCK')
        self.l.desconhecido(i,{'erro':'http'})
        self.assertTrue(self.l.parada())
        with self.assertRaises(ex.Bloqueio):self.l.reservar(b,'MOCK')
    def test_usage_libera_so_parte_conhecida(self):
        b=self.slot('B');self.l.iniciar(b);i=self.l.reservar(b,'MOCK')
        self.l.iniciar_contagem(i);self.l.contar(i,100);self.l.enviar(i)
        self.l.concluir(i,15000,{'MOCK':True},{'MOCK':True})
        self.assertEqual(self.l.resumo()['comprometido_nanoUSD'],ex.BASE_USD+2015000)
        with self.assertRaises(ex.Bloqueio):self.l.enviar(i)
        with self.assertRaises(ex.Bloqueio):self.l.concluir(i,15000,{}, {})
    def test_mock_nunca_usa_carteira_canonica(self):
        with self.assertRaises(ex.Bloqueio):ex.executar(self.a,self.casos,http=HTTPMock(),out=self.p/'out')
    def test_pipeline_nove_slots_sem_respostas_factuais(self):
        self.l.close();http=HTTPMock()
        with contextlib.redirect_stdout(io.StringIO()):r=ex.executar(self.a,self.casos,pasta=self.p,out=self.p/'out',http=http)
        self.assertEqual(r['estados'],dict(pendente=0,iniciado=0,terminado=9));self.assertIsNone(r['parada'])
        self.assertLessEqual(r['orcamento']['tentativas_reservadas']-1114,30)
        regs=[json.loads(p.read_text()) for p in (self.p/'out').glob(ex.ID+'-*.json')]
        n=normalizar(self.a['manifesto'],regs)
        self.assertEqual(len(n['linhas']),9);self.assertEqual(n['anomalias'],[])
        for i in range(0,len(http.calls),2):
            self.assertEqual(http.calls[i][0],'/input_tokens');self.assertEqual(http.calls[i+1][0],'')
            count,payload=http.calls[i][1],http.calls[i+1][1]
            self.assertEqual(count['input'],payload['input']);self.assertEqual(count['text'],payload['text'])
            self.assertTrue(payload['stream']);self.assertEqual(payload['max_output_tokens'],25000)
            self.assertEqual(payload['tools'],[]);self.assertFalse(payload['store'])
        # Retomada não envia nenhum request e não sobrescreve resultados.
        before=len(http.calls)
        with contextlib.redirect_stdout(io.StringIO()):ex.executar(self.a,self.casos,pasta=self.p,out=self.p/'out',http=http)
        self.assertEqual(len(http.calls),before)
    def test_pipeline_erro_HTTP_preserva_oito_pendentes(self):
        self.l.close();http=HTTPMock(falhar=True)
        with contextlib.redirect_stdout(io.StringIO()):r=ex.executar(self.a,self.casos,pasta=self.p,out=self.p/'out',http=http)
        self.assertEqual(r['estados']['terminado'],1);self.assertEqual(r['estados']['pendente'],8)
        self.assertEqual(len(http.calls),1);self.assertTrue(r['parada'])
        self.assertEqual(r['orcamento']['comprometido_nanoUSD'],ex.BASE_USD+ex.RESERVA)


if __name__=='__main__':unittest.main()
