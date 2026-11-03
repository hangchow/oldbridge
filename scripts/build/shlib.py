# 上海市不可移动文物名录（上海图书馆开放数据平台“上海年华”，3452条）里的桥：sh/rows.json 生成后执行。
# 已收但等级偏低的（尚未定级、登记不可移动文物；文物保护点而名录为区保/市保的）改为名录等级；没收的补上。
# “××水桥”是河埠头踏步，不是桥；遗址、碑、碉堡等也不收。
import json, os, re
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = '../../文保名录/上海市/上海市不可移动文物名录（上海图书馆开放数据平台，含“桥”条目）.txt'
SN = '上海市不可移动文物名录（上海图书馆开放数据平台“上海年华”）'
HOLES = json.load(open(S + '/build/cq_holes.json')) if os.path.exists(S + '/build/cq_holes.json') else {}
LENF = json.load(open(S + '/build/cq_len_fill.json')) if os.path.exists(S + '/build/cq_len_fill.json') else {}
NB = re.compile(r'水桥$|遗址|旧址|碑|碉堡|堂|坊|宅|监狱|疗养院|医院|驳岸')
def core(n): return re.sub(r'（.*?）|\s', '', n)
def town(a):
    m = re.match(r'^(.{1,8}?(?:镇|街道|乡|新区|工业区|旅游区|社区))', a or '')
    t = m.group(1) if m else '—'
    return {'拓林镇': '柘林镇', '安亨镇': '安亭镇', '白銪镇': '白鹤镇', '盧固镇': '重固镇', '四渡街道': '西渡街道', '嘉定工业区': '工业区'}.get(t, t)
LV = {'点': None, '区保': '区级文物保护单位', '市保': '上海市文物保护单位', '国保': '全国重点文物保护单位'}
RANK = lambda L: 0 if L.startswith('全国') else 1 if L.startswith('上海市文物保护单位') else 2 if '文物保护单位' in L else 3 if '文物保护点' in L else 4
p = S + '/sh/rows.json'; R = json.load(open(p))
seen = set(); up = add = 0
for line in open(S + '/build/sh_relic_bridges.psv'):
    if not line.strip(): continue
    d, n, lv, a = line.rstrip('\n').split('|')[:4]
    n = n.strip(); lv = lv.split(';')[0].strip(); dist = d + ('新区' if d == '浦东' else '区'); tw = town(a)
    if (dist, n, tw) in seen or NB.search(n) or not re.search(r'桥(（[^）]*）)?$', n): continue
    seen.add((dist, n, tw))
    lvtxt = LV[lv] or (dist + '文物保护点')
    c = core(n)
    cand = [r for r in R if r['dist'] == dist and (core(r['name']) == c or core(r['name']).startswith(c + '又名'))]
    if not cand:   # 名录在桥名前加了地名（“新场西仓桥”“宣桥永安桥”），仓库只写桥名
        cand = [r for r in R if r['dist'] == dist and len(core(r['name'])) >= 2 and c.endswith(core(r['name'])) and 2 <= len(c) - len(core(r['name'])) <= 5 and r['town'] in (tw, '—')]
    if len(cand) > 1: cand = [r for r in cand if r['town'] == tw] or cand
    if cand:
        r = cand[0]; L = r['level']
        if L.startswith(('尚未定级', '登记不可移动')) or RANK(lvtxt) < RANK(L):
            r['note'] = re.sub(r'不在文保名录中，|，等级待核实', '', r.get('note') or '')
            r['note'] = (r['note'] + '；' if r['note'] else '') + f'等级据{SN}（原记为{L}）'
            r['level'] = lvtxt; r['src'] = SRC; up += 1
            if r['town'] == '—' and tw != '—': r['town'] = tw
        continue
    key = f'上海市|{dist}|{tw}|{n}'
    R.append(dict(dist=dist, town=tw, name=n, era='—', loc=a or '—', level=lvtxt, doc='—', src=SRC, note='据' + SN, struct=HOLES.get(key, '—'), len=LENF.get(key, '—')))
    add += 1
json.dump(R, open(p, 'w'), ensure_ascii=False, indent=0)
print('upgraded', up, 'added', add)
