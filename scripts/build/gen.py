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
            d['loc'] += o.get('loc_add', ''); d['note'] = o.get('note', d['note'])
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
        '杨公堤六桥（环璧桥、流金桥、卧龙桥、隐秀桥、景行桥、浚源桥）': ('西湖三堤·杨公堤', [(n, '—', None, '—') for n in ['环璧桥', '流金桥', '卧龙桥', '隐秀桥', '景行桥', '浚源桥']]),
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
    # 1949年后修建的不收录
    R = [r for r in R if not re.search(r'中华人民共和国|19[5-9]\d|20\d\d', r['era'] or '')]
    # 并入一般不可移动文物 / 四普新发现，按 区+乡镇+桥名 去重
    GEN = json.load(open(S + '/build/general.json'))
    SRCNAME.update(GEN['names'])
    def core(n): return re.sub(r'（.*?）|\(.*?\)|\s', '', n)
    for g in GEN['rows']:
        a = core(g['name'])
        dup = [r for r in R if r['dist'] == g['dist'] and r['town'] == g['town'] and (core(r['name']) == a or (min(len(a), len(core(r['name']))) >= 3 and (core(r['name']) in a or a in core(r['name']))))]
        if dup:
            if core(dup[0]['name']) != a: print('DEDUP', g['dist'], g['town'], g['name'], '->', dup[0]['name'])
            continue
        R.append(g)
    for r in R:
        if r['dist'] == '余杭区' and r['level'].startswith('杭州市文物保护单位') and cur.YH not in r['srcs']: r['srcs'].append(cur.YH)
    return R

ORDER = ['全国重点', '浙江省', '杭州市文物保护单位', '建德市文物保护单位', '桐庐县文物保护单位', '淳安县文物保护单位', '杭州市文物保护点', '杭州市历史建筑', '一般不可移动文物', '未定级不可移动文物']
def rank(r):
    for i, k in enumerate(ORDER):
        if r['level'].startswith(k): return i
    return 99

def imgname(name, i=1):
    return re.sub(r'（.*?）|\(.*?\)', '', name).strip() + f'{i}.jpg'

def imgs_of(folder, name):
    return [imgname(name, i) for i in (1, 2, 3) if os.path.exists(os.path.join(folder, imgname(name, i)))]

def link(u):
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
            imgs.append(f'| [{fn}]({fn}) | {s or "—"} |')
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
        if ek in EF and (r['era'] or '—') == EF[ek]['old']:
            f = EF[ek]; old = r['era'] or '—'
            ds = [d for d in ('宋', '元', '明', '清', '民国') if d in old.replace('中华民国', '民国')]
            r['era'] = f['era'] if all(d in f['era'] for d in ds) else old + '；' + f['era']
            src = '老百晓集桥' if f['src'] == 'cq' else '杭州市文物遗产与历史建筑保护中心云端档案'
            r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + f'具体年代据{src}（名录原写“{old}”）'

    # 拱墅区福寿长桥与余杭区三普登录的谢尚书庙桥：实地寻桥资料视为同一座桥（良渚、祥符交界），只在拱墅区列出
    for r in R:
        if (r['dist'], r['town'], r['name']) == ('拱墅区', '祥符街道', '福寿长桥'):
            r['name'] = '福寿长桥（谢尚书庙桥）'; r['loc'] = '祥符街道总管堂社区'
            r['note'] = (r.get('note') or '') + ('；' if r.get('note') else '') + '拱墅区文博名录（2026年5月）记为福寿长桥，地址祥符街道总管堂社区，清代；2026年实地寻桥资料认为即余杭区三普登录的谢尚书庙桥（余杭区良渚街道），位于良渚、祥符交界，尚待官方确认；余杭区不再单列'

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
    # 余杭区良渚街道谢尚书庙桥即拱墅区福寿长桥，只在拱墅区列一次
    R[:] = [r for r in R if (r['dist'], r['town'], r['name']) != ('余杭区', '良渚街道', '谢尚书庙桥')]
    by = {}
    for r in R: by.setdefault((r['dist'], r['town']), []).append(r)
    bad = [k for k in by if k[0] not in towns or k[1] not in towns[k[0]]]
    if bad: print('BAD TOWN KEYS', bad); sys.exit(1)
    n_files = 0
    for dist, ts in towns.items():
        if dist in COUNTIES:
            folder = os.path.join(ROOT, dist); os.makedirs(folder, exist_ok=True)
            rs = sorted([r for t in ts for r in by.get((dist, t), [])], key=lambda r: (rank(r), ts.index(r['town'])))
            open(os.path.join(folder, f'{dist}古桥.md'), 'w').write(doc(f'杭州市{dist}不可移动文物：桥梁', rs, folder, True))
            n_files += 1; continue
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
