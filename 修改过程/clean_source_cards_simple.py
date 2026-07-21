from pathlib import Path
import importlib.util, re
ROOT=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
spec=importlib.util.spec_from_file_location('b', ROOT/'build_learning_site.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
docs,_=b.scan_documents()
MARK='<!-- TYPE_LEARNING_TEMPLATE_START -->'
changed=[]
for d in docs:
    p=ROOT/d['path']
    old=p.read_text(encoding='utf-8', errors='replace')
    if MARK not in old:
        continue
    before, after = old.split(MARK, 1)
    lines=before.splitlines()
    keep=[]
    if lines and lines[0].startswith('# '):
        keep.append(lines[0])
        idx=1
        # keep blank and blockquote metadata immediately after title
        while idx < len(lines):
            line=lines[idx]
            if line.strip()=='' or line.startswith('>'):
                keep.append(line); idx+=1; continue
            break
    else:
        idx=0
    prefix='\n'.join(keep).rstrip()
    new=(prefix+'\n\n'+MARK+after).strip()+'\n'
    if new!=old:
        p.write_text(new, encoding='utf-8')
        changed.append(d['path'])
print('cleaned',len(changed))
for c in changed[:20]: print(c)
