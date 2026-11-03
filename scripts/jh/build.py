# -*- coding: utf-8 -*-
# 金华市古桥名录生成（两级目录：金华市/区县/区县古桥.md）
import json, os, re
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
CQ = json.load(open(S + '/build/cqlinks.json')) if os.path.exists(S + '/build/cqlinks.json') else {}  # 老百晓集桥链接
ROOT = '/Users/sean/workspace/oldbridge/金华市'
DISTS = ['婺城区', '金东区', '兰溪市', '东阳市', '义乌市', '永康市', '浦江县', '武义县', '磐安县']
W = lambda p: 'https://zh.wikipedia.org/wiki/' + p
XLSX = 'http://wwj.zj.gov.cn/'
SRCNAME = {W('浙江省文物保护单位'): '维基百科：浙江省文物保护单位', W('全国重点文物保护单位'): '维基百科：全国重点文物保护单位',
           XLSX: '浙江省文物局：全省文物保护点统计表（金华市文物保护点，本项目 文保名录/浙江省/ 有原件）'}
for d in DISTS: SRCNAME[W(d + '各级文物保护单位列表')] = f'维基百科：{d}各级文物保护单位列表'
def SN(u): return SRCNAME.get(u) or ('老百晓集桥：' + u.rsplit('/', 1)[-1] if 'china-qiao' in u else u)
def load(p): return json.load(open(p)) if os.path.exists(p) else {}
ST, LN, IMG = load(S + '/jh/struct.json'), load(S + '/jh/len.json'), load(S + '/jh/imgsrc.json')
R = []
def e(dist, town, name, era, loc, level, doc, src, note=''):
    k = f'{dist}|{town}|{name}'
    R.append(dict(dist=dist, town=town, name=name, era=era, loc=loc, level=level, doc=doc, src=src, note=note, struct=ST.get(k, '—'), len=LN.get(k, '—')))
GB, ZJ = W('全国重点文物保护单位'), W('浙江省文物保护单位')
# 全国重点文物保护单位
e('义乌市', '赤岸镇', '古月桥', '南宋嘉定六年（1213）', '赤岸镇雅治街村', '全国重点文物保护单位（第五批）', '2001年公布', GB)
e('兰溪市', '梅江镇', '通洲桥', '清道光年间', '梅江镇塔山村', '全国重点文物保护单位（第八批）', '2019年公布', GB, '1997年先列为浙江省文物保护单位（4-75）')
# 浙江省文物保护单位
e('婺城区', '长山乡', '东村桥', '—', '长山乡', '浙江省文物保护单位（第五批，5-37）', '2005年公布', ZJ)
e('婺城区', '—', '金华通济桥', '—', '跨婺江', '浙江省文物保护单位（第六批，6-186）', '2011年公布', ZJ, '现存桥身屡经改建，建造年代以官方公布为准，待核实')
e('婺城区', '汤溪镇', '萧家小龙桥', '—', '汤溪镇', '浙江省文物保护单位（第七批，7-135）', '2017年公布', ZJ)
for n in ['永安桥', '永福桥', '永济桥']:
    e('兰溪市', '游埠镇', n, '清', '游埠镇游埠村', '浙江省文物保护单位（第七批，“游埠古桥群”组成部分，7-145）', '2017年公布', ZJ)
