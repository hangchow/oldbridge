# -*- coding: utf-8 -*-
# 对比老百晓集桥各市目录与项目：找出没对上的古桥页面，分为“项目已有（补链接）”和“不在名录（新增待核实）”
import json, re, os, subprocess, time, sys, collections
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
CITY = {'湖州市': ('huz', 'hzql/'), '嘉兴市': ('jx', 'jxql/'), '上海市': ('sh', ''), '苏州市': ('sz', ''), '金华市': ('jh', ''),
        '绍兴市': ('sx', ''), '宁波市': ('nb', ''), '衢州市': ('qz', ''), '台州市': ('tz', ''), '温州市': ('wz', ''), '丽水市': ('ls', ''), '舟山市': ('zs', ''), '无锡市': ('wx', ''), '南京市': ('nj', ''), '常州市': ('cz', ''), '镇江市': ('zjs', ''), '扬州市': ('yz', '')}
DISTS = {'湖州市': ['吴兴区', '南浔区', '德清县', '长兴县', '安吉县'], '嘉兴市': ['南湖区', '秀洲区', '嘉善县', '平湖市', '海盐县', '海宁市', '桐乡市'],
         '上海市': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区'],
         '苏州市': ['姑苏区', '虎丘区', '吴中区', '相城区', '吴江区', '苏州工业园区', '常熟市', '张家港市', '昆山市', '太仓市'],
         '金华市': ['婺城区', '金东区', '兰溪市', '东阳市', '义乌市', '永康市', '浦江县', '武义县', '磐安县']}
for c, cf in json.load(open(S + '/zj/cities.json')).items(): DISTS[c] = cf['dists']
CQ = json.load(open(S + '/build/cqlinks.json'))
MOD = re.compile(r'大桥|高架|隧道|立交|互通|铁路|公路|高速|地铁|枢纽|跨线|天桥|匝道|快速|大道|钢|复线|一桥|二桥|三桥|四桥|绿道|栈道|玻璃|悬索|索桥|路桥|人行桥|景区|公园|湿地|水泥|闸桥$|码头|河桥$|江桥$|港桥$|塘桥$|运河桥|新桥$|跨海|机场|渡槽|浮桥')
OLD = re.compile(r'(宋|元代|元朝|明代|明朝|清代|清朝|民国|乾隆|康熙|嘉庆|道光|光绪|同治|咸丰|雍正|宣统|顺治|万历|嘉靖|洪武|正德|弘治|成化|天启|崇祯|隆庆|永乐|宣德|正统|景泰|天顺|至正|绍兴|淳熙|嘉定|咸淳|宝祐)')
NEWB = re.compile(r'(19[5-9]\d|20[0-2]\d)年?[^，。]{0,12}(重建|新建|改建|建成|拆除|拆建|翻建|拓宽|移建)|钢筋|混凝土|水泥桥|已拆|被拆|消失|不存|已毁|毁于')
STONE = re.compile(r'石拱|石梁|石板桥|条石|青石|花岗|古桥')
MODX = re.compile(r'(19[5-9]\d|20[0-2]\d)年?[^，。]{0,10}(建成|新建|建造|竣工|通车)|钢筋|混凝土|钢')
def text(p, base):
    f = S + '/cqv/' + (base + p).replace('/', '_')
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        subprocess.run(['curl', '-sL', '-m', '30', '-A', 'Mozilla/5.0', '-o', f, 'http://www.china-qiao.com/' + base + p]); time.sleep(0.15)
    t = re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', open(f, 'rb').read().decode('gb18030', 'ignore'))))
    i = t.find('篇 '); return (t[i + 2:] if i >= 0 else t).split('上一座')[0]
core = lambda n: re.sub(r'（.*?）|\(.*?\)|\s|^重建', '', n)
OUTALL = json.load(open(S + '/build/compare_raw.json')) if os.path.exists(S + '/build/compare_raw.json') else {}   # 只更新本次运行的城市
for city in sys.argv[1:]:
    key, _ = CITY[city]
    rows = json.load(open(f'{S}/{key}/rows.json'))
    if key == 'sh':
        PY = dict(huangpu88='黄浦区', xuhui88='徐汇区', changning88='长宁区', jingan88='静安区', putuo88='普陀区', hongkou88='虹口区', yangpu88='杨浦区', minhang88='闵行区', baoshan88='宝山区', jiading88='嘉定区', pudong88='浦东新区', jinshan88='金山区', songjiang88='松江区', qingpu88='青浦区', fengxian88='奉贤区', chongming88='崇明区')
        idx = {p: (PY.get(a, '') + t) for p, (a, t) in json.load(open(f'{S}/cq2/sh/idx.json')).items()}; base = ''
    elif key in ('sz', 'wx', 'nj', 'cz', 'zjs', 'yz'): idx = json.load(open(f'{S}/cq2/{key}/idx.json')); base = ''
    elif key in ('huz', 'jx'):
        pre = 'hzql/' if key == 'huz' else 'jxql/'
        idx = {p: t for p, t in json.load(open(f'{S}/cq2/idx.json')).items() if p.startswith(pre)}; base = 'ql15/'
    else: idx = json.load(open(f'{S}/cq2/{key}/idx.json')); base = 'ql15/'
    used = {u.split('china-qiao.com/')[1] for k, u in CQ.items() if k.startswith(city)}
    res = collections.Counter(); out = []
    for p, t in idx.items():
        if base + p in used: res['已链接'] += 1; continue
        if MOD.search(t): res['名称为现代桥'] += 1; continue
        x = text(p, base)
        if not OLD.search(x[:600]):   # 没写古代年代：页面像古石桥的也留下，逐座核对
            if not (STONE.search(x) and not MODX.search(x[:800])): res['没写古代年代'] += 1; continue
            res['没写年代但像古石桥'] += 1
        if NEWB.search(x[:600]): res['现桥为近现代重建/已毁/水泥'] += 1; continue
        tt = re.sub('^' + city, '', t)
        d = next((d for d in DISTS[city] if tt.startswith(d) or tt.startswith(d[:2])), None)
        rest = tt[len(d):] if d and tt.startswith(d) else (tt[2:] if d else tt)
        m = re.match(r'^(.{1,6}?(?:街道|镇|乡))?(.*)$', rest); town = m.group(1) or ''; nm = m.group(2)
        nm2 = re.sub(r'^.{1,4}村', '', nm)
        cand = [r for r in rows if (not d or r['dist'] == d) and (core(r['name']) in (nm, nm2) or (len(nm2) >= 2 and core(r['name']).endswith(nm2)) or (len(core(r['name'])) >= 2 and nm.endswith(core(r['name']))))]
        if town: cand = [r for r in cand if r['town'] in ('—', '') or r['town'][:2] == town[:2]] or cand
        out.append(dict(page=base + p, title=t, dist=d, town=town, name=nm, cand=[(r['dist'], r['town'], r['name']) for r in cand], head=x[:260]))
        res['古桥待处理'] += 1
    pg = {o['page'] for o in out}; out += [o for o in OUTALL.get(city, []) if o['page'] not in pg]   # 保留上次的结果（已收录的页面这次算“已链接”）
    OUTALL[city] = out
    print(city, len(idx), dict(res), '其中项目已有候选', sum(1 for o in out if o['cand']))
json.dump(OUTALL, open(S + '/build/compare_raw.json', 'w'), ensure_ascii=False, indent=1)
