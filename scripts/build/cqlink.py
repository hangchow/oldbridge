# -*- coding: utf-8 -*-
# 生成 老百晓集桥 链接表：城市|区县|乡镇|桥名 -> 网页地址（匹配规则与 dl_cq.py / cq2/match.py 相同，唯一匹配才采用）
import os
import json, re, collections
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
OUT = {}
# 杭州
IDX = json.load(open(S + '/build/cq_index.json'))
OLD = {'临安区': ['临安区', '临安市'], '富阳区': ['富阳区', '富阳市'], '临平区': ['临平区', '余杭区'], '钱塘区': ['钱塘区', '钱塘新区'],
       '上城区': ['上城区', '江干区'], '拱墅区': ['拱墅区', '下城区']}
core = lambda n: re.sub(r'（.*?）|\(.*?\)', '', n).strip()
for r in json.load(open(S + '/build/all_rows.json')):
    nm = core(r['name'])
    if '、' in nm or '六桥' in nm or len(nm) < 2: continue
    ds = OLD.get(r['dist'], [r['dist']]); tw = re.sub(r'(街道|镇|乡)$', '', r['town'])
    c = [it for it in IDX if (it['title'] + ' ' + it['alias']).endswith(nm) or nm in it['title']]
    TD = lambda it: re.sub('|'.join(sum(OLD.values(), []) + ['滨江区', '萧山区', '富阳', '临安', '建德', '桐庐', '淳安']), '', it['title'] + ' ' + it['alias'])   # 去掉区县名再比乡镇（“余杭街道”的“余杭”不能匹配“余杭区”）
    c = [it for it in c if any(d in it['title'] + ' ' + it['alias'] for d in ds) and tw in TD(it)]
    if len(c) == 1: OUT[f"杭州市|{r['dist']}|{r['town']}|{r['name']}"] = 'http://www.china-qiao.com/ql15/hz_ql/' + c[0]['page']
# 杭州补充：页面标题不写乡镇的（如“中河之桥——六部桥”“杭州市苏堤映波桥”），
# 桥名在杭州项目里唯一、在目录里去掉前缀后也唯一，才链接
def hshort(t):
    t = re.sub(r'^.*?——', '', t.split(' ')[0]); t = re.sub(r'^杭州市', '', t)
    t = re.sub(r'^(西湖|白堤|苏堤|杨公堤|赵公堤|湘堤|越堤|湘湖|花港观鱼|柳浪闻莺)', '', t)
    t = re.sub(r'^.{1,4}?(区|县|市)', '', t); t = re.sub(r'^.{1,5}?(街道|镇|乡)', '', t)
    return t
HR = json.load(open(S + '/build/all_rows.json'))
from collections import Counter
nc = Counter(core(r['name']) for r in HR)
ic = Counter(hshort(it['title']) for it in IDX)
for r in HR:
    k = f"杭州市|{r['dist']}|{r['town']}|{r['name']}"; n = core(r['name'])
    if k in OUT or nc[n] != 1 or ic[n] != 1 or len(n) < 3: continue
    it = next(it for it in IDX if hshort(it['title']) == n)
    ds = [d for d in ['上城区', '拱墅区', '西湖区', '滨江区', '萧山区', '余杭区', '临平区', '钱塘区', '富阳', '临安', '建德', '桐庐', '淳安', '江干区', '下城区'] if d in it['title']]
    okd = OLD.get(r['dist'], [r['dist']]) + [r['dist'][:2]]
    if ds and not any(any(d.startswith(o[:2]) for o in okd) for d in ds): continue
    if not ds and r['dist'] not in ('上城区', '拱墅区', '西湖区', '滨江区'): continue   # 标题不写区县的，只认市区
    if re.search(r'(街道|镇|乡)', it['title']) and re.sub(r'(街道|镇|乡)$', '', r['town']) not in it['title']: continue
    OUT[k] = 'http://www.china-qiao.com/ql15/hz_ql/' + it['page']
