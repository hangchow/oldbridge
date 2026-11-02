# -*- coding: utf-8 -*-
# 时代为“—”或只写朝代的，从老百晓集桥页面、云端档案简介里提取建造年代
import json, re, os, sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
sys.path.insert(0, S + '/build'); from era import year
CQ = json.load(open(S + '/build/cqlinks.json'))
R = json.load(open(S + '/singdo/recs.json')); R = R.values() if isinstance(R, dict) else R
SDI = {x['id']: x for x in R if isinstance(x, dict)}
F = {'杭州市': 'build/all_rows.json', '湖州市': 'huz/rows.json', '嘉兴市': 'jx/rows.json', '上海市': 'sh/rows.json', '苏州市': 'sz/rows.json', '金华市': 'jh/rows.json', '绍兴市': 'sx/rows.json', '宁波市': 'nb/rows.json', '衢州市': 'qz/rows.json', '台州市': 'tz/rows.json', '温州市': 'wz/rows.json', '丽水市': 'ls/rows.json', '舟山市': 'zs/rows.json'}
RG = {'宋': '建隆 乾德 开宝 太平兴国 雍熙 端拱 淳化 至道 咸平 景德 大中祥符 天禧 乾兴 天圣 明道 景祐 宝元 康定 庆历 皇祐 至和 嘉祐 治平 熙宁 元丰 元祐 绍圣 元符 建中靖国 崇宁 大观 政和 重和 宣和 靖康 建炎 绍兴 隆兴 乾道 淳熙 绍熙 庆元 嘉泰 开禧 嘉定 宝庆 绍定 端平 嘉熙 淳祐 宝祐 开庆 景定 咸淳 德祐',
      '元': '至元 元贞 大德 至大 皇庆 延祐 至治 泰定 致和 天历 至顺 元统 至正',
      '明': '洪武 建文 永乐 洪熙 宣德 正统 景泰 天顺 成化 弘治 正德 嘉靖 隆庆 万历 泰昌 天启 崇祯',
      '清': '顺治 康熙 雍正 乾隆 嘉庆 道光 咸丰 同治 光绪 宣统', '民国': '民国'}
REIGN = {r: d for d, s in RG.items() for r in s.split()}
NUM = r'(?:元|[一二三四五六七八九十廿卅〇零]{1,4}|\d{1,2})'
VERB = r'(建桥年代|建造年代|始建年代|始建|初建|创建|重建|重修|修建|建造|建成|落成|改建|建)'
PAT = re.compile(r'(?:(?:宋|南宋|北宋|元|明|清|大明|大清|皇元)代?)?(' + '|'.join(sorted(REIGN, key=len, reverse=True)) + r')' + r'(?:' + NUM + r'年|年间)(?:[（(]?(?:公元)?\s*(\d{4})\s*年?[)）]?)?[^，。；]{0,6}?' + VERB)
PAT2 = re.compile(r'(始建|初建|创建|重建|重修|修建|建造|建成|落成|改建|建|建桥年代|建造年代|始建年代)' + r'(?:于|在|为|是)(?:(?:宋|南宋|北宋|元|明|清|大明|大清)代?)?(' + '|'.join(sorted(REIGN, key=len, reverse=True)) + r')(' + NUM + r'年|年间)(?:[（(]?(?:公元)?\s*(\d{4})\s*年?[)）]?)?')
def text(k, r):
    ts = []
    if k in CQ:
        f = S + '/cqv/' + CQ[k].split('china-qiao.com/')[1].replace('/', '_')
        if not os.path.exists(f) or os.path.getsize(f) == 0:   # 缓存没有就抓
            import subprocess, time; os.makedirs(S + '/cqv', exist_ok=True)
            subprocess.run(['curl', '-sL', '-m', '30', '-A', 'Mozilla/5.0', '-o', f, CQ[k]]); time.sleep(0.2)
        if os.path.exists(f):
            t = re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', open(f, 'rb').read().decode('gb18030', 'ignore'))))
            i = t.find('篇 '); ts.append(('cq', (t[i:] if i >= 0 else t).split('上一座')[0]))
    if r.get('sdl'):
        sid = r['sdl'].split('/')[-1].split('_')[0]
        if sid in SDI and sid not in ('168', '185', '325', '564'): ts.append(('sd', SDI[sid].get('intro', '')))   # 成组档案的简介不是单座桥的
    return ts
