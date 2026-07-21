from pathlib import Path
p=Path('build_learning_site.py')
text=p.read_text(encoding='utf-8')
needle='@media (max-width:760px) {'
insert='''@media (max-width:760px) {\n.curated-subline { flex-direction:column; align-items:flex-start; gap:10px; }\n.curated-time-tag { margin-left:0; }'''
if insert not in text:
    text=text.replace(needle, insert, 1)
p.write_text(text,encoding='utf-8')
print('mobile patched')
