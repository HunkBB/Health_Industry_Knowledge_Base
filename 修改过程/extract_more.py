from pathlib import Path
import pdfplumber, urllib.request, re
urls={'yunnan2025':'https://static.cninfo.com.cn/finalpage/2026-04-01/1225067975.PDF','tcbj2025':'https://static.cninfo.com.cn/finalpage/2026-03-21/1225023314.PDF'}
for k,u in urls.items():
 p=Path('tmp/pdf')/(k+'.pdf')
 print('\n---',k)
 with pdfplumber.open(p) as pdf:
  for pgno in [6,7,8]:
   page=pdf.pages[pgno]
   text=page.extract_text(x_tolerance=1,y_tolerance=3) or ''
   print('\nPAGE',pgno+1)
   for line in text.splitlines()[:80]:
    if any(w in line for w in ['营业收入','归属于上市公司股东的净利润','扣除非','经营活动产生的现金流量净额','2025年','2024年']): print(line)
