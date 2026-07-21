from pathlib import Path
import hashlib, json, math, random, re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
targets = json.loads((root / 'tmp/pharma_card_targets.json').read_text(encoding='utf-8'))
map_path = root / 'assets/doc_cards_web/doc_image_web_map.json'
image_map = json.loads(map_path.read_text(encoding='utf-8-sig'))
backup_dir = root / 'assets/doc_cards_web/backup_before_pharma_template_v3_varied_elements_20260617'
backup_dir.mkdir(parents=True, exist_ok=True)
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
W, H = 1200, 600
RED = (218, 41, 28, 245)
DARK = (166, 25, 17, 245)
ORANGE = (242, 92, 55, 235)
PALE = (255, 246, 243, 245)
OUTLINE = (242, 146, 132, 205)


def short_title(title, rel=''):
    t = title.replace(' · ', ' ').replace('（2025-2026）', '').replace('(2025-2026)', '')
    t = t.replace('2025-2026', '25-26年').replace('2025—2026', '25-26年')
    t = t.replace('财报与渠道机会摘要', '财报与渠道机会')
    t = t.replace('_院内院外零售DTP电商O2O', '').replace('_', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    if '药企渠道布局' in t:
        return '药企渠道布局'
    return t


def category(title, rel):
    text = f'{title} {rel}'
    if '新闻动态' in text: return 'news'
    if '财报' in text or '官方财报' in text or '核心数据' in text: return 'finance'
    if '矩阵' in text or '评分' in text: return 'matrix'
    if 'DTP' in text or '特药' in text or 'GLP1' in text: return 'dtp'
    if 'OTC' in text or '消费健康' in text or '慢病' in text or '药品与即时零售' in text: return 'otc'
    if '渠道' in text or '平台合作' in text or '合作模式' in text: return 'channel'
    return 'general'


def rng_for(doc_id):
    return random.Random(int(hashlib.md5(doc_id.encode()).hexdigest()[:8], 16))


def fit_font(draw, text, max_width, max_height, max_size=58, min_size=28):
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(str(font_path), size)
        b = draw.textbbox((0, 0), text, font=font)
        if b[2] - b[0] <= max_width and b[3] - b[1] <= max_height:
            return font
    return ImageFont.truetype(str(font_path), min_size)


def wrap_text(draw, text, max_width, font):
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return [text]
    for token in [' 财报', ' 新闻', ' 机会', ' 渠道', ' 矩阵', ' 评分', ' 数据', ' 药品']:
        if token in text:
            i = text.find(token)
            lines = [text[:i].strip(), text[i:].strip()]
            if all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in lines):
                return lines
    mid = len(text) // 2
    split = min(range(max(1, mid - 7), min(len(text) - 1, mid + 8)), key=lambda i: abs(draw.textbbox((0,0), text[:i], font=font)[2] - draw.textbbox((0,0), text[i:], font=font)[2]))
    return [text[:split].strip(), text[split:].strip()]


