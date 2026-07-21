from pathlib import Path
p=Path('build_learning_site.py')
text=p.read_text(encoding='utf-8')
old='.issue-hero-title { margin:0; font-family:var(--serif); color:#102235; letter-spacing:-.04em; line-height:1.05; }'
new='.issue-hero-title { display:block; margin:0; font-family:var(--serif); color:#102235; letter-spacing:-.04em; line-height:1.05; }'
if old not in text:
    raise SystemExit('target css not found')
text=text.replace(old,new)
p.write_text(text,encoding='utf-8')
print('patched')
