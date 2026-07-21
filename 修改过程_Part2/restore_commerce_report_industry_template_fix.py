from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
doc_id = 'doc-a0175105fac2'
out = root / 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
out.parent.mkdir(parents=True, exist_ok=True)
backup = root / 'assets/doc_cards_web/backup_before_restore_commerce_report_20260617'
backup.mkdir(parents=True, exist_ok=True)
old = root / 'assets/doc_cards_web/doc-a0175105fac2.jpg'
for p in [old, out]:
    if p.exists():
        bak = backup / p.name
        if not bak.exists(): bak.write_bytes(p.read_bytes())
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
W,H = 1200,800
# warm desk background similar to industry report covers
im = Image.new('RGB',(W,H),(236,231,220)).convert('RGBA')
base = Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(base)
# subtle table gradients / shadows
for i in range(9):
    alpha = 24 - i*2
    d.ellipse((120+i*6, 40+i*5, 1080-i*8, 780-i*4), fill=(255,255,255,max(0,alpha)))
# report shadow
shadow = Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
sd.polygon([(260,170),(930,115),(980,690),(300,740)], fill=(0,0,0,62))
shadow = shadow.filter(ImageFilter.GaussianBlur(22))
im = Image.alpha_composite(im, shadow)
# report cover
report = Image.new('RGBA',(W,H),(0,0,0,0)); rd=ImageDraw.Draw(report)
cover=[(245,125),(900,90),(965,660),(300,715)]
rd.polygon(cover, fill=(248,247,242,255), outline=(211,207,199,255))
# spine / edge
rd.polygon([(245,125),(300,715),(285,704),(235,136)], fill=(232,229,221,255))
rd.line([(262,145),(315,696)], fill=(216,212,204,255), width=3)
# subtle red network arcs on lower cover
for off in [0,45,90,135]:
    rd.arc((265+off,445-off//3,900+off,840+off//4), 205, 335, fill=(218,41,28,95), width=2)
for x,y,r in [(430,590,8),(570,535,6),(700,575,7),(815,510,6),(880,612,9),(505,650,7)]:
    rd.ellipse((x-r,y-r,x+r,y+r), fill=(218,41,28,165))
    for x2,y2 in [(570,535),(700,575),(815,510)]:
        if abs(x-x2)+abs(y-y2) < 260:
            rd.line((x,y,x2,y2), fill=(218,41,28,55), width=1)
# dotted wave
for i in range(75):
    x = 430 + i*6
    y = 640 + int(18*((i%18)/18))
    rd.ellipse((x,y,x+2,y+2), fill=(218,41,28,45))
im = Image.alpha_composite(im, report).convert('RGB')
draw=ImageDraw.Draw(im)
# title on cover, perspective-ish horizontal enough for readability
title='商务部研究院\n即时零售行业发展报告摘要'
for size in range(48,30,-2):
    font=ImageFont.truetype(str(font_path), size)
    lines=title.split('\n')
    widths=[draw.textbbox((0,0),line,font=font)[2] for line in lines]
    if max(widths) <= 560: break
x=455; y=270
for idx,line in enumerate(lines):
    draw.text((x+2,y+idx*(size+13)+2), line, font=font, fill=(90,90,86))
    draw.text((x,y+idx*(size+13)), line, font=font, fill=(36,38,40))
# small subtitle / tag
small=ImageFont.truetype(str(font_path), 24)
draw.text((460,410), '行业报告 · 渠道结构 · 近场履约', font=small, fill=(130,126,118))
# box and pen like neighboring template
shape=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shape)
sd.polygon([(70,105),(260,70),(360,120),(165,158)], fill=(245,244,239,255), outline=(210,206,198,255))
sd.polygon([(165,158),(360,120),(360,190),(166,228)], fill=(229,226,218,255), outline=(205,201,194,255))
sd.polygon([(70,105),(165,158),(166,228),(72,170)], fill=(236,233,225,255), outline=(205,201,194,255))
sd.line((85,156,165,205), fill=(218,41,28,150), width=2)
# pen
sd.line((1045,350,1160,610), fill=(72,72,72,255), width=16)
sd.line((1058,343,1173,603), fill=(196,196,188,255), width=4)
sd.polygon([(1155,608),(1180,648),(1166,602)], fill=(110,110,105,255))
im=Image.alpha_composite(im.convert('RGBA'), shape).convert('RGB')
im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
# update map to same folder as industry block
mp_path = root / 'assets/doc_cards_web/doc_image_web_map.json'
mp = json.loads(mp_path.read_text(encoding='utf-8-sig'))
mp[doc_id] = 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
mp_path.write_text(json.dumps(mp, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(out)

