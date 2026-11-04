"""应用已核对的嘉兴市文物保护网档案，仅补缺失字段并保留原名录来源。"""
import json
from pathlib import Path
S = Path(__file__).resolve().parent.parent
ARCHIVES = ['嘉兴市/嘉兴市文物保护网_市级文物保护点', '嘉兴市/嘉兴市文物保护网_市级文物保护单位']

def apply(rows):
    for archive in ARCHIVES:
        reviews = json.loads((S.parent / '文保名录' / archive / 'bridge_review.json').read_text())
        for item in reviews:
            if item['status'] not in ('matched', 'new'):
                continue
            target = item['target']
            hits = [r for r in rows if all(r.get(k) == v for k, v in target.items())]
            source = '../../文保名录/' + archive + '/' + item['local_file']
            if not hits:
                if item['status'] != 'new':
                    # 旧条目部分由后续省级名录补全；等补全后再次应用。
                    continue
                r = dict(target, era=item['era'], loc=item['loc'], level=item['level'], doc=item['doc'], src=source,
                         note=item['note'], struct=item['struct'] or '—', len=item['length'] or '—')
                rows.append(r)
            else:
                assert len(hits) == 1, (item['id'], target)
                r = hits[0]
            for field, value in [('struct', item['struct']), ('len', item['length'])]:
                if value and r.get(field) in ('—', '', None):
                    r[field] = value
            notes = ['[嘉兴市文物保护网官方档案](' + source + ')已保存；缺失的结构、长度据档案补充，原名录等级及现行乡镇写法保留']
            notes += item.get('review_notes', [])
            for note in notes:
                if note not in (r.get('note') or ''):
                    r['note'] = (r.get('note') + '；' if r.get('note') else '') + note
    return rows
