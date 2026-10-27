"""Fixtures MOCK sintéticas. Valores vêm das regras aqui, não de caso/gabarito real."""
from copy import deepcopy
from interpretacao_no.contratos import hash_json
REF = dict(fonte_id='f_evento_mock', localizador='L1')
CLAUSULA = dict(fonte_id='f_clausula_mock', localizador='L1')

def exato(valor, ref=REF, delta=False):
    return dict(estado='exato', valor=valor, direcao=('aumento' if valor > 0 else 'reducao' if valor < 0 else 'zero') if delta else 'desconhecida', evidencias=[deepcopy(ref)], lacunas=[], motivo=None)

def desconhecido(texto='Dado quantitativo realmente não informado', ref=REF):
    return dict(estado='indeterminado', valor=None, direcao='desconhecida', evidencias=[deepcopy(ref)], lacunas=[texto], motivo=None)

def projeto():
    f = dict(id=REF['fonte_id'], documento_id='d_mock', versao='1', localizador='L1', trecho='MOCK: alpha passa a seis dias, beta a cinco. Duas obrigações distintas p_aa11 de300 e p_bb22 de700 centavos. A equivalência foi aceita.')
    fc = dict(id=CLAUSULA['fonte_id'], documento_id='d_clausula_mock', versao='1', localizador='L1', trecho='MOCK: equivalência aceita mantém três dias de integração, sem cobrança de readequação desta cláusula; outras obrigações não são dispensadas.')
    duracoes = {'n_alpha': 2, 'n_beta': 4, 'n_join': 3, 'n_marco': 0}
    e = dict(schema_version='1.0-proposta', projeto_id='q_mock', versao='v_mock', moeda='BRL', calendario=dict(unidade='dia_corrido', indice_inicial=0), fontes=[f, fc], entidades=[dict(id=n, tipo='marco' if n == 'n_marco' else 'atividade', nome=n, atributos={}, fonte_refs=[REF]) for n in duracoes], atividades=[dict(id=n, entidade_id=n, duracao=exato(v), restricoes_liberacao=[], fonte_refs=[REF]) for n, v in duracoes.items()], relacoes=[dict(id='l_'+a+'_'+b, origem_id=a, destino_id=b, tipo='precede_FS', lag_dias=0, fonte_refs=[REF]) for a,b in [('n_alpha','n_join'),('n_beta','n_join'),('n_join','n_marco')]], parcelas_base=[dict(id='p_fixo', escopo_id='q_mock', descricao='Fixo MOCK', valor_centavos=10000, moeda='BRL', fonte_refs=[REF]),dict(id='p_tempo', escopo_id='q_mock', descricao='Incidência temporal MOCK', valor_centavos=0, moeda='BRL', fonte_refs=[REF])], regras_custo=[dict(id='c_tempo', parcela_id='p_tempo', taxa_centavos_dia=5000, unidade_taxa='BRL_centavo/dia_corrido', intervalo=dict(inicio_ref='D0', fim_ref=dict(atividade_id='n_marco', atributo='fim')), base_contratada_dias=7, politica_reducao='sem_credito', condicao='MOCK: taxa diária após sete dias até o término do marco', fonte_refs=[REF])], regras_transferencia=[], regras_locais=[dict(id='r_equiv', no_id='n_join', clausula=CLAUSULA, fonte_refs=[CLAUSULA], condicao_textual=fc['trecho'], operacoes_permitidas=['confirmar_manutencao_atributo','confirmar_ausencia_parcela_adicional'], atributos_alvo=['duracao','readequacao'])], marco_final_id='n_marco', declaracoes_completude={k:dict(completa=True, fonte_refs=[REF]) for k in ('entregas','custos','relacoes')}, linha_base=dict(fim=exato(7), custo_centavos=exato(10000)))
    e['regras_custo'][0]['decomposicao_base'] = dict(fixo_centavos=exato(0), incidencia_centavos=exato(0))
    ev = dict(evento_id='e_mock', projeto_id=e['projeto_id'], versao_projeto=e['versao'], instante_observacao=0, relato=f['trecho'], origem=dict(autor='MOCK',documento_id='d_mock',data_registro='D0'), entidades_mencionadas=['n_join'], escopo='Contraprova sintética de integração', lacunas=[], evidencias=[f])
    return e, ev

def proposta(c, op, alvo, valor, regra=None):
    perm = next(p for p in c['permissoes'] if p['operacao'] == op and p['alvo_id'] == alvo)
    refs = [REF, CLAUSULA] if regra else [REF]
    return dict(id=c['no_id']+':'+op+':'+alvo+(':'+regra if regra else ''), **perm, valor=deepcopy(valor), evidencias=deepcopy(refs), regra_refs=[regra] if regra else [], relacao_refs=[], condicoes=[dict(predicado='aplicabilidade_'+regra, estado='confirmada', evidencias=deepcopy(refs))] if op.startswith('confirmar_') else [], origens_causais=[dict(evento_id=c['evento_id'], fato_ref=REF, efeito_id=hash_json([c['evento_id'],alvo]))], no_id=c['no_id'])

def analise(c, *, versao='1.0-proposta', custo=1000, notas=False, desconhecer=False, taxas_desconhecidas=False):
    ps = []
    if c['no_id'] == 'n_alpha': ps.append(proposta(c,'substituir_duracao','n_alpha',exato(6)))
    if c['no_id'] == 'n_beta': ps.append(proposta(c,'substituir_duracao','n_beta',exato(5)))
    if c['no_id'] == 'n_join':
        if desconhecer:
            ps.append(proposta(c,'substituir_duracao','n_join',desconhecido(), 'r_equiv'))
            ob = 'lacuna_'+hash_json([c['evento_id'],'r_equiv','readequacao'])[:16]
            ps.append(proposta(c,'registrar_lacuna_custo',ob,desconhecido(), 'r_equiv'))
        else:
            ps.append(proposta(c,'confirmar_manutencao_atributo','n_join',3,'r_equiv'))
            ps.append(proposta(c,'confirmar_ausencia_parcela_adicional','n_join',0,'r_equiv'))
        ps += [proposta(c,'adicionar_parcela','p_aa11',exato(300)),proposta(c,'adicionar_parcela','p_bb22',exato(700))]
    if c['no_id'] == 'n_marco' and taxas_desconhecidas:
        ps.append(proposta(c,'aplicar_regra_catalogada','c_tempo',{'taxa_centavos_dia':None}))
        ps[-1]['regra_refs']=['c_tempo']
    a = {k:deepcopy(c[k]) for k in ('execucao_id','evento_id','no_id','revisao','contexto_hash','predecessores_versoes')}
    a.update(schema_version=versao, analise_id='a_'+c['no_id'], avaliacao=dict(prazo=desconhecido('O prazo global cabe ao solver'),custo=exato(custo,delta=True) if c['no_id']=='n_join' else desconhecido('Incidência depende do cronograma final')),propostas=ps,justificativa='MOCK prescrito: formato e integração, não avaliação de IA real.',lacunas=['O marco e a parcela temporal serão calculados pelo solver'] if notas else [])
    if versao != '1.0-proposta': a['pendencias_operacionais']=[]
    return a
