"""归档嘉兴市文物保护网市保单位及文保点栏目（支持重复运行及断点续传）。"""
import argparse
import concurrent.futures as cf
import csv
import io
import hashlib
import html
import json
from pathlib import Path
import re
import time
import urllib.parse as up
import urllib.request as ur

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description='归档嘉兴市文物保护网栏目')
parser.add_argument('column_id', nargs='?', choices=['117', '120'], default='120')
args = parser.parse_args()
COLUMN_NAME = {'117': '市级文物保护单位', '120': '市级文物保护点'}[args.column_id]
DEST = ROOT / ('文保名录/嘉兴市/嘉兴市文物保护网_' + COLUMN_NAME)
BASE = 'https://www.jxwwbh.cn/'
COLUMN = BASE + 'ArticleList.aspx?ChID=20&ColID=' + args.column_id
for name in ['lists', 'raw', 'articles', 'assets']:
    (DEST / name).mkdir(parents=True, exist_ok=True)

def fetch(url, path):
    if path.exists() and path.stat().st_size > 0:
        return path.read_bytes()
    for attempt in range(3):
        try:
            request_url = url.replace('http://www.jxwwbh.cn/', BASE)
            req = ur.Request(up.quote(request_url, safe=':/?&=%+#'), headers={'User-Agent': 'Mozilla/5.0'})
            with ur.urlopen(req, timeout=35) as response:
                data = response.read()
            if not data or b'<title>403 Forbidden' in data or b'<title>404 Not Found' in data:
                raise ValueError('empty/error response: ' + url)
            tmp = path.with_suffix(path.suffix + '.part')
            tmp.write_bytes(data)
            tmp.replace(path)
            return data
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)

def clean(s):
    s = re.sub(r'<(?:br|/p|/div|/tr)\b[^>]*>', '\n', s, flags=re.I)
    s = html.unescape(re.sub(r'<[^>]+>', '', s))
    return '\n'.join(x.strip() for x in s.splitlines() if x.strip())

def label(s, number):
    m = re.search(r'id="ctl00_ContentPlaceHolder1_Label' + str(number) + r'"[^>]*>(.*?)</span>', s, re.S)
    return clean(m.group(1)) if m else ''

first = fetch(COLUMN, DEST / 'lists/page1.html').decode('utf8', 'replace')
pages = max([1] + [int(x) for x in re.findall(r'page=(\d+)', first)])
m = re.search(r'共(?:&nbsp;|\s)*(\d+)(?:&nbsp;|\s)*条记录', first)
expected = int(m.group(1)) if m else None
entries = {}
for page in range(1, pages + 1):
    s = first if page == 1 else fetch(COLUMN + '&page=' + str(page), DEST / f'lists/page{page}.html').decode('utf8', 'replace')
    for match in re.finditer(r'href="(ArticleShow\.aspx\?ID=(\d+))"[^>]*>(.*?)</a>', s, re.S | re.I):
        link, ident, title = match.groups()
        title = clean(title)
        if ident not in entries:
            entries[ident] = {'id': ident, 'title': title, 'source_url': up.urljoin(BASE, link), 'list_page': page}
assert expected is None or len(entries) == expected, (len(entries), expected)
print(f'栏目 {pages} 页，{len(entries)} 条；开始下载正文及资源', flush=True)

