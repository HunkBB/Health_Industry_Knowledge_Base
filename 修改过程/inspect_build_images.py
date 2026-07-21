from pathlib import Path
root=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
for p in [root/'build_learning_site.py', root/'build_site.py']:
    print('\n---', p.name, '---')
    text=p.read_text(encoding='utf-8', errors='ignore')
    for i,line in enumerate(text.splitlines(),1):
        if any(k in line for k in ['doc-card','doc_card','hero','cover','imagegen','assets','thumbnail','thumb','card-image','cardImage']):
            print(f'{i}: {line[:220]}')
