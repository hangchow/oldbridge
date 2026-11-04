"""杭州三县市、嘉兴、湖州、绍兴三级目录：市／区县／乡镇。由cityreadme在汇总前调用。"""
import collections
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'scripts'
CITIES = {'嘉兴市': 'jx', '湖州市': 'huz', '杭州市': 'build', '绍兴市': 'sx'}
ASSETS = S / 'build/town_assets.json'
# 这些城市的区县只作索引，共用说明与来源下沉乡镇页。
CLEAN_CITIES = {'嘉兴市', '湖州市', '绍兴市'}
CLEAN_DISTRICTS = {('嘉兴市', '海宁市')} | {('杭州市', d) for d in ['桐庐县', '淳安县', '建德市']}
CONTEXT = S / 'build/town_context.json'
BINDINGS = S / 'build/town_media_bindings.json'
MEDIA_BINDINGS = json.loads(BINDINGS.read_text()) if BINDINGS.exists() else {}


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


def prepare(city, rows):
    key = CITIES[city]
    provenance = json.loads((S / key / 'imgsrc.json').read_text())
    manifest = json.loads(ASSETS.read_text()) if ASSETS.exists() else {}
    moved = {str(ROOT / a): str(ROOT / b) for a, b in manifest.items()}
    bydist = collections.defaultdict(list)
    for r in rows:
        bydist[r['dist']].append(r)
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
        fp = old / (dist + '古桥.md')
        original = fp.read_text() if fp.exists() else ''
        rest = original[original.index('## 说明'):] if '## 说明' in original else ''
        rest = rest.replace('<!-- 区县汇总页（build/cityreadme.py 生成） -->', '').strip()
        rest = rebase(rest, old, old, moved)
        shared = contexts.get(city + '/' + dist, {})
        groups = collections.defaultdict(list)
        for r in rs:
            groups[folder(r['town'])].append(r)
        for town in townlist.get(dist, []):
            groups.setdefault(town, [])
        imgs = {}
        for town, items in groups.items():
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
        state[dist] = dict(groups=groups, imgs=imgs, rest=rest)
    return state


def write_district(city, dist, rows, state, level_table, level_lists):
    old = ROOT / city / dist
    data = state[dist]
    lines = [f'# {city}{dist}古桥', '', f'共收录 {len(rows)} 座桥。', '', '## 按级别统计', ''] + level_table(rows)
    lines += ['', '## 各乡镇（街道）桥梁数量（降序）', '', '| 乡镇（街道） | 数量 |', '|---|---|']
    for town, items in sorted(data['groups'].items(), key=lambda item: -len(item[1])):
        lines.append(f'| [{town}]({town}/{town}古桥.md) | {len(items)} |')
    lines += ['', '## 按级别列出'] + level_lists(rows, True, False, str(old), city, data['imgs'])
    if data['rest'] and city not in CLEAN_CITIES and (city, dist) not in CLEAN_DISTRICTS:
        lines += ['', data['rest']]
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
