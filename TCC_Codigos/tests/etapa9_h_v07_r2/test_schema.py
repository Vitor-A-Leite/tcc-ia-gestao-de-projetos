"""Contrato de geração conferido por jsonschema independente, sem API."""
from copy import deepcopy
from pathlib import Path
import json,unittest
from jsonschema import Draft202012Validator, ValidationError
from hibrido_v07_r2.schema import gerar,formato
from hibrido_v07_r2.wire import WIRE,incorporar
from hibrido_v07_r2 import construir,montar_contexto
from piloto_real.inputs import carregar
from test_vinculo_dimensoes import contexto,wire_fixture,pendencia,checklist

ROOT=Path(__file__).parents[2]

class Schema(unittest.TestCase):
    def test_fixtures_sinteticas_exatas_e_desconhecidas_passam_schema_independente(self):
        for no in ('n_alpha','n_beta','n_join','n_marco'):
            c=contexto(no);v=Draft202012Validator(gerar(c))
            for kwargs in ({},{'desconhecer':True},{'taxas_desconhecidas':True}):
                w=wire_fixture(c,**kwargs);v.validate(w);incorporar(w,c)
                w['pendencias_operacionais']=[pendencia()];v.validate(w)

    def test_reproducao_das_duas_respostas_reais_fora_de_escopo_e_impedida_pelo_schema(self):
        old=ROOT/'outputs/etapa9_piloto_v07_20261028'
        for repeticao in (1,2):
            p=old/f'etapa9-v07-90-BHT-R2-20261028-k_09c2-H-{repeticao}.json'
            t=next(t for t in json.loads(p.read_text())['resultado']['rastro_orquestracao'] if t['no_id']=='n_73fa')
            w=json.loads(t['analise']['execucao']['tentativas'][0]['resposta_bruta'])
            # Só marca de versão muda na contraprova; nenhuma operação é corrigida.
            w['schema_version']=WIRE
            erros=list(Draft202012Validator(gerar(t['contexto'])).iter_errors(w))
            self.assertTrue(any(list(e.path)==['propostas'] and e.validator=='maxItems' for e in erros))
            self.assertEqual(t['contexto']['permissoes'],[])

    def test_alvo_operacao_unidade_e_refs_nao_podem_sair_dos_catalogos(self):
        c=contexto();v=Draft202012Validator(gerar(c))
        for campo,valor in (('alvo_id','n_join'),('unidade','BRL_centavo'),('operacao','adicionar_parcela')):
            w=wire_fixture(c);w['propostas'][0][campo]=valor
            with self.subTest(campo=campo),self.assertRaises(ValidationError):v.validate(w)
        w=wire_fixture(c);w['propostas'][0]['origem_ref']['localizador']='inexistente'
        with self.assertRaises(ValidationError):v.validate(w)
        w=wire_fixture(c);w['contexto_hash']='nao_emitir'
        with self.assertRaises(ValidationError):v.validate(w)

    def test_schema_mantem_indeterminacao_sem_forcar_zero(self):
        c=contexto('n_join');w=wire_fixture(c,desconhecer=True)
        Draft202012Validator(gerar(c)).validate(w)
        self.assertTrue(any(p['valor'].get('estado')=='indeterminado' for p in w['propostas'] if isinstance(p['valor'],dict)))
        w['propostas'][0]['valor']['valor']=0
        with self.assertRaises(ValidationError):Draft202012Validator(gerar(c)).validate(w)

    def test_todos_contextos_possuem_schema_valido_e_limites_publicados(self):
        max_bytes=0;total=0
        for caso in carregar(ROOT/'data/desenvolvimento'):
            p=construir(caso['estado'],caso['evento'],execucao_id='schema_'+caso['caso_id'])
            for no,selecao in p.plano.items():
                c=montar_contexto(caso['estado'],caso['evento'],execucao_id=p.execucao_id,no_id=no,revisao=1,responsabilidades_operacionais=p.responsabilidades_operacionais,**selecao)
                s=gerar(c);Draft202012Validator.check_schema(s);f=formato(c)
                self.assertEqual(f['type'],'json_schema');self.assertIs(f['strict'],True)
                size=len(json.dumps(s,ensure_ascii=False).encode());max_bytes=max(max_bytes,size);total+=1
                def visitar(x):
                    if isinstance(x,dict):
                        self.assertFalse(set(x)&{'allOf','not','if','then','else','dependentRequired','dependentSchemas','uniqueItems'})
                        if x.get('type')=='object':
                            self.assertIs(x['additionalProperties'],False)
                            self.assertEqual(set(x['properties']),set(x['required']))
                        for y in x.values():visitar(y)
                    elif isinstance(x,list):
                        for y in x:visitar(y)
                visitar(s)
        self.assertEqual(total,112)
        self.assertLess(max_bytes,50000)

if __name__=='__main__':unittest.main()
