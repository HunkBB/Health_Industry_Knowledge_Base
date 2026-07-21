from pathlib import Path
import json, re
html = Path('行业信息库.html').read_text(encoding='utf-8', errors='ignore')
match = re.search(r'<script id="site-data" type="application/json">(.*?)</script>', html, re.S)
if not match:
    raise SystemExit('site-data not found')
data = json.loads(match.group(1))
docs = data['documents']
items = [d for d in docs if d.get('contentType') == '综合分析']
print('综合分析篇数:', len(items))
for d in items:
    print(d['path'])
