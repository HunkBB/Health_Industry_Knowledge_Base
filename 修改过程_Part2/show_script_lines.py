from pathlib import Path
lines=Path('tmp/rewrite_comprehensive_analysis.py').read_text(encoding='utf-8').splitlines()
for i in range(190,230):
    print(f'{i+1}: {lines[i] if i < len(lines) else ""}')
