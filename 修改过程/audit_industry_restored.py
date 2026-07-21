import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='行业报告']
checks=[]
for d in items:
    t=Path(d['path']).read_text(encoding='utf-8')
    checks.append(('new_depth' in t, '## 一、本周发生了什么：事件台账' in t, '## 四、需要关注指标/为什么' in t, '## 一、先讲清标题里的概念和关系' in t))
print({'行业报告':len(items),'有事件台账':sum(c[1] for c in checks),'有指标四节':sum(c[2] for c in checks),'有深度新版标题':sum(c[3] for c in checks)})
print('\n'.join(Path('05-行业机构/补充资料/米内网三大终端六大市场数据摘要.md').read_text(encoding='utf-8').splitlines()[:30]))
