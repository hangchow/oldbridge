import os
import json,re,sys,urllib.parse
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
M=json.load(open(S+'/build/missing.json'))
start,n=int(sys.argv[1]),int(sys.argv[2]); TAB=int(sys.argv[3])
acts=[]; keys=[]
for r in M[start:start+n]:
    core=re.sub(r'（.*?）','',r['name'])
    if '、' in core or '六桥' in core: core=core.split('（')[0]
    d=re.sub(r'(区|县|市)$','',r['dist']); t=re.sub(r'(街道|镇|乡|畲族乡)$','',r['town'])
    vill=[re.sub(r'(行政)?村$','',v) for v in re.findall(r'([一-龥]{2,4}?(?:行政)?村)',r['loc'])]
    vill=[v[-3:] if len(v)>3 else v for v in vill if len(v)>=2][:3]
    ctx=list(dict.fromkeys([t,d]+vill))
    q=f'{d} {t} {core}'
    js=f"await new Promise(r=>setTimeout(r,1800)); eval(localStorage.pick)({json.dumps(core,ensure_ascii=False)},{json.dumps(ctx,ensure_ascii=False)},{json.dumps(r['dist']+'|'+r['town']+'|'+r['name'],ensure_ascii=False)})"
    acts+= [dict(name='navigate',input=dict(tabId=TAB,url='https://image.baidu.com/search/index?tn=baiduimage&word='+urllib.parse.quote(q))),
            dict(name='javascript_tool',input=dict(action='javascript_exec',tabId=TAB,text=js)),
            dict(name='computer',input=dict(action='wait',tabId=TAB,duration=2.5)),
            dict(name='computer',input=dict(action='left_click',tabId=TAB,coordinate=[1060,590],action_summary='Clicks 下载 on the image detail page')),
            dict(name='computer',input=dict(action='wait',tabId=TAB,duration=1.5))]
print(json.dumps(acts,ensure_ascii=False))
