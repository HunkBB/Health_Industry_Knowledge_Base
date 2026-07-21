from pathlib import Path
import re

ROOT = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
PLATFORM = next(p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith('01-'))

SOURCES = {
    'meituan': [
        ('美团2026年Q1业绩公告', 'https://www.meituan.com/en-US/investor/results'),
        ('美团2025年度业绩公告', 'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0326/2026032600964.pdf'),
        ('药品网络销售监管解读', 'https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html'),
    ],
    'ali': [
        ('阿里巴巴FY2026业绩', 'https://home.alibabagroup.com/en-US/document-1991237455038119936'),
        ('阿里健康2026财年业绩公告', 'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0514/2026051400755.pdf'),
        ('药品网络销售监管解读', 'https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html'),
    ],
    'jd': [
        ('京东健康2025年度业绩公告', 'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0305/2026030500466.pdf'),
        ('京东健康2025年报', 'https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401364.pdf'),
        ('京东健康IR报告页', 'https://ir.jdhealth.com/en/ir_report.php'),
    ],
    'policy': [
        ('药品网络销售监管解读', 'https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html'),
        ('即时配送高质量发展指导意见', 'https://www.gov.cn/zhengce/zhengceku/202409/content_6974607.htm'),
        ('京东健康2025年报', 'https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401364.pdf'),
    ],
    'cross': [
        ('美团投资者关系', 'https://www.meituan.com/en-US/investor/results'),
        ('阿里巴巴FY2026业绩', 'https://home.alibabagroup.com/en-US/document-1991237455038119936'),
        ('京东健康IR报告页', 'https://ir.jdhealth.com/en/ir_report.php'),
        ('药品网络销售监管解读', 'https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/zhcjd/zhcjdyp/20220905151909197.html'),
    ],
}

def source_lines(kind):
    return '\n'.join(f'- [{name}]({url})' for name, url in SOURCES[kind])

def title_of(text, path):
    m = re.search(r'^#\s+(.+)$', text, re.M)
    return m.group(1).strip() if m else path.stem

def classify(path, title):
    s = str(path.relative_to(PLATFORM)) + title
    if any(k in s for k in ['京东', 'JD']):
        return 'jd'
    if any(k in s for k in ['阿里', '淘宝闪购', '饿了么']):
        return 'ali'
    if any(k in s for k in ['美团']):
        return 'meituan'
    if any(k in s for k in ['合规', '医保', '处方', '监管']):
        return 'policy'
    return 'cross'

