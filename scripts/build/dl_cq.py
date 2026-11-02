# -*- coding: utf-8 -*-
# 从“老百晓集桥”杭州篇按 区/乡镇/桥名 严格匹配，下载桥梁照片并提取结构
import json, os, re, subprocess, time
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT = '/Users/sean/workspace/oldbridge/杭州市'
R = json.load(open(S + '/build/all_rows.json'))
IDX = json.load(open(S + '/build/cq_index.json'))
src = json.load(open(S + '/build/imgsrc.json')) if os.path.exists(S + '/build/imgsrc.json') else {}
LEN = {}
struct_found = json.load(open(S + '/build/cq_struct.json')) if os.path.exists(S + '/build/cq_struct.json') else {}
COUNTIES = ['桐庐县', '淳安县', '建德市']
OLD = {'临安区': ['临安区', '临安市'], '富阳区': ['富阳区', '富阳市'], '临平区': ['临平区', '余杭区'], '钱塘区': ['钱塘区', '钱塘新区'],
       '上城区': ['上城区', '江干区'], '拱墅区': ['拱墅区', '下城区']}
BASE = 'http://www.china-qiao.com/ql15/hz_ql/'
UA = 'Mozilla/5.0 (Macintosh) Chrome/124'
os.makedirs(S + '/img/cq', exist_ok=True)

def folder(r): return os.path.join(ROOT, r['dist']) if r['dist'] in COUNTIES else os.path.join(ROOT, r['dist'], r['town'])
def imgname(n): return re.sub(r'（.*?）|\(.*?\)', '', n).strip() + '.jpg'
def core(n): return re.sub(r'（.*?）|\(.*?\)', '', n).strip()
def short(t): return re.sub(r'(街道|镇|乡)$', '', t)

def fetch(url, out):
    subprocess.run(['curl', '-sL', '-m', '40', '-A', UA, '-e', BASE, '-o', out, url])
    return out

hits = 0
for r in R:
    dst = os.path.join(folder(r), imgname(r['name']))
    nm = core(r['name'])
    if '、' in nm or '六桥' in nm or '古桥' in nm: continue
    dists = OLD.get(r['dist'], [r['dist']])
    cands = []
    for it in IDX:
        t = it['title'] + ' ' + it['alias']
        if not t.endswith(nm) and nm not in it['title']: continue
        if not any(d in t for d in dists): continue
        if short(r['town']) not in t: continue
        cands.append(it)
    if len(cands) != 1: continue
    it = cands[0]
    page = BASE + it['page']
    html_path = S + '/img/cq/' + it['page']
    if not os.path.exists(html_path): fetch(page, html_path); time.sleep(0.5)
    s = open(html_path, 'rb').read().decode('gb18030', 'ignore')
    text = re.sub(r'(&nbsp;|\s)+', ' ', re.sub(r'<[^>]+>', ' ', s))
    m = re.search(r'(单孔|双孔|三孔|四孔|五孔|六孔|七孔|多孔|[一二三四五六七八九]墩[一二三四五六七八九十]孔)?(石拱桥|石梁桥|石板桥|廊桥|拱桥|梁桥)', text)
    if m and r['struct'] in ('—', '', None):
        struct_found[f"{r['dist']}|{r['town']}|{r['name']}"] = ('石' if m.group(2) in ('拱桥', '梁桥') else '') + m.group(2) + (f'（{m.group(1)}）' if m.group(1) else '')
    ml = re.search(r'(?:全长|桥长|总长|长度?为?)\s*([0-9]+(?:\.[0-9]+)?)\s*米', text)
    if ml: LEN[f"{r['dist']}|{r['town']}|{r['name']}"] = ml.group(1) + '米'
    pics = re.findall(r'src="(pic_hz/[^"]+\.jpg)"', s)
    if True: continue
    tmp = S + '/img/cq/' + os.path.basename(pics[0])
    fetch(BASE + pics[0], tmp)
    if 'JPEG' not in subprocess.run(['file', '-b', tmp], capture_output=True, text=True).stdout: continue
    subprocess.run(['cp', '-n', tmp, dst])
    src[os.path.relpath(dst, ROOT)] = f'[老百晓集桥：{it["title"]}]({page})'
    hits += 1
    print('OK', r['dist'], r['town'], r['name'], '<-', it['title'])
json.dump(src, open(S + '/build/imgsrc.json', 'w'), ensure_ascii=False, indent=1)
json.dump(LEN, open(S + '/build/cq_len.json', 'w'), ensure_ascii=False, indent=1)
json.dump(struct_found, open(S + '/build/cq_struct.json', 'w'), ensure_ascii=False, indent=1)
print('hits', hits, 'struct', len(struct_found))
