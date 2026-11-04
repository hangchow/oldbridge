# -*- coding: utf-8 -*-
# 苏州市古桥名录生成（两级目录：苏州市/区县/区县古桥.md），以苏州市文广旅局《苏州市各级文物保护单位名录》为基准
import json, os, re
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
CQ = json.load(open(S + '/build/cqlinks.json')) if os.path.exists(S + '/build/cqlinks.json') else {}  # 老百晓集桥链接
ROOT = '/Users/sean/workspace/oldbridge/苏州市'
GOV = '../文保名录/苏州市/苏州市各级文物保护单位名录（苏州市文广旅局，2026）.html'
GOVURL = 'https://wglj.suzhou.gov.cn/szwhgdhlyj/whbf/201906/d7e226cf3cb543a49044ca851d06c12d.shtml'
DM = {'常熟': '常熟市', '昆山': '昆山市', '太仓': '太仓市', '张家港': '张家港市', '工业园区': '苏州工业园区'}
DISTS = ['姑苏区', '虎丘区', '吴中区', '相城区', '吴江区', '苏州工业园区', '常熟市', '张家港市', '昆山市', '太仓市']
def SN(u): return SRCNAME.get(u) or ('老百晓集桥：' + u.rsplit('/', 1)[-1] if 'china-qiao' in u else u)
def load(p): return json.load(open(p)) if os.path.exists(p) else {}
ST, LN, IMG = load(S + '/sz/struct.json'), load(S + '/sz/len.json'), load(S + '/sz/imgsrc.json')
# 名称里带“桥”但不是桥的条目
NOTB = re.compile(r'刻字|试验区|弄|巷|雕花厅|天主堂|民居|墓|石板街|水闸|桥墩|河廊|某宅')
# 成组或合称条目的说明
NOTE = {'垂虹断桥': '原桥七十二孔，长约450米，1967年坍塌；现存东西两端残段约16孔、长约84米（据百度百科“垂虹断桥”）', '双桥及沿河建筑': '“双桥”即周庄世德桥、永安桥，连同沿河建筑一并公布',
        '蠡墅古桥梁': '成组公布的蠡墅一带古桥',
        '八坼古桥梁': '成组公布的八坼一带古桥',
        '太仓石拱桥': '包括州桥、皋桥、周泾桥三座元代石拱桥',
        '斜塘土地庙及永安桥': '与斜塘土地庙一并公布'}
# 地址里没写乡镇（街道）的，按今行政区划补
TF = {'宝带桥': '长桥街道', '垂虹断桥': '松陵街道', '太仓石拱桥': '城厢镇', '灭渡桥': '双塔街道', '吴门桥': '双塔街道', '行春桥': '横塘街道',
      '普济桥': '虎丘街道', '斜塘土地庙及永安桥': '斜塘街道', '上津桥': '虎丘街道', '下津桥': '虎丘街道', '普安桥': '金阊街道',
      '越城桥': '横塘街道', '官太尉桥': '双塔街道', '里尺桥': '临湖镇', '观桥': '阳澄湖镇', '聚福桥': '虞山街道', '华阳桥': '沙家浜镇',
      '顺民桥': '虞山街道', '永济桥': '虞山街道', '长寿桥': '虞山街道', '香花桥': '虞山街道', '甸桥': '虞山街道', '程家桥': '虞山街道',
      '拂水桥': '虞山街道', '广嗣桥': '虞山街道', '迎阳桥': '辛庄镇', '钓渚渡桥': '辛庄镇', '照山桥': '虞山街道', '张桥张家村西桥': '辛庄镇',
      '太平桥': '蓬朗街道', '彩云桥': '横塘街道', '寿星桥': '双塔街道', '东亭子桥': '城厢镇', '流顺桥': '城厢镇', '长安桥': '城厢镇', '张墓桥': '虞山街道'}
LV = {'国保': '全国重点文物保护单位', '省保': '江苏省文物保护单位', '市保': '苏州市文物保护单位'}
# 苏州市级文保单位的公布日期；名录里其他日期的“市保”是昆山、常熟、张家港、太仓、吴江（吴江县/市）、吴县（市）自己公布的县级文保
SZB = {'1960/3/17', '1963/3/20', '1982/10/22', '1986/3/25', '1991/1/4', '1998/11/24', '2004/12/23', '2009/7/10', '2014/6/30', '2019/8/23'}
def county_lv(area, d, date):
    y = tuple(int(x) for x in date.split('/')) if date else (0,)
    if area in ('昆山', '常熟', '张家港', '太仓'): return area + '市文物保护单位'
    if d == '吴江区': return '吴江市文物保护单位（原吴江县/市公布）' if y < (2012, 9, 1) else '吴江区文物保护单位'
    if d in ('吴中区', '相城区'): return '吴县市文物保护单位（原吴县/吴县市公布）' if y < (2001, 2, 28) else d + '文物保护单位'
    return '苏州市文物保护单位'
