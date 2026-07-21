import importlib.util
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
news=[d for d in docs if d.get('contentType')=='公开新闻']
print(len(news))
for i,d in enumerate(news,1):
    print(f"{i}. {d['title']}")
    print(f"   {d['path']}")
