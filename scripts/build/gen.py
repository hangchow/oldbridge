# -*- coding: utf-8 -*-
import json, os, re, sys, importlib.util
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT = '/Users/sean/workspace/oldbridge/杭州市'
spec = importlib.util.spec_from_file_location('cur', S + '/build/curated.py')
cur = importlib.util.module_from_spec(spec); spec.loader.exec_module(cur)
towns = json.load(open(S + '/hz/towns.json'))
X = json.load(open(S + '/build/xlsx_bridges.json'))
CQ = json.load(open(S + '/build/cqlinks.json')) if os.path.exists(S + '/build/cqlinks.json') else {}  # 老百晓集桥链接
IMGSRC = json.load(open(S + '/build/imgsrc.json')) if os.path.exists(S + '/build/imgsrc.json') else {}
XLSX_URL = 'https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3210/site/attach/0/dd1633cd0c9d451b98d824990a31ae35.xlsx'
COUNTIES = ['桐庐县', '淳安县', '建德市']
SRCNAME = {
    "../../../文保名录/杭州市/临安印记（下）桥梁相关页.pdf": "《临安印记（下）》桥梁相关页",
    'https://mdaily.hangzhou.com.cn/hzrb/2026/04/18/article_detail_1_20260418A048.html': '杭州日报：钱塘区红机埠等入选四普新发现文物（2026年4月18日）',
    'https://mp.weixin.qq.com/s?__biz=MzU4MTUxOTYwNA==&mid=2247488418&idx=1&sn=39e7210bdf1dc4b6d102e2b07631cbae&chksm=fd470239ca308b2f3d527b55e98bdacb1ac928d1925c07277af1c59cf42fb8434bfc410cb152#rd': '微信公众号“宿舟河下”《良渚七贤桥村的古桥》（2025年6月20日）',
    'https://z.hangzhou.com.cn/2021/syjy/content/content_8336564.html': '洞霄宫遗迹之元同桥（杭州网，临安区博物馆供稿，2022）',
    XLSX_URL: '浙江省《全省文物保护点》统计表（杭州市文物保护点）',
    cur.WIKI_HZ: '维基百科：杭州市文物保护单位',
    cur.WIKI_ALL: '维基百科：杭州市各级文物保护单位列表',
    cur.YH: '杭州市余杭区各级文物保护单位（点）一览表（2023）',
    cur.JD: '维基百科：建德市各级文物保护单位列表',
    cur.TL: '2025年桐庐县文博单位名录（桐庐县人民政府）',
    cur.CA: '淳安县文博单位名录（淳安县人民政府，2022）',
    cur.HB7: '杭州市人民政府关于公布第七批市级文物保护单位的通知',
    'https://baijiahao.baidu.com/s?id=1709588752468179224': '西湖区30处历史建筑名单（都市快报，2021）',
    'https://zh.wikipedia.org/wiki/杭州市历史建筑': '维基百科：杭州市历史建筑',
}
OLD_TOWN = {'藻溪镇': '天目山镇', '三口镇': '板桥镇', '新桥乡': '岛石镇', '大峡谷镇': '龙岗镇'}
DROP_X = {('临安区', '青云桥'), ('临安区', '长安桥'), ('临安区', '镇固桥'), ('临安区', '长乐桥'),
          ('西湖区', '凌家桥烈士墓'), ('萧山区', '泥桥头后山窑址'), ('萧山区', '泥桥头馒头山窑址'), ('萧山区', '桥头东楼宗祠'),
          ('萧山区', '凌桥戴氏宗祠'), ('萧山区', '桥头黄乌墙门'), ('余杭区', '石桥村总管堂'), ('临平区', '塘栖八字桥檐廊一角'), ('临安区', '桥头张氏宗祠')}
