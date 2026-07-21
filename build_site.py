#!/usr/bin/env python3
if __name__ == "__main__":
    try:
        from update_industry_latest_news import main as update_industry_latest_news
        update_industry_latest_news()
    except Exception as exc:
        print(f"[WARN] latest news update skipped: {exc}")
    from build_learning_site import main as build_learning_site

    build_learning_site()
    raise SystemExit

"""
行业信息库 HTML 网站构建脚本
扫描所有 Markdown 文件，转换为 HTML，生成自包含的单文件网站。

用法：
    python build_site.py
    python build_site.py --exclude-raw-financials   # 排除大型原始财报
"""

import os
import re
import json
import sys
import html as html_module
from pathlib import Path
from datetime import datetime

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension

# ============================================================
# 配置
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "行业信息库.html"

# 需要标记为骨架的模块（仅有 _index.md）
SKELETON_MODULES = {"07-京东健康与秒送基准库", "09-用户与场景库", "10-供给与履约库", "11-区域市场库"}

# 内容类型路径映射
CONTENT_TYPE_MAP = {
    "财报数据": "财报数据",
    "官方财报数据": "财报数据",
    "公开新闻": "公开新闻",
    "研报摘要": "研报摘要",
}

# 治理文件（根目录非 _index.md 的文件）
GOVERNANCE_FILES = {
    "数据口径字典", "数据引用台账", "信息覆盖矩阵", "主题交叉索引",
    "原始出处索引", "数据引用补齐清单",
}
# 匹配校验报告文件名模式
GOVERNANCE_PATTERNS = [r"行业信息库校验报告"]


def is_governance_file(stem: str) -> bool:
    """判断是否为治理文件"""
    if stem in GOVERNANCE_FILES:
        return True
    for pattern in GOVERNANCE_PATTERNS:
        if re.search(pattern, stem):
            return True
    return False


# ============================================================
# Slug 生成
# ============================================================
def make_slug(path_parts: list, stem: str) -> str:
    """
    从路径组件生成 URL-safe slug。
    _index.md 文件使用父目录名作为 slug。
    """
    # 对于 _index.md，用目录路径拼接
    if stem.startswith("_"):
        # 用所有路径组件拼接
        parts = [p for p in path_parts if p]
        if parts:
            slug = "-".join(parts) + "-index"
        else:
            slug = "home"  # 根目录的 _index.md
    else:
        # 普通文件：用完整路径区分
        parts = [p for p in path_parts if p and not p.startswith("_")]
        parts.append(stem)
        slug = "-".join(parts)

    # 清理：只保留中文、字母、数字、连字符、点
    slug = re.sub(r"[^一-鿿\w\-.]", "", slug)
    return slug or "root"


def make_simple_slug(stem: str) -> str:
    """仅用文件名生成简单 slug"""
    slug = re.sub(r"[^一-鿿\w\-.]", "", stem)
    return slug or "unknown"


# ============================================================
# Markdown → HTML 转换
# ============================================================
def convert_md_to_html(md_text: str) -> str:
    """将 Markdown 文本转换为 HTML"""
    # 预处理：将 wiki 链接占位符暂时保护
    # （wiki 链接在后面单独处理）
    extensions = [
        TableExtension(),
        FencedCodeExtension(),
        TocExtension(title="目录", anchorlink=True),
    ]
    md = markdown.Markdown(extensions=extensions, tab_length=4)
    result = md.convert(md_text)
    md.reset()
    return result


# ============================================================
# Wiki 链接解析
# ============================================================
def resolve_wiki_links(html_text: str, slug_map: dict) -> tuple:
    """
    解析 [[wiki links]] 并转换为内部导航链接。
    返回 (处理后的HTML, 外链slug列表)
    """
    outgoing = []

    def replace_wiki_link(match):
        target = match.group(1)
        # 查找目标 slug
        target_slug = slug_map.get(target)
        if target_slug:
            outgoing.append(target_slug)
            return f'<a href="#doc/{target_slug}" class="wiki-link" data-slug="{target_slug}">{target}</a>'
        else:
            return f'<span class="wiki-link broken" title="链接目标未找到">{target}</span>'

    result = re.sub(r"\[\[([^\]]+)\]\]", replace_wiki_link, html_text)
    return result, outgoing


# ============================================================
# 内容类型检测
# ============================================================
def detect_content_type(rel_path: str, stem: str) -> str:
    """从文件路径推断内容类型"""
    parts = Path(rel_path).parts

    # 先检查路径中的子目录名
    for part in parts:
        if part in CONTENT_TYPE_MAP:
            return CONTENT_TYPE_MAP[part]
        if part == "综合分析":
            if "结构化摘要" in stem:
                return "结构化摘要"
            if "业务洞察" in stem:
                return "业务洞察"
            return "综合分析"

    # 路径中没有明确类型目录，根据文件名推断
    if "业务洞察" in stem:
        return "业务洞察"
    if "结构化摘要" in stem:
        return "结构化摘要"
    if "新闻动态" in stem or "新闻" in stem:
        return "公开新闻"
    if "研报" in stem:
        return "研报摘要"
    if "财报" in stem:
        return "财报数据"
    if "政策" in stem or "监管" in stem:
        return "政策监管"
    if "摘要" in stem:
        return "综合摘要"
    if "信息摘要" in stem:
        return "综合摘要"
    if "报告" in stem:
        return "行业报告"

    return "其他"


# ============================================================
# 模块/实体提取
# ============================================================
def extract_module_entity(rel_path: str) -> tuple:
    """从相对路径提取模块和实体"""
    parts = Path(rel_path).parts

    module = ""
    entity = ""
    prev_part = ""

    for part in parts:
        if re.match(r"^\d{2}-", part):
            module = part
        elif part in ("财报数据", "官方财报数据", "公开新闻", "研报摘要", "综合分析"):
            continue
        elif not part.endswith(".md") and not part.startswith("_"):
            # 可能是实体名
            # 特殊处理：如果上一级是 OTC与消费健康 或 DTP与特药，用公司名
            # 如果当前就是 OTC/DTP 目录，用目录名作为实体
            if part in ("OTC与消费健康", "DTP与特药"):
                entity = part
            elif prev_part in ("OTC与消费健康", "DTP与特药"):
                # 这是 OTC/DTP 下的公司，用公司名
                entity = part
            else:
                if not entity:
                    entity = part
                else:
                    # 用更具体的层级
                    entity = part
        prev_part = part

    return module, entity


# ============================================================
# 纯文本提取（用于搜索）
# ============================================================
def extract_plain_text(md_text: str) -> str:
    """从 Markdown 文本提取纯文本（用于搜索索引）"""
    # 移除链接语法但保留文字
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md_text)
    # 移除图片
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", text)
    # 移除 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)
    # 移除 Markdown 标记
    text = re.sub(r"^[#]+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # 移除表格分隔线
    text = re.sub(r"^\|?[-:| ]+\|?$", "", text, flags=re.MULTILINE)
    # 移除 wiki 链接括号
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    # 压缩空白
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"  +", " ", text)
    return text.strip()


