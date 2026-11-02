# -*- coding: utf-8 -*-
# 汇总一般不可移动文物（三普登录）与四普新发现未定级不可移动文物中的桥梁
import json, re, html, hashlib, os
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
towns = json.load(open(S + '/hz/towns.json'))
G3 = '一般不可移动文物（三普登录）'
G4 = '未定级不可移动文物（四普新发现）'
U = dict(
    yh='https://www.yuhang.gov.cn/art/2025/9/16/art_1229174782_1861133.html',
    gs='https://www.gongshu.gov.cn/col/col1229602407/art/2026/art_485cf2af008c490780daadcb310703ce.html',
    xs1='https://www.xiaoshan.gov.cn/col/col1229303104/art/2026/art_40b635ed85804fbb9be14c581dde73bf.html',
    xs2='https://www.xiaoshan.gov.cn/col/col1229292698/art/2026/art_6fb0ec768c77455ab1160bf1eb80cc7f.html',
    fy='https://www.fuyang.gov.cn/col/col1228923482/art/2026/art_52183baca1db47898a08e94c009c12e5.html',
    la='https://www.linan.gov.cn/col/col1229289091/art/2026/art_1e45d468c64a4e61bffd8feb71937112.html',
    jd='https://www.jiande.gov.cn/col/col1229535322/art/2026/art_cb5db2ecf58f4269aee587b44cd6ef7f.html',
    sc='https://www.hzsc.gov.cn/col/col1229262710/art/2026/art_ebac3ab588614dc2a0646e8ee531f705.html',
    tl='https://www.tonglu.gov.cn/col/col1229254257/art/2026/art_3753223afa6743418312cc06920efbe9.html',
)
NAMES = {
    U['yh']: '余杭区不可移动文物名录（三普，余政办〔2011〕317号）',
    U['gs']: '2026年杭州市拱墅区文博单位名录',
    U['xs1']: '萧山区第四次全国文物普查新发现不可移动文物公示（第一批）',
    U['xs2']: '萧山区第四次全国文物普查新发现不可移动文物公示（第二批）',
    U['fy']: '富阳区第四次全国文物普查新发现不可移动文物名录公示',
    U['la']: '临安区第四次全国文物普查新发现不可移动文物名录',
    U['jd']: '建德市第四次全国文物普查新发现不可移动文物公示',
    U['sc']: '上城区第四次全国文物普查新发现不可移动文物公示',
    U['tl']: '桐庐县第四次全国文物普查新发现不可移动文物公示',
}

def is_bridge(n):
    if re.search(r'遗址|碑|井|民居|旧址|墓|水文站|凉亭|宅|厂|楼|桥头$', n): return False
    return bool(re.search(r'桥$|桥（|桥及|吊桥|廊桥', n))

def post49(era):
    return bool(re.search(r'中华人民共和国|19[5-9]\d|20\d\d', era or ''))

def find_town(dist, addr):
    a = re.sub(r'^(浙江省)?(杭州市)?' + dist, '', addr)
    best = None
    for t in towns[dist]:
        sh = re.sub(r'(街道|镇|乡|畲族乡)$', '', t)
        i = a.find(sh)
        if i >= 0 and (best is None or i < best[0]): best = (i, t)
    return best[1] if best else None

out = []
def add(dist, town, name, era, loc, level, doc, src, note=''):
    if post49(era): return
    if re.search(r'^(近)?现代$|不详', era or ''):
        note = (note + '；' if note else '') + '名录只写“' + era + '”，具体年代待核实，如为1949年后修建则不在本项目范围'
    out.append(dict(dist=dist, town=town, name=name, era=era or '—', loc=loc, level=level, doc=doc, srcs=[src], struct='—', note=note, commons=None))