YHROWS = [r[1] for r in json.load(open(S + '/pages/yh_rows.json')) if r[0] == 9 and r[1][0] != '序号']
DUP_NOTE = {
    '太湖源青云桥': '浙江省文保点统计表里另以“青云桥”（太湖源镇青云村，临文广新〔2006〕34号）列为市级文物保护点，应是同一座桥，这里按较高的市保等级记录',
    '南山长安桥': '浙江省文保点统计表里另以“长安桥”（於潜镇南山坞村，临文广新〔2006〕34号）列为市级文物保护点，应是同一座桥，这里按较高的市保等级记录',
    '镇固桥': '浙江省文保点统计表里也列有“镇固桥”（湍口镇塘溪村，临文广新〔2006〕34号），应是同一座桥，这里按较高的市保等级记录',
    '龙岗长乐桥': '浙江省文保点统计表里另以“长乐桥”（原大峡谷镇龙井桥村，临文广新〔2006〕24号）列为市级文物保护点，应是同一座桥，这里按较高的市保等级记录',
}
# 余杭区原有文件里的补充信息
OVR = {
    ('上城区', '清波街道', '肖公桥'): dict(struct='石拱桥（单孔）', era='清乾隆八年（1743）', loc_add='（原位于秋涛路小学内，因西湖南线景区整合工程迁建至现址）', note='据用户提供的[桥旁说明牌](../../../文保名录/杭州市/肖公桥迁建说明牌.png)，肖公桥又名报恩桥，桥拱呈多边形，长21米、宽4.5米；原位于秋涛路小学内，因西湖南线景区整合工程实施异地搬迁及原状修缮'),
    ('上城区', '清波街道', '新横河桥'): dict(struct='石拱桥（单孔）', era='清光绪五年（1879）始建，六年（1880）落成', loc_add='（原位于仓河下北端，中河与东河交汇处，2002年因仓河下拓宽迁建至此）', note='据[浙江在线转引每日商报](https://zjnews.zjol.com.cn/zjnews/hznews/201709/t20170908_5003822.shtml)，桥长16.4米、宽4.3米、净跨6.8米；维基百科记长19米、宽4.6米，尺寸存在差异待核'),
    ('上城区', '笕桥街道', '全福桥'): dict(struct='石拱桥（单孔）', note='据[江干发布转发的古桥资料](https://www.thepaper.cn/newsDetail_forward_12012091)，乾隆年间已有此桥，位于农科院社区备塘河；省文保点统计表地址为水墩社区备塘河，社区名称差异待核'),
    ('上城区', '笕桥街道', '永安桥'): dict(name='永安桥（麦庄桥、麦庄庙桥）', struct='石拱桥（单孔）', era='北宋绍圣四年（1097）始建，明天启七年（1627）重建', note='据杭州日报，麦庄庙桥又称麦庄桥，桥碑记载绍圣四年建、天启七年重建；[2024年陈树尧文章](https://mp.weixin.qq.com/s/MyIUCDG-OFx5shzOz45CVQ)记桥长约14.50米，与[江干发布](https://www.thepaper.cn/newsDetail_forward_12012091)所记13.64米不同；2023年新命名同名道路桥与古桥关系待核'),
    ('上城区', '笕桥街道', '俞章陆桥'): dict(struct='石拱桥（单孔）', note='据[2024年陈树尧文章](https://mp.weixin.qq.com/s/VJtfTsxAYfy1qIRSJzuiQw)，桥长约15米，桥面曾加宽并铺设水泥；[江干发布](https://www.thepaper.cn/newsDetail_forward_12012091)记长15.5米，尺寸差异待核'),
    ('余杭区', '良渚街道', '永兴桥'): dict(name='永兴桥（俗称杜城桥）', struct='石梁桥（三孔）', loc_add='，跨前山港'),
    ('余杭区', '良渚街道', '回澜桥'): dict(struct='石梁桥（单孔）'),
    ('余杭区', '良渚街道', '杜甫桥'): dict(struct='石梁桥（五孔）', loc_add='，跨良渚港（今良渚文化村滨河公园一带）', note='“跨良渚港”出自网络图片说明，“良渚文化村滨河公园一带”是百度地图的地点信息，都不是官方资料；此桥原来误记在三墩镇名单里'),
    ('余杭区', '仁和街道', '兴福桥'): dict(name='兴福桥（俗称茅家桥）', struct='石梁桥（单孔）', loc_add='，跨茅家桥港', note='和西湖区三墩镇的明代兴福桥不是同一座；门牌号老百晓集桥写作“62号民宅西南”，这里按官方一览表'),
    ('余杭区', '仁和街道', '九省桥'): dict(struct='石梁桥（六墩七孔）'),
    ('余杭区', '仓前街道', '永兴桥'): dict(note='余杭区良渚街道也有一座永兴桥（杜城桥），不是同一座'),
}
TOWN_NOTE = {
    ('余杭区', '良渚街道'): '良渚街道在全国重点文物保护单位“大运河”的范围内，但大运河是整体公布的，没有单独列出桥梁，所以表里不写。',
    ('余杭区', '仁和街道'): '仁和街道在全国重点文物保护单位“大运河”的范围内，但大运河是整体公布的，没有单独列出桥梁，所以表里不写。',
}

