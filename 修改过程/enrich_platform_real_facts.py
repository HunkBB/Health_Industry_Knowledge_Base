from pathlib import Path
import re
ROOT=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
PLATFORM=ROOT/'01-即时零售平台'
START='<!-- PUBLIC_FACT_ENRICHMENT_START -->'
END='<!-- PUBLIC_FACT_ENRICHMENT_END -->'

S={
'meituan_results':'[美团投资者关系｜业绩公告](https://www.meituan.com/en-US/investor/results)',
'meituan_cn':'[美团投资者关系](https://www.meituan.com/investor-relations)',
'meituan_2025':'[美团2025年度业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0326/2026032600964.pdf)',
'alibaba_results':'[阿里巴巴投资者关系｜财务报告](https://home.alibabagroup.com/zh-HK/ir-financial-reports-financial-results)',
'alibaba_fy2026':'[阿里巴巴FY2026业绩](https://home.alibabagroup.com/en-US/document-1991237455038119936)',
'alihealth_fy2026':'[阿里健康2026财年业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0514/2026051400755.pdf)',
'jdhealth_reports':'[京东健康投资者关系｜报告](https://ir.jdhealth.com/sc/ir_report.php)',
'jdhealth_2025_results':'[京东健康2025年度业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0305/2026030500466.pdf)',
'jdhealth_2025_ar':'[京东健康2025年报](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0424/2026042401364.pdf)',
'nmpa_rule':'[《药品网络销售监督管理办法》](https://www.gov.cn/gongbao/content/2022/content_5717002.htm)',
'delivery_guideline':'[国务院办公厅｜促进即时配送行业高质量发展的指导意见](https://www.gov.cn/zhengce/zhengceku/202409/content_6974607.htm)',
'hkex':'[港交所披露易](https://www.hkexnews.hk/index_c.htm)',
'cninfo':'[巨潮资讯网](https://www.cninfo.com.cn/new/index.jsp)',
}

def links(keys):
    return '\n'.join(f'- {S[k]}' for k in keys)

def classify(path):
    s=str(path)
    if '美团' in s: return 'meituan'
    if '阿里' in s or '淘宝闪购' in s or '饿了么' in s: return 'ali'
    if '京东' in s: return 'jd'
    if '合规' in s or '处方' in s or '医保' in s or '监管' in s: return 'policy'
    if '补贴' in s: return 'subsidy'
    if '药店合作' in s: return 'pharmacy'
    if '入口' in s: return 'entry'
    return 'cross'

