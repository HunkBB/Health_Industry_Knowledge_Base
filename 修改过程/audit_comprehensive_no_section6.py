import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='综合分析']
left=[]; bad=[]
required=['## 一、先讲清标题里的概念','## 二、事实与业务链路拆解','## 三、综合判断：哪些事实支持分析，哪些不能外推','## 四、平台、药店、药企/监管主体分别应该怎么看','## 五、需要关注指标/为什么']
for d in items:
    p=Path(d['path']); t=p.read_text(encoding='utf-8')
    if '## 六、资料能证明什么/不能证明什么' in t or '资料能证明什么/不能证明什么' in t:
        left.append(str(p))
    miss=[r for r in required if r not in t]
    if miss: bad.append((d['title'],miss))
print({'综合分析':len(items),'第六节残留':len(left),'结构缺失':len(bad)})
print('left',left[:10])
print('bad',bad[:10])
