import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='行业报告']
bad=[]
for d in items:
    p=Path(d['path']); t=p.read_text(encoding='utf-8')
    checks={
        'concept':'### 0. 先讲清标题里的概念' in t,
        'new_four':'## 四、需要关注指标/为什么' in t,
        'old_four':'## 四、下周需要继续跟踪什么' not in t,
        'old_five':'## 五、本周引用台账' not in t,
        'two_cols':'| 需要关注指标 | 为什么 |' in t,
        'forbidden':'使用边界' not in t and '公开来源' not in t,
    }
    if not all(checks.values()): bad.append((d['title'], checks))
print({'行业报告':len(items),'问题数':len(bad)})
for x in bad: print(x)
