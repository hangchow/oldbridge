# -*- coding: utf-8 -*-
# 浙江、江苏其他城市古桥名录生成（两级目录：市/区县/区县古桥.md）。用法：python3 build.py 绍兴市
import json, os, re, sys, html
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
sys.path.insert(0, S + '/zj'); sys.path.insert(0, S + '/build')
from wikilist import parse, clean, split_names
CITY = sys.argv[1]; CF = json.load(open(S + '/zj/cities.json'))[CITY]; K = CF['key']; DISTS = CF['dists']; PROV = CF.get('prov', '浙江省'); ZJ = PROV == '浙江省'
ROOT = f'/Users/sean/workspace/oldbridge/{CITY}'
W = lambda p: 'https://zh.wikipedia.org/wiki/' + p
XLSX = 'http://wwj.zj.gov.cn/'
SRCNAME = {W('浙江省文物保护单位'): '维基百科：浙江省文物保护单位',
           XLSX: f'浙江省文物局：全省文物保护点统计表（{CITY}文物保护点，本项目 文保名录/浙江省/ 有原件）'}
for d in DISTS: SRCNAME[W(d + '各级文物保护单位列表')] = f'维基百科：{d}各级文物保护单位列表'
def SN(u): return SRCNAME.get(u) or ('老百晓集桥：' + u.rsplit('/', 1)[-1] if 'china-qiao' in u else u)
def load(p): return json.load(open(p)) if os.path.exists(p) else {}
ST, LN, IMG = load(f'{S}/{K}/struct.json'), load(f'{S}/{K}/len.json'), load(f'{S}/{K}/imgsrc.json')
CQ, HOLES, EF, LENF = load(S + '/build/cqlinks.json'), load(S + '/build/cq_holes.json'), load(S + '/build/era_fill.json'), load(S + '/build/cq_len_fill.json')
core = lambda n: re.sub(r'（.*?）|\(.*?\)|\s', '', n)
PRE = r'^(?:' + PROV + r')?(?:' + CITY + r')?(?:' + '|'.join(DISTS) + r')?(?:[一-龥]{2}新区)?'
def town_of(*ss):
    for s in ss:
        if not s: continue
        t = re.sub(PRE, '', s.strip())
        if re.fullmatch(r'.{1,6}?(镇|乡|街道)', t): return t
        m = re.match(r'^(.{1,6}?)(街道|镇|乡)', t)
        if m and not re.search(r'[路街巷弄村古]', m.group(1)) and len(m.group(1)) >= 2: return m.group(1) + m.group(2)
    return '—'
LV = {'gb': 0, 'sb': 1, 'shi': 2, 'xian': 3, 'wbd': 4, 'dj': 5}
R = []
def add(dist, name, era, addr, lv, num='', group='', batch='', src='', town=None, doc='—', unote='', lvtxt=''):
    if dist not in DISTS or not name: return
    era = era or '—'
    if re.match(r'(19[5-9]\d|20\d\d)|现代|当代|中华人民共和国', era): return   # 只看建造年代开头，括号里的重修年份不算
    tw = town or town_of(addr)
    for r in R:
        if r['dist'] == dist and core(r['name']) == core(name):
            if r.get('lvtxt') and lvtxt and tw != '—' and r['town'] != '—' and tw != r['town']: continue   # 原件里同名不同乡镇的两座桥
            if LV[lv] < LV[r['lvk']] and (lvtxt or not r.get('lvtxt')):
                r.update(lvk=lv, num=num or r['num'], group=group or r['group'], batch=batch or r['batch'], src=src, lvtxt=lvtxt or r.get('lvtxt', ''), doc=doc if lvtxt else r['doc'])
            if r['era'] in ('—', '') or (re.search('至', r['era']) and r['group']): r['era'] = era if era != '—' else r['era']
            if r['loc'] in ('—', ''): r['loc'] = addr or '—'
            if r['town'] == '—': r['town'] = town or town_of(addr)
            return
    R.append(dict(dist=dist, name=name, era=era, loc=addr or '—', lvk=lv, num=num, group=group, batch=batch, src=src,
                  town=tw, doc=doc, unote=unote, lvtxt=lvtxt))
# 0) 政府原件（文保名录/ 里的名单，build/official.py 提取）：等级、批次以原件为准
OFF = json.load(open(S + '/build/official.json')).get(CITY, []) if os.path.exists(S + '/build/official.json') else []
for o in OFF:
    u = '../../文保名录/' + o['src']; SRCNAME[u] = '政府原件：' + o['src'].split('/')[-1].rsplit('.', 1)[0]
    add(o['dist'], o['name'], o['era'], o['loc'], o['lv'], src=u, town=o['town'] if o['town'] != '—' else None, doc=o['doc'], lvtxt=o['lvtxt'])
