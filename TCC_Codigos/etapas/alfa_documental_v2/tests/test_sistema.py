from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from .. import ROOT
from ..src import DATA
from ..src.sessoes import Sessoes
from ..src import selecao
from ..src.pipeline import simular, ler_cenario, executar
from ..src.modelo import carregar, projetar, normalizar
from ..src.simulacao import interpretador
from ..src.demo import SugestaoManual
from ..src.vendor.hibrido_v07_r3.adaptador import SimuladoV07R3


def resumo(r):
    return dict(quantidades={k:{x:r[k].get(x) for x in ('estado','valor','limites')} for k in ('fim_novo','delta_dias','custo_novo','delta_centavos')},
                recomendacoes=sorted([x['unidade'],x['valor_proposto']] for x in r['verificacao_documental']['recomendacoes']),
                afirmacoes=[[x['unidade'],x['estado']] for x in r['verificacao_documental']['afirmacoes']])


class Sistema(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.m=Sessoes(self.temp.name)
    def criar(self,limit='todos',cenario='D02',entradas=None,**kwargs):
        return self.m.preparar(cenario,entradas or ler_cenario(cenario)['entidades_mencionadas'],limit,**kwargs)
    def test_equivalencia_nove_casos(self):
        refs=json.loads((ROOT/'avaliacao/equivalencia_v1.json').read_text())
        for cid in refs:
            with self.subTest(cenario=cid):
                s=self.criar(cenario=cid);s=self.m.executar(s['id'])
                self.assertEqual(resumo(s['resultado']),refs[cid]);self.assertEqual(s['estado'],'concluida')
                self.assertLess(s['consumo']['solicitacoes_simuladas'],s['selecao']['maximo_disponivel'])
                self.assertEqual(s['consumo']['chamadas_api'],0)
    def test_modo_completo_incorporado_preserva_resultado(self):
        refs=json.loads((ROOT/'avaliacao/equivalencia_v1.json').read_text())
        self.assertEqual(resumo(simular('D06')),refs['D06'])
    def test_limite_livre(self):
        for n in (1,2,7,11,17,31,32,'todos','3'):
            self.assertEqual(self.criar(n)['selecao']['limite_nos_analise'],32 if n=='todos' else int(n))
    def test_limites_invalidos(self):
        for n in (None,0,-1,3.4,True,False,'','3.0',' 3 ','NaN',33):
            with self.subTest(n=n),self.assertRaises(ValueError):self.criar(n)
    def test_maximo_derivado_dos_dados(self):
        g,d=carregar();e=projetar(g,d);ev=normalizar(ler_cenario('D02'),e)
        g['nodes']=[n for n in g['nodes'] if n['id']!='C_COUPLING']
        self.assertEqual(selecao.validar(g,ev,['SUP_MOTOR'],'todos',e['versao'])['maximo_disponivel'],31)
    def test_entradas_invalidas(self):
        for ns in ([],['SUP_MOTOR','SUP_MOTOR'],['NOT_A_NODE'],['DOC_CAD@1']):
            with self.subTest(ns=ns),self.assertRaises(ValueError):self.m.preparar('D02',ns,'todos')
    def test_entradas_maiores_que_limite(self):
        with self.assertRaises(ValueError):self.criar(1,'D05')
    def test_versao_obsoleta(self):
        with self.assertRaisesRegex(ValueError,'Versão'):self.criar(versao='antiga')
    def test_divergencia_avisada(self):
        with self.assertRaisesRegex(ValueError,'diverge'):self.criar(cenario='D05',entradas=['SUP_MOTOR'])
    def test_teste_delimitado_nao_conclui_global(self):
        s=self.criar(cenario='D05',entradas=['SUP_MOTOR'],escopo='teste_delimitado',confirmar_divergencia=True)
        s=self.m.executar(s['id']);r=s['resultado'];self.assertIsNone(r['fim_novo']['valor'])
        self.assertNotIn('SR.FINISH',{x['trecho_id'] for x in r['verificacao_documental']['recomendacoes']})
    def test_todos_nao_forca_todos(self):
        s=self.m.executar(self.criar()['id']);self.assertEqual(len(s['visitados']),13);self.assertEqual(s['selecao']['maximo_disponivel'],32)
    def test_pausa_e_retomada_sem_repetir(self):
        s=self.m.executar(self.criar(1)['id']);self.assertEqual(s['visitados'],['SUP_MOTOR']);self.assertEqual(s['estado'],'pausada')
        self.assertIsNone(s['resultado']['fim_novo']['valor'])
        s=self.m.executar(s['id'],selecionados=s['pendentes'],max_nos='todos',acao_id='continuar')
        self.assertEqual(s['consumo']['solicitacoes_simuladas'],13);self.assertEqual(s['resultado']['delta_dias']['valor'],5)
        self.assertEqual(self.m.executar(s['id'],acao_id='continuar')['consumo'],s['consumo'])
    def test_continuacao_parcial_dependencia_explicita(self):
        s=self.m.executar(self.criar(1)['id'])
        s=self.m.executar(s['id'],selecionados=['T_ASSEMBLY'],max_nos=10)
        self.assertEqual(s['consumo']['solicitacoes_simuladas'],1);self.assertIn('C_MOTOR',s['dependencias_pendentes']['T_ASSEMBLY'])
        s=self.m.executar(s['id'],selecionados=['C_MOTOR'],max_nos=10)
        self.assertEqual(s['consumo']['solicitacoes_simuladas'],2);self.assertIsNone(s['resultado']['fim_novo']['valor'])
    def test_reabrir_nao_executa(self):
        s=self.m.executar(self.criar(1)['id']);m2=Sessoes(self.temp.name)
        self.assertEqual(m2.ler(s['id'])['consumo']['solicitacoes_simuladas'],1)
        with self.assertRaisesRegex(ValueError,'explicitamente'):m2.executar(s['id'])
    def test_cancelar_preserva_e_bloqueia(self):
        s=self.m.executar(self.criar(1)['id']);s=self.m.cancelar(s['id'])
        self.assertEqual(s['estado'],'cancelada');self.assertEqual(len(s['visitados']),1)
        with self.assertRaisesRegex(ValueError,'cancelada'):self.m.executar(s['id'],selecionados=s['pendentes'])
    def test_cancelar_em_voo(self):
        g,d=carregar();f=json.loads((DATA/'simulacoes/dev/D02.json').read_text());inner=interpretador(f,g)
        started=threading.Event();release=threading.Event()
        class Lento:
            origem='simulado';configuracao={}
            def analisar(self,c):started.set();release.wait(3);return inner.analisar(c)
        s=self.criar();errors=[]
        def work():
            try:self.m.executar(s['id'],adaptador_teste=Lento())
            except Exception as exc:errors.append(exc)
        t=threading.Thread(target=work);t.start();self.assertTrue(started.wait(2))
        self.m.cancelar(s['id']);release.set();t.join(4)
        self.assertFalse(t.is_alive());self.assertFalse(errors)
        s=self.m.ler(s['id']);self.assertEqual(s['estado'],'cancelada');self.assertEqual(s['consumo']['solicitacoes_simuladas'],1)
    def test_duplo_clique_em_voo(self):
        s=self.criar()
        with self.m.lock(s['id']):
            with self.assertRaisesRegex(ValueError,'andamento'):self.m.executar(s['id'])
        self.assertEqual(self.m.ler(s['id'])['consumo']['solicitacoes_simuladas'],0)
    def test_sem_evidencia_fabricada(self):
        s=self.m.executar(self.criar(cenario='D06')['id']);r=s['resultado']
        self.assertEqual(r['estados_selecao']['T_ASSEMBLY'],'fora_do_escopo_justificado')
        self.assertFalse(any(x['no_id']=='T_ASSEMBLY' and x.get('analise') for x in r['rastro_orquestracao']))
        no=next(x for x in r['registros_correntes'] if x['no_id']=='T_ASSEMBLY')
        self.assertEqual(no['estado'],'calculado_sem_interpretacao')
    def test_documento_corrigido_e_folga(self):
        s=self.m.executar(self.criar(cenario='D07')['id']);self.assertEqual(s['resultado']['verificacao_documental']['recomendacoes'],[])
        s=self.m.executar(self.criar(cenario='D01')['id']);self.assertEqual(s['resultado']['delta_dias']['valor'],0)
        self.assertEqual({x['trecho_id'] for x in s['resultado']['verificacao_documental']['recomendacoes']},{'SR.MOTOR'})
    def test_orcamento_chamadas_acumulado(self):
        s=self.criar(limites={'max_solicitacoes':2});s=self.m.executar(s['id'])
        self.assertEqual(s['consumo']['solicitacoes_simuladas'],2);self.assertEqual(s['estado'],'pausada')
        s=self.m.executar(s['id'],selecionados=s['pendentes'],limites={'max_solicitacoes':3})
        self.assertEqual(s['consumo']['solicitacoes_simuladas'],3)
    def test_orcamento_tempo_zero(self):
        s=self.criar(limites={'max_segundos':0});s=self.m.executar(s['id']);self.assertEqual(s['consumo']['solicitacoes_simuladas'],0)
    def test_sugestao_custo_e_cache(self):
        s=self.criar(limites={'max_solicitacoes':13});t=SugestaoManual(['SUP_MOTOR'])
        a=self.m.sugestao(s['id'],'pedido',t);b=self.m.sugestao(s['id'],'pedido',t)
        self.assertEqual(a,b);self.assertFalse(a['confirmada'])
        self.m.selecionar(s['id'],['SUP_MOTOR'],'todos')
        s=self.m.executar(s['id']);self.assertEqual(s['consumo']['solicitacoes_simuladas'],13)
        self.assertEqual(len(s['visitados']),12);self.assertEqual(s['estado'],'pausada')
    def test_sugestao_invalida_nao_repete(self):
        class Ruim:
            origem='simulado'
            def __init__(self):self.n=0
            def __call__(self,p):self.n+=1;return {}
        s=self.criar();t=Ruim()
        for i in range(2):
            with self.assertRaises(ValueError):self.m.sugestao(s['id'],'mesmo',t)
        self.assertEqual(t.n,1);self.assertEqual(self.m.ler(s['id'])['consumo']['solicitacoes_simuladas'],1)
    def test_sugestao_exige_confirmacao_posterior(self):
        s=self.criar();self.m.sugestao(s['id'],'pedido',SugestaoManual(['SUP_MOTOR']))
        with self.assertRaisesRegex(ValueError,'Confirme'):self.m.executar(s['id'])
        s=self.m.ler(s['id']);self.assertEqual(s['consumo']['solicitacoes_simuladas'],1);self.assertEqual(s['visitados'],[])
        s=self.m.selecionar(s['id'],['SUP_MOTOR'],'todos')
        self.assertTrue(s['selecao_confirmada']);self.assertEqual(len(s['historico_selecoes']),2)
        self.assertTrue(s['historico_selecoes'][-1]['sugestoes_consideradas'])
        s=self.m.executar(s['id']);self.assertEqual(s['consumo']['solicitacoes_simuladas'],14)
    def test_sugestao_tempo_zero(self):
        s=self.criar(limites={'max_segundos':0})
        with self.assertRaisesRegex(ValueError,'tempo'):self.m.sugestao(s['id'],'p',SugestaoManual([]))
    def test_modelo_diferente_invalida(self):
        g,d=carregar();f=json.loads((DATA/'simulacoes/dev/D02.json').read_text());a=interpretador(f,g)
        a.configuracao={'modelo':'a'};s=self.criar(1);s=self.m.executar(s['id'],adaptador_teste=a)
        a.configuracao={'modelo':'b'}
        with self.assertRaisesRegex(ValueError,'configuração'):self.m.executar(s['id'],selecionados=s['pendentes'],max_nos='todos',adaptador_teste=a)
    def test_fontes_diferentes_invalidam(self):
        s=self.m.executar(self.criar(1)['id']);g,d=carregar();d=deepcopy(d);d[0]['trechos'][0]['texto']+=' mudança'
        with patch(''.join([Sessoes.__module__,'.carregar']),return_value=(g,d)):
            with self.assertRaisesRegex(ValueError,'mudaram'):self.m.executar(s['id'],selecionados=s['pendentes'])
    def test_encaminhamento_ancestral_reanalisa_contexto(self):
        g,d=carregar();f=json.loads((DATA/'simulacoes/dev/D06.json').read_text())
        f['mudancas'].append(dict(no='M_PROTO_READY',campo='release',valor=30))
        base=interpretador(f,g)
        def responder(c):
            w=base.resposta(c)
            if c['no_id']=='TEST_LOAD':
                route=next(x for x in c['responsabilidades_operacionais'] if x['no_id']=='M_PROTO_READY' and x['operacao']=='substituir_restricao')
                ref=next(x for x in c['fontes'] if x['documento_id']==c['evento']['origem']['documento_id'])
                w['encaminhamentos']=[dict(**route,motivo='Teste de ampliação controlada ao predecessor.',evidencias=[dict(fonte_id=ref['id'],localizador=ref['localizador'])])]
            return w
        a=SimuladoV07R3(responder);s=self.criar(cenario='D06');s=self.m.executar(s['id'],adaptador_teste=a)
        self.assertTrue(s['expansoes']);self.assertIn('M_PROTO_READY',s['visitados'])
        self.assertGreater(s['consumo']['solicitacoes_simuladas'],len(s['visitados']))
        self.assertEqual(s['resultado']['fim_novo']['valor'],49)
        load=[x for x in s['tentativas'] if x['no_id']=='TEST_LOAD'];self.assertEqual(len(load),2)
        self.assertNotEqual(load[0]['contexto_hash'],load[1]['contexto_hash'])
    def test_saida_invalida_nao_vira_zero(self):
        s=self.criar();s=self.m.executar(s['id'],adaptador_teste=SimuladoV07R3({}))
        self.assertIsNone(s['resultado']['fim_novo']['valor']);self.assertTrue(s['pendentes'])
    def test_expansao_na_continuacao_exige_nova_escolha(self):
        g,d=carregar();f=json.loads((DATA/'simulacoes/dev/D02.json').read_text());base=interpretador(f,g)
        def responder(c):
            w=base.resposta(c)
            if c['no_id']=='T_ASSEMBLY':
                route=next(x for x in c['responsabilidades_operacionais'] if x['no_id']=='T_PROC' and x['operacao']=='substituir_restricao')
                ref=next(x for x in c['fontes'] if x['documento_id']==c['evento']['origem']['documento_id'])
                w['encaminhamentos']=[dict(**route,motivo='Verificar predecessor adicional.',evidencias=[dict(fonte_id=ref['id'],localizador=ref['localizador'])])]
            return w
        a=SimuladoV07R3(responder);s=self.criar(1);s=self.m.executar(s['id'],adaptador_teste=a)
        s=self.m.executar(s['id'],selecionados=['C_MOTOR','T_ASSEMBLY'],max_nos=10,adaptador_teste=a)
        self.assertIn('T_PROC',s['pendentes']);self.assertNotIn('T_PROC',s['visitados'])
        self.assertEqual(s['consumo']['solicitacoes_simuladas'],3);self.assertIsNone(s['resultado']['fim_novo']['valor'])
    def test_checkpoint_portavel_sem_repetir_contexto(self):
        s=self.m.executar(self.criar(1)['id'])
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT,Path(tmp)/'alfa_documental_v2',ignore=shutil.ignore_patterns('outputs','__pycache__'))
            code="from alfa_documental_v2.src.sessoes import Sessoes;import sys;m=Sessoes(sys.argv[1]);s=m.ler(sys.argv[2]);s=m.executar(s['id'],selecionados=s['pendentes'],max_nos='todos');assert s['consumo']['solicitacoes_simuladas']==13;assert s['resultado']['delta_dias']['valor']==5"
            p=subprocess.run([sys.executable,'-B','-c',code,self.temp.name,s['id']],cwd=tmp,env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
    def test_transporte_real_bloqueado(self):
        with self.assertRaisesRegex(ValueError,'bloqueado'):executar(ler_cenario('D02'),adapter=object())
        s=self.criar()
        with self.assertRaisesRegex(ValueError,'offline'):self.m.executar(s['id'],adaptador_teste=object())
        self.assertEqual(self.m.ler(s['id'])['estado'],'pronta')
    def test_sessao_id_sem_path_traversal(self):
        with self.assertRaises(ValueError):self.m.ler('../qualquer')
    def test_casos_finais_ausentes(self):
        self.assertFalse((DATA/'cenarios/final').exists());self.assertFalse((ROOT/'avaliacao/referencias/final').exists())
    def test_autonomia_fora_repositorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(ROOT,Path(tmp)/'alfa_documental_v2',ignore=shutil.ignore_patterns('outputs','__pycache__'))
            cmd="from alfa_documental_v2.src.pipeline import simular;import sys; r=simular('D02');assert r['delta_dias']['valor']==5;assert not any(x in sys.modules for x in ('hibrido_v07_r3','motor_deterministico','orquestracao'))"
            p=subprocess.run([sys.executable,'-B','-c',cmd],cwd=tmp,env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)


def run():
    with patch('socket.socket',side_effect=AssertionError('Rede proibida nos testes offline')):
        return unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Sistema))
