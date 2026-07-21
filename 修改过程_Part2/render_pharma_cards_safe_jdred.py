from pathlib import Path
import json, re, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
targets = json.loads((root/'tmp/pharma_card_targets.json').read_text(encoding='utf-8'))
map_path = root/'assets/doc_cards_web/doc_image_web_map.json'
image_map = json.loads(map_path.read_text(encoding='utf-8-sig'))
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
W,H = 1200, 600
JD_RED=(218,41,28,245)
JD_DARK=(166,25,17,245)
JD_ORANGE=(242,92,55,235)

def short_title(title: str) -> str:
    t = title.replace(' · ', ' ').replace('（2025-2026）', '').replace('(2025-2026)', '')
    t = t.replace('2025-2026', '25-26年').replace('2025—2026', '25-26年')
    t = t.replace('财报与渠道机会摘要', '财报与渠道机会')
    t = t.replace('_', ' ')
    return re.sub(r'\s+', ' ', t).strip()

def fit_font(draw, text, max_width, max_height, max_size=66, min_size=26):
    for size in range(max_size, min_size-1, -2):
        font = ImageFont.truetype(str(font_path), size)
        b = draw.textbbox((0,0), text, font=font)
        if b[2]-b[0] <= max_width and b[3]-b[1] <= max_height:
            return font
    return ImageFont.truetype(str(font_path), min_size)

def wrap_text(draw, text, max_width, font):
    if draw.textbbox((0,0), text, font=font)[2] <= max_width:
        return [text]
    tokens = re.split(r'( |与|和|及|/)', text)
    lines=[]; cur=''
    for tok in tokens:
        if not tok: continue
        candidate = cur + tok
        if cur and draw.textbbox((0,0), candidate, font=font)[2] > max_width:
            lines.append(cur.strip()); cur = tok.strip()
        else:
            cur = candidate
    if cur.strip(): lines.append(cur.strip())
    if len(lines) <= 2: return lines
    mid=len(text)//2
    split=min(range(max(1,mid-6),min(len(text)-1,mid+7)), key=lambda i: abs(draw.textbbox((0,0),text[:i],font=font)[2]-draw.textbbox((0,0),text[i:],font=font)[2]))
    return [text[:split].strip(), text[split:].strip()]

def draw_capsule(cx, cy, length, radius, angle, c1, alpha=255):
    pad=20
    layer=Image.new('RGBA',(int(length+2*pad),int(radius*2+2*pad)),(0,0,0,0)); d=ImageDraw.Draw(layer)
    box=(pad,pad,pad+length,pad+radius*2)
    d.rounded_rectangle(box,radius=radius,fill=(255,248,246,alpha),outline=(255,215,205,alpha),width=2)
    d.rectangle((pad+length/2,pad,pad+length,pad+radius*2),fill=c1)
    d.rounded_rectangle((pad+length/2,pad,pad+length,pad+radius*2),radius=radius,fill=c1,outline=(255,230,225,alpha),width=1)
    d.arc(box,90,270,fill=(255,255,255,150),width=3)
    d.line((pad+length*.61,pad+radius*.45,pad+length*.87,pad+radius*.34),fill=(255,255,255,165),width=3)
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2),int(cy-rot.height/2))

def draw_tablet(cx,cy,r,angle,fill):
    layer=Image.new('RGBA',(2*r+16,2*r+16),(0,0,0,0)); d=ImageDraw.Draw(layer)
    d.ellipse((8,8,8+2*r,8+2*r),fill=fill,outline=(245,178,166,230),width=2)
    d.line((8+r*.45,8+r*.55,8+r*1.55,8+r*1.45),fill=(204,92,78,180),width=max(2,r//8))
    d.arc((10,10,6+2*r,6+2*r),210,300,fill=(255,255,255,175),width=2)
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2),int(cy-rot.height/2))

