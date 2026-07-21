import importlib.util, re
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='医学基础']
print('医学基础 docs', len(items))
for d in items:
    p=Path(d['path'])
    t=p.read_text(encoding='utf-8')
    first=t.find('## 一、准确解释')
    zero=t.find('### 0. 先讲清标题里的科学概念')
    next_h2=t.find('\n## 二、', zero)
    block=t[zero:next_h2 if next_h2!=-1 else zero+800]
    ok = first != -1 and zero != -1 and first < zero and '公开来源' not in t and '使用边界' not in t
    print(('OK' if ok else 'BAD'), d['title'], 'concept_chars', len(block))
html=Path('行业信息库.html').read_text(encoding='utf-8')
print('html concept phrase count', html.count('先讲清标题里的科学概念'))
print('html 使用边界 count', html.count('使用边界'))
for title in ['结膜炎眼干眼部不适基础概念','肥胖与GLP1基础概念','失眠焦虑与药店咨询边界','儿童用药基础与药店咨询边界']:
    idx=html.find(title)
    after=html.find('先讲清标题里的科学概念', idx)
    print(title, 'title_in_html', idx!=-1, 'concept_after_title', after!=-1 and after > idx)
