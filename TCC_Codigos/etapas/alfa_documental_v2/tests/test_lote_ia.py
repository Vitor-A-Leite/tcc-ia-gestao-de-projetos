"""Executor completo com HTTP falso; nenhuma coleta paga nem credencial real."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from ..src import lote_ia as lote
from ..src import DATA
from ..src.apresentacao import expandir
from ..src.ia_real import TransporteReal, MODELO
from ..src.modelo import carregar
from ..src.simulacao import interpretador
from .test_revisao import resposta_prescrita


class LoteTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.pasta=Path(self.tmp.name)
        self.hist=self.pasta/'historico.sqlite';self.ledger=self.pasta/'v2.sqlite'
        for p,n in ((self.hist,4_567_653_865),(self.ledger,33_425_810)):
            with sqlite3.connect(p) as db:
                db.execute('CREATE TABLE chamadas(id TEXT PRIMARY KEY, rodada TEXT, estado TEXT, comprometido INTEGER, entrada INTEGER, saida INTEGER, segundos REAL, arquivo TEXT)')
                db.execute('INSERT INTO chamadas VALUES(?,?,?,?,?,?,?,?)',('antiga','antiga','conciliada',n,0,0,0,'historico.json'))
        for nome,valor in [('HISTORICO',self.hist),('LEDGER',self.ledger)]:
            m=patch.object(lote,nome,valor);m.start();self.addCleanup(m.stop)
        m=patch('socket.socket',side_effect=AssertionError('Rede proibida'));m.start();self.addCleanup(m.stop)
        self.calls=[]
        g,_=carregar()
        self.respostas={cid:interpretador(json.loads((DATA/'simulacoes/dev'/f'{cid}.json').read_text()),g).resposta for cid in lote.CENARIOS}
        self.eventos={cid:lote.ler_cenario(cid) for cid in lote.CENARIOS}

    def preparar(self,nome='lote'):
        dest=self.pasta/nome
        lote.preparar_lote(dest)
        return dest/'manifesto.json'

    def http(self,path,p):
        self.calls.append((path,deepcopy(p)))
        if path:return {'input_tokens':100}
        entrada=json.loads(p['input'][1]['content'])
        if 'pacote_hash' in entrada:
            # Uma resposta desfavorável válida não bloqueia o protocolo.
            saida=resposta_prescrita(entrada,'suporte_insuficiente')
        elif 'representacao_entrada' in entrada:
            c=expandir(entrada)['contexto']
            saida=self.respostas[c['evento_id']](c)
        else:
            cid=entrada['evento_id']
            saida=dict(sugestoes=[dict(no_id=n,justificativa='Resposta prescrita de teste') for n in self.eventos[cid]['entidades_mencionadas']],ambiguidades=[])
        return dict(status='completed',model=MODELO,id='http-falso',
            output=[dict(content=[dict(type='output_text',text=json.dumps(saida))])],
            usage={'input_tokens':100,'output_tokens':20})

    def executar(self,m,http=None):
        with patch.object(lote,'ler_chave',return_value='CHAVE_FICTICIA_TESTE'):
            return lote.executar_lote(m,autorizar=True,autorizacao='Autorização fictícia de teste, sem API real',http=http or self.http)

    def test_preparar_nao_le_credencial_nem_altera_carteira(self):
        antes=[p.read_bytes() for p in (self.hist,self.ledger)]
        with patch.object(lote,'ler_chave',side_effect=AssertionError('Não ler chave')):
            m=self.preparar();d=json.loads(m.read_text())
            self.assertEqual(d['estado'],'aguardando_autorizacao')
            self.assertFalse(d['protocolo']['autorizacao_coleta'])
            self.assertEqual(d['protocolo']['cenarios'],list(lote.CENARIOS))
            self.assertEqual(d['protocolo']['teto_total_nano'],20_000_000_000)
            self.assertEqual(d['financeiro']['comprometido_preparo_nano'],4_601_079_675)
            with self.assertRaises(ValueError):lote.executar_lote(m)
        self.assertFalse((m.parent/'execucao.json').exists())
        self.assertEqual(antes,[p.read_bytes() for p in (self.hist,self.ledger)])

    def test_manifesto_dados_e_historico_obsoletos_bloqueiam(self):
        m=self.preparar();original=json.loads(m.read_text())
        ruim=deepcopy(original);ruim['protocolo']['teto_total_nano']=99_000_000_000;m.write_text(json.dumps(ruim))
        with self.assertRaises(ValueError):self.executar(m)
        m.write_text(json.dumps(original))
        with patch.object(lote,'arquivos_congelados',return_value={'alterado':'hash'}):
            with self.assertRaises(ValueError):self.executar(m)
        with sqlite3.connect(self.ledger) as db:db.execute('UPDATE chamadas SET comprometido=10_000_000_000')
        with self.assertRaises(ValueError):self.executar(m)
        self.assertEqual(self.calls,[])

    def test_lote_completo_multiplas_entradas_e_revisao_separada(self):
        m=self.preparar();antes=self.hist.read_bytes();original=Path.read_text
        def ler(p,*args,**kwargs):
            if p==lote.REFERENCIA:
                self.assertTrue(all((m.parent/cid/'resultado.json').exists() and (m.parent/cid/'auditoria.json').exists() for cid in lote.CENARIOS))
            if 'simulacoes' in p.parts:raise AssertionError('Executor real tentou ler fixture')
            return original(p,*args,**kwargs)
        with patch.object(Path,'read_text',ler):r=self.executar(m)
        self.assertEqual(r['estado'],'concluido',r.get('erro'))
        self.assertEqual(r['modo'],'teste_http_injetado_nao_mede_ia')
        self.assertEqual(antes,self.hist.read_bytes())
        self.assertEqual(r['cenarios']['D04']['estado_previsao'],'parcial')
        self.assertEqual(r['cenarios']['D04']['coleta'],'concluida')
        self.assertTrue(all(x['equivalente_referencia_autoral'] for x in r['cenarios'].values()))
        for cid in ('D05','D06'):
            sel=json.loads((m.parent/cid/'selecao.json').read_text())
            self.assertEqual(set(sel['entradas']),set(self.eventos[cid]['entidades_mencionadas']))
            self.assertEqual(len(sel['entradas']),2)
        self.assertTrue(all(v['chamadas_api']<=65 for v in r['transportes'].values()))
        self.assertLess(r['comprometido_total_nano'],20_000_000_000)
        chamadas=len(self.calls)
        with self.assertRaises(FileExistsError):self.executar(m)
        self.assertEqual(len(self.calls),chamadas)

    def test_ambiguidade_interrompe_sem_corrigir_ou_repetir(self):
        m=self.preparar()
        def http(path,p):
            r=self.http(path,p)
            if not path and 'evento_id' in json.loads(p['input'][1]['content']):
                r['output'][0]['content'][0]['text']=json.dumps(dict(sugestoes=[],ambiguidades=['Dúvida prescrita']))
            return r
        r=self.executar(m,http)
        self.assertEqual(r['estado'],'interrompido');self.assertEqual(r['fase'],'coleta:D01')
        self.assertEqual(r['cenarios']['D02']['coleta'],'nao_executada')
        self.assertEqual(len(self.calls),4)  # preflight e sugestão, contagem + inferência
        self.assertTrue((m.parent/'D01/sugestao.json').exists())

    def test_falha_preflight_nao_inicia_coleta_preserva_reserva(self):
        m=self.preparar()
        def http(path,p):
            self.calls.append((path,p));raise TimeoutError('falha prescrita')
        r=self.executar(m,http)
        self.assertEqual(r['estado'],'interrompido');self.assertEqual(r['fase'],'preflight')
        self.assertEqual(len(self.calls),1)
        self.assertTrue(r['transportes']['preflight']['uso_desconhecido'])
        self.assertEqual(r['transportes']['preflight']['comprometido_usd'],.015)
        self.assertTrue(all(x['coleta']=='nao_executada' for x in r['cenarios'].values()))

    def test_parser_revisor_invalido_interrompe_preflight(self):
        m=self.preparar()
        def http(path,p):
            r=self.http(path,p)
            if not path:r['output'][0]['content'][0]['text']='{}'
            return r
        r=self.executar(m,http)
        self.assertEqual(r['estado'],'interrompido');self.assertEqual(len(self.calls),2)
        a=json.loads((m.parent/'preflight_auditoria.json').read_text())
        self.assertIsNone(a['registros'][0]['revisao_semantica']['parecer'])

    def test_falha_local_preserva_resultado_e_nao_avanca(self):
        m=self.preparar()
        def http(path,p):
            r=self.http(path,p)
            if not path:
                u=json.loads(p['input'][1]['content'])
                if 'representacao_entrada' in u and expandir(u)['contexto']['evento_id']=='D05':
                    r['output'][0]['content'][0]['text']='{}'
            return r
        r=self.executar(m,http)
        self.assertEqual(r['fase'],'coleta:D05');self.assertEqual(r['estado'],'interrompido')
        self.assertEqual(r['cenarios']['D06']['coleta'],'nao_executada')
        self.assertTrue((m.parent/'D05/resultado.json').exists())
        self.assertTrue((m.parent/'D04/resultado.json').exists())

    def test_falha_revisao_para_na_primeira_proposta(self):
        m=self.preparar();revisoes=[]
        def http(path,p):
            r=self.http(path,p)
            if not path:
                u=json.loads(p['input'][1]['content'])
                if 'pacote_hash' in u:
                    revisoes.append(u['referencia']['evento_id'])
                    if len(revisoes)>1:r['output'][0]['content'][0]['text']='{}'
            return r
        r=self.executar(m,http)
        self.assertEqual(r['fase'],'revisao:D01');self.assertEqual(r['estado'],'interrompido')
        self.assertEqual(len(revisoes),2)  # preflight e primeira proposta, sem segunda proposta D01
        self.assertTrue(all(x['coleta']=='concluida' for x in r['cenarios'].values()))
        self.assertEqual(r['cenarios']['D02']['revisao'],'nao_executada')
        a=json.loads((m.parent/'D01/auditoria.json').read_text())
        self.assertEqual(a['estado'],'interrompida');self.assertEqual(len(a['registros']),1)

    def test_selecao_nao_suprime_mencoes_nem_adiciona_sucessores(self):
        for cid in ('D05','D06'):
            c=self.eventos[cid];ids=c['entidades_mencionadas']
            for escolha in (ids[:1],ids+['M_RELEASE'],ids+ids):
                with self.assertRaises(ValueError):lote.conferir_selecao(dict(sugestoes=[{'no_id':x} for x in escolha],ambiguidades=[]),c)


class TetoTransporteTests(unittest.TestCase):
    def test_teto_vinte_preserva_historico_e_grupo_entre_rodadas(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasta=Path(tmp);ledger=pasta/'ledger.sqlite';calls=[]
            def http(path,p):
                calls.append(path)
                return {'input_tokens':100} if path else dict(status='completed',model=MODELO,output=[],usage={'input_tokens':100,'output_tokens':20})
            kw=dict(ledger=ledger,teto_total_nano=20_000_000_000,teto_rodada_nano=990_000_000,max_chamadas=65,grupo='lote',teto_grupo_nano=15_000_000,http=http)
            a=TransporteReal(pasta/'a','falso',19_970_000_000,rodada='lote:a',**kw)
            b=TransporteReal(pasta/'b','falso',19_970_000_000,rodada='lote:b',**kw)
            self.addCleanup(a.db.close);self.addCleanup(b.db.close)
            a.gerar([],{},'a')
            with self.assertRaises(Exception):b.gerar([],{},'b')  # saldo grupo não comporta nova reserva
            self.assertEqual(len(calls),2)
            a.db.execute('UPDATE chamadas SET comprometido=20_000_000');a.db.commit()
            b.teto_grupo=1_000_000_000
            with self.assertRaises(Exception):b.gerar([],{},'b')  # teto global de20 inclui histórico
            self.assertEqual(len(calls),2)
