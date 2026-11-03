# -*- coding: utf-8 -*-
# 结构为“—”或只写桥型（石拱桥、石梁桥）没有孔数的，从老百晓集桥页面取桥型和孔数
import json, re, os, subprocess, time
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
CQ = json.load(open(S + '/build/cqlinks.json'))
F = {'杭州市': 'build/all_rows.json', '湖州市': 'huz/rows.json', '嘉兴市': 'jx/rows.json', '上海市': 'sh/rows.json', '苏州市': 'sz/rows.json', '金华市': 'jh/rows.json', '绍兴市': 'sx/rows.json', '宁波市': 'nb/rows.json', '衢州市': 'qz/rows.json', '台州市': 'tz/rows.json', '温州市': 'wz/rows.json', '丽水市': 'ls/rows.json', '舟山市': 'zs/rows.json', '无锡市': 'wx/rows.json', '南京市': 'nj/rows.json', '常州市': 'cz/rows.json', '镇江市': 'zjs/rows.json', '扬州市': 'yz/rows.json'}
N = '单独一二两三四五六七八九十0-9'
TY = r'(石拱桥|拱桥|石梁桥|梁桥|石板桥|平桥|板梁桥|廊桥)'
def norm(h):
    h = {'1': '单', '2': '双', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九', '一': '单', '独': '单', '两': '双', '二': '双'}.get(h, h)
    return h if re.fullmatch(r'单|双|[三四五六七八九]|十[一二三四五六七八九]?|[二三四五六七八九]十[一二三四五六七八九]?', h) else None
def ty(t, ctx):
    if re.search(r'钢|混凝土|水泥', ctx): return None
    if '廊' in t:
        if re.search(r'石[墩礅]', ctx) and re.search(r'木梁|木平', ctx): return '石墩木梁廊桥'
        return '木拱廊桥' if '木拱' in ctx else '廊桥'
    return '石拱桥' if '拱' in t else '石梁桥'
def need(st): return st in ('—', '', None) or re.fullmatch(r'石?(拱|梁)桥|石板桥|平桥|廊桥', st)
def text(u):
    f = S + '/cqv/' + u.split('china-qiao.com/')[1].replace('/', '_')
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        subprocess.run(['curl', '-sL', '-m', '30', '-A', 'Mozilla/5.0', '-o', f, u]); time.sleep(0.2)
    s = open(f, 'rb').read().decode('gb18030', 'ignore')
    t = re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', s)))
    i = t.find('篇 '); t = t[i:] if i >= 0 else t
    return t.split('上一座')[0]
OUT, LOG, LEN = {}, [], {}
_R = json.load(open(S + '/singdo/recs.json')); _R = _R.values() if isinstance(_R, dict) else _R
SDI = {x['id']: x for x in _R if isinstance(x, dict)}
for c, p in F.items():
    for r in json.load(open(S + '/' + p)):
        st = r.get('struct') or '—'
        k = f"{c}|{r['dist']}|{r['town']}|{r['name']}"
        nd = need(st); nl = (r.get('len') or '—') == '—'
        if not nd and not nl: continue
        # 先用杭州市文物遗产与历史建筑保护中心云端档案（官方）简介，再用老百晓集桥页面
        sd = ''
        if r.get('sdl'):
            sid = r['sdl'].split('/')[-1].split('_')[0]
            if sid not in ('168', '185', '325', '564'):
                sd = SDI.get(sid, {}).get('intro', '')
                hp = '/Users/sean/workspace/oldbridge/' + r['sdl']
                if not sd and os.path.exists(hp):   # 本地档案网页的“文物简介”
                    hh = re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', open(hp, encoding='utf8').read())))
                    i = hh.find('文物简介'); sd = hh[i + 5:i + 1500] if i >= 0 else ''
        if not sd and k not in CQ: continue
        t = (sd + ' 。 ' if sd else '') + (text(CQ[k]) if k in CQ else '')
        # 长度：“全长/桥长/总长 N 米”，其次“，长 N 米”（排除湖长、东西长等）
        if nl:
            ml = re.search(r'(?:全长|桥长|总长|桥身长)\s*(?:为|约|达)?\s*约?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:米|m)', t) or \
                 re.search(r'(?:^|[，,。；\s、])(?:桥)?长(?:度?为)?\s*约?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:米|m)', t)
            if ml and 2 <= float(ml.group(1)) <= 600: LEN[k] = ml.group(1) + '米'
        if not nd: continue
        # 只看说本桥的句子：提到别的桥名的句子跳过（防止取到附近其他桥的孔数）
        own = core(r['name']) if 'core' in dir() else re.sub(r'（.*?）', '', r['name'])
        GENC = set('此该本这那座条石拱梁廊木古大小新旧号的长板浮吊平孔双单其全一两三四五六七八九十各引名代端头侧边主副座此')
        def mine(sent):
            for tok in re.findall(r'([一-龥]{2,4})桥', sent):
                nm2 = tok + '桥'
                if tok[-1] in GENC or nm2 in own or own.endswith(nm2) or nm2.endswith(own) or own in nm2 or re.search(r'的|之|大名|百晓|称', tok): continue
                return False
            return True
        to = '。'.join(x for x in re.split(r'[。；！？]', t) if mine(x))
        # 1) 标题下的类型标签，如［人行·单孔石拱桥］
        res = None
        tag = re.search(r'[\[［]([^\]］]*)[\]］]', t[:200])
        if tag:
            m = re.search(r'([' + N + r']{1,3})\s*孔[^\]］]*?' + TY, tag.group(1))
            if m and norm(m.group(1)[-1] if not norm(m.group(1)) else m.group(1)):
                res = (ty(m.group(2), tag.group(1)), norm(m.group(1)) or norm(m.group(1)[-1]), 'tag')
        # 2) 正文里“N孔……石拱桥”这样的说法：开头 150 字内第一处，或全文只有一种
        for src_t in (t[:400], to):
          if res: break
          if True:
              ms = [(norm(m.group(1)) or norm(m.group(1)[-1]), m.group(2), m.start(), src_t[max(0, m.start() - 12):m.end()])
                    for m in re.finditer(r'([' + N + r']{1,3})(?:孔|拱|全环)[^，。；、]{0,10}?' + TY, src_t)]
              ms += [(norm(m.group(2)) or norm(m.group(2)[-1]), m.group(1), m.start(), src_t[max(0, m.start() - 12):m.end()])
                     for m in re.finditer(r'(梁式|拱式|石拱|石梁|拱桥|梁桥|平桥)[^，。；、]{0,4}?([' + N + r']{1,3})孔', src_t)]
              ms.sort(key=lambda x: x[2])
              ms = [x for x in ms if x[0]]
              kinds = {(x[0], ty(x[1], x[3])) for x in ms}
              if ms and ((src_t is not to and ms[0][2] < 150) or len(kinds) == 1):
                  res = (ty(ms[0][1], ms[0][3]), ms[0][0], 'body')
        # 3) “凡十三空”“十二个桥墩”这类写法：N 空即 N 孔，N 个桥墩即 N+1 孔
        if not res:
            CN = '〇一二三四五六七八九'
            def num(x):
                if x.isdigit(): return int(x)
                x = x.replace('两', '二')
                if '十' in x:
                    a, b = x.split('十', 1); return (CN.index(a) if a else 1) * 10 + (CN.index(b) if b else 0)
                return CN.index(x) if len(x) == 1 and x in CN else None
            def zh(n): return {1: '单', 2: '双'}.get(n) or (('' if n < 10 else ('十' if n < 20 else CN[n // 10] + '十')) + (CN[n % 10] if n % 10 else '') if n >= 10 else CN[n])
            # 单独写的“N孔/N洞/N空”：全文说法一致才用；都没有时才按“N个桥墩”推算
            alln = {num(x) for x in re.findall(r'(?<![第一二两三四五六七八九十\d、])([一二两三四五六七八九十\d]{1,3})(?:孔|洞|空|跨(?![径度越过河溪江港湖]))(?![雀])', t[:250])} - {None, 0}
            if len(alln) != 1:
                alln = {num(x) for x in re.findall(r'(?<![第一二两三四五六七八九十\d、])([一二两三四五六七八九十\d]{1,3})(?:孔|洞|空|跨(?![径度越过河溪江港湖]))(?![雀])', to)} - {None, 0}
            mp = re.search(r'([一二两三四五六七八九十\d]{1,3})个桥墩', to)
            # “原有27洞、现存25洞”：以现存为准
            mx = re.search(r'现存([一二两三四五六七八九十\d]{1,3})(?:孔|洞|空)', t)
            if mx and num(mx.group(1)): alln = {num(mx.group(1))}
            n = alln.pop() if len(alln) == 1 else (num(mp.group(1)) + 1 if not alln and mp and num(mp.group(1)) is not None and not re.search(r'[一二两三四五六七八九十\d]孔', t) else None)
            if n: res = (('石拱桥' if '拱' in t[:400] else '石梁桥'), zh(n), 'count')
        # 页面开头写明是水泥/混凝土桥的，结构照写，不当石桥
        NOTCON = ('福丁桥', '白龙桥')   # 页面说的水泥桥是旁边别的桥
        if r['name'] not in NOTCON and re.search(r'(?:为|系|是|属|［[^］]{0,6}|\[[^]]{0,6})[^，。；]{0,10}(?:钢筋水泥|钢筋混凝土|水泥|混凝土)[^，。；]{0,8}(?:桥|结构)', t[:250]):
            if not res: res = ('', '', '')
            OUT[k] = ('钢筋混凝土' + ('拱桥' if '拱' in t[:250] else '桥')) + (f'（{res[1]}孔）' if res[1] else '')
            LOG.append((k, st, OUT[k], res)); continue
        if st == '廊桥':
            h = t[:800]; hn = f'（{res[1]}孔）' if res else ''
            if re.search(r'木拱|叠梁|编梁|贯木', h): OUT[k] = '木拱廊桥'
            elif re.search(r'石拱', h): OUT[k] = '石拱廊桥' + hn
            elif re.search(r'石墩|石砌桥墩|石桥墩|桥墩[^，。]{0,6}石', h):
                OUT[k] = ('石墩木梁廊桥' if re.search(r'木梁|木平|伸臂|木构|杉木|圆木|木桥面|架木|木廊|梁式木', h) else '石墩廊桥') + hn
            elif re.search(r'木梁|木平梁', h): OUT[k] = '木梁廊桥'
            LOG.append((k, st, OUT.get(k), res)); continue
        if res and res[0]:
            typ = res[0]
            if st not in ('—', '', None):
                old = '石拱桥' if '拱' in st else '石梁桥'
                if old != typ: LOG.append((k, st, 'CONFLICT', res)); continue
                typ = st if st.startswith('石') else old
            OUT[k] = f'{typ}（{res[1]}孔）'
        LOG.append((k, st, OUT.get(k), res))
json.dump(OUT, open(S + '/build/cq_holes.json', 'w'), ensure_ascii=False, indent=0)
json.dump(LEN, open(S + '/build/cq_len_fill.json', 'w'), ensure_ascii=False, indent=0)
print('len', len(LEN))
for l in LOG: print(*l)
print('found', len(OUT), 'of', len(LOG))
