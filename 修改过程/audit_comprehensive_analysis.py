import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='综合分析']
required=['## 一、先讲清标题里的概念','## 二、事实与业务链路拆解','## 三、综合判断：哪些事实支持分析，哪些不能外推','## 四、平台、药店、药企/监管主体分别应该怎么看','## 五、需要关注指标/为什么','## 六、资料能证明什么/不能证明什么']
bad=[]; forbidden=[]
for d in items:
    p=Path(d['path']); t=p.read_text(encoding='utf-8')
    miss=[r for r in required if r not in t]
    if miss: bad.append((d['title'], miss))
    if '公开来源' in t or '使用边界' in t: forbidden.append(d['title'])
print({'综合分析':len(items),'结构缺失':len(bad),'禁用词':len(forbidden)})
print('bad',bad[:10])
print('forbidden',forbidden[:10])
p=Path('03-即时零售相关药企/补充资料/药企渠道布局_院内院外零售DTP电商O2O.md')
print('\n'.join(p.read_text(encoding='utf-8').splitlines()[:65]))
