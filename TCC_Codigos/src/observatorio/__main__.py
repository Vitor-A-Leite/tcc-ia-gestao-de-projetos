"""Servidor local sem rede externa ou dependências adicionais."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from . import Observatorio, ROOT


def servidor(porta=8768, observatorio=None):
    obs = observatorio or Observatorio()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def responder(self, corpo, status=200, mime='application/json; charset=utf-8'):
            data = corpo if isinstance(corpo,bytes) else json.dumps(corpo,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status)
            for k,v in {'Content-Type':mime,'Content-Length':str(len(data)), 'Cache-Control':'no-store',
                'X-Content-Type-Options':'nosniff', 'Content-Security-Policy':"default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"}.items(): self.send_header(k,v)
            self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            url=urlsplit(self.path)
            try:
                if url.path=='/api/catalogo': return self.responder(obs.catalogo())
                if url.path=='/api/avaliacao': return self.responder(obs.avaliacao())
                if url.path=='/api/replay':
                    q=parse_qs(url.query,keep_blank_values=True)
                    if set(q) != {'caso','modo'} or any(len(v)!=1 for v in q.values()): raise ValueError('Seleção inválida')
                    return self.responder(obs.executar(q['caso'][0],q['modo'][0]))
                arquivos={'/':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css')}
                if url.path not in arquivos: return self.responder({'erro':'Não encontrado'},404)
                nome,mime=arquivos[url.path]
                return self.responder((ROOT/'visualizacao/observatorio_quantitativo'/nome).read_bytes(),mime=mime+'; charset=utf-8')
            except ValueError as exc: self.responder({'erro':str(exc)},400)
            except Exception: self.responder({'erro':'Falha ao carregar/calcular. Nenhum resultado substituído por zero.'},500)
    return ThreadingHTTPServer(('127.0.0.1',porta),Handler)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--porta',type=int,default=8768)
    args=p.parse_args();s=servidor(args.porta)
    print(f'Observatório: http://127.0.0.1:{s.server_port} · parar: Ctrl+C',flush=True)
    try: s.serve_forever()
    except KeyboardInterrupt: pass
    finally: s.server_close()

if __name__=='__main__': main()
