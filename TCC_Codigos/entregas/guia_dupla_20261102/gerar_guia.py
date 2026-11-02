from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from copy import deepcopy
from io import BytesIO
import hashlib, json, re, subprocess, sys
from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
REF = Path('/Users/vaugusto/.codex/plugins/cache/openai-curated-remote/openai-templates/0.1.1/skills/artifact-template-system-design/assets/reference.docx')
FINAL = BASE / 'Guia_do_desenvolvimento_para_redacao_do_TCC.docx'
SKILL = Path('/Users/vaugusto/.codex/plugins/cache/openai-primary-runtime/documents/26.1026.10807/skills/documents')
HASH = '13504f6c221a42c1726460a9e865e563355539ff97d702d6c9b2267b4b261d76'
assert hashlib.sha256(REF.read_bytes()).hexdigest() == HASH
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
W = '{' + NS['w'] + '}'
R = '{' + NS['r'] + '}'

def clone(x):
    y = deepcopy(x)
    for a in y.iter():
        for k in list(a.attrib):
            if k.endswith('}paraId') or k.endswith('}textId'):
                del a.attrib[k]
    return y

def replace_p(p, text):
    run = next((x for x in p.findall('w:r', NS) if x.find('w:t', NS) is not None), None)
    rp = deepcopy(run.find('w:rPr', NS)) if run is not None and run.find('w:rPr', NS) is not None else None
    for child in list(p):
        if child.tag != W + 'pPr': p.remove(child)
    rr = E.SubElement(p, W + 'r')
    if rp is not None: rr.append(rp)
    tt = E.SubElement(rr, W + 't'); tt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); tt.text = text
    return p

def xml(x): return E.tostring(x, encoding='UTF-8', xml_declaration=True, standalone=True)

with ZipFile(REF) as z: original = {n:z.read(n) for n in z.namelist()}
root = E.fromstring(original['word/document.xml'])
body = root.find('w:body', NS)
src = [deepcopy(x) for x in body]
sect = deepcopy(src[-1])
for x in list(body): body.remove(x)

# Clone the cover in place; all typography and spacing remain source-derived.
cover = [deepcopy(x) for x in src[:23]]
replace_p(cover[8], 'Prazo e custo')
replace_p(cover[9], 'Guia para a redação')
cells = cover[20].findall('w:tr/w:tc', NS)
for ci, head, value in [(0,'SITUAÇÃO','Etapa 12 entregue'),(2,'EQUIPE','Dupla do TCC'),(4,'ATUALIZAÇÃO','02 de novembro de 2026')]:
    ps = cells[ci].findall('w:p', NS)
    replace_p(ps[0], head); replace_p(ps[1], value)
metadata = [('Autoria','Equipe do TCC com apoio de IA'),('Revisão','Parecer humano pendente'),('Evidências','Relatórios, código e registros do experimento'),('Finalidade','Explicar o desenvolvimento para apoiar a escrita do TCC')]
for row, (label, value) in zip(cover[22].findall('w:tr', NS), metadata):
    for c, text in zip(row.findall('w:tc', NS), (label, value)):
        ps=c.findall('w:p', NS); replace_p(ps[0],text)
        for p in ps[1:]: c.remove(p)
for x in cover: body.append(x)

def para(text, role='body', page_break=False):
    proto = {'body':24, 'h1':23, 'h3':38, 'caption':36}[role]
    p = replace_p(clone(src[proto]), text)
    if page_break:
        pp=p.find('w:pPr',NS); E.SubElement(pp,W+'pageBreakBefore')
    if re.match(r'^R\d+ ',text):
        # The left-aligned source caption pattern avoids stretched filename lines.
        pp=p.find('w:pPr',NS); jc=pp.find('w:jc',NS)
        if jc is None: jc=E.SubElement(pp,W+'jc')
        jc.set(W+'val','left')
    body.append(p)
    return p

def space():
    p = clone(src[29]); body.append(p)