def make_card(title, idx):
    rng=random.Random(12060+idx)
    bg=Image.new('RGB',(W,H),'white'); pix=bg.load()
    for y in range(H):
        for x in range(W):
            nx=x/W; ny=y/H
            r=255
            g=int(246 - 13*ny + 5*math.sin(nx*math.pi))
            b=int(243 - 17*ny)
            pix[x,y]=(r,max(225,g),max(220,b))
    im=bg.convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
    # warm JD red medical bubbles, varied but safe
    circles=[(-55,310,210,(218,41,28,62)),(1070,210,250,(242,92,55,54)),(278,270,170,(255,255,255,92)),(760,290,125,(218,41,28,34)),(720,170,50,(255,167,148,65))]
    for cx,cy,r,col in circles:
        cx+=rng.randint(-35,35); cy+=rng.randint(-25,25); r+=rng.randint(-20,25)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=col)
    d.ellipse((730,175,815,260),outline=(218,41,28,76),width=14)
    # podium visible and red accented
    d.ellipse((270,420,930,545),fill=(255,224,218,230),outline=(245,150,135,170),width=2)
    d.rounded_rectangle((230,465,970,560),radius=40,fill=(218,41,28,235))
    d.ellipse((230,425,970,535),fill=(255,245,242,255),outline=(242,146,132,210),width=2)
    d.ellipse((315,398,885,485),fill=(255,252,250,255))
    im=Image.alpha_composite(im,layer)
    pill_layer=Image.new('RGBA',(W,H),(0,0,0,0))
    red_variants=[JD_RED,JD_DARK,JD_ORANGE,(226,50,40,245),(196,30,24,245)]
    positions=[
        (185+rng.randint(-15,20),300+rng.randint(-10,20),210,45,-35+rng.randint(-8,8),red_variants[idx%len(red_variants)]),
        (930+rng.randint(-20,15),315+rng.randint(-15,15),210,45,32+rng.randint(-7,7),red_variants[(idx+1)%len(red_variants)]),
        (565+rng.randint(-35,35),335+rng.randint(-18,18),120,32,18+rng.randint(-12,12),red_variants[(idx+2)%len(red_variants)]),
        (1010+rng.randint(-20,10),430+rng.randint(-10,10),120,28,-18+rng.randint(-10,10),red_variants[(idx+3)%len(red_variants)]),
        (120+rng.randint(-15,15),445+rng.randint(-10,10),135,34,-25+rng.randint(-8,8),red_variants[(idx+4)%len(red_variants)]),
    ]
    # slight distribution variations: skip/reposition one decorative pill by index
    if idx % 3 == 1: positions[2]=(610+rng.randint(-20,25),295+rng.randint(-10,18),112,30,-12+rng.randint(-8,8),red_variants[(idx+2)%len(red_variants)])
    if idx % 3 == 2: positions[4]=(155+rng.randint(-10,20),405+rng.randint(-10,10),125,32,15+rng.randint(-8,8),red_variants[(idx+4)%len(red_variants)])
    for cx,cy,l,r,ang,col in positions:
        cap,pos=draw_capsule(cx,cy,l,r,ang,col,245); pill_layer.alpha_composite(cap,pos)
    tablets=[(455+rng.randint(-20,20),385+rng.randint(-10,10),28,rng.randint(-25,25)),(870+rng.randint(-20,20),205+rng.randint(-8,8),38,rng.randint(-35,35)),(805+rng.randint(-30,25),465+rng.randint(-10,10),44,rng.randint(-15,20))]
    for cx,cy,r,ang in tablets:
        tab,pos=draw_tablet(cx,cy,r,ang,(255,248,246,245)); pill_layer.alpha_composite(tab,pos)
    im=Image.alpha_composite(im,pill_layer.filter(ImageFilter.GaussianBlur(0.12)))
    # title card JD red, fully safe
    x0,y0,x1,y1=110,36,1090,160
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((x0+4,y0+7,x1+4,y1+9),radius=24,fill=(108,16,12,95)); sh=sh.filter(ImageFilter.GaussianBlur(1.4)); im=Image.alpha_composite(im,sh)
    card=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(card)
    cd.rounded_rectangle((x0,y0,x1,y1),radius=24,fill=(190,28,22,255),outline=(255,218,210,245),width=4)
    cd.rounded_rectangle((x0+9,y0+8,x1-9,y0+39),radius=15,fill=(255,120,92,86))
    cd.rounded_rectangle((x0+7,y0+7,x1-7,y1-7),radius=19,outline=(255,180,165,170),width=2)
    im=Image.alpha_composite(im,card).convert('RGB')
    draw=ImageDraw.Draw(im); text=short_title(title)
    font=fit_font(draw,text,x1-x0-86,y1-y0-34,max_size=58,min_size=30)
    lines=wrap_text(draw,text,x1-x0-86,font)
    if len(lines)>1: font=fit_font(draw,max(lines,key=len),x1-x0-86,(y1-y0-34)//2,max_size=42,min_size=28)
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
    im=make_card(item['title'],idx)
    im.save(out,format='JPEG',quality=92,subsampling=0,progressive=False,optimize=False)
    written.append({'doc_id':doc_id,'title':short_title(item['title']),'path':image_rel})
map_path.write_text(json.dumps(image_map,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'tmp/pharma_card_written_safe_jdred.json').write_text(json.dumps(written,ensure_ascii=False,indent=2),encoding='utf-8')
print('rendered safe jd red',len(written))
