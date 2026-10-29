#!/usr/bin/env python3
"""Cálculo cego independente: somente biblioteca padrão e seis JSON de entrada.

Não importa motor, estado normalizado, testes, previsões ou referências autorais.
Relações/fórmulas abaixo foram transcritas das fontes literais pelo revisor.
Execução produz derivacoes.json e NOTAS.md somente nesta pasta.
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / 'pacote_cego_desenvolvimento'
PACKAGES = ('projeto_minimo_v1', 'ampliacao_v1')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exact(value, unit):
    assert type(value) is int
    return {'estado': 'exato', 'valor': value, 'unidade': unit,
            'limite_inferior': value, 'limite_superior': value}


def unknown(unit, low=None, high=None, direction=None, note=None):
    return {'estado': 'direcao' if direction in ('aumento', 'reducao') else 'indeterminado',
            'valor': None, 'unidade': unit, 'limite_inferior': low,
            'limite_superior': high, 'direcao': direction, 'nota': note}


def delta(value, baseline, unit):
    result = exact(value - baseline, unit)
    result['direcao'] = 'aumento' if value > baseline else 'reducao' if value < baseline else 'neutro'
    return result


def known_result(finish, cost, base_finish, base_cost):
    return {'fim_dia': exact(finish, 'dia_corrido'),
            'custo_centavos': exact(cost, 'BRL_centavo'),
            'delta_prazo_dias': delta(finish, base_finish, 'dia_corrido'),
            'delta_custo_centavos': delta(cost, base_cost, 'BRL_centavo')}


def iris(availability=2, prepare=5):
    # f_aab5d508ec: requer cartucho; f_e847b102df: FS0 completo.
    r0 = max(0, availability)
    r1 = r0 + 1
    p1 = prepare
    m0 = max(r1, p1)
    m1 = m0 + 3
    t1 = m1 + 2
    return t1, {'n_42be': [r0, r1], 'n_915c': [0, p1],
                'n_a367': [m0, m1], 'n_08df': [m1, t1], 'n_e659': [t1, t1]}


def iris_cost(finish, direct=0, credit=0, coverage=10):
    # f_8ca6cc3cb4, f_77c5d27cd0, f_aa2f56bbb7.
    fixed = sum((100000, 50000, 150000, 100000, 100000))
    extension = max(0, finish - coverage) * 10000
    return fixed + direct - credit + extension, extension


def nacar(prepare=2, machining=4, dossier=3, opening=8):
    # f_7d2f: duas convergências e marco final. D8 é restrição, não duração.
    integrate0 = max(prepare, machining)
    integrate1 = integrate0 + 3
    test1 = integrate1 + 2
    dossier0 = max(opening, integrate1)
    dossier1 = dossier0 + dossier
    inspect0 = max(test1, dossier1)
    finish = inspect0 + 1
    return finish, {'n_7b42': [0, prepare], 'n_c196': [0, machining],
                    'n_05ed': [integrate0, integrate1], 'n_f8a3': [integrate1, test1],
                    'n_21dc': [dossier0, dossier1], 'n_683f': [inspect0, finish],
                    'n_ae50': [finish, finish]}


def nacar_cost(finish, direct=0, credit_authorized=False):
    # f_b915: seis parcelas = 100000; f_493d: apoio base já contém 15000 de extensão.
    support = 50000 + max(0, finish - 10) * 7500
    if not credit_authorized:
        support = max(65000, support)
    return 100000 + support + direct, support


loaded = {}
manifest = []
sources = {}
for package in PACKAGES:
    loaded[package] = {}
    for name in ('base', 'cenarios', 'fontes'):
        path = INPUT / package / 'inputs' / (name + '.json')
        raw = path.read_bytes()
        loaded[package][name] = json.loads(raw)
        manifest.append({'arquivo': str(path), 'sha256': sha(raw), 'bytes': len(raw)})
    for source in loaded[package]['fontes']['fontes']:
        sources[source['id']] = dict(source, pacote=package,
                                      sha256_trecho_utf8=sha(source['trecho'].encode()))

# Constantes são derivadas acima, sem ler linha_base_declarada no cálculo.
ibf, ibschedule = iris()
ibc, _ = iris_cost(ibf)
nbf, nbschedule = nacar()
nbc, _ = nacar_cost(nbf)

base_iris_refs = ['f_04054cfee1', 'f_11ebeff90b', 'f_359bae5d73', 'f_a2c707b9d7',
                  'f_d96520b3de', 'f_8ca6cc3cb4', 'f_e63d1b2e94', 'f_259da44f35',
                  'f_b1694cb6da', 'f_77c5d27cd0', 'f_aa2f56bbb7',
                  'f_e3f0ade479', 'f_52a04b86dd', 'f_aab5d508ec', 'f_e847b102df', 'f_d34efaf231']
base_nacar_refs = ['f_a781', 'f_36c2', 'f_b915', 'f_493d', 'f_7d2f']

def b_unknown(note, cost_floor=None, cost_exact=None, base_cost=500000,
              finish_exact=None, base_finish=10):
    b = {'fim_dia': unknown('dia_corrido'),
         'delta_prazo_dias': unknown('dia_corrido'),
         'custo_centavos': unknown('BRL_centavo'),
         'delta_custo_centavos': unknown('BRL_centavo'), 'justificativa': note}
    if cost_floor is not None:
        b['custo_centavos'] = unknown('BRL_centavo', cost_floor,
                                    direction='aumento' if cost_floor > base_cost else None)
        b['delta_custo_centavos'] = unknown('BRL_centavo', cost_floor-base_cost,
                                          direction='aumento' if cost_floor > base_cost else None)
    if cost_exact is not None:
        b['custo_centavos'] = exact(cost_exact, 'BRL_centavo')
        b['delta_custo_centavos'] = delta(cost_exact, base_cost, 'BRL_centavo')
    if finish_exact is not None:
        b['fim_dia'] = exact(finish_exact, 'dia_corrido')
        b['delta_prazo_dias'] = delta(finish_exact, base_finish, 'dia_corrido')
    return b


results = []

def append_case(case_id, th, b, schedule, expression, details=None, caveats=None):
    found = [(pkg, case) for pkg in PACKAGES for case in loaded[pkg]['cenarios']['casos']
             if case['caso_id'] == case_id]
    assert len(found) == 1
    pkg, case = found[0]
    refs = (base_iris_refs if pkg == PACKAGES[0] else base_nacar_refs) + case['evidencia_ids']
    bdocs = case['documentos_comuns_vigentes'] + [case['documento_evento_vigente']]
    brefs = [ref for ref in refs if sources[ref]['documento_id'] in bdocs]
    # A referência fixa é conhecida em B; ela não determina o novo cronograma.
    brefs += ['f_bbb437fd83'] if pkg == PACKAGES[0] else []
    results.append({'caso_id': case_id, 'evento_id': case['evento_id'], 'pacote': pkg,
                    'baseline': {'fim_dia': ibf if pkg == PACKAGES[0] else nbf,
                                 'custo_centavos': ibc if pkg == PACKAGES[0] else nbc},
                    'aviso_literal': case['relato'], 'fontes_refs_TH': refs,
                    'fontes_refs_B': brefs, 'documentos_permitidos_B': bdocs,
                    'T': th, 'H': json.loads(json.dumps(th)),
                    'T_H_mesma_informacao': True, 'B': b,
                    'cronograma_TH_intervalos': schedule, 'derivacao': expression,
                    'detalhes_custo': details or {}, 'ambiguidades': caveats or []})


iris_configs = [
    ('k_b731', 4, 5, 0, 0, 10), ('k_09c2', 6, 5, 20000, 0, 10),
    ('k_e168', 2, 5, 30000, 0, 10), ('k_547a', 6, 5, 0, 0, 12),
    ('k_a92f', 3, 5, 15000, 0, 10), ('k_f04b', 2, 4, 0, 10000, 10)]
for cid, avail, prep, direct, credit, cover in iris_configs:
    f, schedule = iris(avail, prep)
    cost, extension = iris_cost(f, direct, credit, cover)
    th = known_result(f, cost, ibf, ibc)
    note = ('Sem d_aa83 não se conhece requisito cartucho→recebimento nem precedências até o marco; '
            'não se pode usar o cronograma TH em B. Disponibilidade não é duração.')
    if cid == 'k_e168':
        b = dict(known_result(10, 530000, ibf, ibc), justificativa=
                 'Disponibilidade D2 preservada e aceite mantém procedimento padrão; nenhum atributo temporal muda. Taxa única +30000.')
    elif cid == 'k_f04b':
        b = b_unknown('Encurtamento de uma atividade não revela sua criticidade. Sob a premissa geral de precedências monotônicas, '
                      'não atrasa o projeto; como a base termina dentro da cobertura, sem crédito do apoio e crédito explícito -10000, '
                      'custo=490000. Essa conclusão de custo depende dessa premissa, não da rede oculta.', cost_exact=490000)
        b['premissa_adicional'] = 'Precedências temporais monotônicas: encurtar uma duração não posterga o término.'
        b['conclusao_sem_essa_premissa'] = 'Prazo e custo totais indeterminados; crédito direto -10000 é exato.'
    else:
        b = b_unknown(note, cost_floor=500000+direct)
    append_case(cid, th, b, schedule,
                f'F=max({avail}+1,{prep})+3+2={f}; C=500000+{direct}-{credit}+10000*max(0,{f}-{cover})={cost}',
                {'base':500000, 'adicional_direto':direct, 'credito':credit, 'extensao':extension},
                ['Usar Q selecionado em D3; D9 habitual cancelado não limita o projeto.'] if cid=='k_a92f' else [])

# Preço de extensão desconhecido, domínio não negativo explícito.
f, schedule = iris(6)
th = {'fim_dia': exact(f,'dia_corrido'), 'delta_prazo_dias': delta(f,ibf,'dia_corrido'),
      'custo_centavos': unknown('BRL_centavo',520000,direction='aumento',note='X inteiro >=0, sem teto; não usar taxa revogada.'),
      'delta_custo_centavos': unknown('BRL_centavo',20000,direction='aumento')}
append_case('k_8c65', th, b_unknown('A taxa antiga foi expressamente revogada. Mesmo sem conhecer término, '
            'fixos 500000 + taxa 20000 e extensão não negativa provam aumento mínimo de 20000.',cost_floor=520000),
            schedule, 'F=max(6+1,5)+3+2=12; C=520000+X; ΔC=20000+X; X∈inteiros, X>=0.',
            {'subtotal_certo':520000, 'extensao':'X desconhecido, >=0, sem limite superior'})

# Aceite pendente: NÃO manter a duração padrão nem usar custo técnico zero.
th = {'fim_dia': unknown('dia_corrido', note='Aceite, espera técnica e duração da montagem não definidos.'),
      'delta_prazo_dias': unknown('dia_corrido'),
      'custo_centavos': unknown('BRL_centavo', note='Preço técnico sem domínio explícito; subtotal conhecido não é total.'),
      'delta_custo_centavos': unknown('BRL_centavo'),
      'conclusao_condicional': {'premissa':'Duração/espera técnica >=0 e custo técnico adicional >=0, sem créditos implícitos.',
          'fim_limite_inferior_conservador':9, 'delta_prazo_limite_inferior':-1,
          'custo_limite_inferior':520000, 'delta_custo_limite_inferior':20000,
          'direcao_custo':'aumento', 'limites_sao_resultados_exatos':False,
          'atingibilidade_dos_limites':'Não demonstrada: domínio técnico não foi definido nas fontes.'}}
append_case('k_23d8',th,b_unknown('Comuns já impõem aceite específico; laudo enviado não equivale a laudo aceito. '
             'Faltam também as relações. Subtotal contratual+taxa=520000; total depende de preço técnico indefinido.'),
            {'n_42be':[6,7], 'n_915c':[0,5], 'n_a367':None,'n_08df':None,'n_e659':None},
            'Recebimento termina D7. Seja S>=7 o futuro início e D a duração técnica ainda não definida: F=S+D+2. '
            'C=520000+10000*max(0,F-10)+R, onde R é preço técnico não definido; não atribuir D=3 nem R=0.',
            {'subtotal_certo':520000,'taxa_direta':20000,'preco_tecnico':'não definido'},
            ['O termo custo e a proibição de crédito implícito favorecem R>=0, mas essa faixa não é expressamente declarada '
             'como no caso k_8c65. Leitura usual: direção de custo aumento; leitura literal conservadora: total indeterminado.',
             'Limite F>=9 é estrutural sob durações não negativas; não significa que concluir em D9 seja tecnicamente possível.',
             'Não há prazo máximo nem garantia de futura aceitação/conclusão.'])

nacar_configs = [
    ('k_6d82',2,4,3,10,0,False), ('k_0ca7',6,7,3,8,0,False),
    ('k_98f3',2,4,1,8,0,False), ('k_42a9',2,4,1,8,0,True),
    ('k_b5e1',2,4,3,8,12345,False), ('k_a064',2,4,3,8,0,False)]
for cid,p,u,d,o,direct,credit in nacar_configs:
    f,schedule=nacar(p,u,d,o)
    cost,support=nacar_cost(f,direct,credit)
    th=known_result(f,cost,nbf,nbc)
    note='Sem d_a70f não há rede documentada que transfira os efeitos das atividades ao marco.'
    if cid in ('k_b5e1','k_a064'):
        b=dict(known_result(12,165000+direct,nbf,nbc),justificativa=
               'Aviso preserva todos os atributos temporais; referência fixa continua. '+
               ('p_0f2b é única: +12345 uma vez.' if direct else 'Correção nominal não altera quantitativos.'))
    elif cid=='k_98f3':
        b=b_unknown('Encurtamento do dossiê pode ou não antecipar o marco. Sob precedências monotônicas não há atraso; '
                    'apoio sem crédito preserva 65000, demais fixos 100000, logo custo 165000.',
                    cost_exact=165000,base_cost=nbc,base_finish=nbf)
        b['premissa_adicional']='Precedências temporais monotônicas: redução de duração não posterga o término.'
        b['conclusao_sem_essa_premissa']='Prazo e custo totais indeterminados.'
    elif cid=='k_42a9':
        b=b_unknown(note+' Reembolso entre 0 e 15000 sob monotonicidade; não se sabe a extensão efetivamente usada.',
                    base_cost=nbc,base_finish=nbf)
        b['limites_condicionais_monotonicidade']={'custo_min':150000,'custo_max':165000,'delta_custo_min':-15000,'delta_custo_max':0}
    else:
        b=b_unknown(note,cost_floor=165000,base_cost=nbc,base_finish=nbf)
        if cid=='k_6d82':
            b['fato_local_exato']='Dossiê não termina antes de D13. Se toda entrega obrigatória deve anteceder o marco, F>=13 e ΔF>=1; essa convergência não está explicitada em B.'
            b['limites_condicionais_convergencia']={'fim_min':13,'delta_prazo_min':1,'custo_min':172500,'delta_custo_min':7500}
    append_case(cid,th,b,schedule,
       f'I=max({p},{u})+3; E=I+2; D=max({o},I)+{d}; F=max(E,D)+1={f}; '
       f'apoio={support}; C=100000+{support}+{direct}={cost}.',
       {'parcelas_fixas_sem_apoio':100000,'apoio_total':support,'adicional_direto':direct},
       ['Aviso usa ID c_d74a não declarado entre as obrigações. Referência inequívoca ao único apoio, cláusula d_540c '
        'e mesmos fixo/cobertura/taxa permite identificar p_a84d por descrição; convém corrigir rastreabilidade do ID.'] if credit else [])

# Usinagem U>=0 desconhecida: eliminar simbolicamente máximos, sem escolher U=0.
# I=max(2,U)+3. D=max(8,I)+3 domina E=I+2. F=max(8,max(2,U)+3)+4=max(12,U+7).
th={'fim_dia':unknown('dia_corrido',12,note='F=max(12,U+7), U inteiro >=0; sem teto.'),
    'delta_prazo_dias':unknown('dia_corrido',0,direction='nao_diminui',note='ΔF=max(0,U-5); pode ser zero ou positivo.'),
    'custo_centavos':unknown('BRL_centavo',167500,direction='aumento'),
    'delta_custo_centavos':unknown('BRL_centavo',2500,direction='aumento')}
append_case('k_d307',th,b_unknown('U pode ser menor ou maior que 4; falta rede para provar direção do marco. '
            'Apoio sem crédito preserva 65000 e obrigação direta +2500 prova custo mínimo 167500.',
            cost_floor=167500,base_cost=nbc,base_finish=nbf),None,
            'U∈inteiros >=0; F=max(12,U+7); ΔF=max(0,U-5). '
            'C=167500+7500*max(0,U-5); ΔC=2500+7500*max(0,U-5).',
            {'adicional_direto':2500,'dominio_usinagem':'inteiro >=0; não usar duração antiga nem atribuir zero'},
            ['U=0..5 produz F=12; U=6 produz F=13. A direção do prazo é não diminui, mas aumento estrito não está provado.'])

# Verificação interna matemática, sem qualquer artefato externo de referência.
assert len(results)==15 and len({r['caso_id'] for r in results})==15
for u in range(101):
    f,_=nacar(machining=u)
    c,_=nacar_cost(f,direct=2500)
    assert f==max(12,u+7)
    assert c==167500+7500*max(0,u-5)
for case in results:
    assert all(ref in sources for ref in case['fontes_refs_TH']+case['fontes_refs_B'])
    assert all(sources[ref]['documento_id'] in case['documentos_permitidos_B'] for ref in case['fontes_refs_B'])
    assert case['T']==case['H']

ordering=[c['caso_id'] for pkg in PACKAGES for c in loaded[pkg]['cenarios']['casos']]
results.sort(key=lambda r:ordering.index(r['caso_id']))
script_hash=sha(Path(__file__).read_bytes())
out={
 'metodo':{'tipo':'auditoria técnica cega por agente separado; não revisão humana nem garantia de independência científica',
    'momento_utc':datetime.now(timezone.utc).isoformat(),
    'restricao_contexto':'Somente base.json, cenarios.json e fontes.json dos dois pacotes autorizados.',
    'nao_lidos':['gabaritos','previsões','estado_projeto.json','src','testes','docs','relatórios','outros outputs'],
    'rede_e_api_paga':False,'comparacao_autoral_realizada':False,
    'selagem':'SHA256 das seis entradas, dos trechos e do script; SHA256 do JSON registrado em NOTAS.md antes de comparação externa.',
    'script_sha256':script_hash,
    'convencoes':['Dias corridos inteiros; intervalos [início,fim); valores monetários inteiros em centavos.',
       'Avisos isolados: somente alterações expressas substituem cláusulas base.',
       'Programação no início mais cedo permitido; fontes fornecem restrições mínimas, sem ordem explícita de otimização. '
       'Resultados pontuais de término adotam essa convenção usual; sem ela atrasos voluntários seriam ilimitados.',
       'estado=exato: valor único; direcao: sinal estrito provado sem magnitude única; indeterminado: valor e/ou sinal estrito não resolvidos. '
       'Uma faixa [0,infinito) de delta não prova aumento estrito.',
       'null é desconhecido, nunca zero. Limite superior null significa não estabelecido; quando texto diz sem teto, é ilimitado.',
       'T e H recebem a mesma união de fontes; não é possível justificar diferença de inferibilidade entre eles sem acrescentar dados.',
       'B não recebe documentos relacionais; inferências que exigem monotonicidade/convergência genérica são declaradas condicionais.']},
 'entradas_sha256':manifest,'fontes_literais':sources,
 'linhas_base':{
  PACKAGES[0]:{'fim_dia':ibf,'custo_centavos':ibc,'cronograma':ibschedule,
    'derivacao':'Receber [2,3); preparar [0,5); montar [5,8); testar [8,10); marco D10. Soma de cinco parcelas=500000; extensão=0.',
    'fontes_refs':base_iris_refs,'B':'D10/500000 declarados em f_bbb437fd83, sem validação temporal independente na ausência da rede.'},
  PACKAGES[1]:{'fim_dia':nbf,'custo_centavos':nbc,'cronograma':nbschedule,
    'derivacao':'Suporte [0,2); usinagem [0,4); integrar [4,7); ensaio [7,9); dossiê [8,11); inspeção [11,12); marco D12. Fixos=100000; apoio=50000+2*7500=65000.',
    'fontes_refs':base_nacar_refs,'B':'D12/165000 declarados nos comuns; não reconstruir rede ausente.'}},
 'casos':results,
 'verificacoes':{'total_casos':15,'fontes_refs_validas':True,'B_sem_fonte_relacional':True,
    'identidade_simbolica_U_verificada_em':{'min':0,'max':100},
    'observacao':'A prova geral consta da álgebra, amostra numérica é somente checagem aritmética.'}}
raw=(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode()
(HERE/'derivacoes.json').write_bytes(raw)
json_hash=sha(raw)
notes='''# Revisão técnica cega — selada antes de comparação

Esta revisão foi feita por agente separado, com contexto limitado ao pacote cego. Não é revisão humana nem garantia de independência científica. Não foram lidos gabaritos, previsões, motor, testes, estado normalizado, relatórios ou documentos externos. Não houve rede, API paga ou acesso a credenciais. O script usa apenas a biblioteca padrão e os seis JSON autorizados.

As relações e fórmulas foram transcritas das fontes literais, não importadas de código. Os valores declarados de base estavam inevitavelmente visíveis nos documentos permitidos, mas as duas bases foram recalculadas: Íris D10/500000; Nácar D12/165000. Não confundir essa verificação interna dos documentos com comparação a referências autorais de resultados.

Resultados pontuais adotam execução no início mais cedo permitido. Sem essa premissa, as cláusulas de não-antes permitem espera voluntária e não definem datas únicas. Não há disputa de recursos. Valores monetários são centavos; dias são corridos inteiros, em intervalos semiabertos.

T e H usam a mesma união documental, portanto têm a mesma inferibilidade nesta revisão. B usa apenas comuns+aviso. A ausência da ficha relacional não autoriza tratar a rede como vazia. Nos casos sem alteração temporal, B conserva a referência conhecida. Algumas conclusões B de custo com redução de duração exigem a premissa geral de precedências monotônicas, explicitamente registrada; a própria rede não foi usada nessas conclusões. Atraso local do dossiê até pelo menos D13 em k_6d82 somente prova atraso do marco se for adotada a convergência das entregas, que não está explícita em B.

O caso k_23d8 permanece indeterminado na leitura literal conservadora: aceite pendente impede manter automaticamente três dias, e preço técnico não tem domínio numérico declarado. Subtotal certo é 520000, não custo total. A leitura usual de custo adicional não negativo, reforçada pela proibição de créditos implícitos, permite direção de aumento e piso 520000; isso está registrado como conclusão condicional. O piso estrutural D9 não afirma viabilidade de montagem instantânea. Não há prazo máximo ou garantia de conclusão. Essa ambiguidade não deve ser escondida por preenchimento com zero.

Em k_8c65, preço da extensão explicitamente não negativo e sem teto permite custo >=520000, embora o término D12 seja exato. Em k_d307, U>=0 é domínio explícito: F=max(12,U+7), ΔF=max(0,U-5), C=167500+7500*max(0,U-5). Não há antecipação, mas pode haver neutralidade ou atraso; o custo aumenta estritamente em pelo menos 2500.

O aviso k_42a9 usa c_d74a sem declaração prévia desse identificador; a descrição do único apoio, contrato citado e valores idênticos permitem mapear semanticamente a p_a84d. Recomenda-se ajustar a rastreabilidade, sem mudar a interpretação calculada.

| Caso | Fim T/H | Δdias | Custo T/H | Δcentavos |
|---|---:|---:|---:|---:|
'''
for row in results:
    t=row['T']
    def show(metric):
        x=t[metric]
        return str(x['valor']) if x['estado']=='exato' else ('≥'+str(x['limite_inferior']) if x['limite_inferior'] is not None else 'indeterminado')
    notes+='| '+row['caso_id']+' | '+' | '.join(show(k) for k in ('fim_dia','delta_prazo_dias','custo_centavos','delta_custo_centavos'))+' |\n'
notes+='\nAs faixas não são previsões pontuais. A fonte literal completa, identificadores e SHA256 por trecho estão em derivacoes.json.\n\n'
notes+='## Selo SHA256\n\nSelado antes de qualquer comparação externa. O hash deste próprio NOTAS.md será comunicado separadamente para evitar autorreferência.\n\n'
notes+='- calcular_independente.py: `'+script_hash+'`\n'
notes+='- derivacoes.json: `'+json_hash+'`\n'
for item in manifest:
    notes+='- '+str(Path(item['arquivo']).relative_to(INPUT))+': `'+item['sha256']+'`\n'
(HERE/'NOTAS.md').write_text(notes)
print(json.dumps({'casos':len(results),'sha256':{'calcular_independente.py':script_hash,
                 'derivacoes.json':json_hash,'NOTAS.md':sha((HERE/'NOTAS.md').read_bytes())}},ensure_ascii=False))
