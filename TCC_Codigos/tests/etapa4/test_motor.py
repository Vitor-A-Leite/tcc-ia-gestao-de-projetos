"""Testes autorais de desenvolvimento, expectativas apartadas do runtime."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from motor_deterministico import calcular
from motor_deterministico.conhecimento import Intervalo, maximo
from motor_deterministico.motor import resumo, incidencia

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/desenvolvimento'


class MotorTest(unittest.TestCase):
    def setUp(self):
        self.e = json.loads((DATA / 'projeto_minimo_grafo_v1/estado_projeto.json').read_text())
        self.x = json.loads((DATA / 'propostas_manuais_v1/k_09c2.json').read_text())

    def rodar(self, reautorizar=False):
        if reautorizar:
            self.x['politica']['autorizacoes'] = {p['id']: resumo(p) for p in self.x['propostas']}
        return calcular(self.e, self.x['evento'], self.x['propostas'], self.x['politica'])

    def erro(self, resultado):
        self.assertEqual(resultado['execucao']['estado'], 'erro', resultado)
        self.assertNotIn('delta_dias', resultado)

    def test_baseline_e_imutabilidade(self):
        antes = deepcopy(self.e)
        r = calcular(self.e)
        self.assertEqual(r['fim_novo']['valor'], 10)
        self.assertEqual(r['custo_novo']['valor'], 500000)
        self.assertEqual(r['delta_dias']['valor'], 0)
        self.assertEqual(self.e, antes)
        self.assertEqual(len(r['livro_parcelas']), 5)
        self.assertEqual(next(n for n in r['resultados_nos'] if n['no_id']=='n_73fa')['fim']['estado'], 'inaplicavel')

    def test_oito_casos(self):
        esperados = {'k_b731':(0,0), 'k_09c2':(2,40000), 'k_e168':(0,30000),
                     'k_547a':(2,0), 'k_a92f':(0,15000), 'k_23d8':(None,None),
                     'k_f04b':(-1,-10000), 'k_8c65':(2,None)}
        for nome, (dias,custo) in esperados.items():
            with self.subTest(nome=nome):
                self.x = json.loads((DATA / f'propostas_manuais_v1/{nome}.json').read_text())
                r = self.rodar()
                self.assertNotEqual(r['execucao']['estado'], 'erro',r)
                self.assertEqual(r['delta_dias']['valor'],dias)
                self.assertEqual(r['delta_centavos']['valor'],custo)
                if custo is None:
                    self.assertEqual(r['delta_centavos']['direcao'],'aumento')
                    self.assertEqual(r['delta_centavos']['limites']['inferior'],20000)
                    self.assertEqual(r['custo_novo']['limites']['inferior'],520000)
                    self.assertEqual(r['parcial_identificado_centavos'],520000)

    def test_convergencia_nao_soma_atrasos(self):
        p=deepcopy(self.x['propostas'][0]); p.update(id='duracao_preparo',operacao='substituir_duracao',alvo_id='n_915c',atributo='duracao',regra_refs=[])
        p['valor']['valor']=7
        self.x['propostas'].append(p)
        r=self.rodar(True)
        self.assertEqual(r['delta_dias']['valor'],2)

    def test_piso_preservado(self):
        a=self.e['atividades'][0]; a['restricoes_liberacao'][0]['valor']['valor']=8
        # Baseline passa a A8-9/C9-12/D12-14; custo base já inclui 4 diárias.
        self.e['linha_base']['fim']['valor']=14
        self.e['linha_base']['custo_centavos']['valor']=540000
        self.e['parcelas_base'][-1]['valor_centavos']=140000
        self.e['regras_custo'][0]['decomposicao_base']['incidencia_centavos']['valor']=40000
        r=self.rodar()
        self.assertEqual(r['delta_dias']['valor'],0)
        self.assertEqual(next(n for n in r['resultados_nos'] if n['no_id']=='n_42be')['inicio']['valor'],8)

    def test_cobranca_referida_duas_vezes(self):
        p=deepcopy(self.x['propostas'][-1]); p['id']='outra_referencia'; self.x['propostas'].append(p)
        self.assertEqual(self.rodar(True)['delta_centavos']['valor'],40000)

    def test_colisao_obrigacao(self):
        p=deepcopy(self.x['propostas'][-1]); p['id']='colisao'; p['valor']['valor']=21000; self.x['propostas'].append(p)
        self.erro(self.rodar(True))

    def test_autorizacao_obsoleta(self):
        self.x['propostas'][0]['valor']['valor']=8
        self.erro(self.rodar())

    def test_sem_condicao_local(self):
        self.x['propostas']=self.x['propostas'][:1]
        self.erro(self.rodar(True))

    def test_sem_aceite_confirmacao_nao_autorizada(self):
        self.x['propostas'][1]['condicoes'][0]['estado']='pendente'
        self.erro(self.rodar(True))

    def test_fonte_invisivel(self):
        self.x['propostas'][0]['evidencias'][0]['fonte_id']='inexistente'
        self.erro(self.rodar(True))

    def test_ciclo(self):
        r=deepcopy(self.e['relacoes'][-1]); r.update(id='ciclo',origem_id='n_e659',destino_id='n_a367'); self.e['relacoes'].append(r)
        self.erro(self.rodar())

    def test_endpoint(self):
        self.e['relacoes'][-1]['destino_id']='fantasma'; self.erro(self.rodar())

    def test_unidade(self):
        self.e['atividades'][0]['duracao']['unidade']='hora'; self.erro(self.rodar())

    def test_negativo_bool_e_fracao(self):
        for valor in (-1,True,1.5):
            with self.subTest(valor=valor):
                self.x['propostas'][0]['valor']['valor']=valor
                self.erro(self.rodar(True))

    def test_baseline_inconsistente(self):
        self.e['linha_base']['fim']['valor']=11; self.erro(self.rodar())

    def test_decomposicao_base_inconsistente(self):
        self.e['regras_custo'][0]['decomposicao_base']['incidencia_centavos']['valor']=10000; self.erro(self.rodar())

    def test_zero_com_lacuna(self):
        self.x['propostas'][0]['valor']['lacunas']=['não confirmado']; self.erro(self.rodar(True))

    def test_sem_fechamento(self):
        self.e['declaracoes_completude']['custos']['completa']=False; self.erro(self.rodar())

    def test_atividade_fora_do_marco(self):
        self.e['relacoes']=[r for r in self.e['relacoes'] if r['id']!='l_263e']; self.erro(self.rodar())

    def test_credito_temporal_vs_nao_credito(self):
        # Base com extensão preexistente: não pode ser contada duas vezes.
        self.e['atividades'][1]['duracao']['valor']=7
        self.e['linha_base']['fim']['valor']=12
        self.e['linha_base']['custo_centavos']['valor']=520000
        self.e['parcelas_base'][-1]['valor_centavos']=120000
        self.e['regras_custo'][0]['decomposicao_base']['incidencia_centavos']['valor']=20000
        self.x=json.loads((DATA/'propostas_manuais_v1/k_f04b.json').read_text())
        r=self.rodar(); self.assertEqual(r['delta_centavos']['valor'],-10000)
        self.e['regras_custo'][0]['politica_reducao']='recalculavel_com_credito'
        r=self.rodar(); self.assertEqual(r['delta_centavos']['valor'],-30000)

    def test_dominancia_limite_documentado(self):
        p=self.x['propostas'][0]; p['valor'].update(estado='indeterminado',valor=None,lacunas=['Dia exato pendente'],limites={'inferior':2,'superior':4})
        r=self.rodar(True); self.assertEqual(r['delta_dias']['valor'],0)
        p['valor']['limites']['superior']=None
        r=self.rodar(True); self.assertIsNone(r['delta_dias']['valor']); self.assertEqual(r['execucao']['estado'],'parcial')

    def test_ids_opacos_e_ordem(self):
        # Troca todos os IDs do estado/evento/propostas/política; nenhum ID dirige a conta.
        ids=set()
        def coletar(o):
            if isinstance(o,dict):
                for k,v in o.items():
                    if k in ('id','projeto_id','evento_id'): ids.add(v)
                    coletar(v)
            elif isinstance(o,list):
                for v in o: coletar(v)
        coletar(self.e); coletar(self.x)
        mapa={v:f'opaco_{i}' for i,v in enumerate(sorted(ids))}
        def trocar(o):
            if isinstance(o,dict): return {mapa.get(k,k):trocar(v) for k,v in o.items()}
            if isinstance(o,list): return [trocar(v) for v in o]
            if isinstance(o,str): return mapa.get(o,o)
            return o
        self.e=trocar(self.e); self.x=trocar(self.x)
        self.e['atividades'].reverse(); self.e['relacoes'].reverse()
        r=self.rodar(True); self.assertEqual(r['delta_centavos']['valor'],40000); self.assertEqual(r['delta_dias']['valor'],2)

    def test_dupla_contagem_direta_temporal(self):
        self.x['propostas'][-1]['alvo_id']='p_c8a0'; self.erro(self.rodar(True))

    def test_proposta_fora_catalogo(self):
        self.x['propostas'][0]['operacao']='executar_python'; self.erro(self.rodar(True))

    def test_dois_eventos_ou_versao_errada(self):
        self.x['evento']['versao_projeto']='outra'; self.erro(self.rodar())

    def test_completude_vazia(self):
        self.e['declaracoes_completude']={}; self.erro(self.rodar())

    def test_base_com_limite_nao_exata(self):
        for chave in ('fim', 'custo_centavos'):
            with self.subTest(chave=chave):
                original=deepcopy(self.e['linha_base'][chave])
                c=self.e['linha_base'][chave]
                c.update(estado='indeterminado', valor=None, lacunas=['Base não confirmada'], limites={'inferior':original['valor'], 'superior':None})
                self.erro(self.rodar())
                self.e['linha_base'][chave]=original

    def test_decomposicao_nao_exata(self):
        c=self.e['regras_custo'][0]['decomposicao_base']['fixo_centavos']
        c.update(estado='indeterminado',valor=None,lacunas=['Fixo não confirmado'],limites={'inferior':100000,'superior':None})
        self.erro(self.rodar())

    def test_restricao_orfa_reutiliza_regra(self):
        r=deepcopy(self.e['atividades'][0]['restricoes_liberacao'][1]); r['id']='orfa'
        self.e['atividades'][0]['restricoes_liberacao'].append(r)
        self.erro(self.rodar())

    def test_intervalo_temporal_indeterminado_e_taxa_zero(self):
        r=deepcopy(self.e['regras_custo'][0])
        r['intervalo']['inicio_ref']={'atividade_id':'n_42be','atributo':'inicio'}
        datas={'n_42be':{'inicio':Intervalo(None,None,(),('Início sem limite',))},'n_e659':{'fim':Intervalo(12,12)}}
        i=incidencia(r,datas)
        self.assertEqual(i.saida()['estado'],'indeterminado')
        r['taxa_centavos_dia']=0
        self.assertEqual(incidencia(r,datas).saida()['valor'],0)
        r['taxa_centavos_dia']=10000
        datas['n_42be']['inicio']=Intervalo(13,13)
        with self.assertRaises(ValueError): incidencia(r,datas)

    def test_rastro_por_no(self):
        r=self.rodar(); nos={n['no_id']:n for n in r['resultados_nos']}
        self.assertFalse(nos['n_73fa']['decisoes']); self.assertFalse(nos['n_73fa']['origens_causais'])
        self.assertEqual(len(nos['n_c820']['decisoes']),1)
        self.assertEqual(nos['n_42be']['efeitos_custo'][0]['parcela_id'],'p_07a4')
        self.assertEqual(nos['n_e659']['efeitos_custo'][0]['parcela_id'],'p_c8a0')
        self.assertIn('c_724f',nos['n_e659']['regras_aplicadas'])
        self.assertIn('n_c820',nos['n_42be']['predecessores_versoes'])

    def test_sintetico_disponibilidade_sem_clausula_local(self):
        self.e['regras_locais']=[]
        self.x['propostas']=[p for p in self.x['propostas'] if not p['operacao'].startswith('confirmar_')]
        self.x['politica']['requisitos_locais']=[]
        r=self.rodar(True)
        self.assertEqual(r['execucao']['estado'],'ok',r)
        self.assertEqual(r['delta_dias']['valor'],2)
        self.assertEqual(r['delta_centavos']['valor'],40000)

    def test_regra_local_fora_dos_candidatos_nao_exigida(self):
        self.e['regras_locais'][0]['no_id']='n_73fa'
        self.x['propostas']=[p for p in self.x['propostas'] if not p['operacao'].startswith('confirmar_')]
        self.x['politica']['requisitos_locais']=[]
        r=self.rodar(True)
        self.assertEqual(r['execucao']['estado'],'ok',r)
        self.assertEqual(r['delta_dias']['valor'],2)

    def test_regra_local_candidata_nao_pode_ser_omitida(self):
        self.x['politica']['requisitos_locais']=[]
        self.erro(self.rodar())

    def test_decisoes_aditivos_nos_marcos(self):
        for caso in ('k_547a','k_8c65'):
            with self.subTest(caso=caso):
                self.x=json.loads((DATA/f'propostas_manuais_v1/{caso}.json').read_text())
                r=self.rodar()
                marco=next(n for n in r['resultados_nos'] if n['no_id']=='n_e659')
                p=next(p for p in self.x['propostas'] if p['operacao']=='aplicar_regra_catalogada')
                self.assertIn(p['id'],[d['proposta_id'] for d in marco['decisoes']])
                self.assertTrue(all(o in marco['origens_causais'] for o in p['origens_causais']))
                self.assertEqual({p['id'] for p in self.x['propostas']}, {d['proposta_id'] for n in r['resultados_nos'] for d in n['decisoes']})
                self.assertEqual(len(r['decisoes']),len(self.x['propostas']))

    def test_decisao_substituicao_piso_no_proprietario(self):
        p=deepcopy(self.x['propostas'][0]); p.update(id='alterar_piso',operacao='substituir_restricao',alvo_id='r_559aea',atributo='valor',regra_refs=[])
        p['valor']['valor']=8
        self.x['propostas'].append(p)
        r=self.rodar(True)
        no=next(n for n in r['resultados_nos'] if n['no_id']=='n_42be')
        self.assertEqual(no['inicio']['valor'],8)
        self.assertIn(p['id'],[d['proposta_id'] for d in no['decisoes']])
        self.assertTrue(all(o in no['origens_causais'] for o in p['origens_causais']))
        self.assertEqual(next(d for d in r['decisoes'] if d['proposta_id']==p['id'])['nos_alvo'],['n_42be'])

    def test_gabarito_rejeitado(self):
        self.e['expected_delta']=2; self.erro(self.rodar())


if __name__ == '__main__':
    unittest.main()
