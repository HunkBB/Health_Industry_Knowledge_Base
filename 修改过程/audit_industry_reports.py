import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='行业报告']
required=['## 一句话定位','## 一、本周发生了什么：事件台账','## 二、本周核心变化判断','## 三、对平台、药店、药企、用户的影响','## 四、下周需要继续跟踪什么','## 五、本周引用台账']
bad=[]; forbidden=[]
for d in items:
    p=Path(d['path']); t=p.read_text(encoding='utf-8')
    miss=[r for r in required if r not in t]
    if miss: bad.append((str(p),miss))
    if '使用边界' in t or '公开来源' in t: forbidden.append(str(p))
print({'行业报告':len(items),'模板缺失':len(bad),'禁用词':len(forbidden)})
print('bad',bad)
print('forbidden',forbidden)
