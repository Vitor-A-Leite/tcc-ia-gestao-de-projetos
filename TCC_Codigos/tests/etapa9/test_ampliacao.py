import builtins
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from piloto_engenharia import carregar, executar_prescrito, preparar_pacote, contraprovas
from piloto_engenharia.prontidao import diagnosticar, estimar
from orquestracao import avaliar, projecao
from orquestracao.simulacao import InterpretadorPrescrito, politica_prescrita
from motor_deterministico import preparar
from interpretacao_no.contratos import hash_json

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'data/desenvolvimento'
NOVO = DATA/'ampliacao_v1'


def ler(p): return json.loads(p.read_text())


class Ampliacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos = {x[0]:x[1:] for x in carregar(DATA, ampliacao=True)}

    def caso(self,cid='k_98f3'): return deepcopy(self.casos[cid])
    def rodar(self,cid): return executar_prescrito(*self.caso(cid))

    def test_referencias_manuais_sete_avisos(self):
        refs=ler(NOVO/'referencias/gabaritos.json')['casos']
        self.assertEqual(len(refs),7)
        self.assertEqual({x['caso_id'] for x in refs},set(self.casos))
        for ref in refs:
            with self.subTest(caso=ref['caso_id']):
                pacote=self.rodar(ref['caso_id']);r=pacote['H']
                for desfecho in ('delta_dias','delta_centavos'):
                    q, g = r[desfecho], ref[desfecho]
                    for k in ('estado','valor','direcao'): self.assertEqual(q[k],g[k])
                    if g['limites'] is not None: self.assertEqual(q['limites'],g['limites'])
                self.assertEqual(r['consumo']['chamadas'],0)
                self.assertEqual(pacote['B']['estado'],'sem_execucao')
                self.assertEqual(pacote['T']['estado'],'sem_execucao')
                self.assertEqual(ref['revisao_independente'],'pendente')

    def test_baseline_com_incidencia_preexistente(self):
        _,_,e,_,_=self.caso();datas,custo=preparar(e)
        self.assertEqual(custo,165000)
        self.assertEqual((datas['n_21dc']['inicio'].inferior,datas['n_21dc']['fim'].inferior),(8,11))
        self.assertEqual(datas[e['marco_final_id']]['fim'].inferior,12)
        self.assertEqual(e['regras_custo'][0]['decomposicao_base']['incidencia_centavos']['valor'],15000)

    def test_restricao_coexiste_com_FS(self):
        p=self.rodar('k_6d82');r=p['H']
        registros={x['no_id']:x for x in r['registros_correntes']}
        self.assertEqual(registros['n_21dc']['quantitativo']['inicio']['valor'],10)
        self.assertEqual(registros['n_21dc']['quantitativo']['fim']['valor'],13)
        self.assertEqual(r['delta_dias']['valor'],2)

    def test_dupla_convergencia_nao_soma_atrasos(self):
        r=self.rodar('k_0ca7')['H']
        registros={x['no_id']:x for x in r['registros_correntes']}
        for no,inicio,fim in [('n_05ed',7,10),('n_f8a3',10,12),('n_21dc',10,13),('n_683f',13,14)]:
            self.assertEqual(registros[no]['quantitativo']['inicio']['valor'],inicio)
            self.assertEqual(registros[no]['quantitativo']['fim']['valor'],fim)
        self.assertEqual(r['delta_centavos']['valor'],15000)

    def test_credito_exige_aditivo(self):
        a=self.rodar('k_98f3')['H'];b=self.rodar('k_42a9')['H']
        self.assertEqual(a['delta_dias']['valor'],b['delta_dias']['valor'])
        self.assertEqual(a['delta_centavos']['valor'],0)
        self.assertEqual(b['delta_centavos']['valor'],-15000)
        for r in (a,b):
            apoio=next(p for p in r['livro_parcelas'] if p['parcela_id']=='p_a84d')
            self.assertEqual(apoio['incidencia_base']['valor'],15000)
            self.assertEqual(apoio['incidencia_nova']['valor'],0)

    def test_cobranca_compartilhada_uma_vez_com_centavos(self):
        r=self.rodar('k_b5e1')['H'];livro=r['livro_parcelas']
        self.assertEqual(len(livro),len({p['parcela_id'] for p in livro}))
        self.assertEqual(r['custo_novo']['valor'],177345)
        self.assertEqual(sum(p['novo']['valor'] for p in livro),177345)

    def test_lacuna_nao_e_erro_nem_zero(self):
        r=self.rodar('k_d307')['H']
        self.assertEqual(r['execucao']['estado'],'parcial');self.assertEqual(r['execucao']['erros'],[])
        self.assertIsNone(r['delta_dias']['valor']);self.assertIsNone(r['delta_centavos']['valor'])
        self.assertEqual(r['delta_dias']['limites'],dict(inferior=0,superior=None))
        self.assertEqual(r['delta_centavos']['limites'],dict(inferior=2500,superior=None))
        self.assertEqual(r['delta_centavos']['direcao'],'aumento')

    def test_contextual_nao_propaga(self):
        b,fs,e,ev,f=self.caso('k_a064')
        self.assertNotIn(('n_914b','n_05ed'),projecao(e))
        r=executar_prescrito(b,fs,e,ev,f)['H']
        self.assertEqual(r['consumo']['analises'],0)
        self.assertEqual((r['delta_dias']['valor'],r['delta_centavos']['valor']),(0,0))

    def test_views_sem_outros_avisos_ou_referencias(self):
        for cid in self.casos:
            b,fs,e,ev,f=self.caso(cid);v,_,audit=preparar_pacote(b,fs,e,ev)
            self.assertTrue(audit['relacoes_completas'])
            for c in 'BHT':
                self.assertEqual([x['id'] for x in v[c]['comum']['fontes'] if x['documento_id']==ev['documento_evento_vigente']],ev['evidencia_ids'])
                texto=json.dumps(v[c])
                for proibido in ('familia_id','derivacao_manual','propostas_por_no','gabaritos','caso_id'):self.assertNotIn(proibido,texto)
                outros={x['id'] for x in fs if x['documento_id'] not in set(b['documentos_comuns']+b['documentos_relacionais']+[ev['documento_evento_vigente']])}
                for outro in outros:self.assertNotIn(outro,texto)
            self.assertNotIn('relacional',v['B'])
            self.assertIn('responsavel',json.dumps(v['H']['relacional']))

    def test_predicao_sem_IO_de_referencias(self):
        # A interface em memória não deve abrir qualquer arquivo, inclusive refs.
        caso=self.caso('k_b5e1');antes=deepcopy(caso)
        with patch.object(builtins,'open',side_effect=AssertionError('I/O na predição')),patch.object(Path,'read_text',side_effect=AssertionError('I/O na predição')):
            p=executar_prescrito(*caso)
        self.assertEqual(caso,antes)
        self.assertEqual(p['H']['delta_centavos']['valor'],12345)

    def test_independente_do_ID_opaco(self):
        _,_,e,_,f=self.caso('k_0ca7')
        mapa={n['id']:'n_novo'+str(j) for j,n in enumerate(e['entidades'])}
        def trocar(x):
            if isinstance(x,str):return mapa.get(x,x)
            if isinstance(x,list):return [trocar(v) for v in x]
            if isinstance(x,dict):return {mapa.get(k,k):trocar(v) for k,v in x.items()}
            return x
        e,f=trocar(e),trocar(f)
        for ps in f['propostas_por_no'].values():
            for p in ps:
                for o in p['origens_causais']:o['efeito_id']=hash_json([f['evento']['evento_id'],p['alvo_id']])
        r=avaliar(e,f['evento'],InterpretadorPrescrito(f),politica_prescrita(f))
        self.assertEqual((r['delta_dias']['valor'],r['delta_centavos']['valor']),(2,15000))

    def test_tipo_pertence_v1_e_tipo_desconhecido(self):
        b,fs,e,ev,_=self.caso('k_a064')
        n=dict(id='n_area',tipo='area',nome='Área sintética',atributos={},fonte_refs=[{'fonte_id':'f_a781','localizador':'L01'}])
        e['entidades'].append(n);b['entidades'].append({**n,'fonte_refs':['f_a781']})
        e['relacoes'].append(dict(id='l_area',origem_id='n_914b',destino_id='n_area',tipo='pertence',fonte_refs=n['fonte_refs']))
        v,_,_=preparar_pacote(b,fs,e,ev)
        self.assertIn('pertence',v['T']['relacoes_texto'])
        self.assertNotIn(('n_914b','n_area'),projecao(e))
        e['relacoes'][-1]['tipo']='inventada'
        with self.assertRaises(ValueError): preparar_pacote(b,fs,e,ev)

    def test_contraprovas_preservam_N_e_origem(self):
        b,fs,e,ev,f=self.caso();v,_,_=preparar_pacote(b,fs,e,ev)
        rs=contraprovas(e,f,v);self.assertEqual(len(rs),12)
        self.assertEqual(sum(r['condicao']=='H' for r in rs),8)
        self.assertEqual(sum(r['condicao']=='B' for r in rs),2)
        self.assertEqual(sum(r['condicao']=='T' for r in rs),2)
        for x in rs:
            if not x['limitacao_conhecida']:
                self.assertNotEqual(x['resultado']['execucao']['estado'],'ok',x['id'])
                self.assertIsNone(x['resultado'].get('delta_dias',{}).get('valor'))
        for x in rs:
            if x['condicao'] in ('B','T'):
                self.assertEqual(x['resultado']['consumo']['chamadas'],1)
                self.assertEqual(x['resultado']['execucao']['origem'],'transporte_mock')
                if x['id'].endswith('timeout'):self.assertIsNone(x['resultado']['consumo']['tokens_entrada'])

    def test_hash_e_citacao_nao_provam_suporte(self):
        b,fs,e,ev,f=self.caso();v,_,_=preparar_pacote(b,fs,e,ev)
        rs={r['id']:r for r in contraprovas(e,f,v)}
        self.assertEqual(rs['valor_sem_suporte']['resultado']['execucao']['estado'],'parcial')
        # Limitação conhecida: resolver externo mentiroso continua autorizando.
        r=rs['resolver_permissivo']['resultado']
        self.assertEqual(r['execucao']['estado'],'ok')
        self.assertEqual(r['delta_dias']['valor'],6)
        self.assertEqual(r['delta_centavos']['valor'],45000)
        self.assertTrue(rs['resolver_permissivo']['limitacao_conhecida'])

    def test_iris_preservado_integracao(self):
        casos=list(carregar(DATA));self.assertEqual(len(casos),8)
        for cid,*args in casos:
            with self.subTest(caso=cid):
                r=executar_prescrito(*args)['H']
                self.assertEqual(r['consumo']['chamadas'],0)
                self.assertEqual(r['execucao']['origem'],'simulado')


