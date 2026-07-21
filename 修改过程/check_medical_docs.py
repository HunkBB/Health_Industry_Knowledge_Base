import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='医学基础']
print('医学基础数量',len(items))
required=['## 一句话定位','## 一、准确解释：三个概念分别是什么','## 二、药店咨询首先要问什么','## 三、轻症、需药师判断、应就医的分层','## 四、常见品类与药店咨询口径','## 五、即时零售医药场景拆解','## 六、对平台、药店、药企的业务分析']
for d in items:
    p=Path(d['path']); text=p.read_text(encoding='utf-8')
    missing=[r for r in required if r not in text]
    bad=[b for b in ['## 七、公开来源','## 公开来源','公开来源'] if b in text]
    print(d['title'],'|',len(text),'| missing',missing,'| bad',bad)
