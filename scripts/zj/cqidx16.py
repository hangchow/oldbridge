# 抓老百晓集桥江苏各市目录页（ql16），生成 页面->标题 索引。用法：python3 cqidx16.py wx:wxql nj:njql cz:czql zjs:zjql
import re, json, subprocess, sys, os
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for a in sys.argv[1:]:
    k, q = a.split(':'); os.makedirs(f'{S}/cq2/{k}', exist_ok=True)
    h = subprocess.run(['curl', '-sL', '-m', '60', '-A', 'Mozilla/5.0', f'http://www.china-qiao.com/ql16/{q}/{q}.htm'], capture_output=True).stdout.decode('gb18030', 'ignore')
    idx = {}
    for p, t in re.findall(r'href="(' + q + r'\d+\.htm)"[^>]*>(.*?)</a>', h, re.S):
        t = re.sub(r'<[^>]+>|\s|&nbsp;', '', t)
        if t: idx.setdefault(f'ql16/{q}/{p}', t)
    json.dump(idx, open(f'{S}/cq2/{k}/idx.json', 'w'), ensure_ascii=False, indent=0)
    print(k, len(idx), list(idx.items())[:2])
