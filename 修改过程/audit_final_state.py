import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
summary={}
for ct in ['综合分析','医学基础','行业报告']:
    items=[d for d in docs if d.get('contentType')==ct]
    summary[ct]=len(items)
print('content types',summary)
# audits
comp=[d for d in docs if d.get('contentType')=='综合分析']
med=[d for d in docs if d.get('contentType')=='医学基础']
ind=[d for d in docs if d.get('contentType')=='行业报告']
print('综合分析 final', {
 'count':len(comp),
 'missing_depth':sum('## 三、业务机制拆解：为什么会这样' not in Path(d['path']).read_text(encoding='utf-8') for d in comp),
 'has_section6':sum('## 六' in Path(d['path']).read_text(encoding='utf-8') for d in comp),
 'has_forbidden':sum(('公开来源' in Path(d['path']).read_text(encoding='utf-8') or '使用边界' in Path(d['path']).read_text(encoding='utf-8')) for d in comp)
})
print('医学基础 final', {
 'count':len(med),
 'missing_concept0':sum('### 0. 先讲清标题里的科学概念' not in Path(d['path']).read_text(encoding='utf-8') for d in med),
 'has_forbidden':sum(('公开来源' in Path(d['path']).read_text(encoding='utf-8') or '使用边界' in Path(d['path']).read_text(encoding='utf-8')) for d in med)
})
print('行业报告 restored', {
 'count':len(ind),
 'has_event_ledger':sum('## 一、本周发生了什么：事件台账' in Path(d['path']).read_text(encoding='utf-8') for d in ind),
 'has_deep_title_version':sum('## 一、先讲清标题里的概念和关系' in Path(d['path']).read_text(encoding='utf-8') for d in ind)
})
html=Path('行业信息库.html').read_text(encoding='utf-8')
print('html size/hash markers', {'docs':len(docs),'业务机制': '业务机制拆解：为什么会这样' in html, '使用边界':'使用边界' in html})
