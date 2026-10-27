from pathlib import Path
import tempfile,shutil,json,unittest
from unittest.mock import patch
from retomada_v04 import *
from retomada_v04.http import worker,seguro
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'outputs/etapa9_coorte_v04_20261026'
class Retomada(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name);shutil.copy(O/'snapshot_pos_parada/ledger.sqlite',self.p/'ledger.sqlite')
        self.pl,self.a,_=preparar_coorte(ROOT/'data/desenvolvimento');self.pro=json.loads((O/'opcao_retomada_73.json').read_text())
    def tearDown(self):self.tmp.cleanup()
    def abrir(self):return CarteiraRetomada(self.p,self.pl,self.a,self.pro)
    def test_lista_exata_ancora_concorrencia_e_persistencia(self):
        with self.abrir()as l:
            self.assertEqual(len(l.permitidos),73);self.assertEqual(l.resumo()['comprometido_nanoUSD'],380502675)
            self.assertIsNone(l.parada());self.assertTrue(l.db.execute('SELECT * FROM parada_v04').fetchall())
            s=l.permitidos[0];l.iniciar(s)
            with self.assertRaises(Bloqueio):l.iniciar(s)
            with self.assertRaises(Bloqueio):self.abrir()
            with self.assertRaises(Bloqueio):l.iniciar(next(s for s,e,_ in l.resultados()if e=='terminado'))
            l.conferir();l.parar('mock_stop');self.assertEqual(l.parada()[0],'mock_stop')
        with self.abrir()as l:
            self.assertEqual(l.parada()[0],'mock_stop');l.conferir()
            with self.assertRaises(Bloqueio):l.iniciar(l.permitidos[1])
    def test_saldo_caps_e_protecao_17_61(self):
        with self.abrir()as l:
            s=next(s for s in l.permitidos if l.novos[s]['condicao']=='B');l.iniciar(s);i=l.reservar(s,'mock')
            self.assertEqual(i,62);l.iniciar_contagem(i);l.contar(i,100);l.enviar(i);l.concluir(i,100,{},{});
            self.assertEqual(l.resumo()['comprometido_nanoUSD'],380502675+2000100);l.conferir()
            with self.assertRaises(Bloqueio):l.reservar(s,'mock')
            # Alteração de original na cópia deve impedir qualquer retomada.
            with l.db:l.db.execute("UPDATE chamadas SET request_hash='adulterado' WHERE id=61")
            with self.assertRaises(Bloqueio):l.iniciar(l.permitidos[1])
    def test_guarda_append_only_e_lista_invalida(self):
        with self.abrir()as l:
            antigos=l.db.execute('SELECT * FROM parada_v04').fetchall()
            ss=[s for s in l.permitidos if l.novos[s]['condicao']!='H'][:5]
            for s in ss:l.iniciar(s);i=l.reservar(s,'mock');l.desconhecido(i,{'erro':'timeout'})
            self.assertIn('Cinco',l.parada()[0]);self.assertEqual(antigos,l.db.execute('SELECT * FROM parada_v04').fetchall())
            l.conferir()
        self.pro['slots_pendentes']=self.pro['slots_pendentes'][:-1]
        with self.assertRaises(Bloqueio):self.abrir()
    def test_worker_sucesso_identico_ao_historico(self):
        from piloto_real.transporte import _http_worker
        class Pipe:
            def __init__(self):self.result=[]
            def send(self,x):self.result.append(x)
            def close(self):pass
        calls=[]
        class Conn:
            status=200
            def request(self,*a,**kw):calls.append((a,kw))
            def getresponse(self):return self
            def read(self,n):return b'{"object":"response.input_tokens","input_tokens":123}'
            def close(self):pass
        payload={'model':'gpt-6-luna','input':[]};old=Pipe();new=Pipe()
        with patch('retomada_v04.http.http.client.HTTPSConnection',return_value=Conn()):
            _http_worker(old,'/input_tokens',payload,'credencial_dummy',180)
            worker(new,'/input_tokens',payload,'credencial_dummy',180)
        self.assertEqual(old.result,new.result);self.assertEqual(calls[0],calls[1])
    def test_telemetria_allowlist_sem_mensagem(self):
        class Pipe:
            def __init__(self):self.result=[]
            def send(self,x):self.result.append(x)
            def close(self):pass
        class Conn:
            def request(self,*a,**kw):raise ConnectionResetError(54,'segredo_mock_nao_deve_aparecer')
            def close(self):pass
        p=Pipe()
        with patch('retomada_v04.http.http.client.HTTPSConnection',return_value=Conn()):worker(p,'',{},'credencial_dummy',180)
        self.assertEqual(p.result,[dict(erro='http_indisponivel',telemetria=dict(fase='envio',classe_excecao='ConnectionResetError',errno=54))])
        self.assertNotIn('segredo_mock',json.dumps(p.result));self.assertNotIn('credencial_dummy',json.dumps(p.result))
        class NomeNaoPermitido(Exception):pass
        self.assertEqual(seguro(NomeNaoPermitido('nunca_expor'),'JSON')['classe_excecao'],'nao_catalogada')
if __name__=='__main__':unittest.main()
