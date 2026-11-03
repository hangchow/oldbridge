# 浙江省文物局《浙江省市县级文物保护单位名录》（2023年7月19日，5262处）里的桥：
# 各市 rows.json 生成后执行——已收但等级偏低（尚未定级、文保点、历史建筑、一般不可移动文物）的改为市保/县保；没收的补上。
# 桥的清单（已按名称拆分古桥群、去掉遗址等）在 build/zjsx_bridges.json；杭州的数据已与名录一致，不处理。
import json, os, re
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = '../../文保名录/浙江省/浙江省市县级文物保护单位名录（5262处，浙江省文物局2023年7月19日发布）.xlsx'
SN = '浙江省文物局《浙江省市县级文物保护单位名录》（2023年7月19日）'
B = json.load(open(S + '/build/zjsx_bridges.json'))
K = {'湖州市': 'huz', '嘉兴市': 'jx', '金华市': 'jh', '绍兴市': 'sx', '宁波市': 'nb', '衢州市': 'qz', '台州市': 'tz', '温州市': 'wz', '丽水市': 'ls', '舟山市': 'zs'}
CITYDOC = {'湖州市': ('湖政',), '嘉兴市': ('嘉政',), '金华市': ('金政', '金华地区行署'), '绍兴市': ('绍政', '绍市'), '宁波市': ('甬政',), '衢州市': ('衢政',), '台州市': ('台政', '台州地区行署'), '温州市': ('温政',), '丽水市': ('丽政', '丽水地区行署', '丽地署'), '舟山市': ('舟政', '舟山地区行署', '行署')}   # 各市市级文号前缀
LOW = ('尚未定级', '一般不可移动', '未定级', '历史建筑')
HOLES = json.load(open(S + '/build/cq_holes.json')) if os.path.exists(S + '/build/cq_holes.json') else {}
LENF = json.load(open(S + '/build/cq_len_fill.json')) if os.path.exists(S + '/build/cq_len_fill.json') else {}
def core(n): return re.sub(r'（.*?）|\(.*?\)|\s', '', n)
def tw(t, d): return re.sub('^' + re.escape(d), '', re.sub(r'^.{2,4}(区|县|市)(?=.{2,}(镇|乡|街道)$)', '', t or '')) or '—'
SAME = {('长兴县', '长兴鸿桥'): '鸿桥', ('海曙区', '清垫夹塘及古桥'): '古桥', ('江北区', '慈城王桥'): '王桥', ('瑞安市', '仙降区林垟大桥'): '大桥', ('平阳县', '联安桥'): '联安石板桥'}   # 名录名称与仓库写法不同、核对地址为同一座桥
n_up = n_add = 0
for c, k in K.items():
    p = f'{S}/{k}/rows.json'; R = json.load(open(p))
    for b in [x for x in B if x['city'] == c]:
        doc = re.sub(r'\s+', '、', b['doc'].strip()) or '—'
        lv = (c if doc.startswith(CITYDOC[c]) else b['dist']) + '文物保护单位'
        lvtxt = lv + ('（' + ('“' + b['group'] + '”组成部分，' if b['group'] else '') + doc + '）' if doc != '—' else '')
        n = core(b['name']); bt = tw(b['town'], b['dist'])
        sm = SAME.get((b['dist'], b['name']))
        cand = [r for r in R if r['dist'] == b['dist'] and r['name'] == sm] if sm else [r for r in R if r['dist'] == b['dist'] and (core(r['name']) == n or (len(n) >= 2 and core(r['name']).endswith(n) and len(core(r['name'])) - len(n) <= 4) or (len(core(r['name'])) >= 3 and n.endswith(core(r['name']))))]
        if len(cand) > 1:
            v = b['vil']
            cand = [r for r in cand if v and (v[:-1] in r['name'] or v[:-1] in (r.get('loc') or ''))] or [r for r in cand if r['town'] == bt] or [r for r in cand if core(r['name']) == n] or cand
        note = '据' + SN
        if cand:
            r = cand[0]; L = r['level']
            if L.startswith(('全国', '浙江省')): continue
            if L.startswith(LOW) or '文物保护点' in L or '文物控制' in L:
                r['note'] = re.sub(r'不在文保名录中，|维基百科名单未收，|，等级待核实', '', r.get('note') or '')
                r['note'] = (r['note'] + '；' if r['note'] else '') + f'等级、文号{note}（原记为{L}）'
                r['level'] = lvtxt; r['doc'] = doc; r['src'] = SRC; n_up += 1
            elif L.startswith(c + '文物保护单位') and not lvtxt.startswith(c):   # 只升不降：原记市保、名录文号为县级的，保持原等级
                r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'{SN}记为{lvtxt}'
            elif '待核对政府原件' in L or '据老百晓集桥' in L or '据博雅地名网' in L or (not re.search('〔|批', L) and doc != '—'):
                r['note'] = re.sub(r'维基百科名单未收，|不在文保名录中，', '', r.get('note') or '')
                r['note'] = (r['note'] + '；' if r['note'] else '') + f'等级、文号{note}'
                r['level'] = lvtxt; r['doc'] = doc; r['src'] = SRC; n_up += 1
            elif (r.get('doc') or '—') == '—':
                r['doc'] = doc
            continue
        name = b['name'] if not b['vil'] or any(core(x['name']) == n for x in R if x['dist'] == b['dist']) is False else b['name']
        if b['vil'] and any(core(x['name']) == n and x['dist'] == b['dist'] for x in R + []): name = b['vil'] + b['name']
        if re.match(r'(19[5-9]\d|20\d\d)|中华人民共和国|现代|当代', b['era'] or ''): continue   # 1949年以后修建的不收
        key = f"{c}|{b['dist']}|{bt}|{name}"
        R.append(dict(dist=b['dist'], town=bt, name=name, era=b['era'] or '—', loc=(b['vil'] + '，' if b['vil'] else '') + (b['loc'] or '—'),
                      src=SRC, doc=doc, level=lvtxt, struct=HOLES.get(key, '—'), len=LENF.get(key, '—'),
                      note=note + ('，名录原名“' + b['orig'] + '”' if b['orig'] != b['name'] else '')))
        n_add += 1
    json.dump(R, open(p, 'w'), ensure_ascii=False, indent=0)
print('upgraded', n_up, 'added', n_add)
