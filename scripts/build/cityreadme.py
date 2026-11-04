# -*- coding: utf-8 -*-
# 生成非底层目录的 md：根目录汇总、市级 README、杭州各区 README；空区县放占位文件
import json, collections, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from era import year, DY
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
O = '/Users/sean/workspace/oldbridge'
C3 = ['桐庐县', '淳安县', '建德市']
CROSS = {('钱塘江大桥', '滨江区'): '西湖区', ('日新桥', '临安区'): '富阳区'}
CATS = ['全国重点文物保护单位', '省级文物保护单位', '市级文物保护单位', '县（区）级文物保护单位', '文物保护点', '县级文物保护点',
        '历史建筑', '一般不可移动文物', '一般不可移动文物（照片确认）', '未定级不可移动文物（四普新发现）', '尚未定级（已核实）', '尚未定级（待核实）']
LIST_FULL = set(CATS[:4])

NB = lambda x: x
CQ = json.load(open(S + '/build/cqlinks.json')) if os.path.exists(S + '/build/cqlinks.json') else {}
def NL(r, base, city=''):
        # 桥名只链到本地云端档案网页；老百晓集桥的链接放在桥名后的“?”上
    nm = f"[{r['name']}]({os.path.relpath(O + '/' + r['sdl'], base)})" if r.get('sdl') else r['name']
    u = r.get('cq') or CQ.get(f"{city}|{r['dist']}|{r['town']}|{r['name']}")
    return f"{nm} [?]({u})" if u else nm

CITIES = ['杭州市', '湖州市', '嘉兴市', '上海市', '苏州市', '金华市', '绍兴市', '宁波市', '衢州市', '台州市', '温州市', '丽水市', '舟山市', '无锡市', '南京市', '常州市', '镇江市', '扬州市', '徐州市', '连云港市', '淮安市', '盐城市', '泰州市', '南通市', '宿迁市']
def cat(lv):
    if lv.startswith('全国重点'): return CATS[0]
    if lv.startswith('浙江省') or lv.startswith('江苏省'): return CATS[1]
    if '文物控制单位' in lv: return CATS[4]
    m = re.match(r'(.{2,3}市)文物保护(单位|点)', lv)
    if m and m.group(1) in CITIES: return CATS[2] if m.group(2) == '单位' else CATS[4]
    if re.match(r'.+(区|县|市)文物保护单位', lv) or lv.startswith('区级文物保护单位'): return CATS[3]
    if '文物保护点' in lv or '文物控制单位' in lv: return CATS[4]   # 统计表不分市级、县级公布，合为一类
    if '历史建筑' in lv: return CATS[6]
    if lv.startswith('一般不可移动文物（照片确认'): return CATS[8]
    if lv.startswith('一般不可移动') or lv.startswith('登记不可移动'): return CATS[7]
    if lv.startswith('未定级'): return CATS[9]
    if lv.startswith('尚未定级（已核实'): return CATS[10]
    return CATS[11]

