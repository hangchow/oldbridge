"""核验嘉兴、湖州、绍兴及杭州三县市三级目录、明细位置和本地链接。"""
import collections
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r'\]\((<[^>]+>|(?:[^()]|\([^()]*\))*)\)')
errors = []
for city, key in [('嘉兴市', 'jx'), ('湖州市', 'huz'), ('绍兴市', 'sx'), ('杭州市', 'build')]:
    file = 'all_rows.json' if city == '杭州市' else 'rows.json'
    rows = json.loads((ROOT / 'scripts' / key / file).read_text())
    counties = ['桐庐县', '淳安县', '建德市'] if city == '杭州市' else None
    if counties: rows = [r for r in rows if r['dist'] in counties]
    expected = collections.Counter((r['dist'], r['town'] if r['town'] not in ('', '—') else '乡镇待核', r['name'], r.get('loc') or '—') for r in rows)
    actual = collections.Counter()
    pages = ([p for d in counties for p in (ROOT / city / d).glob('*/*古桥.md')] if counties else list((ROOT / city).glob('*/*/*古桥.md')))
    for page in pages:
        for line in page.read_text().splitlines():
            if not line.startswith('|'):
                continue
            cells = [re.sub(r'</?nobr>', '', v.strip()) for v in line.strip('|').split('|')]
            if len(cells) != 9 or not cells[0].isdigit():
                continue
            name = re.sub(r' \[\?\]\(.*?\)$', '', cells[1])
            name = re.sub(r'^\[(.*?)\]\(.*\)$', r'\1', name)
            actual[(page.parent.parent.name, page.parent.name, name, cells[5])] += 1
    if actual != expected:
        errors.append((city, '桥梁/位置不一致', expected - actual, actual - expected))
    check_pages = ([p for d in counties for p in (ROOT / city / d).rglob('*.md')] if counties else list((ROOT / city).rglob('*.md')))
    for page in check_pages:
        for match in LINK.finditer(page.read_text()):
            link = match.group(1).strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:|^#|^/', link):
                continue
            if not (page.parent / unquote(link.split('#')[0])).resolve().exists():
                errors.append((page.relative_to(ROOT), '失效链接', link))
    if city in ('嘉兴市', '湖州市', '绍兴市'):
        for page in (ROOT / city).glob('*/*古桥.md'):
            if any('## ' + name in page.read_text() for name in ['说明', '来源', '图片来源']):
                errors.append((page.relative_to(ROOT), '区县仍有明细说明'))
    print(f'{city}：{len(rows)}座桥，{len(pages)}个乡镇明细页')
manifest = json.loads((ROOT / 'scripts/build/town_assets.json').read_text())
for before, after in manifest.items():
    if not (ROOT / after).is_file():
        errors.append(('迁移图片缺失', before, after))
assert not errors, '\n'.join(map(str, errors))
print(f'检查通过：条目、位置、本地链接及{len(manifest)}张迁移图片。')

# 同乡镇同名桥不可共用仅有一个村址依据的照片。
page = ROOT / '嘉兴市/桐乡市/乌镇镇/乌镇镇古桥.md'
for line in page.read_text().splitlines():
    if line.startswith('|') and '杨园村费堡里组' in line:
        assert 'jxql153' not in line and '通济桥1.jpg' not in line, '杨园村通济桥误挂西栅资料'
