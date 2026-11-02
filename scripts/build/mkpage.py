# 把云端档案详情页转成本地网页（与已存页面同样的处理）
import os
import json, re, shutil, sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
M = '/Users/sean/workspace/singdo_云端档案'
D = '/Users/sean/workspace/oldbridge/文保名录/杭州市/云端档案'
R = json.load(open(S + '/singdo/recs.json')); R = R.values() if isinstance(R, dict) else R
for i in sys.argv[1:]:
    r = next(x for x in R if isinstance(x, dict) and x['id'] == i)
    n = r['name']; h = open(f'{S}/singdo/disp/{i}.html', encoding='utf8').read()
    h = h.replace('src="js/', 'src="assets/js/').replace('<link rel="stylesheet" href="css/phone.css?t=2">', '<link rel="stylesheet" href="assets/css/phone.css">\n<link rel="stylesheet" href="assets/css/local.css">')
    h = re.sub(r'<a href="luelan_list\.php\?catid=\d+" class="back">', '<a href="../云端档案_桥梁.md" class="back">', h)
    def ph(m):
        f = f'{i}_{m.group(1)}'; shutil.copy(f'{M}/照片/{f}', f'{D}/图片/{f}'); return f'src="图片/{f}"'
    h = re.sub(r'src="upfile/\d+/\d+/\d+/([^"]+_small\.\w+)"', ph, h)
    for k, f in enumerate(r['imgs'], 1):
        u = re.escape('http://z1.singdo.org/wenbao/upfile/') + r'\d+/\d+/\d+/' + re.escape(f.split('_', 1)[1])
        loc = f'图片/{i}_{n}_保护范围图{k}.jpg'
        shutil.copy(f'{M}/保护范围图_jpg/{i}_{n}_{k}.jpg', f'{D}/{loc}')
        h = re.sub(u, loc, h)
    h = re.sub(r'<script type="text/javascript">\s*var wh = .*?</script>', '<!-- 本地镜像：去掉轮播初始化，照片直接排列 -->', h, flags=re.S)
    h = h.replace('<script src="http://res.wx.qq.com/open/js/jweixin-1.0.0.js" type="text/javascript"></script>', '')
    h = h.replace('http://www.singdo.org/wenbao/images/logo_n.png', 'assets/images/logo_n.png').replace('<script src="assets/js/share.js" type="text/javascript"></script>', '')
    assert 'upfile' not in h, re.findall(r'.{40}upfile.{40}', h)[:3]
    open(f'{D}/{i}_{n}.html', 'w', encoding='utf8').write(h); print('ok', i, n)
