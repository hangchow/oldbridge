#!/bin/bash
# 全部重新生成：先按名录原始数据生成，再算孔数/年代补充，再生成一次
cd "$(dirname "$0")"
B="build/gen.py huz/build.py jx/build.py sh/build.py sz/build.py jh/build.py"
C="绍兴市 宁波市 衢州市 台州市 温州市 丽水市 舟山市 无锡市 南京市 常州市 镇江市 扬州市 徐州市 连云港市 淮安市 盐城市 泰州市 南通市 宿迁市"
gen() { for f in $B; do python3 -I $f >/dev/null || echo "FAIL $f"; done; for c in $C; do python3 -I zj/build.py $c >/dev/null || echo "FAIL $c"; done; python3 -I build/zjsx.py >/dev/null || echo "FAIL zjsx"; }   # zjsx：按省文物局市县级文保名录补正
python3 -I build/official.py >/dev/null || echo "FAIL official"   # 政府原件里的桥
python3 -I build/unlisted.py >/dev/null || echo "FAIL unlisted"   # 老百晓集桥逐座核对结果
mkdir -p /tmp/ob_bak; mv build/cq_holes.json build/era_fill.json build/cq_len_fill.json /tmp/ob_bak/ 2>/dev/null
gen
python3 -I build/cqlink.py && python3 -I build/cqholes.py | tail -1 && python3 -I build/erafill.py | tail -1
gen
python3 -I build/cityreadme.py >/dev/null && python3 -I build/nowrap.py | tail -1
