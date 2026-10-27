"""Somente MOCKS: números arbitrários testam forma, não verdade de cenário."""
from copy import deepcopy
import hashlib,json,sqlite3,unittest
from pathlib import Path
from interpretacao_no.contratos import montar_contexto,validar,hash_json,OPS
from interpretacao_no.adaptadores import LLM,RespostaTransporte
from piloto_real import MODELO,CONFIG
from formato_local_v04 import LocalV04,ResponsesV04,preparar_requisicao
from formato_local_v04.contrato import VERSAO,compilar,QUANTITATIVAS,CONFIRMACOES,SISTEMA

ROOT=Path(__file__).resolve().parents[2]
DIAG=ROOT/'outputs/etapa9_diagnostico_180s_20261026'
REF=dict(fonte_id='f_evento_mock',localizador='L1')


def k(v):return dict(estado='exato',valor=v,direcao='desconhecida',evidencias=[REF],lacunas=[],motivo=None)


def contextos(predicados=None):
    fonte=dict(id=REF['fonte_id'],documento_id='d_mock',versao='1',localizador='L1',trecho='Fonte sintética para validar formato; não define verdade numérica de cenário.')
    e=dict(projeto_id='q_mock',versao='v_mock',fontes=[fonte],entidades=[dict(id=n,tipo=t,nome=n,atributos={'disponibilidade':dict(tipo='inteiro',unidade='dia_corrido',conhecimento=k(7))}if n=='n_comp_mock'else{})for n,t in [('n_comp_mock','componente'),('n_atividade_mock','atividade')]],
        atividades=[dict(id='n_atividade_mock',entidade_id='n_atividade_mock',duracao=k(11),restricoes_liberacao=[dict(id='r_mock',atividade_id='n_atividade_mock',tipo='nao_antes',valor=k(3),fonte_refs=[REF])])],
        relacoes=[dict(id='l_mock',origem_id='n_atividade_mock',destino_id='n_comp_mock',tipo='requer',fonte_refs=[REF])],
        regras_transferencia=[dict(id='t_mock',relacao_id='l_mock',operacao='disponibilidade_para_restricao',origem_atributo='disponibilidade',restricao_destino_id='r_transfer_mock',fonte_refs=[REF])],
        regras_locais=[dict(id='u_mock',no_id='n_atividade_mock',clausula=REF,fonte_refs=[REF],condicao_textual='Condição sintética a interpretar; nenhum aceite vem preenchido.',operacoes_permitidas=list(CONFIRMACOES),atributos_alvo=['duracao','readequacao'])],
        parcelas_base=[dict(id=p,escopo_id='q_mock',descricao=p,valor_centavos=100,moeda='BRL',fonte_refs=[REF])for p in ['p_base_mock','p_temporal_mock']],
        regras_custo=[dict(id='c_mock',parcela_id='p_temporal_mock',taxa_centavos_dia=8,unidade_taxa='BRL_centavo/dia_corrido',intervalo=dict(inicio_ref='D0',fim_ref=dict(atividade_id='n_atividade_mock',atributo='fim')),base_contratada_dias=2,politica_reducao='sem_credito',condicao='Contrato sintético para formato',fonte_refs=[REF])])
    ev=dict(evento_id='e_mock',projeto_id='q_mock',versao_projeto='v_mock',instante_observacao=0,relato=fonte['trecho'],origem=dict(autor='MOCK',documento_id='d_mock',data_registro='D0'),escopo='Teste de formato',lacunas=[],evidencias=[fonte])
    comum=dict(execucao_id='exec_mock',revisao=2,fonte_ids=[REF['fonte_id']],relacao_ids=['l_mock'])
    x=montar_contexto(e,ev,no_id='n_comp_mock',regra_ids=['t_mock'],**comum)
    a=montar_contexto(e,ev,no_id='n_atividade_mock',regra_ids=['u_mock','c_mock'],parcela_ids=['p_base_mock'],obrigacoes=['p_nova_mock'],predicados=['procedimento segue válido']if predicados is None else predicados,**comum)
    return x,a


