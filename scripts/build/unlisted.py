# -*- coding: utf-8 -*-
# 由各市老百晓目录对比结果生成“不在文保名录的古桥”（尚未定级，待核实）
import json, re
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
O = json.load(open(S + '/build/compare_raw.json'))
LV = '尚未定级（待核实，老百晓集桥收录，不在文保名录中）'
DY = r'(北宋|南宋|宋代?|元代?|明代?|清代?|民国|唐代?)'
RG = {'宋': '建隆 乾德 开宝 太平兴国 雍熙 端拱 淳化 至道 咸平 景德 大中祥符 天禧 乾兴 天圣 明道 景祐 宝元 康定 庆历 皇祐 至和 嘉祐 治平 熙宁 元丰 元祐 绍圣 元符 崇宁 大观 政和 宣和 靖康 建炎 绍兴 隆兴 乾道 淳熙 绍熙 庆元 嘉泰 开禧 嘉定 宝庆 绍定 端平 嘉熙 淳祐 宝祐 开庆 景定 咸淳 德祐',
      '元': '元贞 大德 至大 皇庆 延祐 至治 泰定 致和 天历 至顺 元统 至正',
      '明': '洪武 建文 永乐 洪熙 宣德 正统 景泰 天顺 成化 弘治 正德 嘉靖 隆庆 万历 泰昌 天启 崇祯',
      '清': '顺治 康熙 雍正 乾隆 嘉庆 道光 咸丰 同治 光绪 宣统'}
REIGN = {r: d for d, s in RG.items() for r in s.split()}
core = lambda n: re.sub(r'（.*?）|\(.*?\)|\s|^重建', '', n)
def era_of(h):
    m = re.search(DY + '|(' + '|'.join(REIGN) + ')', h)
    if not m: return '—'
    if m.group(1): return {'宋代': '宋', '元代': '元', '明代': '明', '清代': '清', '唐代': '唐'}.get(m.group(1), m.group(1))
    return REIGN[m.group(2)]
OUT = {}
for city, L in O.items():
    rows = []
    for o in L:
        if o['cand'] or not o['dist']: continue
        town = re.sub('^' + o['dist'], '', o['town'] or '')
        town = re.sub(r'^(县|市|区)', '', town)
        if town and not re.fullmatch(r'.{1,6}(街道|镇|乡)', town): town = ''
        nm = re.sub(r'^[^桥]{0,6}?(?:公园|景区|风景区)', '', re.sub('^' + o['dist'], '', o['name'])).strip()
        if not town:   # 名称里带了乡镇
            m2 = re.match(r'^(.{1,5}?(?:街道|镇|乡))(.+桥)$', re.sub('^' + o['dist'], '', nm))
            if m2: town, nm = m2.group(1), m2.group(2)
        vill = ''
        m3 = re.match(r'^(.{1,4}村)(.{2,}桥)$', nm)
        if m3: vill, nm = m3.group(1), m3.group(2)
        if not nm.endswith('桥') or len(nm) < 2 or len(nm) > 12: continue
        if any(r['dist'] == o['dist'] and core(r['name']) == core(nm) and r['town'] == (town or '—') for r in rows): continue
        rows.append(dict(dist=o['dist'], town=town or '—', name=nm, era=era_of(o['head']), loc=vill or '—', level=LV, doc='—',
                         src='http://www.china-qiao.com/' + o['page'], note='不在文保名录中，据老百晓集桥页面收录，年代按页面开头的记载，待核实'))
    OUT[city] = rows
    print(city, len(rows))
# 逐座人工核对的结果：删除（DROP:原因）或改年代；核对过的说明改为“已逐座核对页面”
import os
DEC = json.load(open(S + '/build/review_decisions.json')) if os.path.exists(S + '/build/review_decisions.json') else {}
for city, rows in OUT.items():
    dd = DEC.get(city, {}); keep = []
    for r in rows:
        v = dd.get(f"{r['dist']}|{r['town']}|{r['name']}", dd.get(f"{r['dist']}|{r['name']}"))
        if v and v.startswith('DROP'): continue
        if v is not None: r['era'] = v
        if city in DEC: r['note'] = '不在文保名录中，据老百晓集桥页面收录；已逐座核对页面，现存桥未见毁弃或1949年后重建的记载；年代按页面' + ('' if v is None or v == '—' else '中本桥的记载') + '，等级待核实'
        if r['name'].startswith('街道') and r['town'].endswith('镇'): r['town'] += '街道'; r['name'] = r['name'][2:]   # “嘉定镇街道宾兴桥”拆分有误
        keep.append(r)
    OUT[city] = keep
json.dump(OUT, open(S + '/build/unlisted.json', 'w'), ensure_ascii=False, indent=0)
# 新增桥的老百晓链接
M = json.load(open(S + '/build/cq_manual2.json'))
for city, rows in OUT.items():
    for r in rows: M[f"{city}|{r['dist']}|{r['town']}|{r['name']}"] = r['src'].split('china-qiao.com/')[1]
json.dump(M, open(S + '/build/cq_manual2.json', 'w'), ensure_ascii=False, indent=0)
