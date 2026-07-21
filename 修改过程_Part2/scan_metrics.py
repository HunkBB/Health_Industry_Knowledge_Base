from pathlib import Path
for p in Path('.').rglob('*.md'):
    if any(part.startswith('backup-') for part in p.parts):
        continue
    text=p.read_text(encoding='utf-8', errors='ignore')
    if any(k in p.name for k in ['财报','年度报告','业绩']) or '财报数据' in str(p):
        if any(name in text for name in ['益丰','老百姓','大参林','一心堂','健之佳','漱玉平民','华润三九','汤臣倍健','云南白药','信达生物','再鼎医药','百济神州']):
            print('---', p)
            for line in text.splitlines()[:60]:
                if any(ch.isdigit() for ch in line) and any(key in line for key in ['收入','营收','净利润','门店','O2O','2025','2026','产品']):
                    print(line[:240])
