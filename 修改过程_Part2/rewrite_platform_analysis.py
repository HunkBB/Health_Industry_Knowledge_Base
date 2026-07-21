from pathlib import Path
import re
ROOT=next(p for p in Path('.').iterdir() if p.is_dir() and p.name.startswith('01-'))
START='<!-- READING_FRAMEWORK_START -->'; END='<!-- READING_FRAMEWORK_END -->'

def strip_sections_before_framework(text):
    start=text.find(START)
    head=text if start==-1 else text[:start]
    tail='' if start==-1 else text[start:]
    # Remove known source-card sections from original body before framework.
    cut_heads=['## 数据来源','## 资料主题','## 来源与引用口径','## 正式使用口径','## 可用于回答的问题','## 备注']
    pattern='|'.join(re.escape(h) for h in cut_heads+[START])
    for h in cut_heads:
        while h in head:
            s=head.find(h)
            m=re.search(r'\n## (?!数据来源|资料主题|来源与引用口径|正式使用口径|可用于回答的问题|备注)', head[s+1:])
            if m:
                e=s+1+m.start()
            else:
                e=len(head)
            head=head[:s].rstrip()+"\n\n"+head[e:].lstrip()
    # Remove duplicate original one-line positioning if it is generic source-card language.
    head=re.sub(r'## 一句话定位\s+本文定位为[^\n]+\n?', '', head, flags=re.S)
    return head.rstrip()+('\n\n' if tail else '')+tail

def kind(path):
    s=path.as_posix()
    if '美团' in s: return 'meituan'
    if '阿里' in s or '淘宝闪购' in s: return 'ali'
    if '京东' in s: return 'jd'
    return 'cross'

