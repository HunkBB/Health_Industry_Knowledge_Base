from pathlib import Path
root=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
text=(root/'build_learning_site.py').read_text(encoding='utf-8', errors='ignore').splitlines()
for i,line in enumerate(text,1):
    if 'def md5_id' in line or 'def is_public_industry_doc' in line or 'PUBLIC_CONTENT_PREFIXES' in line:
        print('FOUND', i, line)
        for j in range(max(1,i-8), min(len(text),i+30)+1):
            print(f'{j}: {text[j-1]}')
        print('---')