# --- A. 余杭区三普名录（含今临平区）
for r in json.load(open(S + '/l4/yh3p_bridges.json')):
    if r['level'] != '未定': continue
    name = r['name'].strip()
    if not is_bridge(name): continue
    addr = r['addr'].rstrip('。')
    if addr.startswith('钱江经济开发区'):
        dist, town, note = '临平区', '东湖街道', '名录地址写“钱江经济开发区”，按村名归入东湖街道'
    else:
        dist, town, note = r['dist'], r['town'], ''
    if not town: continue
    loc = re.sub(r'^' + re.sub(r'(街道|镇)$', '', town) + r'(街道|镇)?', '', addr).lstrip('，,')
    add(dist, town, name, r['era'], loc, G3, '余政办〔2011〕317号', U['yh'], note)

# --- B. 拱墅区2026文博单位名录中的一般不可移动文物
for name, town, loc, era in [
    ('华丰文河桥', '石桥街道', '华丰社区南横港上', '清'),
    ('阔板桥', '半山街道', '阔板桥社区5幢西侧，北距半山西南约300米处', '清'),
    ('万顺高桥', '康桥街道', '永和村沾驾桥港上', '清'),
    ('杨店高桥', '康桥街道', '蒋家浜村北马桥港上，方家车前', '清'),
    ('永福桥', '祥符街道', '郭家厍社区郭家厍路，北距石祥路约180米处', '待定'),
    ('平安桥', '康桥街道', '平安桥村平安桥河上，平安桥28号南', '清'),
    ('亦家桥', '祥符街道', '阮家桥社区丰潭路东侧，沁园路北侧，富强路96号', '待定')]:
    add('拱墅区', town, name, era, loc, '一般不可移动文物', '—', U['gs'])

# --- C. 四普新发现（结构化页面）
def page_rows(url):
    s = open(S + '/l4/p_' + hashlib.md5(url.encode()).hexdigest()[:8] + '.html', 'rb').read().decode('utf-8', 'ignore')
    rows = []
    for tr in re.findall(r'<tr.*?</tr>', s, re.S):
        cells = [re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', c))) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S)]
        if len(cells) >= 5 and cells[0].isdigit(): rows.append(cells)
    seen = set(); res = []
    for c in rows:
        k = (c[1], c[4])
        if k in seen: continue
        seen.add(k); res.append(c)
    return res

for key, dist in [('xs1', '萧山区'), ('xs2', '萧山区'), ('fy', '富阳区'), ('la', '临安区'), ('jd', '建德市')]:
    for c in page_rows(U[key]):
        name, era, addr = c[1], c[2], c[4]
        if '“毛主席万岁”' in name: continue  # 名称表明为1949年后修建
        if not is_bridge(name): continue
        town = find_town(dist, addr)
        if not town: print('NOTOWN', dist, name, addr); continue
        loc = re.sub(r'^(浙江省)?(杭州市)?' + dist, '', addr)
        loc = re.sub(r'^' + re.escape(town), '', loc).lstrip('，,')
        add(dist, town, name, era, loc, G4, '2026年公示', U[key])

# --- D. 四普新发现（附件中提取）
add('上城区', '彭埠街道', '郑家桥', '明代、清代', '王家井社区，麦庙港（古后沙河）上，地铁4号线新风站西侧', G4, '2026年公示', U['sc'])
add('桐庐县', '新合乡', '秋星桥', '清代', '松山行政村松山自然村七七坞路口', G4, '2026年公示', U['tl'])
add('桐庐县', '富春江镇', '茆坪仁寿桥', '近现代', '茆坪行政村茆坪自然村', G4, '2026年公示', U['tl'])
add('桐庐县', '分水镇', '喧坞桥', '清代', '三合村张家自然村村口罗沈线北侧十米处', G4, '2026年公示', U['tl'])

json.dump(dict(rows=out, names=NAMES), open(S + '/build/general.json', 'w'), ensure_ascii=False, indent=1)
import collections
print(len(out), collections.Counter((r['dist'], r['level'][:6]) for r in out))
