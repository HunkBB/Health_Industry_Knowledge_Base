from pathlib import Path
import hashlib, json, math, random, re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
targets_path = root / 'tmp/pharma_card_targets.json'
map_path = root / 'assets/doc_cards_web/doc_image_web_map.json'
backup_dir = root / 'assets/doc_cards_web/backup_before_pharma_template_v2_20260617'
backup_dir.mkdir(parents=True, exist_ok=True)

targets = json.loads(targets_path.read_text(encoding='utf-8'))
image_map = json.loads(map_path.read_text(encoding='utf-8-sig'))
font_path = next(p for p in [
    Path(r'C:\Windows\Fonts\msyhbd.ttc'),
    Path(r'C:\Windows\Fonts\msyh.ttc'),
    Path(r'C:\Windows\Fonts\simhei.ttf'),
] if p.exists())

W, H = 1200, 600
JD_RED = (218, 41, 28, 245)
JD_DARK = (166, 25, 17, 245)
JD_ORANGE = (242, 92, 55, 235)
JD_LIGHT = (255, 210, 202, 210)


def short_title(title: str, rel: str = '') -> str:
    t = title.replace(' · ', ' ')
    t = t.replace('（2025-2026）', '').replace('(2025-2026)', '')
    t = t.replace('2025-2026', '25-26年').replace('2025—2026', '25-26年')
    t = t.replace('财报与渠道机会摘要', '财报与渠道机会')
    t = t.replace('_院内院外零售DTP电商O2O', '')
    t = t.replace('药企渠道布局 院内院外零售DTP电商O2O', '药企渠道布局')
    t = t.replace('_', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    if '药企渠道布局' in t:
        return '药企渠道布局'
    return t


def category(title: str, rel: str) -> str:
    text = f'{title} {rel}'
    if '新闻动态' in text:
        return 'news'
    if '财报' in text or '官方财报' in text or '核心数据' in text:
        return 'finance'
    if '矩阵' in text or '评分' in text:
        return 'matrix'
    if 'DTP' in text or '特药' in text or 'GLP1' in text:
        return 'dtp'
    if 'OTC' in text or '消费健康' in text or '慢病' in text or '药品与即时零售' in text:
        return 'otc'
    if '渠道' in text or '平台合作' in text or '合作模式' in text:
        return 'channel'
    return 'general'


def stable_rng(doc_id: str) -> random.Random:
    seed = int(hashlib.md5(doc_id.encode('utf-8')).hexdigest()[:8], 16)
    return random.Random(seed)


def fit_font(draw, text, max_width, max_height, max_size=64, min_size=26):
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(str(font_path), size)
        b = draw.textbbox((0, 0), text, font=font)
        if b[2] - b[0] <= max_width and b[3] - b[1] <= max_height:
            return font
    return ImageFont.truetype(str(font_path), min_size)


def wrap_text(draw, text, max_width, font):
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return [text]
    candidates = [' 财报', ' 新闻', ' 机会', ' 渠道', ' 矩阵', ' 评分', ' 数据']
    for token in candidates:
        if token in text:
            idx = text.find(token)
            lines = [text[:idx].strip(), text[idx:].strip()]
            if all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in lines):
                return lines
    mid = len(text) // 2
    split = min(
        range(max(1, mid - 7), min(len(text) - 1, mid + 8)),
        key=lambda i: abs(draw.textbbox((0, 0), text[:i], font=font)[2] - draw.textbbox((0, 0), text[i:], font=font)[2]),
    )
    return [text[:split].strip(), text[split:].strip()]


