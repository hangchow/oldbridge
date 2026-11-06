"""完整归档杭州文保单位、历史建筑库；支持续传，生成离线网页和资源核对清单。"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import time
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
MIRROR = Path(os.environ.get('SINGDO_MIRROR_ROOT', ROOT.parent / 'singdo_云端档案'))
LIBRARIES = {'wenbao': '文保单位', 'libao': '历史建筑'}
CACHE = ROOT / '文保名录/杭州市/云端档案'
URLS = re.compile(r'''(?:src|href)\s*=\s*["']([^"']+)["']''', re.I)
BIG = re.compile(r'''https?://[^\s"'<>]+/upfile/[^\s"'<>]+''')

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')

def organize():
    """保留原始文件名；先复制项目缓存，再清理项目中的非高频资料。"""
    target = MIRROR / '文保单位'
    target.mkdir(parents=True, exist_ok=True)
    for name in ['cats.json', 'luelan.html', 'recs.json', '保护范围图_jpg',
                 '保护范围图_原图png', '列表页html', '照片', '索引.md', '详情页html']:
        source = MIRROR / name
        if source.exists():
            if (target / name).exists():
                raise RuntimeError(f'迁移目标已存在：{target / name}')
            shutil.move(str(source), str(target / name))
    for kind, label in LIBRARIES.items():
        dest = MIRROR / label
        for folder in ['详情页html', '列表页html', '离线网页', '资源', '项目缓存/图片']:
            (dest / folder).mkdir(parents=True, exist_ok=True)
        for page in CACHE.glob('*.html'):
            if page.name.startswith('历保') != (kind == 'libao'):
                continue
            shutil.copy2(page, dest / '项目缓存' / page.name)
            for ref in URLS.findall(page.read_text()):
                source = (page.parent / unquote(ref)).resolve()
                if source.is_file() and CACHE.resolve() in source.parents:
                    local = source.relative_to(CACHE.resolve())
                    out = dest / '项目缓存' / local
                    out.parent.mkdir(parents=True, exist_ok=True)
                    if not out.exists():
                        shutil.copy2(source, out)
        if kind == 'libao':
            old = ROOT / 'scripts/singdo/libao'
            for page in (old / 'disp').glob('*.html'):
                out = dest / '详情页html' / page.name
                if not out.exists():
                    shutil.copy2(page, out)
            for name in ['index.tsv', 'bridges.json']:
                shutil.copy2(old / name, dest / name)
    # 原始详情页已经核对复制，避免仓库重复保存。
    old = ROOT / 'scripts/singdo/libao/disp'
    for page in old.glob('*.html'):
        dest = MIRROR / '历史建筑/详情页html' / page.name
        assert hashlib.sha256(page.read_bytes()).digest() == hashlib.sha256(dest.read_bytes()).digest()
        page.unlink()
    if old.exists() and not any(old.iterdir()):
        old.rmdir()
    (MIRROR / 'README.md').write_text(
        '# 杭州云端档案完整镜像\n\n'
        '- [文保单位](文保单位/索引.md)：wenbao 库\n'
        '- [历史建筑](历史建筑/索引.md)：libao 库\n\n'
        '两库分别保存原始详情页、目录页、离线网页、资源及抓取报告。'
        '项目缓存保存从 oldbridge 迁入的已处理桥梁档案，原文件名不变。'
        '完整性以各库的抓取报告.json为准。\n')
    print('两个库目录及现有文件迁移完成。', flush=True)

def prune_cache():
    """仅保留项目页面直接使用的档案及其资源；移除前核对完整镜像副本。"""
    used = set()
    for city in ROOT.iterdir():
        if city.is_dir() and city.name.endswith('市'):
            for page in city.rglob('*.md'):
                used.update(re.findall(r'云端档案/([^/)]+\.html)', page.read_text()))
    kept = [page for page in CACHE.glob('*.html') if page.name in used]
    removed = [page for page in CACHE.glob('*.html') if page.name not in used]
    images = set()
    for page in kept:
        for ref in URLS.findall(page.read_text()):
            if ref.startswith('图片/'):
                images.add(unquote(ref))
    obsolete = [f for f in (CACHE / '图片').iterdir()
                if f.is_file() and str(f.relative_to(CACHE)) not in images]
    # 整批先校验，确保归档存在后才清理缓存。
    for file in removed + obsolete:
        label = '历史建筑' if file.name.startswith('历保') else '文保单位'
        target = MIRROR / label / '项目缓存' / file.relative_to(CACHE)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
        if file.read_bytes() != target.read_bytes():
            raise RuntimeError(f'完整镜像副本不一致：{file}')
    for file in removed + obsolete:
        file.unlink()
    index = ROOT / '文保名录/杭州市/云端档案_桥梁.md'
    text = index.read_text()
    for page in removed:
        text = re.sub(r'\[([^\]]+)\]\(云端档案/' + re.escape(page.name) + r'\)', r'\1', text)
    index.write_text(text)
    report = {'kept_pages': len(kept), 'kept_images': len(images),
              'moved_pages': [p.name for p in removed], 'moved_images': [p.name for p in obsolete]}
    dump(MIRROR / '项目缓存整理报告.json', report)
    print(json.dumps(report, ensure_ascii=False), flush=True)

class Archive:
    def __init__(self, kind, workers):
        self.kind = kind
        self.folder = MIRROR / LIBRARIES[kind]
        self.base = f'http://www.singdo.org/{kind}/'
        self.workers = workers
        self.failures = {}
        self.manifest = {}
        self.alternatives = {}
        for name in ['详情页html', '列表页html', '离线网页', '资源']:
            (self.folder / name).mkdir(parents=True, exist_ok=True)

    def fetch(self, url, path, refresh=False):
        if path.exists() and path.stat().st_size and not refresh:
            return path.read_bytes()
        candidates = [url]
        if '/upfile/' in url:
            host = urlsplit(url).netloc
            alternative = 'www.singdo.org' if host == 'z1.singdo.org' else 'z1.singdo.org'
            candidates.append(url.replace('://' + host + '/', '://' + alternative + '/', 1))
        errors = []
        for candidate in candidates:
            for attempt in range(3):
                try:
                    req = Request(candidate, headers={'User-Agent': 'Mozilla/5.0'})
                    with urlopen(req, timeout=40) as response:
                        data = response.read()
                        if not data:
                            raise ValueError('空响应')
                        if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                            if b'<html' in data[:300].lower() or b'<!doctype' in data[:300].lower():
                                raise ValueError('图片URL返回HTML')
                    path.parent.mkdir(parents=True, exist_ok=True)
                    temp = path.with_name(path.name + '.part')
                    temp.write_bytes(data)
                    temp.replace(path)
                    if candidate != url:
                        self.alternatives[url] = candidate
                    return data
                except Exception as exc:
                    error = str(exc)
                    if '404' in error:
                        break
                    time.sleep(attempt + 1)
            errors.append(candidate + ': ' + error)
        self.failures[url] = '; '.join(errors)
        print('FAILED', url, self.failures[url], flush=True)
        return None

    def normalize(self, ref, base=None):
        url = urljoin(base or self.base, html.unescape(ref))
        parts = urlsplit(url)
        if parts.hostname not in ('www.singdo.org', 'singdo.org', 'z1.singdo.org'):
            return None
        if parts.scheme not in ('http', 'https'):
            return None
        return 'http://' + parts.netloc + parts.path + ('?' + parts.query if parts.query else '')

    def resources(self, source):
        refs = URLS.findall(source) + BIG.findall(source)
        # 仅下载静态文件，跳过其他业务页面和分享脚本服务。
        return set(u for ref in refs if (u := self.normalize(ref)) and
                   re.search(r'\.(?:png|jpe?g|gif|webp|svg|ico|css|js|woff2?|ttf)(?:\?|$)', u, re.I))

    def resource_path(self, url):
        u = urlsplit(url)
        # 不解码斜线，不允许URL逃逸归档目录。
        parts = [x for x in u.path.split('/') if x not in ('', '.', '..')]
        return self.folder / '资源' / u.netloc / Path(*parts)

    def seed(self, url, path):
        if path.exists():
            return
        filename = Path(urlsplit(url).path).name
        project = self.folder / '项目缓存/图片'
        candidates = []
        # 按记录ID映射，避免不同记录的相同图片名误配。
        for rid, rec in self.records.items():
            if url not in rec['resources']:
                continue
            if self.kind == 'wenbao':
                candidates += [self.folder / '照片' / f'{rid}_{filename}',
                               self.folder / '保护范围图_原图png' / f'{rid}_{filename}',
                               project / f'{rid}_{filename}']
            else:
                candidates += [project / f'历保{rid}_{filename}']
                bridge = self.bridges.get(rid, {})
                for i, original in enumerate(bridge.get('imgs', []), 1):
                    if self.normalize(original) == url:
                        candidates += [project / f'历保{rid}_{bridge["name"]}_{i}{Path(filename).suffix.lower()}']
        for candidate in candidates:
            if candidate.is_file() and candidate.stat().st_size:
                path.parent.mkdir(parents=True, exist_ok=True)
                # 硬链接复用原图，完整镜像内无需再占一份空间。
                os.link(candidate, path)
                return

    def run(self):
        home = self.fetch(self.base + 'luelan.php', self.folder / 'luelan.html', refresh=True)
        if home is None:
            raise RuntimeError('无法读取库入口')
        home = home.decode('utf8', 'replace')
        cats = dict(re.findall(r'luelan_list\.php\?catid=(\d+)["\'][^>]*>\s*([^<]+)', home))
        if not cats:
            cats = dict.fromkeys(re.findall(r'luelan_list\.php\?catid=(\d+)', home), '')
        index = {}
        for cat, title in cats.items():
            seen = set()
            for page in range(1, 101):
                url = self.base + f'luelan_list.php?catid={cat}&page={page}'
                data = self.fetch(url, self.folder / '列表页html' / f'{cat}_{page}.html', refresh=True)
                if data is None:
                    break
                source = data.decode('utf8', 'replace')
                # 限定在名录正文内，避免导航栏造成分类和完整性误判。
                section = source.split('class="luelan_list"', 1)[-1].split('class="main_footer"', 1)[0]
                entries = re.findall(r'luelan_disp\.php\?luelan_id=(\d+)["\'][^>]*>(.*?)</a>', section, re.S)
                fresh = [(rid, title) for rid, title in entries if rid not in seen]
                for rid, name in fresh:
                    record = index.setdefault(rid, {'id': rid, 'title': html.unescape(re.sub('<[^>]+>', '', name)).strip(), 'cats': []})
                    record['cats'].append(cat)
                    seen.add(rid)
                if not fresh or not re.search(r'(?:[?&]|&amp;)page=\d+', source):
                    break
            print(f'{self.kind} 分类{cat}: {len(seen)} 条，累计 {len(index)} 条', flush=True)
        if not index:
            raise RuntimeError('目录未解析到档案')
        dump(self.folder / 'cats.json', cats)
        dump(self.folder / '目录.json', index)
        self.records = {}
        self.bridges = json.loads((ROOT / 'scripts/singdo/libao/bridges.json').read_text())
        def detail(rid):
            path = self.folder / '详情页html' / f'{rid}.html'
            data = self.fetch(self.base + f'luelan_disp.php?luelan_id={rid}', path)
            if data is None:
                return rid, None
            source = data.decode('utf8', 'replace')
            if 'house_disp' not in source:
                self.failures[self.base + f'luelan_disp.php?luelan_id={rid}'] = '非详情页响应'
                return rid, None
            title = re.search(r'<title>(.*?)</title>', source, re.S)
            text = re.sub(r'(?is)<(script|style).*?</\1>', '', source)
            text = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', text))).strip()
            return rid, {**index[rid], 'url': self.base + f'luelan_disp.php?luelan_id={rid}',
                         'page_title': html.unescape(title[1]) if title else '',
                         'text': text, 'resources': sorted(self.resources(source))}
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            for i, job in enumerate(as_completed([pool.submit(detail, rid) for rid in index]), 1):
                rid, record = job.result()
                if record:
                    self.records[rid] = record
                if i % 100 == 0:
                    print(f'{self.kind} 详情 {i}/{len(index)}', flush=True)
        dump(self.folder / '档案.json', self.records)
        urls = set(self.resources(home))
        for r in self.records.values():
            urls.update(r['resources'])
        pending = urls
        done = set()
        while pending:
            def resource(url):
                path = self.resource_path(url)
                self.seed(url, path)
                data = self.fetch(url, path)
                return url, path, data
            new = set()
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                for i, job in enumerate(as_completed([pool.submit(resource, u) for u in pending]), 1):
                    url, path, data = job.result()
                    done.add(url)
                    if data:
                        self.manifest[url] = {'path': str(path.relative_to(self.folder)), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'fetched_from': self.alternatives.get(url, url)}
                        if path.suffix == '.css':
                            for ref in re.findall(r'url\(["\']?([^\)"\']+)', data.decode('utf8', 'replace')):
                                u = self.normalize(ref, url)
                                if u:
                                    new.add(u)
                    if i % 100 == 0:
                        print(f'{self.kind} 资源 {i}/{len(pending)}，失败 {len(self.failures)}', flush=True)
                        dump(self.folder / '资源清单.json', self.manifest)
            pending = new - done
        dump(self.folder / '资源清单.json', self.manifest)
        self.offline()
        report = {'time': datetime.now().isoformat(), 'library': self.kind, 'categories': len(cats),
                  'listed_records': len(index), 'saved_records': len(self.records),
                  'saved_resources': len(self.manifest), 'failures': self.failures,
                  'complete': len(index) == len(self.records) and not self.failures}
        dump(self.folder / '抓取报告.json', report)
        (self.folder / '索引.md').write_text(
            f'# {LIBRARIES[self.kind]}完整镜像\n\n来源：{self.base}luelan.php\n\n'
            f'目录 {len(index)} 条，详情 {len(self.records)} 条，静态资源 {len(self.manifest)} 份。'
            '缺失及失败见[抓取报告](抓取报告.json)。\n\n'
            '| 记录号 | 名称 | 离线档案 |\n|---|---|---|\n' + ''.join(
                f'| {rid} | {rec["title"]} | [查看](离线网页/{rid}.html) |\n'
                for rid, rec in sorted(self.records.items(), key=lambda v: int(v[0]))))
        print(json.dumps(report, ensure_ascii=False), flush=True)

    def offline(self):
        for rid in self.records:
            source = (self.folder / '详情页html' / f'{rid}.html').read_text()
            def replace(m):
                ref = m[1]
                url = self.normalize(ref)
                if url in self.manifest:
                    return m[0].replace(ref, '../' + self.manifest[url]['path'])
                if 'luelan_list.php?' in ref:
                    return m[0].replace(ref, '../索引.md')
                return m[0]
            source = URLS.sub(replace, source)
            for url, rec in self.manifest.items():
                if url in source:
                    source = source.replace(url, '../' + rec['path'])
            (self.folder / '离线网页' / f'{rid}.html').write_text(source)

def verify():
    result = {}
    for kind, label in LIBRARIES.items():
        folder = MIRROR / label
        report = json.loads((folder / '抓取报告.json').read_text())
        manifest = json.loads((folder / '资源清单.json').read_text())
        records = json.loads((folder / '档案.json').read_text())
        problems = []
        for rid in records:
            for subdir in ['详情页html', '离线网页']:
                if not (folder / subdir / (rid + '.html')).is_file():
                    problems.append(subdir + '/' + rid + '.html')
        for url, meta in manifest.items():
            file = folder / meta['path']
            if not file.is_file():
                problems.append(meta['path'])
            elif hashlib.sha256(file.read_bytes()).hexdigest() != meta['sha256']:
                problems.append('SHA-256不一致：' + meta['path'])
        result[kind] = {'listed_records': report['listed_records'],
                        'saved_records': len(records), 'resources': len(manifest),
                        'source_failures': report['failures'], 'integrity_errors': problems}
    dump(MIRROR / '核验报告.json', result)
    if any(r['integrity_errors'] for r in result.values()):
        raise RuntimeError('镜像核验失败，见核验报告.json')
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


def finish_after(pid):
    """等待已有下载结束，再续传失败项、生成离线档案并验证完整镜像。"""
    folder = MIRROR / '历史建筑'
    records_path = folder / '档案.json'
    records = json.loads(records_path.read_text()) if records_path.exists() else {}
    targets = set(u for r in records.values() for u in r.get('resources', []))
    home = folder / 'luelan.html'
    if home.exists():
        targets.update(Archive('libao', 1).resources(home.read_text()))
    while True:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            break
        dump(MIRROR / '抓取进度.json', {
            'state': 'downloading', 'time': datetime.now().isoformat(),
            'library': 'libao', 'saved_records': len(records),
            'saved_resources': sum(p.is_file() for p in (folder / '资源').rglob('*')),
            'primary_resource_targets': len(targets),
            'final_report': '收尾报告.json',
        })
        time.sleep(20)
    path = MIRROR / '历史建筑/抓取报告.json'
    report = json.loads(path.read_text()) if path.exists() else None
    if not report or not report.get('complete'):
        Archive('libao', 8).run()
    result = verify()
    dump(MIRROR / '抓取进度.json', {'state': 'finished', 'time': datetime.now().isoformat(), 'final_report': '收尾报告.json'})
    dump(MIRROR / '收尾报告.json', {
        'finished': True, 'time': datetime.now().isoformat(),
        'all_resources_available': all(not v['source_failures'] for v in result.values()),
        'libraries': result,
    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='仅核验已抓取详情、离线网页和资源哈希')
    parser.add_argument('--finish-after', type=int, help='等待已有抓取进程结束，再自动重试和核验')
    parser.add_argument('--organize', action='store_true', help='迁移旧镜像及已抓取的项目缓存')
    parser.add_argument('--library', choices=['wenbao', 'libao', 'all'], default='all')
    parser.add_argument('--workers', type=int, default=6)
    parser.add_argument('--prune-cache', action='store_true', help='仅整理项目高频缓存，不访问网络')
    args = parser.parse_args()
    if args.verify:
        verify()
        raise SystemExit(0)
    if args.finish_after:
        finish_after(args.finish_after)
        raise SystemExit(0)
    if args.prune_cache:
        prune_cache()
        raise SystemExit(0)
    if args.organize:
        organize()
    for kind in LIBRARIES if args.library == 'all' else [args.library]:
        Archive(kind, args.workers).run()