# ============================================================
# 摘要提取
# ============================================================
def extract_summary(md_text: str) -> str:
    """从文档提取一句话摘要（取第一段非空非标题文本，限200字）"""
    lines = md_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.startswith(">"):
            line = line.lstrip(">").strip()
            if line:
                return line[:200]
        if line.startswith("|") or line.startswith("-") or line.startswith("*"):
            continue
        # 普通段落
        return line[:200]
    return ""


# ============================================================
# 导航树构建
# ============================================================
def build_nav_tree(documents: list) -> dict:
    """构建导航树结构"""
    tree = {
        "governance": [],  # 治理文件
        "modules": {},     # 模块 → 实体 → 内容类型 → 文档列表
        "homeDoc": None,   # 根首页文档 ID
    }

    for doc in documents:
        # 根首页文档
        if doc["path"] == "_index.md":
            tree["homeDoc"] = doc["id"]
            continue

        if doc.get("isGovernance"):
            tree["governance"].append({
                "id": doc["id"],
                "title": doc["title"],
            })
            continue

        module = doc.get("module", "")
        entity = doc.get("entity", "")
        content_type = doc.get("contentType", "")

        # 跳过没有模块的文档（不应该有，但防御性处理）
        if not module:
            continue

        if module not in tree["modules"]:
            tree["modules"][module] = {
                "title": module,
                "isSkeleton": module in SKELETON_MODULES or any(
                    module.startswith(s.split("-")[0]) for s in SKELETON_MODULES
                ),
                "entities": {},
                "indexDoc": None,
                "standaloneDocs": [],
            }

        mod = tree["modules"][module]

        if doc.get("isIndex"):
            mod["indexDoc"] = doc["id"]
            continue

        if entity:
            if entity not in mod["entities"]:
                mod["entities"][entity] = {
                    "title": entity,
                    "contentTypes": {},
                }
            ent = mod["entities"][entity]
            ct = content_type or "其他"
            if ct not in ent["contentTypes"]:
                ent["contentTypes"][ct] = []
            ent["contentTypes"][ct].append({
                "id": doc["id"],
                "title": doc["title"],
            })
        else:
            mod["standaloneDocs"].append({
                "id": doc["id"],
                "title": doc["title"],
                "contentType": content_type,
            })

    return tree


# ============================================================
# 主流程：扫描 + 转换 + 输出
# ============================================================
def scan_and_convert():
    """扫描所有 MD 文件并转换"""
    documents = []
    slug_map = {}  # 文件名 → slug（用于 wiki 链接解析）
    all_slugs = set()  # 用于确保唯一

    # 收集所有文件
    md_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = Path(root) / fname
            rel_path = fpath.relative_to(BASE_DIR)
            md_files.append((fpath, rel_path, fname))

    # 为每个文件生成唯一 slug
    doc_slugs = {}  # (fpath) -> slug
    for fpath, rel_path, fname in sorted(md_files):
        stem = fname[:-3]
        parts = list(rel_path.parent.parts)
        slug = make_slug(parts, stem)
        # 确保唯一
        base_slug = slug
        counter = 1
        while slug in all_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1
        all_slugs.add(slug)
        doc_slugs[fpath] = slug

        # wiki 链接映射：stem → slug（保留第一个，避免覆盖）
        if stem not in slug_map:
            slug_map[stem] = slug

    print(f"Found {len(md_files)} markdown files")
    print(f"Built {len(slug_map)} slug mappings, {len(all_slugs)} unique IDs")

    # 第二遍：转换内容
    for fpath, rel_path, fname in sorted(md_files):
        stem = fname[:-3]
        # 用 fpath 查找该文档的唯一 slug
        slug = doc_slugs.get(fpath, make_simple_slug(stem))
        rel_path_str = str(rel_path).replace("\\", "/")

        # 读取文件
        try:
            md_text = fpath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  WARN: cannot read {rel_path_str}: {e}")
            continue

        # 提取标题
        title = stem
        title_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

        # 检测是否为 _index.md
        is_index = fname == "_index.md"

        # 检测模块和实体
        module, entity = extract_module_entity(rel_path_str)

        # 检测内容类型
        content_type = detect_content_type(rel_path_str, stem)

        # 是否为治理文件
        is_gov = is_governance_file(stem) and not is_index

        # 是否为骨架模块
        is_skeleton = any(s in rel_path_str for s in SKELETON_MODULES) and is_index

        # 提取最后更新日期
        last_updated = ""
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", rel_path_str)
        if date_match:
            last_updated = date_match.group(1)
        date_match2 = re.search(r"最后更新[：:]\s*(\d{4}-\d{2}-\d{2})", md_text)
        if date_match2:
            last_updated = date_match2.group(1)

        # Markdown → HTML
        html_content = convert_md_to_html(md_text)

        # 解析 wiki 链接
        html_content, outgoing = resolve_wiki_links(html_content, slug_map)

        # 提取纯文本（搜索用）
        raw_text = extract_plain_text(md_text)

        # 提取摘要
        summary = extract_summary(md_text)

        doc = {
            "id": slug,
            "title": title,
            "path": rel_path_str,
            "module": module,
            "entity": entity,
            "contentType": content_type,
            "isIndex": is_index,
            "isGovernance": is_gov,
            "isSkeleton": is_skeleton,
            "html": html_content,
            "rawText": raw_text,
            "outgoingLinks": outgoing,
            "summary": summary,
            "lastUpdated": last_updated,
        }
        documents.append(doc)

    print(f"Converted {len(documents)} documents successfully")
    return documents, slug_map


# ============================================================
# HTML 模板
# ============================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>行业信息库</title>
<style>
/* ============================================================
   CSS 变量 & 主题
   ============================================================ */
:root {{
  --ink: #1b2733;
  --muted: #637083;
  --line: #d8dee8;
  --paper: #f7f8f4;
  --panel: #ffffff;
  --panel-hover: #f0f4f8;
  --navy: #1a365d;
  --teal: #0d9488;
  --amber: #d69e2e;
  --red: #e53e3e;
  --green: #38a169;
  --blue: #2b6cb0;
  --shadow: 0 2px 8px rgba(27,39,51,.08);
  --shadow-lg: 0 8px 24px rgba(27,39,51,.12);
  --radius: 8px;
  --radius-sm: 4px;
  --font-body: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", -apple-system, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", "Source Code Pro", "Consolas", monospace;
  --sidebar-w: 280px;
  --meta-w: 300px;
  --header-h: 56px;
  --transition: 0.2s ease;
}}
[data-theme="dark"] {{
  --ink: #e2e8f0;
  --muted: #a0aec0;
  --line: #2d3748;
  --paper: #1a202c;
  --panel: #2d3748;
  --panel-hover: #374151;
  --navy: #90cdf4;
  --teal: #4fd1c5;
  --amber: #f6e05e;
  --red: #fc8181;
  --green: #68d391;
  --blue: #90cdf4;
  --shadow: 0 2px 8px rgba(0,0,0,.3);
  --shadow-lg: 0 8px 24px rgba(0,0,0,.4);
}}

