from pathlib import Path
import json
from PIL import Image, ImageDraw
root = Path(r'D:\xujianxiang.7\Documents\JD\ME\data\ee\xujianxiang.7\file\source-industry-info-library')
ref = root / 'assets/doc_cards_web/industry_20260617/doc-82874537ac28.jpg'
out = root / 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
backup = root / 'assets/doc_cards_web/backup_before_commerce_report_keep_bottom_only_20260617'
backup.mkdir(parents=True, exist_ok=True)
if out.exists():
    bak = backup / out.name
    if not bak.exists(): bak.write_bytes(out.read_bytes())
im = Image.open(ref).convert('RGBA')
# Remove the book title area cleanly by repainting it with paper color only; keep bottom red network motif.
patch = Image.new('RGBA', im.size, (0,0,0,0))
d = ImageDraw.Draw(patch)
# Broad paper-colored polygon over title area. No text, no sticker/label.
d.polygon([(515,220),(1215,285),(1200,430),(500,365)], fill=(247,247,244,255))
# Very subtle grain lines matching paper, avoiding pasted-card feel.
d.line([(520,365),(1195,428)], fill=(241,241,238,100), width=2)
d.line([(530,226),(1210,288)], fill=(250,250,247,80), width=1)
im = Image.alpha_composite(im, patch).convert('RGB')
im.save(out, format='JPEG', quality=92, subsampling=0, progressive=False, optimize=False)
mp_path = root / 'assets/doc_cards_web/doc_image_web_map.json'
mp = json.loads(mp_path.read_text(encoding='utf-8-sig'))
mp['doc-a0175105fac2'] = 'assets/doc_cards_web/industry_20260617/doc-a0175105fac2.jpg'
mp_path.write_text(json.dumps(mp, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(out)
