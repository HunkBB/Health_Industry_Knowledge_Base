import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='行业报告']
required=['## 一、先讲清标题里的概念和关系','## 二、事实底座：目前能确定什么','## 三、业务机制拆解：为什么会这样','## 四、分类讨论：不同对象不能混在一起看','## 五、需要关注指标/为什么']
bad=[]; forbidden=[]
for d in items:
    p=Path(d['path']); t=p.read_text(encoding='utf-8')
    miss=[r for r in required if r not in t]
    if miss: bad.append((d['title'],miss))
    if '公开来源' in t or '使用边界' in t or '## 六' in t: forbidden.append(d['title'])
print({'行业报告':len(items),'结构缺失':len(bad),'禁用/第六节':len(forbidden)})
print('bad',bad)
print('forbidden',forbidden)
for p in [Path('05-行业机构/补充资料/米内网三大终端六大市场数据摘要.md'), Path('05-行业机构/补充资料/O2O与B2C医药电商模式对比.md')]:
    print('\n---',p)
    print('\n'.join(p.read_text(encoding='utf-8').splitlines()[:50]))
