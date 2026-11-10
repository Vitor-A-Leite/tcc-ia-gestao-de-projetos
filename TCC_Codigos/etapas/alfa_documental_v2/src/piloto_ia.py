"""Piloto explicitamente autorizado: D02, sugestão real, teto de todos os nós."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,sqlite3,hashlib,stat,time
from . import ROOT
from .ia_real import TransporteReal,Sugestor,MODELO,CONFIG
from .vendor.hibrido_v07_r3.adaptador import LocalV07R3
from .sessoes import Sessoes
from .pipeline import ler_cenario
from .avaliacao import resumo

def salvar(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rodar',action='store_true');a=parser.parse_args()
    if not a.rodar:raise SystemExit('Use --rodar para o piloto real autorizado.')
    repo=ROOT.parents[2];hist=repo/'TCC_Codigos/outputs/etapa9_piloto_real_aprovado_20261026/ledger.sqlite'
    with sqlite3.connect('file:'+str(hist)+'?mode=ro',uri=True) as db:
        antigo=db.execute('SELECT coalesce(sum(comprometido),0) FROM chamadas').fetchone()[0]
    path=repo/'.env.piloto'
    if path.is_symlink() or stat.S_IMODE(path.stat().st_mode)!=0o600:raise ValueError('Credencial local requer permissão0600')
    key=path.read_text().split('=',1)[1].strip()
    dest=ROOT/'outputs'/('ia_real_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'));dest.mkdir(parents=True)
    transporte=TransporteReal(dest,key,antigo);inicio=time.monotonic();s=None;err=None;comparacao=None
    manifesto=dict(cenario='D02',modelo=MODELO,configuracao=CONFIG,nos='todos',limite_inferencias=33,teto_novo_usd=.40,teto_agregado_usd=5,historico_comprometido_usd=antigo/1e9,autorizacao='Mensagem do usuário nesta conversa: rodar IA real, sugestão de nó pela IA, máximo de nós; escolha da sugestão delegada ao agente.',precos_fonte='https://developers.openai.com/api/docs/models/gpt-6-luna',precos_usd_milhao={'input':.1,'cached_input':.01,'output':.5},natureza='Piloto de desenvolvimento N=1; não validação científica conclusiva',hashes_codigo={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src').rglob('*.py')})
    salvar(dest/'manifesto.json',manifesto);print(str(dest),flush=True)
    try:
        c=ler_cenario('D02');salvar(dest/'evento.json',c)
        m=Sessoes(dest/'sessoes')
        s=m.preparar('D02',c['entidades_mencionadas'],'todos',modo='ia_real',limites={'max_solicitacoes':33,'max_custo_centavos':40,'max_segundos':7200})
        suggestion=m.sugestao(s['id'],'sugestao-inicial',Sugestor(transporte));salvar(dest/'sugestao.json',suggestion)
        ids=[n['no_id'] for n in suggestion['sugestoes']]
        if suggestion['ambiguidades'] or len(ids)!=1:raise ValueError('Sugestão não inequívoca de um único ponto; requer revisão humana')
        s=m.selecionar(s['id'],ids,'todos',origem='ia_autorizada_pelo_usuario')
        salvar(dest/'selecao_confirmada.json',dict(entradas=ids,origem='IA; aceita pelo agente por delegação explícita do usuário',limite=s['selecao']['maximo_disponivel']))
        print('Entrada sugerida: '+','.join(ids)+'; análise real iniciada',flush=True)
        adapter=LocalV07R3(transporte,modelo=MODELO,configuracao=CONFIG,timeout_s=180)
        s=m.executar(s['id'],adaptador_real=adapter);salvar(dest/'sessao.json',s);salvar(dest/'resultado.json',s['resultado'])
        # Previsão persistida antes de abrir qualquer referência de avaliação.
        refs=json.loads((ROOT/'avaliacao/equivalencia_v1.json').read_text())['D02']
        got=resumo(s['resultado']);comparacao=dict(equivalente=got==refs,observado=got,referencia=refs,natureza='Referência autoral de desenvolvimento; não gabarito humano independente')
        salvar(dest/'comparacao.json',comparacao)
    except Exception as e:
        err={'tipo':type(e).__name__,'mensagem':str(e).replace(key,'[REDACTED]')};salvar(dest/'erro.json',err)
        if s is not None:
            try:
                s=m.ler(s['id']);salvar(dest/'sessao.json',s)
                if s.get('resultado'):salvar(dest/'resultado.json',s['resultado'])
            except Exception:
                pass  # preservar o erro original; não realizar nova chamada
    finally:
        use=transporte.snapshot();use['tempo_total_s']=round(time.monotonic()-inicio,3);salvar(dest/'consumo.json',use)
        r=(s or {}).get('resultado') or {};vd=r.get('verificacao_documental') or {}
        lines=['# Piloto real Alfa v2 — GPT-6 Luna high','',f'Data UTC: {datetime.now(timezone.utc).isoformat()}. Cenário D02; N=1, uma execução.','',f'Estado da sessão: {(s or {}).get("estado","não iniciada")}.',f'Erro do fluxo: {err or "nenhum"}.',f'Equivalência com referência autoral: {comparacao["equivalente"] if comparacao else "não avaliada"}.','', '## Resultado observado','',f'Prazo: {r.get("fim_novo")}',f'Custo do projeto (centavos BRL): {r.get("custo_novo")}',f'Recomendações documentais: {len(vd.get("recomendacoes",[]))}.','', '## Consumo real','', '```json',json.dumps(use,ensure_ascii=False,indent=2),'```','', 'Custo em USD calculado pelo uso retornado e preços oficiais; não é uma fatura. Reservas desconhecidas não são tratadas como consumo zero. O histórico financeiro anterior permanece intacto e integra o teto.','', '## O que funcionou e o que falhou','', 'A execução usa o serviço OpenAI, com saída estruturada e validação independente; não lê respostas manuais de simulação. Sugestão, seleção, resultado e chamadas ficam registrados separadamente.', 'Os números acima e os arquivos comparacao.json/erro.json determinam o sucesso deste piloto. Respostas inválidas ou pendências não foram reparadas silenciosamente.','', '## Melhorias e próximos passos','', '- Auditar semanticamente justificativas e evidências com o orientador; equivalência numérica não prova validade de toda justificativa.', '- Expandir a coleta aos demais eventos, com repetições e referências revisadas, sem alterar prompts a partir dos casos finais reservados.', '- Comparar seleção manual, sugestão por IA e cobertura completa com os mesmos fatos; medir qualidade e custo em conjunto.', '- Testar falhas reais de rede, cancelamento em voo e retomada sem cobranças duplicadas em piloto separado.', '- Integrar a visualização das sessões reais no frontend e distinguir simulação de execução real em todos os rótulos.', '- Ampliar a avaliação documental além das cinco afirmações preparadas do Status Report; manter ausência de dados explícita.','', '## Limites','', 'JSON estruturado e grafo previamente cadastrado. Não importa ata livre/áudio/PDF, não altera documentos oficiais e não constitui uma validação de todos os cenários. Nenhum fallback de modelo ou retry automático foi usado.','', '[Documentação oficial do modelo](https://developers.openai.com/api/docs/models/gpt-6-luna).']
        (dest/'RELATORIO.md').write_text('\n\n'.join(lines)+'\n')
        print(json.dumps({'destino':str(dest),'estado':(s or {}).get('estado'),'erro':err,'equivalente':comparacao and comparacao['equivalente'],'consumo':use},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
