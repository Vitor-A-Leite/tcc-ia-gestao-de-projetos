import unittest,tempfile,sqlite3,json
from pathlib import Path
from retomada_v05 import CarteiraRetomada,preparar_coorte,historico
from piloto_real.ledger import Bloqueio,RESERVA
ROOT=Path(__file__).resolve().parents[2]
class Retomada(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        a=sqlite3.connect('file:'+str(ROOT/'outputs/etapa9_piloto_v05_20261027/ledger_apos.sqlite')+'?mode=ro',uri=True);b=sqlite3.connect(str(self.p/'ledger.sqlite'));a.backup(b);a.close();b.close()
        self.plano,self.adendo,_=preparar_coorte(ROOT/'data/desenvolvimento');self.l=CarteiraRetomada(self.p,self.plano,self.adendo)
    def tearDown(self):self.l.close();self.tmp.cleanup()
    def test_89_pendentes_primeiro_erro_e_parada_preservados(self):
        self.assertEqual(len(self.l.permitidos),89);self.assertIsNone(self.l.parada())
        self.assertEqual(self.l.db.execute('SELECT motivo FROM parada_v05').fetchone(),('Falha transporte/protocolo: http_indisponivel',))
        primeiro=next(s for s,e,r in self.l.resultados()if e=='terminado')
        with self.assertRaises(Bloqueio):self.l.iniciar(primeiro)
        with self.assertRaises(Bloqueio):self.l.reservar(primeiro,'mock')
        with self.assertRaises(Bloqueio):self.l.salvar(primeiro,{})
        s=self.l.permitidos[0];self.l.iniciar(s);self.assertEqual(self.l.reservar(s,'mock'),274)
        self.assertEqual(self.l.resumo()['comprometido_nanoUSD'],1223050975+RESERVA);self.l.conferir()
    def test_parada_nova_nao_remove_original_e_reabertura_sem_replay(self):
        s=self.l.permitidos[0];self.l.iniciar(s);self.l.parar('MOCK guarda')
        self.l.close();self.l=CarteiraRetomada(self.p,self.plano,self.adendo)
        self.assertEqual(self.l.parada(),('MOCK guarda',));self.assertEqual(self.l.estado(s),'iniciado')
        with self.assertRaises(Bloqueio):self.l.iniciar(s)
    def test_tentativa273_tamper_bloqueia(self):
        self.l.db.execute("UPDATE chamadas SET comprometido=0 WHERE id=273");self.l.db.commit()
        with self.assertRaises(Bloqueio):self.l.conferir()
if __name__=='__main__':unittest.main()