def base(c,ps=()):
    q=dict(estado='indeterminado',valor=None,direcao='desconhecida',evidencias=[],lacunas=['Magnitude local sintética não fornecida'],motivo=None)
    a={n:deepcopy(c[n])for n in ('execucao_id','evento_id','no_id','revisao','contexto_hash','predecessores_versoes')}
    a.update(schema_version='1.0-proposta',analise_id='analise_mock',avaliacao=dict(prazo=q,custo=deepcopy(q)),propostas=list(ps),justificativa='Exemplo sintético de formato,sem alegar suporte real',lacunas=[])
    if any(p['operacao']=='confirmar_ausencia_parcela_adicional'for p in ps):a['avaliacao']['custo']=dict(estado='exato',valor=0,direcao='zero',evidencias=[REF],lacunas=[],motivo=None)
    return a


def prop(c,op):
    perm=next(p for p in c['permissoes']if p['operacao']==op)
    v=k(19)
    if op=='registrar_lacuna_custo':v=dict(estado='indeterminado',valor=None,direcao='desconhecida',evidencias=[REF],lacunas=['Preço sintético não informado'],motivo=None)
    if op=='confirmar_manutencao_atributo':v=11
    if op=='confirmar_ausencia_parcela_adicional':v=0
    if op=='aplicar_regra_catalogada':v=dict(taxa_centavos_dia=None,base_contratada_dias=12,politica_reducao='recalculavel_com_credito')
    return dict(id=c['no_id']+':r2:p1',**perm,valor=v,evidencias=[REF],relacao_refs=[],regra_refs=['u_mock']if op in CONFIRMACOES else['c_mock']if op=='aplicar_regra_catalogada'else[],
        condicoes=[dict(predicado=c['predicados'][0],estado='confirmada',evidencias=[REF])]if op in CONFIRMACOES and c['predicados']else[],
        origens_causais=[dict(evento_id=c['evento_id'],fato_ref=REF,efeito_id=hash_json([c['evento_id'],perm['alvo_id']]))],no_id=c['no_id'])


class TransporteMock:
    versao_formato_local=VERSAO
    def __init__(self,conteudo):self.texto=conteudo;self.requests=[]
    def __call__(self,req):self.requests.append(deepcopy(req));return RespostaTransporte(self.texto,modelo=MODELO)


class WalletMock:
    def __init__(self):
        self.manifesto_formato=dict(versao_formato_local=VERSAO,slots=['slot_formato_v04'])
        self.plano={'slots':[dict(execucao_id='slot_historico')]};self.reservas=[];self.passos=[]
    def reservar(self,slot,h):self.reservas.append((slot,h));return 1
    def iniciar_contagem(self,i):self.passos.append('contagem')
    def contar(self,i,n):self.passos.append(('contado',n))
    def enviar(self,i):self.passos.append('envio')
    def concluir(self,*x):self.passos.append('conciliado')
    def desconhecido(self,*x):self.passos.append('desconhecido')
    def parar(self,*x):self.passos.append('parada')
    def nao_enviado(self,*x):self.passos.append('nao_enviado')


class HTTPMock:
    def __init__(self,conteudo):self.texto=conteudo;self.calls=[]
    def post(self,path,payload,timeout):
        self.calls.append((path,deepcopy(payload),timeout))
        if path:return dict(object='response.input_tokens',input_tokens=100)
        return dict(model=MODELO,status='completed',id='mock',output=[dict(type='message',content=[dict(type='output_text',text=self.texto)])],usage=dict(input_tokens=100,output_tokens=50,total_tokens=150,input_tokens_details=dict(cached_tokens=0,cache_write_tokens=0),output_tokens_details=dict(reasoning_tokens=10)))


def rodar(c,a,real_path=False):
    txt=json.dumps(a,ensure_ascii=False);wallet=WalletMock();http=HTTPMock(txt)
    tr=ResponsesV04(wallet,'slot_formato_v04',http,timeout_s=30)if real_path else TransporteMock(txt)
    r=LocalV04(tr,modelo=MODELO,configuracao=CONFIG,timeout_s=30).analisar(c)
    return r,tr,wallet,http


