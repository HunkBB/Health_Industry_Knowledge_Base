from pathlib import Path
p=Path('build_learning_site.py')
text=p.read_text(encoding='utf-8')
old='.issue-hero-divider { width:min(680px, 72%); height:1px; margin:30px auto 0; background:rgba(17,24,39,.92); }'
new='.issue-hero-divider { width:100%; height:1px; margin:42px auto 0; background:rgba(17,24,39,.92); }'
if old not in text:
    raise SystemExit('divider css not found')
text=text.replace(old,new,1)
p.write_text(text,encoding='utf-8')
print('patched')
