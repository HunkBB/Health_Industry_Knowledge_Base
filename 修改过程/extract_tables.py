from pathlib import Path
import pdfplumber
for k in ['yunnan2025','tcbj2025']:
 p=Path('tmp/pdf')/(k+'.pdf')
 print('\n---',k)
 with pdfplumber.open(p) as pdf:
  for pgno,page in enumerate(pdf.pages[:10],1):
   tables=page.extract_tables()
   if tables:
    print('PAGE',pgno,'tables',len(tables))
    for table in tables[:2]:
     for row in table[:8]: print(row)
     print('--')
