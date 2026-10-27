"""Runner único aprovado: plano imutável,90slots; nada acontece ao importar."""
from copy import deepcopy
from itertools import permutations
from collections import Counter
from pathlib import Path
import hashlib
import json
import os
from . import MODELO,CONFIG,POLITICA,LOTE_ID
from .inputs import carregar
from .ledger import Ledger
from .transporte import Responses,HTTP,sanitizar
from .politica import construir
from interpretacao_no import LLM
from interpretacao_no.contratos import hash_json
from condicoes.baseline import Global
from condicoes.hibrido import executar_h
from avaliacao.execucoes import registrar,validar_manifesto


def codigo():
    src=Path(__file__).resolve().parents[1]
    return {str(p.relative_to(src)):hashlib.sha256(p.read_bytes()).hexdigest()
        for pacote in ('piloto_real','condicoes','orquestracao','interpretacao_no','motor_deterministico','avaliacao')
        for p in sorted((src/pacote).glob('*.py'))}


def preparar(dados):
    aprov_path=Path(dados)/'ampliacao_v1/lote_aprovado_v03.json'
    aprov_bruto=aprov_path.read_bytes();aprov=json.loads(aprov_bruto)
    if (aprov['lote_id']!=LOTE_ID or aprov['modelo']!=MODELO or aprov['limite_agregado_USD']!='5.00'
        or aprov['max_output_tokens_total_inclui_raciocinio']!=25000 or aprov['max_tentativas_inferencia']!=300
        or aprov['casos']!=15 or aprov['repeticoes']!=2 or aprov['condicoes']!=['B','H','T']):raise ValueError('Escopo diverge do lote aprovado')
    casos=carregar(dados);slots=[];ordens=list(permutations('BHT'))
    # Seis permutações, repetidas em sequência fixa; diferença de no máximo1.
    for j,caso in enumerate(sorted(casos,key=lambda c:c['caso_id'])):
        for rep in (1,2):
            for c in ordens[(2*j+rep-1)%6]:
                e=caso['estado'];ev=caso['evento'];b=caso['base']
                slots.append(dict(execucao_id=LOTE_ID+'-'+caso['caso_id']+'-'+c+'-'+str(rep),caso_id=caso['caso_id'],repeticao=rep,condicao=c,
                    projeto_id=e['projeto_id'],evento_id=ev['evento_id'],versao_projeto=e['versao'] if c=='H' else b['versao_projeto'],
                    versao_protocolo=POLITICA,view_hash=caso['views'][c]['view_hash'],snapshot_hash=hash_json(e),evento_hash=hash_json(ev),
                    codigo_hash=hash_json(codigo()),modelo=MODELO,config_hash=hash_json(CONFIG),origem='llm_transporte_injetado'))
    plano=dict(lote_id=LOTE_ID,uso='piloto_desenvolvimento',aprovacao=dict(data='2026-10-26',limite_USD='5.00',saida_total_por_chamada=25000,origem='autorizacao_humana_registrada_na_etapa9'),
        aprovacao_arquivo_sha256=hashlib.sha256(aprov_bruto).hexdigest(),
        modelo=MODELO,configuracao=deepcopy(CONFIG),politica=POLITICA,retries=0,max_entrada=16000,max_tentativas=300,
        ordem='seis_permutacoes_balanceadas_em_ordem_de_ID_caso_e_repeticao;deterministica_sem_seed',
        codigo=codigo(),inputs={c['caso_id']:c['hashes_inputs'] for c in casos},slots=slots)
    m=dict(schema_version='1.0-manifesto',uso='piloto',condicoes=['B','H','T'],execucoes=slots)
    validar_manifesto(m)
    return plano,m,{c['caso_id']:c for c in casos}


def gravar_novo(path,obj):
    """Exclusive create/fsync: SQLite é o registro canônico atômico para retomada."""
    path=Path(path)
    bruto=json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n'
    if path.exists():
        if path.read_bytes()!=bruto:raise ValueError('Exportação existente divergente; não sobrescrever')
        return
    import tempfile
    fd,tmp=tempfile.mkstemp(prefix='.export_',dir=str(path.parent))
    try:
        with os.fdopen(fd,'wb') as f:f.write(bruto);f.flush();os.fsync(f.fileno())
        try:os.link(tmp,path) #publicação atômica sem sobrescrever
        except FileExistsError:
            if path.read_bytes()!=bruto:raise ValueError('Exportação concorrente divergente')
    finally:os.unlink(tmp)