/* ============================================================
   基础重置
   ============================================================ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ font-size: 16px; scroll-behavior: smooth; }}
body {{
  font-family: var(--font-body);
  color: var(--ink);
  background: var(--paper);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}
a {{ color: var(--teal); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
button {{ font: inherit; cursor: pointer; }}
input {{ font: inherit; }}

/* ============================================================
   布局
   ============================================================ */
.app {{
  min-height: 100vh;
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr var(--meta-w);
  grid-template-rows: var(--header-h) 1fr;
  grid-template-areas:
    "header header header"
    "sidebar content meta";
}}

/* Header */
.header {{
  grid-area: header;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 20px;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
}}
.header-logo {{
  font-size: 18px;
  font-weight: 700;
  color: var(--navy);
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.header-logo .icon {{
  font-size: 22px;
}}
.search-box {{
  flex: 1;
  max-width: 480px;
  position: relative;
}}
.search-box input {{
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--paper);
  color: var(--ink);
  font-size: 14px;
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
}}
.search-box input:focus {{
  border-color: var(--teal);
  box-shadow: 0 0 0 3px rgba(13,148,136,.15);
}}
.search-box .search-icon {{
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  font-size: 14px;
  pointer-events: none;
}}
.search-box .search-shortcut {{
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: var(--muted);
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 1px 5px;
  pointer-events: none;
}}
.header-actions {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}}
.btn-icon {{
  width: 36px;
  height: 36px;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--panel);
  color: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all var(--transition);
}}
.btn-icon:hover {{
  border-color: var(--teal);
  background: var(--panel-hover);
}}
.hamburger {{
  display: none;
}}

/* Sidebar */
.sidebar {{
  grid-area: sidebar;
  background: var(--panel);
  border-right: 1px solid var(--line);
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(100vh - var(--header-h));
  position: sticky;
  top: var(--header-h);
  padding: 12px 0;
}}
.sidebar-section {{
  margin-bottom: 4px;
}}
.sidebar-section-title {{
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 16px 4px;
  user-select: none;
}}
.nav-item {{
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  font-size: 13px;
  color: var(--ink);
  cursor: pointer;
  transition: background var(--transition);
  border-radius: 0;
  user-select: none;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}}
.nav-item:hover {{
  background: var(--panel-hover);
}}
.nav-item.active {{
  background: rgba(13,148,136,.08);
  color: var(--teal);
  font-weight: 600;
}}
.nav-item .arrow {{
  font-size: 10px;
  transition: transform var(--transition);
  flex-shrink: 0;
  width: 16px;
  text-align: center;
}}
.nav-item .arrow.open {{
  transform: rotate(90deg);
}}
.nav-item .icon {{
  flex-shrink: 0;
  width: 18px;
  text-align: center;
}}
.nav-item .label {{
  overflow: hidden;
  text-overflow: ellipsis;
}}
.nav-item .count {{
  margin-left: auto;
  font-size: 11px;
  color: var(--muted);
  background: var(--paper);
  padding: 1px 6px;
  border-radius: 10px;
  flex-shrink: 0;
}}
.nav-children {{
  display: none;
}}
.nav-children.open {{
  display: block;
}}
.nav-children .nav-item {{
  padding-left: 32px;
}}
.nav-children .nav-children .nav-item {{
  padding-left: 48px;
}}
.nav-children .nav-children .nav-children .nav-item {{
  padding-left: 64px;
}}
.skeleton-badge {{
  font-size: 10px;
  color: var(--amber);
  margin-left: 4px;
}}

/* Content area */
.content-area {{
  grid-area: content;
  overflow-y: auto;
  max-height: calc(100vh - var(--header-h));
  padding: 24px 32px 80px;
}}
.breadcrumb {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 16px;
  flex-wrap: wrap;
}}
.breadcrumb a {{
  color: var(--muted);
}}
.breadcrumb a:hover {{
  color: var(--teal);
}}
.breadcrumb .sep {{
  color: var(--line);
}}
.doc-header {{
  margin-bottom: 24px;
}}
.doc-title {{
  font-size: 26px;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 8px;
  color: var(--ink);
}}
.doc-meta {{
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--muted);
  flex-wrap: wrap;
}}
.doc-meta .tag {{
  background: rgba(13,148,136,.08);
  color: var(--teal);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}}
.doc-meta .tag.amber {{
  background: rgba(214,158,46,.08);
  color: var(--amber);
}}
.doc-meta .tag.navy {{
  background: rgba(26,54,93,.08);
  color: var(--navy);
}}

/* Content type tabs */
.content-tabs {{
  display: flex;
  gap: 4px;
  border-bottom: 2px solid var(--line);
  margin-bottom: 24px;
  overflow-x: auto;
}}
.content-tab {{
  padding: 8px 16px;
  font-size: 13px;
  color: var(--muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition);
}}
.content-tab:hover {{
  color: var(--ink);
}}
.content-tab.active {{
  color: var(--teal);
  border-bottom-color: var(--teal);
  font-weight: 600;
}}
.content-tab.empty {{
  opacity: 0.4;
  cursor: default;
}}

/* Document content */
.doc-content {{
  max-width: 800px;
  line-height: 1.8;
}}
.doc-content h1 {{ display: none; }}  /* 标题已在 doc-title 显示 */
.doc-content h2 {{
  font-size: 20px;
  font-weight: 700;
  margin-top: 2em;
  margin-bottom: 0.8em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--line);
  color: var(--ink);
}}
.doc-content h3 {{
  font-size: 17px;
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.6em;
  color: var(--ink);
}}
.doc-content h4 {{
  font-size: 15px;
  font-weight: 600;
  margin-top: 1.2em;
  margin-bottom: 0.4em;
  color: var(--ink);
}}
.doc-content p {{
  margin: 0.8em 0;
}}
.doc-content ul, .doc-content ol {{
  margin: 0.8em 0;
  padding-left: 2em;
}}
.doc-content li {{
  margin: 0.3em 0;
}}
.doc-content strong {{
  font-weight: 600;
  color: var(--ink);
}}

/* Tables */
.doc-content .table-wrap {{
  overflow-x: auto;
  margin: 1em 0;
  border-radius: var(--radius);
  border: 1px solid var(--line);
}}
.doc-content table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  line-height: 1.5;
}}
.doc-content th {{
  background: var(--navy);
  color: white;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
  position: sticky;
  top: 0;
}}
[data-theme="dark"] .doc-content th {{
  background: #374151;
}}
.doc-content td {{
  padding: 9px 12px;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}}
.doc-content tr:nth-child(even) td {{
  background: rgba(0,0,0,.02);
}}
[data-theme="dark"] .doc-content tr:nth-child(even) td {{
  background: rgba(255,255,255,.03);
}}
.doc-content tr:hover td {{
  background: rgba(13,148,136,.04);
}}

/* Blockquotes */
.doc-content blockquote {{
  border-left: 4px solid var(--teal);
  background: rgba(13,148,136,.04);
  padding: 12px 16px;
  margin: 1em 0;
  color: var(--muted);
  font-size: 14px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}}
.doc-content blockquote p {{
  margin: 0.3em 0;
}}

/* Code */
.doc-content code {{
  font-family: var(--font-mono);
  background: rgba(0,0,0,.05);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}}
