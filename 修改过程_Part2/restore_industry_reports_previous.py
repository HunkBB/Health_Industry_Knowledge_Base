import shutil
from pathlib import Path
backup=Path('backup-before-industry-report-depth-rewrite-20260618')
if not backup.exists():
    raise SystemExit('missing backup')
files=list(backup.rglob('*.md'))
for src in files:
    rel=src.relative_to(backup)
    dst=Path(rel)
    if dst.exists():
        shutil.copy2(src,dst)
    else:
        raise SystemExit(f'target missing {dst}')
print('restored',len(files),'files')