e('永康市', '江南街道', '西津桥', '清', '江南街道，跨永康江', '浙江省文物保护单位（第四批，4-79）', '1997年公布', ZJ)
e('武义县', '壶山街道', '熟溪桥', '南宋始建，清重修', '武义县城熟溪上', '浙江省文物保护单位（第三批，3-73）', '1989年公布', ZJ)
e('浦江县', '大畈乡', '广安桥', '清', '大畈乡建光行政村上河自然村东侧', '浙江省文物保护单位（第七批，7-156）', '2017年公布', ZJ, '原为浦江县文物保护单位（第四批）')
e('磐安县', '—', '道德桥', '民国十七年（1928）', '县城双溪口', '浙江省文物保护单位（第六批，6-329）', '2011年公布', ZJ, '结构、年代据老百晓集桥：县城现存最古老的拱桥，钢筋混凝土独拱桥，长35.53米')
e('磐安县', '—', '宅口承志桥', '—', '—', '浙江省文物保护单位（第七批，7-157）', '2017年公布', ZJ)
# 县（市）级文物保护单位（维基百科各县列表）
for d, town, n, era, loc, lv, note in [
    ('兰溪市', '游埠镇', '潦溪桥', '清', '游埠镇集镇中心', '兰溪市文物保护单位（第五批，名录作“游埠古桥”）', ''),
    ('兰溪市', '横溪镇', '梅溪古桥', '清', '横溪镇施宅、宋宅村', '兰溪市文物保护单位', ''),
    ('兰溪市', '灵洞乡', '怀清桥', '清', '灵洞乡板桥村', '兰溪市文物保护单位', ''),
    ('永康市', '芝英镇', '灵溪桥', '宋', '芝英镇芝英八村', '永康市文物保护单位（第三批，1998年）', ''),
    ('永康市', '象珠镇', '磻溪桥', '清', '象珠镇雅吕村', '永康市文物保护单位（第三批，1998年）', '第四批名单又列一次'),
    ('永康市', '方岩镇', '古竹桥', '清', '方岩镇古竹畈村', '永康市文物保护单位（第四批，2002年）', ''),
    ('永康市', '龙山镇', '众成桥', '清', '龙山镇边颜村', '永康市文物保护单位（第四批，2002年）', ''),
    ('永康市', '象珠镇', '凰江桥', '清', '象珠镇象珠一村', '永康市文物保护单位（第四批，2002年）', ''),
    ('永康市', '唐先镇', '上考保永桥', '清', '唐先镇上考村村中北溪', '永康市文物保护单位（第六批，2010年）', ''),
    ('永康市', '方岩镇', '来龙桥', '明', '方岩镇岩后村村西小溪上', '永康市文物保护单位（第六批，2010年）', ''),
    ('永康市', '象珠镇', '峡源古桥群', '元至民国', '象珠镇峡源村', '永康市文物保护单位（第六批，2010年）', '成组公布'),
    ('浦江县', '杭坪镇', '登云桥', '清', '杭坪镇杭坪行政村笑流坞口自然村东南200米处', '浦江县文物保护单位（第四批）', ''),
    ('浦江县', '郑宅镇', '骢马桥', '清', '郑宅镇横溪行政村横溪自然村村口', '浦江县文物保护单位（第四批）', ''),
    ('浦江县', '虞宅乡', '镇东桥', '清', '虞宅乡新光行政村新光自然村村口', '浦江县文物保护单位（第四批）', ''),
    ('浦江县', '中余乡', '下毛洞口石拱桥', '清', '中余乡五星行政村下毛洞口自然村村口', '浦江县文物保护单位（第四批）', '')]:
    e(d, town, n, era, loc, lv, '—', W(d + '各级文物保护单位列表'), note)
def core(n): return re.sub(r'（.*?）|\(.*?\)|\s', '', n)
# 政府原件（文保名录/ 里的县级名录，build/official.py 提取）
# 名录之外、人工查到出处的桥（build/extra.json）
for o in (json.load(open(S + '/build/extra.json')).get('金华市', []) if os.path.exists(S + '/build/extra.json') else []):
    if not any(r['dist'] == o['dist'] and core(r['name']) == core(o['name']) for r in R): e(o['dist'], o['town'], o['name'], o['era'], o['loc'], o['lvtxt'], '—', o['src'], o.get('note', ''))
for o in (json.load(open(S + '/build/official.json')).get('金华市', []) if os.path.exists(S + '/build/official.json') else []):
    if any(r['dist'] == o['dist'] and core(r['name']) == core(o['name']) for r in R): continue
    u = '../../文保名录/' + o['src']; SRCNAME[u] = '政府原件：' + o['src'].split('/')[-1].rsplit('.', 1)[0]
    e(o['dist'], o['town'], o['name'], o['era'], o['loc'], o['lvtxt'], o['doc'], u)
# 金华市文物保护点（浙江省文物局统计表）
for b in json.load(open(S + '/jh/xlsx_bridges.json')):
    d = b['dist']
    if any(r['dist'] == d and core(r['name']) == core(b['name']) for r in R): continue
    PRE = r'^(?:浙江省)?(?:金华市)?(?:' + '|'.join(DISTS) + r')?'
    t = re.sub(PRE, '', b['town'])
    if not re.search(r'(镇|乡|街道)$', t): t = None
    if not t:
        m = re.match(r'^(.{1,5}?(?:镇|乡|街道))', re.sub(PRE, '', b['loc']))
        t = m.group(1) if m else '—'
    e(d, t, b['name'], b['era'] or '—', b['loc'], '金华市文物保护点', b['doc'] or '—', XLSX)
# 不在文保名录、老百晓集桥收录的古桥（尚未定级，待核实；build/unlisted.py）
for u in (json.load(open(S + '/build/unlisted.json')).get('金华市', []) if os.path.exists(S + '/build/unlisted.json') else []):
    if not any(x['dist'] == u['dist'] and re.sub(r'（.*?）', '', x['name']) == u['name'] for x in R): R.append(dict(u, struct='—', len='—'))
