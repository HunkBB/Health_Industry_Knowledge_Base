from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
ref = root / 'assets/doc_cards_web/industry_20260617/doc-82874537ac28.jpg'
out = root / 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
backup = root / 'assets/doc_cards_web/backup_before_commerce_report_retemplate_20260617'
backup.mkdir(parents=True, exist_ok=True)
if out.exists():
    bak = backup / out.name
    if not bak.exists(): bak.write_bytes(out.read_bytes())
im = Image.open(ref).convert('RGB')
W,H = im.size
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
# Patch only the text area on the book, preserving the original background/book/pen/box frame.
patch = Image.new('RGBA', (W,H), (0,0,0,0))
pd = ImageDraw.Draw(patch)
# Soft white cover patch in the same region where original title sits.
pd.polygon([(560,255),(1098,305),(1090,405),(552,355)], fill=(247,247,244,248))
# Restore a very subtle paper grain / shadow edge.
pd.line([(560,355),(1090,405)], fill=(235,234,230,95), width=2)
im = Image.alpha_composite(im.convert('RGBA'), patch).convert('RGB')
draw = ImageDraw.Draw(im)
title_lines = ['商务部研究院', '即时零售行业发展报告摘要']
# Fit into the same book-title area; keep font scale close to other industry images.
font1 = ImageFont.truetype(str(font_path), 44)
font2 = ImageFont.truetype(str(font_path), 39)
# If second line too long, shrink slightly.
while draw.textbbox((0,0), title_lines[1], font=font2)[2] > 520 and font2.size > 32:
    font2 = ImageFont.truetype(str(font_path), font2.size - 1)
# positions follow the original perspective but remain readable.
x0, y0 = 585, 275
for dx,dy,line,font in [(2,2,title_lines[0],font1),(0,0,title_lines[0],font1)]:
    draw.text((x0+dx, y0+dy), line, font=font, fill=(226,226,222) if dx else (28,34,38))
y2 = y0 + 58
for dx,dy,line,font in [(2,2,title_lines[1],font2),(0,0,title_lines[1],font2)]:
    draw.text((x0+dx, y2+dy), line, font=font, fill=(226,226,222) if dx else (28,34,38))
# Add small red network cue matching existing lower-right red line motif.
small = ImageFont.truetype(str(font_path), 22)
draw.text((590, y2+54), '行业报告 · 渠道结构 · 近场履约', font=small, fill=(128,124,118))
im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
# Ensure map uses industry folder path.
mp_path = root / 'assets/doc_cards_web/doc_image_web_map.json'
mp = json.loads(mp_path.read_text(encoding='utf-8-sig'))
mp['doc-a0175105fac2'] = 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
mp_path.write_text(json.dumps(mp, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(out)
