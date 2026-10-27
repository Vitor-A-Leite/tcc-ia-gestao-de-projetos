"""Contraprovas da revisão final: H/cache e desigualdades das referências."""
from copy import deepcopy
import unittest
from test_etapa7 import dados, views, load, D, resposta
from condicoes import Simulado
from condicoes.hibrido import executar_h
from interpretacao_no.contratos import hash_json
from orquestracao.simulacao import InterpretadorPrescrito, politica_prescrita
from avaliacao import normalizar, avaliar, registrar
from avaliacao.demonstracao import montar_demo, q
from avaliacao.referencias import preparar_referencias
from avaliacao.limites import validar_limites


class InterpretadorMock:
    """Usa conteúdo prescrito, transporte mock explícito; nunca chama provedor."""
    modelo='modelo-mock'
    configuracao={'parametro_teste':1}
    origem='transporte_mock'
    def __init__(self,fixture):self.prescrito=InterpretadorPrescrito(fixture)
    def analisar(self,c):
        a=self.prescrito.analisar(c)
        a['execucao'].update(origem='llm_transporte_injetado',modelo=self.modelo,
            configuracao=deepcopy(self.configuracao),config_hash=hash_json(self.configuracao),
            chamadas=1,tokens_entrada=7,tokens_saida=3,custo_api_centavos=None)
        return a


def h_cache(mock=False):
    b,e,f,g=dados();v=views(b,e,f,g)['H'];fixture=load(D/'orquestracao_simulada_v1/k_09c2.json')
    p=politica_prescrita(fixture)
    origem='transporte_mock' if mock else 'simulado'
    if mock:p.origem='teste_offline_transporte_mock'
    i=InterpretadorMock(fixture) if mock else InterpretadorPrescrito(fixture)
    vinculo=dict(base_hash=hash_json(b),grafo_hash=hash_json(g),versao_base=b['versao_projeto'],versao_grafo=g['versao'])
    def executar():return executar_h(b,e,f,g,fixture['evento'],v,i,p,vinculo=vinculo,origem=origem)
    primeiro=executar();segundo=executar()
    m,rs,_,_=montar_demo();m['execucoes']=m['execucoes'][:3];rs=rs[:3]
    s=m['execucoes'][1]
    s.update(projeto_id=b['projeto_id'],evento_id=e['evento_id'],execucao_id=p.execucao_id,versao_projeto=g['versao'],
        view_hash=v['view_hash'],snapshot_hash=hash_json(g),evento_hash=hash_json(fixture['evento']),
        origem=origem,modelo=getattr(i,'modelo',None),config_hash=hash_json(getattr(i,'configuracao',{})))
    rs[1]=registrar(s,segundo)
    return m,rs,primeiro,segundo