def table(rows):
    n=len(rows[0]); proto={2:28,3:69,4:40}[n]
    t=clone(src[proto]); old=t.findall('w:tr',NS)
    for row in old: t.remove(row)
    for i,data in enumerate(rows):
        row=clone(old[0] if i==0 else old[1+(i-1)%min(2,len(old)-1)])
        cs=row.findall('w:tc',NS)
        assert len(cs)==n
        for ci,(cell,value) in enumerate(zip(cs,data)):
            ps=cell.findall('w:p',NS)
            p=replace_p(ps[0],value)
            for extra in ps[1:]: cell.remove(extra)
            # Short measurements align centrally; narrative cells retain the source alignment.
            if i>0 and (re.fullmatch(r'[0-9.,/−+ sUS$]+',value) or value in ('B','H','T')):
                pp=p.find('w:pPr',NS)
                if pp is None: pp=E.SubElement(p,W+'pPr')
                jc=pp.find('w:jc',NS)
                if jc is None: jc=E.SubElement(pp,W+'jc')
                jc.set(W+'val','center')
        t.append(row)
    if rows[0][0]=='Estado de conhecimento':
        # Keep this compact conceptual comparison on one page.
        for row in t.findall('w:tr',NS)[:-1]:
            for p in row.findall('w:tc/w:p',NS):
                pp=p.find('w:pPr',NS)
                if pp is None: pp=E.SubElement(p,W+'pPr')
                if pp.find('w:keepNext',NS) is None: E.SubElement(pp,W+'keepNext')
    body.append(t)
    # Use the source blank after-table pattern for natural separation.
    space()

content=(BASE/'conteudo.md').read_text()
lines=content.splitlines(); i=0; first_heading=True; note_done=False
while i<len(lines):
    s=lines[i].strip()
    if not s: i+=1; continue
    if s.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            ss=lines[i].strip()
            vals=[x.strip() for x in ss.strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',x) for x in vals): rows.append(vals)
            i+=1
        table(rows); continue
    if s.startswith('# '):
        para(s[2:],'h1',page_break=first_heading)
        first_heading=False
    elif s.startswith('## '):
        para(s[3:],'h3')
    elif s=='!FIG!':
        p=clone(src[35]); pp=p.find('w:pPr',NS)
        if pp is None: pp=E.SubElement(p,W+'pPr')
        E.SubElement(pp,W+'keepNext')
        for dp in p.xpath('.//wp:docPr',namespaces=NS):
            dp.set('descr','Fluxo H: estado e evento, contextos locais, interpretação por IA, validação, motor determinístico e resultado. As referências de avaliação ficam fora do preditor.')
            dp.set('name','Arquitetura H')
        body.append(p)
    else:
        role='caption' if s.startswith('Figura 1.') else 'body'
        p=para(s,role)
        if s.startswith('O cronograma usa dias') and not note_done:
            fn=src[32].xpath('.//w:r[w:footnoteReference]',namespaces=NS)[0]
            p.append(clone(fn)); note_done=True
    i+=1
body.append(sect)

# Figure made from the documented system, replacing the template's placeholder.
im=Image.new('RGB',(1300,667),'white'); d=ImageDraw.Draw(im)
fontroot=Path('/System/Library/Fonts/Supplemental')
normal=ImageFont.truetype(str(fontroot/'Arial.ttf'),27)
bold=ImageFont.truetype(str(fontroot/'Arial Bold.ttf'),29)
small=ImageFont.truetype(str(fontroot/'Arial.ttf'),25)
navy='#082A4A'; slate='#5B7085'; pale='#E6F0F8'
d.rectangle((0,0,1299,62),fill=navy)
d.text((30,14),'Fluxo da condição híbrida H',font=bold,fill='white')
blocks=[(35,95,'1 Estado e evento',['Linha de base','e mudança relatada']), (470,95,'2 Contextos locais',['Fontes, relações','e regras permitidas']), (905,95,'3 Interpretação IA',['Propostas de alteração','e lacunas locais']), (35,365,'4 Validação',['Campos, fontes','e permissões']), (470,365,'5 Motor Python',['Cronograma e livro','de parcelas']), (905,365,'6 Resultado',['Totais, deltas,','rastro e lacunas'])]
for x,y,title,txt in blocks:
    d.rectangle((x,y,x+360,y+155),fill=pale,outline=slate,width=2)
    d.text((x+18,y+20),title,font=bold,fill=navy)
    for j,line in enumerate(txt): d.text((x+18,y+69+j*35),line,font=normal,fill=navy)
def arrow(a,b):
    d.line((a,b),fill=slate,width=5)
    x,y=b; dx=b[0]-a[0]; dy=b[1]-a[1]
    if abs(dx)>=abs(dy):
        direction=1 if dx>0 else -1; poly=[(x,y),(x-14*direction,y-9),(x-14*direction,y+9)]
    else:
        direction=1 if dy>0 else -1; poly=[(x,y),(x-9,y-14*direction),(x+9,y-14*direction)]
    d.polygon(poly,fill=slate)
for y in (173,443): arrow((399,y),(462,y)); arrow((834,y),(897,y))
d.line([(1085,254),(1085,306),(215,306)],fill=slate,width=5)
arrow((215,306),(215,357))
d.line((35,572,1265,572),fill='#CAD8E4',width=2)
d.text((35,590),'Referências reservadas entram somente na avaliação posterior.',font=small,fill=slate)
imagebuf=BytesIO(); im.save(imagebuf,format='PNG')
(BASE/'qa/arquitetura.png').write_bytes(imagebuf.getvalue())

footer=E.fromstring(original['word/footer1.xml'])
for p in footer.findall('.//w:p',NS):
    if p.xpath('.//w:t',namespaces=NS): replace_p(p,'TCC | Guia do desenvolvimento e do experimento')
footnotes=E.fromstring(original['word/footnotes.xml'])
for t in footnotes.xpath('//w:t',namespaces=NS):
    t.text=' D0 é uma origem relativa do cronograma. Os casos finais são futuros em relação a essa origem e usam dias corridos, conforme o protocolo da etapa 10.'
rels=E.fromstring(original['word/_rels/document.xml.rels'])
for r in rels:
    if r.get('Id')=='rId9': r.set('Target','../../docs/desenvolvimento/STATUS.md')
# Keep the existing hyperlink relationship functional in the source map.
target_p=next(p for p in body.findall('w:p',NS) if ''.join(p.xpath('.//w:t/text()',namespaces=NS)).startswith('R1 Estado geral'))
link=E.SubElement(target_p,W+'hyperlink');link.set(R+'id','rId9')
rr=E.SubElement(link,W+'r'); rp=E.SubElement(rr,W+'rPr')
E.SubElement(rp,W+'rStyle').set(W+'val','Hyperlink')
lt=E.SubElement(rr,W+'t'); lt.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); lt.text=' Abrir o estado geral.'

