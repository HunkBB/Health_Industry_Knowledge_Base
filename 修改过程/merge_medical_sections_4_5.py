from pathlib import Path
import re

def split_sections(text):
    matches=list(re.finditer(r'^## [一二三四五六七八九十]+、.*$', text, re.M))
    out=[]
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(text)
        out.append((m.group(0), m.start(), end, text[m.start():end].strip()))
    return out

def merge_file(p):
    text=p.read_text(encoding='utf-8')
    if '## 四、品类、咨询口径与即时零售场景' in text:
        return False
    if '## 四、常见品类与药店咨询口径' not in text or '## 五、即时零售医药场景拆解' not in text or '## 六、对平台、药店、药企的业务分析' not in text:
        return False
    s4=text.index('## 四、常见品类与药店咨询口径')
    s5=text.index('## 五、即时零售医药场景拆解')
    s6=text.index('## 六、对平台、药店、药企的业务分析')
    before=text[:s4].rstrip()
    sec4=text[s4:s5]
    sec5=text[s5:s6]
    after=text[s6:].replace('## 六、对平台、药店、药企的业务分析','## 五、对平台、药店、药企的业务分析',1)
    # extract rows from both tables (simple markdown rows excluding header/separator)
    def rows(sec):
        rs=[]
        for line in sec.splitlines():
            if line.startswith('|') and not line.startswith('|---') and not ('品类/服务' in line or '场景 | 用户需求' in line):
                parts=[x.strip() for x in line.strip('|').split('|')]
                if len(parts)>=3: rs.append(parts[:3])
        return rs
    r4=rows(sec4); r5=rows(sec5)
    merged=[]
    maxn=max(len(r4),len(r5))
    for i in range(maxn):
        a=r4[i] if i<len(r4) else ['药师咨询','用户不确定用药边界','做风险分层和就医提醒']
        b=r5[i] if i<len(r5) else ['咨询/复购','需要药师解释或持续服务','药师在线、复诊提醒']
        merged.append(f"| {a[0]} | {b[0]}：{b[1]} | {a[2]} | {b[2]} |")
    block='''## 四、品类、咨询口径与即时零售场景\n\n| 品类/服务 | 对应场景 | 药师提醒点 | 平台/药店承接点 |\n|---|---|---|---|\n'''+'\n'.join(merged)+'\n\n'
    p.write_text(before+'\n\n'+block+after.lstrip(), encoding='utf-8')
    return True

changed=[]
for p in Path('08-疾病与医学基础').rglob('*.md'):
    if merge_file(p): changed.append(str(p))
print('merged',len(changed))
print('\n'.join(changed))
