import importlib.util, shutil
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='行业报告']
backup=Path('backup-before-industry-report-template-rewrite-20260618')
for d in items:
    src=Path(d['path'])
    dst=backup/src
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src,dst)
print('backed up',len(items),'files')
