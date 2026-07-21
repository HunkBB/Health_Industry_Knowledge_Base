from pathlib import Path
import re
head_re = re.compile(r'^## [一二三四五六七八九十]+、.*$', re.M)
remove_titles = {'使用边界'}
changed=[]
for p in Path('.').rglob('*.md'):
    if any(part.startswith('backup-') for part in p.parts):
        continue
    text=p.read_text(encoding='utf-8', errors='ignore')
    original=text
    matches=list(head_re.finditer(text))
    for m in reversed(matches):
        title=m.group(0).split('、',1)[1].strip()
        if title in remove_titles:
            end=len(text)
            for n in matches:
                if n.start()>m.start():
                    end=n.start()
                    break
            text=text[:m.start()].rstrip()+"\n\n"+text[end:].lstrip()
    if text!=original:
        p.write_text(text.rstrip()+"\n", encoding='utf-8')
        changed.append(str(p))
print('\n'.join(changed))
print('changed',len(changed))
