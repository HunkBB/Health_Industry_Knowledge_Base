from pathlib import Path
import pdfplumber
p=Path('tmp/pdf/yunnan_q1_2026.pdf')
with pdfplumber.open(p) as pdf:
 for i,page in enumerate(pdf.pages[:8],1):
  tx=page.extract_text() or ''
  print('\nPAGE',i)
  for line in tx.splitlines():
   if any(w in line for w in ['营业收入','归属于上市公司股东','经营活动产生','基本每股收益']): print(line)
  tables=page.extract_tables()
  for table in tables[:1]:
   for row in table[:8]: print(row)