# 其余城市
core2 = lambda n: re.sub(r'（.*?）|\(.*?\)|\s|^重建', '', n)
short = lambda x: re.sub(r'(新区|街道|镇|乡|区|县|市)$', '', x)
ALLD = sorted({d for cf in json.load(open(S + '/zj/cities.json')).values() for d in cf['dists']} | set('吴兴区 南浔区 德清县 长兴县 安吉县 南湖区 秀洲区 嘉善县 平湖市 海盐县 海宁市 桐乡市 姑苏区 虎丘区 吴中区 相城区 吴江区 常熟市 张家港市 昆山市 太仓市 婺城区 金东区 兰溪市 东阳市 义乌市 永康市 浦江县 武义县 磐安县'.split()))
ODIST = lambda t, d: any(x in t for x in ALLD if x != d and not d.startswith(x[:-1]))   # 标题写了别的区县（如“惠山区”不能配“梁溪区惠山街道”）
# 标题只写市名的页面一般是市中心城区的桥
CORE = {'南京市': ('秦淮区', '玄武区', '鼓楼区', '建邺区'), '苏州市': ('姑苏区',), '无锡市': ('梁溪区', '滨湖区'), '常州市': ('天宁区', '钟楼区'),
        '镇江市': ('京口区', '润州区'), '宁波市': ('海曙区', '江北区', '鄞州区'), '湖州市': ('吴兴区',), '嘉兴市': ('南湖区', '秀洲区'),
        '绍兴市': ('越城区',), '金华市': ('婺城区', '金东区'), '衢州市': ('柯城区', '衢江区'), '台州市': ('椒江区', '黄岩区', '路桥区'),
        '温州市': ('鹿城区', '龙湾区', '瓯海区'), '丽水市': ('莲都区',), '舟山市': ('定海区', '普陀区'), '上海市': ('黄浦区', '静安区', '虹口区', '徐汇区')}
for city, key in [('湖州市', 'huz'), ('嘉兴市', 'jx'), ('上海市', 'sh'), ('苏州市', 'sz'), ('金华市', 'jh'), ('绍兴市', 'sx'), ('宁波市', 'nb'), ('衢州市', 'qz'), ('台州市', 'tz'), ('温州市', 'wz'), ('丽水市', 'ls'), ('舟山市', 'zs'), ('无锡市', 'wx'), ('南京市', 'nj'), ('常州市', 'cz'), ('镇江市', 'zjs')]:
    BASE = 'http://www.china-qiao.com/' + ('' if key in ('sh', 'sz', 'wx', 'nj', 'cz', 'zjs') else 'ql15/')
    if key == 'sh':
        PY = dict(huangpu88='黄浦区', xuhui88='徐汇区', changning88='长宁区', jingan88='静安区', putuo88='普陀区', hongkou88='虹口区', yangpu88='杨浦区', minhang88='闵行区', baoshan88='宝山区', jiading88='嘉定区', pudong88='浦东新区', jinshan88='金山区', songjiang88='松江区', qingpu88='青浦区', fengxian88='奉贤区', chongming88='崇明区')
        I = {p: (PY.get(a, '') + t) for p, (a, t) in json.load(open(f'{S}/cq2/sh/idx.json')).items()}
    elif key in ('sz', 'wx', 'nj', 'cz', 'zjs'): I = json.load(open(f'{S}/cq2/{key}/idx.json'))
    elif key in ('jh', 'sx', 'nb', 'qz', 'tz', 'wz', 'ls', 'zs', 'wx', 'nj', 'cz', 'zjs'): I = json.load(open(f'{S}/cq2/{key}/idx.json'))
    else: I = json.load(open(f'{S}/cq2/idx.json'))
    RS = json.load(open(f'{S}/{key}/rows.json')); NC = collections.Counter(core2(x['name']) for x in RS); ND = collections.Counter((x['dist'], core2(x['name'])) for x in RS)
    for r in RS:
        n = core2(r['name'])
        if '、' in n or len(n) < 2: continue
        vill = [v[:-1] for v in re.findall(r'[一-龥]{2,4}?村', r['loc'] or '')]
        ctx = [short(r['town'])] + [v for v in vill if len(v) >= 2]
        if key in ('sz',) + ('jh', 'sx', 'nb', 'qz', 'tz', 'wz', 'ls', 'zs', 'wx', 'nj', 'cz', 'zjs'):
            c = [(p, t) for p, t in I.items() if t.endswith(n) and not ODIST(t, r['dist']) and (short(r['dist']) in t or any(x and x != '—' and x in t for x in ctx))]
            if len(c) > 1 or ND[(r['dist'], n)] > 1: c = [x for x in c if any(y and y != '—' and y in x[1] for y in ctx)]   # 本区县同名桥不止一座时要求乡镇对上
        else:
            c = [(p, t) for p, t in I.items() if t.endswith(n) and short(r['dist']) in t and any(x and x in t for x in ctx)]
        if not c and NC[n] == 1 and r['dist'] in CORE.get(city, ()):   # 标题只写市名（如“南京市七桥瓮”）：桥名在本市名录唯一、目录里也唯一才认
            c = [(p, t) for p, t in I.items() if re.sub(r'^.*?——', '', t) in (city + n, city[:-1] + n)]
        if len(c) == 1: OUT[f"{city}|{r['dist']}|{r['town']}|{r['name']}"] = BASE + c[0][0]
