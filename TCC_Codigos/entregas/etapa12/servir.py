"""Servidor de leitura local do pacote, sem API de modelo ou acesso fora da entrega."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import unquote,urlsplit
import argparse
HERE=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(HERE),**kwargs)
    def send_head(self):
        path=unquote(urlsplit(self.path).path)
        if path=='/':self.path='/COMECE_AQUI.html';path=self.path
        target=(HERE/path.lstrip('/')).resolve()
        if HERE not in target.parents or not target.is_file() or target.suffix not in {'.html','.css','.js','.json','.md','.docx','.zip','.txt'}:
            self.send_error(404);return None
        return super().send_head()
    def end_headers(self):
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--porta',type=int,default=8782);a=p.parse_args()
    with ThreadingHTTPServer(('127.0.0.1',a.porta),Handler)as server:
        print(f'Abra http://127.0.0.1:{server.server_port} — Ctrl+C para encerrar. Sem chamadas ao modelo.',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
