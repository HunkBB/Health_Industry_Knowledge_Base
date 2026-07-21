from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
ref = root / 'assets/doc_cards_web/industry_20260617/doc-82874537ac28.jpg'
out = root / 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
im = Image.open(ref).convert('RGBA')
W,H = im.size
patch = Image.new('RGBA', (W,H), (0,0,0,0))
pd = ImageDraw.Draw(patch)
# Cover the full original title area on the tilted book using a large paper-colored polygon.
pd.polygon([(525,230),(1210,292),(1190,438),(510,374)], fill=(247,247,244,255))
# Add back subtle book-paper tone so it does not look like a floating label.
pd.polygon([(525,230),(1210,292),(1190,438),(510,374)], outline=(245,245,242,255))
im = Image.alpha_composite(im, patch).convert('RGB')
draw = ImageDraw.Draw(im)
lines = ['商务部研究院', '即时零售行业发展报告摘要']
font1 = ImageFont.truetype(str(font_path), 42)
font2 = ImageFont.truetype(str(font_path), 36)
while draw.textbbox((0,0), lines[1], font=font2)[2] > 610 and font2.size > 30:
    font2 = ImageFont.truetype(str(font_path), font2.size - 1)
x, y = 560, 262
# draw shadow then text, matching the book cover's flat printed title style
for dx,dy,fill in [(2,2,(225,225,221)),(0,0,(30,36,40))]:
    draw.text((x+dx,y+dy), lines[0], font=font1, fill=fill)
for dx,dy,fill in [(2,2,(225,225,221)),(0,0,(30,36,40))]:
    draw.text((x+dx,y+54+dy), lines[1], font=font2, fill=fill)
small = ImageFont.truetype(str(font_path), 22)
draw.text((562, y+102), '行业报告 · 渠道结构 · 近场履约', font=small, fill=(128,124,118))
im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
mp_path = root / 'assets/doc_cards_web/doc_image_web_map.json'
mp = json.loads(mp_path.read_text(encoding='utf-8-sig'))
mp['doc-a0175105fac2'] = 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
mp_path.write_text(json.dumps(mp, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(out)
