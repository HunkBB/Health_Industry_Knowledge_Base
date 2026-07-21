from pathlib import Path
root=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
lines=(root/'build_learning_site.py').read_text(encoding='utf-8', errors='ignore').splitlines()
for start,end in [(1988,2048),(2020,2035)]:
    print(f'--- {start}-{end} ---')
    for i in range(start-1,min(end,len(lines))): print(f'{i+1}: {lines[i]}')
