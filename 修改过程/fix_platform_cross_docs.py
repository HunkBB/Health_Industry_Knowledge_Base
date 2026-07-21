from pathlib import Path
ROOT=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
files=[
ROOT/'01-即时零售平台/竞争雷达_美团阿里京东.md',
ROOT/'01-即时零售平台/补充资料/美团阿里京东医药即时零售三方对比.md',
ROOT/'01-即时零售平台/补充资料/美团阿里京东每周竞争雷达来源索引.md',
]
for p in files:
    t=p.read_text(encoding='utf-8')
    start=t.find('### 核验后的关键事实')
    end=t.find('### 引用边界')
    if start==-1 or end==-1:
        continue
    replacement='''### 核验后的关键事实

- 美团、阿里、京东的即时零售医药竞争不是同一套能力：美团偏本地生活入口和履约，阿里偏淘宝搜索和生态协同，京东偏供应链、正品心智和健康服务。
- 用户入口要按场景拆分：急用药看履约，慢病复购看稳定供给和服务，品牌药看搜索承接，处方药先看合规。
- 平台对比应把官方公告、财报、监管政策和媒体/研报观点分层使用。

### 关键数据/口径

| 口径 | 已核验公开来源 | 在本文中的用法 |
|---|---|---|
| 美团平台 | [美团投资者关系｜业绩公告](https://www.meituan.com/en-US/investor/results) | 判断本地商业、闪购和履约背景 |
| 阿里平台 | [阿里巴巴投资者关系｜财务报告](https://home.alibabagroup.com/zh-HK/ir-financial-reports-financial-results)、[阿里健康2026财年业绩公告](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0514/2026051400755.pdf) | 判断淘宝闪购、阿里健康和生态协同 |
| 京东平台 | [京东健康投资者关系｜报告](https://ir.jdhealth.com/sc/ir_report.php) | 判断医药供给、健康服务和京东买药基础 |
| 合规边界 | [《药品网络销售监督管理办法》](https://www.gov.cn/gongbao/content/2022/content_5717002.htm) | 判断处方、药师和平台责任 |

### 业务分析

- **急用药**：优先看附近库存、夜间履约和售后稳定。
- **慢病复购**：优先看价格稳定、会员、处方和药师服务。
- **品牌药/OTC**：优先看搜索入口、内容承接和场景转化。
- **处方药**：先看合规和审方，再看流量和补贴。

'''
    t=t[:start]+replacement+t[end:]
    t=t.replace('买药GMV、处方药占比、药店履约质量、药师响应等若未在公告中单独披露，不能写成官方事实。\n- 媒体报道或行业估算可作为竞争线索，但正式汇报应回到公告、监管文件或平台公开材料。','平台排名和份额判断必须说明口径；没有统一公开口径时，只做能力维度对比。')
    p.write_text(t,encoding='utf-8')
    print('fixed',p)
