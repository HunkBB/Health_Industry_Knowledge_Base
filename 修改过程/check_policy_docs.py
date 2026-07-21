import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='政策监管']
print('政策监管数量',len(items))
required=['## 一句话定位','## 一、','## 二、核心问题拆解','## 三、对即时零售医药的影响','## 四、使用边界']
bad_terms=['## 二、关键判断','## 四、对即时零售医药的业务分析','    ##','    >']
for d in items:
    p=Path(d['path']); text=p.read_text(encoding='utf-8')
    missing=[r for r in required if r not in text]
    bad={t:text.count(t) for t in bad_terms if text.count(t)}
    print(d['title'],'|',len(text),'| missing',missing,'| bad',bad)
