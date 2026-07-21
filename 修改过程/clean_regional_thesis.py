from pathlib import Path
repls = {
    '核心判断是：北京样本只用于分析北京“互联网+”医保服务的地方执行方式。核心判断是：': '核心判断是：',
    '核心判断是：上海样本只用于分析上海零售药店互联网购药医保在线支付试点。核心判断是：': '核心判断是：',
    '核心判断是：广东样本只用于分析广东线上医保购药的本地入口和操作路径。核心判断是：': '核心判断是：',
    '核心判断是：浙江样本只用于分析浙江“浙里云药房”互联网医保结算实施路径。核心判断是：': '核心判断是：',
}
files = [
Path(r'07-政策与监管库/补充资料/北京医保药店与线上医保政策样本.md'),
Path(r'07-政策与监管库/补充资料/上海医保药店与线上医保政策样本.md'),
Path(r'07-政策与监管库/补充资料/广东医保药店与线上医保政策样本.md'),
Path(r'07-政策与监管库/补充资料/浙江医保药店与线上医保政策样本.md'),
]
for p in files:
    text = p.read_text(encoding='utf-8')
    for old, new in repls.items():
        text = text.replace(old, new)
    p.write_text(text, encoding='utf-8')
print('cleaned repeated thesis')
