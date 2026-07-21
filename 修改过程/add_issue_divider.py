from pathlib import Path
p=Path('build_learning_site.py')
text=p.read_text(encoding='utf-8')
css_anchor='.curated-section { margin-top: 30px; }'
css_new='.issue-hero-divider { width:min(680px, 72%); height:1px; margin:30px auto 0; background:rgba(17,24,39,.92); }\n.curated-section { margin-top: 30px; }'
if css_anchor not in text:
    raise SystemExit('css anchor not found')
text=text.replace(css_anchor, css_new, 1)
html_anchor='''            <div class="issue-hero-info">
              <p>${esc(issue.description || issue.subtitle || '')}</p>
            </div>
          </section>
          <section class="curated-section">'''
html_new='''            <div class="issue-hero-info">
              <p>${esc(issue.description || issue.subtitle || '')}</p>
            </div>
            <div class="issue-hero-divider" aria-hidden="true"></div>
          </section>
          <section class="curated-section">'''
if html_anchor not in text:
    raise SystemExit('html anchor not found')
text=text.replace(html_anchor, html_new, 1)
p.write_text(text,encoding='utf-8')
print('patched')
