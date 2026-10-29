"""Exercita HTTP somente em loopback, com processo encerrado no próprio teste."""
from pathlib import Path
import importlib.util,json,threading,http.client
r=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('servidor_etapa12',r/'servir.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
server=m.ThreadingHTTPServer(('127.0.0.1',0),m.Handler);t=threading.Thread(target=server.serve_forever,daemon=True);t.start();port=server.server_port
cases=[('GET','/',200),('HEAD','/',200),('GET','/demonstracao/index.html',200),('GET','/demonstracao/app.js',200),('GET','/demonstracao/dados.js',200),('GET','/demonstracao/style.css',200),('GET','/servir.py',404),('HEAD','/servir.py',404),('GET','/%2e%2e/README.md',404),('HEAD','/%2e%2e/README.md',404),('POST','/demonstracao/index.html',501)]
try:
    for method,path,status in cases:
        c=http.client.HTTPConnection('127.0.0.1',port,timeout=5);c.request(method,path);res=c.getresponse();body=res.read();assert res.status==status,(method,path,res.status);assert method!='HEAD'or not body;c.close()
    result={'ok':True,'requisicoes':len(cases),'destino':'127.0.0.1','servidor_encerrado_ao_final':True};(r/'qa/servidor.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
finally:server.shutdown();server.server_close();t.join()
