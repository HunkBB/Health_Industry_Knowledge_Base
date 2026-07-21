import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='行业报告']
print(len(items))
for d in items:
    print(d['title'], '=>', d['path'])
