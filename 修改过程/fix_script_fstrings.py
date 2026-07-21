from pathlib import Path
p=Path('tmp/rewrite_comprehensive_analysis.py')
lines=p.read_text(encoding='utf-8').splitlines()
out=[]
i=0
while i < len(lines):
    if i+1 < len(lines) and lines[i].strip().startswith("text += f'| {a} | {b} | {c} |") and lines[i+1].strip()=="'":
        out.append("        text += f'| {a} | {b} | {c} |\\n'")
        i += 2
    elif i+1 < len(lines) and lines[i].strip().startswith("text += f'| {a} | {b} |") and lines[i+1].strip()=="'":
        out.append("        text += f'| {a} | {b} |\\n'")
        i += 2
    else:
        out.append(lines[i])
        i += 1
p.write_text('\n'.join(out)+'\n', encoding='utf-8')
print('fixed fstrings')
