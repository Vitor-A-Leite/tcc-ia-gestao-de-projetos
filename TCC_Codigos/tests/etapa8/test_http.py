import json
import threading
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from observatorio.__main__ import servidor


class HTTPTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=servidor(0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def test_assets_e_cabecalhos(self):
        for path in ('/','/style.css','/app.js'):
            with urlopen(self.url+path) as r:
                self.assertEqual(r.status,200)
                self.assertEqual(r.headers['Cache-Control'],'no-store')
                self.assertIn("default-src 'self'",r.headers['Content-Security-Policy'])
                self.assertTrue(r.read())
    def test_api_e_fronteiras(self):
        with urlopen(self.url+'/api/catalogo') as r:
            self.assertEqual(len(json.load(r)['casos']),8)
        for mode,estado in [('normal','ok'),('parcial','parcial'),('erro','erro')]:
            with urlopen(self.url+'/api/replay?caso=k_09c2&modo='+mode) as r:
                d=json.load(r)
                self.assertEqual(d['resultado']['execucao']['estado'],estado)
        with urlopen(self.url+'/api/avaliacao') as r:
            self.assertIn('referencias_sinteticas',json.load(r)['arquivos'])
    def test_rotas_e_selecoes_rejeitadas(self):
        for path,status in [('/../../docs/desenvolvimento/STATUS.md',404),
            ('/api/replay?caso=k_09c2&modo=real',400),('/api/replay?caso=k_09c2',400),
            ('/api/replay?caso=k_09c2&modo=normal&modo=erro',400),
            ('/api/replay?caso=../referencias/gabaritos&modo=normal',400)]:
            with self.subTest(path=path),self.assertRaises(HTTPError) as e: urlopen(self.url+path)
            self.assertEqual(e.exception.code,status)