def focus(path, title):
    name = path.stem
    text = title + name
    if '2026Q1' in text or 'FY2025' in text or '财报' in text or '业绩' in text or '年报' in text or '年度报告' in text:
        if '美团' in text:
            return {
                'conclusion': '这份文件真正要看的不是单个收入或利润数字，而是美团把“闪购、到家履约、本地供给”持续纳入核心本地商业后，医药即时零售在集团能力里的位置是否变重。财报口径能证明平台有足够大的即时配送基础，但不能直接证明买药业务的单独盈利能力。',
                'what': ['把美团买药放进核心本地商业框架理解，重点观察即时配送、闪购和本地供给之间的关系。', '财务数据说明平台在继续用履约网络和高频入口换取即时零售心智，医药只是其中更高合规门槛、更强时效需求的品类。', '如果文件出现买药GMV、药店数、订单峰值等非公告口径，应视为业务线索，不能和财报披露等级混用。'],
                'biz': ['美团的优势在“急用药触发 + 本地药店库存 + 骑手履约”，不是单纯线上药房。', '药企在美团上更适合做应急、常备、季节性和症状触发品类，而不是把它当普通货架电商。', '药店合作质量比药店数量更关键，夜间、缺货替换、药师响应和售后决定复购。'],
                'caution': ['美团财报通常不单独披露买药GMV、处方药占比和药店履约质量，文件中的业务拆分只能作为分析推导。', '补贴、订单峰值、闪电仓数量等新闻口径需要回到公司公告或权威报道再引用。']
            }
        if '阿里' in text:
            return {
                'conclusion': '这份文件的核心不是阿里“也做即时零售”，而是淘宝闪购把即时需求接回淘宝主站流量池后，医药品类可能获得更大的搜索入口和会员触达，但履约与合规能力仍要依赖本地供给和阿里健康协同。',
                'what': ['财报中的本地生活、即时零售和淘宝闪购线索共同指向一个变化：阿里把即时零售从外卖场景推向主站电商场景。', '对医药而言，这意味着购药需求可能从“打开买药频道”变成“搜索症状、药名、品牌后即时转化”。', '阿里健康业绩材料提供医药供给和健康服务线索，但不能自动等同于淘宝闪购医药履约能力。'],
                'biz': ['阿里的优势在搜索、会员、内容和电商心智，适合承接品牌药、常备用药和复购需求。', '短板在本地即时履约密度与药店供给深度是否足够稳定，需要和美团、京东分开评估。', '药企若进入淘宝闪购，应更关注搜索词承接、品牌旗舰供给和阿里健康服务协同。'],
                'caution': ['阿里集团财报、阿里健康公告和淘宝闪购新闻属于不同披露主体，不能把一个主体的数据直接套到另一个主体。', '“补贴规模、订单峰值、份额变化”若来自媒体，应只作为竞争信号。']
            }
        if '京东' in text:
            return {
                'conclusion': '这份文件的重点是京东健康的医药供给与京东即时履约能力如何拼接。京东的竞争逻辑不是流量最大，而是自营供应链、正品心智、医生药师服务和京东秒送形成更强的可信任交易闭环。',
                'what': ['京东健康年报更适合用来判断医药供给、用户服务和线上药房能力。', '京东秒送、到家履约和线下合作材料则用来判断即时交付能力，两者合起来才是京东买药的完整竞争力。', '文件如果只看年报，会低估即时履约；如果只看秒送新闻，又会低估医药专业能力。'],
                'biz': ['京东更适合承接高信任、较高客单、慢病复购和需要专业服务的药品需求。', '即时零售部分的增长要看本地库存密度、药店合作和履约时效能否追上美团。', '药企在京东侧更适合做品牌官方供给、慢病管理、会员复购和专业内容承接。'],
                'caution': ['京东健康披露的是集团医药健康业务，不能直接推导京东买药即时零售份额。', '“秒送能力”与“医药合规链路”必须分开核验。']
            }
    if '合规' in text or '医保' in text or '处方' in text or '监管' in text:
        return {
            'conclusion': '这份文件说明，医药即时零售不是普通即时零售加一个药品类目，而是平台责任、处方审核、药师服务、医保支付和履约留痕共同约束的交易系统。合规能力会直接影响平台可卖什么、怎么卖、能否规模化。',
            'what': ['文件把处方药、医保、药师、平台责任和履约放在同一张图里，说明医药竞争的底层不是纯流量。', '药品网络销售监管要求决定了平台必须能证明信息展示、处方来源、审方和配送过程合规。', '医保支付如果接入，会提升转化，但也会带来更强的资质、系统和监管约束。'],
            'biz': ['平台长期门槛在合规链路，而不是补贴。', '药店是否愿意深度合作，取决于平台能否降低合规和履约成本，而不是只给流量。', '药企做即时零售投放时，需要确认平台是否能承接处方、药师咨询和售后风险。'],
            'caution': ['监管政策只能引用国家药监、医保、卫健等官方原文。', '地方医保、处方流转和互联网医院政策差异大，不能用单一城市经验推全国。']
        }
    if '补贴' in text:
        return {
            'conclusion': '这份文件讨论的是补贴战对医药即时零售的传导：补贴能快速拉动订单和用户尝试，但医药品类的长期竞争仍取决于药品供给、履约稳定、合规和复购，而不是单次低价。',
            'what': ['补贴会改变用户入口选择，让用户在美团、淘宝闪购、京东之间迁移。', '医药品类因为急用和信任属性更强，补贴的有效性低于餐饮生鲜，但对常备药、OTC和季节性品类仍有明显拉动。', '如果补贴侵蚀药店毛利，平台可能得到短期订单但损害供给稳定。'],
            'biz': ['评估补贴不能只看GMV，要同时看复购、客单、履约成本和药店利润。', '药企可以利用补贴窗口做新品试用和症状场景触达，但不应把价格补贴当作长期渠道策略。', '平台若无法沉淀搜索词和人群资产，补贴结束后订单会快速回落。'],
            'caution': ['补贴金额、订单峰值和份额多数来自新闻或研报，应作为竞争观察，不直接写成确定事实。', '医药品类与外卖补贴逻辑不同，不能把外卖大战结论简单迁移。']
        }
    if '药店合作' in text:
        return {
            'conclusion': '这份文件的核心是平台与药店的合作模式。平台竞争不是谁接入药店更多，而是谁能让药店在库存、价格、履约、药师和售后上形成稳定供给。',
            'what': ['平台给药店带来线上订单和即时履约入口，但也会带来价格透明、库存同步和服务响应压力。', '美团偏本地履约和急用药心智，阿里偏主站流量与搜索承接，京东偏供应链和信任心智。', '药店合作深度决定平台能否从“有药店”变成“有可交付的药”。'],
            'biz': ['药店需要按平台能力区分合作目标：引流、清库存、做夜间服务、承接慢病复购。', '平台对药店的真正价值是提高确定性订单，而不是简单增加曝光。', '药企做O2O铺货时，必须确认药店库存和平台展示是否一致。'],
            'caution': ['药店数量、覆盖城市和履约时效要看统计口径。', '合作模式可能因城市、连锁、单体药店和医保资质不同而差异很大。']
        }
    if '指标表' in text or '三方对比' in text or '竞争雷达' in text or '入口对比' in text or '来源索引' in text:
        return {
            'conclusion': '这份文件的价值是把平台竞争拆成可对比指标：入口、供给、履约、价格、医保、处方、药师和复购。它不是为了给平台排名，而是为了解释不同玩家为什么在不同购药场景里强弱不同。',
            'what': ['美团优势更偏本地生活入口和即时履约。', '阿里优势更偏淘宝主站流量、搜索和生态协同。', '京东优势更偏自营供应链、正品心智和健康服务。', '叮当等垂直玩家可作为专业履约样本，但规模和流量需要单独评估。'],
            'biz': ['急用药优先看履约密度和夜间供给。', '慢病复购优先看价格稳定、会员和专业服务。', '品牌药推广优先看搜索承接、内容触达和官方供给。', '处方药必须先看合规链路，再看流量。'],
            'caution': ['对比表中的强弱是分析框架，不是静态结论。', '平台能力会随补贴、组织调整、城市覆盖和药店合作快速变化。']
        }
    if '新闻动态' in text:
        return {
            'conclusion': '这份文件适合当作平台动作时间线，而不是单篇新闻摘录。真正有价值的是把新闻放回“入口变化、供给扩张、补贴节奏、履约升级、合规压力”五条线里，看平台动作是否连续。',
            'what': ['新闻动态能捕捉平台短期动作，例如活动、补贴、组织调整、合作升级和品类扩张。', '单条新闻的确定性有限，但多条新闻连在一起可以判断平台战略重心。', '医药相关动态要特别区分官方发布、媒体报道、研报判断和市场传闻。'],
            'biz': ['团队应从新闻里提取可跟踪信号：城市、品类、药店、补贴、履约和合规。', '如果同一平台连续强化买药、健康、即时配送，说明医药即时零售权重在上升。', '如果新闻只停留在营销活动，说明它更像短期拉新而非长期能力建设。'],
            'caution': ['新闻中的市场规模、份额和GMV需要二次核验。', '未出现官方原文的内容只能作为线索。']
        }
    if '研报' in text:
        return {
            'conclusion': '这份文件应作为外部观点集合使用。研报的价值不在于替代事实，而在于提供市场对补贴、份额、利润修复和平台格局的判断，帮助团队识别主流预期与分歧。',
            'what': ['研报通常会把平台竞争抽象成份额、补贴、利润率和用户心智。', '医药即时零售在研报里往往不是主章节，需要从即时零售、到家、健康、O2O等相关段落中提取。', '不同机构对同一平台的判断可能相反，差异本身就是重要信息。'],
            'biz': ['研报适合用于判断市场预期和估值压力，不适合单独作为业务事实。', '当多家机构都关注补贴和利润，说明平台竞争已经影响到资本市场叙事。', '药企和药店应关注研报中对平台长期投入能力的判断。'],
            'caution': ['目标价、份额预测和盈利预测都属于机构判断。', '正式引用必须区分“机构观点”和“公司披露”。']
        }
    return {
        'conclusion': '这份文件的核心价值是把平台公开信息转成业务判断：即时零售医药竞争要同时看流量入口、药品供给、履约网络、合规能力和复购沉淀，单看任何一个指标都会误判。',
        'what': ['文件把平台动作、公开披露和医药场景放在一起，目的是解释不同平台的能力边界。', '医药即时零售既有即时零售的速度竞争，也有医药行业的信任和合规竞争。', '文件中的信息应按“事实披露、媒体线索、机构判断、内部推导”分层理解。'],
        'biz': ['平台选择要按场景拆分：急用药看履约，慢病看复购，品牌药看搜索和内容，处方药看合规。', '药店和药企不能只看流量价格，要看平台能否形成稳定交易闭环。', '竞争雷达应持续更新，不应一次性定性。'],
        'caution': ['未回到公告、监管或公司原文的数据不能作为确定事实。', '平台策略变化快，文件结论需要随着财报和官方动作滚动更新。']
    }

