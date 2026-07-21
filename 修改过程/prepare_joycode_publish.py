from pathlib import Path
import re, shutil, zipfile
root=Path('.')
html_src=root/'行业信息库.html'
index=root/'index.html'
index.write_text(html_src.read_text(encoding='utf-8'), encoding='utf-8')
# Make publish directory
publish=root/'output'/'joycode-publish'
if publish.exists():
    shutil.rmtree(publish)
publish.mkdir(parents=True)
# Copy html entrypoints
shutil.copy2(html_src, publish/'行业信息库.html')
shutil.copy2(index, publish/'index.html')
# Copy only actually referenced assets
h=html_src.read_text(encoding='utf-8')
refs=sorted(set(re.findall(r'assets/[^"\'<>\\) ]+', h)))
used_bytes=0
for r in refs:
    src=root/r
    dst=publish/r
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src,dst)
    used_bytes += src.stat().st_size
# Add a tiny README for deployers
(publish/'README_DEPLOY.txt').write_text('JoyCode发布包：入口 index.html；包含行业信息库.html 与实际引用的 assets。\n', encoding='utf-8')
zip_path=root/'.joycode'/'source-industry-info-library.zip'
zip_path.parent.mkdir(exist_ok=True)
if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in publish.rglob('*'):
        if p.is_file():
            z.write(p, p.relative_to(publish).as_posix())
print('index updated', index.stat().st_size)
print('used assets', len(refs), used_bytes)
print('publish files', sum(1 for p in publish.rglob('*') if p.is_file()))
print('publish bytes', sum(p.stat().st_size for p in publish.rglob('*') if p.is_file()))
print('zip', zip_path, zip_path.stat().st_size)
