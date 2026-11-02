# 抓老百晓集桥浙江各市目录页，生成 页面->标题 索引
import re, json, subprocess, sys, time, os
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
for k in sys.argv[1:]:
    idx = {}; os.makedirs(f'{S}/cq2/{k}', exist_ok=True)
    for i in [''] + [str(n) for n in range(1, 40)]:
        u = f'http://www.china-qiao.com/ql15/{k}ql/zjql_{k}{i}.htm'
        h = subprocess.run(['curl', '-sL', '-m', '30', '-A', 'Mozilla/5.0', u], capture_output=True).stdout.decode('gb18030', 'ignore')
        time.sleep(0.3)
        if '404' in h[:300] or 'Not Found' in h[:400]:
            if i: break
            continue
        for p, t in re.findall(r'href="(' + k + r'ql\d+\.htm)"[^>]*>(.*?)</a>', h, re.S):
            t = re.sub(r'<[^>]+>|\s|&nbsp;', '', t)
            if t: idx.setdefault(f'{k}ql/{p}', t)
    json.dump(idx, open(f'{S}/cq2/{k}/idx.json', 'w'), ensure_ascii=False, indent=0)
    print(k, len(idx), list(idx.items())[:2])
