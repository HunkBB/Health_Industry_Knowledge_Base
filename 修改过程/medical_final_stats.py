import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='医学基础']
for d in sorted(items, key=lambda x: len(Path(x['path']).read_text(encoding='utf-8'))):
    p=Path(d['path']); text=p.read_text(encoding='utf-8')
    missing=[h for h in ['## 一、准确解释：标题里的概念分别是什么','## 四、品类、咨询口径与即时零售场景','## 五、对平台、药店、药企的业务分析'] if h not in text]
    print(f"{len(text):5d} | missing={len(missing)} | {d['title']}")