def article(item):
    s = fetch(item['source_url'], DEST / 'raw' / (item['id'] + '.html')).decode('utf8', 'replace')
    marker = 'id="ctl00_ContentPlaceHolder1_Label3"'
    start = s.index('>', s.index(marker)) + 1
    body = s[start:s.index('</td>', start)].rsplit('</span>', 1)[0].strip()
    title = label(s, 2) or item['title']
    item = dict(item, title=title, published=label(s, 5), text=clean(body))
    assets = []
    candidates = re.findall(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', body, re.I)
    for link in dict.fromkeys(candidates):
        remote = up.urljoin(BASE, html.unescape(link.replace('\\', '/')))
        ext = Path(up.unquote(up.urlsplit(remote).path)).suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']:
            continue
        filename = hashlib.sha256(remote.encode()).hexdigest()[:20] + ext
        data = fetch(remote, DEST / 'assets' / filename)
        entry = {'source_url': remote, 'local_file': 'assets/' + filename, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        assets.append(entry)
        body = body.replace(link, '../assets/' + filename)
    item['assets'] = assets
    item['raw_file'] = 'raw/' + item['id'] + '.html'
    item['local_file'] = 'articles/' + item['id'] + '.html'
    offline = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>' + html.escape(title) + '</title><style>body{max-width:1000px;margin:32px auto;padding:0 20px;font:18px/1.8 sans-serif}img{max-width:100%;height:auto!important}p{margin:1em 0}table{max-width:100%}</style><h1>' + html.escape(title) + '</h1><p>嘉兴市文物保护网 · ' + COLUMN_NAME + ' · ' + html.escape(item['published']) + ' · <a href="' + html.escape(item['source_url']) + '">原文</a></p>' + body + '</html>'
    (DEST / item['local_file']).write_text(offline)
    return item

results, errors = [], []
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    futures = {pool.submit(article, item): item for item in entries.values()}
    for future in cf.as_completed(futures):
        try:
            results.append(future.result())
        except Exception as exc:
            errors.append(dict(futures[future], error=str(exc)))
            print('失败：' + futures[future]['title'] + ' ' + str(exc), flush=True)
        if (len(results) + len(errors)) % 20 == 0:
            print(f'已完成 {len(results)}/{len(entries)}，失败 {len(errors)}', flush=True)
results.sort(key=lambda x: list(entries).index(x['id']))
manifest = {'source_url': COLUMN, 'column': COLUMN_NAME, 'pages': pages, 'expected_articles': expected, 'downloaded_articles': len(results), 'articles': results, 'errors': errors}
(DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
# UTF-8 BOM 便于表格软件直接打开；正文仍可在manifest中按字段读取。
csv_buffer = io.StringIO(newline='')
writer = csv.writer(csv_buffer)
writer.writerow(['id', '名称', '发布日期', '原文链接', '本地正文', '图片数', '正文'])
for item in results:
    writer.writerow([item['id'], item['title'], item['published'], item['source_url'], item['local_file'], len(item['assets']), item['text']])
with (DEST / 'catalog.csv').open('w', encoding='utf-8-sig', newline='') as csv_file:
    csv_file.write(csv_buffer.getvalue())

bridges = [a for a in results if a['title'].endswith('桥') and '遗址' not in a['title']]
lines = ['# 嘉兴市文物保护网：' + COLUMN_NAME, '', f'来源：[{COLUMN}]({COLUMN})。栏目共{pages}页、{expected}条记录，已下载{len(results)}条；正文与资源可离线阅读。', '', '保留原始HTML、栏目分页、正文文字、官方照片及附件；资源文件记录原链接和SHA-256。重新运行 `scripts/tools/download_jxwwbh.py {args.column_id}` 可续传。', '', f'## 桥梁档案（{len(bridges)}条，按标题筛选）', '', '| 名称 | 发布日期 | 来源 |', '|---|---|---|']
lines += [f"| [{a['title']}]({a['local_file']}) | {a['published']} | [原文]({a['source_url']}) |" for a in bridges]
lines += ['', '## 全部档案', '', '| 名称 | 发布日期 | 来源 |', '|---|---|---|']
lines += [f"| [{a['title']}]({a['local_file']}) | {a['published']} | [原文]({a['source_url']}) |" for a in results]
if errors:
    lines += ['', '## 下载失败', ''] + [f"- {a['title']}：{a['error']}" for a in errors]

lines += ['', '## 结构化数据', '', '- [全部档案及资源校验清单](manifest.json)', '- [可用表格软件打开的CSV](catalog.csv)']
if (DEST / 'bridge_review.json').exists():
    lines += ['- [桥梁对应与待核记录](bridge_review.json)：重复档案保留原件；疑似同桥单列待核。']
if (DEST / 'import_summary.json').exists():
    imp = json.loads((DEST / 'import_summary.json').read_text())
    lines += ['- [本地名录导入结果](import_summary.json)', '', f"导入核对：{imp['matched']}条对应已有桥梁，新增{imp['new']}座，重复档案{imp['duplicate']}条，待核{imp['needs_review']}条。为原来缺图的桥梁补入{len(imp['copied_photos'])}张官方照片。"]

    conflicts = imp.get('source_conflicts', [])
    if conflicts:
        lines += ['', '## 来源差异待核', '', '以下条目已确认对应关系，年代、长度、地名或保护身份的来源差异另行保留，不视为新增桥梁。', '']
        for conflict in conflicts:
            lines.append('- ' + conflict['title'] + '：' + '；'.join(conflict['notes']) + '。')
(DEST / 'README.md').write_text('\n'.join(lines) + '\n')
print(f'完成：{len(results)}条，桥梁标题{len(bridges)}条，资源{sum(len(a["assets"]) for a in results)}份，失败{len(errors)}', flush=True)
if errors:
    raise SystemExit(1)
