"""完整归档嘉兴文物地图公开接口、详情页和详情图片；可断点续传。"""
import concurrent.futures as cf
import csv
import datetime
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import urllib.parse as up

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / '文保名录/嘉兴市/嘉兴市文物保护网_不可移动文物地图'
BASE = 'https://www.jxwwbh.cn/'
MAP = BASE + 'ConservationWeb/'
for name in ['raw', 'raw/js', 'raw/regions', 'details', 'assets']:
    (DEST / name).mkdir(parents=True, exist_ok=True)


def fetch(url, path, post=None):
    if path.exists() and path.stat().st_size:
        return path.read_bytes()
    temp = path.with_suffix(path.suffix + '.part')
    cmd = ['curl', '-sSL', '--fail', '--retry', '2', '--retry-delay', '1', '--max-time', '40', '-o', str(temp)]
    if post:
        cmd += ['--data', up.urlencode(post)]
    cmd += [up.quote(url.replace('http://www.jxwwbh.cn/', BASE), safe=':/?&=%+#')]
    subprocess.run(cmd, check=True, capture_output=True)
    assert temp.stat().st_size, url
    temp.replace(path)
    return path.read_bytes()


def clean(value):
    value = re.sub(r'<(?:br\b[^>]*|/p|/div|/tr)>', '\n', value, flags=re.I)
    return '\n'.join(s.strip() for s in html.unescape(re.sub('<[^>]+>', '', value)).splitlines() if s.strip())


def field(source, ident):
    match = re.search(r'<(span|label)\b[^>]*\bid="' + ident + r'"[^>]*>(.*?)</\1>', source, re.S | re.I)
    return clean(match.group(2)) if match else ''


fetch(MAP + 'ConservationMap.aspx', DEST / 'raw/ConservationMap.aspx.html')
tree = fetch(MAP + 'wwTree.aspx', DEST / 'raw/wwTree.aspx.html').decode('utf8', 'replace')
for filename in ['config.js', 'MapInforWindow.js', 'Common.js', 'MapOperation.js', 'zTree/zTreeOpe.js']:
    fetch(MAP + 'js/' + filename, DEST / 'raw/js' / filename.replace('/', '_'))
nodes = [dict(zip(['id', 'pid', 'name', 'type'], m.groups())) for m in re.finditer(r"\{\s*'id':'([^']*)',\s*'pId':'([^']*)',\s*'name':'([^']*)','nodeType':'([^']*)'", tree)]
(DEST / 'tree_nodes.json').write_text(json.dumps(nodes, ensure_ascii=False, indent=2) + '\n')
by_node = {n['id']: n for n in nodes}
response = fetch(MAP + 'handler/PostHandler.ashx', DEST / 'raw/getAllwwd.json', {'action': 'getAllwwd'})
records = json.loads(response.decode('utf-8-sig'))['Allwwds']
assert len({r['Bkydwwid'] for r in records}) == len(records)
regions = [n for n in nodes if n['type'] == 'qh' and by_node.get(n['pid'], {}).get('name') == '嘉兴市']
region_by_id = {}
for n in regions:
    data = fetch(MAP + 'handler/PostHandler.ashx', DEST / 'raw/regions' / (n['name'] + '.json'), {'action': 'OnClickTree', 'nodeID': n['id'], 'nodeType': n['type'], 'nodeLevel': '1', 'nodeName': n['name']})
    result = json.loads(data.decode('utf-8-sig'))
    if isinstance(result, list):
        for group in result:
            if isinstance(group, list):
                for item in group:
                    if isinstance(item, dict) and 'Bkydwwid' in item:
                        region_by_id[str(item['Bkydwwid'])] = n['name']
print(f'接口{len(records)}条；目录树{len(nodes)}节点；开始下载全部详情', flush=True)


