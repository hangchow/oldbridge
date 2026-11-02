import os
import re,json,html
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
towns=json.load(open(S+'/hz/towns.json'))
def find_town(addr,dist=None):
    cands=[]
    for d,ts in towns.items():
        if dist and d!=dist: continue
        for t in ts:
            short=re.sub(r'(街道|镇|乡)$','',t)
            if t in addr or (len(short)>=2 and short+'街道' in addr) or (len(short)>=2 and re.search(re.escape(short)+'(镇|乡|街道)',addr)):
                cands.append((d,t))
    return list(dict.fromkeys(cands))
B=[]
# ---- 文保点 xlsx
ss=open(S+'/x/xl/sharedStrings.xml',encoding='utf8').read()
strs=[''.join(re.findall(r'<t[^>]*>(.*?)</t>',s,re.S)) for s in re.findall(r'<si>(.*?)</si>',ss,re.S)]
x=open(S+'/x/xl/worksheets/sheet2.xml',encoding='utf8').read()
cur=''
for r in re.findall(r'<row[^>]*>(.*?)</row>',x,re.S)[2:]:
    vals=[]
    for attr,inner in re.findall(r'<c ([^>]*?)(?:/>|>(.*?)</c>)',r,re.S):
        v=re.search(r'<v>(.*?)</v>',inner or '')
        vals.append('' if not v else html.unescape(strs[int(v.group(1))] if 't="s"' in attr else v.group(1)))
    while len(vals)<8: vals.append('')
    if vals[1]: cur=re.sub(r'（.*','',vals[1]).replace('钱塘新区','钱塘区')
    name=vals[2]
    if '桥' not in name: continue
    B.append(dict(src='xlsx',dist=cur,town_raw=vals[5],name=name,era=vals[3],cat=vals[4],loc=vals[6],level='杭州市文物保护点',doc=vals[7]))
json.dump(B,open(S+'/build/xlsx_bridges.json','w'),ensure_ascii=False,indent=1)
print(len(B))
for b in B:
    m=find_town(b['town_raw']+' '+b['loc'],b['dist'])
    b['town']=m[0][1] if len(m)==1 else None
    if len(m)!=1: print('UNMATCHED',b['dist'],b['name'],'|',b['town_raw'],'|',b['loc'][:40],'|',m)
json.dump(B,open(S+'/build/xlsx_bridges.json','w'),ensure_ascii=False,indent=1)
