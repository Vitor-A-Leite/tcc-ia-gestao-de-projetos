"""Cadastro versionado de texto preparado. Não extrai Word/PDF nem infere vínculos."""
from copy import deepcopy
import json
import re
from pathlib import Path
from .vendor.interpretacao_no.contratos import hash_json


def validar_documento(doc, entidades):
    if not isinstance(doc,dict) or doc.get('papel') not in ('planejamento','mudanca','situacao'):
        raise ValueError('Papel documental inválido')
    for key in ('id','versao','nome','autoria'):
        if not isinstance(doc.get(key),str) or not doc[key].strip(): raise ValueError('Campo obrigatório: '+key)
    if not all(re.fullmatch(r'[A-Za-z0-9_.-]+',doc[k]) for k in ('id','versao')): raise ValueError('Identidade/versão inválida')
    if doc.get('formato')!='texto_preparado_json': raise ValueError('Somente JSON de texto preparado')
    if type(doc.get('sintetico')) is not bool: raise ValueError('Origem sintética precisa ser explícita')
    if not isinstance(doc.get('trechos'),list) or not doc['trechos']: raise ValueError('Trechos obrigatórios')
    seen=set()
    for t in doc['trechos']:
        if not isinstance(t,dict) or not all(isinstance(t.get(k),str) and t[k].strip() for k in ('id','texto','localizador')): raise ValueError('Trecho incompleto')
        if t['id'] in seen: raise ValueError('Trecho duplicado')
        seen.add(t['id'])
        if not isinstance(t.get('vinculos'),list) or not set(t['vinculos'])<=set(entidades): raise ValueError('Vínculos não cadastrados')
        if 'afirmacao' in t:
            a=t['afirmacao']
            if doc['papel']!='situacao' or set(a)!={'entidade','campo','valor','unidade'}: raise ValueError('Afirmação não normalizada')
            if a['entidade'] not in entidades or a['campo'] not in ('inicio','fim','custo','versao'): raise ValueError('Afirmação fora de catálogo')
    return deepcopy(doc)


def cadastrar(arquivo, destino, entidades):
    if arquivo.suffix.lower()!='.json': raise ValueError('Word/PDF/TXT não são importados automaticamente; prepare o JSON de trechos')
    d=validar_documento(json.loads(arquivo.read_text(encoding='utf8')),entidades)
    destino.mkdir(parents=True,exist_ok=True)
    anteriores=[json.loads(p.read_text()) for p in destino.glob('*.json')]
    prev=d.get('anterior')
    if prev and prev not in {x['id']+'@'+x['versao'] for x in anteriores}: raise ValueError('Versão anterior não cadastrada')
    if not prev and any(x['id']==d['id'] for x in anteriores): raise ValueError('Nova versão exige vínculo com anterior')
    target=destino/(d['id']+'@'+d['versao']+'.json')
    with target.open('x',encoding='utf8') as f: json.dump(d,f,indent=2,ensure_ascii=False)
    return dict(arquivo=str(target),hash=hash_json(d),interpretacao='não executada',atualizacao_oficial=False)