def need(e): return (not e) or e in ('—', '不详', '待定') or (year(e) and not year(e)[1])
OUT = {}
for c, p in F.items():
    for r in json.load(open(S + '/' + p)):
        k = f"{c}|{r['dist']}|{r['town']}|{r['name']}"
        if not need(r['era']): continue
        for src, t in text(k, r):
            ms = []
            for m in PAT.finditer(t):
                ms.append((m.start(), m.group(0), REIGN[m.group(1)], m.group(3)))
            for m in PAT2.finditer(t):
                ms.append((m.start(), m.group(0), REIGN[m.group(2)], m.group(1)))
            ms.sort()
            if ms:
                OUT.setdefault(k, {'era': r['era'], 'src': src, 'hits': []})['hits'] += [(x[1], x[2], x[3]) for x in ms[:4]]
                break
json.dump(OUT, open(S + '/build/erafill_raw.json', 'w'), ensure_ascii=False, indent=1)
print(len(OUT))

# ---------- 第二步：整理成“时代”一列的写法 ----------
START = dict(建隆=960, 乾德=963, 开宝=968, 太平兴国=976, 雍熙=984, 端拱=988, 淳化=990, 至道=995, 咸平=998, 景德=1004, 大中祥符=1008, 天禧=1017, 乾兴=1022, 天圣=1023, 明道=1032, 景祐=1034, 宝元=1038, 康定=1040, 庆历=1041, 皇祐=1049, 至和=1054, 嘉祐=1056, 治平=1064, 熙宁=1068, 元丰=1078, 元祐=1086, 绍圣=1094, 元符=1098, 建中靖国=1101, 崇宁=1102, 大观=1107, 政和=1111, 重和=1118, 宣和=1119, 靖康=1126, 建炎=1127, 绍兴=1131, 隆兴=1163, 乾道=1165, 淳熙=1174, 绍熙=1190, 庆元=1195, 嘉泰=1201, 开禧=1205, 嘉定=1208, 宝庆=1225, 绍定=1228, 端平=1234, 嘉熙=1237, 淳祐=1241, 宝祐=1253, 开庆=1259, 景定=1260, 咸淳=1265, 德祐=1275,
             元贞=1295, 大德=1297, 至大=1308, 皇庆=1312, 延祐=1314, 至治=1321, 泰定=1324, 致和=1328, 天历=1328, 至顺=1330, 元统=1333, 至正=1341,
             洪武=1368, 建文=1399, 永乐=1403, 洪熙=1425, 宣德=1426, 正统=1436, 景泰=1450, 天顺=1457, 成化=1465, 弘治=1488, 正德=1506, 嘉靖=1522, 隆庆=1567, 万历=1573, 泰昌=1620, 天启=1621, 崇祯=1628,
             顺治=1644, 康熙=1662, 雍正=1723, 乾隆=1736, 嘉庆=1796, 道光=1821, 咸丰=1851, 同治=1862, 光绪=1875, 宣统=1909, 民国=1912)