def rows():
    R = []
    for c in cur.C:
        d = dict(c); d['srcs'] = [c['src']]
        if c['name'] in DUP_NOTE: d['note'] = (d['note'] + '；' if d['note'] else '') + DUP_NOTE[c['name']]
        R.append(d)
    for x in X:
        if (x['dist'], x['name']) in DROP_X: continue
        town = x.get('town')
        if not town:
            town = OLD_TOWN.get(x['town_raw']) or ('运河街道' if x['name'] == '报恩新桥' else None)
        if not town: print('NO TOWN', x); continue
        loc = x['loc']
        loc = re.sub(r'^(浙江省)?(杭州市)?' + x['dist'], '', loc)
        loc = re.sub(r'^' + re.escape(x['town_raw']), '', loc) or loc
        note = ''
        if x['town_raw'] != town and x['town_raw'] in OLD_TOWN: note = f'名录地址用的是撤并前的“{x["town_raw"]}”，今属{town}'
        d = dict(dist=x['dist'], town=town, name=x['name'], era=x['era'], loc=loc.lstrip('，,'), level='杭州市文物保护点',
                 doc=x['doc'], srcs=[XLSX_URL], struct='—', note=note, commons=None)
        if x['dist'] == '余杭区': d['srcs'].append(cur.YH)
        if x['dist'] == '余杭区':
            for y in YHROWS:
                if y[1] == x['name'] and y[3].startswith(town):
                    d['era'] = y[2]; d['loc'] = y[3][len(town):].lstrip('，,')
        o = OVR.get((x['dist'], town, x['name']))
        if o:
            d['name'] = o.get('name', d['name']); d['struct'] = o.get('struct', d['struct'])
            d['era'] = o.get('era', d['era'])
            if o.get('loc_add'): d['loc'] = d['loc'].rstrip('。') + o['loc_add']
            d['note'] = o.get('note', d['note'])
        R.append(d)
    CMX = {('拱墅区', '东新桥'): '20250423 Dongxin Qiao.jpg', ('拱墅区', '和睦桥'): '20261014 Hemu Qiao.jpg',
           ('余杭区', '万岁桥'): 'Wansui Bridge in Yuhang 03 2022-09.jpg', ('萧山区', '罗婆桥'): '20260816 Luopo Qiao.jpg'}
    for r in R:
        if (r['dist'], r['name']) in CMX and not r.get('commons'): r['commons'] = CMX[(r['dist'], r['name'])]
    LENS = json.load(open(S + '/build/cq_len.json')) if os.path.exists(S + '/build/cq_len.json') else {}
    for r in R: r['len'] = LENS.get(f"{r['dist']}|{r['town']}|{r['name']}", '—')
    # 杭州市文物遗产与历史建筑保护中心云端档案（官方）：长度优先采用；用户提供过数据的桥不改
    SDD = '/Users/sean/workspace/oldbridge/文保名录/杭州市/云端档案'
    SDL = {f.split('_', 1)[0]: f for f in os.listdir(SDD) if f.endswith('.html')}
    SD = json.load(open(S + '/build/singdo.json')) if os.path.exists(S + '/build/singdo.json') else {}
    LOCK = ('洲口桥', '星拱桥', '恩波桥', '长福桥', '元同桥')
    for r in R:
        sd = SD.get(f"{r['dist']}|{r['town']}|{r['name']}")
        if not sd: continue
        u = f"http://www.singdo.org/wenbao/luelan_disp.php?luelan_id={sd['id']}"
        if sd['len'] and not r['name'].startswith(LOCK):
            if r['len'] not in ('—', sd['len']) and float(r['len'][:-1]) != float(sd['len'][:-1]):
                r['note'] = (r['note'] + '；' if r['note'] else '') + f"长度原按其他资料为{r['len']}，现按杭州市文物遗产与历史建筑保护中心云端档案改为{sd['len']}"
            r['len'] = sd['len']
        elif sd['len'] and r['len'] != sd['len']:
            r['note'] = (r['note'] + '；' if r['note'] else '') + f"杭州市文物遗产与历史建筑保护中心云端档案记长度为{sd['len']}"
        if r['struct'] in ('—', '', None) and sd['struct']: r['struct'] = sd['struct']
        r['singdo'] = u
        lf = SDL.get(sd['id'])
        if lf: r['sdl'] = '文保名录/杭州市/云端档案/' + lf
    CQS = json.load(open(S + '/build/cq_struct.json')) if os.path.exists(S + '/build/cq_struct.json') else {}
    for r in R:
        k = f"{r['dist']}|{r['town']}|{r['name']}"
        if r['struct'] in ('—', '', None) and k in CQS: r['struct'] = CQS[k]
    # 成组公布的文物拆成单桥：每座桥一行，组名写进说明（资料来自杭州市文物遗产与历史建筑保护中心云端档案）
    SPLIT = {
        '中河南段古桥（水澄桥、化仙桥、海月桥、洋泮桥、六部桥、南星桥）': ('中河南段古桥及古泉', [
            ('六部桥', '南宋始建，现桥清代重建', '石拱桥（单孔）', '—'),
            ('南星桥', '南宋已存', '石拱桥（单孔）', '14米'),
            ('洋泮桥', '南宋已存，现桥明万历二十年（1592）重建', '石拱桥（单孔）', '18.3米'),
            ('海月桥', '明万历年间始建，现桥清代重建', '石拱桥（三孔）', '28.6米'),
            ('化仙桥', '原为木桥，明成化十三年（1477）改建为石拱桥', '石拱桥（单孔）', '21.05米'),
            ('水澄桥', '清康熙年间已存，现桥清光绪二十六年（1900）重建', '石梁桥（三孔）', '19.6米')]),
        '苏堤六桥（映波桥、锁澜桥、望山桥、压堤桥、东浦桥、跨虹桥）': ('西湖三堤·苏堤', [(n, '—', '石拱桥（单孔）', '—') for n in ['映波桥', '锁澜桥', '望山桥', '压堤桥', '东浦桥', '跨虹桥']]),
        '杨公堤六桥（环璧桥、流金桥、卧龙桥、隐秀桥、景行桥、浚源桥）': ('西湖三堤·杨公堤', [(n, '2003年重建（杨公堤恢复工程）', None, '—') for n in ['环璧桥', '流金桥', '卧龙桥', '隐秀桥', '景行桥', '浚源桥']]),
        '党山镇古桥（延寿桥、永禄桥、永福桥、迎福桥）': ('党山镇古桥', [
            ('延寿桥', '清', '石梁桥（三孔）', '—'),
            ('永禄桥', '清', '石梁桥（三孔）', '—'),
            ('永福桥', '清', '石梁桥（单孔）', '9.6米'),
            ('迎福桥', '清', '石梁桥（单孔）', '14米')]),
        '环溪双桥': ('环溪双桥', [
            ('安澜桥', '清嘉庆年间（1796—1820）', '石拱桥（单孔）', '18.2米'),
            ('保安桥', '民国元年（1912）', '石拱桥（单孔）', '14.8米')])}
    SPNOTE = {'迎福桥': '1971年桥面改为水泥板', '安澜桥': '又名鼍桥，跨屏源溪', '保安桥': '跨应家溪',
              '延寿桥': '俗称井亭桥', '永禄桥': '又名三眼桥', '永福桥': '又名小桥'}
    out = []
    for r in R:
        sp = SPLIT.get(r['name'])
        if not sp: out.append(r); continue
        grp, ms = sp
        for n, era, st, ln in ms:
            m = dict(r); m['srcs'] = list(r['srcs'])
            m['name'] = n; m['len'] = ln; m['struct'] = st or r['struct']
            if era != '—': m['era'] = era
            gn = f'“{grp}”（{len(ms)}座桥成组公布）的组成部分，这里按单桥列出'
            if grp.startswith('西湖三堤'): gn = f'“西湖三堤”整体列为市保，本桥是{grp[5:]}{len(ms)}桥之一'
            if grp == '西湖三堤·杨公堤': gn += '；现桥多为2003年杨公堤恢复工程重建'
            if n == '景行桥': gn += '；另有“景行古桥”单列为市级文物保护点'
            if grp == '中河南段古桥及古泉': gn += '；这一处文物沿中河南段分布在紫阳、南星等街道，统一记在南星街道'
            m['note'] = gn + ('；' + SPNOTE[n] if n in SPNOTE else '')
            pid = {'中河南段古桥及古泉': '168', '西湖三堤·苏堤': '185', '西湖三堤·杨公堤': '185'}.get(grp)
            if pid and SDL.get(pid):
                m['singdo'] = f'http://www.singdo.org/wenbao/luelan_disp.php?luelan_id={pid}'
                m['sdl'] = '文保名录/杭州市/云端档案/' + SDL[pid]
            out.append(m)
    R = out
    # 文保点“永安桥（五圣桥）”即后来升为市保的“清凉峰永安桥”（现场市保碑与旧“永安桥”碑并立），合并为一条
    ws = next((r for r in R if r['dist'] == '临安区' and r['name'] == '永安桥（五圣桥）'), None)
    qy = next((r for r in R if r['dist'] == '临安区' and r['name'] == '清凉峰永安桥'), None)
    if ws and qy:
        R.remove(ws)
        qy['struct'] = ws['struct'] if qy['struct'] in ('—', '', None) else qy['struct']
        qy['len'] = ws['len'] if qy['len'] in ('—', '', None) else qy['len']
        qy['note'] = (qy['note'] + '；' if qy['note'] else '') + '原名永安桥，又名五圣桥，原为杭州市文物保护点（浙江省统计表仍按“永安桥（五圣桥）”列出），后作为第五批增补升为市保；桥头市保碑与旧“永安桥”碑并立，可证是同一座桥'
    # 1949年后修建的桥：列入文保名录、历史建筑、不可移动文物名录的照收，只有“尚未定级（待核实）”的不收
    R = [r for r in R if not (re.search(r'中华人民共和国|19[5-9]\d|20\d\d', r['era'] or '') and r['level'].startswith(('尚未定级',)))]
    # 并入一般不可移动文物 / 四普新发现，按 区+乡镇+桥名 去重
    GEN = json.load(open(S + '/build/general.json'))
    SRCNAME.update(GEN['names'])
    def core(n): return re.sub(r'（.*?）|\(.*?\)|\s', '', n)
    for g in GEN['rows']:
        a = core(g['name'])
        dup = [r for r in R if r['dist'] == g['dist'] and r['town'] == g['town'] and (core(r['name']) == a or (min(len(a), len(core(r['name']))) >= 3 and (core(r['name']) in a or a in core(r['name']))))]
        if dup:
            d0 = dup[0]
            if d0['level'].startswith('尚未定级'):   # 原来只是“尚未定级”的，按官方名录升级等级、公布文件、来源，位置以名录为准
                print('UPGRADE', g['dist'], g['town'], d0['name'], '->', g['level'])
                d0['note'] = '；'.join(x for x in (d0.get('note'), f"名录登记名“{g['name']}”" if core(g['name']) != core(d0['name']) else '', g.get('note')) if x)
                d0.update(level=g['level'], doc=g['doc'], loc=g['loc'] if g['loc'] not in ('', '—') else d0['loc'], srcs=g['srcs'] + [u for u in d0['srcs'] if u not in g['srcs']])
                if (d0.get('era') or '—').startswith('—'): d0['era'] = g['era']
                continue
            if core(d0['name']) == a or not ('四普' in g['level'] and '三普' in d0['level']): continue
            print('KEEP-BOTH', g['dist'], g['town'], g['name'], '/', d0['name'])   # 两条官方记录名称只是相近，按两座桥处理
        R.append(g)
    for r in R:
        if r['dist'] == '余杭区' and r['level'].startswith('杭州市文物保护单位') and cur.YH not in r['srcs']: r['srcs'].append(cur.YH)
    for item in json.load(open(S + '/build/missing.json')):
        if item.get('name') in ('浙东运河古纤道（和平桥段）', '衣锦桥下古纤道') and not any(r['dist'] == item['dist'] and r['name'] == item['name'] for r in R):
            R.append(item)
    return R

