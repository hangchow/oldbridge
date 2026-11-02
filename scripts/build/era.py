# -*- coding: utf-8 -*-
# 把“时代”一列折算成始建年份，用来排“最早的桥”
import re
DY = [('五代', 907, 960), ('北宋', 960, 1127), ('南宋', 1127, 1279), ('宋', 960, 1279), ('唐', 618, 907), ('元', 1271, 1368), ('明', 1368, 1644), ('清', 1644, 1912), ('中华民国', 1912, 1949), ('民国', 1912, 1949)]
def year(era):
    # 返回 (年份, 是否确切年份)；查不到返回 None。取各分句里最早的一个
    if not era or era in ('—', '不详', '待定'): return None
    yrs = [int(y) for y in re.findall(r'(?<!\d)(\d{3,4})(?!\d)', era) if 500 < int(y) < 1950]
    best = None
    for cl in re.split(r'[，、；,;至—]|现桥|重建|重修', era):
        m = re.search(r'(?<!\d)(\d{3,4})(?!\d)', cl)
        if m and 500 < int(m.group(1)) < 1950: v = (int(m.group(1)), True)
        else:
            d = next(((a, b) for n, a, b in DY if n in cl), None)
            # 同一朝代已有确切年份的（如“元（至元二十六年，1289）”），不再按朝代起始年算
            if not d or any(d[0] <= y < d[1] for y in yrs): continue
            v = (d[0], False)
        if best is None or v[0] < best[0]: best = v
    return best
