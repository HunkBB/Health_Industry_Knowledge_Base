import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
rows=['标题,路径,contentType,Markdown含学术解释,HTML含学术解释']
html=Path('行业信息库.html').read_text(encoding='utf-8') if Path('行业信息库.html').exists() else ''
for d in docs:
    if d.get('contentType') in ('医学基础','医药基础'):
        p=Path(d['path']); text=p.read_text(encoding='utf-8')
        rows.append('"{}","{}",{}, {}, {}'.format(d['title'], d['path'], d['contentType'], '是' if '学术解释' in text else '否', '是' if (d['title'] in html and '学术解释' in html[html.find(d['title']):html.find(d['title'])+5000]) else '否'))
Path('output/医学基础学术解释核查清单.csv').write_text('\n'.join(rows),encoding='utf-8')
print('wrote output/医学基础学术解释核查清单.csv')