# 国保、省保逐座人工核对过的页面（名称或乡镇写法不同，自动匹配不到）
B = 'http://www.china-qiao.com/'
MANUAL = {
 '杭州市|上城区|南星街道|海月桥': 'ql15/hz_ql/hzvql064.htm', '杭州市|西湖区|北山街道|断桥': 'ql15/hz_ql/hzvql093.htm', '杭州市|西湖区|留下街道|古庆春桥': 'ql15/hz_ql/hzvql235.htm', '杭州市|萧山区|城厢街道|永兴桥': 'ql15/hz_ql/hzvql245.htm', '杭州市|萧山区|城厢街道|仓桥': 'ql15/hz_ql/hzvql247.htm', '杭州市|萧山区|城厢街道|惠济桥': 'ql15/hz_ql/hzvql249.htm', '杭州市|萧山区|城厢街道|回澜桥（迴澜桥）': 'ql15/hz_ql/hzvql251.htm', '杭州市|萧山区|新塘街道|霞江村百岁桥': 'ql15/hz_ql/hzvql521.htm', '杭州市|萧山区|新塘街道|戴家桥及螺峰亭': 'ql15/hz_ql/hzvql675.htm', '杭州市|临安区|太湖源镇|太湖源青云桥': 'ql15/hz_ql/hzvql590.htm', '杭州市|临安区|昌化镇|联盟久安桥': 'ql15/hz_ql/hzvql353.htm', '杭州市|临安区|天目山镇|天目山桂芳桥': 'ql15/hz_ql/hzvql358.htm', '杭州市|临安区|龙岗镇|龙岗长乐桥': 'ql15/hz_ql/hzvql360.htm', '杭州市|临平区|东湖街道|竹节关桥': 'ql15/hz_ql/hzvql299.htm', '杭州市|临安区|清凉峰镇|清凉峰永安桥': 'ql15/hz_ql/hzvql580.htm', '杭州市|临安区|於潜镇|南山长安桥': 'ql15/hz_ql/hzvql405.htm', '杭州市|富阳区|鹿山街道|汤家埠万龄桥': 'ql15/hz_ql/hzvql320.htm', '杭州市|临平区|塘栖镇|塘栖村万安桥': 'ql15/hz_ql/hzvql399.htm', '杭州市|临平区|东湖街道|永安桥': 'ql15/hz_ql/hzvql297.htm', '杭州市|临平区|崇贤街道|万年桥': 'ql15/hz_ql/hzvql396.htm', '杭州市|萧山区|城厢街道|市心桥': 'ql15/hz_ql/hzvql246.htm', '杭州市|萧山区|楼塔镇|洲口桥': 'ql15/hz_ql/hzvql271.htm', '杭州市|富阳区|新登镇|湘河湘溪廊桥': 'ql15/hz_ql/hzvql322.htm', 

 '杭州市|西湖区|西湖街道|钱塘江大桥': 'ql15/hz_ql/hzvql001.htm', '杭州市|滨江区|浦沿街道|钱塘江大桥': 'ql15/hz_ql/hzvql001.htm',
 '杭州市|拱墅区|拱宸桥街道|拱宸桥': 'ql15/hz_ql/hzvql026.htm', '杭州市|拱墅区|石桥街道|欢喜永宁桥': 'ql15/hz_ql/hzvql211.htm',
 '湖州市|吴兴区|龙泉街道|潘公桥': 'ql15/hzql/hzql039.htm', '湖州市|吴兴区|朝阳街道|潮音桥': 'ql15/hzql/hzql038.htm',
 '湖州市|吴兴区|朝阳街道|永安桥': 'ql15/hzql/hzql042.htm', '湖州市|南浔区|双林镇|永安桥': 'ql15/hzql/hzql096.htm',
 '湖州市|德清县|阜溪街道|兼济桥': 'ql15/hzql/hzql561.htm', '湖州市|德清县|阜溪街道|社桥': 'ql15/hzql/hzql241.htm',
 '湖州市|德清县|阜溪街道|追远桥': 'ql15/hzql/hzql562.htm', '湖州市|德清县|舞阳街道|万安桥': 'ql15/hzql/hzql565.htm',
 '湖州市|安吉县|梅溪镇|万埭桥': 'ql15/hzql/hzql375.htm',
 '嘉兴市|南湖区|—|三步两爿桥': 'ql15/jxql/jxql039.htm', '嘉兴市|南湖区|—|塔塘桥': 'ql15/jxql/jxql040.htm',
 '嘉兴市|秀洲区|—|鱼池汇桥': 'ql15/jxql/jxql345.htm', '嘉兴市|平湖市|—|马厩庙大桥': 'ql15/jxql/jxql107.htm',
 '上海市|静安区|北站街道|浙江路桥': 'ql02/shql020.htm', '上海市|松江区|永丰街道|大仓桥': 'ql02/shql257.htm', '上海市|松江区|中山街道|望仙桥': 'ql02/shql263.htm',
 '苏州市|吴中区|长桥街道|宝带桥': 'ql16/szql/szql586.htm', '苏州市|吴江区|松陵街道|垂虹断桥': 'ql16/szql/szql362.htm',
 '苏州市|姑苏区|双塔街道|灭渡桥': 'ql16/szql/szql587.htm', '苏州市|姑苏区|双塔街道|吴门桥': 'ql16/szql/szql111.htm',
 '苏州市|虎丘区|横塘街道|行春桥': 'ql16/szql/szql589.htm', '苏州市|姑苏区|虎丘街道|普济桥': 'ql16/szql/szql051.htm',
 '苏州市|苏州工业园区|斜塘街道|斜塘土地庙及永安桥': 'ql16/szql/szql599.htm',
 '苏州市|昆山市|周庄镇|世德桥': 'ql16/szql/szql503.htm', '苏州市|昆山市|周庄镇|永安桥': 'ql16/szql/szql503.htm',
 '苏州市|吴江区|八都镇|香花桥': 'ql16/szql/szql650.htm',
 '苏州市|昆山市|花桥镇|聚福桥': 'ql16/szql/szql502.htm', '苏州市|昆山市|花桥镇|永清桥': 'ql16/szql/szql895.htm', '苏州市|昆山市|花桥镇|万寿桥': 'ql16/szql/szql894.htm',
 '金华市|婺城区|—|金华通济桥': 'ql15/jhql/jhql001.htm', '金华市|磐安县|—|宅口承志桥': 'ql15/jhql/jhql135.htm'}
for k, v in MANUAL.items(): OUT[k] = B + v
# 对比各市目录后人工确认的同桥
for k, v in json.load(open(S + '/build/cq_manual2.json')).items(): OUT[k] = B + v
json.dump(OUT, open(S + '/build/cqlinks.json', 'w'), ensure_ascii=False, indent=0)
import collections; print(collections.Counter(k.split('|')[0] for k in OUT))