class Formato(unittest.TestCase):
    def test_nove_operacoes_sinteticas_validas_mesmo_parser(self):
        x,c=contextos();cobertas=set()
        for op in OPS:
            ctx=x if op=='substituir_disponibilidade'else c
            with self.subTest(op=op):
                a=base(ctx,[prop(ctx,op)]);validar(a,ctx)
                r,_,_,_=rodar(ctx,a);self.assertEqual(r['execucao']['estado'],'ok',r['execucao'])
                self.assertEqual(r['propostas'],a['propostas']);self.assertEqual(r['execucao']['versao_formato_local'],VERSAO)
                cobertas.add(op)
        self.assertEqual(cobertas,set(OPS))
    def test_catalogo_vazio_quantitativo_valido_sem_condicoes(self):
        _,c=contextos([]);a=base(c,[prop(c,'substituir_duracao')]);r,t,_,_=rodar(c,a)
        self.assertEqual(r['execucao']['estado'],'ok')
        data=json.loads(t.requests[0]['mensagens'][1]['conteudo'])
        self.assertEqual(data['contexto']['predicados'],[])
        self.assertEqual(data['contrato_resposta']['condicoes']['lista_exigida_quando_catalogo_vazio'],[])
        self.assertIn('SE contexto.predicados=[] USE condicoes=[]',t.requests[0]['mensagens'][0]['conteudo'])
    def test_predicado_textual_no_catalogo_aceito_e_fora_rejeitado(self):
        _,c=contextos();a=base(c,[prop(c,'confirmar_manutencao_atributo')])
        self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'ok')
        a['propostas'][0]['condicoes'][0]['predicado']='texto não cadastrado'
        self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
    def test_escalar_quantitativo_e_objeto_em_confirmacao_rejeitados(self):
        x,c=contextos()
        for op in QUANTITATIVAS:
            ctx=x if op=='substituir_disponibilidade'else c;a=base(ctx,[prop(ctx,op)]);a['propostas'][0]['valor']=19
            with self.subTest(op=op):self.assertEqual(rodar(ctx,a)[0]['execucao']['estado'],'erro')
        for op in CONFIRMACOES:
            a=base(c,[prop(c,op)]);a['propostas'][0]['valor']=k(0)
            with self.subTest(op=op):self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
    def test_aditivo_nulo_taxa_permitida_objeto_nao_vazio_sem_extras(self):
        _,c=contextos()
        for v,ok in [({'taxa_centavos_dia':None},True),({'base_contratada_dias':0},True),({'politica_reducao':'sem_credito'},True),({},False),(None,False),(5,False),({'multa':3},False),({'taxa_centavos_dia':True},False),({'base_contratada_dias':-1},False),({'politica_reducao':'automatico'},False)]:
            a=base(c,[prop(c,'aplicar_regra_catalogada')]);a['propostas'][0]['valor']=v
            with self.subTest(v=v):self.assertEqual(rodar(c,a)[0]['execucao']['estado']=='ok',ok)
    def test_lacuna_nao_exata_e_inaplicavel_apenas_avaliacao(self):
        _,c=contextos();a=base(c,[prop(c,'registrar_lacuna_custo')]);self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'ok')
        a['propostas'][0]['valor']=k(5);self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
        a=base(c,[prop(c,'substituir_duracao')]);a['avaliacao']['prazo']=dict(estado='inaplicavel',valor=None,direcao='desconhecida',evidencias=[],lacunas=[],motivo='Teste de estrutura')
        self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'ok')
        a['propostas'][0]['valor']=deepcopy(a['avaliacao']['prazo']);self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
    def test_confirmacao_exige_regra_condicao_confirmada_e_zero_local(self):
        _,c=contextos()
        for modo in ('sem_regra','sem_condicao','nao_confirmada','zero_sem_avaliacao','duracao_divergente'):
            op='confirmar_manutencao_atributo'if modo=='duracao_divergente'else'confirmar_ausencia_parcela_adicional'
            a=base(c,[prop(c,op)]);p=a['propostas'][0]
            if modo=='sem_regra':p['regra_refs']=[]
            if modo=='sem_condicao':p['condicoes']=[]
            if modo=='nao_confirmada':p['condicoes'][0]['estado']='nao_confirmada'
            if modo=='zero_sem_avaliacao':a['avaliacao']['custo']=base(c)['avaliacao']['custo']
            if modo=='duracao_divergente':p['valor']=12
            with self.subTest(modo=modo):self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
    def test_identidade_hash_efeito_ref_e_tipo_rigorosos(self):
        _,c=contextos()
        for modo in ('identidade','revisao_bool','hash','efeito','evidencia','unidade','campo_extra','escrita_duplicada','valor_bool','valor_negativo','valor_com_unidade','direcao_absoluta_errada'):
            a=base(c,[prop(c,'substituir_duracao')]);p=a['propostas'][0]
            if modo=='identidade':a['evento_id']='outro'
            if modo=='revisao_bool':a['revisao']=True
            if modo=='hash':a['contexto_hash']='outro'
            if modo=='efeito':p['origens_causais'][0]['efeito_id']='inventado'
            if modo=='evidencia':p['evidencias']=[dict(fonte_id='invisivel',localizador='L1')]
            if modo=='unidade':p['unidade']='BRL_centavo'
            if modo=='campo_extra':a['confianca']=1
            if modo=='escrita_duplicada':a['propostas'].append({**deepcopy(p),'id':'outra'})
            if modo=='valor_bool':p['valor']['valor']=True
            if modo=='valor_negativo':p['valor']['valor']=-1
            if modo=='valor_com_unidade':p['valor']['unidade']='dia_corrido'
            if modo=='direcao_absoluta_errada':p['valor']['direcao']='aumento'
            with self.subTest(modo=modo):self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
    def test_payload_caminho_http_e_contagem_campos_coerentes(self):
        _,c=contextos([]);a=base(c,[prop(c,'substituir_duracao')]);r,_,w,h=rodar(c,a,True)
        self.assertEqual(r['execucao']['estado'],'ok')
        self.assertEqual([x[0]for x in h.calls],['/input_tokens',''])
        count,payload=h.calls[0][1],h.calls[1][1]
        for k_ in ('model','input','text','reasoning'):self.assertEqual(count[k_],payload[k_])
        self.assertEqual(payload['text'],{'format':{'type':'json_object'}})
        self.assertIn(SISTEMA,payload['input'][0]['content'])
        self.assertNotIn('efeito_id é SHA256',payload['input'][0]['content'])
        dados=json.loads(payload['input'][1]['content']);self.assertEqual(dados['contexto'],c)
        contrato=dados['contrato_resposta'];self.assertEqual(contrato['versao_formato'],VERSAO)
        self.assertEqual(contrato['identidades_copiar'],{k_:c[k_]for k_ in ('execucao_id','evento_id','no_id','revisao','contexto_hash','predecessores_versoes')})
        self.assertEqual(payload['max_output_tokens'],25000);self.assertEqual(payload['reasoning'],{'effort':'high'})
        self.assertEqual(payload['prompt_cache_options'],{'ttl':'30m'});self.assertEqual(h.calls[0][2]<=30,True)
        self.assertEqual(len(w.reservas),1)
        self.assertEqual(r['execucao']['versao_formato_local'],VERSAO)
        self.assertEqual(r['execucao']['config_hash'],hash_json(CONFIG))
        self.assertEqual(w.reservas[0][1],hash_json(payload))
        reqs=[]
        class Captura:
            versao_formato_local=VERSAO
            def __call__(self,req):
                reqs.append(req);return RespostaTransporte(json.dumps(a))
        rr=LocalV04(Captura(),modelo=MODELO,configuracao=CONFIG,timeout_s=30).analisar(c)
        self.assertEqual(rr['execucao']['requisicao_adaptador_hash'],hash_json(reqs[0]))
        self.assertIn('formato_local_v04',type(LocalV04(Captura(),modelo=MODELO,configuracao=CONFIG,timeout_s=30)).__module__)
    def test_recusa_transporte_carteira_e_slot_antigos(self):
        class Antigo:pass
        with self.assertRaises(ValueError):LocalV04(Antigo(),modelo=MODELO,configuracao=CONFIG,timeout_s=30)
        with self.assertRaises(ValueError):ResponsesV04(Antigo(),'s',HTTPMock('{}'),timeout_s=30)
        with self.assertRaises(ValueError):ResponsesV04(WalletMock(),'slot_historico',HTTPMock('{}'),timeout_s=30)
    def test_exemplos_e_contrato_imutaveis_sem_gabarito(self):
        x,c=contextos();antes=deepcopy(c);a=base(c,[prop(c,'substituir_duracao')]);r,t,_,_=rodar(c,a)
        self.assertEqual(c,antes);data=json.loads(t.requests[0]['mensagens'][1]['conteudo'])
        for proibido in ('gabarito','referencia_esperada','delta_final','familia_id'):self.assertNotIn(proibido,json.dumps(data))
        self.assertEqual(r['propostas'],a['propostas'])
        descr=data['contrato_resposta'];tipos={p['operacao']:p['valor_tipo']for p in descr['operacoes_permitidas']}
        self.assertEqual(tipos['aplicar_regra_catalogada'],'AditivoContratual');self.assertEqual(tipos['confirmar_manutencao_atributo'],'inteiro_escalar');self.assertEqual(tipos['substituir_duracao'],'ConhecimentoAbsoluto')
    def test_resposta_real_rejeitada_continua_rejeitada_sem_reparo(self):
        real=json.loads((DIAG/'execucao/etapa9-diagnostico-180s-20261026-v1-H-local.json').read_text());b=real['response_original'];texto=''.join(x['text']for i in b['output']if i['type']=='message'for x in i['content']if x['type']=='output_text')
        db=sqlite3.connect('file:'+str((DIAG/'snapshot_pos_diagnostico/ledger.sqlite').resolve())+'?mode=ro',uri=True)
        original=json.loads(db.execute('SELECT registro FROM chamadas WHERE id=4').fetchone()[0]);db.close();c=json.loads(original['payload']['input'][1]['content'])['contexto']
        bruto_hash=hashlib.sha256(texto.encode()).hexdigest();meta=json.loads((DIAG/'revalidacao_offline_local.json').read_text())
        self.assertEqual(bruto_hash,meta['bruto_original_texto_sha256'])
        mock=TransporteMock(texto);r=LocalV04(mock,modelo=MODELO,configuracao=CONFIG,timeout_s=30).analisar(c)
        self.assertEqual(r['execucao']['estado'],'erro');self.assertEqual(r['execucao']['erros'][0]['mensagem'],'Condição fora de catálogo')
        self.assertEqual(r['execucao']['tentativas'][0]['resposta_bruta'],texto)
        self.assertEqual(len(mock.requests),1)