def draw_capsule(cx, cy, length, radius, angle, red, alpha=245):
    pad = 22
    layer = Image.new('RGBA', (int(length + 2 * pad), int(radius * 2 + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    box = (pad, pad, pad + length, pad + radius * 2)
    d.rounded_rectangle(box, radius=radius, fill=(255, 248, 246, alpha), outline=(255, 218, 210, alpha), width=2)
    d.rectangle((pad + length / 2, pad, pad + length, pad + radius * 2), fill=red)
    d.rounded_rectangle((pad + length / 2, pad, pad + length, pad + radius * 2), radius=radius, fill=red, outline=(255, 232, 228, alpha), width=1)
    d.arc(box, 90, 270, fill=(255, 255, 255, 150), width=3)
    d.line((pad + length * .61, pad + radius * .45, pad + length * .87, pad + radius * .34), fill=(255, 255, 255, 170), width=3)
    rot = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    return rot, (int(cx - rot.width / 2), int(cy - rot.height / 2))


def draw_tablet(cx, cy, r, angle, fill=(255, 248, 246, 245)):
    layer = Image.new('RGBA', (2 * r + 18, 2 * r + 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((9, 9, 9 + 2 * r, 9 + 2 * r), fill=fill, outline=(245, 178, 166, 230), width=2)
    d.line((9 + r * .45, 9 + r * .55, 9 + r * 1.55, 9 + r * 1.45), fill=(204, 92, 78, 180), width=max(2, r // 8))
    d.arc((11, 11, 7 + 2 * r, 7 + 2 * r), 210, 300, fill=(255, 255, 255, 175), width=2)
    rot = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    return rot, (int(cx - rot.width / 2), int(cy - rot.height / 2))


def draw_category_symbol(d, cat, rng):
    color = (190, 28, 22, 62)
    strong = (190, 28, 22, 86)
    if cat == 'news':
        x, y = 810 + rng.randint(-20, 15), 235 + rng.randint(-12, 16)
        d.rounded_rectangle((x, y, x + 135, y + 86), radius=12, outline=color, width=5)
        d.rectangle((x + 16, y + 18, x + 112, y + 25), fill=strong)
        d.rectangle((x + 16, y + 40, x + 94, y + 46), fill=color)
        d.rectangle((x + 16, y + 58, x + 118, y + 64), fill=color)
    elif cat == 'finance':
        x, y = 780 + rng.randint(-20, 16), 230 + rng.randint(-10, 14)
        for i, h in enumerate([52, 84, 38, 70]):
            d.rounded_rectangle((x + i * 34, y + 95 - h, x + i * 34 + 20, y + 95), radius=5, fill=strong)
        d.line((x - 8, y + 98, x + 145, y + 98), fill=color, width=4)
    elif cat == 'matrix':
        x, y = 770 + rng.randint(-15, 15), 225 + rng.randint(-10, 10)
        for i in range(4):
            for j in range(3):
                d.rounded_rectangle((x + i * 38, y + j * 30, x + i * 38 + 22, y + j * 30 + 18), radius=4, outline=color, width=3)
        d.ellipse((x + 42, y + 34, x + 58, y + 50), fill=strong)
        d.ellipse((x + 118, y + 64, x + 134, y + 80), fill=strong)
    elif cat == 'dtp':
        x, y = 770 + rng.randint(-16, 16), 235 + rng.randint(-10, 10)
        d.rounded_rectangle((x, y, x + 150, y + 72), radius=14, outline=color, width=4)
        d.arc((x + 16, y + 18, x + 70, y + 72), 190, 350, fill=strong, width=5)
        d.line((x + 92, y + 16, x + 92, y + 60), fill=strong, width=5)
        d.line((x + 74, y + 38, x + 110, y + 38), fill=strong, width=5)
    elif cat == 'otc':
        x, y = 790 + rng.randint(-15, 15), 230 + rng.randint(-8, 12)
        d.rounded_rectangle((x, y + 24, x + 130, y + 96), radius=14, outline=color, width=5)
        d.rounded_rectangle((x + 40, y, x + 90, y + 32), radius=10, outline=color, width=5)
        d.line((x + 65, y + 42, x + 65, y + 78), fill=strong, width=7)
        d.line((x + 47, y + 60, x + 83, y + 60), fill=strong, width=7)
    elif cat == 'channel':
        pts = [(790, 250), (875, 220), (935, 300), (840, 330)]
        pts = [(x + rng.randint(-12, 12), y + rng.randint(-10, 10)) for x, y in pts]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            d.line((a[0], a[1], b[0], b[1]), fill=color, width=5)
        for x, y in pts:
            d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=strong)


def make_card(item):
    doc_id, title, rel = item['doc_id'], item['title'], item['rel']
    rng = stable_rng(doc_id)
    cat = category(title, rel)
    bg = Image.new('RGB', (W, H), 'white')
    pix = bg.load()
    for y in range(H):
        for x in range(W):
            nx, ny = x / W, y / H
            r = 255
            g = int(247 - 13 * ny + 5 * math.sin(nx * math.pi))
            b = int(244 - 18 * ny)
            pix[x, y] = (r, max(225, g), max(220, b))
    im = bg.convert('RGBA')
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    circles = [(-55, 310, 210, (218, 41, 28, 58)), (1070, 210, 250, (242, 92, 55, 50)), (278, 270, 170, (255, 255, 255, 94)), (760, 290, 125, (218, 41, 28, 30)), (720, 170, 50, (255, 167, 148, 62))]
    for cx, cy, r, col in circles:
        cx += rng.randint(-36, 36); cy += rng.randint(-25, 25); r += rng.randint(-20, 25)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.ellipse((730, 175, 815, 260), outline=(218, 41, 28, 70), width=14)
    draw_category_symbol(d, cat, rng)
    d.ellipse((270, 420, 930, 545), fill=(255, 224, 218, 225), outline=(245, 150, 135, 165), width=2)
    d.rounded_rectangle((230, 465, 970, 560), radius=40, fill=(218, 41, 28, 235))
    d.ellipse((230, 425, 970, 535), fill=(255, 245, 242, 255), outline=(242, 146, 132, 205), width=2)
    d.ellipse((315, 398, 885, 485), fill=(255, 252, 250, 255))
    im = Image.alpha_composite(im, layer)
    pill_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    red_variants = [JD_RED, JD_DARK, JD_ORANGE, (226, 50, 40, 245), (196, 30, 24, 245)]
    positions = [
        (185 + rng.randint(-18, 22), 300 + rng.randint(-12, 22), 205 + rng.randint(-10, 12), 44, -35 + rng.randint(-9, 9), red_variants[rng.randrange(len(red_variants))]),
        (930 + rng.randint(-22, 17), 315 + rng.randint(-16, 17), 205 + rng.randint(-12, 14), 44, 32 + rng.randint(-8, 8), red_variants[rng.randrange(len(red_variants))]),
        (565 + rng.randint(-48, 45), 335 + rng.randint(-24, 20), 118 + rng.randint(-8, 10), 31, 18 + rng.randint(-14, 14), red_variants[rng.randrange(len(red_variants))]),
        (1010 + rng.randint(-24, 14), 430 + rng.randint(-12, 12), 118 + rng.randint(-8, 10), 28, -18 + rng.randint(-10, 10), red_variants[rng.randrange(len(red_variants))]),
        (120 + rng.randint(-18, 18), 445 + rng.randint(-12, 12), 132 + rng.randint(-10, 12), 33, -25 + rng.randint(-9, 9), red_variants[rng.randrange(len(red_variants))]),
    ]
    # Stable mild category-specific distribution changes.
    if cat in {'finance', 'matrix'}:
        positions[2] = (620 + rng.randint(-22, 25), 302 + rng.randint(-14, 18), 110, 29, -12 + rng.randint(-8, 8), red_variants[rng.randrange(len(red_variants))])
    elif cat in {'news', 'channel'}:
        positions[4] = (155 + rng.randint(-12, 22), 405 + rng.randint(-12, 10), 122, 31, 15 + rng.randint(-8, 8), red_variants[rng.randrange(len(red_variants))])
    elif cat == 'dtp':
        positions[1] = (945 + rng.randint(-18, 18), 278 + rng.randint(-12, 14), 218, 45, 20 + rng.randint(-7, 7), red_variants[rng.randrange(len(red_variants))])
    for cx, cy, length, radius, angle, red in positions:
        cap, pos = draw_capsule(cx, cy, length, radius, angle, red)
        pill_layer.alpha_composite(cap, pos)
    for cx, cy, r, angle in [
        (455 + rng.randint(-25, 25), 385 + rng.randint(-12, 12), 28, rng.randint(-25, 25)),
        (870 + rng.randint(-24, 24), 205 + rng.randint(-10, 10), 38, rng.randint(-35, 35)),
        (805 + rng.randint(-34, 28), 465 + rng.randint(-12, 12), 44, rng.randint(-18, 22)),
    ]:
        tab, pos = draw_tablet(cx, cy, r, angle)
        pill_layer.alpha_composite(tab, pos)
    im = Image.alpha_composite(im, pill_layer.filter(ImageFilter.GaussianBlur(0.12)))
    # Safe title card.
    x0, y0, x1, y1 = 110, 34, 1090, 166
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((x0 + 5, y0 + 8, x1 + 5, y1 + 10), radius=25, fill=(108, 16, 12, 95))
    sh = sh.filter(ImageFilter.GaussianBlur(1.5)); im = Image.alpha_composite(im, sh)
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((x0, y0, x1, y1), radius=25, fill=(190, 28, 22, 255), outline=(255, 218, 210, 245), width=4)
    cd.rounded_rectangle((x0 + 9, y0 + 8, x1 - 9, y0 + 40), radius=15, fill=(255, 120, 92, 86))
    cd.rounded_rectangle((x0 + 7, y0 + 7, x1 - 7, y1 - 7), radius=19, outline=(255, 180, 165, 170), width=2)
    im = Image.alpha_composite(im, card).convert('RGB')
    draw = ImageDraw.Draw(im)
    text = short_title(title, rel)
    font = fit_font(draw, text, x1 - x0 - 90, y1 - y0 - 36, max_size=58, min_size=30)
    lines = wrap_text(draw, text, x1 - x0 - 90, font)
    if len(lines) > 1:
        font = fit_font(draw, max(lines, key=len), x1 - x0 - 90, (y1 - y0 - 38) // 2, max_size=42, min_size=28)
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    total_h = sum(b[3] - b[1] for b in boxes) + (len(lines) - 1) * 6
    cy = y0 + (y1 - y0 - total_h) / 2 - 3
    for line, b in zip(lines, boxes):
        tw, th = b[2] - b[0], b[3] - b[1]
        tx = x0 + (x1 - x0 - tw) / 2
        draw.text((tx + 2, cy + 3), line, font=font, fill=(82, 8, 6))
        draw.text((tx, cy), line, font=font, fill=(255, 255, 255))
        cy += th + 6
    return im

written = []
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
    im = make_card(item)
    im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
    written.append({
        'doc_id': doc_id,
        'title': short_title(item['title'], item['rel']),
        'category': category(item['title'], item['rel']),
        'path': image_rel,
    })

map_path.write_text(json.dumps(image_map, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(root / 'tmp/pharma_card_written_v2_final.json').write_text(json.dumps(written, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'written={len(written)}')
for row in written:
    print(row['doc_id'], row['category'], row['title'], row['path'])