def core(n): return re.sub(r'（.*?）|\(.*?\)|\s', '', n)
R = []
for c in json.load(open(S + '/sz/gov_rows.json')):
    no, name, lv, area, era, addr, batch, date = c[:8]
    if '桥' not in name or (NOTB.search(name) and not re.search(r'[^桥]桥$', name)): continue   # “张墓桥”“庵弄桥”是桥
    d = DM.get(area, area)
    m = re.match(r'^(?:' + re.escape(d) + r'|' + re.escape(area) + r')?(.{1,5}?(?:镇|街道|乡))', addr)
    town = m.group(1) if m else TF.get(name, '—')
    level = LV[lv] + (f'（{batch}）' if batch else '')
    if lv == '市保' and date not in SZB: level = county_lv(area, d, date)   # 县级市（区）自己公布的“市保”是县级文保
    k = f'{d}|{town}|{name}'
    R.append(dict(dist=d, town=town, name=name, era=era, loc=addr, level=level, doc=(date.replace('/', '-') + '公布') if date else '—',
                  src=GOVURL, note=NOTE.get(name, ''), struct=ST.get(k, '—'), len=LN.get(k, '—')))
# 成组公布的拆成单桥，组名写进说明
SPLIT = {'太仓石拱桥': [('州桥', '石拱桥（单孔）'), ('皋桥', '石拱桥（单孔）'), ('周泾桥', '石拱桥（单孔）')],
         '双桥及沿河建筑': [('世德桥', '石拱桥（单孔）'), ('永安桥', '石梁桥')],
         '同里三桥': [('太平桥', '—'), ('吉利桥', '—'), ('长庆桥', '—')],
         '八坼古桥梁': [('联源桥', '—'), ('南厍永宁桥', '—'), ('八坼合浦桥', '—'), ('八坼万安桥', '—')],
       '天福三桥': [('聚福桥', '石拱桥（单孔并联式）', '元至正八年（1348）始建，清道光二十五年重建', '19米'),
                      ('永清桥', '—', '清乾隆二年（1737）', '—'),
                      ('万寿桥', '石梁桥（单孔）', '清乾隆三十二年（1767）始建，民国二十四年（1935）修复', '16.7米')]}
SPN = {
       '八坼古桥梁': '县保“八坼古桥梁”（联源桥、永宁桥、合浦桥、万安桥四座清代桥）的组成部分，这里按单桥列出；组成桥名据维基百科吴江区列表',
       '同里三桥': '市保“同里三桥”（太平桥、吉利桥、长庆桥）的组成部分，这里按单桥列出；组成桥名据老百晓集桥','太仓石拱桥': '国保“太仓石拱桥”（州桥、皋桥、周泾桥三座元代石拱桥）的组成部分，这里按单桥列出',
       '双桥及沿河建筑': '省保“双桥及沿河建筑”的组成部分（“双桥”即世德桥、永安桥），这里按单桥列出',
       '天福三桥': '省保“天福三桥”（聚福桥、永清桥、万寿桥）的组成部分，这里按单桥列出；组成桥名和年代、长度据老百晓集桥（万寿桥页面）'}
# 苏州名录里没有、维基各区县列表有的桥（控保单位，或名录漏列的）
WX = [('吴中区', '东山镇', '具区风月桥', '清重建', '东山镇渡桥村', '苏州市文物保护单位（据维基百科：1986年3月25日公布，苏州市文广旅局名录未列）', '吴中区'),
      ('吴江区', '盛泽镇', '升明桥', '清', '盛泽镇', '吴江市文物保护单位（据维基百科：原吴江市第二批）', '吴江区'),
      ('张家港市', '杨舍镇', '黄旗桥', '清重修', '杨舍镇塘市李巷村', '张家港市文物保护单位（据维基百科）', '张家港市'),
      ('相城区', '北桥街道', '南濠桥', '民国重建', '北桥街道漕湖村', '相城区文物控制单位（维基百科作“相城区文物控保单位”）', '相城区'),
      ('相城区', '黄埭镇', '香花桥', '宋—清', '黄埭镇黄埭老街', '相城区文物控制单位（维基百科作“相城区文物控保单位”）', '相城区'),
      ('相城区', '黄埭镇', '黄萧桥', '清重建', '黄埭镇金龙村', '相城区文物控制单位（维基百科作“相城区文物控保单位”）', '相城区'),
      ('相城区', '阳澄湖镇', '西洋桥', '清代', '阳澄湖镇莲花村', '相城区文物控制单位（维基百科作“相城区文物控保单位”）', '相城区')]
