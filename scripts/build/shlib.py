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
# 黄浦区第三次全国文物普查登记不可移动文物补充公布名录（2025年8月，254处；页面表格导出为 tsv）
HP = '文保名录/上海市/黄浦区第三次全国文物普查登记不可移动文物补充公布名录（2025年8月，254处）.tsv'
HPSRC = 'https://www.shhuangpu.gov.cn/zw/009002/009002015/009002015004/009002015004003/20250814/390e4ee6-fb85-4dc3-8a07-d735dcbdfe34.html'
for line in open(os.path.join(S, '..', HP), encoding='utf8'):
    c = line.rstrip('\n').split('\t')
    if len(c) < 5 or not c[0].isdigit(): continue
    n, code, a = c[1], c[2], c[3]
    if NB.search(n) or not n.endswith('桥'): continue
    tw = town(a); loc = re.sub(r'^' + re.escape(tw), '', a) if tw != '—' else a
    hit = [r for r in R if r['dist'] == '黄浦区' and core(r['name']) == core(n)]
    if hit:
        r = hit[0]
        if r['town'] == '—' and tw != '—': r['town'] = tw
        if code not in (r.get('note') or ''): r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'黄浦区2025年补充公布三普登记名录，登记表编号{code}'
        continue
    R.append(dict(dist='黄浦区', town=tw, name=n, era='—', loc=loc or '—', level='登记不可移动文物（黄浦区2025年补充公布）', doc='黄浦区文物局2025年8月8日公布', src=HPSRC, note=f'黄浦区第三次全国文物普查登记不可移动文物补充公布名录，登记表编号{code}', struct='—', len='—'))
    add += 1
# 第四次全国文物普查新发现未定级不可移动文物（区文旅局公示/公布）
LV4 = '未定级不可移动文物（四普新发现）'
def add4(dist, tw, n, era, loc, doc, src, note=''):
    global add
    hit = [r for r in R if r['dist'] == dist and core(r['name']) == core(n) and r['town'] in (tw, '—')]
    if hit:
        r = hit[0]
        if r['level'].startswith(('尚未定级', '登记不可移动')):
            r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'等级据{dist}四普新发现名录（原记为{r["level"]}）'
            r.update(level=LV4, doc=doc, src=src)
            if (r.get('era') or '—') == '—': r['era'] = era
        return
    R.append(dict(dist=dist, town=tw, name=n, era=era, loc=loc, level=LV4, doc=doc, src=src, note=note, struct='—', len='—')); add += 1
# 嘉定区（2026年3月24日拟公布名录公示，30处；页面表格：序号、名称、地址、保护级别）
JD4 = '文保名录/上海市/嘉定区第四次全国文物普查新发现不可移动文物拟公布名录公示（2026年3月24日，30处）.html'
JD4URL = 'https://www.jiading.gov.cn/publicity/gg/zwgg__publicity/fdzdgknr/gg/zwgg/196205'
import html as _h
t = open(os.path.join(S, '..', JD4), encoding='utf8', errors='ignore').read()
for tr in re.findall(r'<tr.*?</tr>', t, re.S):
    c = [re.sub(r'\s+', '', _h.unescape(re.sub(r'<[^>]+>', '', x))) for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
    if len(c) < 4 or not c[0].isdigit() or not c[1].endswith('桥') or NB.search(c[1]): continue
    tw = town(c[2])
    add4('嘉定区', tw, c[1], '—', re.sub('^' + re.escape(tw), '', c[2]) if tw != '—' else c[2], '2026年3月24日公示', JD4URL)
# 松江区（拟认定公布名录，共28处；PDF 表格折行严重，桥逐条录入）
SJ4 = '../../文保名录/上海市/松江区第四次全国文物普查拟认定公布新发现未定级不可移动文物名录（共计28处）.pdf'
for tw, n, era, loc, note in [
    ('九里亭街道', '乐郊桥', '清道光十六年（1836）', '涞坊路599弄五洲云景花苑小区内42号楼北侧', ''),
    ('车墩镇', '太平桥', '清代', '永福村（南距长永公路约175米，西距长福公路约330米）', ''),
    ('车墩镇', '指南桥', '1935年', '米市渡松南郊野公园内（东距洞泾港约50米，北距闵塔公路约850米）', ''),
    ('九亭镇', '吴家浜桥', '清光绪十八年（1892）', '勤富路503号吴家浜公园内（北距勤富路约24米，西距沈海高速约125米）', ''),
    ('泖港镇', '来凤桥', '1922年', '园区西路与姚厍公路交汇处', ''),
    ('叶榭镇', '南瑞桥', '1946年', '东勤村北（北距黄浦江南岸约165米，西距东清水港约280米）', ''),
    ('叶榭镇', '友谊桥', '1972年', '叶新公路999号上海力登工业园东北角（北距叶新公路约50米）', ''),
    ('小昆山镇', '永兴桥', '清康熙五十年（1711）', '谢家村路、谢家村北路交汇口北侧', ''),
    ('小昆山镇', '小昆山十字桥', '1977年', '山西路4号小昆山园东南角外，打铁浜横河和小昆山五号河十字交汇口', ''),
    ('小昆山镇', '小昆山三角桥', '1979年', '山西路4号小昆山园西南角外，昆岗河与打铁浜横河“Y”形交汇口', ''),
    ('经开区', '昆秀桥', '清光绪二十八年（1902）', '昆秀湖西侧，东升港路以东约160米、文翔路以北约460米（2010年自姚家浜村原址整体迁建于此）',
     '单跨石梁桥，桥面南北长6.7米、东西宽1.7米；东石条浮雕“崑秀橋”，阴刻“光绪二十八年重建”“里人谨募”，南侧石阶刻“戚万兴石作造”“丙寅年四月”（据松江区政府网2026年4月22日报道《新发现！松江经开区这座百年石桥，入列不可移动文物》）'),
]:
    add4('松江区', tw, n, era, loc, '松江区文旅局公布（拟认定公布名录共28处）', SJ4, note)
json.dump(R, open(p, 'w'), ensure_ascii=False, indent=0)
print('upgraded', up, 'added', add)
