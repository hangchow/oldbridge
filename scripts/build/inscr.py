# -*- coding: utf-8 -*-
# 找桥身题刻纪年：在老百晓集桥页面、云端档案简介里找“刻/镌/题/铭/纪年”等和年号同句的记载
import json, re, os, subprocess, time, sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
sys.path.insert(0, S + '/build'); from era import year
CQ = json.load(open(S + '/build/cqlinks.json'))
R = json.load(open(S + '/singdo/recs.json')); R = R.values() if isinstance(R, dict) else R
SDI = {x['id']: x for x in R if isinstance(x, dict)}
F = {'杭州市': 'build/all_rows.json', '湖州市': 'huz/rows.json', '嘉兴市': 'jx/rows.json', '上海市': 'sh/rows.json', '苏州市': 'sz/rows.json', '金华市': 'jh/rows.json', '绍兴市': 'sx/rows.json', '宁波市': 'nb/rows.json', '衢州市': 'qz/rows.json', '台州市': 'tz/rows.json', '温州市': 'wz/rows.json', '丽水市': 'ls/rows.json', '舟山市': 'zs/rows.json'}
def cqtext(u):
    f = S + '/cqv/' + u.split('china-qiao.com/')[1].replace('/', '_')
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        subprocess.run(['curl', '-sL', '-m', '30', '-A', 'Mozilla/5.0', '-o', f, u]); time.sleep(0.2)
    t = re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', open(f, 'rb').read().decode('gb18030', 'ignore'))))
    i = t.find('篇 '); return (t[i:] if i >= 0 else t).split('上一座')[0]
KW = r'刻|镌|题|铭|纪年|款|桥额|楹联|桥联|字样'
YR = r'(?:[一-龥]{2}(?:元|[一二三四五六七八九十廿卅]{1,3})年|[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]|\d{3,4})'
OUT = []
for c, p in F.items():
    for r in json.load(open(S + '/' + p)):
        y = year(r['era'])
        if not y or y[0] >= 1650: continue
        texts = []
        k = f"{c}|{r['dist']}|{r['town']}|{r['name']}"
        if k in CQ: texts.append(('cq', cqtext(CQ[k])))
        if r.get('sdl'):
            sid = r['sdl'].split('/')[-1].split('_')[0]
            if sid in SDI: texts.append(('singdo', SDI[sid].get('intro', '')))
        hits = []
        for src, t in texts:
            for sent in re.split(r'[。；！]', t):
                if re.search(KW, sent) and re.search(YR, sent): hits.append((src, sent.strip()[:220]))
        OUT.append(dict(key=k, era=r['era'], level=r['level'][:14], n_src=len(texts), hits=hits))
json.dump(OUT, open(S + '/build/inscr_raw.json', 'w'), ensure_ascii=False, indent=1)
print('candidates', len(OUT), 'with sources', sum(1 for o in OUT if o['n_src']), 'with hits', sum(1 for o in OUT if o['hits']))
