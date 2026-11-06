"""已配置城市统一三级目录：市／区县／乡镇。由cityreadme在汇总前调用。"""
import collections
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'scripts'
CITIES = {'嘉兴市': 'jx', '湖州市': 'huz', '杭州市': 'build', '绍兴市': 'sx', '上海市': 'sh', '苏州市': 'sz', '金华市': 'jh', '宁波市': 'nb', '台州市': 'tz', '温州市': 'wz', '丽水市': 'ls', '无锡市': 'wx', '衢州市': 'qz', '舟山市': 'zs', '南京市': 'nj', '常州市': 'cz', '镇江市': 'zjs', '扬州市': 'yz', '徐州市': 'xz', '连云港市': 'lyg', '淮安市': 'ha', '盐城市': 'yc', '泰州市': 'tzj', '南通市': 'nt', '宿迁市': 'sq'}
ASSETS = S / 'build/town_assets.json'
CONTEXT = S / 'build/town_context.json'
BINDINGS = S / 'build/town_media_bindings.json'
MEDIA_BINDINGS = json.loads(BINDINGS.read_text()) if BINDINGS.exists() else {}


def protection_rank(row):
    """乡镇明细统一按保护等级从高到低排序，同级保持原顺序。"""
    level = row.get('level') or ''
    if level.startswith('全国重点'): return 0
    if level.startswith(('浙江省', '江苏省')): return 1
    if level.startswith(tuple(city + '文物保护单位' for city in CITIES)): return 2
    if '文物保护单位' in level: return 3
    if '文物保护点' in level or '文物控制单位' in level: return 4
    if '历史建筑' in level: return 5
    if level.startswith(('一般不可移动', '登记不可移动')):
        return 7 if '照片确认' in level else 6
    if level.startswith('未定级'): return 8
    if '已核实' in level or level == '未评级': return 9
    return 10


def media_allowed(city, row):
    key = '|'.join([city, row['dist'], row['town'], row['name']])
    binding = MEDIA_BINDINGS.get(key)
    return binding is None or row.get('loc') in binding['allowed_locations']


def folder(town):
    return '乡镇待核' if town in ('', '—', None) else town


def core(name):
    return re.sub(r'（.*?）|\(.*?\)|\s|^重建', '', name)


# 旧图片名未加乡镇前缀；来源已明确三座都在油车港镇，避免同名桥误配。
LEGACY_IMAGES = {('嘉兴市', '秀洲区', '油车港镇', n) for n in ('陶家桥', '步云桥', '万兴桥')}


def image_base(city, dist, row, district_rows):
    if city == '杭州市':
        return re.sub(r'（.*?）|\(.*?\)', '', row['name']).strip()
    name = core(row['name'])
    # 三级目录中已有的图片名优先，新增同名桥不应使旧照片失联。
    local = ROOT / city / dist / folder(row['town'])
    if any((local / f'{name}{i}.jpg').exists() for i in (1, 2, 3)):
        return name
    if (city, dist, row['town'], row['name']) in LEGACY_IMAGES:
        return name
    return row['town'] + name if sum(core(x['name']) == name for x in district_rows) > 1 else name


def rebase(text, old, new, moved=None):
    """重定位Markdown本地链接，外链和锚点保持原样。"""
    moved = moved or {}
    def replace(m):
        target = m.group(1)
        raw = target.strip('<>')
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:|^#|^/', raw):
            return m.group(0)
        path, mark, anchor = raw.partition('#')
        resolved = (old / unquote(path)).resolve()
        resolved = Path(moved.get(str(resolved), str(resolved)))
        result = os.path.relpath(resolved, new) + (mark + anchor if mark else '')
        return '](' + ('<' + result + '>' if ' ' in result else result) + ')'
    return re.sub(r'\]\((<[^>]+>|[^)]+)\)', replace, text)