def alpha_layer(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def capsule(cx, cy, length, radius, angle, red=RED, white=PALE):
    pad = 22
    layer = Image.new('RGBA', (int(length + 2 * pad), int(radius * 2 + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    box = (pad, pad, pad + length, pad + radius * 2)
    d.rounded_rectangle(box, radius=radius, fill=white, outline=(255, 218, 210, 240), width=2)
    d.rectangle((pad + length / 2, pad, pad + length, pad + radius * 2), fill=red)
    d.rounded_rectangle((pad + length / 2, pad, pad + length, pad + radius * 2), radius=radius, fill=red, outline=(255, 232, 228, 220), width=1)
    d.line((pad + length * .62, pad + radius * .45, pad + length * .86, pad + radius * .34), fill=(255,255,255,165), width=3)
    rot = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    return rot, (int(cx - rot.width/2), int(cy - rot.height/2))


def tablet(cx, cy, r, angle, fill=PALE):
    layer = Image.new('RGBA', (2*r+18, 2*r+18), (0,0,0,0)); d=ImageDraw.Draw(layer)
    d.ellipse((9,9,9+2*r,9+2*r), fill=fill, outline=(245,178,166,230), width=2)
    d.line((9+r*.45,9+r*.55,9+r*1.55,9+r*1.45), fill=(204,92,78,180), width=max(2,r//8))
    rot=layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2), int(cy-rot.height/2))


def bottle(cx, cy, scale, angle, red=RED):
    w, h = int(92*scale), int(150*scale)
    layer = Image.new('RGBA', (w+50, h+50), (0,0,0,0)); d=ImageDraw.Draw(layer); ox=25; oy=25
    d.rounded_rectangle((ox+w*.32, oy, ox+w*.68, oy+h*.22), radius=int(8*scale), fill=(255,245,242,245), outline=OUTLINE, width=max(1,int(2*scale)))
    d.rounded_rectangle((ox+w*.18, oy+h*.18, ox+w*.82, oy+h), radius=int(18*scale), fill=(255,248,246,245), outline=OUTLINE, width=max(1,int(2*scale)))
    d.rounded_rectangle((ox+w*.24, oy+h*.48, ox+w*.76, oy+h*.72), radius=int(8*scale), fill=red)
    d.line((ox+w*.34, oy+h*.55, ox+w*.66, oy+h*.55), fill=(255,255,255,170), width=max(1,int(3*scale)))
    rot=layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2), int(cy-rot.height/2))


def blister(cx, cy, scale, angle):
    w,h=int(150*scale),int(95*scale)
    layer=Image.new('RGBA',(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(layer); ox=20; oy=20
    d.rounded_rectangle((ox,oy,ox+w,oy+h),radius=int(14*scale),fill=(255,245,242,210),outline=OUTLINE,width=max(1,int(2*scale)))
    for i in range(3):
        for j in range(2):
            x=ox+int((25+i*48)*scale); y=oy+int((25+j*38)*scale); r=int(13*scale)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,255,230),outline=(242,150,135,180),width=1)
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2), int(cy-rot.height/2))


def test_tube(cx, cy, scale, angle):
    w,h=int(55*scale),int(170*scale)
    layer=Image.new('RGBA',(w+50,h+50),(0,0,0,0)); d=ImageDraw.Draw(layer); ox=25; oy=25
    d.rounded_rectangle((ox,oy,ox+w,oy+h),radius=int(23*scale),fill=(255,248,246,210),outline=OUTLINE,width=max(1,int(2*scale)))
    d.rounded_rectangle((ox+5,oy+h*.50,ox+w-5,oy+h-8),radius=int(18*scale),fill=(218,41,28,165))
    d.line((ox+w*.30,oy+h*.18,ox+w*.70,oy+h*.18),fill=(255,255,255,150),width=max(1,int(3*scale)))
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2), int(cy-rot.height/2))


def data_card(cx, cy, scale, angle, mode):
    w,h=int(170*scale),int(105*scale)
    layer=Image.new('RGBA',(w+50,h+50),(0,0,0,0)); d=ImageDraw.Draw(layer); ox=25; oy=25
    d.rounded_rectangle((ox,oy,ox+w,oy+h),radius=int(14*scale),fill=(255,245,242,205),outline=(218,41,28,90),width=max(1,int(3*scale)))
    if mode=='bars':
        for i,val in enumerate([.45,.8,.33,.62]):
            x=ox+int((30+i*30)*scale); d.rounded_rectangle((x,oy+h-int(75*scale*val),x+int(15*scale),oy+h-int(15*scale)),radius=3,fill=(190,28,22,85))
    elif mode=='grid':
        for i in range(4):
            for j in range(3):
                d.rounded_rectangle((ox+int((18+i*36)*scale),oy+int((18+j*24)*scale),ox+int((42+i*36)*scale),oy+int((33+j*24)*scale)),radius=3,outline=(190,28,22,75),width=2)
    else:
        for y in [25,47,69]: d.rectangle((ox+int(24*scale),oy+int(y*scale),ox+int(138*scale),oy+int((y+7)*scale)),fill=(190,28,22,65))
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2), int(cy-rot.height/2))


def med_kit(cx, cy, scale, angle):
    w,h=int(135*scale),int(105*scale)
    layer=Image.new('RGBA',(w+50,h+60),(0,0,0,0)); d=ImageDraw.Draw(layer); ox=25; oy=35
    d.rounded_rectangle((ox+w*.32,oy-28*scale,ox+w*.68,oy+10*scale),radius=int(8*scale),outline=(218,41,28,80),width=max(1,int(4*scale)))
    d.rounded_rectangle((ox,oy,ox+w,oy+h),radius=int(16*scale),fill=(255,245,242,205),outline=(218,41,28,85),width=max(1,int(4*scale)))
    d.line((ox+w*.5,oy+h*.30,ox+w*.5,oy+h*.70),fill=(190,28,22,85),width=max(2,int(7*scale)))
    d.line((ox+w*.35,oy+h*.50,ox+w*.65,oy+h*.50),fill=(190,28,22,85),width=max(2,int(7*scale)))
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2), int(cy-rot.height/2))


