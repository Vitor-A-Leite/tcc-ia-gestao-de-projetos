"""Registra julgamentos do coordenador após leitura das fontes e respostas.

Revisão técnica posterior, não cega, não humana. Não repara respostas.
"""
from pathlib import Path
import json,sqlite3,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'TCC_Codigos/src'))
from interpretacao_no.contratos import hash_json
from piloto_real.runner import gravar_novo
from condicoes.baseline import IDENTIDADES,QUANTIDADES,validar_quantidade

def check(c,m):
    if not c:raise ValueError(m)
def ler(p):return json.loads(p.read_text())

def main():
    registros=ler(OUT/'registros.json');audits=[];locais=[];falhas=[]
    fontes={f['id']:f for f in ler(ROOT/'TCC_Codigos/data/final/etapa10_v2/inputs/fontes.json')['fontes']}
    primeiro='k_1671298a5a';incerto='k_c23705f4ea';credito='k_ec2826cc2a'
    notas={
      (primeiro,'B','prazo'):'A view B omite as arestas. A justificativa usa D15 e a soma 6+3+5=14 das atividades não alteradas: qualquer caminho de 15 dias inclui uma atividade alongada, garantindo atraso mínimo de 3 dias. A magnitude não é identificada: domínio auditado {3,4,6}. A resposta conserva somente aumento.',
      (primeiro,'B','custo'):'O atraso é estritamente positivo; a cobertura acaba em D15 e a taxa positiva de 8600 centavos/dia permanece. A resposta conserva aumento sem magnitude; domínio auditado {25800,34400,51600}.',
      (primeiro,'T','prazo'):'A justificativa calcula alinhamento até D14, configuração até D13 e validação até D19 com as precedências visíveis. Delta 19-15=4.',
      (primeiro,'T','custo'):'O apoio incide uma única vez por 4 dias adicionais; 4×8600=34400 centavos. Não há cobrança direta; total 554800.',
      (primeiro,'H','prazo'):'As propostas locais substituem A por 8 e B por 10, ambas sustentadas pelo aviso visível. Os demais parâmetros permanecem. O rastro calcula C até 14, D até 13 e E/marco até 19; delta 4. Os dez encaminhamentos se resolvem nas duas propostas, sem criar efeitos extras.',
      (primeiro,'H','custo'):'O livro preserva as cinco parcelas fixas (428700), cobra o apoio uma vez (91700+34400=126100) e soma 554800. Aviso sem cobrança direta; apoio de 8600/dia após D15 visível no marco. Delta 34400.',
      (incerto,'H','prazo'):'A proposta do responsável substitui configurar por 9 dias. A apuração do preço não condiciona execução. Precedências produzem configuração D7–D16 e validação D16–D21; delta 6, sem contaminação pela lacuna monetária.',
      (incerto,'H','custo'):'O marco reconhece aditivo expresso e propõe taxa_centavos_dia=null, preservando fixo e cobertura. O livro conserva cinco parcelas, apoio com mínimo 91700 e delta mínimo zero, sem limite superior. A referência é 6r, r inteiro não negativo: zero é possível mas não identificado. Indeterminação adequada; a saída não codifica a congruência módulo 6, apenas um limite externo correto.',
      (credito,'B','prazo'):'O aviso mantém explicitamente durações, liberações, precedências e condições do apoio. O término de referência D15 permanece, mesmo sem arestas visíveis; delta zero sustentado.',
      (credito,'B','custo'):'Crédito definitivo de 11600 sobre obrigação existente, sem novo ajuste. 520400-11600=508800; delta -11600 sustentado.',
      (credito,'T','prazo'):'As relações textuais e durações preservadas produzem D15; o aviso exclui alteração temporal. Delta zero sustentado.',
      (credito,'T','custo'):'O aviso reduz a parcela existente em 11600, sem duplicação. Total 508800 e delta -11600 sustentados.',
      (credito,'H','prazo'):'As seis análises preservam os parâmetros temporais, de acordo com o aviso; o motor mantém D15. Não se substitui falta de informação por zero: há declaração expressa de manutenção.',
      (credito,'H','custo'):'O responsável troca a parcela p_dc2a93810b de 138600 para 127000, apoiado no crédito de 11600. O livro mantém seis parcelas únicas; apoio segue 91700 sem extensão; total 508800. Dois encaminhamentos apontam à mesma proposta, sem duplicação.',
    }
    for reg in registros:
        s=reg['metadados'];r=reg['resultado'];caso=s['caso_id'];cond=s['condicao']
        for dim in ('prazo','custo'):
            invalido=r['execucao']['estado']=='erro'
            nota=('O envelope global foi rejeitado por ausência de justificativa no nível superior; não existe desfecho aceito a aprovar. O conteúdo bruto é examinado separadamente em falhas_formato.json e não é resgatado nas métricas.' if invalido else notas[(caso,cond,dim)])
            audits.append(dict(execucao_id=s['execucao_id'],resultado_hash=reg['resultado_hash'],view_hash=s['view_hash'],desfecho=dim,suporte='insuficiente' if invalido else 'sustentado',revisor='Codex /root — revisão técnica posterior do coordenador, não cega',justificativa=nota,revisao_humana=False))
        if cond!='H':continue
        checks=0;propostas=[];enc=[]
        for step in r['rastro_orquestracao']:
            if 'analise' not in step:continue
            a=step['analise'];ctx=step['contexto'];check(a['execucao']['estado']=='ok','Análise local inválida')
            vis={f['id']:f for f in ctx['fontes']}
            for fid,f in vis.items():check(f==fontes[fid],'Fonte local diferente da original')
            for proposta in a['propostas']:
                for ev in proposta['evidencias']:check(ev['fonte_id']in vis and vis[ev['fonte_id']]['localizador']==ev['localizador'],'Citação invisível')
            propostas.extend(a['propostas']);enc.extend(a['encaminhamentos']);checks+=1
            locais.append(dict(execucao_id=s['execucao_id'],resultado_hash=reg['resultado_hash'],no_id=a['no_id'],analise_id=a['analise_id'],analise_hash=hash_json(a),contexto_hash=ctx['contexto_hash'],estado=a['execucao']['estado'],fontes_visiveis=list(vis),propostas=a['propostas'],encaminhamentos=a['encaminhamentos'],julgamento='sustentado',justificativa=a['justificativa'],nota_revisor='Confrontados o aviso corrente, parâmetros locais, propostas e encaminhamentos; os campos sem alteração permanecem conforme cláusula expressa. Julgamento do coordenador após a coleta.'))
        check(checks==6 and len(r['livro_parcelas'])==6 and len({p['parcela_id']for p in r['livro_parcelas']})==6,'Contagem/duplicação local')
        f=r['registro_operacional']['fechamento_final']
        check(not f['pendencias'] and all(e['estado']=='resolvido_operacional_condicional' for e in f['encaminhamentos']),'Encaminhamento sem resolução')
        valores={(p['operacao'],p['alvo_id']):p['valor']for p in propostas}
        if caso==primeiro:
            check(len(propostas)==2 and valores[('substituir_duracao','n_1cdb614bb0')]['valor']==8 and valores[('substituir_duracao','n_e6792e8666')]['valor']==10,'Propostas do primeiro caso')
        elif caso==incerto:
            check(len(propostas)==2 and valores[('substituir_duracao','n_40da7d7e19')]['valor']==9 and valores[('alterar_parametros_contratuais','c_9c40eea6e9')]=={'taxa_centavos_dia':None},'Propostas do caso incerto')
        else:check(len(propostas)==1 and valores[('substituir_parcela','p_dc2a93810b')]['valor']==127000,'Crédito aplicado')
    with sqlite3.connect((OUT/'ledger_final.sqlite').as_uri()+'?mode=ro',uri=True)as db:
        for reg in registros:
            if reg['resultado']['execucao']['estado']!='erro':continue
            s=reg['metadados'];cid,raw=db.execute('select id,registro from chamadas where slot=?',(s['execucao_id'],)).fetchone();r=json.loads(raw)
            texto=''.join(part['text']for msg in r['response']['output']if msg['type']=='message' for part in msg['content']if part['type']=='output_text')
            original=json.loads(texto);esperado=set(IDENTIDADES+QUANTIDADES+('justificativa',));faltam=esperado-set(original);extras=set(original)-esperado
            check(faltam=={'justificativa'} and not extras,'Outra causa de formato')
            ctx=json.loads(r['payload']['input'][1]['content']);fs=ctx['view']['comum']['fontes']
            if s['condicao']=='T':fs=fs+[json.loads(l.split(': ',1)[1])for l in ctx['view']['relacoes_texto'].splitlines()if l.startswith('fontes: ')]
            for k in IDENTIDADES:check(original[k]==ctx[k],'Identidade do bruto')
            for k in QUANTIDADES:validar_quantidade(original[k],fs,k not in ('delta_dias','delta_centavos'),'dia_corrido'if k in QUANTIDADES[:3]else'BRL_centavo')
            nota=('O bruto T contém D21 e delta +6 com derivação correta. Declara custo 520400+6r, taxa desconhecida podendo ser zero; não afirma aumento estrito.' if s['condicao']=='T' else 'O bruto B preserva prazo e custo indeterminados: sem arestas não decide se haverá atraso; sem taxa substituta não quantifica o custo nem afirma aumento estrito.')
            falhas.append(dict(execucao_id=s['execucao_id'],resultado_hash=reg['resultado_hash'],call_id=cid,campos_ausentes=sorted(faltam),campos_extras=sorted(extras),json_sintaticamente_valido=True,quantidades_individualmente_validas=True,conteudo_bruto=original,avaliacao_semantica_diagnostica=nota,suporte_bruto='sustentado',efeito_metricas='invalido em ambas as dimensões; sem reparo, resgate ou nova inferência',revisao_humana=False))
    for n,obj in [('auditoria_semantica.json',audits),('auditoria_local_H.json',locais),('falhas_formato.json',falhas)]:gravar_novo(OUT/n,obj)
    print(json.dumps(dict(dimensoes=len(audits),sustentadas=sum(a['suporte']=='sustentado'for a in audits),invalidas_sem_resgate=4,analises_locais=len(locais),falhas_formato=len(falhas))))

if __name__=='__main__':main()
