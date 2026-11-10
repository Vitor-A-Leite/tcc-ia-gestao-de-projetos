"""Avaliador offline separado do preditor; referências só após a previsão."""
from datetime import datetime, timezone
import hashlib
import json
import tempfile
from . import ROOT
from .pipeline import simular, ler_cenario
from .sessoes import Sessoes, gravar


def resumo(r):
    return dict(quantidades={k:{x:r[k].get(x) for x in ('estado','valor','limites')} for k in ('fim_novo','delta_dias','custo_novo','delta_centavos')},
                recomendacoes=sorted([x['unidade'],x['valor_proposto']] for x in r['verificacao_documental']['recomendacoes']),
                afirmacoes=[[x['unidade'],x['estado']] for x in r['verificacao_documental']['afirmacoes']])


def comparar():
    dest=ROOT/'outputs'/('comparacao_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));dest.mkdir(parents=True)
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        m=Sessoes(tmp)
        for i in range(1,10):
            cid=f'D{i:02}';r_all=simular(cid)
            s=m.preparar(cid,ler_cenario(cid)['entidades_mencionadas'],'todos');s=m.executar(s['id']);r=s['resultado']
            # Persistir previsões antes de consultar as referências do avaliador.
            gravar(dest/(cid+'_completo.json'),r_all);gravar(dest/(cid+'_seletivo.json'),r)
            refs=json.loads((ROOT/'avaliacao/equivalencia_v1.json').read_text())
            same=resumo(r)==refs[cid] and resumo(r_all)==refs[cid]
            rows.append(dict(cenario=cid,entradas=s['selecao']['nos_entrada'],analises_completas=r_all['consumo']['analises'],
                             analises_seletivas=s['consumo']['solicitacoes_simuladas'],valores_estados_documentos_equivalentes=same,
                             segundos_software=s['consumo']['segundos'],chamadas_api=0,recomendacoes=len(r['verificacao_documental']['recomendacoes'])))
    before=sum(r['analises_completas'] for r in rows);after=sum(r['analises_seletivas'] for r in rows)
    result=dict(natureza='simulacao_offline; respostas locais preparadas manualmente',casos=rows,
                total_analises_completas=before,total_analises_seletivas=after,
                analises_simuladas_evitadas=before-after,reducao_analises_percentual=round(100*(before-after)/before,2),
                equivalencia_casos=sum(r['valores_estados_documentos_equivalentes'] for r in rows),
                economia_api_nao_medida=True,qualidade_interpretacao_ia_nao_avaliada=True,destino=str(dest.relative_to(ROOT)))
    gravar(dest/'metricas.json',result)
    return result


def integridade():
    manifest=json.loads((ROOT/'MANIFESTO_ORIGENS.json').read_text())
    divergentes=[]
    for item in manifest['componentes']:
        path=ROOT/item['destino'];expected=item.get('sha256_entrega',item['sha256_incorporado'])
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:divergentes.append(item['destino'])
    return dict(ok=not divergentes,componentes_incorporados=len(manifest['componentes']),divergentes=divergentes,
                historicos='Ver docs/preservacao_depois.json: conferência realizada no repositório; execução isolada não lê versões anteriores.')