[data-theme="dark"] .doc-content code {{
  background: rgba(255,255,255,.1);
}}
.doc-content pre {{
  background: #1a202c;
  color: #e2e8f0;
  padding: 16px;
  border-radius: var(--radius);
  overflow-x: auto;
  margin: 1em 0;
  font-size: 13px;
  line-height: 1.5;
}}
.doc-content pre code {{
  background: none;
  padding: 0;
  font-size: inherit;
  color: inherit;
}}

/* Horizontal rules */
.doc-content hr {{
  border: none;
  border-top: 1px solid var(--line);
  margin: 2em 0;
}}

/* Wiki links */
.wiki-link {{
  color: var(--teal);
  cursor: pointer;
  border-bottom: 1px dashed var(--teal);
  transition: all var(--transition);
}}
.wiki-link:hover {{
  color: var(--navy);
  border-bottom-style: solid;
  text-decoration: none;
}}
.wiki-link.broken {{
  color: var(--red);
  border-bottom-color: var(--red);
  opacity: 0.7;
}}

/* Quality badges */
.badge {{
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}}
.badge-green {{ background: rgba(56,161,105,.1); color: var(--green); }}
.badge-amber {{ background: rgba(214,158,46,.1); color: var(--amber); }}
.badge-gray {{ background: rgba(160,174,192,.15); color: var(--muted); }}
.badge-red {{ background: rgba(229,62,62,.1); color: var(--red); }}

/* Checkbox lists */
.doc-content .task-list-item {{
  list-style: none;
  margin-left: -1.5em;
}}
.doc-content .task-list-item input[type="checkbox"] {{
  margin-right: 6px;
}}

/* Meta panel */
.meta-panel {{
  grid-area: meta;
  background: var(--panel);
  border-left: 1px solid var(--line);
  overflow-y: auto;
  max-height: calc(100vh - var(--header-h));
  position: sticky;
  top: var(--header-h);
  padding: 20px;
}}
.meta-section {{
  margin-bottom: 20px;
}}
.meta-section-title {{
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}}
.meta-link {{
  display: block;
  padding: 4px 0;
  font-size: 13px;
  color: var(--teal);
  cursor: pointer;
  transition: color var(--transition);
}}
.meta-link:hover {{
  color: var(--navy);
  text-decoration: none;
}}
.meta-value {{
  font-size: 13px;
  color: var(--ink);
  padding: 2px 0;
}}

/* Search overlay */
.search-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.4);
  z-index: 200;
  padding: 80px 20px 20px;
  backdrop-filter: blur(4px);
}}
.search-overlay.open {{
  display: flex;
  justify-content: center;
  align-items: flex-start;
}}
.search-modal {{
  width: 100%;
  max-width: 640px;
  background: var(--panel);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}
.search-modal-input {{
  padding: 16px 20px;
  border: none;
  border-bottom: 1px solid var(--line);
  font-size: 16px;
  background: transparent;
  color: var(--ink);
  outline: none;
}}
.search-modal-results {{
  overflow-y: auto;
  padding: 8px 0;
}}
.search-result {{
  padding: 10px 20px;
  cursor: pointer;
  transition: background var(--transition);
}}
.search-result:hover, .search-result.selected {{
  background: var(--panel-hover);
}}
.search-result-title {{
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 2px;
}}
.search-result-path {{
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 4px;
}}
.search-result-snippet {{
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}}
.search-result-snippet mark {{
  background: rgba(214,158,46,.3);
  color: var(--ink);
  padding: 0 2px;
  border-radius: 2px;
}}
.search-empty {{
  padding: 40px 20px;
  text-align: center;
  color: var(--muted);
  font-size: 14px;
}}

/* Home / dashboard */
.home-dashboard {{
  max-width: 900px;
}}
.home-title {{
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}}
.home-subtitle {{
  font-size: 15px;
  color: var(--muted);
  margin-bottom: 32px;
  line-height: 1.6;
}}
.module-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}}
.module-card {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 16px;
  cursor: pointer;
  transition: all var(--transition);
}}
.module-card:hover {{
  border-color: var(--teal);
  box-shadow: var(--shadow);
  transform: translateY(-1px);
}}
.module-card-title {{
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--ink);
  display: flex;
  align-items: center;
  gap: 6px;
}}
.module-card-desc {{
  font-size: 12px;
  color: var(--muted);
  line-height: 1.5;
}}
.module-card-count {{
  font-size: 11px;
  color: var(--teal);
  margin-top: 8px;
}}

/* Footer */
.footer {{
  margin-top: 40px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  font-size: 11px;
  color: var(--muted);
}}

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 1280px) {{
  .app {{
    grid-template-columns: var(--sidebar-w) 1fr;
    grid-template-areas:
      "header header"
      "sidebar content";
  }}
  .meta-panel {{
    display: none;
  }}
}}
@media (max-width: 768px) {{
  .app {{
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "content";
  }}
  .sidebar {{
    position: fixed;
    left: calc(-1 * var(--sidebar-w) - 10px);
    top: var(--header-h);
    width: var(--sidebar-w);
    height: calc(100vh - var(--header-h));
    z-index: 150;
    transition: left 0.3s ease;
    box-shadow: var(--shadow-lg);
  }}
  .sidebar.open {{
    left: 0;
  }}
  .sidebar-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.3);
    z-index: 140;
  }}
  .sidebar-overlay.open {{
    display: block;
  }}
  .hamburger {{
    display: flex;
  }}
  .content-area {{
    padding: 16px;
  }}
  .doc-title {{
    font-size: 20px;
  }}
  .module-grid {{
    grid-template-columns: 1fr;
  }}
}}

/* ============================================================
   打印
   ============================================================ */
@media print {{
  .sidebar, .meta-panel, .header, .search-overlay, .sidebar-overlay {{
    display: none !important;
  }}
  .app {{
    grid-template-columns: 1fr;
    grid-template-areas: "content";
  }}
  .content-area {{
    max-height: none;
    padding: 0;
  }}
  .doc-content table {{
    page-break-inside: avoid;
  }}
}}

/* ============================================================
   滚动条
   ============================================================ */
