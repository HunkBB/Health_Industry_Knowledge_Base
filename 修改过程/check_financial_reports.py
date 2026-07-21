from pathlib import Path
import re
root=Path.cwd()
html=(root/'行业信息库.html').read_text(encoding='utf-8',errors='replace')
bad_terms=['????','�','来源与引用口径','正式使用口径','可用于回答的问题','需要结合公开来源继续核验']
print('html bad', {x:html.count(x) for x in bad_terms if html.count(x)})
for phrase in ['华润三九2025-2026财报与渠道机会摘要','本文通过美团FY2025全年和2026Q1业绩材料','连锁药店行业已经从“门店数量竞争”']:
    print('has', phrase[:12], phrase in html)
files=[p for p in root.rglob('*.md') if re.search('财报|业绩|年度报告|Q1|FY2025|FY2026', str(p))]
print('financial files',len(files))
for p in files:
    print(p.relative_to(root))
