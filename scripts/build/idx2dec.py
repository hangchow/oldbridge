# 把按编号记录的核对结果转成“区县|乡镇|桥名”键
import os
import json, sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
city, key = sys.argv[1], sys.argv[2]
X = json.load(open(f'{S}/build/review_idx_{key}.json')); R = json.load(open(f'{S}/build/review_{key}.json'))[city]
d = {}
for x in R:
    i = x['i']; k = f"{x['d']}|{x['t']}|{x['n']}"
    if i in X.get('D_modern', []): d[k] = 'DROP:现代桥（页面无古代年代记载）'
    elif str(i) in X.get('D_other', {}): d[k] = 'DROP:' + X['D_other'][str(i)]
    elif str(i) in X.get('E', {}): d[k] = X['E'][str(i)]
    else: print('UNDECIDED', i, k)
D = json.load(open(S + '/build/review_decisions.json')); D[city] = d
json.dump(D, open(S + '/build/review_decisions.json', 'w'), ensure_ascii=False, indent=1)
print(city, len(d), sum(1 for v in d.values() if v.startswith('DROP')))
