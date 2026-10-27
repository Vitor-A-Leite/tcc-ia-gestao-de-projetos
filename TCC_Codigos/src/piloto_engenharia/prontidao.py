"""Estimativa e diagnóstico local; não autoriza nem executa lote pago."""
from fractions import Fraction
from interpretacao_no.contratos import hash_json

REQUISITOS = frozenset((
    "transporte_concreto_e_timeout", "limites_token_e_reserva_orcamentaria_globais",
    "politica_H_sem_oraculo", "autorizacao_operacional_vs_suporte_semantico",
    "normalizacao_versoes_e_ids", "fechamento_obrigacoes_evento",
    "prompts_schemas_hashes", "referencias_e_inferibilidade_por_view",
    "rubrica_e_auditoria_semantica", "ordem_execucao_e_persistencia_sem_selecao",
    "retencao_logs_e_dados_enviados"))


def hash_lote(plano):
    return hash_json({k:v for k,v in plano.items() if k != "aprovacao_lote"})


def estimar(plano):
    """Limites de planejamento, nunca consumo observado ou cotação do provedor."""
    campos = ('casos','repeticoes','max_analises_H','max_retries_transporte',
              'max_tokens_entrada_por_chamada','max_tokens_saida_por_chamada')
    for k in campos:
        v = plano[k]
        if type(v) is not int or v < (0 if k=='max_retries_transporte' else 1):
            raise ValueError('Limite inválido: '+k)
    if plano['max_retries_transporte'] > 1:
        raise ValueError('Contrato v1 admite no máximo um retry de transporte')
    if plano['condicoes'] != ['B','H','T']:
        raise ValueError('Pacote diagnóstico exige B/H/T')
    pares = plano['casos'] * plano['repeticoes']
    logicas = pares * (2 + plano['max_analises_H'])
    tentativas = logicas * (1 + plano['max_retries_transporte'])
    entrada = tentativas * plano['max_tokens_entrada_por_chamada']
    saida = tentativas * plano['max_tokens_saida_por_chamada']
    # Preços em BRL por milhão são entradas futuras, sem arredondamento prematuro.
    precos = plano.get('precos_BRL_por_milhao')
    custo = None
    if precos is not None:
        for k in ('entrada','saida'):
            if isinstance(precos[k],bool): raise ValueError('Preço inválido')
            v = Fraction(str(precos[k]))
            if v < 0: raise ValueError('Preço inválido')
        centavos = (entrada*Fraction(str(precos['entrada'])) + saida*Fraction(str(precos['saida']))) / 10000
        custo = -(-centavos.numerator // centavos.denominator)
    return dict(runs=pares*3,pares_caso_repeticao=pares,chamadas_logicas_max=logicas,
                tentativas_transporte_max=tentativas,tokens_entrada_max=entrada,
                tokens_saida_max=saida,custo_api_teto_centavos=custo,
                natureza='estimativa conservadora condicionada a limites ainda não implementados em transporte real')


def diagnosticar(plano):
    e = estimar(plano)
    requisitos = plano.get('requisitos')
    if not isinstance(requisitos, dict): requisitos = {}
    pendencias = [k for k in sorted(REQUISITOS) if requisitos.get(k) != 'verificado']
    if not isinstance(plano.get('modelo'), str) or not plano['modelo'].strip():
        pendencias.append('modelo')
    if not isinstance(plano.get('configuracao'), dict): pendencias.append('configuracao')
    aprovacao = plano.get('aprovacao_lote')
    if not (isinstance(aprovacao, dict) and aprovacao.get('aprovado') is True
            and isinstance(aprovacao.get('lote_id'), str) and aprovacao['lote_id'].strip()
            and aprovacao.get('lote_hash') == hash_lote(plano)
            and isinstance(aprovacao.get('declarante'), str) and aprovacao['declarante'].strip()):
        pendencias.append('aprovacao_lote')
    if plano.get('precos_BRL_por_milhao') is None:
        pendencias.append('cotacao_oficial_atual_e_conversao_BRL')
    orcamento = plano.get('orcamento_api_centavos')
    if type(orcamento) is not int or orcamento <= 0:
        pendencias.append('orcamento_api_centavos')
    elif e['custo_api_teto_centavos'] is not None and e['custo_api_teto_centavos'] > orcamento:
        pendencias.append('estimativa_excede_orcamento')
    return dict(pronto_para_execucao=not pendencias,pendencias=pendencias,estimativa=e,
                aviso='Diagnóstico declarativo local, não certificação, prova semântica ou autorização humana/rede; JSON autoafirmado não comprova aprovação externa')
