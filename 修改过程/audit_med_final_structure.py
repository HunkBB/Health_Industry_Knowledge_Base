import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='医学基础']
bad=[]; banned=[]; merged=[]
for d in items:
    p=Path(d['path'])
    t=p.read_text(encoding='utf-8')
    if '### 0. 先讲清标题里的科学概念' not in t:
        bad.append(str(p))
    if '公开来源' in t or '使用边界' in t:
        banned.append(str(p))
    if '## 四、品类、咨询口径与即时零售场景' not in t:
        merged.append(str(p))
print({'医学基础':len(items),'缺概念块':len(bad),'含禁用词':len(banned),'缺四五合并结构':len(merged)})
print('bad', bad)
print('banned', banned)
print('merged', merged)