::-webkit-scrollbar {{
  width: 6px;
  height: 6px;
}}
::-webkit-scrollbar-track {{
  background: transparent;
}}
::-webkit-scrollbar-thumb {{
  background: var(--line);
  border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{
  background: var(--muted);
}}

/* ============================================================
   动画
   ============================================================ */
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(8px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in {{
  animation: fadeIn 0.2s ease;
}}
</style>
</head>
<body>

<!-- 数据层 -->
<script id="site-data" type="application/json">___DATA___</script>

<!-- FlexSearch 库 -->
<script>___FLEXSEARCH___</script>

<!-- 应用 -->
<div class="app">
  <!-- Header -->
  <header class="header">
    <button class="btn-icon hamburger" onclick="toggleSidebar()" aria-label="菜单">☰</button>
    <div class="header-logo">
      <span class="icon">📚</span>
      <span>行业信息库</span>
    </div>
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input type="text" id="searchInput" placeholder="搜索行业信息..." autocomplete="off" />
      <span class="search-shortcut">Ctrl+K</span>
    </div>
    <div class="header-actions">
      <button class="btn-icon" onclick="toggleTheme()" id="themeBtn" aria-label="切换主题" title="切换明暗主题">☀️</button>
    </div>
  </header>

  <!-- Sidebar -->
  <aside class="sidebar" id="sidebar"></aside>
  <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

  <!-- Main content -->
  <main class="content-area" id="contentArea"></main>

  <!-- Meta panel -->
  <aside class="meta-panel" id="metaPanel"></aside>
</div>

<!-- Search overlay -->
<div class="search-overlay" id="searchOverlay">
  <div class="search-modal">
    <input type="text" class="search-modal-input" id="searchModalInput" placeholder="输入关键词搜索..." autocomplete="off" />
    <div class="search-modal-results" id="searchResults"></div>
  </div>
</div>

<script>
// ============================================================
// 应用逻辑
// ============================================================

// --- 数据加载 ---
const SITE_DATA = JSON.parse(document.getElementById('site-data').textContent);
const DOCUMENTS = SITE_DATA.documents;
const NAV_TREE = SITE_DATA.navTree;
const SLUG_MAP = SITE_DATA.slugMap;
const BUILD_TIME = SITE_DATA.buildTime;

// 文档查找表
const DOC_BY_ID = {{}};
DOCUMENTS.forEach(d => DOC_BY_ID[d.id] = d);

// 反向链接计算
const BACKLINKS = {{}};
DOCUMENTS.forEach(d => {{
  (d.outgoingLinks || []).forEach(target => {{
    if (!BACKLINKS[target]) BACKLINKS[target] = [];
    BACKLINKS[target].push(d.id);
  }});
}});

// --- 搜索索引 ---
let searchIndex = null;
let searchDocs = [];

function initSearch() {{
  searchIndex = new FlexSearch.Document({{
    document: {{
      id: "id",
      index: ["title", "body", "module", "entity"],
      store: ["title", "path", "module", "entity", "contentType"]
    }},
    encode: function(str) {{
      // 中文双字 n-gram + 英文单词
      const result = [];
      if (!str) return result;
      // 提取中文段
      const chineseSegments = str.match(/[一-鿿]+/g) || [];
      chineseSegments.forEach(seg => {{
        for (let i = 0; i < seg.length - 1; i++) {{
          result.push(seg.substring(i, i + 2));
        }}
        // 也加入单字，支持单字搜索
        for (let i = 0; i < seg.length; i++) {{
          result.push(seg[i]);
        }}
      }});
      // 提取英文单词
      const englishWords = str.match(/[a-zA-Z0-9]+/g) || [];
      englishWords.forEach(w => result.push(w.toLowerCase()));
      return result;
    }},
    tokenize: "forward",
    resolution: 9,
    cache: 100
  }});

  DOCUMENTS.forEach(doc => {{
    if (doc.isIndex && !doc.html) return; // 跳过空 index
    searchIndex.add({{
      id: doc.id,
      title: doc.title,
      body: doc.rawText || "",
      module: doc.module || "",
      entity: doc.entity || "",
      path: doc.path,
      contentType: doc.contentType || ""
    }});
  }});
}}

function doSearch(query) {{
  if (!searchIndex || !query.trim()) return [];
  const results = searchIndex.search(query, {{
    limit: 20,
    enrich: true
  }});

  // 合并不同字段的搜索结果
  const seen = new Set();
  const merged = [];
  results.forEach(fieldResults => {{
    fieldResults.forEach(r => {{
      if (!seen.has(r.id)) {{
        seen.add(r.id);
        merged.push({{
          id: r.id,
          title: r.doc.title,
          path: r.doc.path,
          module: r.doc.module,
          entity: r.doc.entity,
          contentType: r.doc.contentType
        }});
      }}
    }});
  }});
  return merged.slice(0, 20);
}}

// --- 路由 ---
function getCurrentDocId() {{
  const hash = location.hash.slice(1);
  if (hash.startsWith("doc/")) {{
    return hash.slice(4);
  }}
  return null;
}}

function navigateTo(docId) {{
  location.hash = "#doc/" + docId;
}}

function navigateHome() {{
  location.hash = "";
}}

// --- 侧边栏 ---
function renderSidebar() {{
  const sidebar = document.getElementById('sidebar');
  let html = '';

  // 校验与口径
  if (NAV_TREE.governance && NAV_TREE.governance.length > 0) {{
    html += '<div class="sidebar-section">';
    html += '<div class="sidebar-section-title">校验与口径</div>';
    NAV_TREE.governance.forEach(g => {{
      html += `<div class="nav-item" data-doc="${{g.id}}" onclick="navigateTo('${{g.id}}')">
        <span class="icon">📋</span><span class="label">${{escHtml(g.title)}}</span>
      </div>`;
    }});
    html += '</div>';
  }}

  // 模块
  const moduleOrder = Object.keys(NAV_TREE.modules).sort();
  moduleOrder.forEach(modKey => {{
    const mod = NAV_TREE.modules[modKey];
    const entityCount = Object.keys(mod.entities).length;
    const docCount = mod.standaloneDocs.length +
      Object.values(mod.entities).reduce((sum, e) =>
        sum + Object.values(e.contentTypes).reduce((s, docs) => s + docs.length, 0), 0);

    html += '<div class="sidebar-section">';
    html += `<div class="nav-item" data-module="${{escAttr(modKey)}}" onclick="toggleNav(this)">
      <span class="arrow">▶</span>
      <span class="icon">📁</span>
      <span class="label">${{escHtml(modKey)}}${{mod.isSkeleton ? '<span class="skeleton-badge">🚧</span>' : ''}}</span>
      <span class="count">${{docCount}}</span>
    </div>`;
    html += `<div class="nav-children" id="nav-${{escAttr(modKey)}}">`;

    // 模块 index
    if (mod.indexDoc) {{
      html += `<div class="nav-item" data-doc="${{mod.indexDoc}}" onclick="navigateTo('${{mod.indexDoc}}')">
        <span class="icon">🏠</span><span class="label">概览</span>
      </div>`;
    }}

    // 实体
    const entityOrder = Object.keys(mod.entities).sort();
    entityOrder.forEach(entKey => {{
      const ent = mod.entities[entKey];
      const entDocCount = Object.values(ent.contentTypes).reduce((s, docs) => s + docs.length, 0);

      html += `<div class="nav-item" data-entity="${{escAttr(entKey)}}" onclick="toggleNav(this)">
        <span class="arrow">▶</span>
        <span class="icon">🏢</span>
        <span class="label">${{escHtml(entKey)}}</span>
        <span class="count">${{entDocCount}}</span>
      </div>`;
      html += `<div class="nav-children">`;

      // 内容类型
      const ctOrder = ["财报数据", "公开新闻", "研报摘要", "结构化摘要", "业务洞察"];
      Object.keys(ent.contentTypes).sort((a, b) => {{
        const ai = ctOrder.indexOf(a); const bi = ctOrder.indexOf(b);
        return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
      }}).forEach(ct => {{
        ent.contentTypes[ct].forEach(doc => {{
          html += `<div class="nav-item" data-doc="${{doc.id}}" onclick="navigateTo('${{doc.id}}')">
            <span class="icon">${{ctIcon(ct)}}</span><span class="label">${{escHtml(doc.title)}}</span>
          </div>`;
        }});
      }});

      html += '</div>';
    }});

    // 独立文档
    mod.standaloneDocs.forEach(doc => {{
      html += `<div class="nav-item" data-doc="${{doc.id}}" onclick="navigateTo('${{doc.id}}')">
        <span class="icon">${{ctIcon(doc.contentType)}}</span><span class="label">${{escHtml(doc.title)}}</span>
      </div>`;
    }});

    html += '</div></div>';
  }});

  sidebar.innerHTML = html;
}}

function toggleNav(el) {{
  const children = el.nextElementSibling;
  if (!children || !children.classList.contains('nav-children')) return;
  const arrow = el.querySelector('.arrow');
  if (children.classList.contains('open')) {{
    children.classList.remove('open');
    if (arrow) arrow.classList.remove('open');
  }} else {{
    children.classList.add('open');
    if (arrow) arrow.classList.add('open');
  }}
}}

function highlightSidebar(docId) {{
  // 清除所有 active
  document.querySelectorAll('.sidebar .nav-item.active').forEach(el => el.classList.remove('active'));
  // 设置新的 active
  const target = document.querySelector(`.sidebar .nav-item[data-doc="${{docId}}"]`);
  if (target) {{
    target.classList.add('active');
    // 展开父级
    let parent = target.parentElement;
    while (parent && parent !== document.getElementById('sidebar')) {{
      if (parent.classList.contains('nav-children')) {{
        parent.classList.add('open');
        const prevArrow = parent.previousElementSibling?.querySelector('.arrow');
        if (prevArrow) prevArrow.classList.add('open');
      }}
      parent = parent.parentElement;
    }}
    // 滚动到可见
    target.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
  }}
}}

// --- 内容渲染 ---
function renderDoc(docId) {{
  const doc = DOC_BY_ID[docId];
  if (!doc) {{
    renderHome();
    return;
  }}

  const area = document.getElementById('contentArea');
  const isEntityView = doc.entity && doc.contentType;

  // 找同实体的其他文档
  let siblingDocs = [];
  if (doc.entity && doc.module) {{
    siblingDocs = DOCUMENTS.filter(d =>
      d.entity === doc.entity && d.module === doc.module && !d.isIndex
    );
  }}

  // 构建内容类型 tabs
  let tabsHtml = '';
  if (isEntityView && siblingDocs.length > 1) {{
    const ctOrder = ["财报数据", "公开新闻", "研报摘要", "结构化摘要", "业务洞察"];
    const seenCt = new Set();
    const ctDocs = {{}};
    siblingDocs.forEach(d => {{
      const ct = d.contentType || "其他";
      if (!ctDocs[ct]) ctDocs[ct] = [];
      ctDocs[ct].push(d);
      seenCt.add(ct);
    }});

    tabsHtml = '<div class="content-tabs">';
    ctOrder.concat([...seenCt].filter(ct => !ctOrder.includes(ct))).forEach(ct => {{
      const docs = ctDocs[ct];
      if (!docs) return;
      const isActive = ct === doc.contentType;
      const docIdForTab = docs[0]?.id;
      tabsHtml += `<button class="content-tab${{isActive ? ' active' : ''}}" onclick="navigateTo('${{docIdForTab}}')">${{ct}}</button>`;
    }});
    tabsHtml += '</div>';
  }}

  // 面包屑
  let breadcrumbParts = ['<a href="#" onclick="navigateHome();return false">行业信息库</a>'];
  if (doc.module) {{
    // 找模块 index
    const modIndex = DOCUMENTS.find(d => d.module === doc.module && d.isIndex);
    breadcrumbParts.push(`<span class="sep">›</span> <a href="#doc/${{modIndex?.id || ''}}" onclick="navigateTo('${{modIndex?.id || ''}}');return false">${{escHtml(doc.module)}}</a>`);
  }}
  if (doc.entity && doc.entity !== doc.module) {{
    breadcrumbParts.push(`<span class="sep">›</span> ${escHtml(doc.entity)}`);
  }}
  if (doc.contentType && doc.contentType !== "治理/索引") {{
    breadcrumbParts.push(`<span class="sep">›</span> ${escHtml(doc.contentType)}`);
  }}

  // 文档元信息标签
  let metaTags = '';
  if (doc.contentType && doc.contentType !== "其他") {{
    const tagClass = doc.contentType === "业务洞察" ? "teal" : doc.contentType === "财报数据" ? "navy" : "";
    metaTags += `<span class="tag ${{tagClass}}">${{escHtml(doc.contentType)}}</span>`;
  }}
  if (doc.isSkeleton) metaTags += '<span class="tag amber">🚧 建设中</span>';
  if (doc.lastUpdated) metaTags += `<span style="color:var(--muted)">更新于 ${{doc.lastUpdated}}</span>`;

  area.innerHTML = `
    <div class="fade-in">
      <div class="breadcrumb">${{breadcrumbParts.join('')}}</div>
      <div class="doc-header">
        <h1 class="doc-title">${{escHtml(doc.title)}}</h1>
        <div class="doc-meta">${{metaTags}}</div>
      </div>
      ${{tabsHtml}}
      <div class="doc-content">${{doc.html}}</div>
      <div class="footer">
        构建时间：${{BUILD_TIME}} · 文档数：${{DOCUMENTS.length}}
      </div>
    </div>
  `;

  // 处理文档内的 wiki 链接点击
  area.querySelectorAll('.wiki-link').forEach(link => {{
    link.addEventListener('click', e => {{
      e.preventDefault();
      const slug = link.getAttribute('data-slug');
      if (slug) navigateTo(slug);
    }});
  }});

  // 更新侧边栏高亮
  highlightSidebar(docId);

  // 更新 meta panel
  renderMetaPanel(docId);

  // 滚动到顶部
  area.scrollTop = 0;
}}

function renderHome() {{
  const area = document.getElementById('contentArea');
  // 用根 _index.md 的内容
  const rootIndex = NAV_TREE.homeDoc ? DOC_BY_ID[NAV_TREE.homeDoc] : DOCUMENTS.find(d => d.path === "_index.md");

  let html = '<div class="home-dashboard fade-in">';
  html += '<h1 class="home-title">📚 行业信息库</h1>';
  html += '<p class="home-subtitle">即时零售行业全景信息库——竞对动态、合作伙伴财报、行业机构报告、券商研报。<br>所有信息要求溯源链接，每条关键信息标注来源和可应用性思考。</p>';

  // 模块卡片
  html += '<div class="module-grid">';
  const moduleOrder = Object.keys(NAV_TREE.modules).sort();
  const moduleIcons = {{
    "01-即时零售平台": "🛒",
    "02-连锁药店": "💊",
    "03-即时零售相关药企": "🔬",
    "04-券商研报": "📊",
    "05-行业机构": "🏛️",
    "06-其他行业报告": "📑",
    "07-京东健康与秒送基准库": "🏠",
    "08-政策与监管库": "⚖️",
    "09-用户与场景库": "👤",
    "10-供给与履约库": "🚚",
    "11-区域市场库": "🗺️",
  }};
  const moduleDescs = {{
    "01-即时零售平台": "阿里/淘宝闪购 + 美团/美团买药",
    "02-连锁药店": "六大上市连锁药店动态与财报",
    "03-即时零售相关药企": "OTC/消费健康 + DTP特药药企",
    "04-券商研报": "即时零售/医药零售/O2O研报",
    "05-行业机构": "中康科技/西普会/米未研究院",
    "06-其他行业报告": "第三方行业报告与市场份额口径",
    "07-京东健康与秒送基准库": "京东健康/秒送经营口径（建设中）",
    "08-政策与监管库": "处方药/医保/平台监管/药品流通",
    "09-用户与场景库": "用户需求场景维度（建设中）",
    "10-供给与履约库": "供给与履约能力维度（建设中）",
    "11-区域市场库": "区域市场维度（建设中）",
  }};

  moduleOrder.forEach(modKey => {{
    const mod = NAV_TREE.modules[modKey];
    const docCount = mod.standaloneDocs.length +
      Object.values(mod.entities).reduce((sum, e) =>
        sum + Object.values(e.contentTypes).reduce((s, docs) => s + docs.length, 0), 0);
    const icon = moduleIcons[modKey] || "📁";
    const desc = moduleDescs[modKey] || "";

    html += `<div class="module-card" onclick="navigateTo('${{mod.indexDoc || ''}}')">
      <div class="module-card-title">${{icon}} ${{escHtml(modKey)}}${{mod.isSkeleton ? ' 🚧' : ''}}</div>
      <div class="module-card-desc">${{escHtml(desc)}}</div>
      <div class="module-card-count">${{docCount}} 篇文档</div>
    </div>`;
  }});
  html += '</div>';

  // 如果有 _index.md 的内容，也展示
  if (rootIndex && rootIndex.html) {{
    html += '<div class="doc-content">' + rootIndex.html + '</div>';
  }}

  html += `<div class="footer">构建时间：${{BUILD_TIME}} · 文档数：${{DOCUMENTS.length}}</div>`;
  html += '</div>';

  area.innerHTML = html;
  highlightSidebar('');
  renderMetaPanel(null);
}}

// --- Meta panel ---
function renderMetaPanel(docId) {{
  const panel = document.getElementById('metaPanel');
  if (!docId) {{
    panel.innerHTML = '<div class="meta-section"><div class="meta-section-title">快速导航</div><div class="meta-value">点击左侧导航或搜索关键词开始浏览</div></div>';
    return;
  }}

  const doc = DOC_BY_ID[docId];
  if (!doc) return;

  let html = '';

  // 数据质量
  if (doc.contentType) {{
    html += '<div class="meta-section">';
    html += '<div class="meta-section-title">内容类型</div>';
    html += `<div class="meta-value"><span class="badge badge-green">${{escHtml(doc.contentType)}}</span></div>`;
    html += '</div>';
  }}

  // 更新时间
  if (doc.lastUpdated) {{
    html += '<div class="meta-section">';
    html += '<div class="meta-section-title">最后更新</div>';
    html += `<div class="meta-value">${{doc.lastUpdated}}</div>`;
    html += '</div>';
  }}

  // 摘要
  if (doc.summary) {{
    html += '<div class="meta-section">';
    html += '<div class="meta-section-title">摘要</div>';
    html += `<div class="meta-value">${{escHtml(doc.summary)}}</div>`;
    html += '</div>';
  }}

  // 反向链接
  const backlinks = BACKLINKS[docId] || [];
  if (backlinks.length > 0) {{
    html += '<div class="meta-section">';
    html += '<div class="meta-section-title">被引用 (' + backlinks.length + ')</div>';
    backlinks.forEach(blId => {{
      const blDoc = DOC_BY_ID[blId];
      if (blDoc) {{
        html += `<a class="meta-link" onclick="navigateTo('${{blId}}')">${{escHtml(blDoc.title)}}</a>`;
      }}
    }});
    html += '</div>';
  }}

  // 出站链接
  if (doc.outgoingLinks && doc.outgoingLinks.length > 0) {{
    html += '<div class="meta-section">';
    html += '<div class="meta-section-title">引用了 (' + doc.outgoingLinks.length + ')</div>';
    doc.outgoingLinks.forEach(outId => {{
      const outDoc = DOC_BY_ID[outId];
      if (outDoc) {{
        html += `<a class="meta-link" onclick="navigateTo('${{outId}}')">${{escHtml(outDoc.title)}}</a>`;
      }}
    }});
    html += '</div>';
  }}

  // 同模块文档
  if (doc.module) {{
    const sameModule = DOCUMENTS.filter(d => d.module === doc.module && d.id !== docId && !d.isIndex);
    if (sameModule.length > 0) {{
      html += '<div class="meta-section">';
      html += '<div class="meta-section-title">同模块文档</div>';
      sameModule.slice(0, 10).forEach(d => {{
        html += `<a class="meta-link" onclick="navigateTo('${{d.id}}')">${{escHtml(d.title)}}</a>`;
      }});
      if (sameModule.length > 10) {{
        html += `<div class="meta-value">...还有 ${{sameModule.length - 10}} 篇</div>`;
      }}
      html += '</div>';
    }}
  }}

  panel.innerHTML = html;
}}

// --- 搜索 UI ---
const searchInput = document.getElementById('searchInput');
const searchOverlay = document.getElementById('searchOverlay');
const searchModalInput = document.getElementById('searchModalInput');
const searchResultsEl = document.getElementById('searchResults');
let searchSelectedIndex = -1;

searchInput.addEventListener('focus', () => openSearch());
searchInput.addEventListener('input', e => {{
  searchModalInput.value = e.target.value;
  performSearch(e.target.value);
}});

searchModalInput.addEventListener('input', e => {{
  searchInput.value = e.target.value;
  performSearch(e.target.value);
}});

searchOverlay.addEventListener('click', e => {{
  if (e.target === searchOverlay) closeSearch();
}});

document.addEventListener('keydown', e => {{
  // Ctrl+K 打开搜索
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
    e.preventDefault();
    openSearch();
  }}
  // Escape 关闭搜索
  if (e.key === 'Escape') {{
    closeSearch();
  }}
  // 搜索结果键盘导航
  if (searchOverlay.classList.contains('open')) {{
    const items = searchResultsEl.querySelectorAll('.search-result');
    if (e.key === 'ArrowDown') {{
      e.preventDefault();
      searchSelectedIndex = Math.min(searchSelectedIndex + 1, items.length - 1);
      updateSearchSelection(items);
    }} else if (e.key === 'ArrowUp') {{
      e.preventDefault();
      searchSelectedIndex = Math.max(searchSelectedIndex - 1, 0);
      updateSearchSelection(items);
    }} else if (e.key === 'Enter' && searchSelectedIndex >= 0 && items[searchSelectedIndex]) {{
      const docId = items[searchSelectedIndex].getAttribute('data-doc');
      if (docId) {{
        navigateTo(docId);
        closeSearch();
      }}
    }}
  }}
}});