ORDER = ['全国重点', '浙江省', '杭州市文物保护单位', '建德市文物保护单位', '桐庐县文物保护单位', '淳安县文物保护单位', '杭州市文物保护点', '杭州市历史建筑', '一般不可移动文物', '未定级不可移动文物']
from townpages import protection_rank

def rank(r):
    return protection_rank(r)

def imgname(name, i=1):
    return re.sub(r'（.*?）|\(.*?\)', '', name).strip() + f'{i}.jpg'

def imgs_of(folder, name):
    return [imgname(name, i) for i in (1, 2, 3) if os.path.exists(os.path.join(folder, imgname(name, i)))]

def link(u):
    if u in ('', '—', None): return '来源待补'
    return f'[{SRCNAME.get(u, u)}]({u})'

def table(rs, folder, with_town=False):
    head = '| 序号 | ' + ('乡镇 | ' if with_town else '') + '桥名 | 结构 | 长度 | 时代 | 位置 | 文保等级 | 公布文件 | 图片 |'
    sep = '|' + '---|' * (10 if with_town else 9)
    out = [head, sep]
    for i, r in enumerate(rs, 1):
        fs = imgs_of(folder, r['name'])
        img = ' '.join(f'[{i}]({f})' for i, f in enumerate(fs, 1)) if fs else '暂无'
        nm = r['name']
        if r.get('sdl'):
            rel = os.path.relpath('/Users/sean/workspace/oldbridge/' + r['sdl'], folder)
            nm = f"[{r['name']}]({rel})"
        if (ck := f"杭州市|{r['dist']}|{r['town']}|{r['name']}") in CQ:
            nm += f" [?]({CQ[ck]})"
        cells = [str(i)] + ([r['town']] if with_town else []) + [nm, r['struct'] or '—', r.get('len', '—'), r['era'] or '—', r['loc'] or '—', r['level'], r['doc'] or '—', img]
        out.append('| ' + ' | '.join(c.replace('|', '／') for c in cells) + ' |')
    return '\n'.join(out)

def doc(title, rs, folder, with_town=False, extra_notes=()):
    L = [f'# {title}', '']
    if rs:
        L += [table(rs, folder, with_town), '']
    else:
        L += ['国保、省保、市保（县保）和市级文物保护点名录里，这里没有列入桥梁。', '']
    notes = list(extra_notes)
    for r in rs:
        if r['note']: notes.append(f'{r["name"]}：{r["note"]}。'.replace('。。', '。'))
    if rs:
        notes.append('结构一列标“—”的，是没有查到可靠资料；部分结构来自“老百晓集桥”网站。')
    L += ['## 说明', ''] + [f'- {n}' for n in notes] if notes else []
    if notes: L.append('')
    for r in rs:
        if r.get('singdo'): SRCNAME[r['singdo']] = f'杭州市文物遗产与历史建筑保护中心云端档案：{r["name"]}'
    srcs = []
    for r in rs:
        for u in r['srcs'] + ([r['singdo']] if r.get('singdo') else []):
            if u not in srcs: srcs.append(u)
    if not rs: srcs = [XLSX_URL, cur.WIKI_HZ, cur.WIKI_ALL]
    L += ['## 来源', ''] + [f'- {link(u)}' for u in srcs] + ['']
    imgs = []
    for r in rs:
        for fn in imgs_of(folder, r['name']):
            s = IMGSRC.get(os.path.relpath(os.path.join(folder, fn), ROOT))
            line = f'| [{fn}]({fn}) | {s or "—"} |'
            if line not in imgs: imgs.append(line)
    if imgs:
        L += ['## 图片来源', '', '| 文件 | 来源 |', '|---|---|'] + imgs + ['', '维基共享资源的图片按原许可协议使用；其他网站的图片版权归原作者。', '']
    return '\n'.join(L)

