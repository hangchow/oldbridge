# -*- coding: utf-8 -*-
# 为“不在名录的古桥”逐座生成核对摘要：建造年代句、可疑迹象、与名录同名的桥
import json, re, os, sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
U = json.load(open(S + '/build/unlisted.json'))
F = {'湖州市': 'huz', '嘉兴市': 'jx', '上海市': 'sh', '苏州市': 'sz', '金华市': 'jh', '绍兴市': 'sx', '宁波市': 'nb', '衢州市': 'qz', '台州市': 'tz', '温州市': 'wz', '丽水市': 'ls', '舟山市': 'zs', '无锡市': 'wx', '南京市': 'nj', '常州市': 'cz', '镇江市': 'zjs', '扬州市': 'yz', '徐州市': 'xz', '连云港市': 'lyg', '淮安市': 'ha', '盐城市': 'yc', '泰州市': 'tzj', '南通市': 'nt', '宿迁市': 'sq'}
core = lambda n: re.sub(r'（.*?）|\(.*?\)|\s|^重建', '', n)
FLAG = re.compile(r'遗址|已毁|被毁|毁于|不存|消失|拆除|已拆|复建|重建于(19[5-9]\d|20\d\d)|(19[5-9]\d|20[0-2]\d)年[^，。]{0,8}(重建|新建|改建|建成|移建|迁建)|仿古|新建|水泥|混凝土|钢筋|公园内|景区内|移至|迁至|搬迁')
BUILD = re.compile(r'[^。；]{0,40}(始建|建于|建造|重建|重修|创建|修建|建成|年代|始于|落成)[^。；]{0,40}')
def text(u):
    p = u.split('china-qiao.com/')[1]
    for f in [S + '/cqv/' + p.replace('/', '_'), S + '/cq2/' + p.replace('/', '_')]:
        if os.path.exists(f) and os.path.getsize(f) > 0:
            t = re.sub(r'\s+', ' ', re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]+>', ' ', open(f, 'rb').read().decode('gb18030', 'ignore'))))
            i = t.find('篇 ')
            if i < 0: i = t.find('桥梁 ')
            return (t[i + 2:] if i >= 0 else t).split('上一座')[0]
    return ''
out = {}
for city in sys.argv[1:]:
    rows = json.load(open(f"{S}/{F[city]}/rows.json"))
    listed = [r for r in rows if not r['level'].startswith('尚未定级')]
    L = []
    for i, u in enumerate(U[city]):
        t = text(u['src'])
        b = BUILD.search(t); fl = sorted(set(m.group(0)[:10] for m in FLAG.finditer(t)))
        dup = [f"{r['town']}{r['name']}" for r in listed if r['dist'] == u['dist'] and (core(r['name']) == core(u['name']) or (len(core(u['name'])) >= 3 and core(u['name']) in core(r['name'])))]
        L.append(dict(i=i, d=u['dist'], t=u['town'], n=u['name'], era=u['era'], b=(b.group(0).strip() if b else t[:80]), f=fl, dup=dup))
    out[city] = L
    for x in L:
        print(f"{x['i']}|{x['d'][:3]}|{x['t'][:4]}|{x['n']}|{x['era']}|{x['b'][:70]}|{','.join(x['f'])}|{'DUP:' + ';'.join(x['dup']) if x['dup'] else ''}")
json.dump(out, open(S + '/build/review_' + '_'.join(F[c] for c in sys.argv[1:]) + '.json', 'w'), ensure_ascii=False, indent=0)
