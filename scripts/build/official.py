# -*- coding: utf-8 -*-
# 从 文保名录/ 里新增的政府原件（常州、宜兴、丽水、武义）提取桥梁，写 build/official.json
# 每条：dist, town, name, era, loc, lv(gb/sb/shi/xian/wbd), lvtxt(等级文字), doc(公布文件), src(原件相对路径)
import json, os, re, html, sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
W = os.path.join(os.path.dirname(S), '文保名录')
sys.path.insert(0, S + '/zj')
from wikilist import isbridge
CF = json.load(open(S + '/zj/cities.json'))

def tables(f):
    """按顺序返回 (表前文字, 行列表)"""
    t = open(os.path.join(W, f), 'rb').read().decode('utf8', 'ignore')
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S | re.I)
    pre = ''
    for p in re.split(r'(<table.*?</table>)', t, flags=re.S | re.I):
        if p.lower().startswith('<table'):
            rows = [[re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', c))) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S | re.I)]
                    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', p, re.S | re.I)]
            yield pre, rows
        else:
            pre = re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', p)))[-120:]

def town_of(addr, dists):
    a = re.sub(r'^(江苏省|浙江省)?(常州市|无锡市|丽水市|金华市)?', '', addr)
    a = re.sub(r'^(' + '|'.join(dists) + r'|' + '|'.join(d[:2] for d in dists) + r')(区|县|市)?', '', a)
    m = re.match(r'^(.{2,6}?(?:街道|镇|乡))', a)
    return m.group(1) if m and not re.search(r'[路村]', m.group(1)[:-1]) else '—'

OUT = {}
def put(city, **r):
    n = r['name']
    if '、' in n:   # “贤母桥、竞爽桥”：名称、地址按顿号一一对应
        ts = r['loc'].split('、')
        for i, x in enumerate(n.split('、')):
            loc = ts[i] if len(ts) == len(n.split('、')) else r['loc']
            put(city, **dict(r, name=x, loc=loc, town=re.sub(r'^.*?(?:县|市|区)', '', loc) if len(ts) > 1 else r['town']))
        return
    if '遗址' in n or '群' in n or not re.search(r'桥(（.*?）)?$', n) or len(n) > 16: return   # 名称以“桥”结尾才收（“寺前桥”这类也算）
    OUT.setdefault(city, []).append(r)

# 常州市第五、六、八批市级文物保护单位（列：序号、编号、名称、时代、地址）
CZD = CF['常州市']['dists']
for n, f in (('五', '常州市/常州市第五批市级文物保护单位（常州市人民政府）.html'), ('六', '常州市/常州市第六批市级文物保护单位（常州市人民政府）.html'),
             ('八', '常州市/常州市第八批市级文物保护单位（常州市人民政府，2019）.html')):
    for pre, rows in tables(f):
        for c in rows:
            if len(c) < 5 or not c[0].isdigit(): continue
            name, era, addr = c[2], c[3], c[4]
            a = addr.replace('武进经发区', '武进区').replace('金坛市', '金坛区')
            d = next((x for x in CZD if a.startswith(x) or a.startswith(x[:2])), None)
            if not d: continue
            put('常州市', dist=d, town=town_of(a, CZD), name=name, era=era, loc=addr, lv='shi', lvtxt=f'常州市文物保护单位（第{n}批）',
                doc=f'常州市第{n}批市级文物保护单位', src=f)

# 宜兴市第五、六批（每份两张表：文物保护单位、文物控制单位；列：序号、名称、时代、地址、类别）
WXD = CF['无锡市']['dists']
RN = {'万园桥': '万缘桥', '西埝桥': '西堰桥', '新安桥': '新岸桥'}   # 第七批附件3 更名
for (b1, b2, f) in (('五', '二', '无锡市/宜兴市第五批文物保护单位和第二批文物控制单位（2011）.html'),
                    ('六', '三', '无锡市/宜兴市第六批文物保护单位和第三批文物控制单位（2017）.html')):
    k = 0
    for pre, rows in tables(f):
        hdr = next((c for c in rows if '名称' in ''.join(c)), None)
        if not hdr: continue
        k += 1
        ctrl = '控制' in pre or k == 2
        for c in rows:
            if len(c) < 4 or not c[0].isdigit(): continue
            name, era, addr = RN.get(c[1], c[1]), c[2], c[3].replace('宜兴市', '')
            put('无锡市', dist='宜兴市', town=town_of(addr, WXD), name=name, era=era, loc=addr, lv='wbd' if ctrl else 'xian',
                lvtxt=(f'宜兴市文物控制单位（第{b2}批）' if ctrl else f'宜兴市文物保护单位（第{b1}批）'),
                doc=('宜政发〔2009〕111号' if b1 == '五' else '宜政发〔2016〕162号'), src=f)
# 宜兴市第七批、第四批文物控制单位（附件为图片，按图片录入）
F7 = '无锡市/宜兴市第七批文物保护单位和第四批文物控制单位（2023）.html'
for name, era, addr, ctrl in (('田舍桥', '清', '官林镇凌霞村小杨家自然村', 0), ('寿星桥', '清', '和桥镇北新村官庄自然村南200米吉祥寺内', 0),
                              ('王家万寿桥', '1928年', '官林镇都山村水韵新村周家浜', 0), ('里塘渎桥', '1928年', '和桥镇南新社区南新老街', 0),
                              ('莲溪桥', '清', '丁蜀镇三洞桥村村东组', 1), ('永安桥', '1917年', '官林镇官林村', 1)):
    put('无锡市', dist='宜兴市', town=town_of(addr, WXD), name=name, era=era, loc=addr, lv='wbd' if ctrl else 'xian',
        lvtxt=('宜兴市文物控制单位（第四批）' if ctrl else '宜兴市文物保护单位（第七批）'), doc='宜兴市人民政府（2023年12月20日）', src=F7)

# 丽水地区文保单位汇总表（列：序号、县（市、区）、名称、地理位置、时代、类别、公布时间、公布文号、备注/级别）
LSD = CF['丽水市']['dists']
LV = [('国家级', 'gb'), ('国保', 'gb'), ('省', 'sb'), ('市县级', 'xian'), ('市级', 'shi'), ('县', 'xian')]
cur, curlv = '莲都区', 'gb'
for pre, rows in tables('丽水市/丽水地区文保单位汇总表（截至2014年6月30日）.html'):
    for c in rows:
        j = ''.join(c)
        if len(c) == 1:
            curlv = next((v for k, v in LV if k in j), curlv); continue
        if len(c) >= 6 and not c[0].isdigit() and c[0].endswith(('县', '市', '区')):   # 合并为国保的组成部分没有序号
            c = [''] + c + ['国家级']
        if len(c) < 6 or (c[0] and not c[0].isdigit()): continue
        if len(c) >= 9:
            _, cty, name, addr, era, _, when, doc = c[:8]; note = c[8] if len(c) > 8 else ''
        else:   # 县名列合并单元格时少一列
            _, name, addr, era, _, when, doc = (c + [''] * 8)[:7]; cty, note = '', c[7] if len(c) > 7 else ''
        if cty:
            cur = '莲都区' if cty in ('市本级', '丽水市', '莲都') else next((d for d in LSD if d.startswith(cty[:2])), cur)
        lv = next((v for k, v in LV if k in note), curlv)
        txt = {'gb': '全国重点文物保护单位', 'sb': '浙江省文物保护单位', 'shi': '丽水市文物保护单位'}.get(lv, f'{cur}文物保护单位')
        put('丽水市', dist=cur, town=town_of(addr, LSD), name=re.sub(r'^(处州廊桥-|庆元廊桥-杨家庄护龙桥(?=..)|庆元廊桥-)', '', name), era=era, loc=addr, lv=lv,
            lvtxt=txt, doc=doc or '—', src='丽水市/丽水地区文保单位汇总表（截至2014年6月30日）.html')

# 武义县各级文物保护单位名录（列：序号、分类号、名称、年代、地址、备注）
lv = 'gb'
for pre, rows in tables('金华市/武义县各级文物保护单位名录（2022）.html'):
    if '全国重点' in pre: lv = 'gb'
    elif '浙江省文物保护单位' in pre: lv = 'sb'
    elif '武义县文物保护单位' in pre: lv = 'xian'
    elif '武义县文物保护点' in pre: lv = 'wbd'
    for c in rows:
        if len(c) < 5 or not c[0].isdigit(): continue
        name, era, addr, note = c[2], c[3], c[4], (c[5] if len(c) > 5 else '')
        put('金华市', dist='武义县', town=town_of(addr.replace('武义县', ''), ['武义县']), name=name, era=era, loc=addr, lv=lv,
            lvtxt={'gb': '全国重点文物保护单位', 'sb': '浙江省文物保护单位', 'xian': '武义县文物保护单位', 'wbd': '武义县文物保护点'}[lv],
            doc=note or '—', src='金华市/武义县各级文物保护单位名录（2022）.html')

# 镇江市各级文物保护单位名录（三份 xls，已转成 scripts/zjs/official_xls.json）
ZJD = CF['镇江市']['dists']; RNZ = {'老西门桥': '宝成桥（老西门桥）'}
for x in json.load(open(S + '/zjs/official_xls.json')):
    n = x['name'].split('——')[-1].split('--')[-1]
    if not n.endswith('桥') or '遗址' in n: continue
    a = x['addr']; d = x['dist']
    if d in ('新区', '镇江市'):
        KW = [('云阳', '丹阳市'), ('丹阳', '丹阳市'), ('句容', '句容市'), ('茅山', '句容市'), ('扬中', '扬中市'), ('宝堰', '丹徒区'), ('润州', '润州区')]
        d = next((z for k, z in KW if k in a), '京口区')
        a = a.replace('云阳镇', '云阳街道')
    if d not in ZJD: continue
    lv = x['lv']
    if lv == 'shi' and d in ('丹阳市', '句容市', '扬中市'): lv = 'xian'
    txt = {'gb': '全国重点文物保护单位（“大运河”组成部分）' if '大运河' in x['name'] else '全国重点文物保护单位', 'sb': '江苏省文物保护单位',
           'shi': '镇江市文物保护单位', 'xian': f'{d}文物保护单位'}[lv]
    put('镇江市', dist=d, town=town_of(a.replace(d, ''), ZJD), name=RNZ.get(n, n), era=x['era'] or '—', loc=a, lv=lv, lvtxt=txt + f"（{x['date']}公布）",
        doc=x['date'] + '公布', src='镇江市/' + x['file'])

# 其他原件里有、项目原来缺的桥（逐条核对原件后录入）
SXY = '绍兴市/绍兴市大运河世界文化遗产保护名录（2021）.html'
RA = '温州市/瑞安市各级文物保护单位、文物保护点目录（2023）.html'
for city, d, tw, n, era, loc, lv, txt, src in [
    ('绍兴市', '柯桥区', '柯桥街道', '永丰桥', '清', '柯桥街道永丰桥河沿', 'wbd', '一般不可移动文物（三普登录，列入绍兴市大运河世界文化遗产保护名录）', SXY),
    ('绍兴市', '柯桥区', '柯桥街道', '工农桥', '清', '柯桥街道大寺社区红木桥河沿5号', 'wbd', '一般不可移动文物（三普登录，列入绍兴市大运河世界文化遗产保护名录）', SXY),
    ('绍兴市', '越城区', '北海街道', '玉龙桥', '民国', '北海街道北海村虹桥头', 'wbd', '文物保护点（列入绍兴市大运河世界文化遗产保护名录）', SXY),
    ('绍兴市', '越城区', '蕺山街道', '小江桥', '民国', '蕺山街道萧山街西端', 'wbd', '文物保护点（列入绍兴市大运河世界文化遗产保护名录）', SXY),
    ('绍兴市', '越城区', '蕺山街道', '龙华桥', '明', '蕺山街道广宁桥社区龙华寺旁', 'wbd', '文物保护点（列入绍兴市大运河世界文化遗产保护名录）', SXY),
    ('绍兴市', '越城区', '皋埠街道', '董家渡桥', '清至民国', '皋埠镇东湖村', 'wbd', '一般不可移动文物（三普登录，列入绍兴市大运河世界文化遗产保护名录）', SXY),
    ('绍兴市', '越城区', '皋埠街道', '云陵桥', '民国', '皋埠镇山前徐村', 'wbd', '一般不可移动文物（三普登录，列入绍兴市大运河世界文化遗产保护名录）', SXY),
    ('绍兴市', '越城区', '皋埠街道', '兴隆桥', '清', '皋埠镇南祠小区西侧', 'wbd', '列入绍兴市大运河世界文化遗产保护名录（未定级）', SXY),
    ('绍兴市', '上虞区', '东关街道', '大安桥', '清', '东关街道高泾村古纤道上', 'wbd', '列入绍兴市大运河世界文化遗产保护名录（位于国保“浙东运河上虞段”古纤道上）', SXY),
    ('温州市', '瑞安市', '南滨街道', '大桥', '北宋', '南滨街道大桥村', 'xian', '瑞安市文物保护单位', RA),
    ('温州市', '瑞安市', '飞云街道', '栏杆桥', '南宋', '飞云街道孙桥村', 'xian', '瑞安市文物保护单位', RA),
    ('温州市', '瑞安市', '马屿镇', '永乐桥', '民国', '马屿镇河岙底村', 'xian', '瑞安市文物保护单位', RA),
    ('温州市', '泰顺县', '司前镇', '回澜桥', '清', '司前镇司前村', 'sb', '浙江省文物保护单位', '温州市/泰顺县文博单位名录（2024）.html'),
    ('温州市', '永嘉县', '岩头镇', '永度桥', '南宋', '岩头镇协岙村普安禅寺东南侧', 'xian', '永嘉县文物保护单位（第一批）', '温州市/永嘉县文物保护单位名录（2024）.html'),
    ('无锡市', '新吴区', '鸿山街道', '集义桥', '—', '鸿山街道', 'wbd', '无锡市文物控制单位（第三批，锡政发〔2016〕201号）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '鸿山街道', '积福桥', '—', '鸿山街道', 'wbd', '无锡市文物控制单位（第三批，锡政发〔2016〕201号）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '鸿山街道', '大通桥', '—', '鸿山街道', 'wbd', '无锡市文物控制单位（第三批，锡政发〔2016〕201号）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '鸿山街道', '外郞桥', '—', '鸿山街道', 'wbd', '无锡市文物控制单位（第三批，锡政发〔2016〕201号）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '鸿山街道', '坟塘桥', '—', '鸿山街道', 'wbd', '无锡市文物控制单位（第三批，锡政发〔2016〕201号）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '鸿山街道', '德溪桥', '—', '鸿山街道', 'wbd', '无锡市文物控制单位（第三批，锡政发〔2016〕201号）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '江溪街道', '圣塘桥', '—', '江溪街道', 'wbd', '无锡市文物控制单位（第三批，锡政发〔2016〕201号）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '鸿山街道', '毓秀桥', '—', '鸿山街道', 'wbd', '一般不可移动文物（三普文物点）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('无锡市', '新吴区', '硕放街道', '世家桥', '—', '硕放街道', 'wbd', '一般不可移动文物（三普文物点）', '无锡市/新吴区文物保护点一览表（2019）.html'),
    ('南京市', '六合区', '马鞍街道', '杨龙桥', '清', '马鞍街道勤丰村黄庄组西北', 'xian', '六合区文物保护单位', '南京市/六合区区级文物保护单位保护范围及建设控制地带（2020）.html'),
    ('南京市', '六合区', '横梁街道', '陈堡桥', '清', '横梁街道雨花石村', 'xian', '六合区文物保护单位', '南京市/六合区区级文物保护单位保护范围及建设控制地带（2020）.html'),
    ('南京市', '六合区', '冶山街道', '西汇桥', '清', '冶山街道东王社区老街北头', 'xian', '六合区文物保护单位', '南京市/六合区区级文物保护单位保护范围及建设控制地带（2020）.html'),
    ('嘉兴市', '平湖市', '当湖街道', '当湖第一桥', '清咸丰九年（1859）', '当湖街道市河西端', 'xian', '平湖市文物保护单位（1984年公布）', '嘉兴市/平湖市县（市）级文物保护单位名录（2021）.html')]:
    OUT.setdefault(city, []).append(dict(dist=d, town=tw, name=n, era=era, loc=loc, lv=lv, lvtxt=txt, doc='—', src=src))

json.dump(OUT, open(S + '/build/official.json', 'w'), ensure_ascii=False, indent=0)
for c, rs in OUT.items(): print(c, len(rs), [r['name'] for r in rs][:60])