# 结构为“—”或只写桥型、没有孔数的，按老百晓集桥页面补桥型和孔数（build/cqholes.py）
HOLES = json.load(open(S + '/build/cq_holes.json')) if os.path.exists(S + '/build/cq_holes.json') else {}
LENF = json.load(open(S + '/build/cq_len_fill.json')) if os.path.exists(S + '/build/cq_len_fill.json') else {}
for r in R:
    hk = '金华市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
    if hk in HOLES and ((r.get('struct') or '—') == '—' or re.fullmatch(r'石?(拱|梁)桥|石板桥|平桥|廊桥', r['struct'])): r['struct'] = HOLES[hk]
    if hk in LENF and (r.get('len') or '—') in ('—', ''): r['len'] = LENF[hk]
# 时代只写朝代或“—”的，按老百晓集桥、云端档案补具体年代（build/erafill.py）
EF = json.load(open(S + '/build/era_fill.json')) if os.path.exists(S + '/build/era_fill.json') else {}
for r in R:
    ek = '金华市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
    if ek in EF and (r['era'] or '—') == EF[ek]['old']:
        f = EF[ek]; old = r['era'] or '—'
        ds = [d for d in ('宋', '元', '明', '清', '民国') if d in old.replace('中华民国', '民国')]
        r['era'] = f['era'] if all(d in f['era'] for d in ds) else old + '；' + f['era']
        src = '老百晓集桥' if f['src'] == 'cq' else '杭州市文物遗产与历史建筑保护中心云端档案'
        r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'具体年代据{src}（名录原写“{old}”）'

json.dump(R, open(S + '/jh/rows.json', 'w'), ensure_ascii=False, indent=0)
ORD = lambda lv: 0 if lv.startswith('全国') else 1 if lv.startswith('浙江') else 3 if '保护点' in lv else 2
for d in DISTS:
    folder = os.path.join(ROOT, d); os.makedirs(folder, exist_ok=True)
    rs = sorted([r for r in R if r['dist'] == d], key=lambda r: (ORD(r['level']), r['town'] in ('—', ''), r['town']))
    L = [f'# 金华市{d}不可移动文物：桥梁', '']
    if not rs:
        L += [f'目前收集到的名录里，{d}没有桥梁。县级文物保护单位名单还不完整。', '']
        open(os.path.join(folder, f'{d}古桥.md'), 'w').write('\n'.join(L)); print(d, 0); continue
    L += ['| 序号 | 乡镇 | 桥名 | 结构 | 长度 | 时代 | 位置 | 文保等级 | 公布文件 | 图片 |', '|---|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(rs, 1):
        b = core(r['name']); fs = [f'{b}{k}.jpg' for k in (1, 2, 3) if os.path.exists(os.path.join(folder, f'{b}{k}.jpg'))]
        img = ' '.join(f'[{k}]({f})' for k, f in enumerate(fs, 1)) if fs else '暂无'
        L.append('| ' + ' | '.join([str(i), r['town'], (f"{r['name']} [?]({CQ[k]})" if (k := '金华市|' + r['dist'] + '|' + r['town'] + '|' + r['name']) in CQ else r['name']), r['struct'], r['len'], r['era'] or '—', r['loc'] or '—', r['level'], r['doc'], img]) + ' |')
    notes = [f'{r["name"]}：{r["note"]}。' for r in rs if r['note']]
    notes += ['金华市文物保护点以浙江省文物局《全省文物保护点》统计表为准（原件存于本项目 文保名录/浙江省/）。',
              '国保、省保、县保暂时依据维基百科整理，还没找到政府原件；县保名单尤其不完整。',
              '乡镇、结构、长度标“—”的，是没有查到可靠资料。']
    L += ['', '## 说明', ''] + [f'- {n}' for n in notes] + ['', '## 来源', '']
    srcs = list(dict.fromkeys(r['src'] for r in rs))
    L += [f'- [{SN(u)}]({u})' for u in srcs]
    fs = sorted(k for k in IMG if k.startswith(d + '/') and os.path.exists(os.path.join(ROOT, k)))
    if fs:
        L += ['', '## 图片来源', '', '| 图片 | 来源 |', '|---|---|'] + [f'| [{k.split("/")[1]}]({k.split("/")[1]}) | {IMG[k]} |' for k in fs]
    open(os.path.join(folder, f'{d}古桥.md'), 'w').write('\n'.join(L) + '\n')
    print(d, len(rs))
