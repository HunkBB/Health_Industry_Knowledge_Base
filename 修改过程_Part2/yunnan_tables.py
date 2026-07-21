from pathlib import Path
import pdfplumber, re
p=Path('tmp/pdf/yunnan2025.pdf')
with pdfplumber.open(p) as pdf:
 for pgno in [6,7]:
  page=pdf.pages[pgno]
  print('\nPAGE',pgno+1)
  tables=page.extract_tables()
  for ti,table in enumerate(tables):
   print('table',ti)
   for row in table:
    print(row)
   print('--')
