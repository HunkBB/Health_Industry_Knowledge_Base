from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
out = root / 'assets/doc_cards_web/doc-a0175105fac2.jpg'
backup = root / 'assets/doc_cards_web/backup_before_restore_commerce_report_20260617'
backup.mkdir(parents=True, exist_ok=True)
if out.exists():
    bak = backup / out.name
    if not bak.exists(): bak.write_bytes(out.read_bytes())
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
W,H=1200,600
im=Image.new('RGB',(W,H),(255,247,243)).convert('RGBA')
# warm background
layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
d.ellipse((-120,110,310,520), fill=(218,41,28,46))
d.ellipse((840,-80,1280,390), fill=(242,92,55,44))
d.ellipse((245,120,520,400), fill=(255,255,255,120))
d.ellipse((650,170,880,390), fill=(218,41,28,30))
# visual elements: report card + delivery/retail map
# large report card
d.rounded_rectangle((150,215,520,430), radius=24, fill=(255,252,250,238), outline=(218,41,28,105), width=4)
d.rectangle((150,215,520,270), fill=(190,28,22,230))
d.rectangle((190,300,470,314), fill=(218,41,28,78))
d.rectangle((190,335,430,349), fill=(218,41,28,58))
d.rectangle((190,370,485,384), fill=(218,41,28,58))
# small bar chart
d.rounded_rectangle((710,245,955,405), radius=20, fill=(255,252,250,220), outline=(218,41,28,85), width=4)
for i,h in enumerate([55,96,72,120]):
    x=755+i*42
    d.rounded_rectangle((x,370-h,x+24,370), radius=6, fill=(190,28,22,95))
d.line((742,374,925,374), fill=(190,28,22,80), width=4)
# network nodes for instant retail
pts=[(610,335),(675,285),(760,330),(690,400)]
for a,b in zip(pts, pts[1:]+pts[:1]): d.line((*a,*b), fill=(190,28,22,80), width=5)
for x,y in pts: d.ellipse((x-14,y-14,x+14,y+14), fill=(218,41,28,115))
# capsules/tablets
for box,ang in [((86,402,230,462),-22),((945,410,1090,470),18),((560,438,625,502),-8)]:
    cap=Image.new('RGBA',(180,80),(0,0,0,0)); cd=ImageDraw.Draw(cap)
    cd.rounded_rectangle((12,14,168,66), radius=26, fill=(255,248,246,245), outline=(245,178,166,230), width=2)
    cd.rectangle((90,14,168,66), fill=(218,41,28,230))
    cd.rounded_rectangle((90,14,168,66), radius=26, fill=(218,41,28,230))
    cap=cap.rotate(ang, expand=True, resample=Image.Resampling.BICUBIC)
    cx=(box[0]+box[2])//2; cy=(box[1]+box[3])//2
    layer.alpha_composite(cap,(cx-cap.width//2,cy-cap.height//2))
# title card
im=Image.alpha_composite(im,layer)
shadow=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
sd.rounded_rectangle((115,42,1095,172), radius=25, fill=(108,16,12,95)); shadow=shadow.filter(ImageFilter.GaussianBlur(2))
im=Image.alpha_composite(im,shadow)
card=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(card)
cd.rounded_rectangle((110,34,1090,166), radius=25, fill=(190,28,22,255), outline=(255,218,210,245), width=4)
cd.rounded_rectangle((119,42,1081,74), radius=15, fill=(255,120,92,86))
im=Image.alpha_composite(im,card).convert('RGB')
draw=ImageDraw.Draw(im)
title='商务部研究院 即时零售报告'
for size in range(58,30,-2):
    font=ImageFont.truetype(str(font_path),size)
    b=draw.textbbox((0,0),title,font=font)
    if b[2]-b[0] <= 900: break
x=600-(b[2]-b[0])/2; y=96-(b[3]-b[1])/2
draw.text((x+2,y+3),title,font=font,fill=(82,8,6))
draw.text((x,y),title,font=font,fill=(255,255,255))
im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
print(out)
