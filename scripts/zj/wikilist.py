# -*- coding: utf-8 -*-
# 解析维基“××各级文物保护单位列表”原文，取出桥梁（含成组文物里的桥）
import re
LINK = re.compile(r'\[\[(?:[^]|]*\|)?([^]]*)\]\]')
def clean(s):
    s = re.sub(r'<ref[^>]*/>|<ref.*?</ref>', '', s, flags=re.S)
    s = re.sub(r'\[\[(?:File|文件|Image):[^]]*\]\]', '', s)
    s = LINK.sub(r'\1', s)
    s = re.sub(r'<br\s*/?>', '；', s); s = re.sub(r'<[^>]+>', '', s); s = re.sub(r"'''?", '', s)
    s = re.sub(r'\{\{0\}\}', '', s); s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    return s.strip()
NOT = re.compile(r'^桥$|遗存|轮渡|遗址|窑址|台门|民居|故居|碑|摩崖|宗祠|洋龙局|村$|庙|寺|祠|学校|墓|堂|诞生地|街区|建筑群|旧址|古道$|老街|会馆|书院|塔$|亭$|牌坊|坊$|闸$|堰$|渠|码头|埠头|渡口|驿|关$|城墙|故里|古镇|古村|门$|桥头$|楼$|宅$|烽火台|景观|井$|遗迹|题记|石刻|爱吾庐|矴步|碇步|故居')
def isbridge(n): return '桥' in n and len(n) <= 16 and (not NOT.search(n) or bool(re.search(r'[^桥]桥$', n)) and not re.search(r'遗址|遗存|遗迹|轮渡|旧址', n))   # “张仙庙桥”“寺前桥”以桥结尾，是桥
def level_of(h, city=''):
    if '全国' in h: return 'gb'
    if '浙江省' in h or '江苏省' in h or '省级' in h: return 'sb'
    if '不可移动文物' in h or '历史建筑' in h: return 'wbd'
    if city and h.startswith(city) and not re.match(r'[一-龥]{1,4}(区|县|市)', h[len(city):]): return 'shi'
    return 'xian'
COLS = {'name': r'名称|名 称', 'num': r'编号', 'era': r'时代|年代', 'addr': r'所在|地址|位置|地点', 'pub': r'公布|批次|备注'}
def parse(text, city=''):
    text = re.sub(r'<!--.*?-->|<ref[^>]*/>|<ref.*?</ref>', '', text, flags=re.S)   # 标题里的 <ref> 带“=”会弄乱分节
    out = []
    parts = re.split(r'^(==+)\s*([^=\n]+?)\s*\1\s*$', text, flags=re.M)
    sec = ''
    for i in range(0, len(parts), 3):
        body = parts[i]
        if i > 0: sec = parts[i - 1]
        if not sec or '参考' in sec or '注释' in sec: continue
        lv = level_of(sec, city)
        for tb in re.findall(r'\{\|.*?\n\|\}', body, flags=re.S):
            rows = re.split(r'\n\|-[^\n]*', tb)
            hdr = []; batch = ''
            for rw in rows:
                lines = [l for l in rw.split('\n') if l.strip() and not l.startswith('{|')]
                if not lines: continue
                if all(l.startswith('!') for l in lines):
                    hs = [clean(re.sub(r'^!+|^[^|]*\|(?!\|)', '', x)) for l in lines for x in l.split('!!')]
                    if 'colspan' in lines[0]: batch = clean(lines[0].split('|')[-1])
                    else: hdr = [re.sub(r'.*\|', '', h).strip() for h in hs]
                    continue
                cells = []
                for l in lines:
                    if l.startswith('|'):
                        cells += [c for c in l[1:].split('||')]
                    elif l.startswith('!'): cells.append(re.sub(r'^![^|]*\|(?!\|)', '', l)[1:] if re.match(r'^![^|]*\|(?!\|)', l) else l[1:])   # 行首 “! scope="row" | 5” 是序号格
                    elif cells: cells[-1] += '\n' + l
                if not cells: continue
                col = {}
                for k, pat in COLS.items():
                    j = next((n for n, h in enumerate(hdr) if re.search(pat, h)), None)
                    if j is not None and j < len(cells): col[k] = cells[j]
                if 'name' not in col: col['name'] = cells[0]
                out += items(col, lv, sec, batch)
        # 无表格的条目：*名称	时代	地址，年份
        for l in re.sub(r'\{\|.*?\n\|\}', '', body, flags=re.S).split('\n'):
            if not l.startswith('*') or l.startswith('**'): continue
            t = clean(l.lstrip('*'))
            f = [x.strip() for x in re.split(r'\t+|，(?![^（]*）)', t) if x.strip()]
            if not f: continue
            out += [dict(name=n.replace(' ', ''), era=(f[1] if len(f) > 2 else ''), addr=(f[2] if len(f) > 2 else (f[1] if len(f) > 1 else '')), lv=lv, sec=sec, batch='', num='', group='')
                    for n in split_names(f[0])]
    return out
def split_names(n):
    # 括号里列出的桥（如“天姥古驿道（关爷殿、普济桥）”）
    inner = [x for p in re.findall(r'（(.*?)）', n) for x in re.split(r'[、，,]', p) if isbridge(x)]
    if inner and not isbridge(re.sub(r'（.*?）', '', n)): return inner
    n = re.sub(r'（.*?）|\(.*?\)|\[.*?\]', '', n.replace(' ', ''))
    if isbridge(n) and not re.search(r'[、与和及]', n.replace('和尚', '')): return [n]   # “建南和尚桥”的“和”不是连词
    ps = [x for x in re.split(r'[、与和及]', n) if x]
    if len(ps) < 2: return []
    if isbridge(n) and '、' not in n and any(len(p) < 2 or p == '桥' for p in re.split(r'[与和及]', n)): return [n]   # “中和桥”“永和桥”不是两座桥
    if not ps[-1].endswith('桥'): return [p for p in ps if isbridge(p)]
    if all(p.endswith('桥') for p in ps): return [p for p in ps if isbridge(p)]
    # “洗屐、砥流、招隐桥”：前面几项省略了“桥”字
    if all(len(p) <= 3 for p in ps[:-1]): return [p + '桥' for p in ps[:-1]] + [ps[-1]]
    return [p for p in ps if isbridge(p)]
def items(col, lv, sec, batch):
    raw = col['name']; lines = raw.split('\n')
    head = clean(lines[0]); subs = [clean(re.sub(r'^[#*]+', '', l)) for l in lines[1:] if re.match(r'^[#*]', l)]
    addr = col.get('addr', ''); al = [clean(re.sub(r'^[#*]+', '', l)) for l in addr.split('\n') if re.match(r'^[#*]', l)]
    base = dict(era=clean(col.get('era', '')), lv=lv, sec=sec, batch=batch, num=clean(col.get('num', '')))
    res = []
    if subs:
        for j, s in enumerate(subs):
            for n in split_names(s):
                res.append(dict(base, name=n, addr=(al[j] if j < len(al) else clean(addr.split('\n')[0])), group=head))
        return res
    return [dict(base, name=n, addr=clean(addr), group='' if n == head else head) for n in split_names(head)]
