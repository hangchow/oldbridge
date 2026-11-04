"""应用已核对的公开地图桥梁记录；保留已有等级和冲突来源。"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = '嘉兴市/嘉兴市文物保护网_不可移动文物地图'


def apply(rows):
    reviews = json.loads((ROOT / '文保名录' / ARCHIVE / 'bridge_review.json').read_text())
    for item in reviews:
        if item['status'] not in ('matched', 'new'):
            continue
        target = item['target']
        hits = [r for r in rows if all(r.get(k) == v for k, v in target.items())]
        source = '../../文保名录/' + ARCHIVE + '/' + item['source_file']
        if not hits:
            if item['status'] != 'new':
                continue  # 省级补全后再应用。
            level = '一般不可移动文物（地图档案，未核定为文物保护单位）'
            if item['source_level'] == '5':
                level = '文物保护点（地图档案，公布层级待核）'
            elif item['source_level'] == '3':
                level = target['dist'] + '文物保护单位（地图档案）'
            elif item['source_level'] == '2':
                level = '浙江省文物保护单位（地图档案）'
            r = dict(target, era=item['era'] or '—', loc=item['addr'] or '—', level=level,
                     doc='—', src=source, note='', struct=item['struct'] or '—', len=item['length'] or '—')
            rows.append(r)
        else:
            assert len(hits) == 1, target
            r = hits[0]
        for key, value in [('loc', item['addr']), ('struct', item['struct']), ('len', item['length'])]:
            if value and r.get(key) in ('—', '', None):
                r[key] = value
        r['map_coordinates'] = item['map_coordinates']
        r['map_archive_id'] = item['id']
        r['map_record_status'] = item['status']
        notes = ['[嘉兴文物地图档案](' + source + ')已归档；地图所列名称“' + item['name'] + '”，地址“' + item['addr'] + '”']
        if item['map_coordinates']['valid']:
            xy = item['map_coordinates']
            notes.append('地图原始坐标X=' + xy['x'] + '，Y=' + xy['y'] + '（未作坐标转换）')
        else:
            notes.append('地图坐标缺失或异常，原值保存在结构化档案，不作正常经纬度使用')
        if item['status'] == 'new' and item['source_level'] == '4':
            notes.append('地图“未核定文物保护单位”按一般不可移动文物记录，不计作文保单位或文保点')
        if item['detail_status'] != 'ok':
            notes.append('详情请求返回站点验证或非法访问页面，仅采用公开地图基础字段；结构、长度无正文依据时留空')
        if item.get('location_conflict'):
            notes.append(item['location_conflict'])
        if item['cq']:
            notes.append('已核对老百晓同桥页面及照片')
        elif item['status'] == 'new':
            notes.append(item.get('photo_match_note') or '老百晓目录未找到可靠同桥页面，照片待补')
        for note in notes:
            if note not in (r.get('note') or ''):
                r['note'] = (r.get('note') + '；' if r.get('note') else '') + note
    return rows
