#!/usr/bin/env python3
"""
Build a single-file learning site for the industry information library.

The output is self-contained and does not depend on external APIs, CDNs, or a
local server. Source content remains the Markdown library in this directory.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import markdown
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.tables import TableExtension
except Exception as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(f"Missing dependency: markdown ({exc})")


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "行业信息库.html"
DOC_IMAGE_WEB_MAP_FILE = BASE_DIR / "assets" / "doc_cards_web" / "doc_image_web_map.json"
OFFICIAL_SUMMARY_START = "<!-- OFFICIAL_VERIFIED_SUMMARY_START -->"
READING_FRAMEWORK_START = "<!-- READING_FRAMEWORK_START -->"



def content_for_ranking(md_text: str) -> str:
    cut = md_text.split(OFFICIAL_SUMMARY_START, 1)[0]
    cut = cut.split(READING_FRAMEWORK_START, 1)[0]
    return cut.rstrip()


def load_doc_image_map() -> dict[str, str]:
    if not DOC_IMAGE_WEB_MAP_FILE.exists():
        return {}
    try:
        data = json.loads(DOC_IMAGE_WEB_MAP_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(doc_id): str(path) for doc_id, path in data.items()}


GOVERNANCE_FILES = {
    "数据口径字典",
    "数据引用台账",
    "信息覆盖矩阵",
    "主题交叉索引",
    "原始出处索引",
    "数据引用补齐清单",
}

HIDDEN_CONTENT_PATTERNS = [
    "行业信息库校验报告",
    "数据口径",
    "数据引用",
    "信息覆盖矩阵",
    "主题交叉索引",
    "原始出处索引",
    "补齐清单",
    "内部综合判断",
    "米未研究院-搜索结论",
]

PUBLIC_RESEARCH_SUMMARY_FILES = {
    "04-券商研报/研报原文摘要.md",
    "04-券商研报/医药零售行业/券商研报_医药零售行业_2025-2026.md",
    "01-即时零售平台/美团-美团买药/研报摘要/美团及美团买药-研报摘要_2025-2026.md",
    "01-即时零售平台/阿里-淘宝闪购/研报摘要/阿里及阿里健康-研报摘要_2025-2026.md",
}

PUBLIC_BUSINESS_INSIGHT_FILES = {
    "01-即时零售平台/美团-美团买药/综合分析/美团-美团买药-业务洞察.md",
    "01-即时零售平台/阿里-淘宝闪购/综合分析/阿里-淘宝闪购-业务洞察.md",
}

PUBLIC_CONTENT_PREFIXES = (
    "01-即时零售平台/",
    "02-连锁药店/",
    "03-即时零售相关药企/",
    "04-券商研报/",
    "05-行业机构/",
    "06-其他行业报告/",
    "07-政策与监管库/",
    "08-疾病与医学基础/",
)

MIN_NEWS_YEAR = 2025

SHARING_TEXT_REPLACEMENTS = [
    ("视角：京东健康即时零售商分团队", "分析视角：医药即时零售经营分析"),
    ("京东健康即时零售商分团队", "医药即时零售经营分析"),
    ("团队判断和启示", "分析判断和启示"),
    ("内部综合判断", "待核验线索"),
    ("内部推断", "分析推断"),
    ("内部线索", "待核验线索"),
    ("内部判断", "分析判断"),
    ("WebSearch工具本次未返回搜索结果", "公开增量信息暂未补齐"),
    ("WebSearch工具搜索功能暂时不可用", "公开增量信息仍需继续补充"),
    ("本文件信息主要来源于已有项目文件——", "资料来源包括："),
    ("本文件基于", "资料来源包括"),
    ("后续需通过网络搜索补充增量新闻", "后续可继续补充公开报道"),
    ("后续需通过网络搜索补充验证", "后续可继续补充资料核验"),
    ("需后续通过网络搜索补充", "后续可继续补充公开信息"),
    ("以下信息因WebSearch工具未返回结果，暂未获取到", "以下信息暂未在公开材料中补齐"),
    ("当前行业库", "当前资料"),
    ("用于行业库", "阅读价值"),
    ("截图里那类", "没有原文链接的"),
]

CONTENT_TYPE_BY_PART = {
    "财报数据": "财报数据",
    "官方财报数据": "财报数据",
    "公开新闻": "公开新闻",
    "研报摘要": "研报摘要",
    "综合分析": "综合分析",
}

CONTENT_TYPE_ORDER = [
    "财报数据",
    "行业报告",
    "研报摘要",
    "公开新闻",
    "医学基础",
    "综合分析",
    "政策监管",
    "治理口径",
    "索引",
]


RECOMMENDED_READING_RULES = {
    "market": [
        {"label": "行研报告", "keywords": ["行研", "行业研究", "行业报告", "研报", "券商研报", "研究报告"]},
        {"label": "最新资讯", "keywords": ["新闻", "动态", "资讯", "日报", "更新", "最新"]},
    ],
    "competition": [
        {"label": "财报", "keywords": ["财报", "业绩", "年报", "季报", "半年报", "公告"]},
        {"label": "研报", "keywords": ["研报", "研究报告", "行业研究", "券商"]},
        {"label": "新闻", "keywords": ["新闻", "动态", "资讯", "公告", "事件"]},
        {"label": "综合分析", "keywords": ["综合分析", "基准", "能力", "对比", "竞争", "履约", "入口"]},
    ],
    "pharmacy": [
        {"label": "财报", "keywords": ["财报", "业绩", "年报", "季报", "半年报", "公告"]},
        {"label": "研报", "keywords": ["研报", "研究报告", "行业研究", "券商"]},
        {"label": "新闻", "keywords": ["新闻", "动态", "资讯", "公告", "事件"]},
    ],
    "pharma": [
        {"label": "财报", "keywords": ["财报", "业绩", "年报", "季报", "半年报", "公告"]},
        {"label": "研报", "keywords": ["研报", "研究报告", "行业研究", "券商"]},
        {"label": "新闻", "keywords": ["新闻", "动态", "资讯", "公告", "事件"]},
        {"label": "政策监管", "keywords": ["政策", "监管", "医保", "药监", "卫健委", "合规"]},
    ],
    "policy": [
        {"label": "研报", "keywords": ["研报", "研究报告", "行业研究", "券商"]},
        {"label": "新闻", "keywords": ["新闻", "动态", "资讯", "公告", "事件"]},
        {"label": "政策监管", "keywords": ["政策", "监管", "医保", "药监", "卫健委", "合规", "办法", "通知"]},
    ],
    "medical": [
        {"label": "常见疾病", "keywords": ["常见疾病", "高血压", "糖尿病", "心脑血管", "慢阻肺", "哮喘", "流感"]},
        {"label": "重点病种", "keywords": ["重点病种", "癌症", "肿瘤", "罕见病", "慢性病", "门诊慢特病"]},
        {"label": "核心医学概念", "keywords": ["核心医学概念", "医学概念", "处方药", "非处方药", "适应症", "禁忌", "不良反应", "医保"]},
    ],
}

STRATEGIC_ISSUES = [
    {
        "id": "market",
        "eyebrow": "Market sizing",
        "title": "行业全景：医药零售的规模、渠道和增长结构怎么看",
        "summary": "先看医药零售行业整体：全终端规模、实体药店、O2O、电商渠道、客流变化、品类结构和连锁化趋势，再进入平台、药店、药企等细分主题。",
        "takeaway": "适合回答“医药零售行业现在处在什么周期”“哪些渠道和品类还在增长”“后面应该优先读什么”。",
        "displayKeywords": ["市场规模", "渠道结构", "O2O渗透", "实体药店", "增长趋势", "行业报告"],
        "icon": "📊",
        "visualLabel": "市场图表",
        "keywords": ["医药零售", "药品零售", "实体药店", "全终端", "O2O渠道", "中康科技", "西普会", "西鼎会", "米内网", "医药零售市场", "行业全景"],
        "queries": ["医药零售行业", "药品零售规模", "实体药店规模", "O2O渠道", "西普会", "中康科技", "米内网"],
        "includePathPrefixes": ["05-行业机构", "06-其他行业报告/医药零售", "04-券商研报/医药零售行业"],
        "excludePathPrefixes": ["01-即时零售平台", "02-连锁药店", "03-即时零售相关药企"],
        "accent": "blue",
    },
    {
        "id": "competition",
        "eyebrow": "Competitive landscape",
        "title": "竞争格局：美团、淘宝闪购与即时履约平台怎么对比",
        "summary": "聚合平台财报、公开新闻、机构公开材料和公开业务信息，先形成竞对动作的结构化对比，再回到原始出处核验关键数字。",
        "takeaway": "适合回答“竞对最近在做什么”“平台战争对医药即时零售有什么影响”。",
        "displayKeywords": ["美团买药", "淘宝闪购", "京东秒送", "即时配送", "补贴竞争", "供给履约"],
        "icon": "🛰️",
        "visualLabel": "竞争雷达",
        "keywords": ["美团买药", "淘宝闪购", "即时履约平台", "平台竞争", "份额", "订单峰值", "补贴"],
        "queries": ["美团买药", "淘宝闪购", "平台竞争", "订单峰值", "补贴"],
        "includePathPrefixes": ["01-即时零售平台", "04-券商研报/即时零售行业", "04-券商研报/O2O与本地生活", "06-其他行业报告"],
        "excludePathPrefixes": ["02-连锁药店", "03-即时零售相关药企"],
        "accent": "red",
    },
    {
        "id": "pharmacy",
        "eyebrow": "Retail pharmacy",
        "title": "连锁药店：O2O、门店、毛利和线上化发生了什么",
        "summary": "把六大连锁药店的财报、O2O 上线率、线上占比、毛利变化和新闻动态放在同一个阅读路径里看。",
        "takeaway": "适合回答“药店线下基本盘和即时零售增量之间是什么关系”。",
        "displayKeywords": ["门店经营", "O2O业务", "财报指标", "毛利率", "客流变化", "药店合规"],
        "icon": "🏪",
        "visualLabel": "连锁药店",
        "keywords": ["连锁药店", "O2O上线率", "线上占比", "门店", "毛利率", "大参林", "老百姓", "益丰"],
        "queries": ["连锁药店", "O2O上线率", "线上占比", "毛利率", "六家营收"],
        "includePathPrefixes": ["02-连锁药店", "04-券商研报/医药零售行业", "05-行业机构", "06-其他行业报告/医药零售"],
        "excludePathPrefixes": ["01-即时零售平台", "03-即时零售相关药企"],
        "accent": "green",
    },
    {
        "id": "pharma",
        "eyebrow": "Pharma opportunity",
        "title": "药企机会：OTC、DTP、GLP-1 和慢病复购怎么理解",
        "summary": "从 OTC/消费健康和 DTP/特药两个方向看药企与即时零售的连接点，区分事实、线索和分析推断。",
        "takeaway": "适合回答“哪些药企或品类更可能和 DTP/O2O 形成机会”。",
        "displayKeywords": ["OTC", "DTP特药", "慢病复购", "创新药", "GLP-1", "渠道合作"],
        "icon": "💊",
        "visualLabel": "药企机会",
        "keywords": ["OTC", "DTP", "GLP-1", "慢病复购", "华润三九", "信达生物", "百济神州", "再鼎医药"],
        "queries": ["GLP-1", "DTP", "OTC药企", "慢病复购", "信达生物"],
        "includePathPrefixes": ["03-即时零售相关药企", "04-券商研报/医药零售行业", "07-政策与监管库"],
        "excludePathPrefixes": ["01-即时零售平台", "02-连锁药店"],
        "accent": "purple",
    },
    {
        "id": "policy",
        "eyebrow": "Policy and regulation",
        "title": "政策监管：处方药、医保、平台补贴会影响什么",
        "summary": "集中查看处方药网售、医保线上支付、平台补贴监管和药品流通政策，重点标出待确认和慎用信息。",
        "takeaway": "适合回答“哪些监管变量会改变业务打法或引用边界”。",
        "displayKeywords": ["处方药网售", "医保支付", "药品流通", "平台监管", "基金监管", "合规边界"],
        "icon": "⚖️",
        "visualLabel": "政策法规",
        "keywords": ["政策监管", "处方药", "医保", "平台补贴", "药品流通", "GLP-1禁售", "线上不能卖", "线下不能卖", "药品禁售", "网络销售禁止清单"],
        "queries": ["处方药监管", "医保政策", "平台监管", "药品流通", "GLP-1禁售", "哪些药线上不能卖", "哪些药线下不能卖"],
        "includePathPrefixes": ["07-政策与监管库", "04-券商研报/医药零售行业"],
        "accent": "gold",
    },
    {
        "id": "medical",
        "eyebrow": "Medical basics",
        "title": "疾病与医学基础：常见疾病、重点病种和药事概念怎么理解",
        "summary": "汇总常见疾病、重点病种、及核心医学概念",
        "takeaway": "适合快速建立疾病、病种、药事和医保基础概念，支持阅读医药零售资料时统一口径。",
        "displayKeywords": ["常见疾病", "重点病种", "慢病管理", "处方药", "非处方药", "医学概念"],
        "icon": "🩺",
        "visualLabel": "医学基础",
        "keywords": ["疾病与医学基础", "常见疾病", "重点病种", "医学概念", "慢病管理", "处方药", "非处方药", "门诊慢特病", "医保", "药品说明书"],
        "queries": ["疾病", "病种", "医学基础", "常见疾病", "重点病种", "慢病", "处方药", "非处方药", "门诊慢特病", "医保"],
        "includePathPrefixes": ["08-疾病与医学基础"],
        "accent": "ink",
    },
]

LEARNING_PATH = [
    {"issue": "market", "label": "先看行业全景", "note": "看医药零售整体规模、渠道结构、客流变化和品类机会。"},
    {"issue": "competition", "label": "再看平台竞争", "note": "理解美团、淘宝闪购和即时履约平台的打法差异。"},
    {"issue": "pharmacy", "label": "进入药店基本盘", "note": "看连锁药店财报、O2O 和门店指标的结构变化。"},
    {"issue": "pharma", "label": "补上药企机会", "note": "把 OTC、DTP、特药、慢病复购和即时零售连接起来。"},
    {"issue": "policy", "label": "校准监管边界", "note": "识别处方药、医保、平台监管等关键限制。"},
    {"issue": "medical", "label": "疾病与医学基础", "note": "补齐常见疾病、重点病种和核心医学概念的基础认知。"},
]

POLICY_SALES_GUIDE = [
    {
        "scope": "线上明确不得销售",
        "items": "疫苗、血液制品、麻醉药品、精神药品、医疗用毒性药品、放射性药品、药品类易制毒化学品等特殊管理药品。",
        "note": "来自《药品网络销售监督管理办法》及药品网络销售禁止清单口径，具体品种以国家药监局清单和属地监管为准。",
    },
    {
        "scope": "线上处方药可售但强约束",
        "items": "普通处方药不是简单禁售，但必须保证处方来源真实可靠，实行实名制，并做到先方后药、处方审核。",
        "note": "适合用于判断平台能力要求，不宜简化成“处方药都不能网售”。",
    },
    {
        "scope": "线下也不能随便卖",
        "items": "无资质、超经营范围、无处方销售处方药、销售假药劣药、经营被明令禁止或需特殊许可的药品，线下同样不可做。",
        "note": "线下边界主要看经营许可、经营范围、处方管理和特殊管理要求，不是一张简单品类清单。",
    },
    {
        "scope": "需要专项核验",
        "items": "GLP-1、DTP 特药、冷链处方药、医疗机构制剂、中药配方颗粒等高敏品类。",
        "note": "这些品类容易受具体适应症、销售场景、处方流转和地方规则影响，引用前要回到最新原文。",
    },
]


def md5_id(text: str) -> str:
    return "doc-" + hashlib.md5(text.encode("utf-8")).hexdigest()[:12]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sanitize_for_sharing(text: str) -> str:
    sanitized = text
    for old, new in SHARING_TEXT_REPLACEMENTS:
        sanitized = sanitized.replace(old, new)
    return sanitized


def strip_markdown(md_text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", md_text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^[#>*\-\s]+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\|", " ", text)
    return normalize_space(text)


def extract_title(stem: str, md_text: str) -> str:
    match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    return match.group(1).strip() if match else stem


def extract_summary(md_text: str) -> str:
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("|") or re.match(r"^[-:| ]+$", line):
            continue
        line = line.lstrip("> ").strip()
        if line:
            return strip_markdown(line)[:180]
    return ""


def extract_positioning(md_text: str) -> str:
    match = re.search(r"^##\s+一句话定位\s*\n+([\s\S]*?)(?=\n##\s+|\Z)", md_text, flags=re.MULTILINE)
    if not match:
        return ""
    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    if not lines:
        return ""
    return strip_markdown(lines[0])[:180]


def extract_learning_keywords(title: str, rel_path: str, content_type: str, md_text: str) -> list[str]:
    corpus = f"{title} {rel_path} {content_type} {strip_markdown(md_text)[:4000]}"
    keyword_rules = [
        ("行业规模", ["规模", "全景", "市场", "增长", "渠道"]),
        ("平台竞争", ["美团", "阿里", "淘宝闪购", "京东", "竞争", "即时零售"]),
        ("财报指标", ["财报", "业绩", "营收", "收入", "利润", "门店", "GMV"]),
        ("研报观点", ["研报", "券商", "研究报告", "核心观点"]),
        ("新闻动态", ["新闻", "动态", "资讯", "合作", "发布"]),
        ("政策监管", ["政策", "监管", "医保", "药监", "处方药", "合规"]),
        ("连锁药店", ["药店", "连锁", "大参林", "益丰", "老百姓", "一心堂", "健之佳", "国大"]),
        ("药企机会", ["药企", "OTC", "DTP", "特药", "GLP-1", "慢病"]),
        ("医学基础", ["疾病", "病种", "医学", "处方药", "非处方药", "适应症", "慢特病"]),
        ("数据口径", ["口径", "台账", "索引", "矩阵", "来源"]),
    ]
    hits: list[str] = []
    for label, tokens in keyword_rules:
        if any(token in corpus for token in tokens):
            hits.append(label)
    if content_type and content_type not in hits:
        hits.append(content_type)
    return hits[:5]


def build_learning_takeaway(title: str, rel_path: str, content_type: str, md_text: str, summary: str) -> str:
    positioning = extract_positioning(md_text)
    keywords = extract_learning_keywords(title, rel_path, content_type, md_text)
    keyword_text = "、".join(keywords) if keywords else content_type or "资料脉络"
    base = positioning or summary or f"本文围绕{title}整理核心信息。"
    base = re.sub(r"^本文定位为", "本文帮助你理解", base)
    base = base.rstrip("。；; ")
    return f"{base}。阅读后可以重点掌握：{keyword_text}；主要帮助解决“这篇资料讲什么、关键事实是什么、后续应从哪些角度继续核验/阅读”的问题。"[:260]


def extract_last_updated(rel_path: str, md_text: str) -> str:
    match = re.search(r"最后更新[：:]\s*(\d{4}-\d{2}-\d{2})", md_text)
    if match:
        return match.group(1)
    match = re.search(r"(\d{4}-\d{2}-\d{2})", rel_path)
    return match.group(1) if match else ""


def detect_content_type(parts: tuple[str, ...], stem: str, is_index: bool, is_governance: bool) -> str:
    if is_governance:
        return "治理口径"
    if is_index:
        return "索引"
    for part in parts:
        if part in CONTENT_TYPE_BY_PART:
            return CONTENT_TYPE_BY_PART[part]
    if any(part == "08-疾病与医学基础" for part in parts):
        return "医学基础"
    if "政策" in stem or "监管" in stem or "医保" in stem:
        return "政策监管"
    if any(part == "05-行业机构" for part in parts):
        return "行业报告"
    if "行业全景" in stem:
        return "行业报告"
    if "研报" in stem:
        return "研报摘要"
    if "新闻" in stem or "动态" in stem:
        return "公开新闻"
    if "财报" in stem or "公告" in stem:
        return "财报数据"
    if "报告" in stem:
        return "行业报告"
    if "摘要" in stem or "洞察" in stem:
        return "综合分析"
    return "综合分析"


def extract_module_entity(parts: tuple[str, ...], stem: str) -> tuple[str, str]:
    module = ""
    entity = ""
    for idx, part in enumerate(parts):
        if re.match(r"^\d{2}-", part):
            module = part
            continue
        if not module:
            continue
        if part in {"财报数据", "官方财报数据", "公开新闻", "研报摘要", "综合分析"}:
            continue
        if part == "_index.md" or part.startswith("_"):
            continue
        if idx == len(parts) - 1 and part.endswith(".md"):
            continue
        entity = part
    return module, entity


def detect_citation_status(text: str, path: str) -> str:
    sample = text[:5000]
    if "可供研判参考" in sample or "✅可供研判参考" in sample:
        return "可供研判参考"
    if "✅可引用" in sample or "可正式引用" in sample or "官方披露" in sample or "官方年报已归档" in sample:
        return "可正式引用"
    if "⚠️慎用" in sample or "慎用" in sample or "口径冲突" in sample:
        return "慎用"
    if "待确认" in sample or "待核验" in sample or "待补" in sample or "搜索摘要" in sample:
        return "需核验"
    if "可内部用" in sample or "内部线索" in sample:
        return "可内部用"
    if "政策" in path or "研报" in path:
        return "需核验"
    return "可内部用"


def classify_table_html(table_html: str) -> tuple[str, str]:
    plain = re.sub(r"<.*?>", "", table_html)
    plain = html.unescape(plain)
    if "来源/文献" in plain and "公开观点或信息" in plain:
        return "table-scroll source-summary-table-scroll", "source-summary-table"
    if "财报项目/来源" in plain and "披露内容与经营信号" in plain:
        return "table-scroll source-financial-table-scroll", "source-financial-table"
    if "来源" in plain and "本文使用内容" in plain and "引用边界" in plain:
        return "table-scroll source-boundary-table-scroll", "source-boundary-table"
    return "table-scroll", ""


def wrap_table_html(match: re.Match[str]) -> str:
    table_html = match.group(1)
    wrapper_class, table_class = classify_table_html(table_html)
    if table_class:
        table_html = table_html.replace("<table>", f'<table class="{table_class}">', 1)
    return f'<div class="{wrapper_class}">{table_html}</div>'


def convert_markdown(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=[TableExtension(), FencedCodeExtension()],
        tab_length=4,
    )
    rendered = md.convert(md_text)
    rendered = add_heading_anchors(rendered)
    rendered = linkify_plain_urls(rendered)
    rendered = ensure_external_links_open_new_tab(rendered)
    rendered = re.sub(r"(<table>.*?</table>)", wrap_table_html, rendered, flags=re.S)
    return rendered

def add_heading_anchors(rendered_html: str) -> str:
    heading_index = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal heading_index
        heading_index += 1
        tag = match.group(1)
        attrs = match.group(2) or ""
        body = match.group(3)
        if " id=" in attrs:
            return match.group(0)
        return f'<{tag}{attrs} id="doc-heading-{heading_index}">{body}</{tag}>'

    return re.sub(r"<(h[2-4])([^>]*)>(.*?)</\1>", repl, rendered_html, flags=re.S)


def linkify_plain_urls(rendered_html: str) -> str:
    url_pattern = re.compile(r'(?<!["\'=])(https?://[^\s<]+)')

    def repl(match: re.Match[str]) -> str:
        url = match.group(1)
        trailing = ""
        while url and url[-1] in ".,;:!?，。；：！？）)]":
            trailing = url[-1] + trailing
            url = url[:-1]
        safe_url = html.escape(url, quote=True)
        return f'<a class="external-link" href="{safe_url}" target="_blank" rel="noopener noreferrer">{html.escape(url)}</a>{trailing}'

    return url_pattern.sub(repl, rendered_html)


def ensure_external_links_open_new_tab(rendered_html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        attrs = match.group(1)
        if not re.search(r'href=["\']https?://', attrs, flags=re.I):
            return match.group(0)
        if not re.search(r'\starget=', attrs, flags=re.I):
            attrs += ' target="_blank"'
        if not re.search(r'\srel=', attrs, flags=re.I):
            attrs += ' rel="noopener noreferrer"'
        if not re.search(r'\sclass=', attrs, flags=re.I):
            attrs += ' class="external-link"'
        elif "external-link" not in attrs:
            attrs = re.sub(r'class=(["\'])(.*?)\1', lambda m: f'class={m.group(1)}{m.group(2)} external-link{m.group(1)}', attrs, count=1)
        return f"<a{attrs}>"

    return re.sub(r"<a([^>]*?)>", repl, rendered_html, flags=re.I)


def resolve_wiki_links(rendered_html: str, slug_map: dict[str, str]) -> tuple[str, list[str]]:
    outgoing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        label = match.group(1).strip()
        target = label.split("|", 1)[0].strip()
        doc_id = slug_map.get(target)
        if not doc_id:
            return f'<span class="wiki-link missing">{html.escape(label)}</span>'
        outgoing.append(doc_id)
        return f'<a class="wiki-link" href="#doc/{doc_id}" data-doc="{doc_id}">{html.escape(label)}</a>'

    return re.sub(r"\[\[([^\]]+)\]\]", repl, rendered_html), outgoing


def extract_headings(md_text: str) -> list[dict[str, str]]:
    headings = []
    heading_index = 0
    for match in re.finditer(r"^(#{2,4})\s+(.+)$", md_text, flags=re.MULTILINE):
        heading_index += 1
        level = len(match.group(1))
        text = strip_markdown(match.group(2))[:80]
        headings.append({"level": level, "text": text, "anchor": f"doc-heading-{heading_index}"})
    return headings[:18]


def build_search_aliases(rel_path: str, raw_md_text: str, title: str) -> str:
    """Keep search-friendly entity aliases without changing public display text."""
    corpus = f"{rel_path}\n{title}\n{raw_md_text[:5000]}"
    aliases: list[str] = []
    alias_rules = [
        ("京东健康", ["京东健康", "JD Health"]),
        ("京东秒送", ["京东秒送"]),
        ("京东大药房", ["京东大药房"]),
    ]
    for key, values in alias_rules:
        if key in corpus:
            aliases.extend(values)
    if "京东" in corpus:
        aliases.extend(["京东", "京东买药", "京东药急送", "京东互联网医院"])
    return " ".join(dict.fromkeys(aliases))


def scan_documents() -> tuple[list[dict], dict[str, str]]:
    doc_image_map = load_doc_image_map()
    md_files = sorted(
        path for path in BASE_DIR.rglob("*.md")
        if "__pycache__" not in path.parts and not any(part.startswith(".") for part in path.parts)
    )
    slug_map: dict[str, str] = {}
    path_to_id: dict[Path, str] = {}

    for path in md_files:
        if not is_public_industry_doc(path):
            continue
        rel = path.relative_to(BASE_DIR).as_posix()
        doc_id = md5_id(rel)
        path_to_id[path] = doc_id
        stem = path.stem
        slug_map.setdefault(stem, doc_id)

    docs: list[dict] = []
    for path in md_files:
        if path not in path_to_id:
            continue
        rel_path = path.relative_to(BASE_DIR).as_posix()
        parts = tuple(Path(rel_path).parts)
        stem = path.stem
        md_text = sanitize_for_sharing(path.read_text(encoding="utf-8"))
        is_index = path.name == "_index.md"
        is_governance = stem in GOVERNANCE_FILES or stem.startswith("行业信息库校验报告")
        module, entity = extract_module_entity(parts, stem)
        content_type = detect_content_type(parts, stem, is_index, is_governance)
        ranking_md_text = content_for_ranking(md_text)
        raw_text = strip_markdown(md_text)
        ranking_raw_text = strip_markdown(ranking_md_text)
        rendered = convert_markdown(md_text)
        rendered, outgoing = resolve_wiki_links(rendered, slug_map)
        title = sanitize_for_sharing(extract_title(stem, ranking_md_text))
        summary = extract_summary(ranking_md_text)
        doc = {
            "id": path_to_id[path],
            "title": title,
            "path": rel_path,
            "stem": stem,
            "module": module,
            "entity": entity,
            "contentType": content_type,
            "isIndex": is_index,
            "isGovernance": is_governance,
            "summary": summary,
            "searchAliases": build_search_aliases(rel_path, md_text, title),
            "learningTakeaway": build_learning_takeaway(title, rel_path, content_type, ranking_md_text, summary),
            "lastUpdated": extract_last_updated(rel_path, ranking_md_text),
            "citationStatus": detect_citation_status(ranking_md_text + " " + ranking_raw_text, rel_path),
            "coverImage": doc_image_map.get(path_to_id[path], ""),
            "html": rendered,
            "rawText": ranking_raw_text[:28000],
            "headings": extract_headings(md_text),
            "outgoing": outgoing,
        }
        docs.append(doc)

    id_to_doc = {doc["id"]: doc for doc in docs}
    for doc in docs:
        linked_docs = [id_to_doc[target_id] for target_id in doc.get("outgoing", []) if target_id in id_to_doc]
        linked_corpus = " ".join(
            f"{linked.get('path', '')} {linked.get('contentType', '')} {linked.get('citationStatus', '')} {linked.get('title', '')}"
            for linked in linked_docs
        )
        doc_corpus = f"{doc.get('path', '')} {doc.get('contentType', '')} {doc.get('rawText', '')}"
        if any(token in linked_corpus or token in doc_corpus for token in ("研报摘要", "券商研报", "行研报告", "研究报告", "可供研判参考", "核心观点（5条）", "核心观点(5条)")):
            doc["citationStatus"] = "可供研判参考"
        elif doc["citationStatus"] == "可供研判参考" and "研报" not in doc.get("path", ""):
            doc["citationStatus"] = "可正式引用"
    return docs, slug_map


def is_public_industry_doc(path: Path) -> bool:
    """Only expose real industry-information documents in the public site."""
    if path.name == "_index.md":
        return False
    stem = path.stem
    rel = path.relative_to(BASE_DIR).as_posix()
    if not rel.startswith(PUBLIC_CONTENT_PREFIXES):
        return False
    if stem.endswith("业务洞察") and rel not in PUBLIC_BUSINESS_INSIGHT_FILES:
        return False
    if "研报摘要" in rel and rel not in PUBLIC_RESEARCH_SUMMARY_FILES:
        return False
    if is_stale_news_doc(path):
        return False
    if stem in GOVERNANCE_FILES or stem.startswith("行业信息库校验报告"):
        return False
    if any(pattern in stem or pattern in rel for pattern in HIDDEN_CONTENT_PATTERNS):
        return False
    return True


def is_stale_news_doc(path: Path) -> bool:
    rel = path.relative_to(BASE_DIR).as_posix()
    if "公开新闻" not in rel and "新闻动态" not in rel:
        return False
    years = [int(year) for year in re.findall(r"20\d{2}", rel)]
    if not years:
        return False
    return max(years) < MIN_NEWS_YEAR


def content_type_rank(doc: dict) -> int:
    content_type = doc.get("contentType", "")
    if content_type == "财报数据":
        return 0
    if content_type == "行业报告":
        return 1
    if content_type == "研报摘要":
        return 2
    if content_type == "公开新闻":
        return 3
    if content_type == "政策监管":
        return 4
    if content_type == "综合分析":
        return 5
    return 8


def issue_content_rank(doc: dict, issue: dict) -> int:
    if issue.get("id") == "market" and "医药零售行业全景摘要" in doc.get("title", ""):
        return -1
    if issue.get("id") == "policy" and doc.get("contentType") == "政策监管":
        return 0
    return content_type_rank(doc)


def doc_dedupe_key(doc: dict) -> str:
    title = re.sub(r"[\s·：:（）()《》\-—_]+", "", doc.get("title", ""))
    return title or doc.get("id", "")


def issue_score(doc: dict, issue: dict) -> int:
    haystack = " ".join([
        doc.get("title", ""),
        doc.get("path", ""),
        doc.get("summary", ""),
        doc.get("searchAliases", ""),
        doc.get("module", ""),
        doc.get("entity", ""),
        doc.get("rawText", "")[:5000],
    ])
    score = 0
    for keyword in issue["keywords"] + issue["queries"]:
        if keyword and keyword in haystack:
            score += 5 if keyword in doc.get("title", "") or keyword in doc.get("path", "") else 2
    if doc.get("isGovernance") and issue["id"] in {"market", "jd", "policy"}:
        score += 1
    return score


def path_allowed_for_issue(doc: dict, issue: dict) -> bool:
    path = doc.get("path", "")
    include = issue.get("includePathPrefixes") or []
    exclude = issue.get("excludePathPrefixes") or []
    if include and not any(path.startswith(prefix) for prefix in include):
        return False
    if exclude and any(path.startswith(prefix) for prefix in exclude):
        return False
    return True


def recommended_doc_score(doc: dict, issue: dict, keywords: list[str]) -> int:
    visible_corpus = " ".join([
        doc.get("title", ""),
        doc.get("summary", ""),
        doc.get("path", ""),
        doc.get("contentType", ""),
    ]).lower()
    raw_corpus = doc.get("rawText", "")[:2400].lower()
    match_score = 0
    visible_hit = False
    for keyword in keywords:
        key = keyword.lower()
        if not key:
            continue
        title_path = " ".join([doc.get("title", ""), doc.get("path", "")]).lower()
        if key in title_path:
            match_score += 18
            visible_hit = True
        elif key in visible_corpus:
            match_score += 10
            visible_hit = True
        elif visible_hit and key in raw_corpus:
            match_score += 2
    if not visible_hit:
        return 0
    if issue_score(doc, issue) > 0:
        match_score += 4
    if doc.get("citationStatus") == "可正式引用":
        match_score += 3
    elif doc.get("citationStatus") == "可供研判参考":
        match_score += 1
    return match_score


def build_recommended_groups(docs: list[dict], issue: dict) -> list[dict]:
    groups = []
    rules = RECOMMENDED_READING_RULES.get(issue.get("id"), [])
    for rule in rules:
        candidates = []
        seen: set[str] = set()
        for doc in docs:
            if doc["isIndex"]:
                continue
            if not path_allowed_for_issue(doc, issue):
                continue
            score = recommended_doc_score(doc, issue, rule["keywords"])
            if score <= 0:
                continue
            dedupe_key = doc_dedupe_key(doc)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            candidates.append((score, doc))
        candidates.sort(
            key=lambda item: (
                item[0],
                item[1].get("lastUpdated", ""),
                1 if item[1].get("citationStatus") == "可正式引用" else 0,
                item[1].get("title", ""),
            ),
            reverse=True,
        )
        groups.append({
            "label": rule["label"],
            "docs": [{
                "id": doc["id"],
                "title": doc["title"],
                "summary": doc["summary"],
                "path": doc["path"],
                "contentType": doc["contentType"],
                "citationStatus": doc["citationStatus"],
                "lastUpdated": doc["lastUpdated"],
                "coverImage": doc.get("coverImage", ""),
            } for _, doc in candidates[:4]],
        })
    return groups


def build_issues(docs: list[dict]) -> list[dict]:
    issues = []
    for issue in STRATEGIC_ISSUES:
        scored = sorted(
            ((issue_score(doc, issue), doc) for doc in docs),
            key=lambda item: (issue_content_rank(item[1], issue), -item[0], item[1]["path"]),
        )
        seen: set[str] = set()
        related = []
        for score, doc in scored:
            if score <= 0 or doc["isIndex"]:
                continue
            if not path_allowed_for_issue(doc, issue):
                continue
            dedupe_key = doc_dedupe_key(doc)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            related.append({
                "id": doc["id"],
                "title": doc["title"],
                "summary": doc["summary"],
                "path": doc["path"],
                "contentType": doc["contentType"],
                "citationStatus": doc["citationStatus"],
                "coverImage": doc.get("coverImage", ""),
            })
            if len(related) >= 10:
                break
        issues.append({**issue, "relatedDocs": related, "recommendedGroups": build_recommended_groups(docs, issue)})
    return issues


def build_modules(docs: list[dict]) -> list[dict]:
    modules: dict[str, dict] = {}
    for doc in docs:
        module = doc.get("module") or "校验与口径"
        modules.setdefault(module, {"name": module, "count": 0, "docs": [], "entities": defaultdict(int)})
        modules[module]["count"] += 1
        modules[module]["docs"].append({
            "id": doc["id"],
            "title": doc["title"],
            "contentType": doc["contentType"],
            "citationStatus": doc["citationStatus"],
            "path": doc["path"],
        })
        if doc.get("entity"):
            modules[module]["entities"][doc["entity"]] += 1

    result = []
    for module in sorted(modules.values(), key=lambda m: m["name"]):
        module["entities"] = [{"name": k, "count": v} for k, v in sorted(module["entities"].items())]
        module["docs"] = sorted(
            module["docs"],
            key=lambda d: (content_type_rank(d), d["title"]),
        )
        result.append(module)
    return result


def build_stats(docs: list[dict]) -> dict:
    status_counts = defaultdict(int)
    type_counts = defaultdict(int)
    for doc in docs:
        status_counts[doc["citationStatus"]] += 1
        type_counts[doc["contentType"]] += 1
    updated = sorted([d["lastUpdated"] for d in docs if d["lastUpdated"]], reverse=True)
    return {
        "docCount": len(docs),
        "moduleCount": len({d["module"] for d in docs if d["module"]}),
        "officialCount": status_counts["可正式引用"],
        "medicalCount": len([d for d in docs if d["path"].startswith("08-疾病与医学基础/")]),
        "latestUpdate": updated[0] if updated else "",
        "statusCounts": dict(status_counts),
        "typeCounts": dict(type_counts),
    }


def find_doc_by_stem(docs: list[dict], stem: str) -> dict | None:
    return next((doc for doc in docs if doc.get("stem") == stem), None)


def build_weekly_changes(docs: list[dict]) -> dict:
    doc = find_doc_by_stem(docs, "本周行业变化")
    latest = find_doc_by_stem(docs, "行业最新权威资讯")

    def find_doc_id(*stems: str) -> str:
        for stem in stems:
            matched = find_doc_by_stem(docs, stem)
            if matched:
                return matched["id"]
        return doc["id"] if doc else ""

    return {
        "title": "本周行业变化",
        "subtitle": "结论 + 影响总结",
        "docId": doc["id"] if doc else "",
        "sourceDocId": latest["id"] if latest else "",
        "updated": doc.get("lastUpdated", "") if doc else "",
        "items": [
            {
                "type": "医保支付",
                "conclusion": "医保支付方式改革、参照药沟通和医保基金监管仍是本周医药行业的重要政策线索。",
                "impact": "影响处方药、慢特病、创新药支付和零售药店合规经营边界，需要回到医保局原文跟踪细则。",
                "docId": find_doc_id("医保政策汇总"),
            },
            {
                "type": "药品监管",
                "conclusion": "药品监管侧持续关注创新药、血液制品质量安全、医疗器械经营和网络销售监管。",
                "impact": "影响药品/器械线上销售资质、质量管理和合规履约。",
                "docId": find_doc_id("处方药监管政策", "药品流通政策汇总"),
            },
            {
                "type": "行业资讯",
                "conclusion": "权威资讯更新以国家医保局、国家药监局等官方入口为主。",
                "impact": "适合作为政策和监管变化索引，暂不直接生成商业判断。",
                "docId": find_doc_id("行业最新权威资讯"),
            },
        ],
    }


def build_competition_radar(docs: list[dict]) -> dict:
    doc = find_doc_by_stem(docs, "竞争雷达_美团阿里京东")
    def find_contains(*tokens: str) -> str:
        for candidate in docs:
            text = f"{candidate.get('path','')} {candidate.get('title','')}"
            if all(token in text for token in tokens):
                return candidate.get("id", "")
        return ""
    return {
        "title": "竞争雷达",
        "subtitle": "美团 / 阿里 / 京东每周监控",
        "docId": doc["id"] if doc else "",
        "updated": doc.get("lastUpdated", "") if doc else "",
        "platforms": [
            {
                "name": "美团",
                "focus": "美团买药 / 即时零售 / 到店到家",
                "action": "关注供给密度、履约效率、药店合作和补贴变化。",
                "impact": "影响医药即时零售用户触达、商家合作和品类供给。",
                "signals": ["补贴", "供给", "履约", "药店合作"],
                "docId": find_contains("美团", "新闻"),
            },
            {
                "name": "阿里",
                "focus": "淘宝闪购 / 饿了么 / 阿里健康",
                "action": "关注流量入口、本地生活协同、即时配送和医药健康连接。",
                "impact": "影响平台竞争、商家供给和用户心智迁移。",
                "signals": ["淘宝闪购", "饿了么", "会员", "履约"],
                "docId": find_contains("阿里", "新闻"),
            },
            {
                "name": "京东",
                "focus": "京东健康 / 京东秒送 / 京东买药",
                "action": "关注自营供应链、药品供给、即时履约和健康服务闭环。",
                "impact": "影响医药服务能力、履约体验和用户信任。",
                "signals": ["京东健康", "京东秒送", "药品供给", "服务闭环"],
                "docId": find_contains("京东"),
            },
        ],
    }


def build_site_data() -> dict:
    docs, slug_map = scan_documents()
    issues = build_issues(docs)
    return {
        "documents": docs,
        "issues": issues,
        "learningPath": LEARNING_PATH,
        "policyGuide": POLICY_SALES_GUIDE,
        "modules": build_modules(docs),
        "weeklyChanges": build_weekly_changes(docs),
        "competitionRadar": build_competition_radar(docs),
        "stats": build_stats(docs),
        "buildTime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "slugMap": slug_map,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>即时零售医药行业信息库</title>
<style>
:root {
  --paper: #fff7f5;
  --paper-2: #fff0ed;
  --panel: #ffffff;
  --ink: #17202a;
  --muted: #66717f;
  --soft: #8b95a2;
  --line: #f0d1cc;
  --line-strong: #e7aca4;
  --blue: #DA291C;
  --red: #DA291C;
  --jd-red: #DA291C;
  --jd-red-dark: #A61911;
  --jd-red-deep: #7A120C;
  --jd-red-soft: #FFE0D9;
  --jd-red-pale: #FFF3F0;
  --green: #2f6f5e;
  --gold: #a46d18;
  --purple: #67568a;
  --shadow: 0 18px 42px rgba(23,32,42,.08);
  --radius: 8px;
  --serif: "Georgia", "Times New Roman", "Noto Serif SC", "Songti SC", serif;
  --sans: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", system-ui, sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background:
    linear-gradient(90deg, rgba(23,32,42,.035) 1px, transparent 1px) 0 0/48px 48px,
    linear-gradient(180deg, #FFF7F5 0%, #FFF0ED 42%, #FFFFFF 100%);
  color: var(--ink);
  font-family: var(--sans);
  line-height: 1.65;
}
button, input { font: inherit; }
button {
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  color: inherit;
}
a { color: inherit; }
.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 0 28px;
  background: rgba(255,247,245,.94);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(16px);
}
.brand {
  display: flex;
  flex-direction: column;
  min-width: 218px;
  letter-spacing: 0;
}
.brand strong { font-size: 15px; line-height: 1.2; }
.brand span { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; }
.nav-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,.72);
  border-radius: var(--radius);
}
.nav-tabs button {
  border: 0;
  background: transparent;
  color: var(--muted);
  padding: 7px 12px;
  border-radius: 6px;
  font-size: 13px;
}
.nav-tabs button.active {
  color: var(--ink);
  background: var(--panel);
  box-shadow: 0 2px 10px rgba(23,32,42,.08);
}
.topbar-actions {
  min-width: 152px;
  display:flex;
  align-items:center;
  gap:8px;
}
.top-back-link {
  display:none;
  border:1px solid rgba(15,111,127,.22);
  background:#fff;
  color:var(--green);
  border-radius:999px;
  padding:8px 13px;
  font-size:13px;
  font-weight:900;
  box-shadow:0 8px 20px rgba(31,41,51,.05);
}
.top-back-link.visible { display:inline-flex; }
.top-back-link:hover { border-color:rgba(15,111,127,.42); transform:translateY(-1px); }
.global-search {
  flex: 1;
  max-width: 520px;
  margin-left: auto;
  position: relative;
}
.global-search input {
  width: 100%;
  border: 1px solid var(--line-strong);
  background: #fff;
  border-radius: var(--radius);
  height: 38px;
  padding: 0 14px 0 40px;
  color: var(--ink);
  outline: none;
  box-shadow: 0 2px 16px rgba(23,32,42,.04);
}
.global-search input:focus { border-color: var(--blue); box-shadow: 0 0 0 3px rgba(49,95,143,.12); }
.search-mark { position: absolute; left: 13px; top: 8px; color: var(--muted); }
.auth-area {
  min-width: 118px;
  display: flex;
  justify-content: flex-end;
}
.auth-button,
.logout-button {
  border: 1px solid var(--line-strong);
  background: #fff;
  border-radius: 6px;
  padding: 7px 11px;
  font-size: 13px;
  color: #24313e;
}
.auth-button:hover,
.logout-button:hover { border-color: var(--blue); color: var(--blue); }
.auth-user {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: 12px;
}
.auth-user strong { color: var(--ink); font-size: 13px; }
.locked-section {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: start center;
  padding: 86px 24px;
}
.login-card {
  width: min(440px, 100%);
  background: #fff;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 28px;
}
.login-card .kicker { margin-bottom: 14px; }
.login-card h2 {
  margin: 0;
  font-family: var(--serif);
  font-size: 30px;
  line-height: 1.2;
}
.login-card p {
  margin: 10px 0 20px;
  color: var(--muted);
}
.login-form {
  display: grid;
  gap: 12px;
}
.login-form label {
  display: grid;
  gap: 6px;
  color: #283543;
  font-size: 13px;
  font-weight: 700;
}
.login-form input {
  width: 100%;
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  padding: 10px 11px;
  outline: 0;
  background: #fbfbf9;
}
.login-form input:focus {
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(49,95,143,.12);
}
.login-submit {
  margin-top: 4px;
  border: 1px solid #17202a;
  background: #17202a;
  color: #fff;
  border-radius: 6px;
  padding: 10px 12px;
  font-weight: 700;
}
.login-error {
  min-height: 18px;
  color: var(--red);
  font-size: 12px;
}
.page {
  min-height: calc(100vh - 64px);
}
.view { display: none; }
.view.active { display: block; }
.hero {
  max-width: 1240px;
  margin: 0 auto;
  display:grid;
  place-items:center;
  padding: 34px 28px 24px;
}
.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.06fr) minmax(360px, .94fr);
  gap: 28px;
  align-items: stretch;
  border: 1px solid rgba(22, 104, 127, .16);
  border-radius: 34px;
  padding: 28px;
  background:
    radial-gradient(circle at 5% 0%, rgba(49, 174, 167, .18), transparent 34%),
    linear-gradient(135deg, rgba(255,255,255,.96), rgba(235, 248, 247, .88));
  box-shadow: 0 24px 70px rgba(14, 66, 86, .10);
  overflow: hidden;
  position: relative;
}
.hero-grid::after {
  content: "";
  position: absolute;
  inset: auto -80px -130px auto;
  width: 340px;
  height: 340px;
  border-radius: 999px;
  background: rgba(34, 151, 159, .10);
}
.hero-copy { position: relative; z-index: 1; }
.kicker {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: #DA291C;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .12em;
  font-weight: 800;
}
.kicker::before {
  content: "";
  width: 34px;
  height: 1px;
  background: #DA291C;
}
.hero h1 {
  font-family: var(--serif);
  font-size: clamp(42px, 5.4vw, 76px);
  line-height: 1.02;
  letter-spacing: -.03em;
  margin: 18px 0 18px;
  max-width: 820px;
}
.hero-lead {
  max-width: 780px;
  color: #39424c;
  font-size: 18px;
  line-height: 1.75;
}
.hero-actions { display:flex; gap:12px; flex-wrap:wrap; margin-top:20px; }
.hero-search {
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 560px;
  min-height: 48px;
  padding: 0 14px;
  border: 1px solid rgba(15,111,127,.20);
  border-radius: 999px;
  background: rgba(255,255,255,.86);
  box-shadow: 0 12px 30px rgba(14,66,86,.07);
}
.hero-search input {
  flex: 1;
  border: 0;
  background: transparent;
  outline: 0;
  font-size: 15px;
  color: var(--ink);
}
.medical-visual {
  position: relative;
  z-index: 1;
  min-height: 360px;
  border-radius: 28px;
  background:
    linear-gradient(145deg, rgba(19,90,118,.95), rgba(18,148,151,.78)),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,.28), transparent 28%);
  color: #fff;
  overflow: hidden;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.20);
}
.medical-visual::before {
  content: "";
  position:absolute;
  inset:0;
  opacity:.22;
  background-image: linear-gradient(rgba(255,255,255,.24) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.24) 1px, transparent 1px);
  background-size: 34px 34px;
}
.medical-visual-inner { position:relative; padding:26px; height:100%; }
.visual-badge { display:inline-flex; align-items:center; gap:8px; border:1px solid rgba(255,255,255,.28); background:rgba(255,255,255,.12); border-radius:999px; padding:7px 11px; font-size:12px; }
.pill-scene { position:absolute; inset:70px 24px 24px; min-height:80%; display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); grid-template-rows: minmax(156px, 1fr) minmax(124px, .78fr); gap:16px; justify-content:stretch; align-content:stretch; align-items:stretch; }
.med-card { position:relative; border:1px solid rgba(255,255,255,.30); background:rgba(255,255,255,.16); backdrop-filter: blur(8px); border-radius:24px; padding:16px; box-shadow:0 18px 40px rgba(0,0,0,.12); color:#fff; text-align:left; cursor:pointer; display:flex; flex-direction:column; justify-content:space-between; align-items:stretch; min-width:0; min-height:0; overflow:hidden; transition: transform .16s ease, background .16s ease; }
.med-card:hover { transform: translateY(-2px); background:rgba(255,255,255,.22); }
.med-card.news { grid-column:1; grid-row:1; width:100%; height:100%; }
.med-card.drug { grid-column:2; grid-row:1; width:100%; height:100%; }
.med-card.chart { grid-column:1 / -1; grid-row:2; min-height:124px; padding:16px 18px; justify-content:center; gap:8px; }
.med-icon { font-size:30px; margin-bottom:8px; line-height:1; }
.med-card h3 { margin:0 0 5px; font-size:18px; line-height:1.22; color:#fff; }
.med-card p { margin:0; color:rgba(255,255,255,.80); font-size:13px; line-height:1.42; }
.med-card-link { margin-top:10px; color:#fff; font-weight:800; font-size:13px; line-height:1.2; }
.med-card.chart .med-card-link { margin-top:10px; transform:none; }
.chart-line { margin-top:8px; height:24px; border-radius:12px; background: linear-gradient(135deg, transparent 45%, rgba(255,255,255,.75) 47%, transparent 50%), linear-gradient(90deg, rgba(255,255,255,.10), rgba(255,255,255,.18)); }
.btn {
  border: 1px solid var(--ink);
  background: var(--ink);
  color: #fff;
  min-height: 38px;
  padding: 8px 13px;
  border-radius: var(--radius);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.btn.secondary { background: transparent; color: var(--ink); border-color: var(--line-strong); }
.executive-panel {
  background: rgba(255,255,255,.86);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow);
  margin-top: 8px;
}
.snapshot-section {
  max-width: 1240px;
  margin: 0 auto;
  padding: 18px 28px 70px;
}
.snapshot-section .executive-panel { margin-top: 0; }
.briefing-section {
  max-width: 1240px;
  margin: 0 auto;
  padding: 18px 28px 20px;
}
.weekly-layout { display:grid; grid-template-columns: minmax(0,.95fr) minmax(0,1.35fr); gap:14px; align-items:stretch; }
.weekly-lead-card {
  border: 1px solid rgba(15,111,127,.18);
  border-radius: 26px;
  background: linear-gradient(145deg, #fff, #edf9f8);
  padding: 22px;
  min-height: 100%;
  box-shadow: var(--shadow-sm);
}
.weekly-lead-card .news-icon { width:52px; height:52px; display:grid; place-items:center; border-radius:18px; background:rgba(15,111,127,.10); font-size:26px; margin-bottom:14px; }
.weekly-grid, .radar-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.briefing-card, .radar-card {
  border: 1px solid var(--line);
  border-radius: 22px;
  background: rgba(255,255,255,.92);
  padding: 18px;
  box-shadow: var(--shadow-sm);
}
.briefing-card { display:flex; flex-direction:column; min-height: 232px; }
.card-action { margin-top:auto; padding-top:8px; }
.briefing-card h3, .radar-card h3 { margin: 8px 0 4px; font-family: var(--serif); font-size: 19px; }
.briefing-card p, .radar-card p { color: var(--muted); margin: 3px 0 8px; line-height:1.55; }
.radar-section { position: relative; }
.radar-card { position:relative; overflow:hidden; }
.radar-card::before { content:""; position:absolute; inset:auto -42px -64px auto; width:150px; height:150px; border-radius:999px; border:1px solid rgba(15,111,127,.14); box-shadow:0 0 0 18px rgba(15,111,127,.035),0 0 0 38px rgba(15,111,127,.025); }
.radar-top { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; position:relative; }
.platform-mark { width:42px; height:42px; display:grid; place-items:center; border-radius:16px; background:rgba(218,41,28,.09); font-weight:800; color:#DA291C; }
.radar-signals { display:flex; gap:6px; flex-wrap:wrap; margin-top:10px; position:relative; }
.snapshot-section .metric-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.panel-title {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--line);
}
.panel-title h2 { font-size: 15px; margin: 0; }
.panel-title span { color: var(--muted); font-size: 12px; }
.metric-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
.metric { border-left: 2px solid var(--blue); padding: 2px 0 2px 12px; }
.metric strong { display: block; font-family: var(--serif); font-size: 26px; line-height: 1.1; }
.metric span { color: var(--muted); font-size: 12px; }
.issue-section, .path-section, .search-section, .library-section { max-width: 1240px; margin: 0 auto; padding: 26px 28px; }
.section-head { display: flex; justify-content: space-between; align-items: end; gap: 18px; margin-bottom: 16px; }
.section-head h2 { font-family: var(--serif); font-size: 30px; margin: 0; }
.section-head p { max-width: 560px; margin: 0; color: var(--muted); font-size: 14px; }
.issue-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.issue-card {
  background: rgba(255,255,255,.92);
  border: 1px solid var(--line);
  border-radius: 26px;
  min-height: 292px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(23,32,42,.045);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.issue-card:hover { transform: translateY(-3px); box-shadow: var(--shadow); border-color: rgba(15,111,127,.28); }
.issue-card-top { display:flex; align-items:center; gap:12px; }
.issue-icon { width:48px; height:48px; display:grid; place-items:center; border-radius:18px; background:rgba(15,111,127,.08); font-size:25px; }
.issue-card .eyebrow { font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); font-weight: 700; }
.issue-card h3 { margin: 0; font-size: 20px; line-height: 1.28; }
.issue-card p { margin: 0; color: #46515c; font-size: 14px; }
.issue-card .takeaway { border-top: 1px solid var(--line); padding-top: 12px; color: var(--ink); }
.keyword-strip { display:flex; gap:6px; flex-wrap:wrap; margin:2px 0 4px; }
.issue-footer { margin-top: auto; display: flex; justify-content: flex-end; align-items: center; gap: 10px; }
.tag {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line);
  color: var(--muted);
  background: rgba(255,255,255,.76);
  border-radius: 999px;
  padding: 3px 9px;
  font-size: 12px;
}
.text-link { border: 0; background: transparent; color: var(--blue); padding: 0; text-align: left; font-weight: 700; cursor:pointer; }
.accent-blue { border-top: 3px solid var(--blue); }
.accent-red { border-top: 3px solid var(--red); }
.accent-green { border-top: 3px solid var(--green); }
.accent-purple { border-top: 3px solid var(--purple); }
.accent-gold { border-top: 3px solid var(--gold); }
.accent-ink { border-top: 3px solid var(--ink); }
.path-strip { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); border: 1px solid var(--line); background: rgba(255,255,255,.82); border-radius: var(--radius); overflow: hidden; }
.path-step { min-height: 164px; padding: 16px; border-right: 1px solid var(--line); }
.path-step:last-child { border-right: 0; }
.path-step .num { font-family: var(--serif); font-size: 34px; color: var(--red); }
.path-step h3 { margin: 5px 0 8px; font-size: 15px; }
.path-step p { margin: 0; color: var(--muted); font-size: 13px; }
.search-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 18px;
}
.query-panel, .result-panel, .doc-shell, .library-panel, .issue-detail {
  background: rgba(255,255,255,.9);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: 0 10px 28px rgba(23,32,42,.045);
}
.query-panel { padding: 18px; }
.query-panel h3 { margin: 0 0 12px; font-size: 16px; }
.quick-query {
  width: 100%;
  text-align: left;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: var(--radius);
  padding: 10px 11px;
  margin: 0 0 8px;
  color: #34404c;
}
.quick-query:hover { border-color: var(--blue); }
.result-panel { padding: 18px; min-height: 420px; }
.result-item {
  border-bottom: 1px solid var(--line);
  padding: 14px 0;
}
.result-item:first-child { padding-top: 0; }
.result-item:last-child { border-bottom: 0; }
.result-kind {
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .08em;
  font-size: 11px;
  font-weight: 700;
}
.result-item h3 { margin: 4px 0 6px; font-size: 18px; }
.result-item p { margin: 0 0 8px; color: #46515c; font-size: 14px; }
mark { background: #fff1b8; color: inherit; padding: 0 2px; }
.issue-page {
  max-width: 1240px;
  margin: 0 auto;
  padding: 32px 28px 70px;
}
.issue-detail {
  padding: 28px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 28px;
}
.issue-detail h1 {
  font-family: var(--serif);
  font-size: 42px;
  line-height: 1.08;
  margin: 10px 0 16px;
}
.related-list { display: grid; gap: 10px; }
.related-doc {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: var(--radius);
  padding: 12px;
}
.related-doc h4 { margin: 0 0 5px; font-size: 15px; }
.related-doc p { margin: 0; color: var(--muted); font-size: 13px; }
.recommended-groups { display: grid; gap: 18px; margin-top: 12px; }
.recommended-group { border: 1px solid var(--line); border-radius: 20px; background: rgba(255,255,255,.88); padding: 16px; }
.recommended-group h3 { margin: 0 0 12px; font-size: 18px; font-family: var(--serif); }
.recommended-doc-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.recommended-doc { border: 1px solid var(--line); border-radius: 16px; padding: 12px; background: #fff; }
.recommended-doc h4 { margin: 0 0 6px; font-size: 15px; }
.recommended-doc p { margin: 0; color: var(--muted); font-size: 13px; }
.group-entry-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }
.group-entry-card { border: 1px solid var(--line); border-radius: 20px; background: #fff; padding: 16px; text-align: left; cursor: pointer; box-shadow: var(--shadow-sm); transition: transform .16s ease, border-color .16s ease; }
.group-entry-card:hover { transform: translateY(-2px); border-color: rgba(19, 90, 118, .35); }
.group-entry-icon { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: rgba(19, 90, 118, .08); font-size: 22px; margin-bottom: 10px; }
.group-entry-card h3 { margin: 0 0 6px; font-size: 18px; font-family: var(--serif); color: var(--ink); }
.group-entry-card p { margin: 0 0 10px; color: var(--muted); font-size: 13px; }
.group-doc-list { display: grid; gap: 12px; margin-top: 18px; }
.group-doc-card { border: 1px solid var(--line); border-radius: 18px; padding: 15px; background: #fff; }
.group-doc-card h3 { margin: 0 0 6px; font-size: 18px; }
.group-doc-card p { margin: 0; color: var(--muted); }
.doc-page {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px 24px 72px;
}
.doc-shell {
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr) 336px;
  gap: 0;
  overflow: hidden;
}
.doc-nav, .doc-aside {
  padding: 22px;
  background: #fbfbf9;
}
.doc-nav { border-right: 1px solid var(--line); }
.doc-aside { border-left: 1px solid var(--line); }
.doc-main { padding: 26px 38px 38px; min-width: 0; }
.doc-page-compact {
  max-width: 1440px;
  padding-left: 10px;
  padding-right: 10px;
}
.doc-shell-compact {
  grid-template-columns: 248px minmax(0, 1fr);
  overflow: visible;
}
.doc-shell-compact .doc-nav {
  position: sticky;
  top: 84px;
  align-self: start;
  max-height: calc(100vh - 104px);
  overflow-y: auto;
  border-right: 1px solid var(--line);
}
.doc-shell-compact .doc-main {
  padding-left: 40px;
  padding-right: 32px;
}
.doc-shell-compact.doc-nav-hidden {
  grid-template-columns: minmax(0, 1fr);
}
.doc-shell-compact.doc-nav-hidden .doc-nav {
  display: none;
}
.doc-shell-compact.doc-nav-hidden .doc-main {
  padding-left: 32px;
}
.doc-toolbar {
  display:flex;
  align-items:center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.doc-toolbar .crumb { flex: 1; min-width: 220px; }
.doc-nav-toggle {
  width: 36px;
  height: 36px;
  display: inline-grid;
  place-items: center;
  border: 1px solid rgba(15,111,127,.22);
  background: #fff;
  color: var(--green);
  border-radius: 999px;
  padding: 0;
  font-size: 17px;
  line-height: 1;
  font-weight: 900;
  box-shadow: 0 8px 20px rgba(31,41,51,.05);
}
.doc-nav-toggle:hover {
  border-color: rgba(15,111,127,.42);
  transform: translateY(-1px);
}
.doc-nav-head {
  display:flex;
  justify-content: space-between;
  align-items:center;
  gap: 8px;
  margin-bottom: 12px;
}
.doc-nav-head strong {
  color: var(--ink);
  font-size: 13px;
}
.doc-nav-hide {
  border: 1px solid var(--line);
  background: #fff;
  color: var(--muted);
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 800;
}
.doc-nav-hide:hover { color: var(--green); border-color: rgba(15,111,127,.34); }
.doc-page-compact .next-reading-block {
  margin-top: 14px;
}
.doc-page-compact .doc-content {
  max-width: none;
}
.doc-page-compact .table-scroll {
  width: 100%;
  background: #fff;
}
.doc-page-compact .doc-content table {
  width: 100%;
  min-width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  border-spacing: 0;
}
.doc-page-compact .doc-content thead th {
  background: #26313d;
  color: #fff;
  border-top: 0;
}
.doc-page-compact .doc-content th,
.doc-page-compact .doc-content td,
.doc-page-compact .doc-content table:has(th:nth-child(5)) th,
.doc-page-compact .doc-content table:has(th:nth-child(5)) td {
  width: auto !important;
  min-width: 0 !important;
  max-width: none !important;
  white-space: normal;
  text-align: left !important;
}
.doc-page-compact .doc-content table:has(th:nth-child(5)) th,
.doc-page-compact .doc-content table:has(th:nth-child(5)) td {
  width: 20% !important;
  padding-left: 16px;
  padding-right: 16px;
}
.outline-list {
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
  display: grid;
  gap: 6px;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}
.outline-list li {
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}
.outline-item {
  display: inline-block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 5px 8px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #4b5968;
  font-size: 13px;
  line-height: 1.35;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
  box-sizing: border-box;
}
.outline-item.level-3 { padding-left: 18px; color: #5f6d7c; }
.outline-item.level-4 { padding-left: 28px; color: #6b7886; }
.outline-item:hover,
.outline-item.active {
  background: #eef2f4;
  color: #17202a;
}
.doc-content h2,
.doc-content h3,
.doc-content h4 {
  scroll-margin-top: 86px;
}
.doc-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--line);
}
.back-link {
  border: 0;
  background: transparent;
  color: var(--blue);
  padding: 0;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.crumb { color: var(--muted); font-size: 12px; margin-bottom: 12px; }
.doc-main h1 {
  font-family: var(--serif);
  font-size: 38px;
  line-height: 1.15;
  margin: 0 0 12px;
}
.doc-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 22px; }
.doc-content { max-width: 860px; }
.doc-content h1 { display: none; }
.doc-content h2 { font-size: 23px; margin: 34px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--line); }
.doc-content h3 { font-size: 18px; margin: 26px 0 10px; }
.doc-content p, .doc-content li { color: #2f3a45; }
.doc-content blockquote {
  margin: 16px 0;
  border-left: 3px solid var(--blue);
  background: #f3f6f7;
  padding: 12px 16px;
  color: #4a5663;
}
.table-scroll {
  overflow-x: auto;
  overflow-y: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  margin: 22px 0;
  background: #fff;
  max-width: 100%;
  overscroll-behavior-x: contain;
  scrollbar-color: #a5abb0 #eef1ef;
  scrollbar-width: thin;
}
.table-scroll::-webkit-scrollbar {
  height: 10px;
}
.table-scroll::-webkit-scrollbar-track {
  background: #eef1ef;
  border-radius: 999px;
}
.table-scroll::-webkit-scrollbar-thumb {
  background: #a5abb0;
  border-radius: 999px;
  border: 2px solid #eef1ef;
}
table {
  border-collapse: collapse;
  width: max-content;
  min-width: 100%;
  table-layout: auto;
  font-size: 13px;
  background: #fff;
}
th {
  background: #26313d;
  color: #fff;
  text-align: left;
  padding: 11px 12px;
  white-space: nowrap;
}
td {
  border-top: 1px solid var(--line);
  padding: 11px 12px;
  vertical-align: top;
  overflow-wrap: normal;
  word-break: normal;
  line-height: 1.62;
}
td a { overflow-wrap: anywhere; word-break: break-word; }
.doc-content table th,
.doc-content table td {
  min-width: 132px;
  max-width: 360px;
}
.doc-content table th:first-child,
.doc-content table td:first-child {
  min-width: 108px;
  max-width: 180px;
}
.doc-content table th:last-child,
.doc-content table td:last-child {
  min-width: 260px;
  max-width: 460px;
}
.doc-content table:has(th:nth-child(3)):not(:has(th:nth-child(4))) {
  min-width: 760px;
}
.doc-content table:has(th:nth-child(4)):not(:has(th:nth-child(5))) {
  min-width: 880px;
}
.doc-content table:has(th:nth-child(5)) {
  min-width: 1080px;
}
.doc-content table:has(th:nth-child(5)) th:nth-child(1),
.doc-content table:has(th:nth-child(5)) td:nth-child(1) {
  min-width: 120px;
  max-width: 160px;
}
.doc-content table:has(th:nth-child(5)) th:nth-child(2),
.doc-content table:has(th:nth-child(5)) td:nth-child(2),
.doc-content table:has(th:nth-child(5)) th:nth-child(3),
.doc-content table:has(th:nth-child(5)) td:nth-child(3),
.doc-content table:has(th:nth-child(5)) th:nth-child(4),
.doc-content table:has(th:nth-child(5)) td:nth-child(4) {
  min-width: 132px;
  max-width: 190px;
}
.doc-content table:has(th:nth-child(5)) th:nth-child(5),
.doc-content table:has(th:nth-child(5)) td:nth-child(5) {
  min-width: 320px;
  max-width: 480px;
}
tr:nth-child(even) td { background: #fafafa; }

.source-summary-table-scroll,
.source-boundary-table-scroll {
  border-color: var(--jd-red);
  background: #fffdfb;
}
.doc-content table.source-summary-table,
.doc-content table.source-boundary-table {
  width: 100%;
  min-width: 100%;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
}
.doc-content table.source-summary-table th,
.doc-content table.source-summary-table td,
.doc-content table.source-boundary-table th,
.doc-content table.source-boundary-table td {
  min-width: 0;
  max-width: none;
  white-space: normal;
  text-align: left;
}
.doc-content table.source-summary-table th {
  padding: 13px 18px;
  background: #26313d;
}
.doc-content table.source-summary-table th:nth-child(1),
.doc-content table.source-summary-table td:nth-child(1) {
  width: 30%;
}
.doc-content table.source-summary-table th:nth-child(2),
.doc-content table.source-summary-table td:nth-child(2) {
  width: 70%;
}
.doc-content table.source-summary-table td:nth-child(2),
.doc-content table.source-boundary-table td:nth-child(n+2) {
  border-left: 2px solid var(--jd-red);
}
.doc-content table.source-summary-table td {
  padding: 18px 20px;
  border-top: 2px solid var(--jd-red);
  vertical-align: top;
}
.doc-content table.source-summary-table td:first-child {
  padding-left: 18px;
  padding-right: 18px;
  font-weight: 800;
}
.doc-content table.source-summary-table td:nth-child(2) {
  padding-left: 24px;
}
.doc-content table.source-summary-table tr:nth-child(even) td,
.doc-content table.source-boundary-table tr:nth-child(even) td {
  background: #fffaf8;
}
.doc-content table.source-summary-table p,
.doc-content table.source-summary-table ul,
.doc-content table.source-boundary-table p,
.doc-content table.source-boundary-table ul {
  margin-top: 0;
  margin-bottom: 0;
}
.doc-content table.source-summary-table li,
.doc-content table.source-boundary-table li {
  margin: 0 0 6px;
}
.doc-content table.source-boundary-table {
  min-width: 100%;
}
.doc-content table.source-boundary-table th {
  padding: 13px 18px;
  background: #26313d;
}
.doc-content table.source-boundary-table th:nth-child(1),
.doc-content table.source-boundary-table td:nth-child(1) { width: 28%; }
.doc-content table.source-boundary-table th:nth-child(2),
.doc-content table.source-boundary-table td:nth-child(2) { width: 38%; }
.doc-content table.source-boundary-table th:nth-child(3),
.doc-content table.source-boundary-table td:nth-child(3) { width: 34%; }
.doc-content table.source-boundary-table td {
  padding: 18px 20px;
  border-top: 2px solid var(--jd-red);
  vertical-align: top;
}
.doc-content table.source-boundary-table td:nth-child(2),
.doc-content table.source-boundary-table td:nth-child(3) {
  padding-left: 24px;
}

.source-financial-table-scroll {
  border-color: var(--jd-red);
  background: #fffdfb;
}
.doc-content table.source-financial-table {
  width: 100%;
  min-width: 100%;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
}
.doc-content table.source-financial-table th,
.doc-content table.source-financial-table td {
  min-width: 0;
  max-width: none;
  white-space: normal;
  text-align: left;
}
.doc-content table.source-financial-table th {
  padding: 13px 18px;
  background: #26313d;
}
.doc-content table.source-financial-table th:nth-child(1),
.doc-content table.source-financial-table td:nth-child(1) { width: 40%; }
.doc-content table.source-financial-table th:nth-child(2),
.doc-content table.source-financial-table td:nth-child(2) { width: 60%; }
.doc-content table.source-financial-table td:nth-child(2) {
  border-left: 2px solid var(--jd-red);
  padding-left: 24px;
}
.doc-content table.source-financial-table td {
  padding: 18px 20px;
  border-top: 2px solid var(--jd-red);
  vertical-align: top;
}
.doc-content table.source-financial-table td:first-child {
  padding-left: 18px;
  padding-right: 18px;
  font-weight: 800;
}
.doc-content table.source-financial-table tr:nth-child(even) td { background: #fffaf8; }
.doc-content table.source-financial-table p,
.doc-content table.source-financial-table ul {
  margin-top: 0;
  margin-bottom: 0;
}
.doc-content table.source-financial-table li { margin: 0 0 6px; }
.doc-page-compact .doc-content table.source-financial-table th,
.doc-page-compact .doc-content table.source-financial-table td {
  min-width: 0 !important;
  max-width: none !important;
}
.doc-page-compact .doc-content table.source-financial-table th:nth-child(1),
.doc-page-compact .doc-content table.source-financial-table td:nth-child(1) { width: 40% !important; }
.doc-page-compact .doc-content table.source-financial-table th:nth-child(2),
.doc-page-compact .doc-content table.source-financial-table td:nth-child(2) { width: 60% !important; }
.doc-page-compact .doc-content table.source-summary-table th,
.doc-page-compact .doc-content table.source-summary-table td,
.doc-page-compact .doc-content table.source-boundary-table th,
.doc-page-compact .doc-content table.source-boundary-table td {
  min-width: 0 !important;
  max-width: none !important;
}
.doc-page-compact .doc-content table.source-summary-table th:nth-child(1),
.doc-page-compact .doc-content table.source-summary-table td:nth-child(1) { width: 30% !important; }
.doc-page-compact .doc-content table.source-summary-table th:nth-child(2),
.doc-page-compact .doc-content table.source-summary-table td:nth-child(2) { width: 70% !important; }
.doc-page-compact .doc-content table.source-boundary-table th:nth-child(1),
.doc-page-compact .doc-content table.source-boundary-table td:nth-child(1) { width: 28% !important; }
.doc-page-compact .doc-content table.source-boundary-table th:nth-child(2),
.doc-page-compact .doc-content table.source-boundary-table td:nth-child(2) { width: 38% !important; }
.doc-page-compact .doc-content table.source-boundary-table th:nth-child(3),
.doc-page-compact .doc-content table.source-boundary-table td:nth-child(3) { width: 34% !important; }
@media (max-width: 760px) {
  .doc-content table.source-summary-table,
  .doc-content table.source-boundary-table {
    min-width: 760px;
  }
}

.wiki-link { color: var(--blue); text-decoration: none; border-bottom: 1px dotted var(--blue); }
.wiki-link.missing { color: var(--soft); border-bottom: 1px dotted var(--soft); }
.external-link {
  color: var(--blue);
  text-decoration: none;
  border-bottom: 1px solid rgba(49,95,143,.32);
  overflow-wrap: anywhere;
}
.external-link:hover {
  color: #1f4d78;
  border-bottom-color: #1f4d78;
}
.aside-block {
  margin-bottom: 14px;
  padding: 15px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255,255,255,.78);
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}
.aside-block h3 {
  margin: 0 0 9px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.aside-block h3::before {
  content: "";
  width: 16px;
  height: 2px;
  background: var(--red);
  flex: 0 0 auto;
}
.aside-block p, .aside-block li { color: var(--muted); font-size: 13px; }
.aside-block ul { margin: 0; padding-left: 18px; }
.mini-doc {
  display: flex;
  width: 100%;
  align-items: flex-start;
  gap: 8px;
  text-decoration: none;
  border: 0;
  border-top: 1px solid var(--line);
  background: transparent;
  padding: 10px 0;
  color: #34404c;
  font-size: 13px;
  line-height: 1.45;
  text-align: left;
  border-radius: 0;
}
.mini-doc:first-of-type {
  border-top: 0;
  padding-top: 2px;
}
.mini-doc::before {
  content: "↳";
  color: var(--soft);
  flex: 0 0 auto;
}
.mini-doc:hover {
  color: var(--blue);
}
.library-panel { padding: 18px; }
.module-row {
  border-top: 1px solid var(--line);
  padding: 16px 0;
}
.module-row:first-child { border-top: 0; }
.module-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}
.module-head h3 { margin: 0; font-size: 19px; }
.doc-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 14px;
  margin-top: 12px;
}
.doc-list a {
  text-decoration: none;
  color: #37424f;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: var(--radius);
  padding: 9px 10px;
  font-size: 13px;
}
.policy-guide {
  margin: 30px 0 34px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: 0 12px 30px rgba(23,32,42,.05);
  overflow: hidden;
}
.guide-head {
  padding: 22px 24px 18px;
  border-bottom: 1px solid var(--line);
}
.guide-head span {
  display: block;
  color: var(--gold);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.guide-head h2 {
  margin: 0;
  font-family: var(--serif);
  font-size: 28px;
  line-height: 1.25;
}
.guide-head p {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 14px;
}
.policy-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.policy-row {
  padding: 18px 20px;
  border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  min-height: 168px;
}
.policy-row:nth-child(2n) { border-right: 0; }
.policy-row:nth-last-child(-n + 2) { border-bottom: 0; }
.policy-row strong {
  display: block;
  color: #111922;
  font-size: 17px;
  margin-bottom: 8px;
}
.policy-row p {
  margin: 0 0 10px;
  color: #384554;
}
.policy-row small {
  display: block;
  color: var(--muted);
  line-height: 1.65;
}
.empty {
  padding: 46px 0;
  text-align: center;
  color: var(--muted);
}

.issue-hero-banner, .group-hero-banner {
  border: 1px solid rgba(218,41,28,.15);
  border-radius: 26px;
  padding: 22px;
  margin-bottom: 22px;
  background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(236,249,248,.82));
}
.issue-hero-title, .group-hero-title { display:flex; gap:14px; align-items:flex-start; }
.issue-hero-title h1, .group-hero-title h1 { margin-top:0; }
.group-meta-line { display:flex; gap:8px; flex-wrap:wrap; margin-top:14px; }
.med-card-main { display:flex; flex-direction:column; align-items:flex-start; justify-content:flex-start; min-width:0; }
.med-card.chart .med-card-main { gap:0; transform: translateY(6px); }
.weekly-card-body { flex:1; display:flex; flex-direction:column; justify-content:center; padding:10px 0 8px; }
.weekly-card-body h3 + p { margin-bottom:12px; }
.briefing-card.align-top-body .weekly-card-body { justify-content:flex-start; padding-top:22px; }
@media (max-width: 1080px) {
  .hero-grid, .issue-detail, .search-layout, .doc-shell { grid-template-columns: 1fr; }
  .issue-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .path-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .snapshot-section .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .path-step { border-bottom: 1px solid var(--line); }
  .doc-nav, .doc-aside { border: 0; border-top: 1px solid var(--line); }
  .doc-shell-compact.doc-nav-hidden { grid-template-columns: 1fr; }
  .doc-shell-compact.doc-nav-hidden .doc-nav { display: none; }
}
@media (max-width: 760px) {
  .topbar { height: auto; padding: 12px; flex-wrap: wrap; }
  .brand { min-width: 100%; }
  .nav-tabs { width: 100%; overflow-x: auto; }
  .global-search { min-width: 100%; }
  .auth-area { width: 100%; justify-content: flex-start; }
  .hero, .issue-section, .path-section, .search-section, .library-section, .issue-page, .doc-page { padding-left: 14px; padding-right: 14px; }
  .snapshot-section { padding-left: 14px; padding-right: 14px; }
  .issue-grid, .doc-list, .metric-grid, .path-strip, .policy-grid { grid-template-columns: 1fr; }
  .recommended-doc-grid { grid-template-columns: 1fr; }
  .group-entry-grid { grid-template-columns: 1fr; }
  .weekly-grid, .radar-grid { grid-template-columns: 1fr; }
  .hero-grid, .weekly-layout { grid-template-columns: 1fr; }
  .medical-visual { min-height: 520px; }
  .pill-scene { position:absolute; inset:76px 18px 18px; grid-template-columns: 1fr; grid-template-rows: repeat(3, minmax(0,1fr)); }
  .med-card.news, .med-card.drug, .med-card.chart { grid-column:1; grid-row:auto; aspect-ratio:auto; }
  .snapshot-section .metric-grid { grid-template-columns: 1fr; }
  .policy-row, .policy-row:nth-child(2n), .policy-row:nth-last-child(-n + 2) { border-right: 0; border-bottom: 1px solid var(--line); }
  .policy-row:last-child { border-bottom: 0; }
  .hero h1 { font-size: 36px; }
  .doc-main { padding: 22px 18px; }
  .knowledge-node-grid { grid-template-columns: 1fr; }
}

/* UI review redesign: long hero, bottom triad, WSJ-style curated cards */
.hero-grid.ui-review-hero {
  grid-template-columns: 1fr;
  min-height: 560px;
  padding: 48px 56px 38px;
  background:
    linear-gradient(90deg, rgba(229, 249, 247, .88), rgba(255,255,255,.94) 56%, rgba(240,249,247,.86)),
    repeating-linear-gradient(90deg, rgba(19,90,118,.045) 0 1px, transparent 1px 64px),
    repeating-linear-gradient(0deg, rgba(19,90,118,.035) 0 1px, transparent 1px 64px);
}
.ui-review-hero .hero-copy { max-width: 1080px; }
.ui-review-hero h1 { font-size: clamp(48px, 6.2vw, 86px); max-width: none; white-space: nowrap; letter-spacing: -.055em; }
.ui-review-hero .hero-lead { max-width: 960px; font-size: clamp(18px, 1.75vw, 24px); color:#1d2f3e; }
.ui-review-hero .hero-search { max-width: 960px; height: 64px; margin-top:28px; }
.ui-review-hero .hero-actions { margin-top:28px; }
.data-orbit { position:absolute; inset:18px; z-index:0; pointer-events:none; overflow:hidden; border-radius:30px; opacity:.95; }
.data-orbit::before { content:""; position:absolute; inset:0; background: radial-gradient(circle at 18% 28%, rgba(27,211,190,.34), transparent 14%), radial-gradient(circle at 70% 35%, rgba(89,151,255,.26), transparent 18%), linear-gradient(135deg, rgba(3,37,54,.92), rgba(6,93,111,.78)); animation: pulseGrid 9s ease-in-out infinite alternate; }
.data-orbit::after { content:""; position:absolute; inset:-40%; background: conic-gradient(from 120deg, transparent 0 18%, rgba(255,255,255,.28) 20%, transparent 24% 55%, rgba(27,211,190,.20) 58%, transparent 62%); animation: orbitSpin 18s linear infinite; }
.hero-data-chips { display:flex; flex-wrap:wrap; gap:10px; margin-top:22px; position:relative; z-index:1; }
.hero-data-chips span { border:1px solid rgba(11,95,122,.18); background:rgba(255,255,255,.70); color:#0b5f7a; border-radius:999px; padding:8px 12px; font-weight:800; font-size:13px; }
.compact-home-hero { min-height: 430px; padding: clamp(42px, 7vw, 78px); }
.compact-home-hero .hero-copy { max-width: 980px; }
.compact-home-hero h1 { white-space: normal; }
.compact-product-matrix { margin-top: -8px; }
.compact-snapshot { max-width: 1120px; margin: 0 auto 42px; padding: 0 28px; }
.product-matrix { max-width:1120px; margin:0 auto 34px; padding:0 28px; }
.product-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:12px; }
.product-card { border:1px solid rgba(11,95,122,.14); background:linear-gradient(180deg,#fff,rgba(239,250,250,.92)); border-radius:22px; padding:16px; box-shadow:0 18px 42px rgba(5,38,52,.08); text-align:left; cursor:pointer; transition:transform .16s ease, border-color .16s ease; }
.product-card:hover { transform:translateY(-3px); border-color:rgba(15,118,110,.34); }
.product-card .product-icon { width:42px; height:42px; display:grid; place-items:center; border-radius:15px; background:linear-gradient(135deg,rgba(15,118,110,.12),rgba(11,95,122,.08)); font-size:22px; margin-bottom:10px; }
.product-card h3 { margin:0 0 6px; font-family:var(--serif); font-size:18px; }
.product-card p { margin:0; color:var(--muted); font-size:12px; line-height:1.45; }
@keyframes orbitSpin { to { transform:rotate(360deg); } }
@keyframes pulseGrid { from { filter:saturate(.95) brightness(.95); } to { filter:saturate(1.15) brightness(1.08); } }
.home-triad-section { max-width:1120px; margin: 0 auto 34px; padding: 0 28px 24px; }
.home-triad-panel {
  border-radius: 28px;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(23,112,131,.98), rgba(54,171,169,.92)),
    repeating-linear-gradient(90deg, rgba(255,255,255,.08) 0 1px, transparent 1px 64px),
    repeating-linear-gradient(0deg, rgba(255,255,255,.08) 0 1px, transparent 1px 64px);
  box-shadow: 0 26px 70px rgba(19,90,118,.18);
  color:#fff;
}
.home-triad-badge { display:inline-flex; align-items:center; gap:7px; border:1px solid rgba(255,255,255,.30); border-radius:999px; padding:7px 14px; font-size:13px; font-weight:800; margin-bottom:14px; background:rgba(255,255,255,.10); }
.home-triad-grid { display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap:14px; }
.home-triad-card { min-height: 158px; border:1px solid rgba(255,255,255,.25); border-radius:22px; padding:18px; background:rgba(255,255,255,.14); color:#fff; text-align:left; cursor:pointer; display:flex; flex-direction:column; justify-content:space-between; transition:transform .16s ease, background .16s ease; }
.home-triad-card:hover { transform:translateY(-3px); background:rgba(255,255,255,.19); }
.home-triad-card .triad-icon { font-size:24px; margin-bottom:10px; }
.home-triad-card h3 { margin:0 0 5px; font-size:21px; font-family:var(--serif); color:#fff; }
.home-triad-card p { margin:0; color:rgba(255,255,255,.88); font-size:13px; line-height:1.45; }
.home-triad-card strong { margin-top:12px; font-size:13px; }
.issue-detail.ui-review-issue { grid-template-columns: 1fr; }
.issue-detail.ui-review-issue > main { max-width: 1120px; margin:0 auto; width:100%; }
.issue-hero-centered { text-align:left; padding:28px 0 10px; margin-bottom:18px; }
.issue-hero-title { display:block; margin:0; font-family:var(--serif); color:#102235; letter-spacing:-.04em; line-height:1.05; }
.issue-hero-title-main { display:block; font-size:clamp(38px,4.2vw,58px); }
.issue-hero-title-sub { display:block; margin-top:8px; font-size:clamp(25px,2.9vw,42px); line-height:1.18; letter-spacing:-.035em; font-weight:700; }
.issue-hero-info { max-width:920px; margin:18px 0 0; text-align:left; }
.issue-hero-info p { margin:0; color:#5b6672; font-size:18px; line-height:1.7; }
.issue-hero-divider { width:100%; height:1px; margin:42px auto 0; background:rgba(17,24,39,.92); }
.curated-section { margin-top: 30px; }
.curated-head { margin-bottom:18px; }
.curated-title-row { display:flex; align-items:flex-end; justify-content:space-between; gap:18px; }
.curated-head h2 { margin:0; font-family:var(--serif); font-size:clamp(38px,4vw,58px); letter-spacing:-.04em; }
.curated-head p { margin:12px 0 0; color:var(--muted); font-size:18px; line-height:1.65; }
.curated-time-tag { flex:0 0 auto; white-space:nowrap; line-height:1; align-self:center; margin-left:18px; }
.curated-subline { display:flex; align-items:baseline; justify-content:space-between; gap:18px; margin-top:12px; }
.curated-subline p { margin:0; flex:1 1 auto; }
.issue-filter-pills { display:flex; flex-wrap:wrap; gap:18px 20px; margin-top:20px; }
.issue-filter-pill { min-height:64px; border:1px solid rgba(18,38,56,.16); border-radius:999px; padding:0 26px; background:#fff; color:#0e2338; font-weight:900; cursor:pointer; box-shadow:0 14px 34px rgba(15,31,45,.07); display:inline-flex; align-items:center; gap:12px; font-size:22px; font-family:var(--serif); transition:transform .16s ease, border-color .16s ease, box-shadow .16s ease, background .16s ease; }
.issue-filter-pill .pill-icon { font-family:var(--sans); font-size:22px; line-height:1; }
.issue-filter-pill .pill-count { font-family:var(--sans); font-size:20px; font-weight:900; }
.issue-filter-pill:hover { transform:translateY(-2px); border-color:rgba(15,111,127,.35); box-shadow:0 18px 42px rgba(15,31,45,.10); }
.issue-filter-pill.active { border-color:rgba(15,111,127,.50); background:linear-gradient(135deg,#ffffff,#F1FAFF); box-shadow:0 18px 46px rgba(15,111,127,.14); }
.curated-list { display:grid; gap:22px; }
.curated-card { display:grid; grid-template-columns: minmax(280px, 38%) minmax(0,1fr); gap:28px; align-items:stretch; padding:20px 0; border-bottom:1px solid var(--line); }
.curated-art { min-height:210px; border-radius:8px; overflow:hidden; position:relative; background:linear-gradient(135deg, #f04d45, #f6a35a); border:0; cursor:pointer; box-shadow:0 18px 40px rgba(14,27,38,.13), inset 0 0 0 1px rgba(255,255,255,.2); }
.curated-art img { position:absolute; inset:0; width:100%; height:100%; object-fit:contain; padding:0; background:#fff; transition:transform .28s ease, filter .28s ease; }
.curated-art:hover img { transform:scale(1.035); filter:saturate(1.08) contrast(1.04); }
.curated-art.has-cover::before { content:""; position:absolute; inset:0; z-index:1; background:linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.04)); pointer-events:none; }
.curated-art:not(.has-cover)::before { content:""; position:absolute; inset:-44px; background:radial-gradient(circle at 50% 52%, rgba(255,255,255,.96) 0 42px, transparent 43px), repeating-radial-gradient(circle at 50% 52%, rgba(14,24,34,.78) 0 2px, transparent 2px 19px), linear-gradient(135deg, rgba(255,255,255,.18), transparent 42%); opacity:.86; }
.curated-art:not(.has-cover)::after { content:attr(data-icon); position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); width:76px; height:76px; border-radius:50%; display:grid; place-items:center; background:#fff; box-shadow:0 16px 32px rgba(0,0,0,.24); font-size:36px; }
.curated-art.policy { background:linear-gradient(135deg,#315f8f,#74a8c7); }
.curated-art.finance { background:linear-gradient(135deg,#2A1715,#5bb5b4); }
.curated-art.medical { background:linear-gradient(135deg,#2f9b87,#d7f1ed); }
.curated-art.research { background:linear-gradient(135deg,#6d5bd0,#e6ddff); }
.curated-art.news { background:linear-gradient(135deg,#f27c38,#f7cf72); }
.curated-body { padding:2px 0; }
.curated-kind { color:#5b6773; font-weight:900; letter-spacing:.08em; text-transform:uppercase; font-size:13px; margin-bottom:8px; }
.curated-body h3 { margin:0 0 8px; font-family:var(--serif); font-size:30px; line-height:1.16; }
.curated-dash { margin:12px 0 0; display:flex; flex-direction:column; align-items:flex-start; gap:4px; color:#5d6873; font-size:15px; line-height:1.45; }
.curated-dash span { display:block; text-align:left; }`r`n.curated-dash span::before { content:'- '; color:#8a95a0; }
.curated-meta { display:flex; gap:8px; flex-wrap:wrap; color:#6a7480; }
.compact-group-section { display:none; }

body {
  background:
    radial-gradient(circle at 12% 8%, rgba(218, 41, 28, .16), transparent 24%),
    radial-gradient(circle at 88% 12%, rgba(166, 25, 17, .12), transparent 26%),
    linear-gradient(180deg, #FFF3F0 0%, #FFE0D9 46%, #FFF7F5 100%);
  color: #2A1715;
}
.portal-home {
  width: min(1160px, calc(100% - 48px));
  margin: 0 auto;
  padding: 30px 0 72px;
}
.portal-home .kicker { color:#DA291C; letter-spacing:.14em; }
.portal-hero .kicker { color:rgba(255,255,255,.86); }
.portal-home .hero-lead { max-width: 760px; margin: 0 auto; color:#6F4E49; font-size:16px; line-height:1.72; font-weight:500; }
.portal-hero .hero-lead { color:rgba(255,255,255,.86); }
.portal-hero {
  min-height: 330px;
  border: 1px solid rgba(218, 41, 28, .42);
  border-radius: 30px;
  padding: 38px clamp(28px, 5vw, 58px) 40px;
  background:
    radial-gradient(circle at 78% 18%, rgba(255,255,255,.20), transparent 24%),
    radial-gradient(circle at 8% 12%, rgba(255,255,255,.13), transparent 34%),
    linear-gradient(135deg, #DA291C 0%, #B91F16 56%, #7A120C 100%);
  box-shadow: 0 30px 76px rgba(122, 18, 12, .28);
  text-align: center;
  overflow: hidden;
  position: relative;
}
.portal-hero::after {
  content:"";
  position:absolute;
  width: 260px;
  height: 260px;
  right: -110px;
  bottom: -130px;
  border-radius: 50%;
  background: rgba(255,255,255,.12);
}
.portal-hero-copy { position:relative; z-index:1; max-width: 900px; margin: 0 auto; }
.portal-hero h1 {
  margin: 16px auto 14px;
  font-family: var(--serif);
  font-size: clamp(40px, 5vw, 66px);
  line-height: 1.02;
  letter-spacing: -.05em;
  max-width: 920px;
  color:#FFFFFF;
}
.portal-hero .hero-search {
  margin: 22px auto 0;
  max-width: 680px;
  background: rgba(255,255,255,.95);
  border-color: rgba(240,194,188,.76);
  min-height: 50px;
  box-shadow:0 12px 28px rgba(122,18,12,.14);
}
.portal-hero .hero-search input { padding-left: 2px; }
.hero-search-button {
  width: 38px;
  height: 38px;
  border: 0;
  border-radius: 999px;
  display: inline-grid;
  place-items: center;
  background: linear-gradient(135deg, #DA291C, #F26A5B);
  color: #fff;
  font-size: 20px;
  font-weight: 900;
  line-height: 1;
  box-shadow: 0 10px 22px rgba(218,41,28,.22);
  flex: 0 0 auto;
}
.hero-search-button:hover { transform: translateY(-1px); box-shadow: 0 12px 26px rgba(218,41,28,.28); }
.hero-search-button svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.6;
  stroke-linecap: round;
}
.portal-hero .hero-actions { justify-content:center; margin-top: 20px; }
.portal-hero .btn { border-radius: 999px; padding: 9px 17px; }
.portal-map-section {
  margin-top: 34px;
  min-height: 560px;
  border: 1px solid rgba(218, 41, 28, .34);
  border-radius: 32px;
  padding: 28px clamp(28px, 4.5vw, 54px) 42px;
  background:
    radial-gradient(circle at 50% 48%, rgba(255,255,255,.22), transparent 31%),
    radial-gradient(circle at 18% 82%, rgba(255,255,255,.16), transparent 22%),
    linear-gradient(145deg, #DA291C 0%, #C72419 46%, #A61911 100%);
  box-shadow: 0 28px 76px rgba(122, 18, 12, .24);
  text-align: center;
  overflow: hidden;
  position: relative;
}
.portal-map-section::after { content:none; }
.portal-knowledge-visual { position: relative; z-index: 1; width: min(980px, 100%); margin: 18px auto 0; }
.portal-knowledge-visual svg,
.portal-illustration svg { width: 100%; height: auto; display:block; }
.knowledge-map {
  position: relative;
  z-index: 1;
  width: min(980px, 100%);
  min-height: 390px;
  margin: 0 auto;
  color:#FFFFFF;
  display:grid;
  place-items:center;
}
.knowledge-map-grid {
  display:grid;
  grid-template-rows: 1fr;
  gap: 0;
  align-items:center;
  justify-items:center;
  padding: 0;
}
.knowledge-lines,
.map-line,
.knowledge-map-order { display:none; }
.knowledge-center {
  color:#2A1715;
}
.knowledge-center-compact {
  justify-self:center;
  width:auto;
  min-width: 260px;
  min-height:auto;
  border-radius:999px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:12px;
  padding: 12px 22px;
  background: linear-gradient(145deg, rgba(255,255,255,.96), rgba(255,244,242,.92));
  border:1px solid rgba(240,194,188,.86);
  box-shadow:0 16px 42px rgba(218,41,28,.10), inset 0 0 0 1px rgba(255,255,255,.76);
}
.knowledge-center-compact strong { font-size:20px; font-weight:950; letter-spacing:-.035em; }
.knowledge-center-compact span { font-size:11px; color:#7A5E59; letter-spacing:.12em; text-transform:uppercase; font-weight:900; }
.knowledge-node-grid {
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px;
  width:min(900px, 100%);
  align-items:stretch;
  align-self:center;
  justify-self:center;
  transform: translateY(18px);
}
.knowledge-node {
  min-height: 148px;
  border: 1px solid rgba(255,255,255,.24);
  border-radius: 28px;
  padding: 22px 24px 20px;
  background: linear-gradient(145deg, rgba(255,255,255,.96), rgba(255,240,237,.90));
  color:#2A1715;
  box-shadow: 0 18px 42px rgba(74,8,4,.20);
  display:grid;
  grid-template-rows: auto auto 1fr;
  gap: 12px;
  align-items:start;
  justify-items:start;
  text-align:left;
  transition:transform .18s ease, border-color .18s ease, box-shadow .18s ease, color .18s ease;
}
.knowledge-node::before { content:none; }
.knowledge-no {
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-width: 50px;
  height: 28px;
  padding: 0 14px;
  border-radius: 999px;
  background: linear-gradient(135deg, #DA291C, #F26A5B);
  color:#fff !important;
  font-size:13px !important;
  line-height:1;
  font-weight:950 !important;
  letter-spacing:.08em;
  box-shadow:0 10px 22px rgba(218,41,28,.22);
  white-space:nowrap;
}
.knowledge-node strong {
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-width: 92px;
  min-height: 42px;
  padding: 8px 22px;
  border-radius: 999px;
  background: rgba(255,255,255,.86);
  border:1px solid rgba(240,194,188,.92);
  color:#2A1715;
  font-size:22px;
  font-weight:950;
  line-height:1;
  letter-spacing:-.02em;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.68);
}
.knowledge-node > span:last-child {
  color:#7A5E59;
  font-size:14px;
  line-height:1.6;
  font-weight:850;
  white-space:normal;
}
.knowledge-node:hover {
  transform: translateY(-4px);
  color:#DA291C;
  border-color: rgba(242,106,91,.95);
  box-shadow: 0 24px 54px rgba(218,41,28,.14);
}
.knowledge-node:hover strong { border-color:rgba(242,106,91,.95); color:#DA291C; }
.node-market,
.node-platform,
.node-pharmacy,
.node-pharma,
.node-policy,
.node-disease {
  position:relative;
  left:auto; right:auto; top:auto; bottom:auto;
  width:auto;
  transform:none;
  grid-template-columns: none;
  text-align:left;
  justify-items:start;
}
.node-market:hover,
.node-platform:hover,
.node-pharmacy:hover,
.node-pharma:hover,
.node-policy:hover,
.node-disease:hover { transform: translateY(-4px); }
.portal-timeline-section,
.portal-snapshot-section,
.portal-feature,
.portal-competition-band {
  margin-top: 86px;
  border-radius: 38px;
  border: 1px solid rgba(218, 41, 28, .30);
  background:
    radial-gradient(circle at 88% 12%, rgba(218,41,28,.16), transparent 28%),
    linear-gradient(145deg, #FFF7F5, #FFDCD4 86%);
  box-shadow: 0 28px 80px rgba(126, 22, 14, .18);
  backdrop-filter: blur(18px);
}
.portal-timeline-section { padding: 54px 42px 62px; }
.cognition-title { margin:42px 0 18px; text-align:center; font-family:var(--serif); font-size:clamp(36px,4.5vw,58px); line-height:1; color:#FFFFFF; letter-spacing:-.04em; }
.portal-section-head { display:flex; justify-content:space-between; gap:36px; align-items:flex-start; margin-bottom: 34px; }
.portal-section-head h2,
.portal-feature h2,
.portal-competition-band h2 {
  margin:0;
  font-family: var(--serif);
  font-size: clamp(34px, 4vw, 52px);
  line-height:1.08;
  letter-spacing:-.035em;
  color:#2A1715;
}
.portal-section-head p { max-width: 520px; margin: 0; color:#6F4E49; line-height:1.8; font-weight:500; }
.portal-timeline {
  position: relative;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0;
  padding: 34px 4px 8px;
}
.portal-timeline::before {
  content:"";
  position:absolute;
  left: 6%;
  right: 6%;
  top: 58px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(91,175,167,.45), transparent);
}
.portal-timeline-step {
  position: relative;
  z-index: 1;
  border:0;
  background: transparent;
  text-align:center;
  padding: 0 12px;
  color: inherit;
}
.portal-timeline-step > span {
  width: 50px;
  height: 50px;
  margin: 0 auto 26px;
  border-radius: 999px;
  display:grid;
  place-items:center;
  background: #ffffff;
  border: 1px solid rgba(120,198,190,.48);
  color:#4A9F98;
  font-weight:900;
  box-shadow: 0 14px 34px rgba(38,50,56,.08);
}
.portal-timeline-step h3 { margin:0 0 10px; font-size:17px; color:#2A1715; }
.portal-timeline-step p { margin:0; color:#5c6c71; font-size:13px; line-height:1.65; font-weight:500; }
.portal-feature {
  min-height: 420px;
  display:grid;
  grid-template-columns: minmax(0, .96fr) minmax(360px, .82fr);
  gap: 44px;
  align-items:center;
  padding: clamp(38px, 5vw, 58px);
}
.portal-feature.reverse { grid-template-columns: minmax(360px, .82fr) minmax(0, .96fr); }
.portal-feature-dark {
  min-height: 350px;
  grid-template-columns: minmax(0, .95fr) minmax(360px, .8fr);
  background:
    radial-gradient(circle at 82% 24%, rgba(94, 197, 240, .28), transparent 28%),
    linear-gradient(135deg, #7A120C, #DA291C 72%, #F26A5B);
  color:#fff;
  border: 0;
}
.portal-feature-dark h2 { color:#fff; }
.portal-feature-dark p { color:rgba(255,255,255,.82); }
.portal-feature-copy p { margin: 18px 0 0; color:#6F4E49; line-height:1.85; font-size:16px; }
.portal-eyebrow { display:inline-flex; color:#DA291C; font-size:12px; letter-spacing:.12em; text-transform:uppercase; font-weight:900; margin-bottom: 16px; }
.portal-feature-dark .portal-eyebrow { color:#FFE0D9; }
.portal-focus-row,
.portal-insight-strip,
.competition-points {
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 28px;
}
.portal-focus-row button,
.portal-insight-strip button,
.competition-points button {
  border: 1px solid rgba(95, 174, 185, .20);
  border-radius: 22px;
  padding: 18px;
  background: rgba(255,255,255,.62);
  text-align:left;
  color:#2A1715;
  box-shadow: 0 14px 34px rgba(28,91,111,.06);
}
.portal-insight-strip { grid-template-columns: 1fr; margin-top: 0; }
.portal-insight-strip button { background: rgba(255,255,255,.13); color:#fff; border-color: rgba(255,255,255,.18); }
.portal-focus-row strong,
.portal-insight-strip strong,
.competition-points strong { display:block; font-size:17px; margin-bottom:6px; }
.portal-focus-row span,
.portal-insight-strip span,
.competition-points span { display:block; color:inherit; opacity:.72; font-size:13px; line-height:1.55; }
.portal-illustration { width:100%; filter: drop-shadow(0 24px 42px rgba(218,41,28,.14)); }
.portal-snapshot-section { margin-top:30px; padding:34px 38px; border-color:rgba(218,41,28,.34); border-radius:32px; background:radial-gradient(circle at 50% 24%, rgba(255,255,255,.20), transparent 30%), radial-gradient(circle at 14% 86%, rgba(255,255,255,.13), transparent 24%), linear-gradient(145deg, #DA291C 0%, #C72419 46%, #A61911 100%); box-shadow:0 28px 76px rgba(122,18,12,.24); }
.portal-metrics { display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.portal-metrics div { border-radius: 22px; padding: 24px; background:linear-gradient(145deg, rgba(255,255,255,.96), rgba(255,240,237,.90)); border:1px solid rgba(255,255,255,.24); box-shadow:0 16px 36px rgba(74,8,4,.18); }
.portal-metrics strong { display:block; font-family:var(--serif); font-size:38px; line-height:1; color:#DA291C; }
.portal-metrics span { display:block; margin-top:10px; color:#6F4E49; }

.portal-citation-section { margin-top:30px; padding:34px 38px; border:1px solid rgba(218,41,28,.34); border-radius:32px; background:radial-gradient(circle at 50% 24%, rgba(255,255,255,.20), transparent 30%), radial-gradient(circle at 14% 86%, rgba(255,255,255,.13), transparent 24%), linear-gradient(145deg, #DA291C 0%, #C72419 46%, #A61911 100%); box-shadow:0 28px 76px rgba(122,18,12,.24); }
.portal-citation-section h2 { margin:0 0 28px; font-family:var(--serif); font-size:clamp(34px, 4vw, 52px); line-height:1.08; letter-spacing:-.035em; color:#FFFFFF; }
.citation-boundary-list { list-style:none; margin:0; padding:0; display:grid; gap:16px; }
.citation-boundary-list li { position:relative; padding-left:22px; color:rgba(255,255,255,.88); font-size:15px; line-height:1.78; font-weight:500; }
.citation-boundary-list li::before { content:""; position:absolute; left:0; top:.78em; width:8px; height:8px; border-radius:999px; background:#FFFFFF; box-shadow:0 0 0 5px rgba(255,255,255,.14); }
.citation-boundary-list strong { color:#FFFFFF; font-weight:900; }

.portal-snapshot-section .portal-section-head h2 { color:#FFFFFF; }
.portal-snapshot-section .portal-section-head p { color:rgba(255,255,255,.86); }
.strategy-visual-section {
  margin-top: 36px;
  min-height: 320px;
  display:grid;
  grid-template-columns: minmax(0, .88fr) minmax(420px, .92fr);
  gap: 32px;
  align-items:center;
  padding: 28px 32px;
  border: 1px solid rgba(240,194,188,.78);
  border-radius: 30px;
  background: linear-gradient(145deg, rgba(255,247,245,.98), rgba(255,224,217,.90));
  box-shadow: 0 18px 48px rgba(126,22,14,.13);
}
.strategy-copy h2 { margin:0; font-family:var(--serif); font-size:clamp(30px,3.8vw,46px); line-height:1.08; letter-spacing:-.04em; color:#2A1715; }
.strategy-copy p { margin:14px 0 0; color:#6F4E49; line-height:1.72; font-weight:500; }
.strategy-tags { display:flex; flex-wrap:wrap; gap:10px; margin-top:20px; }
.strategy-tags button { border:1px solid rgba(240,194,188,.76); border-radius:999px; padding:8px 13px; background:#FFFFFF; color:#DA291C; font-weight:900; box-shadow:0 8px 20px rgba(31,41,51,.04); }
.strategy-visual { width:100%; filter: drop-shadow(0 18px 30px rgba(126,22,14,.10)); }
.strategy-visual svg { display:block; width:100%; height:auto; }
.competition-section { margin-top: 30px; }
.competition-radar-section {
  grid-template-columns: minmax(260px, .78fr) minmax(0, 1fr);
  min-height: 300px;
  gap: 34px;
  padding: 34px 42px;
  overflow:hidden;
  background:
    radial-gradient(circle at 76% 18%, rgba(255,255,255,.20), transparent 24%),
    radial-gradient(circle at 10% 86%, rgba(255,255,255,.14), transparent 30%),
    linear-gradient(145deg, #DA291C 0%, #C72419 46%, #A61911 100%);
}
.competition-radar-visual {
  width:min(100%, 310px);
  justify-self:center;
  filter: drop-shadow(0 18px 28px rgba(122,18,12,.12));
}
.competition-radar-visual svg { display:block; width:100%; height:auto; }
.competition-radar-copy { max-width: 560px; }
.competition-radar-copy h2 { color:#FFFFFF; }
.competition-radar-copy .portal-eyebrow { margin-bottom: 12px; color:rgba(255,255,255,.82); }
.competition-radar-copy p { max-width: 520px; font-size:16px; line-height:1.78; color:rgba(255,255,255,.86); }
.competition-radar-actions { gap:14px; margin-top:24px; }
.competition-radar-actions button {
  min-width: 132px;
  padding: 12px 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, #FFFFFF, #FFF0ED);
  border-color: rgba(255,255,255,.38);
  box-shadow: 0 14px 32px rgba(74,8,4,.20);
  cursor:pointer;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.competition-radar-actions button:hover {
  transform: translateY(-2px);
  border-color:#FFFFFF;
  box-shadow: 0 18px 38px rgba(74,8,4,.26);
}
.portal-competition-band {
  min-height: 300px;
  display:grid;
  grid-template-columns: minmax(0, .7fr) minmax(560px, 1fr);
  gap: 40px;
  align-items:center;
  padding: 52px;
  background:
    radial-gradient(circle at 88% 18%, rgba(242,106,91,.20), transparent 30%),
    linear-gradient(135deg, rgba(255,255,255,.92), rgba(255,244,242,.86));
}
.portal-competition-band p { margin: 18px 0 0; color:#6F4E49; line-height:1.85; }
.competition-points { grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top:0; }
.competition-points button { min-height: 150px; border-radius:28px; background:rgba(255,255,255,.76); border-color:rgba(240,194,188,.72); }
@media (max-width: 980px) {
  .portal-home { width: min(100% - 28px, 1080px); }
  .portal-hero { min-height: auto; }
  .knowledge-map { min-height:auto; gap:0; margin-top:28px; }
  .knowledge-node-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap:14px; }
  .knowledge-node { min-height:136px; padding:18px; border-radius:24px; }
  .knowledge-node:hover { transform:translateY(-2px); }
  .portal-timeline { grid-template-columns: 1fr; gap: 22px; padding-top: 0; }
  .portal-timeline::before { left: 25px; right:auto; top: 12px; bottom: 12px; width: 2px; height:auto; background: linear-gradient(180deg, rgba(22,151,164,.35), transparent); }
  .portal-timeline-step { display:grid; grid-template-columns: 50px 1fr; gap: 18px; text-align:left; align-items:start; }
  .portal-timeline-step > span { margin:0; }
  .portal-feature,
  .portal-feature.reverse,
  .portal-feature-dark,
  .portal-competition-band { grid-template-columns: 1fr; }
  .strategy-visual-section { grid-template-columns: 1fr; min-height:auto; padding:22px; }
  .strategy-visual { order:-1; }
  .portal-section-head { display:block; }
  .portal-section-head p { margin-top:12px; }
  .portal-focus-row,
  .portal-metrics,
  .competition-points { grid-template-columns: 1fr; }
}

@media (max-width: 900px) {
  .ui-review-hero h1 { font-size:48px; }
  .home-triad-grid, .compact-group-grid { grid-template-columns:1fr; }
  .curated-card { grid-template-columns:1fr; }
  .curated-art { min-height:210px; }
}


.path-section { max-width: 1280px; padding-top: 34px; padding-bottom: 40px; }
.path-section .section-head h2 { font-size: clamp(34px, 3vw, 48px); }
.path-section .section-head p { font-size: 17px; }
.path-strip { border-radius: 28px; box-shadow: 0 22px 60px rgba(126,22,14,.10); }
.path-step { min-height: 190px; padding: 26px 20px; }
.path-step .num { font-size: 18px; }
.path-step h3 { font-size: 22px; line-height: 1.18; }
.path-step p { font-size: 15px; line-height: 1.55; }
.inline-group-links { display:flex; flex-wrap:wrap; gap:10px; margin-top:14px; }
.inline-group-link { border:1px solid var(--line); border-radius:999px; padding:8px 13px; background:#fff; color:#2A1715; font-weight:800; cursor:pointer; box-shadow:var(--shadow-sm); }
.inline-group-link:hover { border-color:rgba(218,41,28,.35); transform:translateY(-1px); }
.curated-card { grid-template-columns: minmax(300px, 40%) minmax(0,1fr); }
.curated-body h3 { margin-top:6px; }
@media (max-width: 1080px) { .ui-review-hero h1 { white-space: normal; } }


/* Home reading path emphasis: make 01-06 feel like a recommended roadmap. */
.path-section {
  max-width: 1180px;
  margin: 22px auto 36px;
  padding: 36px 34px 40px;
  border: 1px solid rgba(38, 99, 118, .13);
  border-radius: 30px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.98), rgba(244,250,250,.94)),
    radial-gradient(circle at 14% 0%, rgba(242,106,91,.12), transparent 36%),
    radial-gradient(circle at 88% 16%, rgba(218,41,28,.07), transparent 30%);
  box-shadow: 0 24px 60px rgba(19, 67, 86, .11);
}
.path-section .section-head {
  margin-bottom: 24px;
  align-items: flex-start;
}
.path-section .section-head h2 {
  font-size: clamp(34px, 3.1vw, 42px);
  letter-spacing: -.035em;
  color: #2A1715;
}
.path-section .section-head p {
  max-width: 760px;
  font-size: 15.5px;
  color: #6F4E49;
  line-height: 1.7;
}
.path-strip {
  position: relative;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
  border: 0;
  background: transparent;
  border-radius: 0;
  overflow: visible;
}
.path-strip::before {
  content: ";
  position: absolute;
  left: 8%;
  right: 8%;
  top: 47px;
  height: 2px;
  background: linear-gradient(90deg, rgba(218,41,28,.10), rgba(218,41,28,.44), rgba(218,41,28,.10));
  z-index: 0;
}
.path-step {
  position: relative;
  z-index: 1;
  min-height: 190px;
  padding: 18px 16px 17px;
  border: 1px solid rgba(27, 74, 92, .11) !important;
  border-radius: 22px;
  background: rgba(255,255,255,.95) !important;
  box-shadow: 0 12px 30px rgba(22, 58, 74, .085);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
.path-step:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 40px rgba(22, 58, 74, .14);
  border-color: rgba(218,41,28,.24) !important;
}
.path-step:not(:last-child)::after {
  content: →;
  position: absolute;
  right: -15px;
  top: 36px;
  width: 19px;
  height: 19px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #DA291C;
  background: #FFF7F5;
  border: 1px solid rgba(218,41,28,.17);
  font-size: 13px;
  font-weight: 900;
  z-index: 2;
}
.path-step .num {
  width: 50px;
  height: 35px;
  min-height: 35px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  font-family: var(--serif);
  font-size: 20px;
  line-height: 1;
  color: #DA291C;
  background: rgba(218,41,28,.09);
  border: 1px solid rgba(218,41,28,.15);
}
.path-step h3 {
  min-height: 42px;
  margin: 0 0 8px;
  font-size: 16px;
  line-height: 1.3;
  color: #2A1715;
}
.path-step p {
  min-height: auto;
  margin: 0;
  color: #7A5E59;
  font-size: 13px;
  line-height: 1.55;
}
.home-triad-section {
  max-width: 1080px;
  margin: 0 auto 28px;
  padding: 0 28px 16px;
}
.home-triad-panel {
  border-radius: 22px;
  padding: 18px;
  background:
    linear-gradient(135deg, rgba(218,41,28,.78), rgba(242,106,91,.66)),
    repeating-linear-gradient(90deg, rgba(255,255,255,.055) 0 1px, transparent 1px 64px);
  box-shadow: 0 14px 36px rgba(126,22,14,.10);
}
.home-triad-badge {
  padding: 5px 11px;
  margin-bottom: 10px;
  font-size: 12px;
  opacity: .86;
}
.home-triad-grid { gap: 10px; }
.home-triad-card {
  min-height: 118px;
  border-radius: 18px;
  padding: 14px;
  background: rgba(255,255,255,.105);
  border-color: rgba(255,255,255,.18);
}
.home-triad-card:hover {
  transform: translateY(-2px);
  background: rgba(255,255,255,.14);
}
.home-triad-card .triad-icon { font-size: 20px; margin-bottom: 6px; opacity: .9; }
.home-triad-card h3 { font-size: 18px; margin-bottom: 4px; }
.home-triad-card p { font-size: 12px; line-height: 1.4; color: rgba(255,255,255,.80); }
.home-triad-card strong { margin-top: 8px; font-size: 12px; opacity: .9; }
@media (max-width: 1080px) {
  .path-section { margin: 16px 14px 26px; padding: 28px 22px 30px; }
  .path-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .path-strip::before { display: none; }
  .path-step:not(:last-child)::after { display: none; }
}
@media (max-width: 760px) {
  .path-section { padding: 24px 16px; border-radius: 24px; }
  .path-section .section-head { display: block; margin-bottom: 18px; }
  .path-section .section-head h2 { font-size: 30px; margin-bottom: 8px; }
  .path-strip { grid-template-columns: 1fr; gap: 10px; }
  .path-step { min-height: auto; padding: 16px; }
  .path-step .num { margin-bottom: 10px; }
  .home-triad-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div class="topbar">
  <div class="brand">
    <strong>即时零售医药行业信息库</strong>
    <span>Strategy intelligence desk</span>
  </div>
  <nav class="nav-tabs" aria-label="主导航">
    <button id="tab-home" onclick="navigateView('home')">行业总览</button>
    <button id="tab-search" onclick="navigateView('search')">智能查询</button>
    <button id="tab-library" onclick="navigateView('library')">行业资料</button>
  </nav>
  <div class="topbar-actions" id="topbarActions" aria-label="页面操作">
    <button class="top-back-link" id="topBackLink" onclick="goBack()">← 返回上一页</button>
  </div>
  <div class="global-search">
    <span class="search-mark">⌕</span>
    <input id="topSearch" placeholder="搜索战略议题、公司、政策、关键数据" autocomplete="off">
  </div>
  <div class="auth-area" id="authArea"></div>
</div>
<main class="page">
  <section id="view-home" class="view"></section>
  <section id="view-search" class="view"></section>
  <section id="view-issue" class="view"></section>
  <section id="view-group" class="view"></section>
  <section id="view-doc" class="view"></section>
  <section id="view-library" class="view"></section>
</main>
<script id="site-data" type="application/json">__SITE_DATA__</script>
<script>
const SITE = JSON.parse(document.getElementById('site-data').textContent);
const DOCS = SITE.documents;
const ISSUES = SITE.issues;
const MODULES = SITE.modules;
const PATH = SITE.learningPath;
const POLICY_GUIDE = SITE.policyGuide || [];

function estimateReadingMinutes(doc) {
  const len = (doc.rawText || doc.summary || '').length;
  return Math.max(8, Math.min(35, Math.ceil(len / 600)));
}
function sourceTierReason(doc, issue) {
  const text = [doc.title, doc.path, doc.contentType, doc.summary, (doc.rawText || '').slice(0, 2400)].join(' ');
  const major = {
    competition: ['美团','阿里','淘宝闪购','京东','京东健康','阿里健康'],
    pharmacy: ['益丰','大参林','老百姓','一心堂','健之佳','漱玉平民','国大','国药一致'],
    pharma: ['华润三九','云南白药','汤臣倍健','百济神州','信达生物','再鼎医药'],
    market: ['中康','西普会','商务部','米内网','艾瑞','易观','CCFA'],
    policy: ['医保','药监','卫健','疾控','处方药','药品流通'],
    medical: ['疾病','病种','医学','慢病','概念']
  }[issue.id] || [];
  const hits = major.filter(k => text.includes(k)).slice(0, 3);
  if (hits.length && /财报|公告|官方|年报|季报|原文/.test(text)) return `主要企业报告/权威材料：${hits.join('、')}`;
  if (/政策|监管|医保|药监|卫健|疾控|财报|公告|官方|交易所|港交所|巨潮/.test(text) || doc.citationStatus === '可正式引用') return '官方/监管/财报/公告优先';
  if (/中康|西普会|商务部|艾瑞|易观|CCFA|米内网|行业机构|行业报告/.test(text)) return '权威机构报告补充';
  if (/研报|券商|研究报告|可供研判参考/.test(text)) return '研报观点，仅作研判参考';
  return '主题匹配补充阅读';
}
function curatedScore(doc, issue) {
    const text = [doc.title, doc.path, doc.contentType, doc.summary].join(' ');
  let score = issueScoreClient(doc, issue);
  if (doc.citationStatus === '可正式引用') score += 30;
  if (/财报|公告|官方|政策|监管|医保|药监|卫健|疾控/.test(text)) score += 24;
  if (/研报|券商/.test(text)) score -= 6;
  if (doc.lastUpdated) score += 5;
  return score;
}
function issueScoreClient(doc, issue) {
  const text = [doc.title, doc.path, doc.summary, doc.searchAliases, doc.module, doc.entity, (doc.rawText || '').slice(0, 2500)].join(' ');
  let score = 0;
  [...(issue.keywords || []), ...(issue.queries || [])].forEach(k => {
    if (!k) return;
    if ((doc.title || '').includes(k) || (doc.path || '').includes(k)) score += 5;
    else if (text.includes(k)) score += 2;
  });
  return score;
}
function pathAllowedClient(doc, issue) {
  const include = issue.includePathPrefixes || [];
  const exclude = issue.excludePathPrefixes || [];
  if (include.length && !include.some(prefix => (doc.path || '').startsWith(prefix))) return false;
  if (exclude.some(prefix => (doc.path || '').startsWith(prefix))) return false;
  return true;
}
const ISSUE_ACTIVE_FILTER = {};
const CONTENT_TYPE_SORT = ['财报数据','行业报告','研报摘要','公开新闻','医学基础','综合分析','政策监管','治理口径','索引'];
function docsForIssue(issue) {
  return DOCS
    .filter(doc => !doc.isIndex && pathAllowedClient(doc, issue) && issueScoreClient(doc, issue) > 0)
    .map(doc => ({ doc, score: curatedScore(doc, issue), minutes: estimateReadingMinutes(doc), reason: sourceTierReason(doc, issue) }))
    .sort((a, b) => b.score - a.score || (b.doc.lastUpdated || '').localeCompare(a.doc.lastUpdated || ''));
}
function curatedDocsFromItems(items, maxItems = 16) {
  const picked = [];
  const seen = new Set();
  let total = 0;
  for (const item of items) {
    const key = (item.doc.title || item.doc.id).replace(/[\s·：:（）()《》\-—_]+/g, '');
    if (seen.has(key)) continue;
    if (total + item.minutes > 300 && total >= 180) continue;
    picked.push(item);
    seen.add(key);
    total += item.minutes;
    if (picked.length >= maxItems || (total >= 240 && picked.length >= 10)) break;
  }
  return { items: picked, total };
}
function curatedDocsForIssue(issue) {
  return curatedDocsFromItems(docsForIssue(issue));
}
function groupSlug(label) {
  return encodeURIComponent(label || '其他');
}
function contentTypeGroupsForIssue(issue) {
  const curated = curatedDocsForIssue(issue);
  const groups = new Map();
  curated.items.forEach(item => {
    const label = item.doc.contentType || '其他';
    if (!groups.has(label)) groups.set(label, { label, slug: groupSlug(label), count: 0, items: [] });
    const group = groups.get(label);
    group.count += 1;
    group.items.push(item);
  });
  return [...groups.values()].sort((a, b) => {
    const rankA = CONTENT_TYPE_SORT.includes(a.label) ? CONTENT_TYPE_SORT.indexOf(a.label) : CONTENT_TYPE_SORT.length;
    const rankB = CONTENT_TYPE_SORT.includes(b.label) ? CONTENT_TYPE_SORT.indexOf(b.label) : CONTENT_TYPE_SORT.length;
    return rankA - rankB || a.label.localeCompare(b.label, 'zh-Hans-CN');
  });
}
function filteredCuratedDocsForIssue(issue, filterSlug) {
  if (!filterSlug || filterSlug === 'all') return curatedDocsForIssue(issue);
  const group = contentTypeGroupsForIssue(issue).find(item => item.slug === filterSlug);
  if (!group) return curatedDocsForIssue(issue);
  const total = group.items.reduce((sum, item) => sum + item.minutes, 0);
  return { items: group.items, total };
}
function docArtClass(doc) {
  const text = [doc.contentType, doc.title, doc.path].join(' ');
  if (/政策|监管|医保|药监/.test(text)) return 'policy';
  if (/财报|公告|业绩/.test(text)) return 'finance';
  if (/疾病|医学|病种|慢病/.test(text)) return 'medical';
  if (/研报|研究/.test(text)) return 'research';
  if (/新闻|动态|资讯/.test(text)) return 'news';
  return 'finance';
}
function docArtIcon(doc) {
  const cls = docArtClass(doc);
  return ({policy:'⚖️', finance:'📊', medical:'💊', research:'📄', news:'📰'}[cls] || '📌');
}
function issueSpecificCoverImage(doc, issue) {
  if (issue && issue.id === 'policy' && doc.id === 'doc-0800e61de0a4') {
    return 'assets/doc_cards_web/policy_20260617/doc-0800e61de0a4-policy.jpg';
  }
  return doc.coverImage || '';
}
function curatedCardHtml(item, issue) {
  const doc = item.doc;
  const reasonShort = (item.reason || '').replace('主要企业报告/权威材料：', '主要企业/权威材料：');
  const coverImage = issueSpecificCoverImage(doc, issue);
  const coverHtml = coverImage ? `<img src="${esc(coverImage)}" alt="" loading="lazy">` : '';
  return `<article class="curated-card">
    <button class="curated-art ${docArtClass(doc)} ${coverImage ? 'has-cover' : ''}" data-icon="${esc(docArtIcon(doc))}" onclick="navigateDoc('${doc.id}')" aria-label="打开 ${esc(doc.title)}">${coverHtml}</button>
    <div class="curated-body">
      <div class="curated-kind">${esc(doc.contentType || issue.visualLabel || 'READING')}</div>
      <h3><button class="text-link" onclick="navigateDoc('${doc.id}')">${esc(doc.title)}</button></h3>
      <div class="curated-dash">
        <span>${esc(doc.citationStatus || '')}</span>
        <span>预计 ${item.minutes} 分钟</span>
        ${doc.lastUpdated ? '<span>更新 ' + esc(doc.lastUpdated) + '</span>' : ''}
        <span>${esc(reasonShort)}</span>
      </div>
    </div>
  </article>`;
}

function groupIconForInline(label) {
  const icons = {
    '财报数据': '📊',
    '行业报告': '📚',
    '研报摘要': '📄',
    '公开新闻': '📰',
    '医学基础': '🩺',
    '综合分析': '🧩',
    '政策监管': '⚖️',
    '全部': '🔎'
  };
  return icons[label] || groupIcon(label) || '🔎';
}
function inlineGroupLinks(issue, activeSlug = 'all') {
  const curated = curatedDocsForIssue(issue);
  const groups = contentTypeGroupsForIssue(issue);
  const items = [{ label:'全部', slug:'all', count:curated.items.length }, ...groups].filter(item => item.count > 0);
  if (!items.length) return '';
  return `<div class="issue-filter-pills">${items.map(item => `
    <button class="issue-filter-pill ${item.slug === activeSlug ? 'active' : ''}" onclick="filterIssueDocs('${issue.id}', '${item.slug}')"><span class="pill-icon">${groupIconForInline(item.label)}</span><span>${esc(item.label)}</span><span class="pill-count">${item.count}</span></button>
  `).join('')}</div>`;
}


function renderHomeTriad() {
  return `
    <section class="portal-feature portal-feature-visual">
      <div class="portal-feature-copy">
        <span class="portal-eyebrow">01 · 行业全局认知</span>
        <h2>把即时零售医药生态放在一张图里看</h2>
        <p>从行业资讯、平台竞争、连锁药店、药企机会、政策监管和医学基础六个入口，先建立全局框架，再进入精选阅读路径。</p>
        <div class="portal-focus-row">
          <button onclick="navigateIssue('market')"><strong>行业资讯</strong><span>规模、趋势、渠道变化</span></button>
          <button onclick="navigateIssue('pharmacy')"><strong>连锁药店</strong><span>门店、履约、经营质量</span></button>
          <button onclick="navigateIssue('policy')"><strong>政策监管</strong><span>医保、药监、合规边界</span></button>
        </div>
      </div>
      ${renderEcosystemVisual()}
    </section>
    <section class="portal-feature portal-feature-dark">
      <div class="portal-feature-copy">
        <span class="portal-eyebrow">02 · 证据与判断</span>
        <h2>从资料入口快速走到业务判断</h2>
        <p>每个模块都保留原有精选阅读路径，适合先看结论，再回到文档、关键词和引用边界做验证。</p>
      </div>
      <div class="portal-insight-strip">
        <button onclick="navigateView('search')"><strong>智能查询</strong><span>用问题进入资料</span></button>
        <button onclick="navigateIssue('competition')"><strong>平台动向</strong><span>追踪竞对动作</span></button>
        <button onclick="navigateIssue('medical')"><strong>医学基础</strong><span>补齐品类认知</span></button>
      </div>
    </section>
    <section class="portal-feature portal-feature-visual reverse">
      ${renderDemandVisual()}
      <div class="portal-feature-copy">
        <span class="portal-eyebrow">03 · 用户需求洞察</span>
        <h2>用搜索词、场景和品类线索理解购药需求</h2>
        <p>把医保支付、慢病管理、夜间急用药、平台搜索和药店供给放在同一条用户路径里，帮助判断真实需求和经营机会。</p>
        <div class="portal-focus-row">
          <button onclick="openSearch('慢病管理')"><strong>慢病管理</strong><span>长期用药与复购</span></button>
          <button onclick="openSearch('医保支付')"><strong>医保支付</strong><span>支付方式与转化</span></button>
          <button onclick="openSearch('夜间购药')"><strong>场景需求</strong><span>急用药与履约体验</span></button>
        </div>
      </div>
    </section>`;
}

function renderHeroKnowledgeVisual() {
  const nodes = [
    { no: '01', cls: 'node-market', issue: 'market', title: '行业', desc: '趋势｜供给｜需求' },
    { no: '02', cls: 'node-platform', issue: 'competition', title: '平台', desc: '入口｜补贴｜履约' },
    { no: '03', cls: 'node-pharmacy', issue: 'pharmacy', title: '药店', desc: '门店｜库存｜服务' },
    { no: '04', cls: 'node-pharma', issue: 'pharma', title: '药企', desc: '产品｜营销｜合作' },
    { no: '05', cls: 'node-policy', issue: 'policy', title: '政策', desc: '医保｜处方｜监管' },
    { no: '06', cls: 'node-disease', issue: 'medical', title: '疾病', desc: '场景｜用药｜人群' },
  ];
  return `<div class="knowledge-map knowledge-map-grid" aria-label="即时零售医药行业信息库认知地图">
    <div class="knowledge-node-grid">
      ${nodes.map(node => `<button class="knowledge-node ${node.cls}" onclick="navigateIssue('${node.issue}')">
        <span class="knowledge-no">${node.no}</span>
        <strong>${node.title}</strong>
        <span>${node.desc}</span>
      </button>`).join('')}
    </div>
  </div>`;
}

function renderEcosystemVisual() {
  return `<div class="portal-illustration ecosystem-visual" aria-label="医药即时零售生态插图">
    <svg viewBox="0 0 520 340" role="img">
      <defs><linearGradient id="ecoA" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFF0ED"/><stop offset="1" stop-color="#ffffff"/></linearGradient></defs>
      <rect width="520" height="340" rx="32" fill="url(#ecoA)"/><circle cx="264" cy="170" r="78" fill="#ffffff" stroke="#F2B8B0" stroke-width="2"/><text x="264" y="164" text-anchor="middle" font-size="18" font-weight="800" fill="#2A1715">即时零售</text><text x="264" y="190" text-anchor="middle" font-size="13" fill="#6F4E49">平台 × 药店 × 药企</text>
      <g stroke="#F26A5B" stroke-width="2" fill="none"><path d="M264 92L128 78M326 122L438 82M332 214L438 258M198 218L92 264"/></g>
      <g font-size="13" font-weight="800" fill="#2A1715"><rect x="66" y="48" width="124" height="58" rx="20" fill="#fff" stroke="#F2B8B0"/><text x="128" y="83" text-anchor="middle">行业报告</text><rect x="376" y="52" width="124" height="58" rx="20" fill="#fff" stroke="#F2B8B0"/><text x="438" y="87" text-anchor="middle">平台竞争</text><rect x="376" y="232" width="124" height="58" rx="20" fill="#fff" stroke="#F2B8B0"/><text x="438" y="267" text-anchor="middle">政策监管</text><rect x="30" y="238" width="124" height="58" rx="20" fill="#fff" stroke="#F2B8B0"/><text x="92" y="273" text-anchor="middle">医学基础</text></g>
    </svg>
  </div>`;
}

function renderDemandVisual() {
  return `<div class="portal-illustration demand-visual" aria-label="用户需求与搜索词洞察插图">
    <svg viewBox="0 0 520 340" role="img">
      <rect width="520" height="340" rx="32" fill="#FFF7F5"/><path d="M72 260C134 176 176 198 224 150C280 94 350 96 444 70" fill="none" stroke="#0B86C8" stroke-width="5" stroke-linecap="round"/><g fill="#0B86C8"><circle cx="72" cy="260" r="8"/><circle cx="224" cy="150" r="8"/><circle cx="444" cy="70" r="8"/></g>
      <g font-size="13" font-weight="800"><rect x="54" y="54" width="124" height="40" rx="20" fill="#ffffff" stroke="#F2B8B0"/><text x="116" y="80" text-anchor="middle" fill="#2A1715">医保支付</text><rect x="206" y="238" width="124" height="40" rx="20" fill="#ffffff" stroke="#F2B8B0"/><text x="268" y="264" text-anchor="middle" fill="#2A1715">慢病复购</text><rect x="338" y="176" width="128" height="40" rx="20" fill="#ffffff" stroke="#F2B8B0"/><text x="402" y="202" text-anchor="middle" fill="#2A1715">夜间急用药</text></g>
      <g opacity=".84"><rect x="74" y="126" width="58" height="118" rx="16" fill="#dff6f8"/><rect x="150" y="166" width="58" height="78" rx="16" fill="#bfecef"/><rect x="344" y="104" width="58" height="140" rx="16" fill="#dff6f8"/><rect x="420" y="132" width="58" height="112" rx="16" fill="#bfecef"/></g>
    </svg>
  </div>`;
}

function renderDemandInsightSection() {
  return `<section class="strategy-visual-section demand-section">
    <div class="strategy-copy">
      <span class="portal-eyebrow">03 · Demand intelligence</span>
      <h2>搜索、需求与购药场景</h2>
      <p>把搜索词、用户动机、品类机会和购药场景放到一条路径里，帮助判断真实需求和转化抓手。</p>
      <div class="strategy-tags"><button onclick="openSearch('搜索词 用户需求')">搜索词</button><button onclick="openSearch('购药场景 用户路径')">购药场景</button><button onclick="openSearch('品类机会 转化路径')">转化路径</button></div>
    </div>
    ${renderDemandDashboardVisual()}
  </section>`;
}

function renderDemandDashboardVisual() {
  return `<div class="strategy-visual" aria-label="搜索词、用户需求、购药场景数据插图">
    <svg viewBox="0 0 520 320" role="img">
      <rect width="520" height="320" rx="28" fill="#FFFFFF"/>
      <rect x="42" y="38" width="300" height="44" rx="22" fill="#FFF4F2" stroke="#F0C2BC"/><circle cx="66" cy="60" r="9" fill="#DA291C" opacity=".88"/><text x="88" y="65" font-size="14" font-weight="800" fill="#7A5E59">医保支付 / 慢病管理 / 夜间购药</text>
      <path d="M62 238C126 176 168 196 218 142C280 76 352 96 450 62" fill="none" stroke="#DA291C" stroke-width="5" stroke-linecap="round" opacity=".88"/>
      <g fill="#F26A5B"><circle cx="62" cy="238" r="7"/><circle cx="218" cy="142" r="7"/><circle cx="450" cy="62" r="7"/></g>
      <g opacity=".92"><rect x="70" y="126" width="54" height="92" rx="14" fill="#E9E2D2"/><rect x="144" y="154" width="54" height="64" rx="14" fill="#D7EEE9"/><rect x="354" y="112" width="54" height="106" rx="14" fill="#E9E2D2"/><rect x="428" y="138" width="54" height="80" rx="14" fill="#D7EEE9"/></g>
      <g font-size="12" font-weight="900" fill="#2A1715"><text x="70" y="268">搜索触发</text><text x="210" y="118">需求识别</text><text x="390" y="42">转化机会</text></g>
    </svg>
  </div>`;
}

function renderCompetitionInsight() {
  return `<section class="strategy-visual-section competition-section competition-radar-section">
    ${renderCompetitionRadarVisual()}
    <div class="strategy-copy competition-radar-copy">
      <span class="portal-eyebrow">COMPETITION RADAR</span>
      <h2>竞争雷达（待补充）</h2>
      <p>围绕京东健康、阿里健康、美团买药、叮当快药等玩家，沉淀平台定位、供给履约、增长机会和后续动作。</p>
      <div class="strategy-tags competition-radar-actions">
        <button onclick="(SITE.weeklyChanges || {}).docId ? navigateDoc(SITE.weeklyChanges.docId) : navigateIssue('market')">本周变化</button>
      </div>
    </div>
  </section>`;
}

function renderCompetitionRadarVisual() {
  return `<div class="competition-radar-visual" aria-label="竞争雷达插图">
    <svg viewBox="0 0 360 360" role="img">
      <defs>
        <radialGradient id="radarGlow" cx="50%" cy="50%" r="55%">
          <stop offset="0%" stop-color="#FFFFFF" stop-opacity=".42"/>
          <stop offset="62%" stop-color="#DA291C" stop-opacity=".10"/>
          <stop offset="100%" stop-color="#FFDCD4" stop-opacity=".95"/>
        </radialGradient>
        <linearGradient id="radarSweep" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#DA291C" stop-opacity=".06"/>
          <stop offset="100%" stop-color="#DA291C" stop-opacity=".34"/>
        </linearGradient>
        <filter id="radarBlur" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="3"/>
        </filter>
      </defs>
      <rect x="10" y="10" width="340" height="340" rx="34" fill="#FFF3F0"/>
      <rect x="10" y="10" width="340" height="340" rx="34" fill="url(#radarGlow)"/>
      <g fill="none" stroke="#DA291C" stroke-width="3.2" opacity=".46">
        <circle cx="180" cy="180" r="48"/>
        <circle cx="180" cy="180" r="94"/>
        <circle cx="180" cy="180" r="140"/>
      </g>
      <g stroke="#DA291C" stroke-width="1.4" opacity=".20">
        <path d="M180 40v280"/>
        <path d="M40 180h280"/>
        <path d="M81 81l198 198"/>
        <path d="M279 81L81 279"/>
      </g>
      <path d="M180 180 L294 64 A160 160 0 0 1 320 178 Z" fill="url(#radarSweep)" opacity=".78"/>
      <path d="M180 180 L294 64" stroke="#DA291C" stroke-width="7" stroke-linecap="round" filter="url(#radarBlur)" opacity=".24"/>
      <path d="M180 180 L294 64" stroke="#DA291C" stroke-width="3.2" stroke-linecap="round" opacity=".56"/>
      <g fill="#DA291C" filter="url(#radarBlur)" opacity=".36">
        <circle cx="108" cy="138" r="11"/>
        <circle cx="246" cy="108" r="8"/>
        <circle cx="130" cy="242" r="7"/>
        <circle cx="224" cy="238" r="9"/>
      </g>
      <g fill="#DA291C" opacity=".76">
        <circle cx="108" cy="138" r="4.8"/>
        <circle cx="246" cy="108" r="3.8"/>
        <circle cx="130" cy="242" r="3.4"/>
        <circle cx="224" cy="238" r="4"/>
      </g>
    </svg>
  </div>`;
}



const DOC_BY_ID = Object.fromEntries(DOCS.map(doc => [doc.id, doc]));
const ISSUE_BY_ID = Object.fromEntries(ISSUES.map(issue => [issue.id, issue]));
const BACKLINKS = {};
DOCS.forEach(doc => (doc.outgoing || []).forEach(id => {
  if (!BACKLINKS[id]) BACKLINKS[id] = [];
  BACKLINKS[id].push(doc.id);
}));
let currentQuery = '';
const AUTH_KEY = 'industry-info-library-auth';
const BUILT_IN_ERP = 'jdhjsls';
const BUILT_IN_PASSWORD = 'jdhjslssf';
const PROTECTED_VIEWS = new Set(['search', 'issue', 'doc', 'library']);
let currentUser = readAuthUser();
let pendingRoute = '';
let appBackStack = [];
let currentRoute = location.hash || '#home';

function esc(value) {
  return String(value || '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function readAuthUser() {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    return null;
  }
}
function isLoggedIn() {
  return Boolean(currentUser && currentUser.erp);
}
function viewHash(name) {
  if (name === 'search') return '#search';
  if (name === 'library') return '#library';
  return location.hash || '#home';
}
function routeHashForView(name) {
  if (name === 'home') return '#home';
  if (name === 'search') return '#search';
  if (name === 'library') return '#library';
  return '';
}
function setAppRoute(hash, mode = 'replace') {
  const target = hash || '#home';
  if (mode === 'push') {
    const from = currentRoute || location.hash || '#home';
    if (from !== target) {
      appBackStack.push(from);
      currentRoute = target;
      history.pushState({ appRoute: target }, '', target);
      return;
    }
  }
  currentRoute = target;
  history.replaceState({ appRoute: target }, '', target);
}
function fallbackHash(name) {
  if (name === 'search') return '#search';
  if (name === 'library') return '#library';
  return '#home';
}
function activateView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-tabs button').forEach(b => b.classList.remove('active'));
  const view = document.getElementById(`view-${name}`);
  if (view) view.classList.add('active');
  const tab = document.getElementById(`tab-${name}`);
  if (tab) tab.classList.add('active');
  updateTopbarBack(name);
}
function updateTopbarBack(name) {
  const back = document.getElementById('topBackLink');
  const showBack = ['issue', 'group', 'doc'].includes(name);
  if (back) back.classList.toggle('visible', showBack);
}
function updateAuthUI() {
  const area = document.getElementById('authArea');
  if (!area) return;
  if (isLoggedIn()) {
    area.innerHTML = `<div class="auth-user"><span>已登录</span><strong>${esc(currentUser.erp)}</strong><button class="logout-button" onclick="logout()">退出</button></div>`;
  } else {
    area.innerHTML = `<button class="auth-button" onclick="showLoginRequired('search', '#search')">登录</button>`;
  }
}
function showLoginRequired(viewName = 'search', targetHash = '') {
  const view = document.getElementById(`view-${viewName}`) || document.getElementById('view-search');
  pendingRoute = targetHash || pendingRoute || viewHash(viewName);
  view.innerHTML = `
    <section class="locked-section">
      <div class="login-card">
        <div class="kicker">Access required</div>
        <h2>需要登录后查看</h2>
        <p>请输入 ERP 和密码。未登录状态下仅开放首页，登录后可使用查询、议题和资料正文。</p>
        <form class="login-form" onsubmit="loginFromForm(event)">
          <label>ERP
            <input name="erp" autocomplete="username" placeholder="请输入 ERP">
          </label>
          <label>密码
            <input name="password" type="password" autocomplete="current-password" placeholder="请输入密码">
          </label>
          <button class="login-submit" type="submit">登录并继续</button>
          <div class="login-error" id="loginError"></div>
        </form>
      </div>
    </section>
  `;
  activateView(view.id.replace('view-', ''));
  const erpInput = view.querySelector('input[name="erp"]');
  if (erpInput) erpInput.focus();
}
function loginFromForm(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const erp = String(form.elements.erp.value || '').trim();
  const password = String(form.elements.password.value || '').trim();
  const error = document.getElementById('loginError');
  if (!erp || !password) {
    if (error) error.textContent = '请输入 ERP 和密码。';
    return;
  }
  if (erp !== BUILT_IN_ERP || password !== BUILT_IN_PASSWORD) {
    if (error) error.textContent = 'ERP 或密码不正确。';
    return;
  }
  currentUser = { erp, loginAt: new Date().toISOString() };
  localStorage.setItem(AUTH_KEY, JSON.stringify(currentUser));
  updateAuthUI();
  const target = pendingRoute || '#search';
  pendingRoute = '';
  if (location.hash === target) {
    handleRoute();
  } else {
    location.hash = target;
  }
}
function logout() {
  localStorage.removeItem(AUTH_KEY);
  currentUser = null;
  pendingRoute = '';
  updateAuthUI();
  showView('home');
}
function words(query) {
  const q = String(query || '').trim().toLowerCase();
  if (!q) return [];
  const chunks = q.match(/[a-z0-9]+|[\u4e00-\u9fff]+/g) || [];
  const tokens = [];
  chunks.forEach(chunk => {
    tokens.push(chunk);
    if (/[\u4e00-\u9fff]/.test(chunk) && chunk.length > 2) {
      for (let i = 0; i < chunk.length - 1; i++) tokens.push(chunk.slice(i, i + 2));
    }
  });
  return [...new Set(tokens.filter(Boolean))];
}
function scoreText(target, tokens, weight) {
  const text = String(target || '').toLowerCase();
  let score = 0;
  tokens.forEach(token => {
    if (text.includes(token)) score += weight * (token.length > 1 ? 2 : 1);
  });
  return score;
}
function highlight(text, tokens) {
  const source = esc(text || '');
  const normalizedTokens = [...new Set(tokens.filter(t => t.length > 1))]
    .sort((a, b) => b.length - a.length)
    .slice(0, 10);
  let out = source;
  normalizedTokens.forEach(token => {
    if (out.includes('<mark>')) return;
    const safe = token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    out = out.replace(new RegExp(safe, 'gi'), m => `<mark>${m}</mark>`);
  });
  return out;
}
function docPath(doc) {
  return [doc.module, doc.entity, doc.contentType].filter(Boolean).join(' / ');
}
function statusClass(status) {
  if (status === '可正式引用') return '可正式引用';
  if (status === '慎用') return '慎用';
  if (status === '需核验') return '需核验';
  return status || '可内部用';
}
function docChipHtml(doc) {
  return `
    <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">
      <span class="tag">${esc(doc.contentType || '资料')}</span>
      <span class="tag">${esc(doc.citationStatus || '')}</span>
      ${doc.lastUpdated ? `<span class="tag">${esc(doc.lastUpdated)}</span>` : ''}
    </div>
  `;
}
function groupIcon(label) {
  const map = {
    '财报数据': '📊',
    '行业报告': '📚',
    '研报摘要': '📄',
    '公开新闻': '📰',
    '医学基础': '🩺',
    '综合分析': '🧩',
    '政策监管': '⚖️',
  };
  return map[label] || '📌';
}

function groupDescription(issue, group) {
  const label = group.label;
  const count = group.count || (group.docs || []).length;
  const base = {
    '财报数据': '优先展示公司公告、年报、季报和业绩材料。',
    '行业报告': '沉淀行业规模、渠道结构、竞争格局和关键增长判断。',
    '研报摘要': '集中展示券商研报、行业研究和机构观点资料。',
    '公开新闻': '汇总公开新闻动态、合作事件和经营变化。',
    '医学基础': '整理疾病、病种、药事和健康管理基础概念。',
    '综合分析': '汇总结构化摘要、业务洞察和专题补充资料。',
    '政策监管': '集中展示政策、监管、医保、药监和合规相关资料。',
  };
  return `${base[label] || '按主题聚合相关资料。'} 当前匹配 ${count} 篇文档。`;
}
function relatedDocsForIssue(issue) {
  return (issue.relatedDocs || []).map(doc => `
    <article class="related-doc">
      <h4><button class="text-link" onclick="navigateDoc('${doc.id}')">${esc(doc.title)}</button></h4>
      <p>${esc(doc.summary || doc.path)}</p>
      ${docChipHtml(doc)}
    </article>
  `).join('');
}
function groupEntriesForIssue(issue) {
  const groups = contentTypeGroupsForIssue(issue);
  if (!groups.length) return `<div class="related-list">${relatedDocsForIssue(issue)}</div>`;
  return `<div class="group-entry-grid">${groups.map(group => `
    <button class="group-entry-card" onclick="navigateGroup('${issue.id}', '${groupSlug(group.label)}')">
      <div class="group-entry-icon">${groupIcon(group.label)}</div>
      <h3>${esc(group.label)}</h3>
      <p>${esc(groupDescription(issue, group))}</p>
      <span class="tag">进入小页面</span>
    </button>
  `).join('')}</div>`;
}
function findGroup(issue, slug) {
  return contentTypeGroupsForIssue(issue).find(group => group.slug === slug);
}
function renderGroup(issueId, slug) {
  const issue = ISSUE_BY_ID[issueId];
  if (!issue) return;
  const group = findGroup(issue, slug);
  if (!group) return;
  const docs = (group.items || []).map(item => item.doc);
  document.getElementById('view-group').innerHTML = `
    <section class="issue-page">
      <div class="issue-detail accent-${esc(issue.accent)}">
        <main>
          <div class="group-hero-banner">
            <div class="group-hero-title">
              <div class="issue-icon">${groupIcon(group.label)}</div>
              <div>
                <div class="kicker">${esc(issue.visualLabel || issue.eyebrow)}</div>
                <h1>${esc(group.label)}</h1>
                <p class="hero-lead">${esc(groupDescription(issue, group))}</p>
              </div>
            </div>
            <div class="group-meta-line">
              <span class="tag">${docs.length} 篇文档</span>
              <span class="tag">按匹配度排序</span>
              <span class="tag">最近更新优先</span>
              <span class="tag">引用级别辅助排序</span>
            </div>
          </div>
          <div class="group-doc-list">
            ${docs.length ? docs.map(doc => `
              <article class="group-doc-card">
                <h3><button class="text-link" onclick="navigateDoc('${doc.id}')">${esc(doc.title)}</button></h3>
                <p>${esc(doc.summary || doc.path)}</p>
                ${docChipHtml(doc)}
              </article>
            `).join('') : '<p style="color:var(--muted);margin:0">暂无匹配文档</p>'}
          </div>
        </main>
        <aside>
          <div class="aside-block">
            <h3>排序规则</h3>
            <p>按匹配度、最近更新、引用级别排序。</p>
          </div>
          <div class="aside-block">
            <h3>所属类目</h3>
            <p>${esc(issue.title)}</p>
          </div>
        </aside>
      </div>
    </section>
  `;
}

function showView(name, options = {}) {
  const mode = options.mode || 'replace';
  if (PROTECTED_VIEWS.has(name) && !isLoggedIn()) {
    const target = viewHash(name);
    setAppRoute(target, mode);
    showLoginRequired(name, target);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  activateView(name);
  const hash = routeHashForView(name);
  if (hash) setAppRoute(hash, mode);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function navigateView(name) {
  if (name === 'search') renderSearch(currentQuery);
  if (name === 'library') renderLibrary();
  showView(name, { mode: 'push' });
}
function navigateIssue(id) {
  if (!isLoggedIn()) {
    const target = `#issue/${id}`;
    setAppRoute(target, 'push');
    showLoginRequired('issue', target);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  ISSUE_ACTIVE_FILTER[id] = ISSUE_ACTIVE_FILTER[id] || 'all';
  renderIssue(id);
  activateView('issue');
  setAppRoute(`#issue/${id}`, 'push');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function filterIssueDocs(issueId, slug) {
  ISSUE_ACTIVE_FILTER[issueId] = slug || 'all';
  renderIssue(issueId);
  activateView('issue');
  setAppRoute(`#issue/${issueId}`, 'replace');
  const section = document.getElementById('issue-curated-list');
  if (section) section.scrollIntoView({ behavior:'smooth', block:'start' });
}
function navigateGroup(issueId, slug) {
  if (!isLoggedIn()) {
    const target = `#group/${issueId}/${slug}`;
    setAppRoute(target, 'push');
    showLoginRequired('group', target);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  ISSUE_ACTIVE_FILTER[issueId] = slug || 'all';
  renderIssue(issueId);
  activateView('issue');
  setAppRoute(`#issue/${issueId}`, 'replace');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function navigateDoc(id) {
  if (!isLoggedIn()) {
    const target = `#doc/${id}`;
    setAppRoute(target, 'push');
    showLoginRequired('doc', target);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  renderDoc(id);
  activateView('doc');
  setAppRoute(`#doc/${id}`, 'push');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function goBack(fallback = 'home') {
  const previous = appBackStack.pop();
  renderRoute(previous || fallbackHash(fallback), 'replace');
}
function openSearch(query) {
  currentQuery = query || currentQuery;
  if (!isLoggedIn()) {
    setAppRoute('#search', 'push');
    showLoginRequired('search', '#search');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  renderSearch(currentQuery);
  showView('search', { mode: 'push' });
  const input = document.getElementById('searchInput');
  if (input) input.value = currentQuery;
}
function scrollToHeading(anchor) {
  const target = document.getElementById(anchor);
  if (!target) return;
  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  document.querySelectorAll('.outline-item').forEach(item => item.classList.remove('active'));
  const active = document.querySelector(`.outline-item[data-anchor="${anchor}"]`);
  if (active) active.classList.add('active');
}
function runSearch(query) {
  const tokens = words(query);
  if (!tokens.length) return [];
  const issueResults = ISSUES.map(issue => {
    const corpus = [issue.title, issue.summary, issue.takeaway, issue.keywords?.join(' '), issue.queries?.join(' ')].join(' ');
    return {
      kind: '战略议题',
      id: issue.id,
      title: issue.title,
      summary: issue.summary,
      meta: `${issue.relatedDocs.length} 篇相关资料`,
      score: scoreText(issue.title, tokens, 8) + scoreText(corpus, tokens, 3),
      action: 'issue',
    };
  }).filter(r => r.score > 0);
  const docResults = DOCS.map(doc => {
    const corpus = [doc.title, doc.path, doc.module, doc.entity, doc.contentType, doc.citationStatus, doc.summary, doc.rawText].join(' ');
    return {
      kind: '原始资料',
      id: doc.id,
      title: doc.title,
      summary: doc.summary || doc.rawText.slice(0, 130),
      meta: `${docPath(doc)} / ${doc.citationStatus}`,
      aliases: doc.searchAliases || '',
      score: scoreText(doc.title, tokens, 6) + scoreText(doc.path, tokens, 4) + scoreText(doc.searchAliases, tokens, 8) + scoreText(corpus, tokens, 1),
      action: 'doc',
    };
  }).filter(r => r.score > 0 && !DOC_BY_ID[r.id]?.isIndex);
  return [...issueResults, ...docResults].sort((a, b) => b.score - a.score).slice(0, 30);
}
function renderWeeklyChanges() {
  const weekly = SITE.weeklyChanges || {};
  const items = weekly.items || [];
  const lead = items[0] || {};
  return `
    <section class="briefing-section">
      <div class="section-head">
        <h2>${esc(weekly.title || '本周行业变化')}</h2>
        <p>${esc(weekly.subtitle || '结论 + 影响总结')}${weekly.updated ? ` · 更新 ${esc(weekly.updated)}` : ''}</p>
      </div>
      <div class="weekly-layout">
        <article class="weekly-lead-card">
          <div class="news-icon">📰</div>
          <span class="tag">本周核心结论</span>
          <h3 style="font-family:var(--serif);font-size:28px;margin:12px 0 10px">${esc(lead.conclusion || '持续跟踪权威行业变化')}</h3>
          <p>${esc(lead.impact || '从政策、监管、平台竞争和医药零售变化中识别影响。')}</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px">
            <span class="tag">医保局</span><span class="tag">药监局</span><span class="tag">官方资讯</span>
          </div>
          ${weekly.docId ? `<button class="text-link" style="margin-top:16px" onclick="navigateDoc('${weekly.docId}')">查看本周行业变化详情</button>` : ''}
        </article>
        <div class="weekly-grid">
          ${items.map((item, index) => `
            <article class="briefing-card ${index > 0 ? 'align-top-body' : ''}">
              <span class="tag">${esc(item.type)}</span>
              <div class="weekly-card-body">
                <h3>结论</h3>
                <p>${esc(item.conclusion)}</p>
                <h3>影响总结</h3>
                <p>${esc(item.impact)}</p>
              </div>
              ${item.docId ? `<div class="card-action"><button class="text-link" onclick="navigateDoc('${item.docId}')">变化详情 →</button></div>` : ''}
            </article>
          `).join('')}
        </div>
      </div>
    </section>
  `;
}

function renderCompetitionRadar() {
  const radar = SITE.competitionRadar || {};
  const platforms = radar.platforms || [];
  return `
    <section class="briefing-section radar-section">
      <div class="section-head">
        <h2>${esc(radar.title || '竞争雷达')}</h2>
        <p>${esc(radar.subtitle || '美团 / 阿里 / 京东每周监控')}${radar.updated ? ` · 更新 ${esc(radar.updated)}` : ''}</p>
      </div>
      <div class="radar-grid">
        ${platforms.map(platform => `
          <article class="radar-card">
            <div class="radar-top">
              <div>
                <span class="tag">${esc(platform.focus)}</span>
                <h3>${esc(platform.name)}</h3>
              </div>
              <div class="platform-mark">${esc((platform.name || '?').slice(0,1))}</div>
            </div>
            <p><strong>本周动作：</strong>${esc(platform.action)}</p>
            <p><strong>可能影响：</strong>${esc(platform.impact)}</p>
            <div class="radar-signals">${(platform.signals || []).map(signal => `<span class="tag">${esc(signal)}</span>`).join('')}</div>
            ${platform.docId ? `<button class="text-link" style="margin-top:12px" onclick="navigateDoc('${platform.docId}')">查看平台资料</button>` : ''}
          </article>
        `).join('')}
      </div>
      ${radar.docId ? `<button class="text-link" style="margin-top:14px" onclick="navigateDoc('${radar.docId}')">查看竞争雷达详情</button>` : ''}
    </section>
  `;
}

function renderHome() {
  const stats = SITE.stats;
  const homeSteps = [
    { label: '行业', issue: 'market', note: '看行业趋势、供给格局、消费需求和医药零售整体变化。' },
    { label: '用户', query: '用户画像 购药动机 搜索行为 转化路径', note: '理解用户画像、购药动机、搜索行为和转化路径。' },
    { label: '平台', issue: 'competition', note: '对比京东、阿里、美团、抖音等平台的策略与能力。' },
    { label: '疾病', issue: 'medical', note: '从病种场景出发，理解高频需求、用药链路和人群特征。' },
    { label: '政策', issue: 'policy', note: '追踪医保、处方药、互联网医疗和监管变化。' },
    { label: '药企', issue: 'pharma', note: '关注药企动向、产品布局、营销打法和合作机会。' },
  ];
  const pathHtml = homeSteps.map((step, index) => `
      <button class="portal-timeline-step" onclick="${step.issue ? `navigateIssue('${step.issue}')` : `openSearch('${esc(step.query)}')`}">
        <span>${String(index + 1).padStart(2, '0')}</span>
        <div><h3>${esc(step.label)}</h3><p>${esc(step.note)}</p></div>
      </button>
    `).join('');
  document.getElementById('view-home').innerHTML = `
    <div class="portal-home">
      <section class="portal-hero">
        <div class="portal-hero-copy">
          <div class="kicker">Medical intelligence hub</div>
          <h1>即时零售医药行业信息库</h1>
          <p class="hero-lead">聚合行业资讯、平台竞争、连锁药店、药企机会、政策监管与医学基础知识，帮助行业内外用户快速定位问题、阅读证据和追踪变化。</p>
          <div class="hero-search">
            <input placeholder="搜索：医保支付 / 美团买药 / 连锁药店 / 慢病管理" onkeydown="if(event.key==='Enter') openSearch(this.value)">
            <button class="hero-search-button" aria-label="search" onclick="openSearch(this.previousElementSibling.value)"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.8" cy="10.8" r="6.2"></circle><path d="M15.4 15.4L20 20"></path></svg></button>
          </div>
        </div>
      </section>

      <section class="portal-map-section">
        <h2 class="cognition-title">认知地图</h2>
        ${renderHeroKnowledgeVisual()}
      </section>


      ${renderCompetitionInsight()}

      <section class="portal-snapshot-section">
        <div class="portal-section-head">
          <h2>信息库快照</h2>
          <p>当前为网站可见资料口径，不包含索引、临时脚本和未纳入展示的源文件。</p>
        </div>
        <div class="portal-metrics">
          <div><strong>${stats.docCount}</strong><span>篇可见资料</span></div>
          <div><strong>${stats.moduleCount}</strong><span>个可见模块</span></div>
          <div><strong>${esc(stats.latestUpdate || '-')}</strong><span>最近资料日期</span></div>
        </div>
      </section>

      <section class="portal-citation-section">
        <h2>引用边界</h2>
        <ul class="citation-boundary-list">
          <li><strong>可正式引用：</strong>公司公告、交易所披露文件、年报/季报中的收入、利润、现金流、门店数、线上销售额、O2O销售额等原始披露数据。</li>
          <li><strong>可研判参考：</strong>本文对渠道机会、即时零售适配性、平台合作价值和经营压力的判断，属于基于公开事实的业务分析。</li>
          <li><strong>数据适用说明：</strong>未拆分的平台GMV、即时零售订单量、处方药占比、单一平台销售额、单店履约时效、药师服务质量等；对外或跨部门正式引用时，优先回到本文“信息溯源清单”的原文链接。</li>
        </ul>
      </section>
    </div>
  `;
}

function renderSearch(query = '') {
  const results = runSearch(query);
  const tokens = words(query);
  const quick = ['医药零售行业', '美团买药 份额', '连锁药店 O2O 占比', 'GLP-1 禁售影响', '处方药监管', '哪些药线上不能卖'];
  const resultsHtml = renderSearchResults(results, tokens, query);
  document.getElementById('view-search').innerHTML = `
    <section class="search-section">
      <div class="section-head">
        <h2>智能查询</h2>
        <p>先返回战略议题和结论卡，再返回原始资料，方便从问题进入证据。</p>
      </div>
      <div class="search-layout">
        <aside class="query-panel">
          <h3>常用查询</h3>
          ${quick.map(q => `<button class="quick-query" onclick="openSearch('${esc(q)}')">${esc(q)}</button>`).join('')}
        </aside>
        <section class="result-panel">
          <div class="global-search" style="max-width:none;margin:0 0 14px">
            <span class="search-mark">⌕</span>
            <input id="searchInput" value="${esc(query)}" placeholder="输入自然问题或关键词" oninput="updateSearchResults(this.value)">
          </div>
          <div id="searchResults">${resultsHtml}</div>
        </section>
      </div>
    </section>
  `;
}
function renderSearchResults(results, tokens, query) {
  if (!results.length) {
    return `<div class="empty">${query ? '没有找到相关内容' : '输入关键词后开始检索'}</div>`;
  }
  return results.map(r => `
    <article class="result-item">
      <div class="result-kind">${esc(r.kind)}</div>
      <h3><button class="text-link" onclick="${r.action === 'issue' ? `navigateIssue('${r.id}')` : `navigateDoc('${r.id}')`}">${highlight(r.title, tokens)}</button></h3>
      <p>${highlight(r.summary, tokens)}</p>
      <span class="tag">${esc(r.meta)}</span>
      ${r.aliases ? `<span class="tag">匹配：${highlight(r.aliases, tokens)}</span>` : ''}
    </article>
  `).join('');
}
function updateSearchResults(query) {
  currentQuery = query;
  const resultsEl = document.getElementById('searchResults');
  if (!resultsEl) return;
  const tokens = words(query);
  resultsEl.innerHTML = renderSearchResults(runSearch(query), tokens, query);
}
function renderPolicyGuide() {
  if (!POLICY_GUIDE.length) return '';
  return `
    <section class="policy-guide">
      <div class="guide-head">
        <span>Regulatory quick guide</span>
        <h2>药品线上/线下销售边界速查</h2>
        <p>用于先判断风险边界，正式引用和业务落地前仍需回到最新法规原文、药监清单和属地合规意见。</p>
      </div>
      <div class="policy-grid">
        ${POLICY_GUIDE.map(item => `
          <article class="policy-row">
            <strong>${esc(item.scope)}</strong>
            <p>${esc(item.items)}</p>
            <small>${esc(item.note)}</small>
          </article>
        `).join('')}
      </div>
    </section>
  `;
}
function renderIssue(id) {
  const issue = ISSUE_BY_ID[id];
  if (!issue) return;
  const activeFilter = ISSUE_ACTIVE_FILTER[id] || 'all';
  const curated = filteredCuratedDocsForIssue(issue, activeFilter);
  const titleParts = String(issue.title || '').split('：');
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
            <div class="issue-hero-divider" aria-hidden="true"></div>
          </section>
          <section class="curated-section">
            <div class="curated-head">
              <div class="curated-title-row">
                <h2>精选阅读路径</h2>
              </div>
              <div class="curated-subline">
                <p>优先收录主要企业报告、官方/监管/财报/公告和权威来源资料。</p>
                <span class="tag curated-time-tag">${curated.items.length}&nbsp;篇&nbsp;·&nbsp;约&nbsp;${Math.round(curated.total / 60 * 10) / 10}&nbsp;小时</span>
              </div>
              ${inlineGroupLinks(issue, activeFilter)}
            </div>
            <div class="curated-list" id="issue-curated-list">
              ${curated.items.length ? curated.items.map(item => curatedCardHtml(item, issue)).join('') : '<p style="color:var(--muted);margin:0">暂无匹配文档</p>'}
            </div>
          </section>
        </main>
      </div>
    </section>
  `;
}
function toggleDocNav(forceVisible) {
  const shell = document.getElementById('doc-shell');
  const toggle = document.getElementById('doc-nav-toggle');
  if (!shell) return;
  const shouldHide = typeof forceVisible === 'boolean' ? !forceVisible : !shell.classList.contains('doc-nav-hidden');
  shell.classList.toggle('doc-nav-hidden', shouldHide);
  if (toggle) {
    toggle.innerHTML = shouldHide ? '&#9776;' : '&#9783;';
    toggle.setAttribute('aria-expanded', shouldHide ? 'false' : 'true');
  }
}
function renderDoc(id) {
  const doc = DOC_BY_ID[id];
  if (!doc) return;
  const sameIssue = ISSUES
    .filter(issue => (issue.relatedDocs || []).some(item => item.id === doc.id))
    .slice(0, 4);
  const nextDocs = [];
  sameIssue.forEach(issue => {
    (issue.relatedDocs || []).forEach(item => {
      if (item.id !== doc.id && !nextDocs.some(existing => existing.id === item.id)) nextDocs.push(item);
    });
  });
  if (nextDocs.length < 4) {
    DOCS.filter(item => item.module === doc.module && item.id !== doc.id).slice(0, 6).forEach(item => {
      if (!nextDocs.some(existing => existing.id === item.id)) nextDocs.push(item);
    });
  }
  const useCompactDocLayout = true;
  const nextReadingBlock = `
          <div class="aside-block next-reading-block">
            <h3>下一步建议阅读</h3>
            ${nextDocs.slice(0, 5).map(item => `<button class="mini-doc" onclick="navigateDoc('${item.id}')">${esc(item.title)}</button>`).join('') || '<p>暂无推荐</p>'}
          </div>`;
  document.getElementById('view-doc').innerHTML = `
    <section class="doc-page ${useCompactDocLayout ? 'doc-page-compact' : ''}">
      <div id="doc-shell" class="doc-shell ${useCompactDocLayout ? 'doc-shell-compact' : ''}">
        <aside class="doc-nav" id="doc-nav-panel">
          <div class="doc-nav-head">
            <strong>文档导航</strong>
            <button class="doc-nav-hide" onclick="toggleDocNav(false)">隐藏</button>
          </div>
          <div class="aside-block">
            <h3>文档位置</h3>
            <p>${esc(docPath(doc) || doc.path)}</p>
          </div>
          <div class="aside-block">
            <h3>正文大纲</h3>
            <ul class="outline-list">
              ${(doc.headings || []).map(h => `<li><button class="outline-item level-${h.level}" title="${esc(h.text)}" data-anchor="${esc(h.anchor)}" onclick="scrollToHeading('${esc(h.anchor)}')">${esc(h.text)}</button></li>`).join('') || '<li><span class="outline-item">无二级标题</span></li>'}
            </ul>
          </div>
          ${useCompactDocLayout ? nextReadingBlock : ''}
        </aside>
        <main class="doc-main">
          <div class="doc-toolbar">
            <button class="doc-nav-toggle" id="doc-nav-toggle" onclick="toggleDocNav()" aria-expanded="true" title="显示或隐藏左侧栏" aria-label="显示或隐藏左侧栏">&#9783;</button>
          </div>
          <h1>${esc(doc.title)}</h1>
          <div class="doc-meta">
            <span class="tag">${esc(doc.contentType)}</span>
            <span class="tag">${esc(doc.citationStatus)}</span>
            ${doc.lastUpdated ? `<span class="tag">更新 ${esc(doc.lastUpdated)}</span>` : ''}
          </div>
          <article class="doc-content">${doc.html}</article>
        </main>
        ${useCompactDocLayout ? '' : `<aside class="doc-aside">
          <div class="aside-block">
            <h3>所属战略议题</h3>
            ${sameIssue.map(issue => `<button class="mini-doc" onclick="navigateIssue('${issue.id}')">${esc(issue.title)}</button>`).join('') || '<p>暂无匹配议题</p>'}
          </div>
          ${nextReadingBlock}
        </aside>`}
      </div>
    </section>
  `;
  document.querySelectorAll('.doc-content a[data-doc]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      navigateDoc(link.dataset.doc);
    });
  });
}
function renderLibrary() {
  const modules = MODULES.map(module => `
    <section class="module-row">
      <div class="module-head">
        <h3>${esc(module.name)}</h3>
        <span class="tag">${module.count} 篇资料</span>
      </div>
      <div class="doc-list">
        ${module.docs.map(doc => `<a href="#doc/${doc.id}" onclick="navigateDoc('${doc.id}');return false">${esc(doc.title)}<br><span style="color:var(--muted);font-size:12px">${esc(doc.contentType)} / ${esc(doc.citationStatus)}</span></a>`).join('')}
      </div>
    </section>
  `).join('');
  document.getElementById('view-library').innerHTML = `
    <section class="library-section">
      <div class="section-head">
        <h2>行业资料</h2>
        <p>这里保留真正的行业信息正文；维护指引、数据口径、引用台账和校验报告不进入公开阅读界面。</p>
      </div>
      <div class="library-panel">${modules}</div>
    </section>
  `;
}
function renderRoute(hash, mode = 'replace') {
  const targetHash = hash || '#home';
  if (targetHash.startsWith('#doc/')) {
    if (!isLoggedIn()) {
      pendingRoute = targetHash;
      setAppRoute(targetHash, mode);
      showLoginRequired('doc', targetHash);
      return;
    }
    renderDoc(targetHash.slice(5));
    activateView('doc');
    setAppRoute(targetHash, mode);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (targetHash.startsWith('#group/')) {
    if (!isLoggedIn()) {
      pendingRoute = targetHash;
      setAppRoute(targetHash, mode);
      showLoginRequired('group', targetHash);
      return;
    }
    const parts = targetHash.slice(7).split('/');
    renderGroup(parts[0], parts[1]);
    activateView('group');
    setAppRoute(targetHash, mode);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (targetHash.startsWith('#issue/')) {
    if (!isLoggedIn()) {
      pendingRoute = targetHash;
      setAppRoute(targetHash, mode);
      showLoginRequired('issue', targetHash);
      return;
    }
    renderIssue(targetHash.slice(7));
    activateView('issue');
    setAppRoute(targetHash, mode);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (targetHash === '#search') {
    if (!isLoggedIn()) {
      pendingRoute = targetHash;
      setAppRoute(targetHash, mode);
      showLoginRequired('search', targetHash);
      return;
    }
    renderSearch(currentQuery);
    showView('search', { mode });
  } else if (targetHash === '#library') {
    if (!isLoggedIn()) {
      pendingRoute = targetHash;
      setAppRoute(targetHash, mode);
      showLoginRequired('library', targetHash);
      return;
    }
    renderLibrary();
    showView('library', { mode });
  } else {
    showView('home', { mode });
  }
}
function handleRoute() {
  renderRoute(location.hash || '#home', 'replace');
}
document.getElementById('topSearch').addEventListener('keydown', event => {
  if (event.key === 'Enter') openSearch(event.currentTarget.value);
});
document.getElementById('topSearch').addEventListener('input', event => {
  currentQuery = event.currentTarget.value;
});
renderHome();
if (isLoggedIn()) {
  renderSearch('');
  renderLibrary();
}
updateAuthUI();
window.addEventListener('hashchange', handleRoute);
handleRoute();
</script>
</body>
</html>
"""


def main() -> None:
    site_data = build_site_data()
    rendered = HTML_TEMPLATE.replace(
        "__SITE_DATA__",
        json.dumps(site_data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
    )
    OUTPUT_FILE.write_text(rendered, encoding="utf-8")
    print(f"[OK] output: {OUTPUT_FILE}")
    print(f"     documents: {site_data['stats']['docCount']}")
    print(f"     issues: {len(site_data['issues'])}")
    print(f"     size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()




















