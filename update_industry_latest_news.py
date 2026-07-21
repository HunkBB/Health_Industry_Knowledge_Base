#!/usr/bin/env python3
"""Update authoritative industry latest news markdown before site build.

Only writes publicly traceable official-source items. If network/pages fail, the
script keeps a source-entry document without fabricating news facts.
"""
from __future__ import annotations

import html
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "05-行业机构" / "行业最新权威资讯.md"
TODAY = datetime.now().strftime("%Y-%m-%d")

KEYWORDS = ("医", "药", "医保", "卫生", "健康", "医疗", "药品", "处方", "零售", "流通", "慢病", "集采", "监管", "疾控")

SOURCES = [
    ("中国政府网·政策最新", "https://www.gov.cn/zhengce/zuixin/"),
    ("国家卫生健康委·新闻", "https://www.nhc.gov.cn/xcs/yqfkdt/list_gzbd.shtml"),
    ("国家药品监督管理局·要闻", "https://www.nmpa.gov.cn/yaowen/ypjgyw/index.html"),
    ("国家医疗保障局·动态", "https://www.nhsa.gov.cn/col/col14/index.html"),
    ("中国疾病预防控制中心", "https://www.chinacdc.cn/yyrdgz/"),
]

@dataclass
class NewsItem:
    source: str
    title: str
    url: str
    published: str
    summary: str


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CodexIndustryInfoBot/1.0"})
    with urllib.request.urlopen(req, timeout=18) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    charset_match = re.search(r"charset=([\w-]+)", ctype, re.I)
    charsets = [charset_match.group(1)] if charset_match else []
    charsets += ["utf-8", "gb18030"]
    for charset in charsets:
        try:
            return raw.decode(charset)
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")


def strip_tags(value: str) -> str:
    value = re.sub(r"<script[\s\S]*?</script>", "", value, flags=re.I)
    value = re.sub(r"<style[\s\S]*?</style>", "", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_date(value: str) -> str:
    match = re.search(r"(20\d{2})[年\-/\.](\d{1,2})[月\-/\.](\d{1,2})", value)
    if not match:
        return ""
    y, m, d = match.groups()
    return f"{y}-{int(m):02d}-{int(d):02d}"


def extract_links(source: str, base_url: str, page_html: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for href, body in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>', page_html, flags=re.I):
        title = strip_tags(body)
        if len(title) < 8 or len(title) > 120:
            continue
        if not any(keyword in title for keyword in KEYWORDS):
            continue
        if href.startswith("javascript:") or href.startswith("#"):
            continue
        url = urllib.parse.urljoin(base_url, href)
        if not url.startswith("http"):
            continue
        links.append((title, url))
    deduped = []
    seen = set()
    for title, url in links:
        key = (title, url)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((title, url))
    return deduped[:8]


def extract_detail(source: str, title: str, url: str) -> NewsItem | None:
    try:
        detail = fetch(url)
    except Exception:
        return None
    plain = strip_tags(detail)
    published = normalize_date(plain[:4000]) or normalize_date(url)
    if not published:
        return None
    desc = ""
    meta = re.search(r'<meta\b[^>]*(?:name|property)=["\'](?:description|og:description)["\'][^>]*content=["\']([^"\']+)["\']', detail, flags=re.I)
    if meta:
        desc = strip_tags(meta.group(1))
    if not desc:
        paragraphs = [strip_tags(p) for p in re.findall(r"<p\b[^>]*>([\s\S]*?)</p>", detail, flags=re.I)]
        paragraphs = [p for p in paragraphs if len(p) >= 24]
        desc = paragraphs[0] if paragraphs else title
    desc = desc[:180]
    return NewsItem(source=source, title=title, url=url, published=published, summary=desc)


def collect_items() -> tuple[list[NewsItem], list[str]]:
    items: list[NewsItem] = []
    errors: list[str] = []
    seen_urls = set()
    for source, url in SOURCES:
        try:
            page = fetch(url)
            links = extract_links(source, url, page)
        except Exception as exc:
            errors.append(f"{source}：{type(exc).__name__}")
            continue
        for title, link in links:
            if link in seen_urls:
                continue
            seen_urls.add(link)
            item = extract_detail(source, title, link)
            if item:
                items.append(item)
            if len(items) >= 12:
                break
        if len(items) >= 12:
            break
    items.sort(key=lambda item: item.published, reverse=True)
    return items[:12], errors


def md_link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def render_markdown(items: list[NewsItem], errors: list[str]) -> str:
    source_lines = "\n".join(f"- {md_link(name, url)}" for name, url in SOURCES)
    if items:
        rows = "\n".join(
            f"| {item.published} | {item.source} | {md_link(item.title.replace('|', '｜'), item.url)} | {item.summary.replace('|', '｜')} | 用于更新行业公开信息和政策/监管动态索引，不直接构成业务结论。 |"
            for item in items
        )
    else:
        rows = "| 本次构建未抓取到可自动核验日期的新增条目 | 官方入口 | 请从上方权威入口人工复核 | 自动采集未写入不可追溯新闻事实 | 不生成业务结论 |"
    error_note = "；".join(errors) if errors else "无"
    return f"""# 行业最新权威资讯

> 引用级别：✅可正式引用
> 资料基础：国家部委/监管机构官网、国家级公共卫生机构官网、中国政府网政策发布入口及已核验权威公开来源。
> 最后更新：{TODAY}

## 一句话定位

本文定位为行业最新权威资讯资料，核心关注医药健康、药品监管、医保政策、公共卫生和行业政策相关的最新官方公开动态。

## 使用说明

- 本文由构建前脚本自动采集权威公开入口生成，只保留可追溯标题、发布时间、发布主体和原文链接。
- 本文不写入无法追溯原文的媒体摘要，不替代政策原文、监管文件或公司公告。
- 自动采集异常：{error_note}。

## 数据来源

{source_lines}

## 最新资讯

| 发布时间 | 发布主体 | 标题/原文链接 | 事件摘要 | 信息库影响 |
|:---|:---|:---|:---|:---|
{rows}
"""


def main() -> int:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    items, errors = collect_items()
    OUTPUT_FILE.write_text(render_markdown(items, errors), encoding="utf-8")
    print(f"[OK] latest news updated: {OUTPUT_FILE} ({len(items)} items)")
    if errors:
        print("[WARN] source fetch errors: " + "; ".join(errors))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
