# -*- coding: utf-8 -*-
# 上海市古桥名录生成（两级目录：上海市/区/区古桥.md）
import json, os, re
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
CQ = json.load(open(S + '/build/cqlinks.json')) if os.path.exists(S + '/build/cqlinks.json') else {}  # 老百晓集桥链接
ROOT = '/Users/sean/workspace/oldbridge/上海市'
DISTS = ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区']
W = lambda p: 'https://zh.wikipedia.org/wiki/' + p
SRCNAME = {W('上海市文物保护单位'): '维基百科：上海市文物保护单位'}
for d in DISTS: SRCNAME[W(d + '文物保护单位')] = f'维基百科：{d}文物保护单位'
def SN(u): return SRCNAME.get(u) or ('老百晓集桥：' + u.rsplit('/', 1)[-1] if 'china-qiao' in u else u)
def load(p): return json.load(open(p)) if os.path.exists(p) else {}
ST, LN, IMG = load(S + '/sh/struct.json'), load(S + '/sh/len.json'), load(S + '/sh/imgsrc.json')
R = []
def e(dist, town, name, era, loc, level, doc, src, note=''):
    k = f'{dist}|{town}|{name}'
    R.append(dict(dist=dist, town=town, name=name, era=era, loc=loc, level=level, doc=doc, src=src, note=note, struct=ST.get(k, '—'), len=LN.get(k, '—')))
# 上海市文物保护单位
M = W('上海市文物保护单位')
e('静安区', '北站街道', '浙江路桥', '1907年', '浙江中路与浙江北路连接处，跨苏州河', '上海市文物保护单位（第八批）', '2014年4月4日公布', M, '', )
e('松江区', '永丰街道', '大仓桥', '明天启六年（1626）', '中山西路仓桥弄南', '上海市文物保护单位（第八批）', '2014年4月4日公布', M, '1985年先列为区级文物保护单位')
e('松江区', '中山街道', '望仙桥', '南宋', '中山东路235号内', '上海市文物保护单位（第八批归并）', '2014年4月4日公布', M, '1985年先列为区级文物保护单位')
e('青浦区', '朱家角镇', '放生桥', '明隆庆五年（1571）始建，清嘉庆十七年（1812）重建', '北大街东首，跨漕港', '上海市文物保护单位（第四批）', '1987年11月17日公布', M)
e('青浦区', '金泽镇', '普济桥', '南宋咸淳元年（1265）', '南市梢', '上海市文物保护单位（第四批）', '1987年11月17日公布', M)
e('青浦区', '金泽镇', '迎祥桥', '明天顺六年（1462）', '金溪居委会（南市梢）', '上海市文物保护单位（第八批）', '2014年4月4日公布', M, '1959年先列为区级文物保护单位')
# 区级文物保护单位
EXCL = re.compile('杀人塘|纪念|花园|坊$|司令部|宫$|山$|楼$|海塘|堂$|园$|就义|驳岸')
rows = json.load(open(S + '/sh/wiki_rows.json'))
for src, sec, cells, files in rows:
    d = src.replace('文物保护单位', '')
    if d not in DISTS or len(cells) < 3: continue
    name = cells[0].replace('colspan="2"|', '').strip()
    if EXCL.search(name) or not re.search(r'桥(（.*）|\(.*\))?$', name): continue
    loc = cells[1]; date = cells[2] if re.match(r'^[0-9]', cells[2]) else '—'
    loc = re.sub(r'^' + d, '', loc)
    m = re.match(r'^(.{1,6}?(?:镇|街道|乡))', loc)
    FIX = [('七宝古镇', '七宝镇'), ('嘉定镇', '嘉定镇街道'), ('嘉定', '嘉定镇街道'), ('安亭', '安亭镇'), ('南翔', '南翔镇'), ('外冈', '外冈镇'), ('西渡', '西渡街道')]
    town = next((v for k, v in FIX if loc.startswith(k)), None) or (m.group(1) if m else '—')
    if any(r['dist'] == d and re.sub(r'（.*', '', r['name']) == re.sub(r'（.*', '', name) for r in R): continue
    e(d, town, name, '—', loc, '区级文物保护单位', (date + '公布') if date != '—' else '—', W(src))
