from pathlib import Path
import re, json
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
sec = root / '03-即时零售相关药企'
img_re = re.compile(r'!\[[^\]]*\]\(([^)]+)\)|<img[^>]+src=["\']([^"\']+)["\']', re.I)
rows = []
for p in sorted(sec.rglob('*.md')):
    text = p.read_text(encoding='utf-8', errors='ignore')
    title = ''
    for line in text.splitlines():
        if line.startswith('# '):
            title = line[2:].strip()
            break
    imgs = [m.group(1) or m.group(2) for m in img_re.finditer(text)]
    rows.append({'file': str(p.relative_to(root)), 'title': title, 'images': imgs})
print(json.dumps(rows, ensure_ascii=False, indent=2))
