"""Contraprovas sintéticas H07; não medem desempenho do modelo em casos reais."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from hibrido_v07 import avaliar, construir, SimuladoV07, LocalV07
from hibrido_v07.contratos import montar_contexto, VERSAO
from hibrido_v07.wire import WIRE, incorporar, conferir_vinculo
from hibrido_v07.avaliacao import conferir_proveniencia_h
from interpretacao_no.adaptadores import RespostaTransporte
from interpretacao_no.contratos import hash_json

spec = importlib.util.spec_from_file_location('fixture_h06', Path(__file__).parents[1] / 'etapa9_h_v06/test_encaminhamentos.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
projeto, REF, encaminhar = f.projeto, f.REF, f.encaminhar


def wire_fixture(c, **kwargs):
    """Converte apenas fixture sintética prescrita; não é reparador de respostas reais."""
    a = f.analise(c, **kwargs)
    w = {k: deepcopy(a[k]) for k in ('avaliacao', 'propostas', 'justificativa', 'lacunas', 'pendencias_operacionais', 'encaminhamentos')}
    w['schema_version'] = WIRE
    for q in w['avaliacao'].values():
        if q['estado'] != 'direcao': q.pop('direcao')
    for p in w['propostas']:
        p['origem_ref'] = p['origens_causais'][0]['fato_ref']
        for k in ('id', 'no_id', 'origens_causais'): p.pop(k)
        if isinstance(p['valor'], dict) and 'estado' in p['valor'] and p['valor']['estado'] != 'direcao':
            p['valor'].pop('direcao')
    checklist(w, c)
    return w


def checklist(w, c):
    w['resolucoes_regras'] = [dict(regra_id=r['regra_id'], propostas_indices=[i for i,p in enumerate(w['propostas'],1) if r['regra_id'] in p['regra_refs']]) for r in c['escopos_regras']]


def pendencia(d='custo'):
    return dict(dimensao=d, motivo='MOCK: falta definição contratual não representável', evidencias=[REF])


def contexto(no='n_alpha'):
    e, ev = projeto(); p = construir(e, ev, execucao_id='mock_h07')
    return montar_contexto(e, ev, execucao_id=p.execucao_id, no_id=no, revisao=1,
                          responsabilidades_operacionais=p.responsabilidades_operacionais, **p.plano[no])


def rodar(alterar=None, **kwargs):
    e, ev = projeto()
    def resposta(c):
        w = wire_fixture(c, **kwargs)
        if alterar: alterar(c, w)
        return w
    return avaliar(e, ev, SimuladoV07(resposta), construir(e, ev, execucao_id='mock_h07'))


def proveniencia(r):
    e, ev = projeto()
    r.update(contrato_h='4.0-h', condicao_orquestracao='orquestracao_v07', politica_versao='7.0-politica-h-dimensoes')
    r['execucao'].update(origem='simulado', modelo=None, configuracao={}, config_hash=hash_json({}))
    slot=dict(modelo=None, config_hash=hash_json({}), origem='simulado', execucao_id=r['execucao_id'], evento_id=ev['evento_id'], snapshot_hash=hash_json(e), projeto_id=e['projeto_id'], versao_projeto=e['versao'], versao_protocolo=r['politica_versao'])
    conferir_proveniencia_h(r, slot, uso='teste_prescrito')


class Vinculo(unittest.TestCase):
    def test_hash_e_ids_gerados_pelo_adaptador_sem_copia_pelo_modelo(self):
        c=contexto(); w=wire_fixture(c); raw=json.dumps(w)
        class Transporte:
            versao_formato_local=VERSAO
            def __call__(self, req): return RespostaTransporte(raw)
        r=LocalV07(Transporte(), modelo='mock', configuracao={}, timeout_s=1).analisar(c)
        self.assertEqual(r['execucao']['estado'], 'ok', r['execucao'])
        self.assertEqual(r['contexto_hash'],c['contexto_hash'])
        self.assertEqual(r['execucao']['tentativas'][0]['resposta_bruta'],raw)
        self.assertEqual(r['propostas'][0]['id'],'n_alpha:r1:p1')
        conferir_vinculo(r,c)
        outro=deepcopy(c);outro['execucao_id']='outra';outro['contexto_hash']=hash_json({k:v for k,v in outro.items() if k!='contexto_hash'})
        with self.assertRaises(ValueError): conferir_vinculo(r,outro)
        r['propostas'][0]['valor']['valor']+=1
        with self.assertRaises(ValueError): conferir_vinculo(r,c)

    def test_campo_tecnico_retornado_e_rejeitado_sem_reparo(self):
        c=contexto()
        for campo in ('contexto_hash','analise_id','no_id','execucao_id'):
            w=wire_fixture(c);w[campo]='nao_confiavel'
            with self.subTest(campo=campo), self.assertRaises(ValueError):incorporar(w,c)
        w=wire_fixture(c);w['propostas'][0]['origens_causais']=[]
        with self.assertRaises(ValueError):incorporar(w,c)

    def test_sinal_derivado_e_quantidade_absoluta_validada(self):
        c=contexto()
        for valor,direcao in ((-2,'reducao'),(0,'zero'),(3,'aumento')):
            w=wire_fixture(c);w['avaliacao']['prazo']=dict(estado='exato',valor=valor,evidencias=[REF],lacunas=[],motivo=None)
            a=incorporar(w,c)
            self.assertEqual(a['avaliacao']['prazo']['direcao'],direcao)
            self.assertEqual(a['propostas'][0]['valor']['direcao'],'desconhecida')
        for valor in (-1,True,1.5,'3'):
            w=wire_fixture(c);w['propostas'][0]['valor']['valor']=valor
            with self.subTest(valor=valor),self.assertRaises(ValueError):incorporar(w,c)
        w=wire_fixture(c);w['propostas'][0]['valor']['direcao']='aumento'
        with self.assertRaises(ValueError):incorporar(w,c)

    def test_desconhecido_direcional_e_falso_zero(self):
        c=contexto();w=wire_fixture(c)
        w['avaliacao']['custo']=dict(estado='direcao',valor=None,direcao='aumento',evidencias=[REF],lacunas=['Preço não informado'],motivo=None)
        a=incorporar(w,c)
        self.assertIsNone(a['avaliacao']['custo']['valor'])
        self.assertEqual(a['avaliacao']['custo']['direcao'],'aumento')
        self.assertIsNone(a['avaliacao']['prazo']['valor'])
        w['avaliacao']['custo'].pop('direcao');w['avaliacao']['custo'].update(estado='exato',valor=0)
        with self.assertRaises(ValueError):incorporar(w,c)

    def test_checklist_exige_vinculo_explicito_sem_inventar_regra(self):
        c=contexto('n_join');w=wire_fixture(c)
        incorporar(w,c)
        for indices in ([0],[True],[99],[1,1],[],[3]):
            alterado=deepcopy(w);alterado['resolucoes_regras'][0]['propostas_indices']=indices
            with self.subTest(indices=indices),self.assertRaises(ValueError):incorporar(alterado,c)
        w['resolucoes_regras']=[]
        with self.assertRaises(ValueError):incorporar(w,c)


class Dimensoes(unittest.TestCase):
    def test_pipeline_exato_com_mesma_matematica(self):
        r=rodar(); self.assertEqual(r['execucao']['estado'],'ok',r)
        self.assertEqual((r['delta_dias']['valor'],r['delta_centavos']['valor']),(2,11000))
        proveniencia(r)

    def test_manutencao_escopada_resolve_encaminhamento_de_duracao(self):
        def alterar(c,w):
            if c['no_id']=='n_alpha':w['encaminhamentos']=[encaminhar(c,'substituir_duracao','n_join')]
        r=rodar(alterar)
        self.assertEqual(r['execucao']['estado'],'ok',r.get('lacunas'))
        item=r['registro_operacional']['fechamento_final']['encaminhamentos'][0]
        self.assertEqual(item['criterio'],'manutencao_escopada_clausula_unica')
        proveniencia(r)

    def test_equivalencia_nao_aceita_regra_diferente_ambigua_ou_sem_proposta(self):
        from hibrido_v07.escopo import reconciliar
        r=rodar(); e,_=projeto()
        aceitas=[p for t in r['rastro_orquestracao'] for p in t['analise']['propostas']]
        pedido=dict(no_origem='n_alpha',analise_id='mock',contexto_hash='mock',encaminhamento=encaminhar(contexto(),'substituir_duracao','n_join'))
        for modo in ('outra','ambigua','sem_proposta','sem_condicao','outra_unidade'):
            ps=deepcopy(aceitas); regras=deepcopy(e['regras_locais']); req=deepcopy(pedido)
            if modo=='outra':regras[0]['id']='outra'
            if modo=='ambigua':regras.append(dict(regras[0],id='outra'))
            if modo=='sem_proposta':ps=[]
            if modo=='sem_condicao':
                for p in ps:p['condicoes']=[]
            if modo=='outra_unidade':req['encaminhamento']['unidade']='BRL_centavo'
            self.assertEqual(reconciliar([req],ps,regras)[0]['estado'],'pendente',modo)

    def test_pendencia_so_de_custo_preserva_prazo(self):
        def alterar(c,w):
            if c['no_id']=='n_alpha':w['pendencias_operacionais']=[pendencia()]
        r=rodar(alterar)
        self.assertEqual(r['execucao']['estado'],'parcial',r)
        self.assertEqual(r['delta_dias']['valor'],2)
        self.assertEqual(r['delta_centavos']['estado'],'indeterminado')
        self.assertEqual(r['consumo']['analises'],4)
        proveniencia(r)
        r['delta_centavos']=deepcopy(r['delta_dias'])
        with self.assertRaises(ValueError):proveniencia(r)

    def test_pendencia_temporal_ou_ambos_bloqueia(self):
        for d in ('prazo','ambos'):
            def alterar(c,w):
                if c['no_id']=='n_alpha':w['pendencias_operacionais']=[pendencia(d)]
            r=rodar(alterar)
            self.assertIsNone(r['delta_dias']['valor'])
            self.assertIsNone(r['delta_centavos']['valor'])
            self.assertEqual(r['consumo']['analises'],2)
            proveniencia(r)

    def test_clausula_de_custo_pendente_nao_inventa_zero(self):
        def alterar(c,w):
            if c['no_id']=='n_join':
                w['propostas']=[p for p in w['propostas'] if p['operacao']!='confirmar_ausencia_parcela_adicional']
                checklist(w,c)
        r=rodar(alterar)
        self.assertEqual(r['delta_dias']['valor'],2)
        self.assertIsNone(r['delta_centavos']['valor'])
        proveniencia(r)

    def test_clausula_de_duracao_nao_vinculada_continua_pendente(self):
        def alterar(c,w):
            if c['no_id']=='n_join':
                p=w['propostas'][0]
                p.update(operacao='substituir_duracao',regra_refs=[],condicoes=[],valor=dict(estado='exato',valor=3,evidencias=[REF],lacunas=[],motivo=None))
                checklist(w,c)
        r=rodar(alterar)
        self.assertIsNone(r['delta_dias']['valor'])
        self.assertTrue(any('duração sem resolução' in x for x in r['lacunas']))
        proveniencia(r)

    def test_indeterminacoes_reais_nao_se_tornam_numeros(self):
        for kwargs in ({'desconhecer':True},{'taxas_desconhecidas':True}):
            r=rodar(**kwargs)
            self.assertEqual(r['execucao']['estado'],'parcial',r)
            self.assertIsNone(r['delta_centavos']['valor'])
            if kwargs.get('desconhecer'):self.assertIsNone(r['delta_dias']['valor'])
            else:self.assertEqual(r['delta_dias']['valor'],2)
            proveniencia(r)

    def test_cache_revalida_vinculo_e_nao_herda_pendencias(self):
        e,ev=projeto();p=construir(e,ev,execucao_id='mock_cache');i=SimuladoV07(wire_fixture)
        r=avaliar(e,ev,i,p);self.assertEqual(r['execucao']['estado'],'ok')
        r=avaliar(e,ev,i,p);self.assertTrue(all(t['processamento']=='reuso_cache' for t in r['rastro_orquestracao']))
        key=next(iter(p.cache));p.cache[key]['propostas'][0]['valor']['valor']+=1
        r=avaliar(e,ev,i,p);self.assertEqual(r['execucao']['estado'],'erro')


if __name__=='__main__':unittest.main()

class EntradasVigentes(unittest.TestCase):
    def test_contextos_15_casos_sem_gabarito_com_checklist_e_fechamento(self):
        from piloto_real.inputs import carregar
        from hibrido_v07 import executar_h
        casos=carregar(Path(__file__).parents[2]/'data/desenvolvimento')
        self.assertEqual(len(casos),15)
        for caso in casos:
            with self.subTest(caso=caso['caso_id']):
                p=construir(caso['estado'],caso['evento'],execucao_id='mock_'+caso['caso_id'])
                def resposta(c):
                    q=dict(estado='indeterminado',valor=None,evidencias=[],lacunas=['MOCK sem interpretação factual'],motivo=None)
                    w=dict(schema_version=WIRE,avaliacao=dict(prazo=q,custo=deepcopy(q)),propostas=[],justificativa='MOCK sem semântica',lacunas=[],pendencias_operacionais=[],encaminhamentos=[])
                    checklist(w,c)
                    return w
                r=executar_h(caso['base'],caso['evento_comum'],caso['fontes'],caso['estado'],caso['evento'],caso['views']['H'],SimuladoV07(resposta),p,vinculo=caso['vinculo'],origem='simulado')
                self.assertNotEqual(r['execucao']['estado'],'erro',r['execucao'])
                slot=dict(modelo=None,config_hash=hash_json({}),origem='simulado',execucao_id=p.execucao_id,evento_id=caso['evento']['evento_id'],snapshot_hash=hash_json(caso['estado']),projeto_id=caso['estado']['projeto_id'],versao_projeto=caso['estado']['versao'],versao_protocolo=p.versao)
                conferir_proveniencia_h(r,slot,uso='teste_prescrito')
