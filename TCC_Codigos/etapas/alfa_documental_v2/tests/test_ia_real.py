import unittest,tempfile,json
from pathlib import Path
from ..src.ia_real import TransporteReal,MODELO

class TransporteTests(unittest.TestCase):
    def test_usage_and_key_not_saved(self):
        with tempfile.TemporaryDirectory() as tmp:
            def http(path,p):
                if path:return {'input_tokens':100}
                return {'status':'completed','model':MODELO,'usage':{'input_tokens':100,'output_tokens':20,'input_tokens_details':{'cached_tokens':10}},'output':[]}
            t=TransporteReal(Path(tmp)/'run','TEST_SECRET',0,http=http)
            t.gerar([],{'type':'json_object'},'test')
            s=t.snapshot();self.assertEqual(s['chamadas_api'],1);self.assertFalse(s['uso_desconhecido']);self.assertEqual(s['tokens_entrada'],100)
            self.assertAlmostEqual(s['custo_api_usd'],.0000191)
            self.assertNotIn('TEST_SECRET',next((Path(tmp)/'run').glob('*.json')).read_text())
    def test_failure_preserves_reserve_blocks_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            def http(path,p):raise TimeoutError()
            t=TransporteReal(Path(tmp)/'run','TEST',0,http=http)
            with self.assertRaises(TimeoutError):t.gerar([],{},'x')
            self.assertEqual(t.snapshot()['comprometido_usd'],.015)
            with self.assertRaises(Exception):t.gerar([],{},'x')
            self.assertEqual(t.snapshot()['chamadas_api'],1)
    def test_historical_budget_not_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=TransporteReal(Path(tmp)/'run','TEST',4_999_000_000,http=lambda *a:self.fail('network called'))
            with self.assertRaises(Exception):t.gerar([],{},'x')
            self.assertEqual(t.snapshot()['chamadas_api'],0)
    def test_overlimit_input_no_inference(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            def http(path,p):calls.append(path);return {'input_tokens':64001}
            t=TransporteReal(Path(tmp)/'run','TEST',0,http=http)
            with self.assertRaises(Exception):t.gerar([],{},'x')
            self.assertEqual(calls,['/input_tokens'])
    def test_session_reserves_before_next_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=TransporteReal(Path(tmp)/'run','TEST',0,http=lambda *a:self.fail('network called'))
            t.db.execute('INSERT INTO chamadas VALUES(?,?,?,?,?,?,?,?)',('prior','run','conciliada',390_000_000,0,0,0,'prior.json'));t.db.commit()
            with self.assertRaises(Exception):t.gerar([],{},'x')
            self.assertEqual(t.snapshot()['chamadas_api'],1)
