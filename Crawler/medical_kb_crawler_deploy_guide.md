> 引用级别：✅可正式引用
> 资料基础：官方公告、公司财报、交易所/港交所披露、公司官网新闻稿、监管披露或已核验权威公开来源。


## 一句话定位



本文定位为医疗知识库爬虫与部署说明资料，核心关注medical_kb_crawler_deploy_guide的配置、运行、输出字段和部署使用方式。

## 1. 推荐目录结构

建议把爬虫项目放在现有部署项目同级目录：（仅推测）

```text
workspace/
  industry-info-site-deploy/
    public/
      index.html
    scripts/
      sync-site.ps1
    server.js
    package.json
    README.md
  medical_kb_crawler/
    configs/
      sites.example.yaml
    data/
      output/
    src/
    pyproject.toml
    requirements.txt
```

如果你希望爬虫结果直接进入网站静态目录，也可以把输出目录设置为：（仅推测）

```text
industry-info-site-deploy/public/data
```

## 2. 安装 Python 环境

进入爬虫目录：

```powershell
cd medical_kb_crawler
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

如果你只是本地开发并运行测试，再安装：（仅推测）

```powershell
pip install -r requirements-dev.txt
```

## 3. 配置真实网站爬取规则

复制示例配置：

```powershell
copy configs\sites.example.yaml configs\sites.yaml
```

编辑 `configs/sites.yaml`，每个网站一段配置。例如：

```yaml
sites:
  - name: 某医疗资讯网站
    enabled: true
    base_url: https://example.com
    list_urls:
      - https://example.com/news
    pagination:
      enabled: true
      max_pages: 5
      url_template: https://example.com/news?page={page}
      start_page: 1
    request:
      timeout: 15
      delay_seconds: 1
      headers:
        User-Agent: Mozilla/5.0 MedicalKBCrawler/0.1
    selectors:
      item: article
      title: h2 a::text
      link: h2 a::attr(href)
      published_at: time::attr(datetime)
      summary: .summary::text
      tags: .tag::text
    defaults:
      tags:
        - 医疗
        - 行业知识
```

选择器说明：

- `item`：列表页中每条文章的外层元素。
- `title`：标题选择器，常见写法 `h2 a::text`。
- `link`：链接选择器，常见写法 `h2 a::attr(href)`。
- `published_at`：发布时间选择器。
- `summary`：摘要选择器。
- `tags`：标签选择器，可匹配多个标签。

## 4. 手动运行爬虫

默认输出到爬虫项目自己的 `data/output`：

```powershell
medical-kb-crawler --config configs/sites.yaml --output-dir data/output --limit 100 --verbose
```

如果要输出到现有网站静态目录，先在网站项目创建目录：（仅推测）

```powershell
mkdir ..\industry-info-site-deploy\public\data
```

然后运行：

```powershell
medical-kb-crawler --config configs/sites.yaml --output-dir ..\industry-info-site-deploy\public\data --limit 100 --verbose
```

输出文件包括：

```text
medical_articles_YYYYMMDD_HHMMSS.csv
medical_articles_YYYYMMDD_HHMMSS.xlsx
```

字段固定为：

```text
来源, 标题, 链接, 发布时间, 摘要, 标签
```

## 5. 和你现有网站部署流程结合

你当前 README 中的流程是：

```text
维护源目录 -> 运行 scripts/sync-site.cmd -> 部署 industry-info-site-deploy
```

推荐加入爬虫后调整为：

```text
运行爬虫生成 CSV / Excel -> 原行业信息库读取 CSV 生成 HTML -> 运行 scripts/sync-site.cmd -> 部署 industry-info-site-deploy
```

### 方案 A：只把 CSV / Excel 放到网站 public/data

适合先快速上线下载文件，不改现有页面生成逻辑。

操作：

```powershell
cd medical_kb_crawler
.venv\Scripts\activate
medical-kb-crawler --config configs/sites.yaml --output-dir ..\industry-info-site-deploy\public\data --limit 100 --verbose
```

然后部署平台部署 `industry-info-site-deploy` 即可。

### 方案 B：让原行业信息库生成 HTML 时读取 CSV

适合把爬虫结果展示到 `public/index.html` 页面里。

你需要在原目录：

```text
06-参考与研究/行业信息库
```

的 HTML 生成逻辑里读取爬虫生成的 CSV，比如：

```text
industry-info-site-deploy/public/data/latest.csv
```

建议后续把爬虫导出的最新 CSV 固定复制为 `latest.csv`，这样前端或生成脚本不用关心时间戳文件名。（仅推测）

## 6. 建议新增同步脚本

可以在 `industry-info-site-deploy/scripts` 下增加一个脚本，例如 `run-crawler.ps1`：

```powershell
$CrawlerDir = Join-Path $PSScriptRoot "..\..\medical_kb_crawler"
$OutputDir = Join-Path $PSScriptRoot "..\public\data"

Set-Location $CrawlerDir
. .\.venv\Scripts\Activate.ps1
medical-kb-crawler --config configs\sites.yaml --output-dir $OutputDir --limit 100 --verbose
```

日常更新时执行：

```powershell
scripts\run-crawler.ps1
scripts\sync-site.cmd
npm start
```

## 7. 部署平台注意事项

如果部署平台只支持 Node 静态站：（仅推测）

- Python 爬虫不要放在部署平台运行。
- 在本地或定时任务服务器运行爬虫。
- 把生成后的 CSV / Excel / HTML 同步到 `industry-info-site-deploy/public` 后再部署。

如果部署平台支持 Python 定时任务：（仅推测）

- 上传 `medical_kb_crawler`。
- 安装 `requirements.txt`。
- 定时执行 `medical-kb-crawler --config configs/sites.yaml --output-dir <网站public/data>`。

## 8. 常见问题

### 页面没有抓到数据

优先检查：

1. `selectors.item` 是否能选中每条文章。
2. `title` 和 `link` 是否在 `item` 内部。
3. 网站是否需要 JavaScript 渲染；当前版本适合静态 HTML 页面。
4. 网站是否有反爬限制，必要时调大 `delay_seconds`。

### Excel 正常，CSV 中文乱码

当前 CSV 使用 `utf-8-sig`，Excel 打开通常不会乱码。

### 想抓详情页正文

当前版本按列表页采集摘要。建议持续跟踪以在 `pipeline.py` 中对每条链接做详情页二次请求，并在 `Article` 模型里增加 `content` 字段。（仅推测）
