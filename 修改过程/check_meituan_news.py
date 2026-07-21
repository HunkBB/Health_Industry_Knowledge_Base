from pathlib import Path
html=Path('行业信息库.html').read_text(encoding='utf-8',errors='ignore')
print('has new meituan', '美团买药的真实价值不是“把药送得更快”' in html)
print('old meituan template', '涉及的主体动作、事件变化和后续影响' in html)
