import re,os,json,time,subprocess,html
import os; S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
D=S + '/singdo'
R=json.load(open(D+'/recs.json')); os.makedirs(D+'/photo',exist_ok=True); n=0
for i,r in R.items():
    s=open(f'{D}/disp/{i}.html',encoding='utf8',errors='ignore').read()
    ph=[]
    for src,tit in re.findall(r'<img src="(upfile/[^"]+_small\.\w+)"\s*/?>\s*</a>\s*<a class="tit">(.*?)</a>',s,re.S):
        p=f'{D}/photo/{i}_'+os.path.basename(src)
        if not os.path.exists(p) or os.path.getsize(p)==0:
            subprocess.run(['curl','-sL','-m','60','-A','Mozilla/5.0','-o',p,'http://www.singdo.org/wenbao/'+src]); time.sleep(0.3)
        ph.append(dict(file=os.path.basename(p),caption=html.unescape(tit).strip())); n+=1
    r['photos']=ph
json.dump(R,open(D+'/recs.json','w'),ensure_ascii=False,indent=1)
print('photos',n)
