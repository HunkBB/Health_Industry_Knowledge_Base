from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
out = root / 'assets/doc_cards_web/policy_20260617/doc-0800e61de0a4-policy.jpg'
out.parent.mkdir(parents=True, exist_ok=True)
font_path = next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'), Path(r'C:\Windows\Fonts\msyh.ttc'), Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
W,H=1024,640
im=Image.new('RGB',(W,H),(246,249,252)).convert('RGBA')
layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
# soft policy-blue background
for box,col in [((-120,80,220,450),(53,111,165,28)),((790,60,1130,460),(53,111,165,24)),((420,210,720,520),(180,205,220,36))]:
    d.ellipse(box, fill=col)
# shadow
shadow=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
sd.rounded_rectangle((185,120,690,515), radius=18, fill=(0,40,85,42)); shadow=shadow.filter(ImageFilter.GaussianBlur(18)); im=Image.alpha_composite(im,shadow)
# document card
card=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(card)
cd.rounded_rectangle((170,100,675,500), radius=18, fill=(255,255,255,255), outline=(196,214,226,255), width=2)
cd.rounded_rectangle((170,100,675,168), radius=18, fill=(43,96,148,255))
cd.rectangle((170,138,675,168), fill=(43,96,148,255))
# title and lines
font_big=ImageFont.truetype(str(font_path), 42)
cd.text((215,122),'医保政策汇总',font=font_big,fill=(255,255,255))
for i,w in enumerate([360,315,385,340,285]):
    y=220+i*46
    cd.rounded_rectangle((230,y,230+w,y+8), radius=4, fill=(126,151,164,220))
# official stamp / shield
cd.ellipse((555,405,625,475), outline=(174,28,45,255), width=8)
cd.line((560,440,620,440), fill=(174,28,45,255), width=7)
# side compliance card
cd.rounded_rectangle((735,270,918,405), radius=16, fill=(255,255,255,245), outline=(184,207,222,255), width=3)
cd.rectangle((755,294,898,332), fill=(43,96,148,255))
font_mid=ImageFont.truetype(str(font_path), 30)
cd.text((766,352),'政策监管',font=font_mid,fill=(55,70,80))
cd.line((860,348,860,386), fill=(43,96,148,255), width=8)
cd.line((842,367,878,367), fill=(43,96,148,255), width=8)
# small医保 card
cd.rounded_rectangle((745,430,930,505), radius=14, fill=(255,255,255,225), outline=(184,207,222,230), width=2)
font_small=ImageFont.truetype(str(font_path), 24)
cd.text((770,452),'医保支付',font=font_small,fill=(43,96,148))
cd.rectangle((770,485,900,492), fill=(126,151,164,120))
im=Image.alpha_composite(im,card).convert('RGB')
im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
print(out)