def section(kind, title):
    if kind=='meituan':
        return f'''{START}

## 公开核验补充（2026-06-16）

### 核验后的关键事实

- 美团相关经营数据应优先回到美团投资者关系和港交所披露文件；公开公告能确认集团和分部经营情况，但通常不会把“美团买药”单独拆成完整经营报表。
- 美团买药的业务判断应放在“核心本地商业 + 即时配送 + 闪购/到家 + 药店供给”框架下理解，而不是只看买药频道本身。
- 对医药即时零售而言，美团最值得跟踪的真实变量是附近药店库存、夜间履约、药师/处方合规、急用药搜索触发和售后稳定性。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 集团财报/业绩公告 | {S['meituan_results']}、{S['hkex']} | 用于引用收入、利润、分部表现和管理层表述 |
| FY2025年度业绩 | {S['meituan_2025']} | 用于判断美团本地商业与即时零售投入背景 |
| 药品网络销售合规 | {S['nmpa_rule']} | 用于判断买药业务的处方、药师、平台责任边界 |

### 业务分析

- **平台能力**：美团强项是本地生活高频入口和即时履约网络，适合承接急用、夜间、季节性和家庭常备用药需求。
- **药店合作**：不能只看接入药店数量，要看库存同步、价格稳定、药师响应、处方承接和异常订单处理。
- **药企机会**：美团更适合做症状触发和即时转化，例如感冒发烧、肠胃、皮肤、儿童、家庭常备等场景。

### 引用边界

- 买药GMV、处方药占比、药店履约质量、药师响应等若未在公告中单独披露，不能写成官方事实。
- 媒体报道或行业估算可作为竞争线索，但正式汇报应回到公告、监管文件或平台公开材料。

{END}'''
    if kind=='ali':
        return f'''{START}

## 公开核验补充（2026-06-16）

### 核验后的关键事实

- 阿里即时零售应拆成三层看：阿里集团财报里的本地生活/即时零售方向、淘宝闪购/饿了么的履约场景、阿里健康的医药供给和健康服务能力。
- 淘宝闪购的价值在于把即时需求接回淘宝主站流量和搜索场景；医药品类能否转化，还要看阿里健康供给、药店库存和处方/药师合规链路。
- 阿里健康财报可作为医药健康供给和服务能力来源，但不能直接等同于淘宝闪购买药的本地履约表现。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 阿里集团财报 | {S['alibaba_results']}、{S['alibaba_fy2026']} | 判断本地生活、淘宝闪购和即时零售方向 |
| 阿里健康业绩 | {S['alihealth_fy2026']} | 判断医药供给、健康服务和药品电商能力 |
| 药品网售监管 | {S['nmpa_rule']} | 判断处方药、药师服务和平台责任边界 |

### 业务分析

- **平台能力**：阿里优势在淘宝搜索、会员、品牌旗舰和生态协同，适合承接品牌药、常备药和慢病复购。
- **履约挑战**：淘宝闪购医药场景必须验证本地药店供给、配送时效和售后稳定性，不能只看主站流量。
- **药企机会**：适合围绕“症状词/药名搜索—品牌供给—即时配送—健康服务”设计转化链路。

### 引用边界

- 阿里集团、阿里健康、淘宝闪购是不同披露主体，数据不能混用。
- 补贴规模、订单峰值、份额变化若来自媒体或研报，只能作为竞争信号。

{END}'''
    if kind=='jd':
        return f'''{START}

## 公开核验补充（2026-06-16）

### 核验后的关键事实

- 京东健康公开报告适合用于核验医药供给、线上药房、健康服务和用户信任心智；京东买药/秒送的即时履约能力需要和本地库存、配送覆盖分开判断。
- 京东的医药即时零售逻辑不是单纯“更快”，而是“可信供给 + 专业服务 + 近场履约”。
- 对慢病复购、品牌药、较高信任需求和专业咨询场景，京东健康资料的参考价值更高。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 京东健康年度业绩 | {S['jdhealth_2025_results']} | 判断医药健康业务表现和管理层表述 |
| 京东健康年报 | {S['jdhealth_2025_ar']} | 判断经营结构、业务模式和风险边界 |
| 京东健康IR报告页 | {S['jdhealth_reports']} | 后续更新财报和公告入口 |

### 业务分析

- **平台能力**：京东强项在供应链、正品心智、线上药房和健康服务，适合高信任和复购型用药需求。
- **履约判断**：京东秒送/买药要单独验证城市覆盖、附近库存和即时配送稳定性，不能只用京东健康整体指标替代。
- **药企机会**：更适合品牌官方供给、慢病管理、会员复购和专业内容承接。

### 引用边界

- 京东健康披露的是医药健康业务口径，不等同于京东买药即时零售份额。
- 秒送能力、药店库存、药师响应等需要平台或公开材料另行核验。

{END}'''
    if kind=='policy':
        return f'''{START}

## 公开核验补充（2026-06-16）

### 核验后的关键事实

- 医药即时零售的底层约束来自药品网络销售监管：平台责任、处方来源、药师审核、信息展示、配送留痕都必须可解释。
- 即时配送政策强调行业高质量发展，说明平台不能只追求速度，还要保证服务规范、安全和稳定。
- 医保、处方流转和互联网诊疗存在地方差异，不能用单个城市或单个平台经验替代全国口径。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 药品网络销售 | {S['nmpa_rule']} | 判断平台、药店和处方药销售边界 |
| 即时配送规范 | {S['delivery_guideline']} | 判断履约服务、配送安全和行业规范 |
| 医保/处方支付 | 国家医保局及地方医保公开文件 | 判断线上医保和定点药店支付边界 |

### 业务分析

- **平台**：必须建立处方、药师、药品展示、交易记录和配送责任闭环。
- **药店**：必须确认资质、库存、审方、医保和履约责任。
- **药企**：做即时零售投放前要确认品类是否适合线上展示和即时交付。

### 引用边界

- 政策条款必须引用监管原文，不能用媒体摘要替代。
- 地方医保和处方流转政策差异较大，正式使用时要标明地区。

{END}'''
    if kind=='subsidy':
        return f'''{START}

## 公开核验补充（2026-06-16）

### 核验后的关键事实

- 平台补贴可以改变短期用户入口选择，但医药品类不同于外卖和生鲜，长期转化更依赖信任、真实库存、药师服务和履约稳定。
- 补贴数据常来自新闻或研报，正式使用时要回到平台公告、财报费用变化或权威报道确认。
- 医药补贴如果挤压药店毛利，可能带来短期订单增长但削弱供给稳定性。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 平台经营投入 | {S['meituan_results']}、{S['alibaba_results']} | 判断补贴与利润压力背景 |
| 医药销售合规 | {S['nmpa_rule']} | 判断补贴不能突破药品网售边界 |
| 即时配送规范 | {S['delivery_guideline']} | 判断补贴后的履约稳定性要求 |

### 业务分析

- 评估补贴要同时看 GMV、复购、客单、药店毛利、退单和投诉。
- 药企可借补贴窗口做症状场景触达和新品试用，但不能把低价当成长期渠道策略。
- 平台如果不能沉淀搜索词、人群资产和复购关系，补贴结束后订单容易回落。

### 引用边界

- 补贴金额、订单峰值和市场份额若未来自官方披露，只能作为研判参考。

{END}'''
    if kind=='pharmacy':
        return f'''{START}

## 公开核验补充（2026-06-16）

### 核验后的关键事实

- 平台药店合作不应只看“接入多少药店”，更要看库存同步、价格稳定、药师响应、处方承接、医保资质和售后履约。
- 对连锁药店，平台合作可能带来增量订单；对单体药店，平台流量更重要但运营压力也更大。
- 药店数量、上线率和城市覆盖必须注明统计口径。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 药品网络销售规则 | {S['nmpa_rule']} | 判断平台和药店责任 |
| 平台财报/公告 | {S['meituan_results']}、{S['alibaba_results']}、{S['jdhealth_reports']} | 判断平台投入和合作方向 |
| 上市连锁药店公告 | {S['cninfo']} | 判断药店O2O、门店和经营变化 |

### 业务分析

- 平台给药店带来曝光和订单，也要求药店具备库存、拣货、药师咨询、配送协同和售后能力。
- 药店合作质量比数量更重要；真实可交付库存决定用户体验。
- 药企做O2O铺货时，要确认平台展示与药店实际库存是否一致。

### 引用边界

- 药店数量、覆盖城市和履约时效不能跨平台直接比较，除非统计口径一致。

{END}'''
    # cross/entry default
    return f'''{START}

## 公开核验补充（2026-06-16）

### 核验后的关键事实

- 美团、阿里、京东的即时零售医药竞争不是同一套能力：美团偏本地生活入口和履约，阿里偏淘宝搜索和生态协同，京东偏供应链、正品心智和健康服务。
- 用户入口要按场景拆分：急用药看履约，慢病复购看稳定供给和服务，品牌药看搜索承接，处方药先看合规。
- 平台对比应把官方公告、财报、监管政策和媒体/研报观点分层使用。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 美团平台 | {S['meituan_results']} | 判断本地商业、闪购和履约背景 |
| 阿里平台 | {S['alibaba_results']}、{S['alihealth_fy2026']} | 判断淘宝闪购、阿里健康和生态协同 |
| 京东平台 | {S['jdhealth_reports']} | 判断医药供给、健康服务和京东买药基础 |
| 合规边界 | {S['nmpa_rule']} | 判断处方、药师和平台责任 |

### 业务分析

- **急用药**：优先看附近库存、夜间履约和售后稳定。
- **慢病复购**：优先看价格稳定、会员、处方和药师服务。
- **品牌药/OTC**：优先看搜索入口、内容承接和场景转化。
- **处方药**：先看合规和审方，再看流量和补贴。

### 引用边界

- 平台排名和份额判断必须说明口径；没有统一公开口径时，只做能力维度对比。

{END}'''