class Prontidao(unittest.TestCase):
    def plano(self):return ler(NOVO/'proposta_lote_real.json')
    def test_pacote_atual_nao_autoriza_real(self):
        r=diagnosticar(self.plano());self.assertFalse(r['pronto_para_execucao'])
        self.assertIn('politica_H_sem_oraculo',r['pendencias'])
        self.assertIsNone(r['estimativa']['custo_api_teto_centavos'])
    def test_limites_de_planejamento(self):
        e=estimar(self.plano())
        self.assertEqual((e['runs'],e['chamadas_logicas_max'],e['tentativas_transporte_max']),(90,300,300))
        self.assertEqual((e['tokens_entrada_max'],e['tokens_saida_max']),(4800000,600000))
    def test_cotacao_hipotetica_e_teto(self):
        p=self.plano();p['precos_BRL_por_milhao']={'entrada':'1.25','saida':'2.50'}
        self.assertEqual(estimar(p)['custo_api_teto_centavos'],750) # R$7,50 hipotéticos, não cotação real
        p['orcamento_api_centavos']=749
        self.assertIn('estimativa_excede_orcamento',diagnosticar(p)['pendencias'])
    def test_retry_somente_limite_v1_e_inteiros(self):
        p=self.plano();p['max_retries_transporte']=1
        self.assertEqual(estimar(p)['tentativas_transporte_max'],600)
        for k,v in [('casos',True),('repeticoes',0),('max_retries_transporte',2),('max_analises_H',-1)]:
            p=self.plano();p[k]=v
            with self.assertRaises(ValueError):estimar(p)




