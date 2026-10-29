"""Integração nova em cópia temporária da carteira, sem chave/rede."""
import json,sqlite3,tempfile,unittest
from pathlib import Path
from copy import deepcopy
from piloto_v07_r2 import preparar_coorte,CarteiraV07R2,historico
from piloto_v07_r2.transporte import ResponsesSSE,LocalSSE
from retomada_v04_sse.transporte import ResponsesSSE as Antigo
from piloto_real.ledger import Bloqueio,RESERVA
from piloto_real import MODELO,CONFIG
from hibrido_v07_r2 import construir,LocalV07R2,SCHEMA
from interpretacao_no.contratos import hash_json
ROOT=Path(__file__).resolve().parents[2]
class HTTPMock:
    def __init__(self,texto='{}'):self.calls=[];self.texto=texto
    def post(self,path,payload,timeout):
        self.calls.append((path,deepcopy(payload),timeout))
        if path:return dict(object='response.input_tokens',input_tokens=100)
        return dict(id='mock',model=MODELO,status='completed',usage=dict(input_tokens=100,output_tokens=10,total_tokens=110,input_tokens_details=dict(cached_tokens=0,cache_write_tokens=0),output_tokens_details=dict(reasoning_tokens=0)),output=[dict(type='message',content=[dict(type='output_text',text=self.texto)])])
