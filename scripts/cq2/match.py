# -*- coding: utf-8 -*-
# 用法: python3 match.py 湖州市 huz  /  python3 match.py 嘉兴市 jx
import json, os, re, subprocess, sys, time
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
city, key = sys.argv[1], sys.argv[2]
ROOT = '/Users/sean/workspace/oldbridge/' + city
R = json.load(open(f'{S}/{key}/rows.json'))
BASE = 'http://www.china-qiao.com/' + ('' if key in ('sh', 'sz', 'wx', 'nj', 'cz', 'zjs', 'yz', 'xz', 'lyg', 'ha', 'yc', 'tzj', 'nt', 'sq') else 'ql15/')
if key == 'sh':
    PY = dict(huangpu88='黄浦区', xuhui88='徐汇区', changning88='长宁区', jingan88='静安区', putuo88='普陀区', hongkou88='虹口区', yangpu88='杨浦区', minhang88='闵行区', baoshan88='宝山区', jiading88='嘉定区', pudong88='浦东新区', jinshan88='金山区', songjiang88='松江区', qingpu88='青浦区', fengxian88='奉贤区', chongming88='崇明区')
    IDX = {p: (PY.get(a, '') + t) for p, (a, t) in json.load(open(f'{S}/cq2/sh/idx.json')).items()}
elif key in ('sz', 'wx', 'nj', 'cz', 'zjs', 'yz', 'xz', 'lyg', 'ha', 'yc', 'tzj', 'nt', 'sq'):
    IDX = json.load(open(f'{S}/cq2/sz/idx.json'))
elif key in ('jh', 'sx', 'nb', 'qz', 'tz', 'wz', 'ls', 'zs', 'wx', 'nj', 'cz', 'zjs', 'yz', 'xz', 'lyg', 'ha', 'yc', 'tzj', 'nt', 'sq'):
    IDX = {'jhql/' + p.split('/')[-1] if False else p: t for p, t in json.load(open(f'{S}/cq2/{key}/idx.json')).items()}
else:
    IDX = json.load(open(f'{S}/cq2/idx.json'))
def load(p): return json.load(open(p)) if os.path.exists(p) else {}
ST, LN, SRC = load(f'{S}/{key}/struct.json'), load(f'{S}/{key}/len.json'), load(f'{S}/{key}/imgsrc.json')
def core(n): return re.sub(r'（.*?）|\(.*?\)|\s|^重建', '', n)
def short(x): return re.sub(r'(新区|街道|镇|乡|区|县|市)$', '', x)
ALLD = sorted({d for cf in json.load(open(S + '/zj/cities.json')).values() for d in cf['dists']} | set('吴兴区 南浔区 德清县 长兴县 安吉县 南湖区 秀洲区 嘉善县 平湖市 海盐县 海宁市 桐乡市 姑苏区 虎丘区 吴中区 相城区 吴江区 常熟市 张家港市 昆山市 太仓市 婺城区 金东区 兰溪市 东阳市 义乌市 永康市 浦江县 武义县 磐安县'.split()))
ODIST = lambda t, d: any(x in t for x in ALLD if x != d and not d.startswith(x[:-1]))   # 标题写了别的区县（如“惠山区”不能配“梁溪区惠山街道”）
def imgbase(r):
    same = [x for x in R if x['dist'] == r['dist'] and core(x['name']) == core(r['name'])]
    return (r['town'] + core(r['name'])) if len(same) > 1 else core(r['name'])
hits = 0
for r in R:
    n = core(r['name'])
    if '、' in n or len(n) < 2: continue
    vill = [v[:-1] for v in re.findall(r'[一-龥]{2,4}?村', r['loc'])]
    ctx = [short(r['town'])] + [v for v in vill if len(v) >= 2]
    if key in ('sz',) + ('jh', 'sx', 'nb', 'qz', 'tz', 'wz', 'ls', 'zs', 'wx', 'nj', 'cz', 'zjs', 'yz', 'xz', 'lyg', 'ha', 'yc', 'tzj', 'nt', 'sq'):
        c = [(p, t) for p, t in IDX.items() if t.endswith(n) and not ODIST(t, r['dist']) and (short(r['dist']) in t or any(x and x != '—' and x in t for x in ctx))]
        if len(c) > 1: c = [x for x in c if any(y and y != '—' and y in x[1] for y in ctx)]
    else:
        c = [(p, t) for p, t in IDX.items() if t.endswith(n) and short(r['dist']) in t and any(x and x in t for x in ctx)]
    if len(c) != 1: continue
    p, t = c[0]; html_path = f'{S}/cq2/' + p.replace('/', '_')
    if not os.path.exists(html_path):
        subprocess.run(['curl', '-sL', '-m', '40', '-A', 'Mozilla/5.0', '-o', html_path, BASE + p]); time.sleep(0.4)
    s = open(html_path, 'rb').read().decode('gb18030', 'ignore')
    text = re.sub(r'(&nbsp;|\s)+', ' ', re.sub(r'<[^>]+>', ' ', s))
    k = f"{r['dist']}|{r['town']}|{r['name']}"
    m = re.search(r'(单孔|双孔|[一二三四五六七八九十]孔|[二三四五六七八]墩[一二三四五六七八九十]孔)?[^，。；\s]{0,3}?(石拱桥|石梁桥|拱桥|梁桥|廊桥)', text)
    if m and k not in ST:
        ST[k] = ('石' if m.group(2) in ('拱桥', '梁桥') else '') + m.group(2) + (f'（{m.group(1)}）' if m.group(1) else '')
    ml = re.search(r'(?:全长|桥长|总长|桥身长)\s*(?:为|约|达)?\s*约?\s*([0-9]+(?:\.[0-9]+)?)\s*米', text) or re.search(r'(?<![湖塘河江溪街路村东西南北中跨宽高径引])长(?:度?为)?\s*约?\s*([0-9]+(?:\.[0-9]+)?)\s*米', text)
    if ml and k not in LN: LN[k] = ml.group(1) + '米'
    folder = os.path.join(ROOT, r['dist']); dst = os.path.join(folder, imgbase(r) + '1.jpg')
    pics = re.findall(r'src="([^"]*pic[^"]*\.jpg)"', s, re.I)
    if pics and not os.path.exists(dst) and os.path.basename(dst) not in ('旗峰桥1.jpg',):   # 人工检查后删掉的图
        u = pics[0] if pics[0].startswith('http') else BASE + os.path.dirname(p) + '/' + pics[0]
        tmp = f'{S}/cq2/img_' + os.path.basename(u)
        subprocess.run(['curl', '-sL', '-m', '40', '-A', 'Mozilla/5.0', '-e', BASE + p, '-o', tmp, u])
        if subprocess.run(['file', '-b', tmp], capture_output=True).stdout.startswith(b'JPEG'):
            subprocess.run(['cp', '-n', tmp, dst]); SRC[f"{r['dist']}/{os.path.basename(dst)}"] = f'[老百晓集桥：{t}]({BASE + p})'; hits += 1
    print('OK', k, '<-', t, ST.get(k, ''), LN.get(k, ''))
json.dump(ST, open(f'{S}/{key}/struct.json', 'w'), ensure_ascii=False, indent=1)
json.dump(LN, open(f'{S}/{key}/len.json', 'w'), ensure_ascii=False, indent=1)
json.dump(SRC, open(f'{S}/{key}/imgsrc.json', 'w'), ensure_ascii=False, indent=1)
print('images', hits, 'struct', len(ST), 'len', len(LN))
