from pathlib import Path
import importlib.util, re
ROOT=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
spec=importlib.util.spec_from_file_location('b', ROOT/'build_learning_site.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
docs,_=b.scan_documents()
TEMPLATE_START='<!-- TYPE_LEARNING_TEMPLATE_START -->'
TEMPLATE_END='<!-- TYPE_LEARNING_TEMPLATE_END -->'

def remove_source_card_before_template(text):
    if TEMPLATE_START not in text:
        return text
    before, after = text.split(TEMPLATE_START,1)
    # Preserve title and blockquote metadata at the top.
    m = re.match(r'(?s)^(# .+?\n(?:\n|>.*\n)*)', before)
    prefix = m.group(1).rstrip() if m else ''
    # Drop known source-card headings/sections before the template.
    rest = before[len(prefix):]
    for heading in ['一句话定位','数据来源','优先来源','备用来源','资料主题','来源与引用口径','正式使用口径','可用于回答的问题','备注']:
        rest = re.sub(rf'(?ms)^##?\s*{re.escape(heading)}\s*$.*?(?=^##?\s+|^---\s*$|\Z)', '', rest)
    # Drop separator-only leftovers before template.
    rest = re.sub(r'(?m)^---\s*$', '', rest).strip()
    # If there is meaningful original content before template, keep it after template later; usually source-card rest is empty.
    rebuilt = prefix + '\n\n' + TEMPLATE_START + after
    if rest:
        # keep non-boilerplate original content after the template block
        if TEMPLATE_END in rebuilt:
            rebuilt = rebuilt.replace(TEMPLATE_END, TEMPLATE_END + '\n\n' + rest, 1)
    return re.sub(r'\n{4,}', '\n\n\n', rebuilt).strip()+'\n'

changed=[]
for d in docs:
    p=ROOT/d['path']
    old=p.read_text(encoding='utf-8', errors='replace')
    new=remove_source_card_before_template(old)
    if new!=old:
        p.write_text(new, encoding='utf-8')
        changed.append(d['path'])
print('cleaned',len(changed))
for c in changed[:20]: print(c)
