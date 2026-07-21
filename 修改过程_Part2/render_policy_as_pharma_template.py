from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, random, hashlib, math
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
targets = [
    {'doc_id':'doc-0800e61de0a4','title':'医保政策汇总','path':'assets/doc_cards_web/policy_20260617/doc-0800e61de0a4.jpg','kind':'医保'},
    {'doc_id':'doc-f79a4ef81b94','title':'慢特病与门诊统筹政策资料','path':'assets/doc_cards_web/policy_20260617/doc-f79a4ef81b94.jpg','kind':'慢特病'},
]
backup = root / 'assets/doc_cards_web/backup_before_policy_to_pharma_template_20260617'
backup.mkdir(parents=True, exist_ok=True)
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
W,H=1200,600
RED=(218,41,28,245); DARK=(166,25,17,245); ORANGE=(242,92,55,235); PALE=(255,246,243,245)

def fit(draw,text,maxw,maxh,max_size=58,min_size=30):
    for size in range(max_size,min_size-1,-2):
        font=ImageFont.truetype(str(font_path),size); b=draw.textbbox((0,0),text,font=font)
        if b[2]-b[0] <= maxw and b[3]-b[1] <= maxh: return font
    return ImageFont.truetype(str(font_path),min_size)

def capsule(cx,cy,length,radius,angle,red):
    pad=22; layer=Image.new('RGBA',(int(length+2*pad),int(radius*2+2*pad)),(0,0,0,0)); d=ImageDraw.Draw(layer)
    box=(pad,pad,pad+length,pad+radius*2)
    d.rounded_rectangle(box,radius=radius,fill=PALE,outline=(255,218,210,240),width=2)
    d.rectangle((pad+length/2,pad,pad+length,pad+radius*2),fill=red)
    d.rounded_rectangle((pad+length/2,pad,pad+length,pad+radius*2),radius=radius,fill=red,outline=(255,232,228,220),width=1)
    d.line((pad+length*.62,pad+radius*.45,pad+length*.86,pad+radius*.34),fill=(255,255,255,165),width=3)
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2),int(cy-rot.height/2))

