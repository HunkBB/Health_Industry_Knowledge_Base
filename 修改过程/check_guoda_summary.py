from pathlib import Path
html=Path('行业信息库.html').read_text(encoding='utf-8',errors='ignore')
print('has new guoda', '它不是一个普通连锁药店样本' in html)
print('has validation', '有效上线门店数' in html)
