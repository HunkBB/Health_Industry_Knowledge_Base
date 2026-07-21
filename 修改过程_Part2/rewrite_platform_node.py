from pathlib import Path
import re
ROOT = next(p for p in Path('.').iterdir() if p.is_dir() and p.name.startswith('01-'))
START = '<!-- READING_FRAMEWORK_START -->'
END = '<!-- READING_FRAMEWORK_END -->'
SOURCES = {
    'meituan': ['[美团2026年Q1业绩公告](https://media-meituan.todayir.com/202606011753301715997254_en.pdf)','[美团2025年度业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0326/2026032600964.pdf)','[美团投资者业绩页](https://www.meituan.com/en-US/investor/results)','[药品网络销售监督管理办法解读](https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html)'],
    'ali': ['[阿里巴巴2026财年业绩](https://home.alibabagroup.com/en-US/document-1991237455038119936)','[阿里巴巴财务业绩页](https://home.alibabagroup.com/ir-financial-reports-financial-results)','[阿里健康2026财年业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0514/2026051400755.pdf)','[药品网络销售监督管理办法解读](https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html)'],
    'jd': ['[京东健康2025年报](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401364.pdf)','[京东健康2025年度业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0305/2026030500466.pdf)','[京东健康报告页](https://ir.jdhealth.com/en/ir_report.php)','[药品网络销售监督管理办法解读](https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html)'],
    'cross': ['[美团2026年Q1业绩公告](https://media-meituan.todayir.com/202606011753301715997254_en.pdf)','[阿里巴巴2026财年业绩](https://home.alibabagroup.com/en-US/document-1991237455038119936)','[京东健康2025年报](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401364.pdf)','[国务院即时配送行业指导意见](https://www.gov.cn/zhengce/zhengceku/202409/content_6974607.htm)','[药品网络销售监督管理办法解读](https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html)']
}
ANALYSES = {
    'meituan': {
        'conclusion': '美团的核心不是“有买药入口”，而是本地生活流量、骑手网络、药店供给和即时履约能否共同支撑急用药、夜间购药和慢病复购场景。',
        'qs': [('美团在医药即时零售的真实壁垒是什么？','不是“买药入口”本身，而是高频本地生活流量、骑手网络、药店覆盖和履约时效的组合。阅读美团材料时，要把闪购、即时配送和买药品类分开看，否则会把平台总能力误当成医药单品类能力。'),('对药店和药企有什么启示？','美团更适合承接即时性强、目的明确的需求，如退烧、止痛、肠胃、夜间急用和常备药补货。药店要关注门店在平台内的距离、库存、价格和配送承诺；药企要把即时零售当成场景货架，不是单纯电商货架。'),('最容易误读的地方是什么？','不要把媒体报道中的份额、单量或补贴表述直接当成经营结论。美团正式引用应以业绩公告、年报和投资者关系页为准。')]
    },
    'ali': {
        'conclusion': '阿里线索的关键是“淘宝流量 + 饿了么履约 + 阿里健康医药供给”能否连成闭环，而不能把 Quick Commerce 整体增长直接等同于医药即时零售成功。',
        'qs': [('阿里的竞争变量是什么？','核心不是“有没有闪购”，而是淘宝主站流量能多快转化成本地即时需求，以及医药健康品类能否在履约、药师和处方边界上跟上流量增长。'),('对美团的压力在哪里？','阿里的压力来自“电商心智 + 即时履约”的组合。对医药品类来说，这意味着平台可以在搜索、推荐、会员和跨品类场景中切入购药需求，但合规和供给密度仍是约束。'),('最需要分清的口径是什么？','阿里巴巴集团的 Quick Commerce 数据、淘宝闪购的运营数据和阿里健康的医药健康收入不能混用。正式引用必须指明是集团、本地生活还是阿里健康口径。')]
    },
    'jd': {
        'conclusion': '京东线索的核心是供应链、正品心智、医疗健康服务和即时履约的组合，不是单纯用补贴或时效和美团、阿里比拼。',
        'qs': [('京东的差异化在哪里？','京东差异化更像“自营供给 + 正品心智 + 医疗健康服务”。如果只看即时履约，会低估京东健康年报里的医药服务平台价值。'),('和平台即时零售的关系怎么看？','京东秒送、买药入口和京东健康并不是一个口径。阅读时要把“履约能力”和“医药健康业务收入”分开，再看两者能否在用户体验上闭环。'),('对业务的启示是什么？','京东更适合观察高信任品类、复购品类和健康服务连接。如果药企或连锁药店希望做长期信任和用户留存，京东线索的参考价值高于短期补贴数据。')]
    },
    'cross': {
        'conclusion': '跨平台对比的关键不是给美团、阿里、京东排名，而是用同一张表比较流量入口、药品供给、履约网络、合规能力和经营机会。',
        'qs': [('三方对比应该先看什么？','先看主体口径：美团是本地生活和即时配送，阿里是淘宝闪购/饿了么/阿里健康的协同，京东是京东健康/买药/秒送的组合。口径不同，数据不能直接横比。'),('平台补贴战应该怎么解读？','补贴是短期用户转化和商家供给的加速器，但不是长期壁垒。要看补贴后的留存、复购、药店收益和处方药合规成本，否则容易把营销投入看成经营能力。'),('合规边界为什么要单独拎出来？','医药即时零售不是普通即时零售。处方审核、药师服务、平台资质、禁售清单和履约留痕都会影响商业模式。比较平台时必须把合规能力纳入指标。')]
    }
}
def kind(file):
    s = file.as_posix()
    if '美团' in s: return 'meituan'
    if '阿里' in s or '淘宝闪购' in s: return 'ali'
    if '京东' in s: return 'jd'
    return 'cross'
