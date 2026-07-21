from pathlib import Path
import json, re
root = Path.cwd()
html = (root / '行业信息库.html').read_text(encoding='utf-8', errors='ignore')
match = re.search(r'<script id="site-data" type="application/json">(.*?)</script>', html, re.S)
if not match:
    raise SystemExit('site-data not found')
data = json.loads(match.group(1))
counts = {}
for doc in data['documents']:
    counts[doc['contentType']] = counts.get(doc['contentType'], 0) + 1
print(json.dumps(counts, ensure_ascii=False, indent=2))
others = [doc['path'] for doc in data['documents'] if doc['contentType'] == '其他']
print('other_count', len(others))
print('other_docs', json.dumps(others, ensure_ascii=False))
print('html_has_contenttype_other', '"contentType":"其他"' in html)
