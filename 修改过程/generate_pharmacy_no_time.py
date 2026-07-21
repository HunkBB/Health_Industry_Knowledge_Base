from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import hashlib, json, re, shutil
W,H=960,540
ROOT=Path('\u0030\u0032-\u8fde\u9501\u836f\u5e97'); OUT=Path('assets/doc_cards_web/pharmacy_batch_20260617_unique_v3_no_time'); PRE=Path('output/pharmacy_batch_20260617_unique_v3_no_time'); MAP=Path('assets/doc_cards_web/doc_image_web_map.json')
OUT.mkdir(parents=True,exist_ok=True); PRE.mkdir(parents=True,exist_ok=True)
LP,RP='\uff08','\uff09'; font_dir=Path(r'C:/Windows/Fonts')
def font(name,size):
 p=font_dir/name
 if not p.exists(): p=font_dir/'msyh.ttc'
 return ImageFont.truetype(str(p),size)
FB=lambda s:font('msyhbd.ttc',s)
C={'news':'\u65b0\u95fb','dynamic':'\u52a8\u6001','research':'\u7814\u62a5','finance':'\u8d22\u62a5','summary':'\u6458\u8981','data':'\u6570\u636e','index':'\u6307\u6807','member':'\u4f1a\u5458','insurance':'\u533b\u4fdd','region':'\u533a\u57df','compliance':'\u5408\u89c4','punish':'\u5904\u7f5a','reg':'\u76d1\u7ba1','storeopen':'\u5173\u5e97\u5f00\u5e97','eff':'\u576a\u6548','insight':'\u4e1a\u52a1\u6d1e\u5bdf','struct':'\u7ed3\u6784\u5316\u6458\u8981','guide':'\u9605\u8bfb\u6307\u5357','chain':'\u8fde\u9501\u836f\u5e97','official':'\u5b98\u65b9','core':'\u6838\u5fc3','biz':'\u7ecf\u8425','dashanlin':'\u5927\u53c2\u6797','yxt':'\u4e00\u5fc3\u5802','jzj':'\u5065\u4e4b\u4f73','gd':'\u56fd\u5927\u836f\u623f','gyyz':'\u56fd\u836f\u4e00\u81f4','sypm':'\u6f31\u7389\u5e73\u6c11','yfyf':'\u76ca\u4e30\u836f\u623f','lbx':'\u8001\u767e\u59d3'}
def clean_title(t):
 for token in [f'{LP}2025-2026{RP}','(2025-2026)','_2025-2026','2025-2026',f'{LP}{RP}','()','2026Q1','2025']:
  t=t.replace(token,'')
 t=re.sub(r'\s+',' ',t).strip(' ·-_()'+LP+RP)
 return C['chain'] if t=='_index' or not t else t
