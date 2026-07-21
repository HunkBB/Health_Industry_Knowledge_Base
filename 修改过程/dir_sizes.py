from pathlib import Path
root=Path('.')
items=[]
for p in root.iterdir():
    if p.is_file():
        size=p.stat().st_size
        count=1
    else:
        files=[f for f in p.rglob('*') if f.is_file()]
        size=sum(f.stat().st_size for f in files)
        count=len(files)
    items.append((size,count,p.name))
for size,count,name in sorted(items, reverse=True)[:30]:
    print(f'{size/1024/1024:8.2f} MB  {count:5d} files  {name}')
