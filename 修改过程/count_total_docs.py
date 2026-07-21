from pathlib import Path
import json, re
html = Path('行业信息库.html').read_text(encoding='utf-8', errors='ignore')
match = re.search(r'<script id="site-data" type="application/json">(.*?)</script>', html, re.S)
if not match:
    raise SystemExit('site-data not found')
data = json.loads(match.group(1))
docs = data['documents']
counts = {}
for doc in docs:
    counts[doc.get('contentType','')] = counts.get(doc.get('contentType',''), 0) + 1
print('total', len(docs))
for k,v in sorted(counts.items(), key=lambda kv: kv[0]):
    print(k, v)
