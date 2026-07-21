from pathlib import Path
for p in [Path('05-行业机构/本周行业变化.md'), Path('05-行业机构/补充资料/中康科技药品全终端市场回顾与展望.md'), Path('06-其他行业报告/医药零售行业全景摘要_2025-2026.md')]:
    print('---', p)
    text=p.read_text(encoding='utf-8')
    print('\n'.join(text.splitlines()[:25]))