def make_block(path, title, kind):
    f = focus(path, title)
    what = '\n'.join(f'- {x}' for x in f['what'])
    biz = '\n'.join(f'- {x}' for x in f['biz'])
    caution = '\n'.join(f'- {x}' for x in f['caution'])
    return f'''<!-- READING_FRAMEWORK_START -->

## 文件分析结论

{f['conclusion']}

## 先读这几份公开原文

{source_lines(kind)}

## 文件内容拆解

{what}

## 对业务的判断

{biz}

## 需要谨慎的口径

{caution}

## 可以沉淀成的结论

| 观察维度 | 本文件给出的信号 | 对平台竞争的含义 |
|---|---|---|
| 流量入口 | 用户从搜索、频道、外卖/到家、本地生活入口进入购药链路 | 谁能更早承接需求，谁就更容易获得交易机会 |
| 供给质量 | 药店库存、品牌供给、价格稳定性和服务响应共同决定转化 | 供给不是数量问题，而是可交付、可信任、可复购 |
| 履约能力 | 即时配送决定急用药体验，夜间和异常售后决定信任 | 医药履约的稳定性比单次速度更重要 |
| 合规链路 | 处方、药师、医保和平台责任限制业务边界 | 合规不是附属条件，而是医药即时零售的长期门槛 |

<!-- READING_FRAMEWORK_END -->'''

