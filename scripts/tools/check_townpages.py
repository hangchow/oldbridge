"""检查25市三级目录、逐桥位置、区县索引、媒体绑定及本地链接。"""
import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/build'))
from townpages import CITIES
LINK = re.compile(r'\]\((<[^>]+>|(?:[^()]|\([^()]*\))*)\)')
errors = []


def cells(line):
    return [re.sub(r'</?nobr>', '', v.strip()) for v in line.strip('|').split('|')]


def bridge_name(value):
    value = re.sub(r' \[\?\]\(.*?\)$', '', value)
    return re.sub(r'^\[(.*?)\]\(.*\)$', r'\1', value)


master_total = 0
for city, key in CITIES.items():
    filename = 'all_rows.json' if city == '杭州市' else 'rows.json'
    rows = json.loads((ROOT / 'scripts' / key / filename).read_text())
    if city == '杭州市':
        rows = [r for r in rows if (r['dist'], r['town']) != ('西湖区', '三墩镇')]
        manual = ROOT / '杭州市/西湖区/三墩镇/三墩镇古桥.md'
        for line in manual.read_text().splitlines():
            c = cells(line) if line.startswith('|') else []
            if len(c) == 9 and c[0].isdigit():
                rows.append(dict(dist='西湖区', town='三墩镇', name=bridge_name(c[1]), loc=c[5]))
    expected = collections.Counter((r['dist'], r['town'] if r['town'] not in ('', '—') else '乡镇待核', r['name'], (r.get('loc') or '—').strip()) for r in rows)
    actual = collections.Counter()
    pages = list((ROOT / city).glob('*/*/*古桥.md'))
    for page in pages:
        for line in page.read_text().splitlines():
            c = cells(line) if line.startswith('|') else []
            if len(c) != 9 or not c[0].isdigit():
                continue
            actual[(page.parent.parent.name, page.parent.name, bridge_name(c[1]), c[5])] += 1
    if actual != expected:
        errors.append((city, '桥梁/位置不一致', expected - actual, actual - expected))
    for page in (ROOT / city).rglob('*.md'):
        for match in LINK.finditer(page.read_text()):
            link = match.group(1).strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:|^#|^/', link):
                continue
            if not (page.parent / unquote(link.split('#')[0])).resolve().exists():
                errors.append((page.relative_to(ROOT), '失效链接', link))
    for page in (ROOT / city).glob('*/*古桥.md'):
        if any('## ' + name in page.read_text() for name in ['说明', '来源', '图片来源']):
            errors.append((page.relative_to(ROOT), '区县仍有明细说明'))
    expected_count = len(rows) - (2 if city == '杭州市' else 0)  # 两座跨区桥在乡镇各列两次，全市各计一次。
    master_total += expected_count
    if f'共收录 {expected_count} 座桥' not in (ROOT / city / 'README.md').read_text():
        errors.append((city, '市级总数不一致', expected_count))
    print(f'{city}：{expected_count}座桥，{len(pages)}个乡镇明细页')
root_total = next(cells(line)[-1] for line in (ROOT / 'README.md').read_text().splitlines() if '**合计**' in line)
if int(root_total) != master_total:
    errors.append(('根目录总计不一致', root_total, master_total))
manifest = json.loads((ROOT / 'scripts/build/town_assets.json').read_text())
for before, after in manifest.items():
    if not (ROOT / after).is_file():
        errors.append(('迁移图片缺失', before, after))
page = ROOT / '嘉兴市/桐乡市/乌镇镇/乌镇镇古桥.md'
for line in page.read_text().splitlines():
    if line.startswith('|') and '杨园村费堡里组' in line and ('jxql153' in line or '通济桥1.jpg' in line):
        errors.append(('杨园村通济桥误挂西栅媒体',))
assert not errors, '\n'.join(map(str, errors))
print(f'检查通过：{len(CITIES)}市、总计{master_total}座桥；全部乡镇明细、区县索引、本地链接及{len(manifest)}张迁移图片。')
