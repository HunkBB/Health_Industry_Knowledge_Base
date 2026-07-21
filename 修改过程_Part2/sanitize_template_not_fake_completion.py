from pathlib import Path
import importlib.util, re
ROOT=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
spec=importlib.util.spec_from_file_location('b', ROOT/'build_learning_site.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
docs,_=b.scan_documents()
START='<!-- TYPE_LEARNING_TEMPLATE_START -->'
END='<!-- TYPE_LEARNING_TEMPLATE_END -->'

def section(block, name):
    m=re.search(rf'(?ms)^## {re.escape(name)}\s*\n.*?(?=^## |\Z)', block)
    return m.group(0).strip() if m else ''

def sanitize_block(block):
    keep=[]
    for name in ['一句话定位','一句话结论','资料来源','已核验公开来源','可沉淀标签']:
        sec=section(block,name)
        if not sec: continue
        # remove fake completion phrases; keep concise learning framing and links only
        sec=sec.replace('本资料作为补充线索，用于连接六大板块的事实、观点和后续阅读路径。','本资料用于连接六大板块的事实、观点和后续阅读路径。')
        sec=sec.replace('已用[','参考[')
        sec=sec.replace('补齐核验入口；','提供公开核验入口；')
        sec=sec.replace('补齐财报核验路径；','提供财报核验路径；')
        sec=sec.replace('补齐行业背景入口；','提供行业背景入口；')
        sec=sec.replace('补齐事实核验入口；','提供事实核验入口；')
        sec=sec.replace('补齐医学核验入口；','提供医学核验入口；')
        sec=sec.replace('待核验','需核验')
        keep.append(sec)
    return START+'\n\n'+'\n\n'.join(keep)+'\n\n'+END

changed=[]
for d in docs:
    p=ROOT/d['path']
    t=p.read_text(encoding='utf-8', errors='replace')
    if START not in t or END not in t: continue
    before, rest=t.split(START,1)
    block, after=rest.split(END,1)
    new=before+sanitize_block(block)+after
    new=re.sub(r'\n{4,}','\n\n\n',new).strip()+'\n'
    if new!=t:
        p.write_text(new,encoding='utf-8')
        changed.append(d['path'])
print('changed',len(changed))
