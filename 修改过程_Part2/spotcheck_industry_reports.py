from pathlib import Path
for p in [Path('05-行业机构/本周行业变化.md'), Path('05-行业机构/补充资料/O2O与B2C医药电商模式对比.md'), Path('06-其他行业报告/医药零售行业全景摘要_2025-2026.md')]:
    t=p.read_text(encoding='utf-8')
    print('\n---',p)
    print('\n'.join(t.splitlines()[:35]))
html=Path('行业信息库.html').read_text(encoding='utf-8')
checks=['本周发生了什么：事件台账','本周引用台账','O2O与B2C医药电商模式对比','医药零售行业全景摘要_2025-2026']
print('\nHTML checks', {c:(c in html) for c in checks})
print('HTML 使用边界 count', html.count('使用边界'))
