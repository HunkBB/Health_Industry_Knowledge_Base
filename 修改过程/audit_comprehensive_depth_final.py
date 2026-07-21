import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='综合分析']
required=['## 一、先讲清标题里的概念和关系','## 二、事实底座：目前能确定什么','## 三、业务机制拆解：为什么会这样','### 4. 不能下结论的部分为什么不能','## 四、分类讨论：不同对象不能混在一起看','## 五、需要关注指标/为什么','读表结论：']
bad=[]; forbidden=[]; shallow=[]
for d in items:
    t=Path(d['path']).read_text(encoding='utf-8')
    miss=[r for r in required if r not in t]
    if miss: bad.append((d['title'],miss))
    if '公开来源' in t or '使用边界' in t or '资料能证明什么/不能证明什么' in t or '## 六' in t: forbidden.append(d['title'])
    if t.count('具体例子：') < 3 or t.count('发生逻辑：') < 3: shallow.append(d['title'])
print({'综合分析':len(items),'结构缺失':len(bad),'禁用/第六节':len(forbidden),'例子不足':len(shallow)})
print('bad',bad[:5]); print('forbidden',forbidden[:5]); print('shallow',shallow[:5])