def prepare(city, rows, *, districts=None):
    key = CITIES[city]
    provenance_path = S / key / 'imgsrc.json'
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {}
    manifest = json.loads(ASSETS.read_text()) if ASSETS.exists() else {}
    moved = {str(ROOT / a): str(ROOT / b) for a, b in manifest.items()}
    bydist = collections.defaultdict(list)
    for r in rows:
        bydist[r['dist']].append(r)
    if districts is not None:
        bydist = {d: bydist.get(d, []) for d in districts}
    elif city != '杭州市':
        for district in (ROOT / city).iterdir():
            if district.is_dir(): bydist.setdefault(district.name, [])
    # 先迁移所有可确定归属的图片，再生成页内、跨层链接。
    for dist, rs in bydist.items():
        old = ROOT / city / dist
        for r in rs:
            town = folder(r['town'])
            target = old / town
            target.mkdir(parents=True, exist_ok=True)
            name = core(r['name'])
            base = image_base(city, dist, r, rs)
            for i in (1, 2, 3):
                src = old / f'{base}{i}.jpg'
                dst = target / src.name
                if src.exists():
                    if dst.exists():
                        assert hashlib.sha256(src.read_bytes()).digest() == hashlib.sha256(dst.read_bytes()).digest(), (src, dst)
                        src.unlink()
                    else:
                        src.rename(dst)
                    manifest[str(src.relative_to(ROOT))] = str(dst.relative_to(ROOT))
                    moved[str(src)] = str(dst)
                # 兼容下载脚本仍记录在区县层的来源键，同时增加乡镇层键。
                oldkey, newkey = dist + '/' + src.name, dist + '/' + town + '/' + src.name
                if dst.exists() and oldkey in provenance:
                    provenance[newkey] = provenance[oldkey]
    ASSETS.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n')
    (S / key / 'imgsrc.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=1) + '\n')
    cq = json.loads((S / 'build/cqlinks.json').read_text())
    contexts = json.loads(CONTEXT.read_text()) if CONTEXT.exists() else {}
    townlist = json.loads((S / 'build/towns_all.json').read_text()).get(city, {})
    state = {}
    for dist, rs in bydist.items():
        old = ROOT / city / dist
        shared = contexts.get(city + '/' + dist, {})
        groups = collections.defaultdict(list)
        for r in rs:
            groups[folder(r['town'])].append(r)
        for town in townlist.get(dist, []):
            groups.setdefault(town, [])
        imgs = {}
        for town, items in groups.items():
            items.sort(key=protection_rank)
            page = old / town / (town + '古桥.md')
            page.parent.mkdir(parents=True, exist_ok=True)
            lines = [f'# {city}{dist}{town}不可移动文物：桥梁', '', '| 序号 | 桥名 | 结构 | 长度 | 时代 | 位置 | 文保等级 | 公布文件 | 图片 |', '|---|---|---|---|---|---|---|---|---|']
            used = []
            for i, r in enumerate(items, 1):
                name = core(r['name'])
                base = image_base(city, dist, r, rs)
                photos = [page.parent / f'{base}{j}.jpg' for j in (1, 2, 3) if (page.parent / f'{base}{j}.jpg').exists()]
                if not media_allowed(city, r): photos = []
                image = ' '.join(f'[{j}]({p.name})' for j, p in enumerate(photos, 1)) or '暂无'
                imgs[(r['town'], r['name'], r.get('loc'))] = ' '.join(f'[{j}]({town}/{p.name})' for j, p in enumerate(photos, 1)) or '暂无'
                used.extend(photos)
                url = cq.get(f"{city}|{dist}|{r['town']}|{r['name']}")
                if not media_allowed(city, r): url = None
                label = r['name']
                if r.get('sdl'):
                    label = '[' + label + '](' + os.path.relpath(ROOT / r['sdl'], page.parent) + ')'
                label += f' [?]({url})' if url else ''
                fields = [str(i), label, r.get('struct'), r.get('len'), r.get('era'), r.get('loc'), r.get('level'), r.get('doc'), image]
                lines.append('| ' + ' | '.join(str(x or '—').replace('\n', '<br>') for x in fields) + ' |')
            if not items:
                lines += ['', '当前收录名录中暂无桥梁记录。']
            lines += ['', '## 说明', '']
            for r in items:
                if r.get('note'):
                    note_name = r['name']
                    if sum(x['name'] == r['name'] for x in items) > 1:
                        note_name += '（' + (r.get('loc') or '位置待核') + '）'
                    lines.append('- ' + note_name + '：' + rebase(r['note'], old, page.parent, moved) + '。')
            for note in shared.get('town_notes', {}).get(town, []) + shared.get('notes', []):
                note = rebase(note, old, page.parent, moved)
                if note not in lines: lines.append(note)
            lines += ['- 乡镇名称沿用资料中的写法；“乡镇待核”仅表示来源未明确乡镇，不代表实际行政区划。', '- 结构、长度、位置标“—”表示现有资料未提供。', '', '## 来源', '']
            sources = []
            for r in items:
                sources.extend(r.get('srcs') or ([r['src']] if r.get('src') else []))
                if r.get('singdo'): sources.append(r['singdo'])
            for src in dict.fromkeys(sources):
                if src in ('', '—', None): continue
                source_label = shared.get('source_labels', {}).get(src, '资料来源')
                link = rebase(f'[{source_label}]({src})', old, page.parent, moved)
                lines.append('- ' + link)
            for source in shared.get('sources', []):
                source = rebase(source, old, page.parent, moved)
                if source not in lines: lines.append(source)
            if used:
                lines += ['', '## 图片来源', '', '| 文件 | 来源 |', '|---|---|']
                for p in dict.fromkeys(used):
                    source = provenance.get(dist + '/' + town + '/' + p.name, provenance.get(dist + '/' + p.name, '—'))
                    lines.append(f'| [{p.name}]({p.name}) | {rebase(source, old, page.parent, moved)} |')
                lines += ['', '图片版权及许可见各图片来源。']
            page.write_text('\n'.join(lines).rstrip() + '\n')
        state[dist] = dict(groups=groups, imgs=imgs)
    return state


def write_district(city, dist, rows, state, level_table, level_lists):
    old = ROOT / city / dist
    data = state[dist]
    lines = [f'# {city}{dist}古桥', '', f'共收录 {len(rows)} 座桥。', '', '## 按级别统计', ''] + (level_table(rows) if rows else ['名录里暂无桥梁记录。'])
    lines += ['', '## 各乡镇（街道）桥梁数量（降序）', '', '| 乡镇（街道） | 数量 |', '|---|---|']
    for town, items in sorted(data['groups'].items(), key=lambda item: -len(item[1])):
        lines.append(f'| [{town}]({town}/{town}古桥.md) | {len(items)} |')
    lines += ['', '## 按级别列出'] + (level_lists(rows, True, False, str(old), city, data['imgs'], with_location=True) if rows else ['', '无。'])
    lines += ['', '<!-- 区县汇总页（build/cityreadme.py 生成） -->', '']
    (old / (dist + '古桥.md')).write_text('\n'.join(lines))


def repair_links():
    """修正迁移图片的外部引用，并转义乡镇路径中的半角括号。"""
    manifest = json.loads(ASSETS.read_text()) if ASSETS.exists() else {}
    moved = {str(ROOT / a): ROOT / b for a, b in manifest.items()}
    pattern = r'\]\((<[^>]+>|(?:[^()]|\([^()]*\))*)\)'
    changed = []
    for page in ROOT.rglob('*.md'):
        if '.git' in page.parts:
            continue
        before = page.read_text()
        def replace(m):
            raw = m.group(1).strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:|^#|^/', raw):
                return m.group(0)
            path, sep, anchor = raw.partition('#')
            target = (page.parent / unquote(path)).resolve()
            if str(target) in moved:
                target = moved[str(target)]
                path = os.path.relpath(target, page.parent)
            if any((ROOT / city) in target.parents for city in CITIES):
                path = path.replace('(', '%28').replace(')', '%29')
            result = path + (sep + anchor if sep else '')
            if result == raw:
                return m.group(0)
            return '](' + ('<' + result + '>' if ' ' in result else result) + ')'
        after = re.sub(pattern, replace, before)
        if before != after:
            page.write_text(after)
            changed.append(str(page.relative_to(ROOT)))
    return changed
