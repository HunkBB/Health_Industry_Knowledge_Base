import importlib.util
spec=importlib.util.spec_from_file_location('site','build_learning_site.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
docs,_=mod.scan_documents()
items=[d for d in docs if d.get('contentType')=='政策监管']
print(len(items))
for i,d in enumerate(items,1):
    print(f"{i}. {d['title']}")
    print(f"   {d['path']}")
