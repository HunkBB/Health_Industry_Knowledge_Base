from pathlib import Path
for p in [Path('05-行业机构/中康科技/中康科技-公开报告与数据摘要.md'), Path('05-行业机构/补充资料/O2O与B2C医药电商模式对比.md'), Path('05-行业机构/补充资料/商务部研究院即时零售行业发展报告摘要.md'), Path('05-行业机构/西普会/西普会-内容摘要.md')]:
    t=p.read_text(encoding='utf-8')
    print('\n---',p)
    print('\n'.join(t.splitlines()[:45]))
