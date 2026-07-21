from pathlib import Path
import re,json,html
from html.parser import HTMLParser
ROOT=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
backup=ROOT/'backup-before-ui-review-template-sync-20260610-113612'/'行业信息库.html'
data=json.loads(re.search(r'<script id="site-data" type="application/json">(.*?)</script>', backup.read_text(encoding='utf-8', errors='replace'), re.S).group(1))
START='<!-- TYPE_LEARNING_TEMPLATE_START -->'; END='<!-- TYPE_LEARNING_TEMPLATE_END -->'

class MDParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out=[]; self.href=None; self.in_li=False; self.table=[]; self.row=[]; self.cell=[]; self.in_cell=False; self.in_tr=False
    def emit(self,s): self.out.append(s)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in ['h1','h2','h3','h4']:
            self.emit('\n\n'+'#'*int(tag[1])+' ')
        elif tag=='p': self.emit('\n\n')
        elif tag=='blockquote': self.emit('\n')
        elif tag=='li': self.emit('\n- '); self.in_li=True
        elif tag in ['strong','b']: self.emit('**')
        elif tag in ['em','i']: self.emit('*')
        elif tag=='a': self.href=attrs.get('href')
        elif tag=='br': self.emit('\n')
        elif tag=='tr': self.row=[]; self.in_tr=True
        elif tag in ['td','th']: self.cell=[]; self.in_cell=True
    def handle_endtag(self, tag):
        if tag in ['h1','h2','h3','h4','p','ul','ol','blockquote']:
            self.emit('\n')
        elif tag=='li': self.in_li=False
        elif tag in ['strong','b']: self.emit('**')
        elif tag in ['em','i']: self.emit('*')
        elif tag=='a': self.href=None
        elif tag in ['td','th']:
            self.row.append(''.join(self.cell).strip())
            self.cell=[]; self.in_cell=False
        elif tag=='tr':
            if self.row: self.table.append(self.row)
            self.in_tr=False
        elif tag=='table':
            self.emit('\n\n')
            if self.table:
                width=max(len(r) for r in self.table)
                for idx,r in enumerate(self.table):
                    r=r+['']*(width-len(r))
                    self.emit('| '+' | '.join(c.replace('\n',' ').strip() for c in r)+' |\n')
                    if idx==0: self.emit('| '+' | '.join(['---']*width)+' |\n')
            self.table=[]
            self.emit('\n')
    def handle_data(self,data):
        s=data.replace('\xa0',' ')
        if self.href:
            txt=s.strip()
            if txt:
                rendered=f'[{txt}]({self.href})'
                if self.in_cell: self.cell.append(rendered)
                else: self.emit(rendered)
            return
        if self.in_cell: self.cell.append(s)
        else: self.emit(s)
    def markdown(self):
        text=''.join(self.out)
        text=re.sub(r'[ \t]+\n','\n',text)
        text=re.sub(r'\n{3,}','\n\n',text)
        return text.strip()

def html_to_md(h):
    parser=MDParser(); parser.feed(h); return parser.markdown()

def compact_template(cur):
    if START in cur and END in cur:
        return START+cur.split(START,1)[1].split(END,1)[0]+END
    return ''
changed=[]
for d in data['documents']:
    p=ROOT/d['path']
    if not p.exists(): continue
    cur=p.read_text(encoding='utf-8', errors='replace')
    templ=compact_template(cur)
    md=html_to_md(d['html'])
    # remove duplicate h1 from old html, use current title first line
    lines=md.splitlines()
    if lines and lines[0].startswith('# '):
        body='\n'.join(lines[1:]).strip()
    else: body=md
    title=cur.splitlines()[0] if cur.startswith('# ') else '# '+d['title']
    new=(title+'\n\n'+templ+'\n\n---\n\n'+body).strip()+'\n'
    if new!=cur:
        p.write_text(new,encoding='utf-8')
        changed.append(d['path'])
print('html-restored',len(changed))