def title_of(file, text):
    for line in text.splitlines():
        if line.startswith('#'):
            return line.lstrip('#').strip().lstrip('\ufeff').strip()
    return file.stem
def block(file, title):
    k = kind(file); a = ANALYSES[k]
    source_md = '\n'.join('- ' + x for x in SOURCES[k])
    q_md = '\n\n'.join(f'### Q{i+1}：{q}\n\n{ans}' for i,(q,ans) in enumerate(a['qs']))
    return f'''{START}

## 一句话定位

{title} 是一篇面向即时零售平台竞争的分析资料，重点用于判断平台动作背后的业务能力、经营变量和医药品类影响，而不是只记录信息来源。

## 一句话结论

{a['conclusion']}

## 先读这几份公开原文

{source_md}

## 核心问题与分析

{q_md}

## 关键数据/判断表

| 维度 | 读法 | 对业务的启示 |
|---|---|---|
| 流量入口 | 看平台是外卖/本地生活入口、淘宝电商入口还是医药健康入口 | 决定用户是“急用”还是“补货/复购”心智 |
| 供给能力 | 看自营、线下药店、健康仓、平台商家的组合 | 决定品类宽度、现货率和价格竞争力 |
| 履约体验 | 看配送时效、覆盖半径、骑手/配送网络和夜间服务 | 决定急用药、夜间购药和高时效品类的转化 |
| 合规能力 | 看处方审核、药师服务、平台资质和药品网售边界 | 决定处方药、DTP、慢病和医保场景能否放大 |

## 对团队的启示

- 不要只盯平台单量或补贴，要把平台竞争还原成“谁掌握用户入口、谁掌握供给、谁掌握履约和合规”。
- 医药品类的即时零售机会更像“场景运营”：急用药看时效，慢病看复购，处方药看合规和服务链路。
- 后续跟踪建议把每条动态落到指标：入口、药店数、配送时效、处方审核、药师服务、品类增长、补贴强度。

## 怎么使用这些资料

- 用于竞品追踪：把平台动作拆成流量入口、药品供给、履约时效、药店合作、处方/药师、补贴投入六类信号。
- 用于经营判断：先看平台能力是否能提升用户转化和复购，再判断对药店、药企和品类运营的影响。
- 用于汇报引用：财务、订单、业务描述和政策边界必须回到公告、年报、投资者关系页或监管原文。

## 引用边界

- 公司经营和财务数据以交易所公告、年报和投资者关系材料为准。
- 药品网络销售、处方药和平台责任以药监部门和现行政策原文为准。
- 媒体报道、研报和搜索摘要只能做线索，不能替代可回溯原文。

{END}'''
changed = []
for file in ROOT.rglob('*.md'):
    if file.name == '_index.md':
        continue
    text = file.read_text(encoding='utf-8', errors='replace')
    b = block(file, title_of(file, text))
    if START in text and END in text:
        new = re.sub(re.escape(START) + r'[\s\S]*?' + re.escape(END), b, text)
    else:
        new = text.rstrip() + '\n\n' + b
    if new != text:
        file.write_text(new, encoding='utf-8')
        changed.append(file.as_posix())
print('changed', len(changed))
