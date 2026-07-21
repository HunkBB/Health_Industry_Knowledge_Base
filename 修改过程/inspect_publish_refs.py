from pathlib import Path
import re
h=Path('行业信息库.html').read_text(encoding='utf-8')
refs=sorted(set(re.findall(r'(?:src|href)="([^"]+)"', h)))
print('refs', len(refs))
for r in refs[:100]: print(r)
files=[p for p in Path('assets').rglob('*') if p.is_file()]
print('assets files', len(files), 'bytes', sum(p.stat().st_size for p in files))