def network(cx, cy, scale, angle):
    w,h=int(180*scale),int(120*scale)
    layer=Image.new('RGBA',(w+50,h+50),(0,0,0,0)); d=ImageDraw.Draw(layer); ox=25; oy=25
    pts=[(ox+20*scale,oy+50*scale),(ox+82*scale,oy+22*scale),(ox+150*scale,oy+55*scale),(ox+95*scale,oy+95*scale)]
    for a,b in zip(pts, pts[1:]+pts[:1]): d.line((a[0],a[1],b[0],b[1]),fill=(190,28,22,75),width=max(2,int(4*scale)))
    for x,y in pts: d.ellipse((x-12*scale,y-12*scale,x+12*scale,y+12*scale),fill=(190,28,22,85))
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2), int(cy-rot.height/2))


def icon_asset(kind, cx, cy, scale, angle):
    if kind=='capsule': return capsule(cx,cy,180*scale,38*scale,angle,RED)
    if kind=='tablet': return tablet(cx,cy,int(42*scale),angle)
    if kind=='bottle': return bottle(cx,cy,scale,angle)
    if kind=='blister': return blister(cx,cy,scale,angle)
    if kind=='tube': return test_tube(cx,cy,scale,angle)
    if kind=='bars': return data_card(cx,cy,scale,angle,'bars')
    if kind=='grid': return data_card(cx,cy,scale,angle,'grid')
    if kind=='news': return data_card(cx,cy,scale,angle,'news')
    if kind=='kit': return med_kit(cx,cy,scale,angle)
    if kind=='network': return network(cx,cy,scale,angle)
    return capsule(cx,cy,160*scale,34*scale,angle,DARK)


def element_set(cat, idx):
    sets = {
        'news': [['capsule','news','tablet','bottle'], ['blister','news','capsule','tablet'], ['bottle','news','tablet','capsule']],
        'finance': [['capsule','bars','tablet','bottle'], ['blister','bars','capsule','tablet'], ['bottle','bars','tablet','capsule']],
        'matrix': [['grid','blister','capsule','tablet'], ['grid','tablet','bottle','capsule'], ['blister','grid','tablet','capsule']],
        'dtp': [['tube','capsule','bottle','tablet'], ['bottle','tube','blister','capsule'], ['capsule','tube','tablet','bars']],
        'otc': [['kit','capsule','tablet','bottle'], ['kit','blister','capsule','tablet'], ['bottle','kit','tablet','capsule']],
        'channel': [['network','capsule','bottle','tablet'], ['network','blister','capsule','tablet'], ['capsule','network','bars','tablet']],
        'general': [['capsule','tablet','bottle','blister'], ['bottle','capsule','grid','tablet']],
    }
    arr = sets.get(cat, sets['general'])
    return arr[idx % len(arr)]