def core(n): return re.sub(r'（.*?）|\(.*?\)|\s', '', n)
ARCH = 'https://web.archive.org/web/2014/http://wgj.sh.gov.cn/wgj/node1257/node1264/'
SRCNAME[ARCH] = '上海市文广影视局：区县级文物保护单位、登记不可移动文物（2011，网页存档）'
for a in json.load(open(S + '/sh/arch_bridges.json')):
    d, name, loc = a['dist'], a['name'], re.sub('^' + a['dist'], '', a['addr'])
    if any(r['dist'] == d and core(r['name']) == core(name) and (r['town'] == '—' or r['town'][:2] in loc) for r in R): continue
    m = re.match(r'^(.{1,6}?(?:镇|街道|乡))', loc)
    town = m.group(1) if m else '—'
    lv = '登记不可移动文物' if a['sec'] == '登记不可移动文物' else '区级文物保护单位'
    e(d, town, name, '—', loc, lv, (a['date'] + '公布') if a['date'] else '—', ARCH)
# 维基“金山区不可移动文物列表”的“未定级不可移动文物”一节（据金山区第三次全国文物普查登录点告知函，2013）里有、上面没收的桥
JSW = 'https://zh.wikipedia.org/wiki/金山区不可移动文物列表'
e('金山区', '漕泾镇', '彩虹桥', '清光绪三年（1877）', '漕泾镇金光村20组', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '漕泾镇', '连塘桥', '清乾隆十五年（1750）', '漕泾镇护塘村7组1039号西侧', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '漕泾镇', '闸桥', '清同治十二年', '漕泾镇护塘村1050号东侧', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '金山卫镇', '迎龙桥', '民国十六年（1927）', '金山卫镇农建村7组', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '廊下镇', '彩虹桥', '清代', '廊下镇南塘村14组3113号西20米', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '金山工业区', '同乐桥', '民国二十五年（1936）', '金山工业区欢兴村3组2025号东北侧20米', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '金山工业区', '西陈行桥', '民国二十四年（1935）', '金山工业区欢兴村2组3008号北500米', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '金山工业区', '第一桥', '—', '金山工业区立新村8组3003号北250米', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '金山工业区', '华秀桥', '—', '金山工业区高楼村2组1082号南10米', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '金山工业区', '永懋桥', '清宣统元年（1909）', '金山工业区运河村4组', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '金山工业区', '东风桥', '民国六年（1917）', '金山工业区高楼村2组', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '亭林镇', '太平桥', '民国十三年（1924）', '亭林镇驳岸村8组5096号东南20米', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '亭林镇', '亭林小石桥', '清光绪二十九年（1903）', '亭林镇复兴居委会和平南路40弄1号', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '张堰镇', '亿寿桥', '清代', '张堰镇百家村', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('金山区', '朱泾镇', '启秀桥', '清嘉庆十八年（1813）', '朱泾镇待泾村', '登记不可移动文物（金山区第三次全国文物普查登录点）', '2013年告知', JSW)
e('松江区', '中山街道', '杜公祠桥', '—', '中山东路250号', '区级文物保护单位', '2013年6月8日公布', 'https://zh.wikipedia.org/wiki/松江区各级文物保护单位列表')
# 不在文保名录、老百晓集桥收录的古桥（尚未定级，待核实；build/unlisted.py）
for u in (json.load(open(S + '/build/unlisted.json')).get('上海市', []) if os.path.exists(S + '/build/unlisted.json') else []):
    if not any(x['dist'] == u['dist'] and re.sub(r'（.*?）', '', x['name']) == u['name'] for x in R): R.append(dict(u, struct='—', len='—'))
# 结构为“—”或只写桥型、没有孔数的，按老百晓集桥页面补桥型和孔数（build/cqholes.py）
HOLES = json.load(open(S + '/build/cq_holes.json')) if os.path.exists(S + '/build/cq_holes.json') else {}
LENF = json.load(open(S + '/build/cq_len_fill.json')) if os.path.exists(S + '/build/cq_len_fill.json') else {}
for r in R:
    hk = '上海市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
    if hk in HOLES and ((r.get('struct') or '—') == '—' or re.fullmatch(r'石?(拱|梁)桥|石板桥|平桥|廊桥', r['struct'])): r['struct'] = HOLES[hk]
    if hk in LENF and (r.get('len') or '—') in ('—', ''): r['len'] = LENF[hk]
# 时代只写朝代或“—”的，按老百晓集桥、云端档案补具体年代（build/erafill.py）
EF = json.load(open(S + '/build/era_fill.json')) if os.path.exists(S + '/build/era_fill.json') else {}
for r in R:
    ek = '上海市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
    if ek in EF and (r['era'] or '—') == EF[ek]['old']:
        f = EF[ek]; old = r['era'] or '—'
        ds = [d for d in ('宋', '元', '明', '清', '民国') if d in old.replace('中华民国', '民国')]
        r['era'] = f['era'] if all(d in f['era'] for d in ds) else old + '；' + f['era']
        src = '老百晓集桥' if f['src'] == 'cq' else '杭州市文物遗产与历史建筑保护中心云端档案'
        r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'具体年代据{src}（名录原写“{old}”）'

json.dump(R, open(S + '/sh/rows.json', 'w'), ensure_ascii=False, indent=0)
for d in DISTS:
    folder = os.path.join(ROOT, d); os.makedirs(folder, exist_ok=True)
    rs = sorted([r for r in R if r['dist'] == d], key=lambda r: (0 if r['level'].startswith('上海市') else 1 if r['level'].startswith('区级') else 2, r['town'] in ('—', ''), r['town']))
    if not rs:
        open(os.path.join(folder, f'{d}古桥.md'), 'w').write(f'# 上海市{d}不可移动文物：桥梁\n\n上海市文物保护单位和{d}区级文物保护单位名录里没有桥梁。嘉定、崇明、虹口的登记不可移动文物名单暂缺。\n')
        print(d, 0); continue
    L = [f'# 上海市{d}不可移动文物：桥梁', '', '| 序号 | 乡镇 | 桥名 | 结构 | 长度 | 时代 | 位置 | 文保等级 | 公布文件 | 图片 |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(rs, 1):
        b = core(r['name']); fs = [f'{b}{k}.jpg' for k in (1, 2, 3) if os.path.exists(os.path.join(folder, f'{b}{k}.jpg'))]
        img = ' '.join(f'[{k}]({f})' for k, f in enumerate(fs, 1)) if fs else '暂无'
        L.append('| ' + ' | '.join([str(i), r['town'], (f"{r['name']} [?]({CQ[k]})" if (k := '上海市|' + r['dist'] + '|' + r['town'] + '|' + r['name']) in CQ else r['name']), r['struct'], r['len'], r['era'] or '—', r['loc'] or '—', r['level'], r['doc'], img]) + ' |')
    notes = [f'{r["name"]}：{r["note"]}。' for r in rs if r['note']]
    notes += ['区级文物保护单位的时代，维基百科列表里没有写，暂标“—”。', '乡镇一列按名录地址提取，个别只写到老街、地块的保留原文。',
              '登记不可移动文物取自上海市文广影视局 2011 年公布的各区县名单（网页存档）；嘉定、崇明、虹口三区的名单存档无法获取，暂缺。', '结构、长度标“—”的，是没有查到可靠资料。']
    L += ['', '## 说明', ''] + [f'- {n}' for n in notes] + ['', '## 来源', '']
    srcs = []
    for r in rs:
        if r['src'] not in srcs: srcs.append(r['src'])
    L += [f'- [{SN(u)}]({u})' for u in srcs]
    fs = sorted(k for k in IMG if k.startswith(d + '/') and os.path.exists(os.path.join(ROOT, k)))
    if fs:
        L += ['', '## 图片来源', '', '| 图片 | 来源 |', '|---|---|'] + [f'| [{k.split("/")[1]}]({k.split("/")[1]}) | {IMG[k]} |' for k in fs]
    L += ['']
    open(os.path.join(folder, f'{d}古桥.md'), 'w').write('\n'.join(L))
    print(d, len(rs))