def strip_bad_sections(text):
    # remove previous framework fully
    text = re.sub(r'<!-- READING_FRAMEWORK_START -->.*?<!-- READING_FRAMEWORK_END -->\s*', '', text, flags=re.S)
    # remove official verified summaries if any
    text = re.sub(r'<!-- OFFICIAL_VERIFIED_SUMMARY_START -->.*?<!-- OFFICIAL_VERIFIED_SUMMARY_END -->\s*', '', text, flags=re.S)
    # remove generic source-card sections from first part until first major content heading
    headings = ['数据来源','优先来源','备用来源','资料主题','来源与引用口径','正式使用口径','可用于回答的问题','备注']
    for h in headings:
        pattern = rf'(?ms)^##?\s*{re.escape(h)}\s*$.*?(?=^##?\s+|^---\s*$|\Z)'
        text = re.sub(pattern, '', text)
    # remove exact/generic boilerplate lines and source-card blockquote lines
    text = re.sub(r'(?m)^>\s*数据来源[:：].*\n?', '', text)
    text = re.sub(r'(?m)^>\s*信息来源[:：].*\n?', '', text)
    text = re.sub(r'(?m)^本文定位为平台竞争补充资料.*\n?', '', text)
    text = re.sub(r'(?m)^.*是一篇面向即时零售平台竞争的分析资料，重点用于判断平台动作背后的业务能力、经营变量和医药品类影响，而不是只记录信息来源。\s*\n?', '', text)
    text = text.replace('链接/备注', '链接/口径').replace('来源/备注', '来源/口径')
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip() + '\n'

changed = []
for path in sorted(p for p in PLATFORM.rglob('*.md') if p.name != '_index.md'):
    old = path.read_text(encoding='utf-8', errors='replace')
    title = title_of(old, path)
    kind = classify(path, title)
    clean = strip_bad_sections(old)
    lines = clean.splitlines()
    insert_idx = 1 if lines and lines[0].startswith('# ') else 0
    # keep metadata block after title if present, but place analysis before old body after first ---
    m = re.search(r'(?ms)^(# .+?\n(?:\n|>.*\n|---\s*\n)*)', clean)
    if m:
        prefix = m.group(1).rstrip()
        rest = clean[m.end():].lstrip()
        new = prefix + '\n\n' + make_block(path, title, kind) + ('\n\n' + rest if rest else '')
    else:
        new = make_block(path, title, kind) + '\n\n' + clean
    if new != old:
        path.write_text(new, encoding='utf-8')
        changed.append(str(path.relative_to(ROOT)))
print('changed', len(changed))
for p in changed:
    print(p)
