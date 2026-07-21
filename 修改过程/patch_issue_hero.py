from pathlib import Path
p=Path('build_learning_site.py')
text=p.read_text(encoding='utf-8')
text=text.replace('"title": "疾病与医学基础",', '"title": "疾病与医学基础：常见疾病、重点病种和药事概念怎么理解",')
old_css='.issue-hero-centered h1 { margin:0; font-family:var(--serif); font-size:clamp(38px,4.2vw,58px); letter-spacing:-.04em; line-height:1.05; color:#102235; }\n.issue-hero-info { max-width:920px; margin:18px 0 0; text-align:left; }\n.issue-hero-info p { margin:0; color:#5b6672; font-size:18px; line-height:1.7; }\n.issue-answer-row { margin-top:14px; padding:15px 18px; border:1px solid rgba(15,111,127,.14); border-radius:18px; background:linear-gradient(135deg, rgba(255,255,255,.96), rgba(239,249,249,.78)); color:#314457; line-height:1.65; }\n.issue-answer-row strong { display:inline-flex; align-items:center; gap:6px; margin-right:6px; color:#102235; }'
new_css='.issue-hero-title { margin:0; font-family:var(--serif); color:#102235; letter-spacing:-.04em; line-height:1.05; }\n.issue-hero-title-main { display:block; font-size:clamp(38px,4.2vw,58px); }\n.issue-hero-title-sub { display:block; margin-top:8px; font-size:clamp(25px,2.9vw,42px); line-height:1.18; letter-spacing:-.035em; font-weight:700; }\n.issue-hero-info { max-width:920px; margin:18px 0 0; text-align:left; }\n.issue-hero-info p { margin:0; color:#5b6672; font-size:18px; line-height:1.7; }'
if old_css not in text:
    raise SystemExit('css block not found')
text=text.replace(old_css,new_css)
old_js='''  const answerText = issue.answer || issue.subtitle || '用于快速判断该板块的核心问题、资料入口和后续阅读路径。';
  document.getElementById('view-issue').innerHTML = `
    <section class="issue-page">
      <div class="issue-detail ui-review-issue accent-${esc(issue.accent)}">
        <main>
          <section class="issue-hero-centered">
            <h1>${esc(issue.title)}</h1>
            <div class="issue-hero-info">
              <p>${esc(issue.description || issue.subtitle || '')}</p>
              <div class="issue-answer-row"><strong>适合回答</strong>${esc(answerText)}</div>
            </div>
          </section>'''
new_js='''  const titleParts = String(issue.title || '').split('：');
  const titleMain = titleParts[0] || '';
  const titleSub = titleParts.slice(1).join('：');
  document.getElementById('view-issue').innerHTML = `
    <section class="issue-page">
      <div class="issue-detail ui-review-issue accent-${esc(issue.accent)}">
        <main>
          <section class="issue-hero-centered">
            <h1 class="issue-hero-title">
              <span class="issue-hero-title-main">${esc(titleMain)}${titleSub ? '：' : ''}</span>
              ${titleSub ? `<span class="issue-hero-title-sub">${esc(titleSub)}</span>` : ''}
            </h1>
            <div class="issue-hero-info">
              <p>${esc(issue.description || issue.subtitle || '')}</p>
            </div>
          </section>'''
if old_js not in text:
    raise SystemExit('js block not found')
text=text.replace(old_js,new_js)
p.write_text(text,encoding='utf-8')
print('patched')
