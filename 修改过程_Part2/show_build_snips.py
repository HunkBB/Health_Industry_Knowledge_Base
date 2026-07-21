from pathlib import Path
root=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
text=(root/'build_learning_site.py').read_text(encoding='utf-8', errors='ignore').splitlines()
for start,end in [(1,80),(520,620),(560,610),(2800,2860)]:
    print(f'--- lines {start}-{end} ---')
    for i in range(start-1,min(end,len(text))):
        print(f'{i+1}: {text[i]}')