# 1) 各区县列表
for d in DISTS:
    f = f'{S}/{K}/{d}各级文物保护单位列表.txt'
    if not os.path.exists(f) or os.path.getsize(f) < 300: continue
    for r in parse(open(f).read(), CITY):
        if f"{d}|{r['name']}" in CF.get('skipwiki', []): continue   # 维基区县有误、以原件为准的条目
        add(d, r['name'], r['era'], r['addr'], r['lv'], r['num'], r['group'], r['batch'], W(d + '各级文物保护单位列表'))
# 2) 浙江省文物保护单位总表（补区县列表里缺的省保）
t = open(S + '/jx/浙江省文物保护单位.txt').read()
m = ZJ and re.search(r'===\[\[' + CITY + r'\]\]===(.*?)\n===\[\[', t, re.S)
if m:
    body = re.sub(r'<!--.*?-->', '', m.group(1), flags=re.S); cur = None
    for l in body.split('\n'):
        h = re.match(r'====\[\[(.+?)\]\]====', l)
        if h: cur = h.group(1); continue
        if l.startswith('*') and cur in DISTS:
            c = clean(l.lstrip('*')); num = (re.search(r'（(\d+-?\d*)）', c) or [None, ''])[1]
            c = re.sub(r'（\d.*', '', c).split('；')[0]
            for n in split_names(c): add(cur, n, '', '', 'sb', num, '' if n == c else c, '', W('浙江省文物保护单位'))
# 3) 文保点（浙江省文物局统计表）
for _ in ([1] if CF.get('sheet') else []):
  ss = open(S + '/x/xl/sharedStrings.xml', encoding='utf8').read()
  strs = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', x, re.S)) for x in re.findall(r'<si>(.*?)</si>', ss, re.S)]
  x = open(f"{S}/x/xl/worksheets/sheet{CF['sheet']}.xml", encoding='utf8').read(); cur = ''
  for row in re.findall(r'<row[^>]*>(.*?)</row>', x, re.S)[2:]:
      v = {}
      for attr, inner in re.findall(r'<c ([^>]*?)(?:/>|>(.*?)</c>)', row, re.S):
          col = re.search(r'r="([A-Z]+)\d+"', attr).group(1); vv = re.search(r'<v>(.*?)</v>', inner or '')
          v[col] = '' if not vv else html.unescape(strs[int(vv.group(1))] if 't="s"' in attr else vv.group(1))
      if v.get('B'): cur = re.sub(r'（.*', '', v['B']).strip()
      n = v.get('C', '')
      if '桥' not in n: continue
      d = next((dd for dd in DISTS if dd[:2] == cur[:2]), cur)
      tw = re.sub(PRE, '', v.get('F', ''))
      add(d, n, v.get('D', ''), v.get('G', ''), 'wbd', town=tw if re.search(r'(镇|乡|街道)$', tw) else town_of(v.get('G', '')), src=XLSX, doc=v.get('H', '') or '—')
# 4) 不在文保名录、老百晓集桥收录的古桥（尚未定级，待核实）
for u in (json.load(open(S + '/build/unlisted.json')).get(CITY, []) if os.path.exists(S + '/build/unlisted.json') else []):
    if not any(r['dist'] == u['dist'] and core(r['name']) == core(u['name']) for r in R): add(u['dist'], u['name'], u['era'], '', u.get('lv', 'dj'), src=u['src'], town=u['town'], unote=(f"据老百晓集桥页面：{u['lvnote']}（维基百科名单未收，待核对政府原件）；" if u.get('lvnote') else '') + u.get('note', ''))
# 撤镇设街道的旧名改成今名（以统计表里同一区县出现过的街道名为准）
XT = {}
for r in R:
    if r['town'].endswith('街道'): XT.setdefault(r['dist'], set()).add(r['town'])
for r in R:
    t = r['town']
    if t.endswith('镇') and t[:-1] + '街道' in XT.get(r['dist'], ()): r['town'] = t[:-1] + '街道'
    if r['group'] and core(r['group']) == core(r['name']): r['group'] = ''
    r['town'] = CF.get('townfix', {}).get(f"{r['dist']}|{r['name']}", r['town'])
# 组名只留名称本身；成组条目在已拆出单桥时去掉
for r in R:
    if r['group']: r['group'] = re.split(r'共\d|其中|[，；,;]|含', r['group'])[0].strip()
