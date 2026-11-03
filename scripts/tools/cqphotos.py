# 给缺照片的桥补“老百晓集桥”页面上的照片（每座最多3张，与已有照片逐一比对去重）
# 用法：python3 tools/cqphotos.py 杭州市 西湖区     （在 scripts/ 下运行）
import json, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ahash import ahash, dist
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); O = os.path.dirname(S)
city, D = sys.argv[1], sys.argv[2]
CQ = json.load(open(S + '/build/cqlinks.json'))
R = [r for r in json.load(open(S + '/build/all_rows.json')) if r['dist'] == D] if city == '杭州市' else []
SRC = json.load(open(S + '/build/imgsrc.json'))
COUNTIES = ['桐庐县', '淳安县', '建德市']
n = 0
for r in R:
    if (r['dist'], r['town']) == ('西湖区', '三墩镇'): continue   # 三墩镇是手工整理的文件
    u = CQ.get(f"{city}|{r['dist']}|{r['town']}|{r['name']}")
    if not u: continue
    folder = f"{O}/{city}/{r['dist']}" + ('' if r['dist'] in COUNTIES else f"/{r['town']}")
    base = re.sub(r'（.*?）|\(.*?\)', '', r['name']).strip()
    have = [f'{folder}/{base}{i}.jpg' for i in (1, 2, 3) if os.path.exists(f'{folder}/{base}{i}.jpg')]
    if len(have) >= 3: continue
    cache = S + '/cqv/' + u.split('china-qiao.com/')[1].replace('/', '_')
    if not os.path.exists(cache): continue
    h = open(cache, 'rb').read().decode('gb18030', 'ignore')
    title = re.sub(r'——.*', '', re.search(r'<title>(.*?)</title>', h).group(1)) if '<title>' in h else r['name']
    pics = list(dict.fromkeys(re.findall(r'src="(pic_[^"]+\.(?:jpg|jpeg|png))"', h, re.I)))
    hs = [ahash(p) for p in have]
    for pic in pics:
        if len(have) >= 3: break
        url = u.rsplit('/', 1)[0] + '/' + pic; tmp = '/tmp/cqp.jpg'
        subprocess.run(['curl', '-sL', '-m', '60', '-A', 'Mozilla/5.0', '-o', tmp, url]); time.sleep(0.3)
        if not os.path.exists(tmp) or os.path.getsize(tmp) < 5000: continue
        hh = ahash(tmp)
        if any(dist(hh, x) <= 18 for x in hs): continue
        dst = f'{folder}/{base}{len(have) + 1}.jpg'
        subprocess.run(['sips', '-s', 'format', 'jpeg', tmp, '--out', dst], capture_output=True)
        SRC[os.path.relpath(dst, f'{O}/{city}')] = f'[老百晓集桥：{title}]({u})'
        have.append(dst); hs.append(hh); n += 1; print('add', os.path.relpath(dst, O))
json.dump(SRC, open(S + '/build/imgsrc.json', 'w'), ensure_ascii=False, indent=1)
print('added', n)
