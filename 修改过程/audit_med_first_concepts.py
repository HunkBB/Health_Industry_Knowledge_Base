import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='医学基础']
print('medical contentType',len(items))
for d in items:
    p=Path(d['path'])
    txt=p.read_text(encoding='utf-8')
    miss='### 0. 先讲清标题里的科学概念' not in txt
    first=txt.find('## 一、准确解释')
    zero=txt.find('### 0. 先讲清标题里的科学概念')
    one=txt.find('### 1.', first if first!=-1 else 0)
    wrong = zero!=-1 and first!=-1 and not (first < zero and (one==-1 or zero < one))
    if miss or wrong:
        print(('MISS' if miss else 'WRONG'), d['title'], p.as_posix())