def sandun_rows():
    rs = []
    for l in open(f'{O}/杭州市/西湖区/三墩镇/三墩镇古桥.md', encoding='utf8'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        c = [re.sub(r'</?nobr>', '', x) for x in c]
        if len(c) >= 8 and c[0].isdigit():
            q = re.search(r' \[\?\]\((http[^)]+)\)$', c[1])
            nmc = c[1][:q.start()] if q else c[1]
            m = re.match(r'\[(.*?)\]\((.*?)\)', nmc)
            d = dict(dist='西湖区', town='三墩镇', name=m.group(1) if m else nmc, struct=c[2], len=c[3], era=c[4], level=c[6])
            if m and '云端档案/' in m.group(2): d['sdl'] = '文保名录/杭州市/云端档案/' + m.group(2).split('云端档案/', 1)[1]
            if q: d['cq'] = q.group(1)
            rs.append(d)
    return rs

def level_table(rows):
    c = collections.Counter(cat(r['level']) for r in rows)
    return ['| 级别 | 数量 |', '|---|---|'] + [f'| {k} | {c[k]} |' for k in CATS if c[k]]

def DLk(r, base, city):
    # 区县名链接到区县汇总页
    d = r['dist']; f = f"{O}/{city}/{d}/{d}古桥.md"
    return NB(f"[{d}]({os.path.relpath(f, base)})") if city and os.path.exists(f) else NB(d)

def TL(r, base, city):
    # 乡镇名链接到乡镇文件（目前只有杭州市辖区分到乡镇）
    t = r['town']; f = f"{O}/{city}/{r['dist']}/{t}/{t}古桥.md"
    return f"[{t}]({os.path.relpath(f, base)})" if city and t not in ('—', '') and os.path.exists(f) else t

def level_lists(rows, full_all, with_dist, base=O, city='', imgs=None):
    L = []
    for k in CATS:
        x = [r for r in rows if cat(r['level']) == k]
        first = {}
        for r in x: first.setdefault((r['dist'], r['town']), len(first)); first.setdefault(r['dist'], len(first))
        x.sort(key=lambda r: (first[r['dist']], r['town'] in ('—', ''), first[(r['dist'], r['town'])]))   # 同一区县、同一乡镇的桥排在一起
        if not x: continue
        L += ['', f'### {k}（{len(x)} 座）', '']
        if full_all or k in LIST_FULL:
            hdr = ('| 区县 ' if with_dist else '') + '| 乡镇 | 桥名 | 结构 | 长度 | 时代 | 等级说明 |' + (' 图片 |' if imgs is not None else '')
            L += [hdr, '|---' * ((7 if with_dist else 6) + (imgs is not None)) + '|']
            L += [('| ' + DLk(r, base, city) + ' ' if with_dist else '') + f"| {TL(r, base, city)} | {NL(r, base, city)} | {r.get('struct') or '—'} | {r.get('len') or '—'} | {r['era'] or '—'} | {r['level']} |" + (f" {imgs.get((r['town'], r['name']), '暂无')} |" if imgs is not None else '') for r in x]
        else:
            L += ['数量较多，见各区县文件。']
    return L

INS = json.load(open(S + '/build/inscr.json')) if os.path.exists(S + '/build/inscr.json') else {}
def oldest(items, title, with_city):
    # 只认桥身题刻纪年（老百晓集桥、云端档案里对题刻的记载）
    # 刻的只是朝代或年号、没有年数的，按其最晚可能年份排（如刻“唐”的排在所有宋代纪年之前）
    ex = sorted([((INS[k]['hi'], INS[k]['lo']), c, r, INS[k]) for c, r in items if (k := f"{c}|{r['dist']}|{r['town']}|{r['name']}") in INS], key=lambda x: x[0])
    L = ['', f'## {title}', '']
    if not ex: return L + ['还没有查到桥身题刻纪年的记载。']
    L += ['| 名次 | ' + ('市 | ' if with_city else '') + '区县 | 乡镇 | 桥名 | 结构 | 刻有年代 | 题刻 | 时代 | 级别 |', '|---' * (10 if with_city else 9) + '|']
    for i, (y, c, r, d) in enumerate(ex[:20], 1):
        base = O if with_city else O + '/' + c
        L.append(f"| {i} | " + (f"{NB(c)} | " if with_city else '') + f"{DLk(r, base, c)} | {TL(r, base, c)} | {NL(r, base, c)} | {r.get('struct') or '—'} | {d['label']} | [{d['text']}]({d['src']}) | {r['era'] or '—'} | {cat(r['level'])} |")
    L += ['', '统计范围：只限本项目收录的二十五个市（杭州、湖州、嘉兴、上海、苏州、金华、绍兴、宁波、衢州、台州、温州、丽水、舟山、无锡、南京、常州、镇江、扬州、徐州、连云港、淮安、盐城、泰州、南通、宿迁）的桥，而且只统计老百晓集桥、云端档案中记载了题刻内容的桥，不代表整个江浙沪；其他桥可能也有更早的刻字，只是资料里没有记载。']
    L += ['', f'只收桥身上刻有年代的桥（桥柱、栏板、拱券、桥肚等处的题刻），方志等文献记载的始建年份不算。题刻写明年号和年数（或干支）的，按该年排序；只刻朝代或年号、没有年数的，按这个朝代或年号的最后一年排序，例如刻“唐”的会排在所有宋代纪年之前。题刻内容据老百晓集桥、杭州市文物遗产与历史建筑保护中心云端档案的记载，点击“题刻”一列可看原文。很多题刻记的是重建年份，桥本身可能更早。目前查到题刻的共 {len(ex)} 座。']
    return L

def city_readme(city, rows, sub):
    extra = {}
    for (n, d), p in CROSS.items():
        if any(r['name'] == n and r['dist'] == d for r in rows): extra.setdefault(d, []).append((n, p))
    rows = [r for r in rows if (r['name'], r['dist']) not in CROSS]
    c = collections.Counter(r['dist'] for r in rows)
    for d in sorted(x for x in os.listdir(f'{O}/{city}') if os.path.isdir(f'{O}/{city}/{x}')): c.setdefault(d, 0)   # 没有桥的区县也列出（0）
    L = [f'# {city}古桥', '', f'共收录 {len(rows)} 座桥。', '', '## 按级别统计', ''] + level_table(rows)
    L += ['', '## 各区县桥梁数量（降序）', '', '| 区县 | 数量 |', '|---|---|']
    L += [f'| [{NB(d)}]({d}/{d}古桥.md) | {n}' + ''.join(f'（另有跨区的{a}，计入{b}）' for a, b in extra.get(d, [])) + ' |' for d, n in c.most_common()]
    if extra: L += ['', '跨区的桥（钱塘江大桥跨西湖区、滨江区；日新桥跨富阳区、临安区）在两个区的文件里都有列出，但统计只算一次。']
    st = sorted([r for r in rows if re.match(r'^[0-9.]+米$', r.get('len') or '') and not re.search(r'钢|混凝土|水泥|铁|索桥', r.get('struct') or '') and (not r['level'].startswith('尚未定级') or '已逐座核对' in (r.get('note') or ''))], key=lambda r: -float(r['len'][:-1]))
    L += ['', f'## {city}石木桥桥长前 20 名', '', '| 名次 | 区县 | 乡镇 | 桥名 | 结构 | 长度 | 时代 | 级别 |', '|---|---|---|---|---|---|---|---|']
    L += [f"| {i} | {DLk(r, O + '/' + city, city)} | {TL(r, O + '/' + city, city)} | {NL(r, O + '/' + city, city)} | {r.get('struct') or '—'} | {r['len']} | {r['era'] or '—'} | {cat(r['level'])} |" for i, r in enumerate(st[:20], 1)]
    L += ['', f'只比石桥和木桥（含石拱、石墩、木拱、木梁等各类廊桥）；结构写明钢、铁、混凝土、水泥或悬索的不参加；结构标“—”的按古代石木桥计入，在已查到长度的 {len(st)} 座中排序。']
    L += oldest([(city, r) for r in rows], f'{city}桥身刻字最早的前 20 名', False)
    L += ['', '## 按级别列出'] + level_lists(rows, False, True, O + '/' + city, city)
    open(f'{O}/{city}/README.md', 'w').write('\n'.join(L) + '\n')
    return rows

H = [r for r in json.load(open(S + '/build/all_rows.json')) if not (r['dist'] == '西湖区' and r['town'] == '三墩镇')] + sandun_rows()
HZ = json.load(open(S + '/huz/rows.json'))
hrows = city_readme('杭州市', H, True)
zrows = city_readme('湖州市', HZ, False)
jrows = city_readme('嘉兴市', json.load(open(S + '/jx/rows.json')), False)
srows = city_readme('上海市', json.load(open(S + '/sh/rows.json')), False)
zsrows = city_readme('苏州市', json.load(open(S + '/sz/rows.json')), False)
jhrows = city_readme('金华市', json.load(open(S + '/jh/rows.json')), False)
r_sx = city_readme('绍兴市', json.load(open(S + '/sx/rows.json')), False)
r_nb = city_readme('宁波市', json.load(open(S + '/nb/rows.json')), False)
r_qz = city_readme('衢州市', json.load(open(S + '/qz/rows.json')), False)
r_tz = city_readme('台州市', json.load(open(S + '/tz/rows.json')), False)
r_wz = city_readme('温州市', json.load(open(S + '/wz/rows.json')), False)
r_ls = city_readme('丽水市', json.load(open(S + '/ls/rows.json')), False)
r_zs = city_readme('舟山市', json.load(open(S + '/zs/rows.json')), False)
r_js = {c: city_readme(c, json.load(open(f'{S}/{k}/rows.json')), False) for c, k in [('无锡市', 'wx'), ('南京市', 'nj'), ('常州市', 'cz'), ('镇江市', 'zjs'), ('扬州市', 'yz'), ('徐州市', 'xz'), ('连云港市', 'lyg'), ('淮安市', 'ha'), ('盐城市', 'yc'), ('泰州市', 'tzj'), ('南通市', 'nt'), ('宿迁市', 'sq')]}

# 杭州各市辖区
def hz_town_imgs(d):
    # 从各乡镇页的表格里取“图片”列，相对链接改为指向乡镇子目录
    out = {}
    for t in os.listdir(f'{O}/杭州市/{d}'):
        f = f'{O}/杭州市/{d}/{t}/{t}古桥.md'
        if not os.path.isfile(f): continue
        for l in open(f, encoding='utf8'):
            c = [x.strip() for x in l.strip().strip('|').split('|')]
            if len(c) < 8 or not re.sub(r'</?nobr>', '', c[0]).isdigit(): continue
            nm = re.sub(r' \[\?\]\(http[^)]+\)$', '', c[1]); m = re.match(r'\[(.*?)\]\(.*?\)$', nm); nm = m.group(1) if m else nm
            out[(t, nm)] = re.sub(r'\]\((?!https?:|\.\./)([^)]+)\)', lambda m: f'](<{t}/{m.group(1)}>)' if ' ' in m.group(1) else f']({t}/{m.group(1)})', c[-1])
    return out
MK = '<!-- 区县汇总页（build/cityreadme.py 生成） -->'
towns = json.load(open(S + '/hz/towns.json'))
for d in towns:
    if d in C3: continue
    rs = [r for r in H if r['dist'] == d]
    t = collections.Counter(r['town'] for r in rs)
    for k in towns[d]: t.setdefault(k, 0)   # 名录里没有桥的乡镇也列出（0）
    L = [f'# 杭州市{d}古桥', '', f'共收录 {len(rs)} 座桥。' + ('（含跨区桥，市级统计只算一次）' if any((r['name'], d) in CROSS for r in rs) else ''),
         '', '## 按级别统计', ''] + (level_table(rs) if rs else ['名录里没有桥梁。'])
    L += ['', '## 各乡镇（街道）桥梁数量（降序）', '', '| 乡镇（街道） | 数量 |', '|---|---|'] + [f'| [{k}]({k}/{k}古桥.md) | {n} |' for k, n in t.most_common()]
    L += ['', '## 按级别列出'] + (level_lists(rs, True, False, f'{O}/杭州市/{d}', '杭州市', hz_town_imgs(d)) if rs else ['', '无。'])
    open(f'{O}/杭州市/{d}/{d}古桥.md', 'w').write('\n'.join(L) + '\n' + MK + '\n')
    if os.path.exists(f'{O}/杭州市/{d}/README.md'): os.remove(f'{O}/杭州市/{d}/README.md')   # 旧文件名

# 其余城市
for c in []:
    open(f'{O}/{c}/README.md', 'w').write(f'# {c}古桥\n\n整理中。\n')
    for d in os.listdir(f'{O}/{c}'):
        p = f'{O}/{c}/{d}'
        if os.path.isdir(p) and not any(f.endswith('.md') for f in os.listdir(p)):
            open(f'{p}/{d}古桥.md', 'w').write(f'# {c}{d}古桥\n\n整理中。\n')

# 根目录 README 的汇总段
tot0 = {'杭州市': hrows, '湖州市': zrows, '嘉兴市': jrows, '上海市': srows, '苏州市': zsrows, '金华市': jhrows, '绍兴市': r_sx, '宁波市': r_nb, '衢州市': r_qz, '台州市': r_tz, '温州市': r_wz, '丽水市': r_ls, '舟山市': r_zs, **r_js}
ORDER = ['杭州市', '湖州市', '嘉兴市', '金华市', '绍兴市', '宁波市', '衢州市', '台州市', '温州市', '丽水市', '舟山市', '上海市', '苏州市', '无锡市', '常州市', '南京市', '镇江市', '扬州市', '泰州市', '南通市', '盐城市', '淮安市', '宿迁市', '徐州市', '连云港市']   # 浙江、上海、江苏
tot = {c: tot0[c] for c in ORDER}

# 其余城市（及杭州桐庐、淳安、建德）的区县 README：格式同杭州市辖区，原“区县古桥.md”的表格和说明并在后面
TA = json.load(open(S + '/build/towns_all.json'))   # 各区县乡镇（街道）名单（据统计用区划代码，modood/Administrative-divisions-of-China）
DONE = []
for c in ORDER:
    for d in sorted({r['dist'] for r in tot0[c]} | {x for x in os.listdir(f'{O}/{c}') if os.path.isdir(f'{O}/{c}/{x}')}):
        if c == '杭州市' and d not in C3: continue
        p = f'{O}/{c}/{d}'
        if not os.path.isdir(p): continue
        rs = [r for r in tot0[c] if r['dist'] == d]
        t = collections.Counter(r['town'] for r in rs)
        for k in TA.get(c, {}).get(d, []):   # 没有桥的乡镇（街道）也列出（0）；仓库里写法带前缀（如“经开区长水街道”）或旧名包含它的不重复列
            if k not in t and not any(x.endswith(k) or k.endswith(x) for x in t if x != '—'): t[k] = 0
        fp = f'{p}/{d}古桥.md'
        body = open(fp, encoding='utf8').read() if os.path.exists(fp) else ''
        body = [] if MK in body else body.split('\n')[1:]   # 原表格文件：去掉标题，整体并入；上一轮生成的汇总页不再并入
        L = [f'# {c}{d}古桥', '', f'共收录 {len(rs)} 座桥。', '', '## 按级别统计', ''] + (level_table(rs) if rs else [x for x in body if x.strip()] or ['名录里没有桥梁。'])
        if rs: L += ['', '## 各乡镇（街道）桥梁数量（降序）', '', '| 乡镇（街道） | 数量 |', '|---|---|'] + [f'| {k} | {n} |' for k, n in t.most_common()]
        # 原表格：取“图片”一列并到按级别列出里，表格后面的说明、来源、图片来源保留
        imgs, rest, intab, hdr = {}, [], False, []
        for x in body:
            if x.startswith('| ') and ('序号' in x or intab):
                cs = [re.sub(r'</?nobr>', '', y).strip() for y in x.strip().strip('|').split(' | ')]
                if '序号' in x: hdr = cs; intab = True; continue
                if hdr and hdr[-1] == '图片' and len(cs) == len(hdr):
                    nm = re.sub(r' \[\?\]\(.*?\)$', '', cs[2]); nm = re.sub(r'^\[(.*?)\]\(.*?\)$', r'\1', nm)
                    imgs[(cs[1], nm)] = cs[-1]
            elif x.startswith('|---') and intab: continue
            else:
                if intab and not x.strip(): intab = False
                if not intab: rest.append(x)
        L += ['', '## 按级别列出'] + (level_lists(rs, True, False, p, c, imgs) if rs else ['', '无。'])
        zx = [r for r in rs if '浙江省市县级文物保护单位名录' in (r.get('note') or '') or '上海市不可移动文物名录（上海图书馆' in (r.get('note') or '')]
        zn = {r['name'] for r in zx}
        rest = [x for x in rest if not any(x.startswith(f'- {n}：') for n in zn)]   # 这些桥的说明改在下面统一列出
        if rs and body: L += rest
        if zx:
            if c == '上海市': L += ['', '### 据上海市不可移动文物名录补正', '', '以下桥梁的等级据上海市不可移动文物名录（上海图书馆开放数据平台“上海年华”，摘录见 [文保名录/上海市/](../../文保名录/上海市/)）补正或新增：', '']
            else: L += ['', '### 据省文物局市县级文保名录补正', '', '以下桥梁的等级、公布文号据浙江省文物局《浙江省市县级文物保护单位名录》（2023年7月19日发布，原件见 [文保名录/浙江省/](../../文保名录/浙江省/)）补正或新增：', '']
            L += [f"- {r['name']}：{r['note']}。" for r in zx]
        open(fp, 'w').write('\n'.join(L).rstrip('\n') + '\n' + MK + '\n')
        DONE.append((c, d, len(rs), fp))
        if os.path.exists(f'{p}/README.md'): os.remove(f'{p}/README.md')   # 旧文件名
CL = lambda c: f'[{c}]({c}/README.md)' if os.path.exists(f'{O}/{c}/README.md') else c   # 市名链到各市 README
L = ['<!-- SUMMARY START -->', '## 各市按级别统计', '', '| 级别 | ' + ' | '.join(CL(c) for c in tot) + ' | 合计 |', '|---|' + '---|' * (len(tot) + 1)]
for k in CATS:
    v = [sum(1 for r in rs if cat(r['level']) == k) for rs in tot.values()]
    if sum(v): L.append(f'| {k} | ' + ' | '.join(map(str, v)) + f' | {sum(v)} |')
v = [len(rs) for rs in tot.values()]
L.append('| **合计** | ' + ' | '.join(map(str, v)) + f' | {sum(v)} |')
gb = [(c, r) for c, rs in tot.items() for r in rs if cat(r['level']) == CATS[0]]
L += ['', f'## 全国重点文物保护单位（{len(gb)} 座）', '', '| 序号 | 市 | 区县 | 乡镇 | 桥名 | 结构 | 长度 | 时代 | 等级说明 |', '|---|---|---|---|---|---|---|---|---|']
L += [f"| {i} | {c} | {DLk(r, O, c)} | {TL(r, O, c)} | {NL(r, O, c)} | {r.get('struct') or '—'} | {r.get('len') or '—'} | {r['era'] or '—'} | {r['level']} |" for i, (c, r) in enumerate(gb, 1)]
allr = [(c, r) for c, rs in tot.items() for r in rs if re.match(r'^[0-9.]+米$', r.get('len') or '') and not re.search(r'钢|混凝土|水泥|铁|索桥', r.get('struct') or '') and (not r['level'].startswith('尚未定级') or '已逐座核对' in (r.get('note') or ''))]
allr.sort(key=lambda x: -float(x[1]['len'][:-1]))
L += ['', '## 江浙沪石木桥桥长前 20 名', '', '| 名次 | 市 | 区县 | 乡镇 | 桥名 | 结构 | 长度 | 时代 | 级别 |', '|---|---|---|---|---|---|---|---|---|']
L += [f"| {i} | {NB(c)} | {DLk(r, O, c)} | {TL(r, O, c)} | {NL(r, O, c)} | {r.get('struct') or '—'} | {r['len']} | {r['era'] or '—'} | {cat(r['level'])} |" for i, (c, r) in enumerate(allr[:20], 1)]
L += ['', f'只比石桥和木桥（含各类廊桥）：结构写明钢、铁、混凝土、水泥或悬索的不参加（如钱塘江大桥）；结构标“—”的按古代石木桥计入。只在已查到长度的 {len(allr)} 座中排序，大部分桥还没有长度数据。']
L += oldest([(c, r) for c, rs in tot.items() for r in rs], '本项目收录范围内桥身刻字最早的前 20 名', True)
L += ['', '各市的分级名单见各市目录下的 README。', '<!-- SUMMARY END -->']
p = f'{O}/README.md'; s = open(p, encoding='utf8').read()
blk = '\n'.join(L)
if '<!-- SUMMARY START -->' in s:
    s = re.sub(r'<!-- SUMMARY START -->.*?<!-- SUMMARY END -->', blk, s, flags=re.S)
else:
    s = s.replace('## 目录结构', blk + '\n\n## 目录结构', 1)
open(p, 'w', encoding='utf8').write(s)
for root, ds, fs in os.walk(O):
    if '.git' not in root and not any(f.endswith('.md') for f in fs): print('NO MD:', root)
print('杭州', len(hrows), '湖州', len(zrows))
