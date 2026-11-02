# 国保、省保缺孔数或长度的桥，到维基百科单桥条目取（条目须写到所在区县）
import json, re, time, urllib.request, urllib.parse, os
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
UA = {'User-Agent': 'oldbridge-research/1.0 (personal project)'}
def get(t):
    u = 'https://zh.wikipedia.org/w/api.php?' + urllib.parse.urlencode(dict(action='query', titles=t, prop='extracts', explaintext=1, redirects=1, format='json', variant='zh-cn'))
    for k in range(4):
        try:
            time.sleep(1.5); return list(json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40))['query']['pages'].values())[0]
        except urllib.error.HTTPError as e:
            if e.code != 429: return {}
            time.sleep(30 * (k + 1))
    return {}
N = '单一二两三四五六七八九十0-9'
L = json.load(open('/tmp/need_gbsb.json')); OUT = {}
for c, d, t, n, st, ln in L:
    core = re.sub(r'（.*?）', '', n)
    for title in [f'{core} ({c[:2]})', f'{core} ({d[:2]})', core]:
        pg = get(title); ex = pg.get('extract', '')
        if not ex or 'missing' in pg: continue
        if not (d[:2] in ex or c[:2] in ex): continue
        r = {}
        m = re.search(r'(?:全长|桥长|总长)(?:约|为)?\s*([0-9]+(?:\.[0-9]+)?)\s*米', ex)
        if m and ln == '—': r['len'] = m.group(1) + '米'
        h = re.findall(r'(?<![第' + N + r'])([' + N + r']{1,3})(?:孔|拱|跨)(?:石|梁|拱|，|、|桥)', ex)
        if h and len(set(h)) == 1 and '孔' not in st: r['holes'] = h[0]
        if r: OUT[f'{c}|{d}|{t}|{n}'] = dict(r, title=pg.get('title'))
        break
json.dump(OUT, open(S + '/build/wiki_fill.json', 'w'), ensure_ascii=False, indent=1)
for k, v in OUT.items(): print(k, v)