function openSearch() {{
  searchOverlay.classList.add('open');
  searchModalInput.value = searchInput.value;
  searchModalInput.focus();
  searchSelectedIndex = -1;
}}

function closeSearch() {{
  searchOverlay.classList.remove('open');
  searchInput.blur();
}}

function performSearch(query) {{
  if (!query.trim()) {{
    searchResultsEl.innerHTML = '<div class="search-empty">输入关键词开始搜索</div>';
    return;
  }}

  const results = doSearch(query);
  searchSelectedIndex = -1;

  if (results.length === 0) {{
    searchResultsEl.innerHTML = `<div class="search-empty">未找到与"${{escHtml(query)}}"相关的内容</div>`;
    return;
  }}

  let html = '';
  results.forEach((r, i) => {{
    // 生成路径显示
    let pathParts = [];
    if (r.module) pathParts.push(r.module);
    if (r.entity) pathParts.push(r.entity);
    if (r.contentType) pathParts.push(r.contentType);
    const pathStr = pathParts.join(' › ');

    // 生成 snippet
    const doc = DOC_BY_ID[r.id];
    let snippet = '';
    if (doc && doc.rawText) {{
      const lowerText = doc.rawText.toLowerCase();
      const lowerQuery = query.toLowerCase();
      const idx = lowerText.indexOf(lowerQuery);
      if (idx >= 0) {{
        const start = Math.max(0, idx - 40);
        const end = Math.min(doc.rawText.length, idx + query.length + 60);
        snippet = (start > 0 ? '...' : '') +
          doc.rawText.substring(start, end) +
          (end < doc.rawText.length ? '...' : '');
        // 高亮
        const regex = new RegExp(escRegex(query), 'gi');
        snippet = escHtml(snippet).replace(regex, '<mark>$&</mark>');
      }} else {{
        snippet = escHtml(doc.rawText.substring(0, 120)) + '...';
      }}
    }}

    html += `<div class="search-result" data-doc="${{r.id}}" onclick="navigateTo('${{r.id}}');closeSearch()">
      <div class="search-result-title">${{escHtml(r.title)}}</div>
      <div class="search-result-path">${{escHtml(pathStr)}}</div>
      ${{snippet ? `<div class="search-result-snippet">${{snippet}}</div>` : ''}}
    </div>`;
  }});

  searchResultsEl.innerHTML = html;
}}