def tablet(cx,cy,r,angle):
    layer=Image.new('RGBA',(2*r+18,2*r+18),(0,0,0,0)); d=ImageDraw.Draw(layer)
    d.ellipse((9,9,9+2*r,9+2*r),fill=PALE,outline=(245,178,166,230),width=2)
    d.line((9+r*.45,9+r*.55,9+r*1.55,9+r*1.45),fill=(204,92,78,180),width=max(2,r//8))
    rot=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return rot,(int(cx-rot.width/2),int(cy-rot.height/2))

def policy_symbol(kind,rng):
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
    x,y=780+rng.randint(-16,16),220+rng.randint(-10,15)
    if kind=='医保':
        d.rounded_rectangle((x,y,x+155,y+110),radius=16,fill=(255,245,242,205),outline=(190,28,22,90),width=4)
        d.rectangle((x+18,y+22,x+135,y+35),fill=(190,28,22,80))
        d.line((x+78,y+52,x+78,y+88),fill=(190,28,22,110),width=8)
        d.line((x+57,y+70,x+99,y+70),fill=(190,28,22,110),width=8)
        d.rectangle((x+22,y+92,x+92,y+100),fill=(190,28,22,55))
    else:
        d.rounded_rectangle((x,y,x+170,y+112),radius=16,fill=(255,245,242,205),outline=(190,28,22,90),width=4)
        for i,h in enumerate([48,75,34,62]):
            bx=x+28+i*32; d.rounded_rectangle((bx,y+92-h,bx+18,y+92),radius=5,fill=(190,28,22,85))
        d.line((x+20,y+96,x+148,y+96),fill=(190,28,22,70),width=4)
        d.arc((x+24,y+18,x+86,y+78),200,340,fill=(190,28,22,85),width=5)
    return layer

def make_card(t,idx):
    rng=random.Random(int(hashlib.md5(t['doc_id'].encode()).hexdigest()[:8],16))
    bg=Image.new('RGB',(W,H),'white'); pix=bg.load()
    for yy in range(H):
        for xx in range(W):
            nx,ny=xx/W,yy/H; pix[xx,yy]=(255,max(226,int(248-14*ny+5*math.sin(nx*math.pi))),max(221,int(245-18*ny)))
    im=bg.convert('RGBA'); layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
    for cx,cy,r,col in [(-55,310,210,(218,41,28,52)),(1070,215,250,(242,92,55,44)),(280,270,170,(255,255,255,96)),(740,285,125,(218,41,28,30))]:
        cx+=rng.randint(-35,35); cy+=rng.randint(-25,25); d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=col)
    d.ellipse((270,420,930,545),fill=(255,224,218,218),outline=(245,150,135,150),width=2)
    d.rounded_rectangle((230,465,970,560),radius=40,fill=(218,41,28,230))
    d.ellipse((230,425,970,535),fill=(255,245,242,255),outline=(242,146,132,198),width=2)
    d.ellipse((315,398,885,485),fill=(255,252,250,255))
    im=Image.alpha_composite(im,layer)
    im=Image.alpha_composite(im,policy_symbol(t['kind'],rng))
    elems=Image.new('RGBA',(W,H),(0,0,0,0))
    reds=[RED,DARK,ORANGE]
    for cx,cy,l,r,ang in [(185,310,205,44,-35),(925,320,205,44,30),(565,335,118,31,15),(105,430,132,33,-18)]:
        cap,pos=capsule(cx+rng.randint(-24,24),cy+rng.randint(-18,18),l,r,ang+rng.randint(-10,10),reds[rng.randrange(3)]); elems.alpha_composite(cap,pos)
    for cx,cy,r,ang in [(455,385,28,15),(850,455,42,-12)]:
        tab,pos=tablet(cx+rng.randint(-20,20),cy+rng.randint(-10,10),r,ang+rng.randint(-15,15)); elems.alpha_composite(tab,pos)
    im=Image.alpha_composite(im,elems)
    # title
    x0,y0,x1,y1=110,34,1090,166
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh); sd.rounded_rectangle((x0+5,y0+8,x1+5,y1+10),radius=25,fill=(108,16,12,95)); sh=sh.filter(ImageFilter.GaussianBlur(1.5)); im=Image.alpha_composite(im,sh)
    card=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(card)
    cd.rounded_rectangle((x0,y0,x1,y1),radius=25,fill=(190,28,22,255),outline=(255,218,210,245),width=4)
    cd.rounded_rectangle((x0+9,y0+8,x1-9,y0+40),radius=15,fill=(255,120,92,86))
    im=Image.alpha_composite(im,card).convert('RGB'); draw=ImageDraw.Draw(im)
    font=fit(draw,t['title'],x1-x0-90,y1-y0-40)
    b=draw.textbbox((0,0),t['title'],font=font); x=x0+(x1-x0-(b[2]-b[0]))/2; y=y0+(y1-y0-(b[3]-b[1]))/2-4
    draw.text((x+2,y+3),t['title'],font=font,fill=(82,8,6)); draw.text((x,y),t['title'],font=font,fill=(255,255,255))
    return im
mp_path=root/'assets/doc_cards_web/doc_image_web_map.json'; mp=json.loads(mp_path.read_text(encoding='utf-8-sig'))
for idx,t in enumerate(targets):
    out=root/t['path']; out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        bak=backup/out.name
        if not bak.exists(): bak.write_bytes(out.read_bytes())
    im=make_card(t,idx); im.save(out,format='JPEG',quality=92,subsampling=0,progressive=False,optimize=False)
    mp[t['doc_id']]=t['path']
mp_path.write_text(json.dumps(mp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('written',len(targets))