CN = dict(zip('〇零一二三四五六七八九', [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
def cnum(s):
    if s == '元': return 1
    if s.isdigit(): return int(s)
    s = s.replace('廿', '二十').replace('卅', '三十')
    if '十' in s:
        a, b = s.split('十', 1); return (CN.get(a, 1) if a else 1) * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s, None) if len(s) == 1 else None
SKIP_SD = {'168', '185', '325', '564'}   # 成组档案，简介里的年代不是单座桥的
VN = {'建桥年代': '建', '建造年代': '建', '始建年代': '始建', '始建': '始建', '初建': '始建', '创建': '始建', '建': '建', '建造': '建', '建成': '建成', '落成': '建成', '重建': '重建', '改建': '改建', '重修': '重修', '修建': '建'}
RE1 = re.compile(r'(' + '|'.join(sorted(START, key=len, reverse=True)) + r')(' + NUM + r')?年(间)?')
def zh(s):
    # 年号后的阿拉伯数字改成汉字（括号里的公元年不动）
    D = '〇一二三四五六七八九'
    def f(m):
        n = int(m.group(1))
        t = ('' if n < 10 else ('十' if n < 20 else D[n // 10] + '十')) + (D[n % 10] if n % 10 or n < 10 else '')
        return t + '年'
    return re.sub(r'(?<![（\d])(\d{1,2})年', f, s)
def parse(ph):
    m = RE1.search(ph)
    if not m: return None
    rg = m.group(1); d = REIGN[rg]
    dn = ('南宋' if START[rg] >= 1127 else '北宋') if d == '宋' else d   # 显示用
    vb = re.findall(VERB, ph); vb = VN.get(vb[-1] if ph.find(m.group(0)) < ph.find(vb[-1]) else vb[0], '建') if vb else '建'
    if m.group(3) or not m.group(2):
        return (START[rg], f"{'' if d == '民国' else dn}{rg}年间{vb}", d)
    n = cnum(m.group(2))
    if n is None: return None
    g = re.search(r'(\d{4})', ph[m.end():m.end() + 14])
    if rg == '至元':   # 前后两个至元，只认原文给出的公元年
        if not g: return None
        y = int(g.group(1))
    else:
        y = START[rg] + n - 1
        if g and abs(int(g.group(1)) - y) > 1: return None   # 原文换算不一致，不采用
    return (y, f"{'' if d == '民国' else dn}{rg}{m.group(2)}年（{y}）{vb}", d)
DYS = ['宋', '元', '明', '清', '民国']
FILL = {}
from collections import Counter
SHARED = {u for u, n in Counter(CQ[k] for k in OUT if k in CQ).items() if n > 1}   # 一页写几座桥的（如周庄双桥），分不清说的是哪座
for k, v in OUT.items():
    if v['src'] == 'cq' and CQ.get(k) in SHARED: continue
    if v['src'] == 'sd' and any(f'/{i}_' in k for i in SKIP_SD): continue
    off = v['era']
    offd = [d for d in DYS if d in (off or '').replace('中华民国', '民国')] if off and off not in ('—', '不详', '待定') else []
    ps = []
    for ph, d, _ in v['hits']:
        p = parse(ph)
        if not p: continue
        if offd and p[2] not in offd: continue
        ps.append(p)
    # 同一年只留一条；“始建/建”说法不止一种的（页面自相矛盾），都不用
    BUILD = ('始建', '建', '建成')
    b = {x[1].rsplit('）', 1)[0] if '）' in x[1] else x[1][:-2] for x in ps if x[1].endswith(BUILD) and not x[1].endswith(('重建', '改建'))}
    reb = [x[0] for x in ps if x[1].endswith(('重建', '改建', '重修'))]
    ps = [x for x in ps if not (x[1].endswith(BUILD) and not x[1].endswith(('重建', '改建')) and reb and x[0] > min(reb))]   # “建”比重建还晚的，说法可疑，不用
    out, seen = [], set()
    for x in sorted(ps):
        isb = x[1].endswith(BUILD) and not x[1].endswith(('重建', '改建'))
        if isb and len({x[0] for x in ps if x[1].endswith(BUILD) and not x[1].endswith(('重建', '改建'))}) > 1: continue
        key = x[0] if '年间' not in x[1] else x[1][:-2]
        if key in seen: continue
        seen.add(key); out.append(x)
    if not out: continue
    FILL[k] = dict(old=off, era=zh('，'.join(x[1] for x in out[:3])).replace('廿', '二十').replace('卅', '三十'), src=v['src'])
json.dump(FILL, open(S + '/build/era_fill.json', 'w'), ensure_ascii=False, indent=1)
print('fill', len(FILL))