class Integracao(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        src=sqlite3.connect('file:'+str(ROOT/'outputs/etapa9_piloto_v07_20261028/ledger_final.sqlite')+'?mode=ro',uri=True)
        dst=sqlite3.connect(str(self.p/'ledger.sqlite'));src.backup(dst);dst.close();src.close()
        self.plano,self.a,self.casos=preparar_coorte(ROOT/'data/desenvolvimento')
        self.l=CarteiraV07R2(self.p,self.plano,self.a)
    def tearDown(self):self.l.close();self.tmp.cleanup()
    def slot(self,c):return next(s['execucao_id']for s in self.a['manifesto']['execucoes']if s['condicao']==c)
    def test_mesma_carteira_nova_coorte_e_historico(self):
        self.assertEqual(len(self.l.resultados()),90);self.assertEqual(self.l.resumo()['tentativas_reservadas'],790)
        s=self.slot('B');self.l.iniciar(s);i=self.l.reservar(s,'mock');self.assertEqual(i,791)
        self.l.desconhecido(i,{'erro':'timeout'})
        self.assertEqual(self.l.resumo()['comprometido_nanoUSD'],3281889545+RESERVA)
        self.l.conferir()
        with self.assertRaises(Bloqueio):self.l.iniciar(s)
        with self.assertRaises(Bloqueio):self.l.reservar(s,'segundo')
    def test_teto_USD_e_teto_1090_bloqueiam_antes_do_HTTP(self):
        s=self.slot('H');self.l.iniciar(s)
        for n in range(300):self.l.db.execute("INSERT INTO chamadas(slot,request_hash,estado,comprometido)VALUES(?,?,?,?)",('fake','mock','reservado',0))
        self.l.db.commit()
        with self.assertRaises(Bloqueio):self.l.reservar(s,'mock')
        self.l.db.execute('DELETE FROM chamadas WHERE id>790');self.l.db.execute("INSERT INTO chamadas(slot,request_hash,estado,comprometido)VALUES('fake','mock','reservado',1718110455)");self.l.db.commit()
        with self.assertRaises(Bloqueio):self.l.reservar(s,'mock')
    def test_payload_B_T_identico_ao_SSE_antigo(self):
        class L:
            def reservar(self,*a):return 1
            def __getattr__(self,k):return lambda *a:None
        for c in ('B','T'):
            req=dict(modelo=MODELO,configuracao=CONFIG,formato='json',timeout_s=180,mensagens=[dict(papel='sistema',conteudo='MOCK'),dict(papel='usuario',conteudo=json.dumps({'view':c}))])
            one,two=HTTPMock(),HTTPMock();Antigo(L(),'mock',one,timeout_s=180)(req);ResponsesSSE(L(),'mock',two,timeout_s=180)(req)
            self.assertEqual([x[:2]for x in one.calls],[x[:2]for x in two.calls]);self.assertTrue(two.calls[1][1]['stream'])
            self.assertTrue(0<two.calls[1][2]<=two.calls[0][2]<=180)
    def test_v07_pedido_tipado_sem_nota_antiga_e_sem_retries(self):
        s=self.slot('H');self.l.iniciar(s);http=HTTPMock();t=LocalSSE(self.l,s,http,timeout_s=180)
        c=self.casos[self.l.novos[s]['caso_id']];p=construir(c['estado'],c['evento'],execucao_id=s)
        from hibrido_v07_r2.contratos import montar_contexto
        n=p.alvos[0];ctx=montar_contexto(c['estado'],c['evento'],no_id=n,execucao_id=s,revisao=1,responsabilidades_operacionais=p.responsabilidades_operacionais,**p.plano[n])
        LocalV07R2(t,modelo=MODELO,configuracao=CONFIG,timeout_s=180).analisar(ctx)
        self.assertEqual(len(http.calls),2)
        from hibrido_v07_r2.formato import SISTEMA
        self.assertEqual(http.calls[1][1]['input'][0]['content'],SISTEMA)
        self.assertEqual(http.calls[0][1]['text'],http.calls[1][1]['text'])
        self.assertEqual(http.calls[1][1]['text']['format']['type'],'json_schema')
        self.assertIs(http.calls[1][1]['text']['format']['strict'],True)
        from hibrido_v07_r2.schema import gerar
        self.assertEqual(http.calls[1][1]['text']['format']['schema'],gerar(ctx))
        self.assertEqual(self.l.db.execute('SELECT count(*) FROM chamadas WHERE id>790').fetchone()[0],1)
        self.assertEqual(self.l.db.execute('SELECT estado FROM chamadas WHERE id=791').fetchone()[0],'conciliado')
    def test_pipeline_runner_H_valido_ate_normalizacao_e_falha_pre_analise(self):
        from unittest.mock import patch
        from piloto_v07_r2 import executar
        from hibrido_v07_r2.avaliacao import normalizar,registrar
        from piloto_real.runner import indisponivel
        a=deepcopy(self.a);a['manifesto']['execucoes']=a['manifesto']['execucoes'][:3];a['slots']=[s['execucao_id']for s in a['manifesto']['execucoes']]
        class MockTipado(HTTPMock):
            def post(self,path,payload,timeout):
                if not path:
                    d=json.loads(payload['input'][1]['content'])
                    if 'contexto'in d:
                        c=d['contexto'];q=dict(estado='indeterminado',valor=None,evidencias=[],lacunas=['MOCK sem interpretação factual'],motivo=None)
                        from hibrido_v07_r2.wire import WIRE
                        r=dict(schema_version=WIRE,avaliacao=dict(prazo=q,custo=deepcopy(q)),propostas=[],justificativa='MOCK de integração, sem semântica',lacunas=[],pendencias_operacionais=[dict(dimensao='ambos',motivo='Fato não interpretado neste MOCK',evidencias=[dict(fonte_id=c['fontes'][0]['id'],localizador=c['fontes'][0]['localizador'])])],encaminhamentos=[],resolucoes_regras=[dict(regra_id=x['regra_id'],propostas_indices=[]) for x in c['escopos_regras']])
                        self.texto=json.dumps(r)
                    else:self.texto='{}'
                return super().post(path,payload,timeout)
        self.l.close()
        db=sqlite3.connect(str(self.p/'ledger.sqlite'))
        for t in ('coorte_v07_r2','slots_v07_r2','parada_v07_r2'):db.execute('DROP TABLE '+t)
        db.commit();db.close()
        with patch('piloto_v07_r2.preparar_coorte',return_value=(self.plano,a,self.casos)):
            res=executar(ROOT/'data/desenvolvimento',self.p,self.p/'out',http=MockTipado(),coletar=True)
        self.l=CarteiraV07R2(self.p,self.plano,a)
        regs=[r for _,_,r in self.l.resultados()if r];h=next(r for r in regs if r['metadados']['condicao']=='H')
        self.assertTrue(any(t.get('analise',{}).get('execucao',{}).get('estado')=='ok'for t in h['resultado']['rastro_orquestracao']))
        n=normalizar(a['manifesto'],regs)
        self.assertFalse(n['anomalias'],n['anomalias']);self.assertEqual(len(n['linhas']),3)
        s=h['metadados'];ruim=registrar(s,indisponivel(s,'FALHA_ANTES_DA_ANALISE'))
        n=normalizar(a['manifesto'],[ruim if r['metadados']['condicao']=='H'else r for r in regs])
        self.assertEqual(len(n['linhas']),3);self.assertEqual(n['linhas'][1]['desfechos']['prazo']['classe'],'invalido')

    def test_versao_mista_bloqueada_sem_HTTP(self):
        s=self.slot('H');http=HTTPMock();t=LocalSSE(self.l,s,http,timeout_s=180)
        with self.assertRaises(ValueError):t(dict(versao_formato_local='4.0-formato-local'))
        self.assertFalse(http.calls)
if __name__=='__main__':unittest.main()