def download(record):
    ident = str(record['Bkydwwid'])
    url = BASE + 'ShowDetail.aspx?wwid=' + ident
    source = fetch(url, DEST / 'raw' / ('detail_' + ident + '.html')).decode('utf8', 'replace')
    parsed = {key: field(source, key) for key in ['wwmc', 'wwdz', 'wwjb', 'wwlb', 'wwjj', 'bhfw', 'jskzdd']}
    detail_status = 'ok' if parsed['wwmc'] else 'blocked_or_unavailable'
    if not parsed['wwmc']:
        parsed.update(wwmc=record['Bkydwwmc'], wwdz=record['Addr'], wwlb=record['bkwwtype'])
    assets = []
    for tag in re.findall(r'<img\b[^>]*\bid="wwimg"[^>]*>', source, re.I):
        match = re.search(r'\bsrc=["\']([^"\']+)', tag, re.I)
        if not match:
            continue
        remote = up.urljoin(url, html.unescape(match.group(1)))
        extension = Path(up.urlsplit(remote).path).suffix.lower() or '.jpg'
        filename = hashlib.sha256(remote.encode()).hexdigest()[:20] + extension
        data = fetch(remote, DEST / 'assets' / filename)
        assets.append(dict(source_url=remote, local_file='assets/' + filename, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
    title = parsed['wwmc']
    lines = ['<!doctype html><meta charset="utf-8"><title>' + html.escape(title) + '</title>', '<h1>' + html.escape(title) + '</h1>', '<p><a href="' + html.escape(url) + '">原始详情页</a></p>']
    if detail_status != 'ok':
        lines.append('<p>原始详情请求返回站点验证或非法访问页面；以下仅展示已取得的地图基础数据，未取得详情正文。</p>')
    for label, key in [('地址', 'wwdz'), ('来源所列等级', 'wwjb'), ('类别', 'wwlb'), ('简介', 'wwjj'), ('保护范围', 'bhfw'), ('建设控制地带', 'jskzdd')]:
        lines.append('<h2>' + label + '</h2><p>' + html.escape(parsed[key]).replace('\n', '<br>') + '</p>')
    for asset in assets:
        lines.append('<img style="max-width:100%" src="../' + asset['local_file'] + '">')
    if not assets:
        lines.append('<p>原始详情页未提供有效的文物图片src，未用站点页眉或其他图片替代。</p>')
    (DEST / 'details' / (ident + '.html')).write_text('\n'.join(lines) + '\n')
    return dict(record, map_region=region_by_id.get(ident, ''), detail_status=detail_status, detail=parsed, source_url=url, local_file='details/' + ident + '.html', assets=assets, raw_sha256=hashlib.sha256(source.encode()).hexdigest())


results, failures = [], []
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    future = {pool.submit(download, r): r for r in records}
    for i, task in enumerate(cf.as_completed(future), 1):
        try:
            results.append(task.result())
        except Exception as error:
            failures.append(dict(id=future[task]['Bkydwwid'], error=str(error)))
        if i % 100 == 0:
            print(f'{i}/{len(records)} 完成，失败{len(failures)}', flush=True)
results.sort(key=lambda r: int(r['Bkydwwid']))
manifest = dict(source_url=MAP + 'ConservationMap.aspx', fetched_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), endpoint_count=len(records), tree_nodes=len(nodes), detail_count=sum(r['detail_status'] == 'ok' for r in results), unavailable_details=[r['Bkydwwid'] for r in results if r['detail_status'] != 'ok'], failures=failures, coordinate_note='地图JavaScript以wkid:4326构建范围，坐标原样保存；未独立核验底图偏移，不作坐标系转换。', records=results)
(DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
with (DEST / 'catalog.csv').open('w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', '名称', '地图分区', '地址', '来源所列等级', '年代', '类别', 'X', 'Y', '来源', '离线文件'])
    for r in results:
        writer.writerow([r['Bkydwwid'], r['Bkydwwmc'], r['map_region'], r['Addr'], r['detail']['wwjb'], r['Bkydwwniandai'], r['bkwwtype'], r['X'], r['Y'], r['source_url'], r['local_file']])
print(f'已归档{len(results)}基础记录及离线页；图片{sum(len(r["assets"]) for r in results)}；失败{len(failures)}', flush=True)
assert not failures, f'{len(failures)}条记录处理失败，见manifest.json'
assert len(results) == len(records)
