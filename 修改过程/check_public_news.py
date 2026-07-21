import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
news=[d for d in docs if d.get('contentType')=='公开新闻']
print('contentType公开新闻',len(news))
terms=['药品网络销售与平台合作边界','药品网络销售监管持续适用','## 六、','事实底座','关键判断','后续跟踪']
for d in news:
    p=Path(d['path']); text=p.read_text(encoding='utf-8')
    missing=[h for h in ['## 一句话定位','## 一、年度新闻主线','## 二、关键事件拆解','## 三、从新闻中读出的变化','## 四、对即时零售医药的具体影响','## 五、仍不能下结论的事项'] if h not in text]
    bad={t:text.count(t) for t in terms if text.count(t)}
    print(d['title'],'|',len(text),'| missing',missing,'| bad',bad)