class ProvenienciaH(unittest.TestCase):
    def test_cache_real_contrato_sem_novo_consumo(self):
        for mock in (False,True):
            with self.subTest(mock=mock):
                m,rs,primeiro,segundo=h_cache(mock)
                self.assertEqual(segundo['condicao'],'H')
                self.assertEqual(segundo['condicao_orquestracao'],'orquestracao_v1')
                self.assertEqual(segundo['consumo']['observacoes_novas'],[])
                self.assertEqual(segundo['consumo']['chamadas'],0)
                self.assertEqual(segundo['consumo']['tokens_entrada'],0)
                usadas=[p for p in segundo['rastro_orquestracao'] if 'analise' in p]
                self.assertEqual(len(usadas),3)
                self.assertTrue(all(p['processamento']=='reuso_cache' for p in usadas))
                self.assertEqual(primeiro['consumo']['chamadas'],3 if mock else 0)
                out=normalizar(m,rs)
                self.assertEqual(out['anomalias'],[])
                self.assertEqual(out['linhas'][1]['desfechos']['custo']['classe'],'exato')
                self.assertEqual(out['linhas'][1]['consumo']['chamadas'],0)
    def test_view_hash_obrigatorio_todas_condicoes(self):
        for indice in (0,1,2):
            for valor in (None,'outro'):
                m,rs,_,_=montar_demo();r=rs[indice]['resultado']
                if valor is None:r.pop('view_hash')
                else:r['view_hash']=valor
                rs[indice]=registrar(m['execucoes'][indice],r)
                out=normalizar(m,rs)
                self.assertEqual(out['linhas'][indice]['desfechos']['prazo']['classe'],'invalido')
                self.assertEqual(len(out['linhas']),24)
                self.assertEqual(out['anomalias'][0]['tipo'],'view_divergente')
    def test_B_nao_passavel_como_H(self):
        m,rs,_,r=h_cache();b,e,f,g=dados();v=views(b,e,f,g)['B']
        baseline=Simulado(resposta(v,'x')).prever(v,execucao_id='x')
        s=m['execucoes'][1]
        # Ajusta identidades comuns para isolar a distinção de condição/contrato.
        baseline.update(execucao_id=s['execucao_id'],projeto_id=s['projeto_id'],evento_id=s['evento_id'],
            versao=s['versao_projeto'],view_hash=s['view_hash'],snapshot_hash=s['snapshot_hash'],evento_hash=s['evento_hash'])
        rs[1]=registrar(s,baseline)
        self.assertEqual(normalizar(m,rs)['anomalias'][0]['tipo'],'condicao_divergente')
        baseline['condicao']='H';rs[1]=registrar(s,baseline)
        self.assertIn('Envelope H ausente',normalizar(m,rs)['anomalias'][0]['tipo'])
    def test_prescrito_so_aceito_no_manifesto_de_teste(self):
        m,rs,_,_=montar_demo();m['uso']='desenvolvimento'
        out=normalizar(m,rs)
        self.assertEqual(out['linhas'][1]['desfechos']['prazo']['classe'],'invalido')
        self.assertEqual(out['linhas'][0]['desfechos']['prazo']['classe'],'exato')
        self.assertEqual(len(out['linhas']),24)
    def test_envelope_H_modelo_configuracao_origem(self):
        for campo,valor in [('modelo','outro'),('config_hash',hash_json({'outro':1})),('configuracao',{'outro':1}),('origem','simulado')]:
            m,rs,_,r=h_cache(mock=True);r['execucao'][campo]=valor
            rs[1]=registrar(m['execucoes'][1],r)
            self.assertEqual(normalizar(m,rs)['linhas'][1]['desfechos']['prazo']['classe'],'invalido')
    def test_analises_cacheadas_modelo_configuracao_origem(self):
        for campo,valor in [('modelo','outro'),('config_hash',hash_json({'outro':1})),('configuracao',{'outro':1}),('origem','simulado')]:
            m,rs,_,r=h_cache(mock=True)
            passo=next(p for p in r['rastro_orquestracao'] if 'analise' in p)
            passo['analise']['execucao'][campo]=valor
            rs[1]=registrar(m['execucoes'][1],r)
            out=normalizar(m,rs)
            self.assertIn('proveniencia_H_invalida',out['anomalias'][0]['tipo'])
            self.assertEqual(out['linhas'][1]['desfechos']['prazo']['classe'],'invalido')
            self.assertEqual(r['consumo']['chamadas'],0)
    def test_rastro_cache_ausente_ou_contagem_divergente(self):
        for tipo in ('ausente','analise_ausente','contagem'):
            m,rs,_,r=h_cache()
            if tipo=='ausente':r.pop('rastro_orquestracao')
            elif tipo=='analise_ausente':next(p for p in r['rastro_orquestracao'] if 'analise' in p).pop('analise')
            else:r['consumo']['analises']=0
            rs[1]=registrar(m['execucoes'][1],r)
            self.assertEqual(normalizar(m,rs)['linhas'][1]['desfechos']['prazo']['classe'],'invalido')


def referencias_autorais():
    b,_,f,g=dados();casos=load(D/'projeto_minimo_v1/inputs/cenarios.json')['casos']
    vs={ev['caso_id']:views(b,ev,f,g) for ev in casos}
    return preparar_referencias(load(D/'projeto_minimo_v1/referencias/gabaritos.json'),vs,
        dict(B=b['versao_projeto'],H=g['versao'],T=b['versao_projeto']))


def com_limite(qtd=None):
    m,rs,refs,a=montar_demo()
    limite=dict(inferior=20000,superior=None,unidade='BRL_centavo',grandeza='delta',
        proveniencia=dict(tipo='teste_prescrito',referencia_origem_hash=hash_json('limite-prescrito'),
            derivacao='delta >= 20000 centavos; magnitude exata desconhecida',fonte_ids=['f_demo']))
    ref=refs[5];ref['verdade']['custo'].update(unidade='BRL_centavo',limites=deepcopy(limite))
    for c in ('B','H','T'):
        ref['por_view'][c]['custo'].update(estado='direcao',valor=None,direcao='aumento',unidade='BRL_centavo',limites=deepcopy(limite))
        idx=next(i for i,r in enumerate(rs) if r['metadados']['caso_id']=='demo_5' and r['metadados']['condicao']==c)
        if qtd is not None:
            rs[idx]['resultado']['delta_centavos']=q(valor=qtd,unidade='BRL_centavo')
            rs[idx]=registrar(m['execucoes'][idx],rs[idx]['resultado'])
    return m,rs,refs,a


