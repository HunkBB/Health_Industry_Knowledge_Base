import importlib.util, re
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='综合分析']
changed=0
for d in items:
    p=Path(d['path'])
    t=p.read_text(encoding='utf-8')
    m=re.search(r'\n## 六、不能下结论的部分为什么不能\n([\s\S]*)$', t)
    if m:
        bullets=m.group(1).strip()
        insert='\n### 4. 不能下结论的部分为什么不能\n\n'+bullets+'\n'
        marker='\n## 四、分类讨论：不同对象不能混在一起看\n'
        t=t[:m.start()]+'\n'
        t=t.replace(marker, insert+marker, 1)
        p.write_text(t.rstrip()+'\n', encoding='utf-8')
        changed+=1
print('merged section6 into section3',changed)