class FronteirasProximas(unittest.TestCase):
    def test_confirma_catalogo_vazio_ou_zero_sem_evidencia_nao_passa(self):
        _,c=contextos([]);a=base(c,[prop(c,'confirmar_ausencia_parcela_adicional')])
        self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
        _,c=contextos();a=base(c,[prop(c,'confirmar_ausencia_parcela_adicional')]);a['avaliacao']['custo']['evidencias']=[]
        self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
    def test_estados_conhecimento_e_sinais_sem_imputacao(self):
        _,c=contextos();a=base(c,[prop(c,'substituir_duracao')])
        a['propostas'][0]['valor']=dict(estado='direcao',valor=None,direcao='aumento',evidencias=[REF],lacunas=['Magnitude desconhecida'],motivo=None)
        a['avaliacao']['prazo']=dict(estado='exato',valor=-3,direcao='reducao',evidencias=[REF],lacunas=[],motivo=None)
        self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'ok')
        a['avaliacao']['prazo']['direcao']='aumento';self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
        a['avaliacao']['prazo']['direcao']='reducao';a['propostas'][0]['valor']['lacunas']=[]
        self.assertEqual(rodar(c,a)[0]['execucao']['estado'],'erro')
    def test_pedido_sem_versao_e_slot_historico_explicitamente_listado_bloqueados(self):
        w=WalletMock();w.manifesto_formato['slots'].append('slot_historico')
        with self.assertRaises(ValueError):ResponsesV04(w,'slot_historico',HTTPMock('{}'),timeout_s=30)
        w=WalletMock();h=HTTPMock('{}');t=ResponsesV04(w,'slot_formato_v04',h,timeout_s=30)
        _,c=contextos();r=LLM(t,modelo=MODELO,configuracao=CONFIG,timeout_s=30).analisar(c)
        self.assertEqual(r['execucao']['estado'],'erro');self.assertFalse(h.calls);self.assertFalse(w.reservas)