def analysis_block(path,title):
    k=kind(path)
    if k=='meituan':
        conclusion='这份文件的重点是把美团即时零售能力放到医药场景里看：美团不是单靠“买药”频道竞争，而是靠本地生活入口、骑手网络、药店供给和到家履约共同承接急用药需求。'
        qs=[('文件实际说明了什么？','它说明美团买药应被放在美团核心本地商业和即时配送能力中理解。文件中的业绩、闪购、到家和买药线索，本质上都指向一个问题：美团能否把高频本地生活用户转化成高确定性的购药用户。'),('从文件能推导出什么业务判断？','对药店来说，美团渠道的价值在于距离、库存和履约承诺；对药企来说，美团渠道的价值在于场景货架，尤其是急用、夜间、常备和轻问诊后的即时转化。'),('文件里哪些内容不能直接当结论？','如果文件中出现份额、订单、补贴、增长等描述，不能脱离美团公告和原始披露直接引用；这些内容适合做竞争信号，不适合单独作为最终判断。')]
    elif k=='ali':
        conclusion='这份文件的重点是解释阿里即时零售进入医药场景的路径：淘宝闪购负责流量触发，饿了么负责即时履约，阿里健康负责医药供给和健康服务。'
        qs=[('文件实际说明了什么？','它说明阿里医药即时零售不是单独的“淘宝闪购”问题，而是集团电商入口、本地履约网络和阿里健康供给能力的协同问题。'),('从文件能推导出什么业务判断？','阿里对美团的压力来自淘宝主站流量和电商心智，但医药场景能否跑通，还要看线下供给、药师服务、处方合规和履约稳定性。'),('文件里哪些口径必须拆开？','集团 Quick Commerce、淘宝闪购运营数据、饿了么履约能力和阿里健康收入不是同一口径；文件分析时必须分开，不然会把集团增长误读成医药品类增长。')]
    elif k=='jd':
        conclusion='这份文件的重点是解释京东在医药即时零售中的差异化：供应链、正品心智、京东健康服务能力和即时履约共同构成信任型购药入口。'
        qs=[('文件实际说明了什么？','它说明京东买药和京东秒送不能只按配送速度理解，还要放到京东健康的医药服务平台、自营药房、供应链和用户信任框架里看。'),('从文件能推导出什么业务判断？','京东更适合承接高信任、复购、慢病和健康服务相关需求；它未必在短期补贴声量上最强，但在正品心智和服务闭环上有分析价值。'),('文件里哪些内容需要谨慎？','京东秒送、京东买药、京东健康财务数据不是同一层级。文件如果把履约能力和医药健康收入放在一起，需要明确只是业务协同分析，不是同口径财务合并。')]
    else:
        conclusion='这份文件的重点是把美团、阿里、京东等平台放在同一张竞争框架里，比较入口、供给、履约、合规和经营机会，而不是给平台做简单排名。'
        qs=[('文件实际说明了什么？','它说明医药即时零售竞争不是单一维度竞争：美团强在本地生活和履约，阿里强在淘宝流量和生态协同，京东强在供应链和信任型医药服务。'),('从文件能推导出什么业务判断？','平台对药店和药企的价值不同：美团偏即时场景，阿里偏流量转化，京东偏信任和复购。业务选择平台时，应按品类场景拆分，而不是按平台声量押注。'),('文件里最需要避免的误读是什么？','不能把不同公司的财务口径、订单口径、媒体口径和研报口径混在一起比较；跨平台分析必须先统一维度，再讨论结论。')]
    source='''- [美团2026年Q1业绩公告](https://media-meituan.todayir.com/202606011753301715997254_en.pdf)
- [美团2025年度业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0326/2026032600964.pdf)
- [阿里巴巴2026财年业绩](https://home.alibabagroup.com/en-US/document-1991237455038119936)
- [阿里健康2026财年业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0514/2026051400755.pdf)
- [京东健康2025年报](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401364.pdf)
- [药品网络销售监督管理办法解读](https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html)'''
    qmd='\n\n'.join(f'### Q{i+1}：{q}\n\n{a}' for i,(q,a) in enumerate(qs))
    return f'''{START}

## 文件分析结论

{conclusion}

## 先读这几份公开原文

{source}

## 文件内容拆解

{qmd}

## 关键判断表

| 文件里的信息 | 应该怎么理解 | 可以形成的判断 |
|---|---|---|
| 平台入口 | 不是单纯入口数量，而是用户心智和触发场景 | 急用药、慢病复购、健康服务对应的平台选择不同 |
| 供给能力 | 不是只有药店数量，还包括库存、价格、药师和处方链路 | 药店合作深度决定即时零售能否从流量变成交易 |
| 履约能力 | 不是越快越好，而是时效、覆盖、夜间和售后稳定 | 急用药更依赖履约，慢病更依赖复购和服务 |
| 合规能力 | 医药即时零售必须叠加药监、处方和平台责任 | 合规能力是平台长期竞争门槛，不是后台成本 |

## 对团队的启示

- 这类文件应直接服务于平台选择、品类策略和竞对跟踪，而不是只做来源索引。
- 对药店：重点看平台能否带来确定性订单、合理毛利和稳定履约。
- 对药企：重点看平台是否能成为场景化触达入口，而不是单纯低价渠道。
- 对内部分析：后续每条平台动态都应落到“入口、供给、履约、合规、复购、补贴”六个指标上。

## 引用边界

- 财务和经营数据必须回到公司公告、年报、投资者关系材料。
- 药品网售、处方药、平台责任必须回到药监和监管原文。
- 媒体、研报和搜索摘要只能作为线索，不能替代原文。

{END}'''

changed=[]
for p in ROOT.rglob('*.md'):
    if p.name=='_index.md': continue
    t=p.read_text(encoding='utf-8',errors='replace')
    t=strip_sections_before_framework(t)
    title=''
    for line in t.splitlines():
        if line.startswith('#'):
            title=line.lstrip('#').strip().lstrip('\ufeff').strip(); break
    if not title: title=p.stem
    b=analysis_block(p,title)
    if START in t and END in t:
        nt=re.sub(re.escape(START)+r'[\s\S]*?'+re.escape(END),b,t)
    else:
        nt=t.rstrip()+'\n\n'+b
    if nt!=t:
        p.write_text(nt,encoding='utf-8')
        changed.append(p.as_posix())
print('changed',len(changed))
