"""Observatório offline: projeção de apresentação; cálculos pertencem ao motor."""
from copy import deepcopy
import json
from pathlib import Path
from uuid import uuid4
from interpretacao_no.contratos import hash_json
from motor_deterministico.motor import preparar
from orquestracao import ordem, projecao
from orquestracao.simulacao import InterpretadorPrescrito, politica_prescrita
from condicoes.views import montar_views
from condicoes.hibrido import executar_h

ROOT = Path(__file__).resolve().parents[2]


def ler(path):
    return json.loads(path.read_text(encoding='utf-8'))


def quantidade(q, moeda=False, delta=False):
    """Formata somente; nunca transforma limites em total nem ausência em zero."""
    if not isinstance(q, dict):
        return 'Não disponível'
    def valor(v):
        if type(v) is not int:
            raise ValueError('Quantitativo exige inteiro')
        sinal = '+' if delta and v > 0 else ''
        if moeda:
            inteiro, centavos = divmod(abs(v), 100)
            return ('−' if v < 0 else sinal) + 'R$ ' + f'{inteiro:,}'.replace(',', '.') + f',{centavos:02}'
        return sinal + str(v) + (' dias' if delta else ' (dia corrido)')
    estado = q.get('estado')
    if estado == 'exato':
        return valor(q['valor'])
    texto = {'direcao': 'Direção: ' + q.get('direcao', 'desconhecida'),
             'indeterminado': 'Indeterminado', 'inaplicavel': 'Inaplicável'}.get(estado, 'Não disponível')
    limites = q.get('limites') or {}
    partes = []
    for chave, simbolo in [('inferior', '≥'), ('superior', '≤')]:
        if limites.get(chave) is not None:
            partes.append(simbolo + ' ' + valor(limites[chave]))
    return texto + (' · ' + '; '.join(partes) if partes else '')


