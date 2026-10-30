from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
out = root / 'writing_outputs' / 'Iris_Project_Report.docx'
qa = root / 'tmp' / 'iris-report-qa'
qa.mkdir(exist_ok=True, parents=True)
image = Image.new('RGB', (1500, 1100), 'white')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 32)
bold = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 34)

def box(bounds, title, body):
    draw.rounded_rectangle(bounds, radius=12, fill='#F2F4F6', outline='#41464B', width=3)
    x0,y0,x1,y1 = bounds
    draw.text(((x0+x1)/2,y0+15), title, font=bold, fill='black', anchor='mt')
    for n,line in enumerate(body):
        draw.text(((x0+x1)/2,y0+61+n*39), line, font=font, fill='black', anchor='mt')

def arrow(x,y0,y1):
    draw.line((x,y0,x,y1), fill='#41464B', width=4)
    draw.polygon([(x,y1),(x-10,y1-16),(x+10,y1-16)], fill='#41464B')

box((260,10,1240,120), 'USER', ['Face movement and speech'])
arrow(750,120,165)
box((260,165,1240,320), 'ESP32 CAM INPUT', ['OV3660 camera and INMP441 microphone', 'JPEG images and microphone PCM'])
arrow(750,320,395)
draw.text((775,339), 'Wi-Fi / WebSocket', font=font, fill='black')
box((160,395,1340,605), 'PYTHON HOST', ['OpenCV face detection and gaze mapping', 'Whisper speech recognition -> Ollama -> Coqui', 'Interaction state and playback amplitude'])
arrow(750,605,680)
draw.text((775,624), 'Controls and response audio', font=font, fill='black')
box((260,680,1240,795), 'ESP32 CAM OUTPUT CONTROL', ['Facial rendering and optional audio playback'])
draw.line((750,795,750,840,350,840,350,875),fill='#41464B',width=4)
draw.line((750,840,1150,840,1150,875),fill='#41464B',width=4)
arrow(350,855,875)
arrow(1150,855,875)
box((30,875,690,995), 'TFT DISPLAY', ['Animated eyes and mouth'])
box((810,875,1470,995), 'AUDIO OUTPUT', ['MAX98357A and speaker'])
draw.text((750,1045), 'Laptop microphone and speaker paths are also supported', font=font, fill='#41464B', anchor='mm')
fig = qa / 'block_diagram.png'
image.save(fig)

doc = Document()
sec = doc.sections[0]
sec.page_width,sec.page_height=Inches(8.27),Inches(11.69)
sec.top_margin=sec.bottom_margin=Inches(.7)
sec.left_margin=sec.right_margin=Inches(.8)
for name in ['Normal','Title','Heading 1','Caption']:
    s=doc.styles[name]
    s.font.name='Calibri'
    s.font.color.rgb=RGBColor(0,0,0)
normal=doc.styles['Normal']
normal.font.size=Pt(11)
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.line_spacing=1.07
doc.styles['Title'].font.size=Pt(22)
doc.styles['Title'].paragraph_format.space_after=Pt(12)
doc.styles['Heading 1'].font.size=Pt(14)
doc.styles['Heading 1'].paragraph_format.space_before=Pt(12)
doc.styles['Heading 1'].paragraph_format.space_after=Pt(6)
doc.styles['Caption'].font.size=Pt(9)
doc.styles['Caption'].font.italic=False
doc.core_properties.title='Iris Project Report'
doc.core_properties.subject='AI companion with face tracking and voice interaction'
doc.core_properties.author=''

def inline(p,text):
    pattern=r'(\*\*.*?\*\*|\[([^\]]+)\]\(([^)]+)\))'
    pos=0
    for m in re.finditer(pattern,text):
        p.add_run(text[pos:m.start()])
        if m.group(0).startswith('**'):
            p.add_run(m.group(0)[2:-2]).bold=True
        else:
            h=OxmlElement('w:hyperlink')
            rid=p.part.relate_to(m.group(3),'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
            h.set(qn('r:id'),rid)
            r=OxmlElement('w:r'); props=OxmlElement('w:rPr')
            u=OxmlElement('w:u');u.set(qn('w:val'),'single');props.append(u)
            r.append(props); t=OxmlElement('w:t');t.text=m.group(2);r.append(t);h.append(r);p._p.append(h)
        pos=m.end()
    p.add_run(text[pos:])

lines=(root/'writing_outputs'/'iris-project-report.md').read_text(encoding='utf-8-sig').splitlines()
i=0
while i<len(lines):
    line=lines[i]
    if not line.strip(): i+=1;continue
    if line.startswith('# '):
        doc.add_paragraph('Iris AI Companion Project Report', 'Title')
        p=doc.add_paragraph('Face tracking and voice interaction');p.paragraph_format.space_after=Pt(12)
    elif line.startswith('## '):
        title=line[3:]
        if title.startswith('Proposed Methodology') or title.startswith('Experimental Results'):doc.add_page_break()
        title=title.replace(' (With Block Diagram)','').replace(' (With Comparison)','')
        doc.add_paragraph(title,'Heading 1')
    elif line.startswith('```'):
        i+=1
        while i<len(lines) and not lines[i].startswith('```'):i+=1
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(fig),width=Inches(5.8))
        p.paragraph_format.keep_with_next=True
    elif line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            row=[c.strip() for c in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+',c) for c in row):rows.append(row)
            i+=1
        table=doc.add_table(rows=0,cols=len(rows[0]));table.alignment=WD_TABLE_ALIGNMENT.CENTER
        table.autofit=False
        widths=[2.1,4.5] if len(rows[0])==2 else [1.15,1.6,1.9,1.95]
        for col,w in zip(table.columns,widths):col.width=Inches(w)
        borders=OxmlElement('w:tblBorders')
        for edge in ['top','left','bottom','right','insideH','insideV']:
            e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
        table._tbl.tblPr.append(borders)
        for idx,row in enumerate(rows):
            cells=table.add_row().cells
            trpr=table.rows[-1]._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
            if idx==0:trpr.append(OxmlElement('w:tblHeader'))
            for cell,txt,w in zip(cells,row,widths):
                cell.width=Inches(w);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                pr=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E6EBEF' if idx==0 else ('F7F8F9' if idx%2==0 else 'FFFFFF'));pr.append(shade)
                margins=OxmlElement('w:tcMar')
                for side in ['top','bottom','left','right']:
                    e=OxmlElement('w:'+side);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');margins.append(e)
                pr.append(margins)
                p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.0
                run=p.add_run(txt);run.font.size=Pt(9.5);run.bold=idx==0
        doc.add_paragraph().paragraph_format.space_after=Pt(0)
        continue
    else:
        p=doc.add_paragraph(style='Caption' if line.startswith('**Figure') else 'Normal');inline(p,line)
        if line.startswith('['):p.paragraph_format.space_after=Pt(4);p.runs[0].font.size=Pt(10)
    i+=1
doc.save(out)
print(out)
print('Paragraphs:',len(doc.paragraphs),'Tables:',len(doc.tables))
