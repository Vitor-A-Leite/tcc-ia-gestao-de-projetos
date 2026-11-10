"""Interface local offline; não expõe segredos, rede externa ou escrita oficial."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from threading import Thread
from urllib.parse import urlparse, parse_qs

from . import ROOT
from .modelo import carregar, projetar, normalizar, grafo_documental
from .pipeline import ler_cenario
from .sessoes import Sessoes
from .selecao import catalogo


def projeto(cenario_id):
    """Estado visual inicial, sem executar interpretação ou consultar gabaritos."""
    g, docs = carregar()
    c = ler_cenario(cenario_id)
    return dict(grafo=grafo_documental(g, docs, c), documento_origem=c['documento'],
                fim_base=dict(valor=g['fim_base']), custo_base=dict(valor=g['custo_base']),
                rastro_orquestracao=[], propagacao=[], nos_com_mudanca_quantitativa=[],
                estado_projetado_nos={}, baseline_nos={}, folgas_base_dias={})


def publico(s):
    r=s.get('resultado') or {}
    visual={k:r.get(k) for k in ('execucao','completude','fim_novo','delta_dias','custo_novo','delta_centavos',
        'estados_selecao','verificacao_documental','pendencias_execucao','fim_base','custo_base',
        'baseline_nos','estado_projetado_nos','folgas_base_dias','propagacao','nos_com_mudanca_quantitativa',
        'efeitos_financeiros','livro_parcelas','registro_operacional')}
    # A interface recebe o rastro necessário à inspeção, sem cache nem envelopes
    # completos do transporte. O grafo/documentos são carregados uma vez por caso.
    visual['rastro_orquestracao']=[dict(no_id=t['no_id'],processamento=t['processamento'],motivo=t.get('motivo'),
        analise={k:t['analise'].get(k) for k in ('justificativa','propostas','lacunas')} if t.get('analise') else None,
        fontes=t.get('contexto',{}).get('fontes',[])) for t in r.get('rastro_orquestracao',[])]
    return {**{k:s.get(k) for k in ('id','cenario_id','selecao','selecao_confirmada','regiao','estado','revisao','limites','consumo','pendentes','dependencias_pendentes','cancelamento_solicitado','em_voo','erro_interface','expansoes')},
            'resultado':visual,
            'solicitacoes_previstas':len(s['regiao']['nos'])+s['consumo']['solicitacoes_simuladas'] if s['estado']=='pronta' else len(s['pendentes'])+s['consumo']['solicitacoes_simuladas']}


class SugestaoManual:
    origem='simulado'
    def __init__(self,ids):self.ids=ids
    def __call__(self,pedido):
        return dict(sugestoes=[dict(no_id=n,justificativa='Menção explícita cadastrada no documento de mudança; sugestão preparada, não inferência de IA.') for n in self.ids],ambiguidades=[])


def handler(gerente):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def resposta(self,body,status=200,tipo='application/json; charset=utf-8'):
            data=json.dumps(body,ensure_ascii=False).encode() if tipo.startswith('application/json') else body
            self.send_response(status);self.send_header('Content-Type',tipo);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def do_GET(self):
            try:
                url=urlparse(self.path)
                if url.path=='/api/catalogo':
                    g,d=carregar();e=projetar(g,d)
                    casos=[]
                    for i in range(1,10):
                        c=ler_cenario(f'D{i:02}');ev=normalizar(c,e)
                        casos.append(dict(id=c['id'],relato=ev['relato'],mencoes=ev['entidades_mencionadas'],total_nos=len(grafo_documental(g,d,c)['nodes'])))
                    return self.resposta(dict(catalogo=catalogo(g),arestas=[x for x in g['edges'] if x['classe']=='temporal'],casos=casos,versao=e['versao']))
                if url.path=='/api/sessao':return self.resposta(publico(gerente.ler(parse_qs(url.query)['id'][0])))
                if url.path=='/api/projeto':return self.resposta(projeto(parse_qs(url.query)['cenario'][0]))
                paths={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/graph3d.js':'graph3d.js'}
                if url.path not in paths:return self.resposta({'erro':'Recurso não encontrado'},404)
                p=ROOT/'web'/paths[url.path];return self.resposta(p.read_bytes(),tipo=mimetypes.guess_type(p)[0] or 'text/plain')
            except (ValueError,KeyError,FileNotFoundError) as exc:self.resposta({'erro':str(exc)},400)
        def do_POST(self):
            try:
                # Navegador remoto não pode acionar mutações no servidor local.
                origin=self.headers.get('Origin')
                if origin and origin not in ('http://'+self.headers.get('Host',''),):raise ValueError('Origem externa recusada.')
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=65536:raise ValueError('Pedido inválido ou grande demais.')
                b=json.loads(self.rfile.read(size));path=urlparse(self.path).path
                if path=='/api/preparar':
                    s=gerente.preparar(b['cenario'],b['entradas'],b['limite'],limites={'max_solicitacoes':b.get('max_solicitacoes',32)},escopo=b.get('escopo','impacto_do_evento'),confirmar_divergencia=b.get('confirmar_divergencia',False))
                    return self.resposta(publico(s))
                if path=='/api/selecionar':return self.resposta(publico(gerente.selecionar(b['id'],b['entradas'],b['limite'],escopo=b.get('escopo','impacto_do_evento'),confirmar_divergencia=b.get('confirmar_divergencia',False))))
                if path=='/api/sugerir':
                    s=gerente.ler(b['id']);c=ler_cenario(s['cenario_id'])
                    return self.resposta(gerente.sugestao(b['id'],b['pedido_id'],SugestaoManual(c['entidades_mencionadas'])))
                if path=='/api/cancelar':return self.resposta(publico(gerente.cancelar(b['id'])))
                if path=='/api/executar':
                    def trabalho():
                        try:gerente.executar(b['id'],selecionados=b.get('selecionados'),max_nos=b.get('limite'),limites={'max_solicitacoes':b['max_solicitacoes']} if 'max_solicitacoes' in b else None,acao_id=b['acao_id'],revisao=b.get('revisao'))
                        except ValueError as exc:
                            try:
                                with gerente.lock(b['id']):
                                    s=gerente.ler(b['id']);s['erro_interface']=str(exc);gerente.salvar(s)
                            except ValueError:pass
                    Thread(target=trabalho,daemon=True).start()
                    return self.resposta({'aceito':True,'id':b['id']},202)
                return self.resposta({'erro':'Ação desconhecida'},404)
            except (ValueError,KeyError,FileNotFoundError,TypeError) as exc:self.resposta({'erro':str(exc)},400)
    return Handler


def servir(porta=8767):
    server=ThreadingHTTPServer(('127.0.0.1',porta),handler(Sessoes()))
    print(f'Alfa v2 · simulação offline: http://127.0.0.1:{porta}',flush=True)
    server.serve_forever()
