from pathlib import Path
p=Path('tmp/rewrite_comprehensive_analysis.py')
t=p.read_text(encoding='utf-8')
start=t.find("    else:\n        channel_table = '| 分析对象")
end=t.find("    text = f'''", start)
replacement="""    else:
        channel_lines = ['| 分析对象 | 现实中看什么 | 为什么重要 | 不能下结论 |', '|---|---|---|---|']
        for a,b in rows[:4]:
            channel_lines.append(f'| {a} | 对应公开事实、业务动作和可跟踪指标 | {b} | 不能仅凭单一动作推出经营结果 |')
        channel_table = '\\n'.join(channel_lines) + '\\n'
"""
if start==-1 or end==-1:
    raise SystemExit('pattern not found')
t=t[:start]+replacement+t[end:]
p.write_text(t,encoding='utf-8')
print('patched')
