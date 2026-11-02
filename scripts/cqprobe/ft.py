import json, re, os, subprocess, time, sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
HZ=[('ql15/hz_ql/'+it['page'],it['title']+' '+it['alias']) for it in json.load(open(S+'/build/cq_index.json'))]
G=[('ql15/'+p,t) for p,t in json.load(open(S+'/cq2/idx.json')).items()]
SZ=list(json.load(open(S+'/cq2/sz/idx.json')).items())
JH=[('ql15/'+p,t) for p,t in json.load(open(S+'/cq2/jh/idx.json')).items()]
Q=[(HZ,['富阳','新登','龙门','建德','大慈岩'],['庄泽','永安桥','神仙桥','新叶','乘庄']),
   (G,['南浔区','德清'],['博成','沈庄漾','德武','太堡']),
   (G,['平湖','嘉善县天凝','新埭'],['姐妹','古桥群']),
   (SZ,['甪直','车坊','郭巷','东山','七都','常熟','沙家浜','花桥','吴江区'],['大觉','大姚','渡水','渡桥村','广福','北新','唐市','天福三桥','三桥']),
   (JH,['浦江'],['广安','建光','上河'])]
os.makedirs(S+'/cqv',exist_ok=True)
for idx,places,words in Q:
    for p,t in idx:
        if not any(x in t for x in places): continue
        f=S+'/cqv/'+p.replace('/','_')
        if not os.path.exists(f) or os.path.getsize(f)==0:
            subprocess.run(['curl','-sL','-m','30','-A','Mozilla/5.0','-o',f,'http://www.china-qiao.com/'+p]); time.sleep(0.2)
        s=open(f,'rb').read().decode('gb18030','ignore'); tx=re.sub(r'\s+',' ',re.sub(r'&nbsp;',' ',re.sub(r'<[^>]+>',' ',s)))
        for w in words:
            for m in re.finditer(w,tx):
                print(w,'|',p,'|',t[:24],'|',tx[max(0,m.start()-40):m.end()+40]); break