grp = {(r['dist'], core(r['group'])) for r in R if r['group']}
R[:] = [r for r in R if (r['dist'], core(r['name'])) not in grp]
# 等级文字
for r in R:
    g = f"“{r['group']}”组成部分" if r['group'] and r['group'] != r['name'] else ''
    if r['lvk'] == 'gb': r['level'] = '全国重点文物保护单位' + (f'（{g}）' if g else '')
    elif r['lvk'] == 'sb': r['level'] = PROV + '文物保护单位' + ('（' + '，'.join(x for x in [g, r['num']] if x) + '）' if g or r['num'] else '')
    elif r['lvk'] == 'shi': r['level'] = f'{CITY}文物保护单位'
    elif r['lvk'] == 'xian': r['level'] = f"{r['dist']}文物保护单位"
    elif r['lvk'] == 'dj': r['level'] = '尚未定级（待核实，老百晓集桥收录，不在文保名录中）'
    else: r['level'] = f'{CITY}文物保护点' if ZJ else f"一般不可移动文物（{r['dist']}不可移动文物名录）"
    if r.get('lvtxt'): r['level'] = r['lvtxt']
    k = f"{r['dist']}|{r['town']}|{r['name']}"
    r['struct'] = ST.get(k, '—'); r['len'] = LN.get(k, '—'); r['note'] = r['unote'] or ('不在文保名录中，据老百晓集桥页面收录，年代按页面开头的记载，待核实' if r['lvk'] == 'dj' else '')
    ck = f"{CITY}|{k}"
    if ck in HOLES and (r['struct'] == '—' or re.fullmatch(r'石?(拱|梁)桥|石板桥|平桥|廊桥', r['struct'])): r['struct'] = HOLES[ck]
    if ck in LENF and r['len'] in ('—', ''): r['len'] = LENF[ck]
    if ck in EF and r['era'] == EF[ck]['old']:
        f = EF[ck]; old = r['era']; ds = [d for d in ('宋', '元', '明', '清', '民国') if d in old.replace('中华民国', '民国')]
        r['era'] = f['era'] if all(d in f['era'] for d in ds) else old + '；' + f['era']
        r['note'] = (r['note'] + '；' if r['note'] else '') + f"具体年代据{'老百晓集桥' if f['src'] == 'cq' else '云端档案'}（名录原写“{old}”）"
for r in R:
    for kk in ('lvk', 'num', 'group', 'batch', 'unote', 'lvtxt'): r.pop(kk, None)
json.dump(R, open(f'{S}/{K}/rows.json', 'w'), ensure_ascii=False, indent=0)
# 生成区县 md
ORD = lambda lv: 0 if lv.startswith('全国') else 1 if lv.startswith(PROV) else 5 if lv.startswith('尚未') else 4 if '保护点' in lv or '不可移动' in lv or '控制单位' in lv else 2 if lv.startswith(CITY) else 3
for d in DISTS:
    folder = os.path.join(ROOT, d); os.makedirs(folder, exist_ok=True)
    rs = sorted([r for r in R if r['dist'] == d], key=lambda r: ORD(r['level']))
    L = [f'# {CITY}{d}不可移动文物：桥梁', '']
    if not rs:
        L += [f'目前收集到的名录里，{d}没有桥梁。', '']
        open(os.path.join(folder, f'{d}古桥.md'), 'w').write('\n'.join(L)); print(d, 0); continue
    L += ['| 序号 | 乡镇 | 桥名 | 结构 | 长度 | 时代 | 位置 | 文保等级 | 公布文件 | 图片 |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(rs, 1):
        b = core(r['name']); fs = [f'{b}{k}.jpg' for k in (1, 2, 3) if os.path.exists(os.path.join(folder, f'{b}{k}.jpg'))]
        img = ' '.join(f'[{k}]({f})' for k, f in enumerate(fs, 1)) if fs else '暂无'
        ck = f"{CITY}|{r['dist']}|{r['town']}|{r['name']}"
        nm = f"{r['name']} [?]({CQ[ck]})" if ck in CQ else r['name']
        L.append('| ' + ' | '.join([str(i), r['town'], nm, r['struct'], r['len'], r['era'] or '—', (r['loc'] or '—').replace('|', '／'), r['level'], r['doc'], img]) + ' |')
    notes = [f'{r["name"]}：{r["note"]}。' for r in rs if r['note']]
    notes += ([f'{CITY}文物保护点以浙江省文物局《全省文物保护点》统计表为准（原件存于本项目 文保名录/浙江省/）。'] if ZJ else [f'{PROV}没有找到公开的文物保护点统计表，未定级的古桥只收录了老百晓集桥上的（尚未定级，待核实）。']) + [
              '国保、省保、市保、县保依据维基百科整理，还没有核对政府原件；市保、县保名单可能不完整。',
              '成组公布的文物（如古桥群）按单桥列出，组名写在文保等级里。',
              '乡镇、结构、长度标“—”的，是没有查到可靠资料；部分结构、长度、年代来自“老百晓集桥”网站。']
    L += ['', '## 说明', ''] + [f'- {n}' for n in notes] + ['', '## 来源', '']
    L += [f'- [{SN(u)}]({u})' for u in dict.fromkeys(r['src'] for r in rs)]
    fs = sorted(k for k in IMG if k.startswith(d + '/') and os.path.exists(os.path.join(ROOT, k)))
    if fs: L += ['', '## 图片来源', '', '| 图片 | 来源 |', '|---|---|'] + [f'| [{k.split("/")[1]}]({k.split("/")[1]}) | {IMG[k]} |' for k in fs]
    open(os.path.join(folder, f'{d}古桥.md'), 'w').write('\n'.join(L) + '\n')
    print(d, len(rs))
