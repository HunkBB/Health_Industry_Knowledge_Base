from pathlib import Path
import re,json,importlib.util
ROOT=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
backup=ROOT/'backup-before-ui-review-template-sync-20260610-113612'/'行业信息库.html'
text=backup.read_text(encoding='utf-8', errors='replace')
data=json.loads(re.search(r'<script id="site-data" type="application/json">(.*?)</script>', text, re.S).group(1))
old_by_path={d['path']: d for d in data['documents']}
TEMPLATE_START='<!-- TYPE_LEARNING_TEMPLATE_START -->'
TEMPLATE_END='<!-- TYPE_LEARNING_TEMPLATE_END -->'

def split_template(current):
    if TEMPLATE_START not in current or TEMPLATE_END not in current:
        return ''
    return current.split(TEMPLATE_START,1)[1].split(TEMPLATE_END,1)[0]

def compact_template_block(block):
    # keep the learning top and verified links, but remove generic content sections that replaced real body
    keep=[]
    for sec in ['一句话定位','一句话结论','资料来源','已核验公开来源','可沉淀标签']:
        m=re.search(rf'(?ms)^## {re.escape(sec)}\s*\n.*?(?=^## |\Z)', block)
        if m: keep.append(m.group(0).strip())
    return TEMPLATE_START+'\n\n'+'\n\n'.join(keep)+'\n\n'+TEMPLATE_END

def title_line(raw, fallback):
    m=re.search(r'^#\s+(.+)$', raw, re.M)
    return m.group(0) if m else '# '+fallback

def remove_title_and_meta(raw):
    lines=raw.splitlines()
    if lines and lines[0].startswith('# '):
        lines=lines[1:]
    # keep old real content including blockquote; remove old official/framework markers just in case
    body='\n'.join(lines).strip()
    body=re.sub(r'(?ms)<!-- OFFICIAL_VERIFIED_SUMMARY_START -->.*?<!-- OFFICIAL_VERIFIED_SUMMARY_END -->\s*','',body)
    body=re.sub(r'(?ms)<!-- READING_FRAMEWORK_START -->.*?<!-- READING_FRAMEWORK_END -->\s*','',body)
    return body.strip()

changed=[]; missing=[]
for rel,dold in old_by_path.items():
    p=ROOT/rel
    if not p.exists():
        missing.append(rel); continue
    cur=p.read_text(encoding='utf-8', errors='replace')
    templ=compact_template_block(split_template(cur))
    raw=dold.get('rawText') or ''
    # rawText has no markdown links, but contains real facts; old html links are still not ideal. Use raw for content, current template has links.
    title=title_line(cur, dold.get('title') or p.stem)
    body=remove_title_and_meta(raw)
    new=(title+'\n\n'+templ+'\n\n---\n\n'+body).strip()+'\n'
    if new!=cur:
        p.write_text(new, encoding='utf-8')
        changed.append(rel)
print('restored',len(changed),'missing',len(missing))
for x in changed[:30]: print(x)