def indisponivel(s,codigo_erro):
    return dict(execucao_id=s['execucao_id'],projeto_id=s['projeto_id'],evento_id=s['evento_id'],versao=s['versao_projeto'],condicao=s['condicao'],view_hash=s['view_hash'],
        execucao=dict(estado='erro',origem=s['origem'],modelo=MODELO,configuracao=CONFIG,config_hash=hash_json(CONFIG),erros=[dict(codigo=codigo_erro,mensagem='Slot preservado sem previsão; não repetir automaticamente')]),
        suporte_semantico='nao_auditado',consumo=dict(chamadas=None,tokens_entrada=None,tokens_saida=None,custo_api_centavos=None))


def executar(dados,pasta,*,chave=None,http=None,coletar=False,redator=None):
    plano,manifesto,casos=preparar(dados)
    if coletar and http is None and not chave:raise ValueError('Chave ausente; configure localmente antes de executar')
    redact=redator or (lambda x:sanitizar(x,chave))
    with Ledger(pasta,plano) as l:
        pasta=Path(pasta)
        gravar_novo(pasta/'plano.json',plano);gravar_novo(pasta/'manifesto.json',manifesto)
        if not coletar:return dict(estado='preparado_sem_rede',slots=90,lote_id=LOTE_ID,orcamento=l.resumo())
        api=http or HTTP(chave)
        for s in plano['slots']:
            eid=s['execucao_id'];status=l.estado(eid)
            if status=='terminado':continue
            if status=='iniciado':
                # Queda pode ter ocorrido depois do envio. Não reenviar o run/local nodes.
                l.salvar(eid,registrar(s,indisponivel(s,'INTERROMPIDO_SEM_REPLAY')));continue
            l.iniciar(eid)
            try:
                c=casos[s['caso_id']];t=Responses(l,eid,api,redator=redact,timeout_s=30)
                if s['condicao']=='H':
                    politica=construir(c['estado'],c['evento'],execucao_id=eid)
                    i=LLM(t,modelo=MODELO,configuracao=CONFIG,timeout_s=30,repetir_transporte=False)
                    r=executar_h(c['base'],c['evento_comum'],c['fontes'],c['estado'],c['evento'],c['views']['H'],i,politica,vinculo=c['vinculo'],origem='llm_transporte_injetado')
                    r.update(natureza_previsao='condicional_original',suporte_semantico='nao_auditado',registro_operacional=deepcopy(politica.registro_operacional))
                else:
                    r=Global(t,modelo=MODELO,configuracao=CONFIG,timeout_s=30,repetir_transporte=False,origem='llm_transporte_injetado').prever(c['views'][s['condicao']],execucao_id=eid)
                    r.update(natureza_previsao='original_global_nao_corrigida',suporte_semantico='nao_auditado')
                r['orcamento_apos_slot']=l.resumo()
                registro=redact(registrar(s,r))
            except Exception:
                # Detalhes de transporte sanitizados estão no ledger. Não vazar exceção/headers.
                registro=registrar(s,indisponivel(s,'FALHA_SLOT_SANITIZADA'))
            l.salvar(eid,registro)
        resultados=l.resultados()
        for eid,_,r in resultados:
            if r is not None:gravar_novo(pasta/(eid+'.json'),r)
        resumo=dict(lote_id=LOTE_ID,N_planejado=90,por_condicao={},orcamento=l.resumo(),metricas_IA=None,
                    suporte_semantico='nao_auditado',nota='Sem avaliação científica; referências/inferibilidade e auditoria posteriores. Inferência/tokenização reais identificadas no ledger.')
        for cond in 'BHT':
            rs=[r for _,_,r in resultados if r is not None and r['metadados']['condicao']==cond]
            resumo['por_condicao'][cond]=dict(N=30,persistidos=len(rs),estados=dict(Counter(r['resultado']['execucao']['estado'] for r in rs)))
        # Resumo derivado pode ser reexportado em versão nova; resultados originais são imutáveis.
        gravar_novo(pasta/('resumo-'+hash_json(resumo)[:12]+'.json'),resumo)
        return resumo