def remove_old_enrichment(text):
    text=re.sub(r'(?ms)<!-- PUBLIC_FACT_ENRICHMENT_START -->.*?<!-- PUBLIC_FACT_ENRICHMENT_END -->\s*','',text)
    return text

def insert_after_template_or_title(text, block):
    if '<!-- TYPE_LEARNING_TEMPLATE_END -->' in text:
        return text.replace('<!-- TYPE_LEARNING_TEMPLATE_END -->', '<!-- TYPE_LEARNING_TEMPLATE_END -->\n\n'+block, 1)
    lines=text.splitlines()
    if lines and lines[0].startswith('# '):
        return lines[0]+'\n\n'+block+'\n\n'+'\n'.join(lines[1:]).lstrip()
    return block+'\n\n'+text

changed=[]
for p in sorted(PLATFORM.rglob('*.md')):
    if p.name=='_index.md': continue
    old=p.read_text(encoding='utf-8', errors='replace')
    kind=classify(p)
    title=p.stem
    block=section(kind,title)
    new=insert_after_template_or_title(remove_old_enrichment(old), block)
    new=re.sub(r'\n{4,}','\n\n\n',new).strip()+'\n'
    if new!=old:
        p.write_text(new,encoding='utf-8')
        changed.append((str(p.relative_to(ROOT)),kind))
print('changed',len(changed))
for c in changed: print(c)
