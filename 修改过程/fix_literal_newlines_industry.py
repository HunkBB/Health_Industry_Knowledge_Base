import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='行业报告']
fixed=[]
for d in items:
    p=Path(d['path'])
    t=p.read_text(encoding='utf-8')
    if '\\n' in t:
        t=t.replace('\\n','\n')
        p.write_text(t,encoding='utf-8')
        fixed.append(str(p))
print('fixed literal newline files', len(fixed))
for f in fixed: print(f)