def split_title(t):
 t=clean_title(t)
 for sep in [' · ','／','/',':','：']:
  if sep in t and len(t)>13:
   a,b=t.split(sep,1); a=a.strip()+(' ·' if sep==' · ' else ''); b=b.strip(); return [a,b] if b else [a.rstrip(' ·')]
 if len(t)<=14: return [t]
 if len(t)<=22:
  cut=max(8,min(13,len(t)//2+3)); return [t[:cut],t[cut:]]
 return [t[:14],t[14:28]]
def entity(t,rel):
 for name,key in [(C['dashanlin'],'dashanlin'),(C['yxt'],'yxt'),(C['jzj'],'jzj'),(C['gd'],'gd'),(C['gyyz'],'gyyz'),(C['sypm'],'sypm'),(C['yfyf'],'yfyf'),(C['lbx'],'lbx')]:
  if name in t or name in rel: return key
 return 'chain'
def motif(t,rel):
 s=t+' '+rel
 if t=='_index': return 'index'
 if C['news'] in s or C['dynamic'] in s: return 'news'
 if C['research'] in s: return 'research'
 if C['guide'] in s: return 'guide'
 if 'O2O' in s: return 'o2o'
 if C['member'] in s: return 'member'
 if C['insurance'] in s: return 'insurance'
 if C['region'] in s: return 'region'
 if C['compliance'] in s or C['punish'] in s or C['reg'] in s: return 'compliance'
 if C['storeopen'] in s or C['eff'] in s: return 'store_efficiency'
 if 'DTP' in s: return 'dtp'
 if C['finance'] in s or C['biz'] in s or C['core'] in s or C['data'] in s or C['index'] in s: return 'finance'
 if C['insight'] in s: return 'insight'
 if C['struct'] in s: return 'summary'
 return 'general'
ENTITY_COLORS={'dashanlin':('#168060','#164b63','#ef6b6b','#57b9e8'),'yxt':('#1b7f66','#315f8f','#f0705d','#66c5c8'),'jzj':('#247c53','#1a5163','#ee7b5f','#72c0e8'),'gd':('#0f7f73','#173f69','#e96878','#56b7ef'),'gyyz':('#0f7f73','#173f69','#e96878','#56b7ef'),'sypm':('#19846b','#3c617d','#e86d65','#5ebbd6'),'yfyf':('#2a8b5e','#234e73','#f17a62','#62c4da'),'lbx':('#137d64','#285b76','#e96f75','#67bedc'),'chain':('#168060','#164b63','#ef6b6b','#57b9e8')}
def shadow(img,box,rad=28,off=(0,14),blur=18,alpha=28):
 layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer); x0,y0,x1,y1=box; d.rounded_rectangle((x0+off[0],y0+off[1],x1+off[0],y1+off[1]),radius=rad,fill=(16,83,64,alpha)); img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
def store(d,x,y,teal,navy,red,blue,var,style='front'):
 line='#b9d9cf'; cream='#fff3e7'; green='#5fb08e'; yellow='#f2bf61'; d.rounded_rectangle((x+12,y+48,x+388,y+238),radius=18,fill='#fbfffd',outline=line,width=2)
 if style=='wide': d.polygon([(x+20,y+10),(x+382,y+10),(x+404,y+54),(x-2,y+54)],fill=navy)
 elif style=='clinic': d.rounded_rectangle((x+34,y+8,x+370,y+56),radius=16,fill=navy)
 else: d.polygon([(x+34,y+8),(x+370,y+8),(x+402,y+56),(x,y+56)],fill=navy)
 d.rectangle((x+34,y,x+370,y+12),fill='#4e7890'); d.rounded_rectangle((x+172,y+18,x+228,y+45),radius=10,fill=(255,255,255,238)); d.rectangle((x+194,y+23,x+204,y+40),fill=teal); d.rectangle((x+186,y+29,x+212,y+36),fill=teal)
 for i in range(10):
  xx=x+4+i*40; fill=red if (i+var)%2==0 else cream; d.polygon([(xx,y+56),(xx+34,y+56),(xx+24,y+90),(xx-7,y+90)],fill=fill); d.ellipse((xx-7,y+80,xx+24,y+100),fill=fill)
 d.rectangle((x,y+54,x+402,y+63),fill='#86cdda'); d.rectangle((x+24,y+98,x+376,y+238),fill='#fbfffd'); d.line((x+24,y+238,x+376,y+238),fill='#235c70',width=7)
 d.rounded_rectangle((x+48,y+114,x+188,y+192),radius=8,fill='#dcf2f5',outline='#22566c',width=5); d.line((x+118,y+114,x+118,y+192),fill='#22566c',width=4); d.line((x+52,y+152,x+184,y+152),fill='#9fc6c7',width=3)
 colors=[teal,green,yellow,red,blue]
 for row,yy in enumerate([y+125,y+163]):
  for col,xx in enumerate(range(x+62,x+172,24)): d.rounded_rectangle((xx,yy,xx+15,yy+16),radius=3,fill=colors[(row+col+var)%5])
 d.rounded_rectangle((x+238,y+112,x+320,y+238),radius=8,fill='#8fd0e8',outline='#22566c',width=5); d.rectangle((x+244,y+168,x+314,y+174),fill='#22566c'); d.rounded_rectangle((x+336,y+124,x+380,y+168),radius=5,fill=red); d.rectangle((x+354,y+132,x+362,y+160),fill='white'); d.rectangle((x+343,y+142,x+373,y+150),fill='white')
def bottle(d,x,y,w,h,body,cap,cross=False):
 d.rounded_rectangle((x,y+16,x+w,y+h),radius=9,fill=body); d.rounded_rectangle((int(x+w*.22),y,int(x+w*.78),y+22),radius=8,fill=cap); d.rectangle((x+8,y+38,x+w-8,y+70),fill='#fff8e8')
 if cross: d.ellipse((x+w/2-14,y+44,x+w/2+14,y+70),fill='white'); d.rectangle((x+w/2-4,y+49,x+w/2+4,y+66),fill='#ef6b6b'); d.rectangle((x+w/2-12,y+56,x+w/2+12,y+63),fill='#ef6b6b')
 else: d.arc((x+17,y+43,x+w-14,y+77),190,350,fill='#67422e',width=4)
def chart(d,x,y,teal,red):
 line='#b9d9cf'; green='#7fc4a6'; yellow='#f2bf61'; d.rounded_rectangle((x,y,x+126,y+116),radius=18,fill=(255,255,255,232),outline=line,width=2)
 for i,h in enumerate([38,70,52,88]): bx=x+24+i*22; d.rounded_rectangle((bx,y+92-h,bx+13,y+92),radius=4,fill=[teal,green,yellow,red][i])
 d.line((x+18,y+96,x+106,y+96),fill='#9fc6c7',width=3)
def news_cards(d,x,y,teal):
 line='#b9d9cf'; green='#7fc4a6'
 for i,(dx,dy) in enumerate([(0,0),(48,36),(26,78)]): d.rounded_rectangle((x+dx,y+dy,x+dx+88,y+dy+54),radius=12,fill=(255,255,255,232),outline=line,width=2); d.rounded_rectangle((x+dx+12,y+dy+12,x+dx+52,y+dy+20),radius=4,fill=teal if i==0 else green); d.rounded_rectangle((x+dx+12,y+dy+30,x+dx+70,y+dy+37),radius=3,fill='#d5e9e2')
def report(d,x,y,teal):
 line='#b9d9cf'; green='#7fc4a6'
 for i in range(3): d.rounded_rectangle((x+i*18,y+i*14,x+106+i*18,y+126+i*14),radius=10,fill=(255,255,255,234),outline=line,width=2); d.rectangle((x+16+i*18,y+18+i*14,x+84+i*18,y+27+i*14),fill=teal if i==2 else green); d.rectangle((x+16+i*18,y+44+i*14,x+72+i*18,y+52+i*14),fill='#d5e9e2'); d.rectangle((x+16+i*18,y+64+i*14,x+88+i*18,y+72+i*14),fill='#e6f2ee')
def phone(d,x,y,teal):
 line='#b9d9cf'; green='#7fc4a6'; yellow='#f2bf61'; d.rounded_rectangle((x,y,x+100,y+140),radius=22,fill=(255,255,255,235),outline=line,width=3); d.rounded_rectangle((x+16,y+20,x+84,y+48),radius=9,fill=teal)
 for yy,c in [(76,teal),(104,yellow),(126,green)]: d.ellipse((x+20,y+yy-7,x+34,y+yy+7),fill=c); d.rounded_rectangle((x+48,y+yy-5,x+82,y+yy+4),radius=3,fill='#d5e9e2')
def member(d,x,y,teal):
 line='#b9d9cf'; yellow='#f2bf61'; green='#7fc4a6'; d.rounded_rectangle((x,y,x+132,y+96),radius=18,fill=(255,255,255,235),outline=line,width=2)
 for i,(cx,cy) in enumerate([(x+38,y+36),(x+74,y+32),(x+96,y+60)]): d.ellipse((cx-12,cy-12,cx+12,cy+12),fill=[teal,green,yellow][i]); d.rounded_rectangle((cx-20,cy+16,cx+20,cy+30),radius=8,fill='#d5e9e2')
def map_icon(d,x,y,teal):
 line='#b9d9cf'; green='#7fc4a6'; red='#ef6b6b'; d.rounded_rectangle((x,y,x+138,y+112),radius=18,fill=(255,255,255,235),outline=line,width=2); pts=[(x+34,y+76),(x+62,y+42),(x+102,y+70),(x+82,y+92)]; d.line(pts,fill='#9fc6c7',width=5,joint='curve')
 for i,(px,py) in enumerate(pts): d.ellipse((px-8,py-8,px+8,py+8),fill=[teal,green,red,teal][i])
def shield(d,x,y,teal):
 line='#b9d9cf'; d.rounded_rectangle((x,y,x+120,y+120),radius=18,fill=(255,255,255,235),outline=line,width=2); d.polygon([(x+60,y+24),(x+92,y+38),(x+84,y+82),(x+60,y+100),(x+36,y+82),(x+28,y+38)],fill='#dff2f5',outline=teal); d.rectangle((x+55,y+48,x+65,y+78),fill=teal); d.rectangle((x+44,y+59,x+76,y+68),fill=teal)
def dtp_icon(d,x,y,teal):
 line='#b9d9cf'; green='#7fc4a6'; d.rounded_rectangle((x,y,x+128,y+124),radius=18,fill=(255,255,255,235),outline=line,width=2); d.ellipse((x+32,y+24,x+94,y+86),fill='#dff2f5',outline=teal,width=4); d.rectangle((x+58,y+38,x+70,y+72),fill=teal); d.rectangle((x+46,y+50,x+82,y+62),fill=teal); d.rounded_rectangle((x+34,y+96,x+96,y+108),radius=6,fill=green)
def store_grid(d,x,y,teal):
 green='#7fc4a6'; red='#ef6b6b'; yellow='#f2bf61'
 for r in range(2):
  for c in range(3): xx=x+c*42; yy=y+r*42; d.rounded_rectangle((xx,yy,xx+30,yy+30),radius=7,fill=[teal,green,red,yellow][(r+c)%4])
 d.line((x-8,y+80,x+126,y+80),fill='#9fc6c7',width=4)
def efficiency(d,x,y,teal):
 line='#b9d9cf'; red='#ef6b6b'; green='#7fc4a6'; d.rounded_rectangle((x,y,x+130,y+106),radius=18,fill=(255,255,255,235),outline=line,width=2)
 for xx,h,c in [(x+24,50,teal),(x+58,72,green),(x+92,36,red)]: d.rectangle((xx,y+84-h,xx+18,y+84),fill=c)
 d.line((x+20,y+88,x+112,y+88),fill='#9fc6c7',width=3)
def guide(d,x,y,teal):
 line='#b9d9cf'; green='#7fc4a6'; d.rounded_rectangle((x,y,x+122,y+112),radius=16,fill=(255,255,255,235),outline=line,width=2); d.rectangle((x+26,y+18,x+96,y+28),fill=teal)
 for i in range(4): d.rectangle((x+24,y+44+i*14,x+98,y+50+i*14),fill='#d5e9e2')
 d.ellipse((x+84,y+76,x+106,y+98),outline=green,width=4)
def draw_motif(d,m,x,y,teal,red,blue):
 if m=='news': news_cards(d,x,y,teal)
 elif m=='research': report(d,x,y,teal)
 elif m=='finance': chart(d,x,y,teal,red)
 elif m=='o2o': phone(d,x,y,teal)
 elif m=='member': member(d,x,y,teal)
 elif m in ['insurance','compliance']: shield(d,x,y,teal)
 elif m=='region': map_icon(d,x,y,teal)
 elif m=='store_efficiency': efficiency(d,x,y,teal)
 elif m=='dtp': dtp_icon(d,x,y,teal)
 elif m=='guide': guide(d,x,y,teal)
 elif m=='index': store_grid(d,x,y,teal)
 else: chart(d,x,y,teal,red)
def draw_left(d,m,teal,red,blue):
 if m in ['finance','guide']: chart(d,102,336,teal,red)
 elif m=='o2o': phone(d,106,320,teal)
 elif m=='member': member(d,104,350,teal)
 elif m in ['region','index']: store_grid(d,108,342,teal)
 elif m=='store_efficiency': efficiency(d,100,342,teal)
 elif m in ['compliance','insurance']: shield(d,104,326,teal)
 elif m=='dtp': dtp_icon(d,104,326,teal)
 else: bottle(d,114,348,70,104,'#7ecf12','#8ae600'); bottle(d,176,320,78,126,blue,'#854735')
def draw(title,rel,idx):
 ent=entity(title,rel); teal,navy,red,blue=ENTITY_COLORS[ent]; m=motif(title,rel); img=Image.new('RGB',(W,H),'#f1faf6'); d=ImageDraw.Draw(img)
 for x in range(0,W+1,80): d.line((x,0,x,H),fill='#d4ebe3')
 for y in range(0,H+1,80): d.line((0,y,W,y),fill='#d4ebe3')
 for cx,cy,r,c in [(110+(idx%6)*12,154+(idx%3)*8,110,'#dff1eb'),(826-(idx%4)*10,380,150,'#e5f4ee'),(450,470-(idx%5)*4,124,'#e8f6f1'),(770,114+(idx%4)*8,88,'#e1f1eb')]: d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=c)
 img=img.convert('RGBA'); d=ImageDraw.Draw(img); panel=(56,56,904,184); shadow(img,panel,34,(0,12),18,28); d=ImageDraw.Draw(img); d.rounded_rectangle(panel,radius=34,fill=(255,255,255,247),outline='#b9d9cf',width=2)
 lines=split_title(title)
 if len(lines)==1:
  size=50 if len(lines[0])<=12 else 43 if len(lines[0])<=18 else 36; d.text((100,88),lines[0],font=FB(size),fill=teal)
 else:
  d.text((100,78),lines[0],font=FB(40 if len(lines[0])<=12 else 34),fill=teal); d.text((100,124),lines[1],font=FB(31 if len(lines[1])<=14 else 25),fill=teal)
 d.rounded_rectangle((104,153,286,166),radius=7,fill=teal); d.rounded_rectangle((306,153,392,166),radius=7,fill='#7fc4a6')
 style='clinic' if m in ['dtp','insurance','compliance'] else 'wide' if m in ['region','store_efficiency','index'] else 'front'; store(d,280+(idx%3-1)*10,202+(idx%2)*6,teal,navy,red,blue,idx,style)
 draw_left(d,m,teal,red,blue); draw_motif(d,m,746,238,teal,red,blue)
 if m not in ['o2o','member','finance','region','store_efficiency']: bottle(d,724,356,62,92,'#ff5b1f','#fff1c5',True)
 d.rounded_rectangle((126,506,834,516),radius=5,fill=teal); return img.convert('RGB')
items=[]
for p in sorted(ROOT.rglob('*.md')):
 rel=p.as_posix(); text=p.read_text(encoding='utf-8'); mt=re.search(r'^#\s+(.+)$',text,re.M); title=mt.group(1).strip() if mt else p.stem; did='doc-'+hashlib.md5(rel.encode('utf-8')).hexdigest()[:12]; items.append((did,rel,title,motif(title,rel)))
if MAP.exists():
 b=MAP.with_name('doc_image_web_map.before-pharmacy-no-time-20260617.json')
 if not b.exists(): shutil.copy2(MAP,b)
 data=json.loads(MAP.read_text(encoding='utf-8-sig'))
else: data={}
for idx,(did,rel,title,m) in enumerate(items):
 img=draw(title,rel,idx); out=OUT/f'{did}.png'; img.save(out,'PNG',optimize=True); data[did]=out.as_posix()
 if idx<14 or m in ['o2o','member','insurance','region','compliance','store_efficiency','dtp']: img.save(PRE/f'{idx:02d}-{m}-{did}.png','PNG',optimize=True)
MAP.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('generated_no_time',len(items),'previews',len(list(PRE.glob('*.png'))))
