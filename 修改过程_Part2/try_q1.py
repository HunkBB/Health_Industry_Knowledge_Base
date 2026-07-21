from pathlib import Path
import urllib.request, pdfplumber
urls={
'yunnan_q1_2026':'https://static.cninfo.com.cn/finalpage/2026-04-25/1225178841.PDF',
'tcbj_q1_2026':'https://static.cninfo.com.cn/finalpage/2026-04-25/1225178878.PDF',
}
# URLs may be wrong; try current known CNINFO by search not available here? download and report.
for k,u in urls.items():
 p=Path('tmp/pdf')/(k+'.pdf')
 try:
  p.write_bytes(urllib.request.urlopen(u,timeout=20).read())
  print('download',k,p.stat().st_size,p.read_bytes()[:4])
  with pdfplumber.open(p) as pdf:
   print('pages',len(pdf.pages))
   for i,page in enumerate(pdf.pages[:5],1):
    tx=page.extract_text() or ''
    if '营业收入' in tx:
     print('PAGE',i)
     for line in tx.splitlines():
      if any(w in line for w in ['营业收入','归属于上市公司股东','经营活动产生']): print(line)
 except Exception as e: print('ERR',k,e)