function updateSearchSelection(items) {{
  items.forEach((item, i) => {{
    item.classList.toggle('selected', i === searchSelectedIndex);
  }});
  if (items[searchSelectedIndex]) {{
    items[searchSelectedIndex].scrollIntoView({{ block: 'nearest' }});
  }}
}}

// --- 主题切换 ---
function toggleTheme() {{
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  document.getElementById('themeBtn').textContent = next === 'dark' ? '🌙' : '☀️';
  localStorage.setItem('theme', next);
}}

// 初始化主题
(function() {{
  const saved = localStorage.getItem('theme');
  if (saved) {{
    document.documentElement.setAttribute('data-theme', saved);
    document.getElementById('themeBtn').textContent = saved === 'dark' ? '🌙' : '☀️';
  }} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
    document.documentElement.setAttribute('data-theme', 'dark');
    document.getElementById('themeBtn').textContent = '🌙';
  }}
}})();

// --- 移动端侧边栏 ---
function toggleSidebar() {{
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
}}

// --- 工具函数 ---
function escHtml(str) {{
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}
function escAttr(str) {{
  return escHtml(str).replace(/'/g, '&#39;');
}}
function escRegex(str) {{
  return str.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
}}
function ctIcon(ct) {{
  const icons = {{
    "财报数据": "📊", "公开新闻": "📰", "研报摘要": "📑",
    "结构化摘要": "📋", "业务洞察": "💡", "治理/索引": "📋",
    "其他": "📄"
  }};
  return icons[ct] || "📄";
}}

// --- Hash 路由 ---
window.addEventListener('hashchange', handleRoute);
function handleRoute() {{
  const docId = getCurrentDocId();
  if (docId && DOC_BY_ID[docId]) {{
    renderDoc(docId);
  }} else {{
    renderHome();
  }}
}}

// --- 初始化 ---
renderSidebar();
initSearch();
handleRoute();
</script>
</body>
</html>'''


# ============================================================
# FlexSearch 库代码
# ============================================================
def get_flexsearch_code():
    """获取 FlexSearch 库的 JS 代码（从 CDN 下载并嵌入）"""
    import urllib.request
    url = "https://cdn.jsdelivr.net/npm/flexsearch/dist/flexsearch.bundle.js"
    try:
        print("Downloading FlexSearch library...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.read().decode('utf-8')
        print(f"FlexSearch downloaded ({len(code)} bytes)")
        return code
    except Exception as e:
        print(f"WARN: cannot download FlexSearch: {e}")
        print("Using fallback search implementation")
        # 返回一个极简的搜索实现
        return '''
// FlexSearch fallback - simplified search implementation
var FlexSearch = {
  Document: function(opts) {
    this.docs = {};
    this.opts = opts || {};
    this.encoder = opts.encode || function(s) { return (s||"").toLowerCase().split(/\\s+/); };
  }
};
FlexSearch.Document.prototype.add = function(doc) {
  this.docs[doc.id] = doc;
};
FlexSearch.Document.prototype.search = function(query, opts) {
  var q = query.toLowerCase();
  var results = [];
  var limit = (opts && opts.limit) || 20;
  for (var id in this.docs) {
    var doc = this.docs[id];
    var title = (doc.title || "").toLowerCase();
    var body = (doc.body || "").toLowerCase();
    if (title.indexOf(q) >= 0 || body.indexOf(q) >= 0) {
      results.push([{id: id, doc: doc}]);
    }
    if (results.length >= limit) break;
  }
  return results;
};
'''


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("Building industry info HTML site")
    print("=" * 60)

    # 扫描和转换
    documents, slug_map = scan_and_convert()

    # 构建导航树
    nav_tree = build_nav_tree(documents)

    # 获取 FlexSearch 代码
    flexsearch_code = get_flexsearch_code()

    # 准备数据 JSON
    site_data = {
        "documents": documents,
        "navTree": nav_tree,
        "slugMap": {k: v for k, v in slug_map.items()},
        "buildTime": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    data_json = json.dumps(site_data, ensure_ascii=False, separators=(',', ':'))

    # 生成 HTML
    # 步骤：先还原模板中的双花括号，再插入数据
    # 这样 JSON 数据和 FlexSearch 代码中的花括号不会被影响
    html = HTML_TEMPLATE.replace("{{", "{").replace("}}", "}")
    html = html.replace("___DATA___", data_json)
    html = html.replace("___FLEXSEARCH___", flexsearch_code)

    # 写入文件
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    file_size = OUTPUT_FILE.stat().st_size
    print(f"\n[OK] output: {OUTPUT_FILE}")
    print(f"   file size: {file_size / 1024:.1f} KB ({file_size / 1024 / 1024:.2f} MB)")
    print(f"   doc count: {len(documents)}")
    print(f"   build time: {site_data['buildTime']}")


if __name__ == "__main__":
    main()
