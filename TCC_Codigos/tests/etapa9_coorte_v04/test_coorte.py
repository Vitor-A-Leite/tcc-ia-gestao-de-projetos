import json,shutil,tempfile,unittest
from pathlib import Path
from coorte_v04 import *
from piloto_real.ledger import PROVISAO_CONTAGEM
ROOT=Path(__file__).resolve().parents[2]
W=ROOT/'outputs/etapa9_coorte_v04_20261026/snapshot_antes'
class Coorte(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        shutil.copy(W/'ledger.sqlite',self.p/'ledger.sqlite')
        self.pl,self.a,self.c=preparar_coorte(ROOT/'data/desenvolvimento')
    def tearDown(self):self.tmp.cleanup()
    def test_plano_contagem_ordem_e_historico(self):
        self.assertEqual(len(self.a['slots']),90);self.assertEqual(self.a['estimativa_passagem_completa'],284);self.assertEqual(self.a['estimativa_agregada'],299)
        self.assertEqual([s['condicao']for s in self.a['manifesto']['execucoes']],[s['condicao']for s in self.pl['slots']])
        self.assertTrue(set(self.a['slots']).isdisjoint(s['execucao_id']for s in self.pl['slots']))
        with CarteiraV04(self.p,self.pl,self.a)as l:
            self.assertEqual(l.resumo()['comprometido_nanoUSD'],172820515)
            self.assertEqual(historico(l.db),l.hist)
            with self.assertRaises(Bloqueio):CarteiraV04(self.p,self.pl,self.a)
        with CarteiraV04(self.p,self.pl,self.a)as l:self.assertEqual(len(l.resultados()),90)
    def test_replay_caps_soma_global_e_preservacao(self):
        with CarteiraV04(self.p,self.pl,self.a)as l:
            s=next(s for s in self.a['manifesto']['execucoes']if s['condicao']=='B')['execucao_id'];l.iniciar(s)
            with self.assertRaises(Bloqueio):l.iniciar(s)
            i=l.reservar(s,'mock');l.iniciar_contagem(i);l.contar(i,100);l.enviar(i);l.concluir(i,123,{},{});
            self.assertEqual(l.resumo()['comprometido_nanoUSD'],172820515+PROVISAO_CONTAGEM+123)
            with self.assertRaises(Bloqueio):l.reservar(s,'mock')
            self.assertEqual(historico(l.db),l.hist)
            l.salvar(s,{'mock':True})
            with self.assertRaises(Bloqueio):l.salvar(s,{})
    def test_timeout_guard_and_http_fault(self):
        with CarteiraV04(self.p,self.pl,self.a)as l:
            ss=[s['execucao_id']for s in self.a['manifesto']['execucoes']if s['condicao']!='H'][:6]
            for s in ss[:5]:
                l.iniciar(s);i=l.reservar(s,'mock');l.desconhecido(i,{'erro':'timeout'})
            self.assertIn('Cinco',l.parada()[0])
            with self.assertRaises(Bloqueio):l.iniciar(ss[5])
        # Independent copy, fresh coorte: HTTP authentication/protocol fault stops immediately.
        shutil.copy(W/'ledger.sqlite',self.p/'ledger.sqlite')
        with CarteiraV04(self.p,self.pl,self.a)as l:
            s=self.a['slots'][0];l.iniciar(s);i=l.reservar(s,'mock');l.desconhecido(i,{'erro':'http','falha_transporte':{'status_http':401}})
            self.assertTrue(l.parada())
    def test_cap_300_mesmo_com_saldo(self):
        with CarteiraV04(self.p,self.pl,self.a)as l:
            s=self.a['slots'][0];l.iniciar(s)
            n=l.db.execute('SELECT count(*) FROM chamadas').fetchone()[0]
            with l.db:
                l.db.executemany("INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES('mock','m','reservado',0)",[()for _ in range(300-n)])
            self.assertEqual(l.db.execute('SELECT count(*) FROM chamadas').fetchone()[0],300)
            with self.assertRaises(Bloqueio):l.reservar(s,'m')
    def test_global_caps_and_manifest_tamper(self):
        with CarteiraV04(self.p,self.pl,self.a)as l:
            s=self.a['slots'][0];l.iniciar(s)
            with l.db:l.db.execute("INSERT INTO chamadas(slot,request_hash,estado,comprometido) VALUES('mock','m','reservado',?)",(5*NANO_USD,))
            with self.assertRaises(Bloqueio):l.reservar(s,'m')
        bad=deepcopy(self.a);bad['deadline_chamada_s']=181
        with self.assertRaises(Bloqueio):CarteiraV04(self.p,self.pl,bad)
if __name__=='__main__':unittest.main()
