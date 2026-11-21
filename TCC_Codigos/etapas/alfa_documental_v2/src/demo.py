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


ROTULOS_CONDICAO = {
    'ia': 'Documentos em prosa · afirmações extraídas pela IA (rodada real v2, 21/11/2026)',
    'referencia': 'Documentos em prosa · afirmações de referência (antes da extração por IA)',
    'cadastro': 'Status Report estruturado · afirmações cadastradas manualmente',
}
RODADA_IA = ROOT/'outputs/extracao_ia_v2_20261121'


def extracoes_ia(documentos, pasta=RODADA_IA):
    """Leituras gravadas da rodada real; não chama a IA. Documento sem leitura válida volta com o erro."""
    validas, falhas = [], {}
    for d in documentos:
        caso = pasta/'casos'/f"{d['id']}_{d['versao']}.json"
        if not caso.exists():
            falhas[(d['id'], d['versao'])] = [dict(codigo='sem_extracao', mensagem='Documento não lido na rodada registrada')]
            continue
        reg = json.loads(caso.read_text())
        x = reg.get('extracao') or {}
        if reg.get('estado') == 'concluido' and x.get('extracao'):
            validas.append(x['extracao'])
        else:
            falhas[(d['id'], d['versao'])] = [dict(codigo=e['codigo'], mensagem=e['mensagem']) for e in x.get('erros', [])] or [dict(codigo='interrompida', mensagem='Extração sem resposta registrada')]
    manifesto = json.loads((pasta/'manifesto.json').read_text())
    return validas, falhas, dict(rodada=manifesto['id'], modelo=manifesto['modelo'], versao_contrato=manifesto['versao'])


def conteudo(s, condicao='referencia'):
    """Revisão do conteúdo sobre o resultado da sessão; nada é escrito nos documentos."""
    from . import conteudo as C
    if condicao not in ROTULOS_CONDICAO: raise ValueError('Condição desconhecida')
    r = s.get('resultado') or {}
    if not r.get('execucao'): raise ValueError('Execute a análise antes de revisar o conteúdo.')
    cen = ler_cenario(s['cenario_id']); _, base = carregar()
    if condicao == 'cadastro':
        ext = C.afirmacoes_cadastro(cen)
        v = cen['registro_vigente']
        textos = [dict(id=v['id'], versao=v['versao'], nome=v['nome'], artefato='status_report',
                       trechos=[dict(id=t['id'], localizador=t['localizador'], texto=t['texto']) for t in v['trechos']])]
    elif condicao == 'ia':
        todos = C.documentos_do_cenario(cen)
        ext, falhas, origem_ia = extracoes_ia(todos)
        lidos = {(e['documento_id'], e['versao']) for e in ext}
        textos = [d for d in todos if (d['id'], d['versao']) in lidos]
    else:
        ext = C.extracoes_referencia(cen)
        textos = C.documentos_do_cenario(cen)
    rev = C.revisar_documentos(r, cen, ext, condicao=condicao, documentos=base)
    fontes = {t['id']: dict(documento_id=d['id'], versao=d['versao'], texto=t['texto']) for d in base for t in d['trechos']}
    fontes.update({t['id']: dict(documento_id=cen['documento']['id'], versao=cen['documento']['versao'], texto=t['texto']) for t in cen['documento']['trechos']})
    nomes = {n['id']: n['name'] for n in carregar()[0]['nodes']}
    docs = []
    for d, rd in zip(textos, rev['documentos']):
        docs.append(dict(documento_id=d['id'], versao=d['versao'], nome=d.get('nome'), artefato=d.get('artefato'),
            trechos=[dict(id=t['id'], localizador=t['localizador'], texto=t['texto']) for t in d['trechos']],
            nao_mapeados=rd['nao_mapeados'], resumo=rd['resumo'],
            afirmacoes=[dict(id=x['afirmacao']['id'], trecho_id=x['afirmacao']['trecho_id'], citacao=x['afirmacao']['citacao'],
                             predicado=x['afirmacao']['predicado'], entidades=x['afirmacao']['entidades'],
                             nomes=[nomes.get(e, e) for e in x['afirmacao']['entidades']],
                             estado=x['estado'], motivo=x['motivo'], sugestao=x['sugestao'],
                             por_que=x['explicacao']['texto'], caminhos=x['explicacao']['caminhos'],
                             absorcoes=x['explicacao']['absorcoes'], efeitos_custo=x['explicacao']['efeitos_custo'],
                             evidencias=[dict(**e, **fontes.get(e['fonte_id'], {})) for e in x['explicacao']['evidencias']])
                        for x in rd['afirmacoes']]))
    extra = {}
    if condicao == 'ia':
        for d in todos:
            if (d['id'], d['versao']) in falhas:
                docs.append(dict(documento_id=d['id'], versao=d['versao'], nome=d.get('nome'), artefato=d.get('artefato'),
                                 trechos=[dict(id=t['id'], localizador=t['localizador'], texto=t['texto']) for t in d['trechos']],
                                 nao_mapeados=[], resumo={}, afirmacoes=[], erro_extracao=falhas[(d['id'], d['versao'])]))
        extra['origem_ia'] = origem_ia
    total = {}
    for d in docs:
        for k, v in d['resumo'].items(): total[k] = total.get(k, 0)+v
    return dict(condicao=condicao, rotulo=ROTULOS_CONDICAO[condicao], cenario_id=s['cenario_id'], revisao_sessao=s.get('revisao'),
                execucao_global=rev['execucao_global'], documentos=docs, resumo=total, **extra,
                atualizacao_executada=False, natureza=rev['natureza'], suporte_semantico=rev['suporte_semantico'])


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
                if url.path=='/api/conteudo':
                    q=parse_qs(url.query);return self.resposta(conteudo(gerente.ler(q['id'][0]),q.get('condicao',['referencia'])[0]))
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