class Lote(unittest.TestCase):
    def test_erro_normal_preserva_slots_e_continua(self):
        import tempfile
        from piloto_engenharia.lote import executar_lote
        chamados=[]
        def executor(*args):
            cid=args[-1]['execucao_id'];chamados.append(cid)
            if cid=='offline9-k_6d82':raise RuntimeError('Falha inesperada injetada')
            return executar_prescrito(*args)
        with tempfile.TemporaryDirectory() as tmp:
            saida=Path(tmp)/'lote';r=executar_lote(DATA,saida,executor=executor)
            self.assertEqual(r['normais']['N_H'],15)
            self.assertEqual(len(r['normais']['registros']),15)
            self.assertEqual(len(chamados),15)
            slot=next(x for x in r['normais']['registros'] if x['caso_id']=='k_6d82')
            self.assertEqual(slot['execucao']['estado'],'erro')
            self.assertIsNone(slot['delta_dias']);self.assertIsNone(slot['delta_centavos'])
            self.assertEqual(next(x for x in r['normais']['registros'] if x['caso_id']=='k_a064')['execucao']['estado'],'ok')
            p=ler(saida/'k_a064.json')['proveniencia_slot']
            self.assertEqual(set(p['hashes_arquivos']),{'base','fontes','estado','fixture'})
            import hashlib
            for v in p['hashes_arquivos'].values():self.assertEqual(v['sha256'],hashlib.sha256(Path(v['path']).read_bytes()).hexdigest())
            self.assertEqual(len(ler(saida/'plano_slots.json')['slots']),15)
            self.assertEqual((r['normais']['N_B_executados'],r['normais']['N_T_executados']),(0,0))
            self.assertEqual(r['contraprovas']['N'],12)

    def test_fixture_ausente_e_JSON_malformado_preservam_N(self):
        import tempfile,shutil
        from piloto_engenharia.lote import executar_lote
        with tempfile.TemporaryDirectory() as tmp:
            raiz=Path(tmp)/'dados';raiz.mkdir()
            # Só os quatro pacotes de desenvolvimento necessários no diretório temporário.
            for d in ('ampliacao_v1','projeto_minimo_v1','projeto_minimo_grafo_v1','orquestracao_simulada_v1'):
                shutil.copytree(DATA/d,raiz/d)
            (raiz/'ampliacao_v1/fixtures_prescritas/k_6d82.json').unlink()
            (raiz/'ampliacao_v1/fixtures_prescritas/k_98f3.json').write_text('{inválido')
            saida=Path(tmp)/'lote';r=executar_lote(raiz,saida)
            self.assertEqual(r['normais']['N_H'],15)
            self.assertEqual(r['normais']['estados_H']['erro'],2)
            self.assertEqual(r['contraprovas']['N'],12)
            self.assertEqual(sum(v['estados'].get('erro',0) for v in r['contraprovas']['por_condicao'].values()),12)
            ausente=ler(saida/'k_6d82.json')['proveniencia_slot']['hashes_arquivos']['fixture']
            self.assertIsNone(ausente['sha256']);self.assertIn('erro',ausente)
            malformado=ler(saida/'k_98f3.json')['proveniencia_slot']['hashes_arquivos']['fixture']
            self.assertIsNotNone(malformado['sha256']);self.assertIn('erro',malformado)
            self.assertEqual(ler(saida/'k_a064.json')['H']['execucao']['estado'],'ok')

    def test_catalogo_ausente_falha_lote_sem_N_ficticio(self):
        import tempfile
        from piloto_engenharia.lote import executar_lote
        with tempfile.TemporaryDirectory() as tmp:
            saida=Path(tmp)/'lote'
            with self.assertRaisesRegex(ValueError,'catálogo'):executar_lote(Path(tmp)/'sem_dados',saida)
            self.assertIsNone(ler(saida/'erro_lote.json')['N_planejado'])
            self.assertFalse((saida/'resumo.json').exists())


