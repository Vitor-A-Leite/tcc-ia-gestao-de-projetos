"""Demonstração local, sem dependências de rede/CDN, com execução Python offline."""
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import mimetypes
from . import ROOT
from .dados import gravar


def construir_demo(resultados):
    results={}
    for f in sorted(resultados.glob('D[0-9][0-9].json')):
        r=json.loads(f.read_text())
        # Apenas apresentação reduzida; brutos completos ficam no diretório da rodada.
        for t in r.get('rastro_orquestracao',[]):
            c=t.get('contexto',{})
            t['contexto']={k:c[k] for k in ('no_id','fontes','contexto_hash') if k in c}
        results[r['cenario_id']]=r
    if len(results)!=9: raise ValueError('Demo exige os nove casos de desenvolvimento completos')
    scenarios=[dict(id=id,titulo=json.loads((ROOT/'inputs/cenarios/dev'/(id+'.json')).read_text())['titulo']) for id in results]
    payload=json.dumps(dict(results=results,scenarios=scenarios),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    (ROOT/'web/data.js').write_text('const ALFA_DATA = '+payload+';\n')


def servir(porta=8766):
    from .pipeline import simular
    from .integridade import verificar_selo
    verificar_selo()
    web=ROOT/'web'
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            name=self.path.split('?')[0]
            allowed={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css','/data.js':'data.js'}
            if name=='/favicon.ico': self.send_response(204);self.end_headers();return
            if name not in allowed: self.send_error(404);return
            content=(web/allowed[name]).read_bytes()
            self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(allowed[name])[0] or 'text/plain');self.send_header('Content-Length',str(len(content)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(content)
        def do_POST(self):
            if self.path!='/api/simular': self.send_error(404);return
            # Nenhuma operação paga/aprovação/escrita de documento está exposta via HTTP.
            origin=self.headers.get('Origin')
            if origin and origin not in (f'http://127.0.0.1:{porta}',f'http://localhost:{porta}'): self.send_error(403);return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<1000: raise ValueError('Entrada inválida')
                data=json.loads(self.rfile.read(length))
                if set(data)!={'cenario'} or data['cenario'] not in {f'D{i:02}' for i in range(1,10)}: raise ValueError('Somente cenários de desenvolvimento cadastrados')
                r=simular(data['cenario']);directory=ROOT/'runs'/'interativo';directory.mkdir(parents=True,exist_ok=True)
                name=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'-'+data['cenario']+'.json'
                with (directory/name).open('x') as f: json.dump(r,f,ensure_ascii=False,indent=2)
                body=json.dumps(r,ensure_ascii=False).encode()
                self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            except (ValueError,KeyError) as exc: self.send_error(400,str(exc))
    server=ThreadingHTTPServer(('127.0.0.1',porta),Handler)
    print(f'Demo local: http://127.0.0.1:{porta} — Ctrl+C encerra. Zero API paga.',flush=True)
    server.serve_forever()
