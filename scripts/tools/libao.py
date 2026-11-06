# 云端档案“历史建筑”库（singdo.org/libao/）里的桥梁：详情页转成本地网页，照片和保护图则存入 文保名录/杭州市/云端档案/图片/
# 原始页面在完整镜像的 历史建筑/详情页html/，桥梁清单 scripts/singdo/libao/bridges.json（名称含“桥”、去掉祠堂民居等）
import os, re, json, subprocess, time
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
D = os.path.join(os.path.dirname(S), '文保名录/杭州市/云端档案')
M = os.path.join(os.environ.get('SINGDO_MIRROR_ROOT', os.path.join(os.path.dirname(os.path.dirname(S)), 'singdo_云端档案')), '历史建筑')
MANIFEST = json.load(open(os.path.join(M, '资源清单.json'))) if os.path.exists(os.path.join(M, '资源清单.json')) else {}
import shutil
USED = {str(x['id']) for x in json.load(open(S + '/build/libao.json'))}
B = json.load(open(S + '/singdo/libao/bridges.json'))
def dl(u, p):
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        cached = MANIFEST.get(u.replace('https://', 'http://'), {}).get('path')
        if cached and os.path.isfile(os.path.join(M, cached)):
            shutil.copy2(os.path.join(M, cached), p)
            return True
        subprocess.run(['curl', '-sL', '-m', '90', '-A', 'Mozilla/5.0', '-o', p, u]); time.sleep(0.3)
    return os.path.getsize(p) > 0
for i, r in B.items():
    if i not in USED:
        continue
    n = re.sub(r'[/\\:*?"<>|]', '', r['name'])
    h = open(f'{M}/详情页html/{i}.html', encoding='utf8', errors='ignore').read()
    h = h.replace('src="js/', 'src="assets/js/').replace('<link rel="stylesheet" href="css/phone.css">', '<link rel="stylesheet" href="assets/css/phone.css">\n<link rel="stylesheet" href="assets/css/local.css">')
    h = re.sub(r'<a href="luelan_list\.php\?catid=\d+" class="back">', '<a href="../云端档案_桥梁.md" class="back">', h)
    def ph(m):
        f = f'历保{i}_{m.group(2)}'
        return f'src="图片/{f}"' if dl('http://www.singdo.org/libao/upfile/' + m.group(1) + m.group(2), f'{D}/图片/{f}') else m.group(0)
    h = re.sub(r'src="upfile/(\d+/\d+/\d+/)([^"]+_small\.\w+)"', ph, h)
    big = list(dict.fromkeys(re.findall(r'http://z1\.singdo\.org/libao/upfile/\d+/\d+/\d+/[^"\']+\.(?:jpe?g|png)', h, re.I)))
    imgs = []
    for k, u in enumerate(big, 1):
        loc = f'图片/历保{i}_{n}_{k}{os.path.splitext(u)[1].lower()}'
        if dl(u, f'{D}/{loc}'): h = h.replace(u, loc); imgs.append(loc)
    h = re.sub(r'<script type="text/javascript">\s*var wh = .*?</script>', '<!-- 本地镜像：去掉轮播初始化，照片直接排列 -->', h, flags=re.S)
    h = re.sub(r'<script src="//res\.wx\.qq\.com/open/js/jweixin-1\.0\.0\.js" type="text/javascript"></script>\s*<script type="text/javascript">.*?</script>', '', h, flags=re.S)
    h = h.replace('<script src="js/share.js" type="text/javascript"></script>', '').replace('<script src="assets/js/share.js" type="text/javascript"></script>', '')
    h = h.replace('http://www.singdo.org/libao/images/logo_n.png', 'assets/images/logo_n.png')
    left = re.findall(r'.{30}(?:upfile|singdo\.org).{30}', h)
    if left: print('LEFT', i, left[:2])
    open(f'{D}/历保{i}_{n}.html', 'w', encoding='utf8').write(h)
    r['local'] = f'云端档案/历保{i}_{n}.html'; r['bigimgs'] = imgs
json.dump(B, open(S + '/singdo/libao/bridges.json', 'w'), ensure_ascii=False, indent=1)
print('pages', len(B))
