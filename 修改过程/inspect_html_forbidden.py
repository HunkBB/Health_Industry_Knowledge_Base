from pathlib import Path
h=Path('行业信息库.html').read_text(encoding='utf-8')
for term in ['公开来源','使用边界']:
    print('TERM',term,'count',h.count(term))
    idx=h.find(term)
    print(h[max(0,idx-300):idx+300] if idx!=-1 else 'none')
