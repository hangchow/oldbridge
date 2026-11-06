# -*- coding: utf-8 -*-
"""将浙江三普桥梁图录中的待核条目并入各市结构化数据。"""
import json
from pathlib import Path

S = Path(__file__).resolve().parents[1]
data = json.loads((S / 'build/zhejiang_p3_bridges.json').read_text())
by_city = {}
for record in data['records']:
    by_city.setdefault(record['key'], []).append(record)

for key, records in by_city.items():
    path = S / key / 'rows.json'
    rows = json.loads(path.read_text())
    # 重复生成时更新本来源的旧记录；其他来源的同名记录优先保留。
    rows = [r for r in rows if r.get('catalog_source') != 'zhejiang_p3_bridges']
    added = 0
    for item in records:
        if any(r.get('dist') == item['dist'] and r.get('name') == item['name'] for r in rows):
            continue
        rows.append(dict(dist=item['dist'], town='乡镇待核', name=item['name'], era='—', loc='—',
                         level='尚未定级（待核实）', doc='—', src=data['source'],
                         struct=item['struct'], len='—',
                         note=f"据《{data['book']}》目录“{item['title']}”收录；乡镇、年代、文保等级、现状及与同名桥是否相同均待核",
                         catalog_source='zhejiang_p3_bridges'))
        added += 1
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=0) + '\n')
    print(f'{key}: {added}')
