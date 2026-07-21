from pathlib import Path
import re, json
h=Path('行业信息库.html').read_text(encoding='utf-8')
refs=sorted(set(re.findall(r'assets/[^"\'<>\\) ]+', h)))
print('asset refs', len(refs))
for r in refs[:50]: print(r)
missing=[]; total=0
for r in refs:
    p=Path(r)
    if p.exists(): total += p.stat().st_size
    else: missing.append(r)
print('missing', len(missing), 'used bytes', total)
