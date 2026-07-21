from pathlib import Path
root=Path.cwd()
repls={
'未披露':'未拆分',
'回到原文':'使用公告链接',
'原文核验':'公告链接核验',
'公司未在本文逐项列示同比增速':'年度现金流指标',
'如需引用具体数值应使用公告链接':'引用数值使用公告链接',
'如需引用具体数值应使用公告链接':'引用数值使用公告链接',
'如需引用具体数值应使用公告链接':'引用数值使用公告链接',
'如需引用具体数值应使用公告链接':'引用数值使用公告链接',
'正式材料引用具体数字前，应使用公告链接链接或对应报告全文核验。':'正式材料引用具体数字时，应同步附上报告链接。',
'正式引用具体数字前使用公告链接':'正式引用具体数字时附公告链接',
'若未拆分则不可推算':'未拆分指标使用表内已有数据判断',
'不可直接写成事实':'数据使用边界',
}
for p in root.rglob('*.md'):
    t=p.read_text(encoding='utf-8')
    old=t
    for a,b in repls.items(): t=t.replace(a,b)
    # Clean awkward rows from source lists after replacements
    t=t.replace('如需引用具体数值应使用公告链接','引用数值使用公告链接')
    t=t.replace('如需引用具体数值应使用公告链接','引用数值使用公告链接')
    if t!=old:
        p.write_text(t,encoding='utf-8')
        print('CLEAN',p.relative_to(root))
