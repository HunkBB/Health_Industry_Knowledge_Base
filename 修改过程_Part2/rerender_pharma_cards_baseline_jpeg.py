from pathlib import Path
import json, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
root=Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
template=Image.open(root/'output/imagegen/pharma-blue-yunnan-baiyao-25-26-center-pills.png').convert('RGB')
targets=json.loads((root/'tmp/pharma_card_targets.json').read_text(encoding='utf-8'))
map_path=root/'assets/doc_cards_web/doc_image_web_map.json'
image_map=json.loads(map_path.read_text(encoding='utf-8-sig'))
font_path=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
def short_title(title):
    t=title.replace(' · ',' ').replace('（2025-2026）','').replace('(2025-2026)','')
    t=t.replace('2025-2026','25-26年').replace('2025—2026','25-26年')
    t=t.replace('财报与渠道机会摘要','财报与渠道机会').replace('_',' ')
    return re.sub(r'\s+',' ',t).strip()
def fit_font(draw,text,max_width,max_height):
    for size in range(78,34,-2):
        font=ImageFont.truetype(str(font_path),size)
        b=draw.textbbox((0,0),text,font=font)
        if b[2]-b[0]<=max_width and b[3]-b[1]<=max_height: return font
    return ImageFont.truetype(str(font_path),34)
def render(title):
    im=template.copy().convert('RGBA')
    x0,y0,x1,y1=158,58,1378,231
    shadow=Image.new('RGBA',im.size,(0,0,0,0)); sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0-5,y0+5,x1+5,y1+10),radius=30,fill=(0,32,96,110)); shadow=shadow.filter(ImageFilter.GaussianBlur(9))
    im=Image.alpha_composite(im,shadow)
    card=Image.new('RGBA',im.size,(0,0,0,0)); cd=ImageDraw.Draw(card)
    cd.rounded_rectangle((x0,y0,x1,y1),radius=27,fill=(0,49,137,255),outline=(190,236,255,240),width=4)
    cd.rounded_rectangle((x0+8,y0+8,x1-8,y1-8),radius=21,outline=(88,190,255,150),width=2)
    im=Image.alpha_composite(im,card)
    glow=Image.new('RGBA',im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.rounded_rectangle((x0+12,y0+12,x1-12,y0+54),radius=17,fill=(60,160,235,70))
    im=Image.alpha_composite(im,glow).convert('RGB')
    draw=ImageDraw.Draw(im); text=short_title(title); font=fit_font(draw,text,x1-x0-150,y1-y0-62)
    b=draw.textbbox((0,0),text,font=font); tw,th=b[2]-b[0],b[3]-b[1]
    tx=x0+(x1-x0-tw)/2; ty=y0+(y1-y0-th)/2-5
    draw.text((tx+3,ty+4),text,font=font,fill=(0,18,70)); draw.text((tx,ty),text,font=font,fill=(255,255,255))
    return im
for item in targets:
    doc_id=item['doc_id']; image_rel=item.get('image') or f'assets/doc_cards_web/{doc_id}.jpg'; image_map[doc_id]=image_rel
    out=root/image_rel; out.parent.mkdir(parents=True,exist_ok=True)
    im=render(item['title'])
    # Non-progressive baseline JPEG for broad viewer compatibility.
    im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
map_path.write_text(json.dumps(image_map,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('baseline jpeg rewritten',len(targets))
