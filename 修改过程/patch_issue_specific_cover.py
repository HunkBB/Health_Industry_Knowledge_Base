from pathlib import Path
p = Path('build_learning_site.py')
text = p.read_text(encoding='utf-8-sig')
old = '''function curatedCardHtml(item, issue) {
  const doc = item.doc;
  const reasonShort = (item.reason || '').replace('主要企业报告/权威材料：', '主要企业/权威材料：');
  const coverHtml = doc.coverImage ? `<img src="${esc(doc.coverImage)}" alt="" loading="lazy">` : '';
  return `<article class="curated-card">
    <button class="curated-art ${docArtClass(doc)} ${doc.coverImage ? 'has-cover' : ''}" data-icon="${esc(docArtIcon(doc))}" onclick="navigateDoc('${doc.id}')" aria-label="打开 ${esc(doc.title)}">${coverHtml}</button>'''
new = '''function issueSpecificCoverImage(doc, issue) {
  if (issue && issue.id === 'policy' && doc.id === 'doc-0800e61de0a4') {
    return 'assets/doc_cards_web/policy_20260617/doc-0800e61de0a4-policy.jpg';
  }
  return doc.coverImage || '';
}
function curatedCardHtml(item, issue) {
  const doc = item.doc;
  const reasonShort = (item.reason || '').replace('主要企业报告/权威材料：', '主要企业/权威材料：');
  const coverImage = issueSpecificCoverImage(doc, issue);
  const coverHtml = coverImage ? `<img src="${esc(coverImage)}" alt="" loading="lazy">` : '';
  return `<article class="curated-card">
    <button class="curated-art ${docArtClass(doc)} ${coverImage ? 'has-cover' : ''}" data-icon="${esc(docArtIcon(doc))}" onclick="navigateDoc('${doc.id}')" aria-label="打开 ${esc(doc.title)}">${coverHtml}</button>'''
if old not in text:
    raise SystemExit('target curatedCardHtml block not found')
text = text.replace(old, new)
p.write_text(text, encoding='utf-8')
print('patched')
