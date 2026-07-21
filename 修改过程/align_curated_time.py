from pathlib import Path
p=Path('build_learning_site.py')
text=p.read_text(encoding='utf-8')
old_css='.curated-time-tag { flex:0 0 auto; white-space:nowrap; line-height:1; }'
new_css='.curated-time-tag { flex:0 0 auto; white-space:nowrap; line-height:1; align-self:center; margin-left:18px; }\n.curated-subline { display:flex; align-items:baseline; justify-content:space-between; gap:18px; margin-top:12px; }\n.curated-subline p { margin:0; flex:1 1 auto; }'
if old_css not in text:
    raise SystemExit('css target not found')
text=text.replace(old_css,new_css)
old='''              <div class="curated-title-row">
                <h2>精选阅读路径</h2>
                <span class="tag curated-time-tag">${curated.items.length}&nbsp;篇&nbsp;·&nbsp;约&nbsp;${Math.round(curated.total / 60 * 10) / 10}&nbsp;小时</span>
              </div>
              <p>优先收录主要企业报告、官方/监管/财报/公告和权威来源资料。</p>'''
new='''              <div class="curated-title-row">
                <h2>精选阅读路径</h2>
              </div>
              <div class="curated-subline">
                <p>优先收录主要企业报告、官方/监管/财报/公告和权威来源资料。</p>
                <span class="tag curated-time-tag">${curated.items.length}&nbsp;篇&nbsp;·&nbsp;约&nbsp;${Math.round(curated.total / 60 * 10) / 10}&nbsp;小时</span>
              </div>'''
if old not in text:
    raise SystemExit('html target not found')
text=text.replace(old,new)
p.write_text(text,encoding='utf-8')
print('patched')