class LimitesReferencia(unittest.TestCase):
    def test_preserva_limites_sem_alterar_originais(self):
        orig=load(D/'projeto_minimo_v1/referencias/gabaritos.json');antes=hash_json(orig)
        refs=referencias_autorais()
        for r in refs:
            if r['caso_id'] not in ('k_23d8','k_8c65'):continue
            v=r['verdade']['custo']
            self.assertEqual(v['estado'],'direcao');self.assertIsNone(v['valor'])
            self.assertEqual(v['limites']['inferior'],20000);self.assertIsNone(v['limites']['superior'])
            self.assertEqual(v['unidade'],'BRL_centavo')
            self.assertEqual(v['limites']['proveniencia']['referencia_origem_hash'],r['referencia_origem_hash'])
            for c in ('B','H','T'):
                q=r['por_view'][c]['custo'];self.assertIsNone(q['valor'])
                self.assertEqual(q['limites']['inferior'],20000)
                self.assertTrue(set(q['limites']['proveniencia']['fonte_ids']) <= {f['fonte_id'] for f in q['fontes']})
        self.assertEqual(antes,hash_json(load(D/'projeto_minimo_v1/referencias/gabaritos.json')))
        self.assertTrue(any(r['por_view']['B']['prazo']['estado']=='pendente' for r in refs))
    def test_100_contradiz_300_compativel_sem_exatidao(self):
        for qtd,contradiz in ((10000,True),(20000,False),(30000,False)):
            m,rs,refs,a=com_limite(qtd)
            out=avaliar(m,rs,refs,a)
            for c in ('B','H','T'):
                met=out['metricas'][c+':custo']
                self.assertEqual(met['contradicao_limite'],dict(n=int(contradiz),comparaveis=1,N=8))
                self.assertEqual(met['erro_numerico']['n'],2)
                self.assertEqual(met['erro_numerico']['MAE'],150)
                self.assertEqual(met['falsa_certeza']['n'],2)
                item=next(x for x in out['detalhes'] if x['caso_id']=='demo_5' and x['condicao']==c and x['desfecho']=='custo')
                self.assertIsNone(item['erro_absoluto'])
                self.assertEqual(item['contradicao_limite'],contradiz)
                self.assertEqual(item['compatibilidade_limite'],'contradiz' if contradiz else 'compativel_sem_demonstrar_exatidao')
                self.assertEqual(item['suporte'],'nao_auditado')
    def test_direcao_sem_magnitude_nao_entra_diagnostico_numerico(self):
        m,rs,refs,a=com_limite()
        out=avaliar(m,rs,refs,a)
        self.assertEqual(out['metricas']['B:custo']['contradicao_limite'],dict(n=0,comparaveis=0,N=8))
    def test_limites_invalidos(self):
        mudancas=[('inferior',True),('inferior',1.5),('inferior','20000'),('unidade','BRL'),
            ('grandeza','custo_total'),('superior',10000),('superior',20000),('superior',-1)]
        for campo,valor in mudancas:
            m,rs,refs,a=com_limite(10000);refs[5]['verdade']['custo']['limites'][campo]=valor
            with self.subTest(campo=campo,valor=valor),self.assertRaises(ValueError):avaliar(m,rs,refs,a)
    def test_limite_sem_proveniencia_ou_unidade_invalido(self):
        for campo in ('proveniencia','unidade'):
            m,rs,refs,a=com_limite(10000);refs[5]['verdade']['custo']['limites'].pop(campo)
            with self.assertRaises(ValueError):avaliar(m,rs,refs,a)
        m,rs,refs,a=com_limite(10000);refs[5]['verdade']['custo']['unidade']='BRL'
        with self.assertRaises(ValueError):avaliar(m,rs,refs,a)
    def test_referencia_exata_fora_limite_rejeitada(self):
        m,rs,refs,a=com_limite()
        refs[5]['verdade']['custo'].update(estado='exato',valor=10000)
        with self.assertRaises(ValueError):avaliar(m,rs,refs,a)
    def test_limite_visivel_invalido_rejeitado(self):
        m,rs,refs,a=com_limite()
        refs[5]['por_view']['B']['custo']['limites']['inferior']=True
        with self.assertRaises(ValueError):avaliar(m,rs,refs,a)

if __name__=='__main__':unittest.main()