class Observatorio:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        dados = self.root / 'data/desenvolvimento'
        self.estado = ler(dados/'projeto_minimo_grafo_v1/estado_projeto.json')
        inputs = dados/'projeto_minimo_v1/inputs'
        self.base = ler(inputs/'base.json')
        self.fontes = ler(inputs/'fontes.json')['fontes']
        self.casos = {c['caso_id']: c for c in ler(inputs/'cenarios.json')['casos']}
        self.fixtures = dados/'orquestracao_simulada_v1'
        self.vinculo = dict(base_hash=hash_json(self.base), grafo_hash=hash_json(self.estado),
                            versao_base=self.base['versao_projeto'], versao_grafo=self.estado['versao'])
        datas, _ = preparar(self.estado)
        self.datas_base = {n: {k: v.saida() for k, v in d.items()} for n, d in datas.items()}

    def catalogo(self):
        return dict(casos=[dict(id=k, evento_id=c['evento_id'], relato=c['relato'], resumo=c['relato'][:115]+('…' if len(c['relato'])>115 else '')) for k,c in self.casos.items()],
                    modos=['normal', 'parcial', 'erro'], origem='simulado',
                    condicoes={'H': 'Replay prescrito disponível', 'B': 'Sem execução; view disponível', 'T': 'Sem execução; view disponível'})

    def executar(self, caso, modo='normal'):
        if caso not in self.casos or modo not in ('normal','parcial','erro'):
            raise ValueError('Caso ou modo desconhecido')
        comum = self.casos[caso]
        fixture = ler(self.fixtures/(caso+'.json'))
        if fixture['evento']['evento_id'] != comum['evento_id']:
            raise ValueError('Fixture de outro evento')
        fixture_origem_hash=hash_json(fixture)
        fixture = deepcopy(fixture)
        fixture['execucao_id'] = 'observatorio-' + uuid4().hex
        vs = montar_views(self.base, comum, self.fontes, self.estado, vinculo=self.vinculo)
        politica = politica_prescrita(fixture, **({'max_analises': 1} if modo=='parcial' else {}))
        if modo == 'erro':
            # Contraprova operacional declarada, rejeitada pelo validador real da agenda.
            politica.alvos = ['no_inexistente_teste_interface']
        r = executar_h(self.base, comum, self.fontes, self.estado, fixture['evento'], vs['H'],
                      InterpretadorPrescrito(fixture), politica, vinculo=self.vinculo, origem='simulado')
        pacote=self.apresentar(r, fixture, vs, modo, politica)
        pacote['identidades']['fixture_arquivo_hash']=fixture_origem_hash
        return pacote

    def apresentar(self, r, fixture, views, modo, politica):
        if (r.get('evento_id') != fixture['evento']['evento_id'] or r.get('projeto_id') != self.estado['projeto_id']
            or r.get('versao') != self.estado['versao'] or r.get('snapshot_hash') != hash_json(self.estado)
            or r.get('view_hash') != views['H']['view_hash'] or r.get('condicao') != 'H'):
            raise ValueError('Identidade/versão/hash incompatíveis com a apresentação')
        # Todo valor exibido conserva seu objeto científico original no download.
        resumo = []
        for titulo, base, novo, delta, moeda in [
            ('Prazo final','fim_base','fim_novo','delta_dias',False),
            ('Custo do projeto','custo_base','custo_novo','delta_centavos',True)]:
            resumo.append(dict(titulo=titulo, antes=quantidade(r.get(base),moeda),
                depois=quantidade(r.get(novo),moeda), delta=quantidade(r.get(delta),moeda,True),
                conhecimento=r.get(delta), completude=r.get('completude',{}).get('custo' if moeda else 'prazo','Não disponível')))
        resultados = {n['no_id']: n for n in r.get('resultados_nos',[])}
        passos = {n['no_id']: n for n in r.get('rastro_orquestracao',[])}
        nos=[]
        atividades={a['id']:a for a in self.estado['atividades']}
        correntes={a['no_id']:a for a in r.get('registros_correntes',[])}
        nomes={a['id']:a['nome'] for a in self.estado['entidades']}
        seq, pred = ordem(self.estado)
        niveis = {}
        for ident in seq:
            niveis[ident] = 1 + max((niveis[p] for p in pred[ident]), default=-1)
        for n in self.estado['entidades']:
            atual=resultados.get(n['id'],{})
            temporal=n['id'] in atividades
            datas=self.datas_base.get(n['id'],{})
            campos=[]
            for campo, titulo in [('inicio','Início'),('fim','Fim'),('duracao_usada','Duração')]:
                antes=atividades.get(n['id'],{}).get('duracao') if campo=='duracao_usada' else datas.get(campo)
                campos.append(dict(titulo=titulo, antes=quantidade(antes) if temporal else 'Não se aplica (entidade não temporal)',
                    depois=quantidade(atual.get(campo)) if temporal else 'Não se aplica (entidade não temporal)'))
            if n['tipo']=='componente':
                campos.append(dict(titulo='Disponibilidade',antes=quantidade(n.get('atributos',{}).get('disponibilidade',{}).get('conhecimento')),
                    depois=quantidade(correntes.get(n['id'],{}).get('quantitativo',{}).get('disponibilidade'))))
            predecessores=[]
            for ident in sorted(pred[n['id']]):
                reg=correntes.get(ident,{})
                predecessores.append(dict(nome=nomes[ident],id=ident,estado=reg.get('estado','Não avaliado'),
                    revisao=reg.get('revisao'), dados=[dict(campo=k,valor=quantidade(v)) for k,v in reg.get('quantitativo',{}).items()]))
            restricoes=[dict(id=x['id'],tipo=x['tipo'],valor=quantidade(x['valor']),fontes=x['fonte_refs']) for x in atual.get('restricoes_usadas',[])]
            efeitos=[dict(parcela_id=x['parcela_id'],delta=quantidade(x.get('delta_centavos'),True,True),fontes=x.get('fonte_refs',[])) for x in atual.get('efeitos_custo',[])]
            nos.append(dict(id=n['id'], nome=n['nome'], tipo=n['tipo'], nivel_visual=niveis[n['id']],
                baseline=self.datas_base.get(n['id']), resultado=atual or None, campos=campos, predecessores=predecessores, restricoes=restricoes, efeitos=efeitos, passo=deepcopy(passos.get(n['id'])),
                fim_base=quantidade(self.datas_base.get(n['id'],{}).get('fim')),
                fim_novo=quantidade(atual.get('fim')), delta=quantidade(atual.get('delta_fim'),delta=True),
                disponibilidade_base=n.get('atributos',{}).get('disponibilidade'),
                estado=atual.get('processamento','nao_avaliado')))
        for no in nos:
            no['propostas_apresentacao']={}
            analise=(no.get('passo') or {}).get('analise') or {}
            for proposta in analise.get('propostas',[]):
                valor_proposto=proposta.get('valor')
                if type(valor_proposto) is int:
                    valor_proposto={'estado':'exato','valor':valor_proposto}
                no['propostas_apresentacao'][proposta['id']]=quantidade(valor_proposto,proposta.get('unidade')=='BRL_centavo')
        regras={k:deepcopy(self.estado[k]) for k in ('regras_locais','regras_custo')}
        for regra in regras['regras_custo']:
            regra['apresentacao']=quantidade({'estado':'exato','valor':regra['taxa_centavos_dia']},True)+'/dia; '+str(regra['base_contratada_dias'])+' dias contratados; '+regra['politica_reducao']+'; intervalo '+str(regra['intervalo'])
        descricoes={p['id']:p['descricao'] for p in self.estado['parcelas_base']}
        parcelas=[dict(original=p, incidencia_base=quantidade(p.get('incidencia_base'),True), incidencia_nova=quantidade(p.get('incidencia_nova'),True), descricao=descricoes.get(p['parcela_id'],'Obrigação adicional documentada'), antes=quantidade({'estado':'exato','valor':p['base_centavos']},True),
                       depois=quantidade(p.get('novo'),True), delta=quantidade(p.get('delta'),True,True))
                  for p in r.get('livro_parcelas',[])]
        alteracoes=[]
        decisoes={d['proposta_id']:d for d in r.get('decisoes',[])}
        for passo in r.get('rastro_orquestracao',[]):
            for proposta in (passo.get('analise') or {}).get('propostas',[]):
                if proposta['operacao']=='aplicar_regra_catalogada':
                    campos=[]
                    for chave,valor in proposta['valor'].items():
                        if chave=='taxa_centavos_dia':
                            texto='Taxa: desconhecida; a taxa BASE não deve ser tomada como vigente' if valor is None else 'Taxa: '+quantidade({'estado':'exato','valor':valor},True)+'/dia'
                        elif chave=='base_contratada_dias': texto='Base contratada: '+str(valor)+' dias'
                        else: texto=chave.replace('_',' ')+': '+str(valor)
                        campos.append(texto)
                    alteracoes.append(dict(regra=proposta['alvo_id'], parametros='; '.join(campos),
                        decisao=decisoes.get(proposta['id'],{}).get('status','Sem decisão final de aplicação'),
                        fontes=proposta['evidencias']))
        return dict(schema='1.0-observatorio', origem='simulado', modo=modo,
            aviso='Replay prescrito: interpretação e política autorais; Python calcula. Sem LLM real, sem validação científica independente.',
            resultado=r, resumo=resumo, nos=nos, parcelas=parcelas, evento=fixture['evento'],
            views=views, politica=dict(origem=fixture['origem'], plano=fixture['plano'],alvos=politica.alvos, limite_analises=politica.max_analises, limite_chamadas=politica.max_chamadas, limite_tempo_s=politica.max_tempo_s,
                dispensas=fixture.get('dispensas',{}), contraprova=modo),
            grafo=dict(relacoes=self.estado['relacoes'], regras_transferencia=self.estado['regras_transferencia'],
                arcos_causais=projecao(self.estado)),
            regras=regras, alteracoes_contratuais=alteracoes,
            fontes=self.estado['fontes']+fixture['evento']['evidencias'],
            identidades=dict(snapshot_hash=hash_json(self.estado),evento_hash=hash_json(fixture['evento']),
                fixture_execucao_hash=hash_json(fixture), view_hash=views['H']['view_hash'], resultado_hash=hash_json(r)),
            condicoes=self.catalogo()['condicoes'])

    def avaliacao(self):
        # Fronteira explícita e independente do caminho executar(). Nenhum gabarito é input de H.
        pasta=self.root/'outputs/etapa7_offline_20261025/demo'
        return dict(aviso='AVALIAÇÃO SEPARADA: oito casos sintéticos simétricos. Não são os avisos Bancada Íris; não avaliam IA nem superioridade.',
                    arquivos={nome:ler(pasta/(nome+'.json')) for nome in
                        ('manifesto','metricas','previsoes_prescritas','referencias_sinteticas','auditorias_prescritas')})
