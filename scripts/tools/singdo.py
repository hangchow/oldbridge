import re,os,json,time,html,subprocess,urllib.parse
import os; S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
D=S + '/singdo'
B='http://www.singdo.org/wenbao/'
def get(u,p):
    if not os.path.exists(p) or os.path.getsize(p)==0:
        subprocess.run(['curl','-sL','-m','60','-A','Mozilla/5.0','-o',p,u]); time.sleep(0.5)
    return open(p,'rb').read().decode('utf-8','ignore')
top=open(D+'/luelan.html',encoding='utf8').read()
cats=[]
for c,t in re.findall(r'luelan_list\.php\?catid=(\d+)">([^<]+)<',top):
    if (c,t) not in cats: cats.append((c,t.strip()))
os.makedirs(D+'/list',exist_ok=True); os.makedirs(D+'/disp',exist_ok=True); os.makedirs(D+'/img',exist_ok=True)
idx={}
for c,t in cats:
    ids=[]; pg=1
    while True:
        s=get(f'{B}luelan_list.php?catid={c}&page={pg}',f'{D}/list/{c}_{pg}.html')
        new=[i for i in re.findall(r'luelan_disp\.php\?luelan_id=(\d+)',s) if i not in ids]
        if not new: break
        ids+=new; pg+=1
        if pg>30: break
    idx[c]=dict(title=t,ids=ids); print(c,t,len(ids),flush=True)
json.dump(idx,open(D+'/cats.json','w'),ensure_ascii=False,indent=1)
recs={}
for c,v in idx.items():
    for i in v['ids']:
        if i in recs: recs[i]['cats'].append(v['title']); continue
        s=get(f'{B}luelan_disp.php?luelan_id={i}',f'{D}/disp/{i}.html')
        t=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'(?is)<(script|style).*?</\1>','',s))))
        f=lambda k: (re.search(k+r'\s*[：:]\s*(.*?)\s+(?:地 址|年 代|结 构|类 别|文物简介)',t) or [None,''])[1]
        name=(re.search(r'名 称\s*[：:]\s*(\S+)',t) or [None,''])[1]
        intro=(re.search(r'文物简介\s*[：:]\s*(.*?)\s*点击查看大图',t) or [None,''])[1]
        imgs=[]
        for u in dict.fromkeys(re.findall(r'(http://z1\.singdo\.org/wenbao/upfile/[^"\']+\.(?:png|jpe?g))',s,re.I)):
            p=f'{D}/img/{i}_'+os.path.basename(u)
            if not os.path.exists(p): subprocess.run(['curl','-sL','-m','90','-A','Mozilla/5.0','-o',p,u]); time.sleep(0.3)
            imgs.append(os.path.basename(p))
        recs[i]=dict(id=i,name=name,addr=f('地 址'),era=f('年 代'),struct=f('结 构'),kind=f('类 别'),intro=intro,imgs=imgs,cats=[v['title']])
    json.dump(recs,open(D+'/recs.json','w'),ensure_ascii=False,indent=1)
print('records',len(recs),'images',sum(len(r['imgs']) for r in recs.values()))
