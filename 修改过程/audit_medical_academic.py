import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
for ct in sorted(set(d.get('contentType') for d in docs)):
    if '医' in str(ct):
        print('CONTENTTYPE', ct, sum(1 for d in docs if d.get('contentType')==ct))
print('--- medical docs')
for d in docs:
    if d.get('contentType') in ('医学基础','医药基础'):
        p=Path(d['path']); text=p.read_text(encoding='utf-8')
        html_hit=False
        print(('OK' if '学术解释' in text else 'MISS'), d['contentType'], d['title'], d['path'])