for d, town, name, era, addr, level, w in WX:
    if any(x['dist'] == d and x['name'] == name for x in R): continue
    k = f'{d}|{town}|{name}'
    R.append(dict(dist=d, town=town, name=name, era=era, loc=addr, level=level, doc='—', src='https://zh.wikipedia.org/wiki/' + w + '各级文物保护单位列表', note='', struct=ST.get(k, '—'), len=LN.get(k, '—')))
out = []
for r in R:
    if r['name'] not in SPLIT: out.append(r); continue
    for x in SPLIT[r['name']]:
        n, st = x[0], x[1]
        m = dict(r); m.update(name=n, struct=ST.get(f"{r['dist']}|{r['town']}|{n}", st), len=LN.get(f"{r['dist']}|{r['town']}|{n}", x[3] if len(x) > 3 else '—'), note=SPN[r['name']])
        if len(x) > 2: m['era'] = x[2]
        out.append(m)
R = out
# 不在文保名录、老百晓集桥收录的古桥（尚未定级，待核实；build/unlisted.py）
for u in (json.load(open(S + '/build/unlisted.json')).get('苏州市', []) if os.path.exists(S + '/build/unlisted.json') else []):
    if not any(x['dist'] == u['dist'] and re.sub(r'（.*?）', '', x['name']) == u['name'] for x in R): R.append(dict(u, struct='—', len='—'))
# 吴中区第四次全国文物普查新发现不可移动文物名录公示（2026年4月14日，153处；附件xlsx，列：序号、名称、年代、类别、地址）
import zipfile, html as _h
WZ4 = '/Users/sean/workspace/oldbridge/文保名录/苏州市/吴中区第四次全国文物普查新发现不可移动文物名录公示（2026年4月14日，153处）.xlsx'
WZ4URL = 'https://qr61.cn/oJEmRU/qllcPAG'
SRCNAME = globals().get('SRCNAME', {}); SRCNAME[WZ4URL] = '吴中区第四次全国文物普查新发现不可移动文物名录公示（2026年4月14日，草料二维码附件）'
z = zipfile.ZipFile(WZ4)
SS = [_h.unescape(''.join(re.findall(r'<t[^>]*>([^<]*)</t>', si))) for si in re.findall(r'<si>.*?</si>', z.read('xl/sharedStrings.xml').decode('utf8'), re.S)]
for row in re.findall(r'<row[^>]*>(.*?)</row>', z.read('xl/worksheets/sheet1.xml').decode('utf8'), re.S):
    c = []
    for attr, inner in re.findall(r'<c ([^>]*?)(?:/>|>(.*?)</c>)', row, re.S):
        v = re.search(r'<v>([^<]*)</v>', inner or ''); v = v.group(1) if v else ''
        c.append((SS[int(v)] if 't="s"' in attr and v else v).strip())
    if len(c) < 5 or not c[0].isdigit(): continue
    name, era, addr = c[1], c[2], c[4]
    if not re.search(r'桥$', name) or NOTB.search(name): continue
    a2 = re.sub(r'^(江苏省)?(苏州市)?吴中区', '', addr)
    tw = (re.match(r'^(.{2,4}?(?:镇|街道))', a2) or [None, '—'])[1]
    loc = re.sub('^' + re.escape(tw), '', a2) if tw != '—' else a2
    LV4 = '未定级不可移动文物（四普新发现）'
    hit = [x for x in R if x['dist'] == '吴中区' and re.sub(r'（.*?）', '', x['name']) == name and x['town'] in (tw, '—')]
    if hit:
        x = hit[0]
        if x['level'].startswith('尚未定级'):
            x['note'] = (x.get('note') or '') + ('；' if x.get('note') else '') + f'等级据吴中区四普新发现名录公示（原记为{x["level"]}）'
            x.update(level=LV4, doc='2026年4月14日公示', src=WZ4URL, era=era if (x.get('era') or '—') in ('—', '清', '明') else x['era'])
        continue
    R.append(dict(dist='吴中区', town=tw, name=name, era=era, loc=loc, level=LV4, doc='2026年4月14日公示', src=WZ4URL, note='', struct='—', len='—'))
