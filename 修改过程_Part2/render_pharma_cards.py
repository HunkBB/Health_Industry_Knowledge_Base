from pathlib import Path
import json, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
template_path = root / 'output/imagegen/pharma-blue-yunnan-baiyao-25-26-center-pills.png'
targets_path = root / 'tmp/pharma_card_targets.json'
map_path = root / 'assets/doc_cards_web/doc_image_web_map.json'
backup_dir = root / 'assets/doc_cards_web/backup_before_pharma_template_20260617_1438'
backup_dir.mkdir(parents=True, exist_ok=True)

image_map = json.loads(map_path.read_text(encoding='utf-8-sig'))
targets = json.loads(targets_path.read_text(encoding='utf-8'))
template = Image.open(template_path).convert('RGB')

font_candidates = [
    Path(r'C:\Windows\Fonts\msyhbd.ttc'),
    Path(r'C:\Windows\Fonts\msyh.ttc'),
    Path(r'C:\Windows\Fonts\simhei.ttf'),
]
font_path = next((p for p in font_candidates if p.exists()), None)
if not font_path:
    raise SystemExit('No Chinese font found')

def short_title(title: str) -> str:
    t = title.replace(' · ', ' ').replace('（2025-2026）', '').replace('(2025-2026)', '')
    t = t.replace('2025-2026', '25-26年').replace('2025—2026', '25-26年')
    t = t.replace('财报与渠道机会摘要', '财报与渠道机会')
    t = t.replace('_', ' ')
    return re.sub(r'\s+', ' ', t).strip()

def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int):
    for size in range(92, 40, -2):
        font = ImageFont.truetype(str(font_path), size)
        bbox = draw.textbbox((0,0), text, font=font)
        if bbox[2]-bbox[0] <= max_width and bbox[3]-bbox[1] <= max_height:
            return font
    return ImageFont.truetype(str(font_path), 40)

def draw_title_card(base: Image.Image, title: str) -> Image.Image:
    im = base.copy()
    draw = ImageDraw.Draw(im)
    # cover original title card area with a rounded pharma-blue title card
    x0, y0, x1, y1 = 158, 58, 1378, 231
    # soft shadow / glow
    shadow = Image.new('RGBA', im.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0-4, y0+4, x1+4, y1+8), radius=28, fill=(0, 45, 120, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    im = Image.alpha_composite(im.convert('RGBA'), shadow)
    card = Image.new('RGBA', im.size, (0,0,0,0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((x0, y0, x1, y1), radius=27, fill=(0, 49, 137, 255), outline=(190, 236, 255, 220), width=3)
    cd.rounded_rectangle((x0+6, y0+6, x1-6, y1-6), radius=22, outline=(85, 188, 255, 120), width=2)
    # subtle top highlight
    cd.rounded_rectangle((x0+10, y0+9, x1-10, y0+58), radius=18, fill=(22, 112, 205, 65))
    im = Image.alpha_composite(im, card).convert('RGB')
    draw = ImageDraw.Draw(im)
    text = short_title(title)
    font = fit_font(draw, text, x1-x0-120, y1-y0-55)
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    tx = x0 + (x1-x0-tw)/2
    ty = y0 + (y1-y0-th)/2 - 7
    # text shadow + white text
    draw.text((tx+3, ty+4), text, font=font, fill=(0, 18, 70))
    draw.text((tx, ty), text, font=font, fill=(255,255,255))
    return im

written=[]
for item in targets:
    doc_id = item['doc_id']
    image_rel = item.get('image') or f'assets/doc_cards_web/{doc_id}.jpg'
    image_map[doc_id] = image_rel
    out = root / image_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        bak = backup_dir / out.name
        if not bak.exists():
            bak.write_bytes(out.read_bytes())
    im = draw_title_card(template, item['title'])
    im.save(out, quality=92, optimize=True, progressive=True)
    written.append({'doc_id': doc_id, 'title': short_title(item['title']), 'path': image_rel})

map_path.write_text(json.dumps(image_map, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(root/'tmp/pharma_card_written.json').write_text(json.dumps(written, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'written={len(written)}')
for row in written:
    print(row['doc_id'], row['title'], row['path'])
