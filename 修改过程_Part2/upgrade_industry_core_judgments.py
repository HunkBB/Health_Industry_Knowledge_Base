from pathlib import Path
root=Path.cwd()

section_judgments = {
'一、行业大盘：规模、增速与阶段': '行业大盘放缓不是单纯周期问题，而是增长来源发生了变化。过去药店依赖扩店、自然客流、医保红利和渠道价差获得增长，现在这些变量都在减弱；后续更应该验证存量需求如何被平台、连锁药店和药企重新分配，重点看店均产出、经营现金流、O2O订单毛利、慢病复购和专业服务收入，而不是只看市场规模。',
'二、渠道结构：线下、O2O、B2C、DTP分别怎么看': '渠道变化的本质是同一批购药需求被重新分配。O2O拿走的是急用、附近和夜间需求，B2C持续挤压标准化复购和价格敏感品类，DTP承接的是高专业度和高服务成本需求；药店真正要判断的不是要不要上线，而是哪些需求值得自己承接、哪些必须借助平台承接，以及线上订单是否带来真实毛利和复购。',
'三、品类结构：哪些品类托底，哪些品类增长': '品类机会不能只按高频和低频判断。药品占比提升说明刚需仍在，也说明非药和健康消费品在药店场景里的转化并不轻松；OTC适合即时零售，但如果只做价格和配送，会变成低毛利流量品。后续应验证品类毛利、连带购买、复购率、药师咨询转化和缺货率，而不是只看销售额。',
'四、关键矛盾：行业真正的问题是什么': '医药即时零售最难的不是上线，而是经济模型和服务模型能否同时成立。平台希望用即时履约提升频次，药店希望用O2O补足客流，药企希望获得近场触达，但三方都面临同一个问题：订单增长不等于利润增长，流量增加不等于专业服务增强。后续要看谁承担履约和服务成本、谁获得复购、谁沉淀用户关系。',
'五、对即时零售医药的启示': '如果即时零售医药只停留在“更快送药”，最终容易变成低毛利、高履约成本的流量生意。真正有价值的是把一次性急用药订单转化为家庭常备、慢病复购、药师咨询和会员关系；因此后续应重点验证用户是否复购、药店是否赚钱、药企是否获得场景数据，以及平台是否能把服务能力产品化。'
}

def upgrade_core_judgments(text):
    lines=text.splitlines()
    out=[]
    current=None
    i=0
    while i < len(lines):
        line=lines[i]
        if line.startswith('## '):
            title=line[3:].strip()
            current=title
            out.append(line)
            i+=1
            continue
        if line.startswith('**核心判断：**') and current in section_judgments:
            out.append('**核心判断：**' + section_judgments[current])
            # skip continuation lines until blank or next heading/table marker/list? Current generated judgments are one paragraph only.
            i+=1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('## ') and not lines[i].startswith('|') and not lines[i].startswith('- ') and not lines[i].startswith('**核心判断：**'):
                i+=1
            continue
        out.append(line)
        i+=1
    return '\n'.join(out).rstrip()+'\n'

changed=[]
for p in root.rglob('*.md'):
    rel=str(p.relative_to(root))
    if p.name=='_index.md': continue
    if rel.startswith('05-行业机构') or rel.startswith('06-其他行业报告'):
        t=p.read_text(encoding='utf-8')
        nt=upgrade_core_judgments(t)
        if nt!=t:
            p.write_text(nt,encoding='utf-8')
            changed.append(str(p.relative_to(root)))
print('changed',len(changed))
for x in changed: print(x)
