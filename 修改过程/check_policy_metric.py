from pathlib import Path
html=Path('行业信息库.html').read_text(encoding='utf-8',errors='ignore')
print('has target', '平台竞争指标表_流量供给履约医保处方药师' in html)
print('has policy flow', '流量、供给和履约指标应与处方、医保、药师和合规指标一起看' in html)
