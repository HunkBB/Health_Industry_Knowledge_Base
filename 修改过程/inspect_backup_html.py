from pathlib import Path
import re,json
text=Path('backup-before-ui-review-template-sync-20260610-113612/行业信息库.html').read_text(encoding='utf-8', errors='replace')
m=re.search(r'<script id="site-data" type="application/json">(.*?)</script>', text, re.S)
data=json.loads(m.group(1))
print(data.keys())
print(len(data.get('documents',[])))
d=data['documents'][0]
print(d.keys())
print(d['path'])
print(d['html'][:500])
