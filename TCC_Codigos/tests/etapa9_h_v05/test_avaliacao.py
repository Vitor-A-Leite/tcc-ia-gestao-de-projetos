"""Pipeline offline da fronteira v05 à normalização e métricas; sem rede."""
import json, unittest
from pathlib import Path
from copy import deepcopy
from condicoes.views import montar_views
from interpretacao_no.contratos import hash_json
from hibrido_v05 import executar_h,construir,SimuladoV05,SCHEMA
from hibrido_v05.avaliacao import normalizar,registrar,hash_implementacao
from hibrido_v05.metricas import avaliar
from avaliacao.execucoes import normalizar as legado
from avaliacao.demonstracao import montar_demo
from cenarios import analise
ROOT=Path(__file__).resolve().parents[2]/'data/desenvolvimento'
def pipeline():
    def ler(s):return json.loads((ROOT/s).read_text())
    b=ler('projeto_minimo_v1/inputs/base.json'); ec=ler('projeto_minimo_v1/inputs/cenarios.json')['casos'][1]
    f=ler('projeto_minimo_v1/inputs/fontes.json')['fontes']; g=ler('projeto_minimo_grafo_v1/estado_projeto.json')
    ev=ler('orquestracao_simulada_v1/k_09c2.json')['evento']
    vinculo=dict(base_hash=hash_json(b),grafo_hash=hash_json(g),versao_base=b['versao_projeto'],versao_grafo=g['versao'])
    view=montar_views(b,ec,f,g,vinculo=vinculo)['H']
    def resposta(c):
        a=analise(c,versao=SCHEMA);a['propostas']=[]
        for q in a['avaliacao'].values():q.update(estado='indeterminado',valor=None,direcao='desconhecida',evidencias=[],lacunas=['MOCK: fato não interpretado'])
        a['pendencias_operacionais']=['MOCK sem interpretação semântica deste cenário']
        return a
    p=construir(g,ev,execucao_id='mock_fronteira_v05')
    r=executar_h(b,ec,f,g,ev,view,SimuladoV05(resposta),p,vinculo=vinculo,origem='simulado')
    m,rs,refs,_=montar_demo();m['execucoes']=m['execucoes'][:3];rs=rs[:3]
    m['schema_version']='2.0-manifesto-h05'
    s=m['execucoes'][1];s.update(projeto_id=b['projeto_id'],evento_id=ev['evento_id'],execucao_id=p.execucao_id,versao_projeto=g['versao'],view_hash=view['view_hash'],snapshot_hash=hash_json(g),evento_hash=hash_json(ev),codigo_hash=hash_implementacao(),versao_protocolo=p.versao,origem='simulado',modelo=None,config_hash=hash_json({}))
    rs[1]=registrar(s,r)
    # Referência exclusivamente estrutural do MOCK: sem gabarito ou inferibilidade afirmada.
    ref=deepcopy(refs[0]);ref['caso_id']=s['caso_id'];ref['versao_projeto']=s['versao_projeto']
    for d in ('prazo','custo'):ref['por_view']['H'][d].update(estado='pendente',view_hash=view['view_hash'])
    return m,rs,refs+[ref],r
class Avaliacao(unittest.TestCase):
    def test_fronteira_normalizacao_e_metricas(self):
        m,rs,refs,r=pipeline();n=normalizar(m,rs)
        self.assertTrue(any(p.get('analise',{}).get('execucao',{}).get('estado')=='ok' for p in r['rastro_orquestracao']))
        self.assertFalse(n['anomalias'],n['anomalias']);self.assertEqual(r['contrato_h'],'2.0-h')
        self.assertEqual(n['linhas'][1]['resultado_original'],r)
        # Mesma lógica de métricas com referências artificiais e sem alegação de acurácia.
        por={(x['caso_id'],x['versao_projeto']):x for x in refs}
        avaliar(m,rs,list(por.values()))
        with self.assertRaises(ValueError):legado(m,rs)
    def test_rejeita_envelope_ou_analise_legada_sem_reidentificar(self):
        for alteracao in ('envelope','local'):
            m,rs,_,r=pipeline()
            if alteracao=='envelope':r['contrato_h']='1.0-h'
            else:r['rastro_orquestracao'][0]['analise']['schema_version']='1.0-proposta'
            rs[1]=registrar(m['execucoes'][1],r)
            self.assertTrue(normalizar(m,rs)['anomalias'])
if __name__=='__main__':unittest.main()
