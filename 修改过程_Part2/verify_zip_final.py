from pathlib import Path
import zipfile, hashlib
zip_path=Path('.joycode/source-industry-info-library.zip')
files=['index.html','行业信息库.html','build_learning_site.py']
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
with zipfile.ZipFile(zip_path) as z:
    names=set(z.namelist())
    print('zip exists', zip_path.exists(), 'size', zip_path.stat().st_size, 'entries', len(names))
    for f in files:
        in_zip=f in names
        disk_hash=sha_file(f) if Path(f).exists() else None
        zip_hash=sha_bytes(z.read(f)) if in_zip else None
        print(f, {'in_zip':in_zip,'disk_hash':disk_hash,'zip_hash':zip_hash,'match':disk_hash==zip_hash})
    # representative changed docs
    reps=[
      '03-即时零售相关药企/补充资料/药企渠道布局_院内院外零售DTP电商O2O.md',
      '01-即时零售平台/竞争雷达_美团阿里京东.md',
      '08-疾病与医学基础/补充资料/结膜炎眼干眼部不适基础概念.md',
      '05-行业机构/补充资料/米内网三大终端六大市场数据摘要.md'
    ]
    for f in reps:
        disk_hash=sha_file(f)
        zip_hash=sha_bytes(z.read(f)) if f in names else None
        txt=z.read(f).decode('utf-8') if f in names else ''
        print(f, {'in_zip':f in names,'match':disk_hash==zip_hash,'has_final_markers': all(s in txt for s in ['一句话定位'])})
