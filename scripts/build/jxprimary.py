# 嘉兴第五批政府公布原件的补正；在市数据生成和省级汇总补全后均应用。
import json
from pathlib import Path
S = Path(__file__).resolve().parent.parent
SOURCE = '嘉兴市/嘉兴市第五批市级文物保护单位及撤销北溪桥名单（2010年3月29日）.html'
NOTE_REVOKED = '2010年3月29日市政府第五批通知明确撤销北溪桥市保；2023年省文物局汇总表仍按嘉政〔1992〕196号列为市保，尚未找到重新公布文件，现行保护身份待核；暂保留省级汇总表所列等级并标明冲突'
def apply(rows):
    data = json.loads((S.parent / '文保名录' / SOURCE.replace('.html', '.json')).read_text())
    names = {'塘汇思贤桥': ('秀洲区', '塘汇街道', '思贤桥'), '栖真麟湖桥': ('秀洲区', '油车港镇', '麟湖桥'), '鉏家桥': ('南湖区', '解放街道', '鉏家桥')}
    for item in data['rows']:
        if item['name'] not in names: continue
        dist, town, name = names[item['name']]
        hits = [r for r in rows if r['dist'] == dist and r['name'] == name]
        if not hits: continue
        assert len(hits) == 1
        r = hits[0]
        r.update(town=town, era=item['era'], loc=item['address'], level='嘉兴市文物保护单位（第五批）', doc=data['doc'], src='../../文保名录/' + SOURCE)
        note = '等级、年代及地址据2010年3月29日市政府第五批通知；文号据2023年省文物局汇总表交叉核对'
        if name == '鉏家桥': note += '；政府通知作民国二十年（1931），老百晓集桥及省级汇总原记1933年，暂按政府公布原件，年代差异待核'
        if name == '思贤桥': note += '；原件名称“塘汇思贤桥”，暂未找到老百晓同桥页面及可靠照片'
        old = r.get('note') or ''
        if note not in old: r['note'] = (old + '；' if old else '') + note
    for r in rows:
        if r['dist'] == '秀洲区' and r['name'] == '北溪桥':
            r['status_conflict'] = True
            r['level'] = '嘉兴市文物保护单位（1992年公布；2010年撤销记载与2023年汇总冲突，现行身份待核）'
            if NOTE_REVOKED not in (r.get('note') or ''): r['note'] = (r.get('note') + '；' if r.get('note') else '') + NOTE_REVOKED
            r['revocation_src'] = '../../文保名录/' + SOURCE
    # 历史建筑身份以公报名单为准；桥梁细节据已核对的同桥资料补充。
    hn2path = S.parent / '文保名录/嘉兴市/海宁市第二批历史建筑名单（海政发〔2019〕38号，公报摘录）.json'
    hn2 = json.loads(hn2path.read_text())
    for name, detail in hn2['bridge_details'].items():
        hits = [r for r in rows if r['dist'] == '海宁市' and r['name'] == name]
        if not hits: continue
        assert len(hits) == 1
        r = hits[0]
        r.update({k: v for k, v in detail.items() if k != 'note'})
        if detail['note'] not in (r.get('note') or ''):
            r['note'] = (r.get('note') + '；' if r.get('note') else '') + detail['note']
    import runpy
    rows = runpy.run_path(str(S / 'build/jxwwbh.py'))['apply'](rows)
    rows = runpy.run_path(str(S / 'build/jxmap.py'))['apply'](rows)
    # 海宁2022汇总表：用户确认的新资料取值及桥梁独立评级口径。
    hn2022 = json.loads((S.parent / '文保名录/嘉兴市/海宁市各级文物保护单位名录2022.json').read_text())
    for name, change in hn2022['adopted_updates'].items():
        hits = [r for r in rows if r['dist'] == '海宁市' and r['name'] == name]
        if not hits:
            if name == '庆成桥': rows.append(dict(change))
            continue
        assert len(hits) == 1
        r = hits[0]
        r.update({k: v for k, v in change.items() if k != 'note'})
        if change['note'] not in (r.get('note') or ''):
            r['note'] = (r.get('note') + '；' if r.get('note') else '') + change['note']
    return rows
