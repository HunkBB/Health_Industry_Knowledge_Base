from pathlib import Path
p = Path('build_learning_site.py')
text = p.read_text(encoding='utf-8-sig')
old_css = ".curated-head { display:flex; align-items:flex-start; justify-content:space-between; gap:18px; margin-bottom:18px; }"
new_css = ".curated-head { margin-bottom:18px; }\n.curated-title-row { display:flex; align-items:center; justify-content:space-between; gap:18px; }"
text = text.replace(old_css, new_css)
old = '''            <div class="curated-head">
              <div>
                <h2>精选阅读路径</h2>
                <p>优先收录主要企业报告、官方/监管/财报/公告和权威来源资料。</p>
                ${inlineGroupLinks(issue, activeFilter)}
              </div>
              <span class="tag curated-time-tag">${curated.items.length}&nbsp;篇&nbsp;·&nbsp;约&nbsp;${Math.round(curated.total / 60 * 10) / 10}&nbsp;小时</span>
            </div>'''
new = '''            <div class="curated-head">
              <div class="curated-title-row">
                <h2>精选阅读路径</h2>
                <span class="tag curated-time-tag">${curated.items.length}&nbsp;篇&nbsp;·&nbsp;约&nbsp;${Math.round(curated.total / 60 * 10) / 10}&nbsp;小时</span>
              </div>
              <p>优先收录主要企业报告、官方/监管/财报/公告和权威来源资料。</p>
              ${inlineGroupLinks(issue, activeFilter)}
            </div>'''
if old not in text:
    raise SystemExit('target template block not found')
text = text.replace(old, new)
p.write_text(text, encoding='utf-8')
print('patched')
