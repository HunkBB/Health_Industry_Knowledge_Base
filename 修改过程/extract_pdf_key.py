from pathlib import Path
import urllib.request, re
import pdfplumber
urls={
'yunnan2025':'https://static.cninfo.com.cn/finalpage/2026-04-01/1225067975.PDF',
'tcbj2025':'https://static.cninfo.com.cn/finalpage/2026-03-21/1225023314.PDF',
'hr39q1':'https://static.cninfo.com.cn/finalpage/2026-04-25/1225178865.PDF',
}
tmp=Path('tmp/pdf'); tmp.mkdir(parents=True,exist_ok=True)
for k,u in urls.items():
    path=tmp/(k+'.pdf')
    if not path.exists(): path.write_bytes(urllib.request.urlopen(u,timeout=30).read())
    print('---',k,path.stat().st_size)
    text=''
    with pdfplumber.open(path) as pdf:
        for i,p in enumerate(pdf.pages[:20]):
            tx=p.extract_text() or ''
            if any(w in tx for w in ['营业收入','归属于上市公司股东','经营活动产生的现金流量净额','主要会计数据']):
                print('PAGE',i+1)
                for line in tx.splitlines():
                    if any(w in line for w in ['营业收入','归属于上市公司股东','经营活动产生的现金流量净额','基本每股收益']):
                        print(line)