class CacheDirecionado(unittest.TestCase):
    def test_tipo_v04_separa_chave_legada_e_reutiliza_so_a_propria(self):
        from orquestracao import avaliar
        from orquestracao.simulacao import politica_prescrita
        e=json.loads((ROOT/'data/desenvolvimento/projeto_minimo_grafo_v1/estado_projeto.json').read_text())
        f=json.loads((ROOT/'data/desenvolvimento/orquestracao_simulada_v1/k_09c2.json').read_text())
        p=politica_prescrita(f);p.resolver=lambda c,a:True
        class MockDinamico:
            versao_formato_local=VERSAO
            def __init__(self):self.requests=[]
            def __call__(self,req):
                self.requests.append(deepcopy(req))
                return RespostaTransporte(json.dumps(base(json.loads(req['mensagens'][1]['conteudo'])['contexto'])))
        antigo_mock=MockDinamico();novo_mock=MockDinamico()
        antigo=LLM(antigo_mock,modelo=MODELO,configuracao=CONFIG,timeout_s=30)
        novo=LocalV04(novo_mock,modelo=MODELO,configuracao=CONFIG,timeout_s=30)
        a=avaliar(e,f['evento'],antigo,p);chaves_a=set(p.cache);vinculo_a=p._vinculo
        self.assertTrue(chaves_a);n=len(antigo_mock.requests)
        aa=avaliar(e,f['evento'],antigo,p)
        self.assertEqual(len(antigo_mock.requests),n)
        self.assertTrue(all(t['processamento']=='reuso_cache'for t in aa['rastro_orquestracao']if 'analise'in t))
        b=avaliar(e,f['evento'],novo,p);chaves_b=set(p.cache)-chaves_a
        self.assertTrue(chaves_b);self.assertTrue(novo_mock.requests)
        self.assertNotEqual(vinculo_a,p._vinculo)
        self.assertTrue(all(t['processamento']=='interpretado'for t in b['rastro_orquestracao']if 'analise'in t))
        ca=next(t['contexto']for t in a['rastro_orquestracao']if 'analise'in t);cb=next(t['contexto']for t in b['rastro_orquestracao']if 'analise'in t)
        limpar=lambda c:{k:v for k,v in c.items()if k not in ('contrato_execucao','contexto_hash','revisao')}
        self.assertEqual(limpar(ca),limpar(cb))
        self.assertNotEqual(ca['contexto_hash'],cb['contexto_hash'])
        for campo in ('modelo','configuracao','timeout_s','repetir'):
            self.assertEqual(ca['contrato_execucao']['configuracao'][campo],cb['contrato_execucao']['configuracao'][campo])
        n=len(novo_mock.requests);bb=avaliar(e,f['evento'],novo,p)
        self.assertEqual(len(novo_mock.requests),n)
        self.assertTrue(all(t['processamento']=='reuso_cache'for t in bb['rastro_orquestracao']if 'analise'in t))
        evidencia=dict(rotulo='Contraprova offline com respostas mock, sem rede',assinatura_legada=ca['contrato_execucao'],assinatura_v04=cb['contrato_execucao'],contexto_hash_legado=ca['contexto_hash'],contexto_hash_v04=cb['contexto_hash'],chaves_legadas=sorted(chaves_a),chaves_v04=sorted(chaves_b),reuso_proprio_confirmado=True,reuso_cruzado=False)
        (ROOT/'outputs/etapa9_formato_v04_20261026/cache_contraprova.json').write_text(json.dumps(evidencia,ensure_ascii=False,indent=2))

if __name__=='__main__':unittest.main()