class GuardasProntidao(unittest.TestCase):
    def completo(self):
        from piloto_engenharia.prontidao import REQUISITOS,hash_lote
        p=ler(NOVO/'proposta_lote_real.json')
        p.update(modelo='MOCK_DIAGNOSTICO',configuracao={},orcamento_api_centavos=1000,
                 precos_BRL_por_milhao=dict(entrada=1,saida=1),requisitos={k:'verificado' for k in REQUISITOS})
        p['aprovacao_lote']=dict(aprovado=True,lote_id='LOTE_HIPOTETICO',lote_hash=hash_lote(p),declarante='TESTE_APENAS')
        return p
    def test_declaracao_completa_so_diagnostico(self):
        r=diagnosticar(self.completo())
        self.assertTrue(r['pronto_para_execucao'])
        self.assertIn('não comprova aprovação externa',r['aviso'])
    def test_aprovacao_falsa_vazia_ou_desvinculada(self):
        for a in (False,True,'',{},dict(aprovado=False),dict(aprovado=True,lote_id='x',lote_hash='errado',declarante='teste')):
            p=self.completo();p['aprovacao_lote']=a
            self.assertFalse(diagnosticar(p)['pronto_para_execucao'])
            self.assertIn('aprovacao_lote',diagnosticar(p)['pendencias'])
    def test_requisito_removido_continua_pendente(self):
        p=self.completo();del p['requisitos']['politica_H_sem_oraculo']
        self.assertIn('politica_H_sem_oraculo',diagnosticar(p)['pendencias'])
        p['requisitos']={}
        from piloto_engenharia.prontidao import REQUISITOS
        self.assertTrue(REQUISITOS<=set(diagnosticar(p)['pendencias']))
    def test_modelo_configuracao_e_orcamento(self):
        for campo,v in [('modelo',' '),('configuracao',[]),('orcamento_api_centavos',False),('orcamento_api_centavos',0)]:
            p=self.completo();p[campo]=v
            self.assertIn(campo,diagnosticar(p)['pendencias'])


class IsolamentoContraprovas(unittest.TestCase):
    def test_erro_contraprovas_nao_substitui_previsao_normal(self):
        import tempfile
        from piloto_engenharia.lote import executar_lote
        with tempfile.TemporaryDirectory() as tmp, patch('piloto_engenharia.lote.contraprovas',side_effect=RuntimeError('Falha na fase de contraprovas')):
            saida=Path(tmp)/'lote';r=executar_lote(DATA,saida)
            self.assertEqual(r['normais']['N_H'],15)
            self.assertEqual(r['normais']['estados_H'],dict(ok=12,parcial=3))
            pacote=ler(saida/'k_98f3.json')
            self.assertEqual(pacote['H']['execucao']['estado'],'ok')
            self.assertEqual((pacote['H']['delta_dias']['valor'],pacote['H']['delta_centavos']['valor']),(-2,0))
            self.assertEqual(r['contraprovas']['N'],12)
            self.assertTrue(all(x['resultado']['execucao']['estado']=='erro' for x in ler(saida/'contraprovas.json')))
            self.assertIn('Falha na fase',ler(saida/'erro_preparacao_contraprovas.json')['mensagem'])


if __name__=='__main__':unittest.main()
