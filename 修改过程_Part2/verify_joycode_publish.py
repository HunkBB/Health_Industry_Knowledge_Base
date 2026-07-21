from pathlib import Path
import zipfile
zip_path=Path('.joycode/source-industry-info-library.zip')
with zipfile.ZipFile(zip_path) as z:
    names=z.namelist()
    print('zip entries', len(names))
    print('has index', 'index.html' in names)
    print('has main html', '行业信息库.html' in names)
    print('asset entries', sum(n.startswith('assets/') for n in names))
    print('first', names[:10])
for p in [Path('行业信息库.html'), Path('index.html'), Path('.joycode/source-industry-info-library.zip'), Path('output/joycode-publish')]:
    print(p, 'exists', p.exists(), 'size', p.stat().st_size if p.is_file() else '')
