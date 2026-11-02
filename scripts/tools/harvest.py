# usage: harvest.py '<json [[i,slot,ts_ms,alt],...]>'  map Downloads files (new since before.txt) by mtime to click ts; never deletes
import json,os,sys,re,subprocess
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT='/Users/sean/workspace/oldbridge/杭州市'; DL=os.path.expanduser('~/Downloads'); C3=['桐庐县','淳安县','建德市']
K=json.load(open(S+'/build/qkeys.json')); items=json.loads(sys.argv[1])
before=set()
used=set(json.load(open(S+'/tools/used.json'))) if os.path.exists(S+'/tools/used.json') else set()
files=[(os.stat(os.path.join(DL,f)).st_birthtime,f) for f in os.listdir(DL) if f not in before and f not in used and not f.endswith('.crdownload') and f!='.DS_Store']
src=json.load(open(S+'/build/imgsrc.json')); out=[]
for i,slot,ts,alt in items:
    t=ts/1000; cand=[(ft-t,f) for ft,f in files if -1<=ft-t<=12 and f not in used]
    if not cand: print('MISS',i,slot); continue
    cand.sort(); f=cand[0][1]; used.add(f)
    d,tn,n=K[i].split('|'); folder=os.path.join(ROOT,d) if d in C3 else os.path.join(ROOT,d,tn)
    dst=os.path.join(folder,re.sub(r'（.*?）','',n)+f'{slot}.jpg')
    raw=os.path.join(S,'img/raw',f); subprocess.run(['mv','-n',os.path.join(DL,f),raw])
    if os.path.exists(dst): print('EXISTS',dst); continue
    ty=subprocess.run(['file','-b',raw],capture_output=True,text=True).stdout
    if ty.startswith('JPEG'): subprocess.run(['cp','-n',raw,dst])
    else: subprocess.run(['sips','-s','format','jpeg',raw,'--out',dst],capture_output=True)
    src[os.path.relpath(dst,ROOT)]=f'百度图片：《{alt}》'; out.append(os.path.relpath(dst,ROOT))
json.dump(src,open(S+'/build/imgsrc.json','w'),ensure_ascii=False,indent=1)
json.dump(sorted(used),open(S+'/tools/used.json','w'))
os.makedirs(S+'/img/review',exist_ok=True)
for p in out:
    subprocess.run(['sips','-Z','220',os.path.join(ROOT,p),'--out',S+'/img/review/'+p.replace('/','_')],capture_output=True)
print('saved',len(out)); print('\n'.join(out))