# 结构为“—”或只写桥型、没有孔数的，按老百晓集桥页面补桥型和孔数（build/cqholes.py）
HOLES = json.load(open(S + '/build/cq_holes.json')) if os.path.exists(S + '/build/cq_holes.json') else {}
LENF = json.load(open(S + '/build/cq_len_fill.json')) if os.path.exists(S + '/build/cq_len_fill.json') else {}
for r in R:
    hk = '苏州市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
    if hk in HOLES and ((r.get('struct') or '—') == '—' or re.fullmatch(r'石?(拱|梁)桥|石板桥|平桥|廊桥', r['struct'])): r['struct'] = HOLES[hk]
    if hk in LENF and (r.get('len') or '—') in ('—', ''): r['len'] = LENF[hk]
# 时代只写朝代或“—”的，按老百晓集桥、云端档案补具体年代（build/erafill.py）
EF = json.load(open(S + '/build/era_fill.json')) if os.path.exists(S + '/build/era_fill.json') else {}
for r in R:
    ek = '苏州市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
    if ek in EF and (r['era'] or '—') == EF[ek]['old']:
        f = EF[ek]; old = r['era'] or '—'
        ds = [d for d in ('宋', '元', '明', '清', '民国') if d in old.replace('中华民国', '民国')]
        r['era'] = f['era'] if all(d in f['era'] for d in ds) else old + '；' + f['era']
        src = '老百晓集桥' if f['src'] == 'cq' else '杭州市文物遗产与历史建筑保护中心云端档案'
        r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'具体年代据{src}（名录原写“{old}”）'

json.dump(R, open(S + '/sz/rows.json', 'w'), ensure_ascii=False, indent=0)
ORD = {'全': 0, '江': 1, '苏': 2, '尚': 4}
for d in DISTS:
    folder = os.path.join(ROOT, d); os.makedirs(folder, exist_ok=True)
    for f in os.listdir(folder):
        if f.endswith('古桥.md'): os.remove(os.path.join(folder, f))
    rs = sorted([r for r in R if r['dist'] == d], key=lambda r: (ORD.get(r['level'][0], 3), r['town'] in ('—', ''), r['town']))
    L = [f'# 苏州市{d}不可移动文物：桥梁', '']
    if not rs:
        L += [f'《苏州市各级文物保护单位名录》里，{d}没有桥梁类的国保、省保、市保。', '']
        open(os.path.join(folder, f'{d}古桥.md'), 'w').write('\n'.join(L)); print(d, 0); continue
    L += ['| 序号 | 乡镇 | 桥名 | 结构 | 长度 | 时代 | 位置 | 文保等级 | 公布日期 | 图片 |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(rs, 1):
        b = core(r['name']); fs = [f'{b}{k}.jpg' for k in (1, 2, 3) if os.path.exists(os.path.join(folder, f'{b}{k}.jpg'))]
        img = ' '.join(f'[{k}]({f})' for k, f in enumerate(fs, 1)) if fs else '暂无'
        L.append('| ' + ' | '.join([str(i), r['town'], (f"{r['name']} [?]({CQ[k]})" if (k := '苏州市|' + r['dist'] + '|' + r['town'] + '|' + r['name']) in CQ else r['name']), r['struct'], r['len'], r['era'] or '—', r['loc'] or '—', r['level'], r['doc'], img]) + ' |')
    notes = [f'{r["name"]}：{r["note"]}。' for r in rs if r['note']]
    notes += ['名单、等级、时代、地址、公布日期均以苏州市文化广电和旅游局公布的《苏州市各级文物保护单位名录》为准（原件存于本项目 文保名录/苏州市/）。',
              '目前只收录国保、省保、市保；控制保护建筑、登记不可移动文物（文物点）还未收录。',
              '乡镇一列按名录地址提取，地址里没有写到乡镇的标“—”。',
              '结构、长度标“—”的，是没有查到可靠资料。']
    L += ['', '## 说明', ''] + [f'- {n}' for n in notes] + ['', '## 来源', '', f'- [苏州市文化广电和旅游局：文物保护单位（苏州市各级文物保护单位名录）]({GOVURL})']
    fs = sorted(k for k in IMG if k.startswith(d + '/'))
    if fs:
        L += ['', '## 图片来源', '', '| 图片 | 来源 |', '|---|---|'] + [f'| [{k.split("/")[1]}]({k.split("/")[1]}) | {IMG[k]} |' for k in fs]
    open(os.path.join(folder, f'{d}古桥.md'), 'w').write('\n'.join(L) + '\n')
    print(d, len(rs))
