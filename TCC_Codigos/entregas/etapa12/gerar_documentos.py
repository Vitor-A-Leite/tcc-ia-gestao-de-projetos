"""Converte os textos da entrega em dois DOCX editáveis; usa python-docx do runtime."""
from pathlib import Path
import re
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE=Path(__file__).resolve().parent

def cellprops(cell):
    pr=cell._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
    for side in ['top','left','bottom','right']:
        x=OxmlElement('w:'+side);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');b.append(x)
    pr.append(b);m=OxmlElement('w:tcMar')
    for side in ['top','left','bottom','right']:
        x=OxmlElement('w:'+side);x.set(qn('w:w'),'100');x.set(qn('w:type'),'dxa');m.append(x)
    pr.append(m);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

def create(src,dest):
    d=Document();s=d.sections[0];s.page_width=Cm(21);s.page_height=Cm(29.7);s.top_margin=Cm(2.4);s.bottom_margin=Cm(2.2);s.left_margin=Cm(2.6);s.right_margin=Cm(2.2)
    normal=d.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(12);normal.font.color.rgb=RGBColor(0,0,0);normal.paragraph_format.line_spacing=1.12;normal.paragraph_format.space_after=Pt(7)
    for style in d.styles:
        for border in list(style.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
    for style,size in [('Title',22),('Subtitle',11),('Heading 1',16),('Heading 2',13)]:
        st=d.styles[style];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0);st.paragraph_format.space_before=Pt(10);st.paragraph_format.space_after=Pt(8)
    footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    run=footer.add_run('Etapa 12  |  ');run.font.size=Pt(9)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    d.core_properties.title=src.read_text().splitlines()[0][2:];d.core_properties.author='Projeto TCC';d.core_properties.subject='Consolidação do experimento final de prazo e custo'
    lines=src.read_text().splitlines();i=0
    while i<len(lines):
        text=lines[i].strip();i+=1
        if not text:continue
        if text=='<!-- page -->':
            if 'revisao_orientador' in str(src):d.add_page_break()
            continue
        if text.startswith('|'):
            rows=[text];
            while i<len(lines)and lines[i].strip().startswith('|'):rows.append(lines[i].strip());i+=1
            parsed=[[c.strip() for c in row.strip('|').split('|')]for row in rows if not re.match(r'^\|[-:| ]+\|$',row)]
            table=d.add_table(rows=0,cols=len(parsed[0]));table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
            widths=[6.6]+[(16.2-6.6)/(len(parsed[0])-1)]*(len(parsed[0])-1) if len(parsed[0])==4 else ([2.1,8.3,5.8]if len(parsed[0])==3 and parsed[0][0]=='Código' else [16.2/len(parsed[0])]*len(parsed[0]))
            for col,width in zip(table.columns,widths):col.width=Cm(width)
            for ri,row in enumerate(parsed):
                cells=table.add_row().cells
                for ci,(c,value)in enumerate(zip(cells,row)):
                    c.width=Cm(widths[ci]);cellprops(c);p=c.paragraphs[0];p.paragraph_format.line_spacing=1.02;p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2)
                    if len(parsed)<15:p.paragraph_format.keep_with_next=ri<len(parsed)-1 and not (len(parsed)>9 and ri==5)
                    run=p.add_run(value);run.font.size=Pt(10.5);run.bold=ri==0
                    if ri==0:
                        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E9EEEB');c._tc.get_or_add_tcPr().append(shade)
                    if ci>0 and len(parsed[0])==4 and len(value)<30:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                cant=OxmlElement('w:cantSplit');table.rows[-1]._tr.get_or_add_trPr().append(cant)
                if ri==0:table.rows[-1]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            d.add_paragraph().paragraph_format.space_after=Pt(1);continue
        if text.startswith('# '):d.add_paragraph(text[2:],'Title');continue
        if text.startswith('## '):d.add_paragraph(text[3:],'Heading 1');continue
        if text.startswith('### '):d.add_paragraph(text[4:],'Heading 2');continue
        p=d.add_paragraph(text)
        if i<5:p.style='Subtitle'
        p.paragraph_format.widow_control=True
    dest.parent.mkdir(exist_ok=True,parents=True);d.save(dest);print(dest)

if __name__=='__main__':
    create(HERE/'material_tcc/Texto_e_tabelas.md',HERE/'material_tcc/Material_para_redacao_TCC.docx')
    create(HERE/'revisao_orientador/Roteiro_de_revisao.md',HERE/'revisao_orientador/Pacote_de_revisao.docx')
