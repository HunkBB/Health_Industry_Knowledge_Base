from pathlib import Path
root=Path.cwd()
p=next(root.rglob('医药零售行业全景摘要_2025-2026.md'))
t=p.read_text(encoding='utf-8')
html=(root/'行业信息库.html').read_text(encoding='utf-8',errors='ignore')
terms=['TYPE_LEARNING_TEMPLATE','一句话结论','仅推测','未披露','未在本文摘录','回到原文','原文核验','﻿#']
print('md', {x:t.count(x) for x in terms if t.count(x)})
print('html has new phrase', '把用户需求、附近供给、专业服务' in html)
print('html old template', 'TYPE_LEARNING_TEMPLATE' in html)