def make_bg(item, idx):
    doc_id, title, rel = item['doc_id'], item['title'], item['rel']
    rng = rng_for(doc_id)
    cat = category(title, rel)
    bg = Image.new('RGB', (W,H), 'white'); pix=bg.load()
    for y in range(H):
        for x in range(W):
            nx,ny=x/W,y/H
            pix[x,y]=(255, max(226,int(248-14*ny+5*math.sin(nx*math.pi))), max(221,int(245-18*ny)))
    im=bg.convert('RGBA')
    layer=alpha_layer(); d=ImageDraw.Draw(layer)
    # Differentiated soft blobs.
    blob_palette=[(218,41,28,50),(242,92,55,42),(255,255,255,96),(255,190,176,48),(190,28,22,26)]
    for bidx,(cx,cy,r) in enumerate([(-45,310,210),(1080,225,250),(285,270,170),(755,290,125),(705,165,55)]):
        d.ellipse((cx+rng.randint(-40,40)-r, cy+rng.randint(-28,28)-r, cx+rng.randint(-40,40)+r, cy+rng.randint(-28,28)+r), fill=blob_palette[(idx+bidx)%len(blob_palette)])
    # Podium remains consistent but not dominant.
    d.ellipse((270,420,930,545),fill=(255,224,218,218),outline=(245,150,135,150),width=2)
    d.rounded_rectangle((230,465,970,560),radius=40,fill=(218,41,28,230))
    d.ellipse((230,425,970,535),fill=(255,245,242,255),outline=(242,146,132,198),width=2)
    d.ellipse((315,398,885,485),fill=(255,252,250,255))
    im=Image.alpha_composite(im,layer)
    elems=alpha_layer()
    kinds=element_set(cat, idx)
    # Four visible zones; each card uses different element types and slight positions.
    zones=[(190,315,1.05,-30),(910,300,1.10,28),(550,330,.72,12),(105,430,.72,-18),(830,445,.62,-10)]
    for zidx, (cx,cy,scale,ang) in enumerate(zones):
        kind = kinds[zidx % len(kinds)] if zidx < 4 else ('tablet' if idx % 2 else 'capsule')
        asset,pos = icon_asset(kind, cx+rng.randint(-28,28), cy+rng.randint(-20,20), scale*(.92+rng.random()*.18), ang+rng.randint(-12,12))
        elems.alpha_composite(asset,pos)
    im=Image.alpha_composite(im, elems.filter(ImageFilter.GaussianBlur(0.08)))
    return im.convert('RGB')


def draw_title(im, text):
    im=im.convert('RGBA')
    x0,y0,x1,y1=110,34,1090,166
    sh=alpha_layer(); sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((x0+5,y0+8,x1+5,y1+10),radius=25,fill=(108,16,12,95)); sh=sh.filter(ImageFilter.GaussianBlur(1.5)); im=Image.alpha_composite(im,sh)
    card=alpha_layer(); cd=ImageDraw.Draw(card)
    cd.rounded_rectangle((x0,y0,x1,y1),radius=25,fill=(190,28,22,255),outline=(255,218,210,245),width=4)
    cd.rounded_rectangle((x0+9,y0+8,x1-9,y0+40),radius=15,fill=(255,120,92,86))
    cd.rounded_rectangle((x0+7,y0+7,x1-7,y1-7),radius=19,outline=(255,180,165,170),width=2)
    im=Image.alpha_composite(im,card).convert('RGB')
    draw=ImageDraw.Draw(im); font=fit_font(draw,text,x1-x0-90,y1-y0-36)
    lines=wrap_text(draw,text,x1-x0-90,font)
    if len(lines)>1: font=fit_font(draw,max(lines,key=len),x1-x0-90,(y1-y0-38)//2,max_size=42,min_size=28)
    boxes=[draw.textbbox((0,0),line,font=font) for line in lines]
    total_h=sum(b[3]-b[1] for b in boxes)+(len(lines)-1)*6
    cy=y0+(y1-y0-total_h)/2-3
    for line,b in zip(lines,boxes):
        tw=b[2]-b[0]; th=b[3]-b[1]; tx=x0+(x1-x0-tw)/2
        draw.text((tx+2,cy+3),line,font=font,fill=(82,8,6))
        draw.text((tx,cy),line,font=font,fill=(255,255,255))
        cy+=th+6
    return im

written=[]
for idx,item in enumerate(targets):
    doc_id=item['doc_id']; image_rel=item.get('image') or f'assets/doc_cards_web/{doc_id}.jpg'; image_map[doc_id]=image_rel
    out=root/image_rel; out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        bak=backup_dir/out.name
        if not bak.exists(): bak.write_bytes(out.read_bytes())
    title=short_title(item['title'],item['rel'])
    im=draw_title(make_bg(item,idx),title)
    im.save(out,format='JPEG',quality=92,subsampling=0,progressive=False,optimize=False)
    written.append({'doc_id':doc_id,'title':title,'category':category(item['title'],item['rel']),'elements':element_set(category(item['title'],item['rel']),idx),'path':image_rel})
map_path.write_text(json.dumps(image_map,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'tmp/pharma_card_written_v3_varied_elements.json').write_text(json.dumps(written,ensure_ascii=False,indent=2),encoding='utf-8')
print('written',len(written))
for row in written: print(row['doc_id'], row['category'], ','.join(row['elements']), row['title'])
