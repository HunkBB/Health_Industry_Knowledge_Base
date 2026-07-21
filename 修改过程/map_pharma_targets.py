from pathlib import Path
import hashlib, json, re
root=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
sec=root/'03-即时零售相关药企'
mp=json.loads((root/'assets/doc_cards_web/doc_image_web_map.json').read_text(encoding='utf-8-sig'))
rows=[]
for p in sorted(sec.rglob('*.md')):
    if p.name=='_index.md': continue
    rel=p.relative_to(root).as_posix()
    stem=p.stem
    if stem.endswith('业务洞察'): continue
    if '研报摘要' in rel: continue
    text=p.read_text(encoding='utf-8', errors='ignore')
    title=next((line[2:].strip() for line in text.splitlines() if line.startswith('# ')), stem)
    doc_id='doc-'+hashlib.md5(rel.encode('utf-8')).hexdigest()[:12]
    image=mp.get(doc_id,'')
    rows.append({'doc_id':doc_id,'rel':rel,'title':title,'image':image,'exists': bool(image and (root/image).exists())})
print('COUNT', len(rows))
for r in rows:
    print('\t'.join([r['doc_id'], r['rel'], r['title'], r['image'], str(r['exists'])]))
(root/'tmp/pharma_card_targets.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