changed={'word/document.xml':xml(root),'word/footer1.xml':xml(footer),'word/footnotes.xml':xml(footnotes),'word/media/image1.png':imagebuf.getvalue(),'word/_rels/document.xml.rels':xml(rels)}
with ZipFile(FINAL,'w',ZIP_DEFLATED) as z:
    for n, data in original.items(): z.writestr(n,changed.get(n,data))

# Fidelity and content checks: compare actual parts, section, relationships, and source hash.
with ZipFile(FINAL) as z:
    assert set(z.namelist())==set(original)
    assert all(z.read(n)==v for n,v in original.items() if n not in changed)
    newroot=E.fromstring(z.read('word/document.xml'))
    assert E.tostring(newroot.find('w:body/w:sectPr',NS),method='c14n',exclusive=True)==E.tostring(src[-1],method='c14n',exclusive=True)
    visible=' '.join(newroot.xpath('//w:t/text()',namespaces=NS))
    assert not re.search(r'\[Draft|\[Name|\[Describe|\[Team|System Name|Title of Proposal|example.com',visible)
    assert len(newroot.xpath('//w:footnoteReference',namespaces=NS))==1
    assert len(newroot.xpath('//w:drawing',namespaces=NS))==1
assert hashlib.sha256(REF.read_bytes()).hexdigest()==HASH
report={'final':str(FINAL),'word_count_markdown':len(content.split()),'reference_sha256':HASH,'changed_parts':list(changed),'preserved_parts':len(original)-len(changed),'sections':1,'main_sections':12,'figure_count':1,'footnote_count':1,'reference_unchanged':True,'paid_api_calls':0}
(BASE/'qa/fidelidade_estrutural.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,ensure_ascii=False,indent=2))