def main():
    R = rows()
    # 一般不可移动文物 / 四普新发现是最后并入的，也按人工结构表补（build/cq_struct.json）
    CQS2 = json.load(open(S + '/build/cq_struct.json'))
    for r in R:
        k = f"{r['dist']}|{r['town']}|{r['name']}"
        if (r.get('struct') or '—') == '—' and k in CQS2: r['struct'] = CQS2[k]
    # 结构为“—”或只写桥型、没有孔数的，按老百晓集桥页面补桥型和孔数（build/cqholes.py）
    HOLES = json.load(open(S + '/build/cq_holes.json')) if os.path.exists(S + '/build/cq_holes.json') else {}
    LENF = json.load(open(S + '/build/cq_len_fill.json')) if os.path.exists(S + '/build/cq_len_fill.json') else {}
    for r in R:
        hk = '杭州市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
        if hk in HOLES and ((r.get('struct') or '—') == '—' or re.fullmatch(r'石?(拱|梁)桥|石板桥|平桥|廊桥', r['struct'])): r['struct'] = HOLES[hk]
        if hk in LENF and (r.get('len') or '—') in ('—', ''): r['len'] = LENF[hk]
    # 时代只写朝代或“—”的，按老百晓集桥、云端档案补具体年代（build/erafill.py）
    EF = json.load(open(S + '/build/era_fill.json')) if os.path.exists(S + '/build/era_fill.json') else {}
    for r in R:
        ek = '杭州市|' + r['dist'] + '|' + r['town'] + '|' + r['name']
        if ek in EF and (r['era'] or '—') == EF[ek]['old'] and EF[ek]['era'] not in (r['era'] or ''):   # 原文已含同样年代的不再改
            f = EF[ek]; old = r['era'] or '—'
            ds = [d for d in ('宋', '元', '明', '清', '民国') if d in old.replace('中华民国', '民国')]
            r['era'] = f['era'] if all(d in f['era'] for d in ds) else old + '；' + f['era']
            src = '老百晓集桥' if f['src'] == 'cq' else '杭州市文物遗产与历史建筑保护中心云端档案'
            r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'具体年代据{src}（名录原写“{old}”）'

    # 拱墅区福寿长桥与余杭区三普登录的谢尚书庙桥：实地寻桥资料视为同一座桥（良渚、祥符交界），只在拱墅区列出
    for r in R:
        if (r['dist'], r['town'], r['name']) == ('拱墅区', '祥符街道', '福寿长桥'):
            r['name'] = '福寿长桥（谢尚书庙桥）'; r['loc'] = '祥符街道总管堂社区'
            r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + '拱墅区文博名录（2026年5月）记为福寿长桥，地址祥符街道总管堂社区，清代；2026年实地寻桥资料认为即余杭区三普登录的谢尚书庙桥（余杭区良渚街道），位于良渚、祥符交界，尚待官方确认；余杭区不再单列。云端档案“历史建筑”库余杭区第一批第114号谢尚书庙桥（良渚街道谢村谢家塘东，南北向跨谢家塘），保护图则记为五孔石梁桥，桥长28米、宽2.6米、高约4米，因西侧建巨州路桥、东侧建上塘路高架桥已废弃不用；长度据此'

    # 云端档案“历史建筑”库（singdo.org/libao/）的桥：已有的升为历史建筑并挂本地档案，没有的新增（build/libao.json，scripts/tools/libao.py）
    LB = json.load(open(S + '/build/libao.json')); LBP = json.load(open(S + '/singdo/libao/bridges.json'))
    LOW = ('一般不可移动文物', '尚未定级', '未定级')
    for x in LB:
        p = LBP[x['id']]; sdl = '文保名录/杭州市/' + p['local']
        if x['op'] == 'up':
            r = next((r for r in R if f"{r['dist']}|{r['town']}|{r['name']}" == x['key']), None)
            if not r: print('LIBAO MISS', x['key']); continue
            if r['level'].startswith(LOW):
                old = r['level']; r['level'] = x['level']
                r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'原为{old}'
            elif '历史建筑' not in r['level']:
                r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f"另列为{x['level']}"
            if not r.get('sdl'): r['sdl'] = sdl
        else:
            R.append(dict(dist=x['dist'], town=x['town'], name=x['name'], era=x['era'], loc=x['loc'], level=x['level'], doc=x['doc'],
                          src='http://www.singdo.org/libao/luelan_disp.php?luelan_id=' + x['id'], srcs=['http://www.singdo.org/libao/luelan_disp.php?luelan_id=' + x['id']],
                          struct=x['struct'], len=x['len'], note=x['note'], sdl=sdl))
            SRCNAME['http://www.singdo.org/libao/luelan_disp.php?luelan_id=' + x['id']] = f"杭州市文物遗产与历史建筑保护中心云端档案（历史建筑）：{x['name']}"
    # 云端档案保护范围图、历史建筑保护图则上的结构、长度（图片文字识别，build/ocr_fill.json）：只补缺的
    OF = json.load(open(S + '/build/ocr_fill.json')) if os.path.exists(S + '/build/ocr_fill.json') else {}
    for r in R:
        f = OF.get(f"{r['dist']}|{r['town']}|{r['name']}")
        if not f: continue
        got = []
        if f.get('struct') and not re.search('孔|跨', r.get('struct') or '') and not re.search('钢|混凝土|水泥|铁|廊', r.get('struct') or ''): r['struct'] = f['struct']; got.append('结构')
        if f.get('len') and (r.get('len') or '—') in ('—', ''): r['len'] = f['len']; got.append('长度')
        if got: r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + '、'.join(got) + '据云端档案保护图则'
        if f.get('len') and r.get('len') not in ('—', '') and re.fullmatch(r'[\d.]+米', r.get('len') or '') and float(r['len'][:-1]) != float(f['len'][:-1]) and '长度' not in got: r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f"云端档案保护图则另记长度为{f['len']}"
    for r in R:
        if (r['dist'], r['town'], r['name']) == ('萧山区', '衙前镇', '巽龙桥'):
            r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + '长度按云端档案保护图则（“桥身由两块长条石构成，长5.3米”），百度百科记“全长约13米”'
    # 名录只有名称、地址的桥，据微信公众号文章补的结构、长度（文章标题写在说明里）
    WX = {('拱墅区', '石桥街道', '华丰文河桥'): ('石拱桥（单孔）', '11.5米', '清乾隆年间（1736—1795）', '结构、长度、年代据微信公众号文章《拱墅华丰文河桥》（陈树尧）：单孔半圆形石拱桥，全长约11.50米，孔跨径3.80米，桥面石板为近年修缮时新换'),
          ('拱墅区', '康桥街道', '杨店高桥'): ('石梁桥（三孔）', '—', '清光绪年间', '东西走向，原为三孔石梁桥，河道变窄后两侧桥台已不可见；桥上刻石记为清光绪年间所建，南北桥额刻“杨店高桥”，东侧石排柱有两处莲花字堂。据[微信公众号“宿舟河下”：《拱墅区康桥街道的古桥》（2026年3月13日）](https://mp.weixin.qq.com/s/nWHtXoqUvKKUHWHcZdJViQ)。2017年西杨村拆迁时随文物调查发现，同年“拱墅发布”图题称“清末时期 当地居民修建的石桥”，并列入城中村改造征集的“建筑类老物件”'),
          ('拱墅区', '祥符街道', '亦家桥'): ('石拱桥（单孔）', '—', '2013年重建', '现桥为2013年重建（栏板纪年），全部为新石材，是绿道中的景观桥；栏板刻“亦佳桥”，文物标志牌作“亦家桥”。据[微信公众号“宿舟河下”：《看似不像文物但已成为一般不可移动文物的亦家桥》（2025年10月31日）](https://mp.weixin.qq.com/s/05k2-qXO5whtIlSuNn77iQ)'),
          ('拱墅区', '康桥街道', '万顺高桥'): ('石梁桥（三孔）', '—', None, '南北走向，三孔石梁桥，桥墩为多层石条垒叠的石墩；东侧桥额刻“万顺高桥”。据[微信公众号“宿舟河下”：《拱墅区康桥街道的古桥》（2026年3月13日）](https://mp.weixin.qq.com/s/nWHtXoqUvKKUHWHcZdJViQ)'),
          ('拱墅区', '康桥街道', '平安桥'): ('钢筋混凝土桥（桥面铺有原古桥构件）', '—', '清同治元年（1862）始建，近年重建', '现桥为钢筋混凝土结构，桥面铺有数块原古桥构件，其中一块刻建桥纪年及“里人重修”落款（“桥”字刻作“碻”）；原桥建于清同治元年（1862）。据[微信公众号“宿舟河下”：《拱墅区康桥街道的古桥》（2026年3月13日）](https://mp.weixin.qq.com/s/nWHtXoqUvKKUHWHcZdJViQ)'),
          ('拱墅区', '祥符街道', '永福桥'): ('石拱桥（单孔）', '—', None, '结构据微信视频号“韩想有钱”2023年8月17日视频截图（单孔石拱桥，桥面两侧有石栏杆）'),
          ('西湖区', '西湖街道', '断桥'): ('石拱桥（单孔）', '—', '唐代已有，现桥1921年重建', '据老百晓集桥：唐代已有“断桥”之名，现桥为1921年重建的单孔环洞石拱桥，长8.8米，宽8.6米，净跨6.1米'),
          ('西湖区', '西湖街道', '映波桥'): (None, '—', '北宋始建，民国九年（1920）桥面改石级为斜坡', '年代据老百晓集桥'),
          ('西湖区', '西湖街道', '锁澜桥'): (None, '—', '北宋始建，民国九年至十一年（1920—1922）桥面改石级为斜坡', '年代据老百晓集桥'),
          ('西湖区', '西湖街道', '望山桥'): (None, '—', '北宋始建，民国九年至十一年（1920—1922）桥面改石级为斜坡', '年代据老百晓集桥'),
          ('西湖区', '西湖街道', '压堤桥'): (None, '—', '北宋始建，民国九年至十一年（1920—1922）桥面改石级为斜坡', '年代据老百晓集桥'),
          ('西湖区', '西湖街道', '东浦桥'): (None, '—', '北宋始建，民国九年至十一年（1920—1922）桥面改石级为斜坡', '年代据老百晓集桥'),
          ('西湖区', '西湖街道', '跨虹桥'): (None, '—', '北宋始建，明代桥址略有移动', '年代据老百晓集桥：苏堤六桥中唯一移动过桥址的'),
          ('西湖区', '留下街道', '古楹春桥'): (None, '—', '清乾隆二十八年（1763）重建', '年代据云端档案（历史建筑）：始建年代无考，清乾隆二十八年重建，薄拱式单孔石拱桥'),
          ('西湖区', '西湖街道', '玉涧桥'): ('石拱桥（双孔）', '—', '明洪武年间始建，清康熙间重修；2003年自桐庐迁建', '原在桐庐县分水镇丰收村（印渚镇），明洪武年间始建，现桥为清康熙间重修，2003年8月按原貌迁至西湖杨公堤景区；双孔石拱桥，老百晓集桥记长29.1米，[微信公众号“方志浙江”：《浙江古桥——桐庐古桥风韵》（2022年7月19日）]记长32米、单孔跨度9.5米'),
          ('西湖区', '西湖街道', '永福桥'): ('石梁桥（三孔，斜托梁）', '约30米', '明弘治年间始建，民国初重修；2003年自桐庐迁建', '原在桐庐县横村镇深畈村，明弘治年间始建，称安福桥，原为单孔石拱桥（长27.4米）；民国初重修时改为三孔石梁桥，桥面条石由斜托梁支撑、以平行四边形楔石闭锁，形成梯形桥孔，改名永福桥；2003年8月迁至西湖杨公堤景区。据[微信公众号“方志浙江”：《浙江古桥——桐庐古桥风韵》（2022年7月19日）]'),
          ('西湖区', '西湖街道', '毓秀桥'): ('石拱桥（单孔）', '16米', '清道光九年（1829）；2003年自萧山迁建', '据现场说明牌：原位于萧山区新塘街道涝湖村，清道光九年（1829）里人陈有尚出资修建，单孔石拱桥，长16米，宽2.5米，东侧桥眉石镌刻“毓秀”二字，桥心石刻八卦图案；2003年按原貌迁移保护至西湖湖西景区'),
          ('西湖区', '西湖街道', '流金桥'): ('石拱桥（单孔）', '—', None, '孔数据老百晓集桥页面照片'),
          ('西湖区', '西湖街道', '隐秀桥'): ('石拱桥（单孔）', '—', None, '孔数据老百晓集桥页面照片'),
          ('西湖区', '西湖街道', '景行桥'): ('石拱桥（单孔）', '—', None, '孔数据老百晓集桥页面照片'),
          ('西湖区', '西湖街道', '浚源桥'): ('石拱桥（单孔，双桥并列）', '—', None, '老百晓集桥称“浚源桥也是双桥”，照片为两座单孔石拱桥并列'),
          ('西湖区', '西湖街道', '通利桥'): ('石拱桥（单孔）', '约14.5米', '清中叶以前', '据现场说明牌（老百晓集桥页面照片）：单孔石拱桥，长约14.5米、宽3.5米，纵联分节并列砌筑，2003年恢复；多篇游记称单孔石桥、建于清中叶以前，2003年保护性修复，现以栏杆围护、不能通行'),
          ('西湖区', '翠苑街道', '思娘桥'): (None, '15米', None, '长度据今日头条《千年古桥“思娘桥”》（2025年6月25日）'),
          ('西湖区', '蒋村街道', '伍郎桥'): ('石梁桥（三孔）', '17.6米', '清康熙六十一年（1722）；清光绪二十年重修', '据杭州日报《294岁的伍郎桥保住了》（2016年4月8日）：两墩三孔石板桥，桥面由三块长条石铺成，正中雕圆形葵花纹，高3.5米，宽1.7米，长17.6米；报道写“建于清乾隆三十六年，也就是1722年”，乾隆三十六年为1771年，按标题“294岁”取1722年（康熙六十一年）；“清光绪二十年（1895年）重修”中光绪二十年实为1894年。2014年花蒋路开通后旁建新桥，此桥保留'),
          ('西湖区', '留下街道', '栅桥'): ('石梁桥（三孔）', '18—19米', '清道光六年（1826）', '据今日头条“烟雨莽苍苍”《杭州古建筑之留下古灵慈桥和栅桥》（2024年9月21日）：因桥下设水栅又名水栅桥，旧有宝胜庙又名宝胜桥；两墩三孔石梁平桥，长十八九米，宽近2米，桥墩为三长条石并列的石排柱，桥面三段共九块长条石，中孔南侧桥板阳刻“万安桥”，无栏杆；在飞雪街晴雨桥北约80米'),
          ('西湖区', '灵隐街道', '古荡桥'): ('石拱桥（单孔）', '21米', '清道光元年（1821）重建', '据灵隐街道办事处2018年7月所立说明牌：位于庆丰社区，东西向横跨沿山河，原名古塘桥，《咸淳临安志》卷二十一载“古塘桥，城西钢线局前”；单孔石拱桥，长21米，宽3.1米，拱券分节并列法砌筑，金刚墙条石错缝平砌，有两根长系石，露明部分有雕花。另据小红书“夜何其”《寻桥记9 • 西溪古荡桥》（2026年1月17日）：单孔石拱桥，抱鼓石、望柱和多数栏板为新换，金刚墙、券石多为旧物；北侧栏板刻“道光元年桂月”、南侧刻“道光元年桂月立”，即1821年重建；灵隐街道两块简介牌一说明代始建，一说旧名古塘桥、南宋《咸淳临安志》已有记载'),
          ('西湖区', '西湖街道', '卧龙桥'): (None, '71.6米', None, '长度据搜狐（2018年12月20日）：杨公堤恢复时重建，桥长71.6米，宽12.7米，高4.3米'),
          ('拱墅区', '长庆街道', '广安新桥'): (None, '—', '南宋已有（端平桥），清顺治十三年（1656）重建', '跨东河，宝善桥南、凤起桥北；南宋称端平桥，桥上有安仁亭，明重修，因桥东有广积仓又名广积仓桥，清顺治十一年（1654）桥塌，十三年重建后名新桥；保存宋代石栏板二十块、望柱五根及部分桥身条石；桥额南刻“兆民永济”、北镌“四镜咸康”，南面栏板背面刻顺治重建桥志铭；1989年东河改造时重修。据微信公众号“互联网数字成果共享城”《杭州市原下城区文物单位简介之二十三“广安新桥”》（2023年1月27日，https://mp.weixin.qq.com/s/iwodl6XXx9nNXUc3TxTJbg）'),
          ('拱墅区', '半山街道', '花桥'): (None, '—', None, '类别为“近现代重要史迹及代表性建筑”（拱墅区文博单位名录2026，2017年8月25日公布）；结构、长度未查到，网上未见照片。待核实：附近崇杭街拱墅区界有公交站“大花桥”（350路、7439路，石塘公园旁、宣杭铁路一侧），可能即此桥所在；名录“宝杭铁路”疑为“宣杭铁路”之误'),
          ('西湖区', '西湖街道', '西泠桥'): (None, '54米', None, ''),
          ('西湖区', '灵隐街道', '白乐桥（原名万佛桥）'): (None, '14.8米', None, ''),
          ('西湖区', '灵隐街道', '合涧桥'): (None, '约10米', None, ''),
          ('西湖区', '西湖街道', '西泠印社锦带桥'): (None, '约1米（三尺）', None, ''),
          ('拱墅区', '半山街道', '阔板桥'): ('石拱桥（单孔）', '—', None, '现状：桥身主体原地埋于阔板桥路下保护（2000年后填河修路时就地填埋），杭玻阔板桥社区西墙角尚存部分残桥；单孔石拱桥，桥面宽约3米，桥洞直径约3米，桥面铺八米长的石板，左右原有石柱、石板护栏（1984年前被拆作建材），全长不详；1914年拱宸桥地图上位于金家堰与崇光寺之间；2023年6月底拱墅区文物局授“全国文物普查一般不可移动文物”牌，牌立于残桥旁。据微信公众号“半山发布”《半山文化遗存寻踪丨毅行—阔板桥下流水的记忆》（2024年4月10日，https://mp.weixin.qq.com/s/v2HxEdlO91DJPADRUHOr6Q）')}
    for r in R:
        w = WX.get((r['dist'], r['town'], r['name']))
        if not w: continue
        if w[0] and ((r.get('struct') or '—') == '—' or not re.search('孔|跨', r.get('struct') or '')): r['struct'] = w[0]
        if (r.get('len') or '—') in ('—', '') and w[1] and w[1] != '—': r['len'] = w[1]
        if w[2] and ((r.get('era') or '—') in ('清', '明', '—', '待定', '民国', '明、清') or w[2].startswith(r.get('era') or '—')): r['era'] = w[2]
        if w[3]: r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + w[3]
        MV = {'玉涧桥': '原在桐庐县分水镇丰收村，2003年迁建于此', '永福桥': '原在桐庐县横村镇深畈村，2003年迁建于此', '毓秀桥': '原在萧山区新塘街道涝湖村，2003年迁建于此'}
        if r['dist'] == '西湖区' and r['name'] in MV and '迁建' not in (r.get('loc') or ''): r['loc'] = (r.get('loc') or '—') + f"（{MV[r['name']]}）"
    # 余杭区良渚街道谢尚书庙桥即拱墅区福寿长桥，只在拱墅区列一次
    R[:] = [r for r in R if (r['dist'], r['town'], r['name']) != ('余杭区', '良渚街道', '谢尚书庙桥')]
    for r in R:
        if (r['dist'], r['town'], r['name']) == ('余杭区', '仓前街道', '新桥'): r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + '三普登录名“吴山前新桥”（东西向跨新桥港）'
    R[:] = [r for r in R if (r['dist'], r['town'], r['name']) != ('余杭区', '仓前街道', '吴山前新桥')]
    # 用户确认古水登桥与水澄桥为同一座，保留市保记录。
    for r in R:
        if (r['dist'], r['town'], r['name']) == ('上城区', '南星街道', '水澄桥'):
            r['note'] = (r.get('note') or '') + '；古水登桥（水登桥）按用户确认与水澄桥合并，另见[老百晓集桥](http://www.china-qiao.com/ql15/hz_ql/hzvql070.htm)'
    R[:] = [r for r in R if (r['dist'], r['town'], r['name']) != ('上城区', '南星街道', '古水登桥')]
    # 姚陡门桥是历史建筑姚斗门桥的异写，保留最高等级及现存档案。
    for r in R:
        if (r['dist'], r['town'], r['name']) == ('上城区', '笕桥街道', '姚斗门桥'):
            r['note'] = (r.get('note') or '') + '；又写作姚陡门桥，据老百晓集桥建在唐代姚陡门（闸门）基础上，南宋已有记载，现桥年代以档案记载并保留差异'
    R[:] = [r for r in R if (r['dist'], r['town'], r['name']) != ('上城区', '笕桥街道', '姚陡门桥')]
    R = __import__('linan_book').apply(R)
    R = __import__('linan_xia').apply(R)
    R = __import__('keling').apply(R)
    R = __import__('chunan_wenwu').apply(R)
    R = __import__('leijiaqiao').apply(R)
    if not any((r['dist'], r['town'], r['name']) == ('拱墅区', '文晖街道', '打铁关纤道') for r in R):
        R.append(dict(dist='拱墅区', town='文晖街道', name='打铁关纤道', struct='纤道（石板路）', len='—', era='—', loc='文晖街道打铁关一带，具体位置待核', level='尚未定级（待核实）', doc='—', src='—', srcs=[], commons=None, note='据用户提供线索收录；具体位置、现状、水面范围及保护等级待核'))
    for r in R:
        if (r['dist'], r['town'], r['name']) == ('淳安县', '瑶山乡', '云溪廊桥'):
            source = '../../文保名录/杭州市/淳安县文物保护单位一览表2025.doc'
            if source not in r.setdefault('srcs', []): r['srcs'].append(source)
    by = {}
    for r in R: by.setdefault((r['dist'], r['town']), []).append(r)
    bad = [k for k in by if k[0] not in towns or (k[1] not in towns[k[0]] and not (k[0] in COUNTIES and k[1] == '乡镇待核'))]
    if bad: print('BAD TOWN KEYS', bad); sys.exit(1)
    n_files = 0
    for dist, ts in towns.items():
        if dist in COUNTIES:
            continue  # 三县市乡镇页由统一模板生成，停用旧区县明细输出。
        for t in ts:
            if (dist, t) == ('西湖区', '三墩镇'): continue  # 手工整理的文件，单独处理
            folder = os.path.join(ROOT, dist, t); os.makedirs(folder, exist_ok=True)
            rs = sorted(by.get((dist, t), []), key=rank)
            notes = [TOWN_NOTE[(dist, t)]] if (dist, t) in TOWN_NOTE else []
            open(os.path.join(folder, f'{t}古桥.md'), 'w').write(doc(f'杭州市{dist}{t}不可移动文物：桥梁', rs, folder, False, notes))
            n_files += 1
    json.dump(R, open(S + '/build/all_rows.json', 'w'), ensure_ascii=False, indent=1)
    print('files', n_files, 'bridges', len(R), 'excluding 三墩')

if __name__ == '__main__':
    main()
