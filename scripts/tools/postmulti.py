# usage: python3 postmulti.py '<json list of {"key":"dist|town|name","src":"..."}>'  -- assigns NEW files (since before.txt) in mtime order; never deletes
import json,os,sys,subprocess,re,time
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT='/Users/sean/workspace/oldbridge/杭州市'; DL=os.path.expanduser('~/Downloads')
C=['桐庐县','淳安县','建德市']
items=json.loads(sys.argv[1])
before=set(open(S+'/tools/before.txt').read().split('\n'))
for _ in range(10):
    new=[f for f in os.listdir(DL) if f not in before and not f.endswith('.crdownload') and f!='.DS_Store']
    if len(new)>=len(items): break
    time.sleep(2)
new.sort(key=lambda f: os.path.getmtime(os.path.join(DL,f)))
if len(new)!=len(items):
    print('ABORT count mismatch: new',len(new),new,'expected',len(items)); sys.exit(1)
src=json.load(open(S+'/build/imgsrc.json'))
os.makedirs(S+'/img/raw',exist_ok=True)
for f,it in zip(new,items):
    dist,town,name=it['key'].split('|')
    folder=os.path.join(ROOT,dist) if dist in C else os.path.join(ROOT,dist,town)
    dst=os.path.join(folder,re.sub(r'（.*?）','',name)+str(it.get('n',1))+'.jpg')
    raw=os.path.join(S,'img/raw',f)
    subprocess.run(['mv','-n',os.path.join(DL,f),raw])
    t=subprocess.run(['file','-b',raw],capture_output=True,text=True).stdout
    if os.path.exists(dst): print('EXISTS',dst); continue
    if t.startswith('JPEG'): subprocess.run(['cp','-n',raw,dst])
    elif re.match(r'(PNG|RIFF|GIF)',t): subprocess.run(['sips','-s','format','jpeg',raw,'--out',dst],capture_output=True)
    else: print('NOTIMG',f,t[:40]); continue
    src[os.path.relpath(dst,ROOT)]=it['src']
    print('OK',it['key'],subprocess.run(['sips','-g','pixelWidth','-g','pixelHeight',dst],capture_output=True,text=True).stdout.split()[-3:])
json.dump(src,open(S+'/build/imgsrc.json','w'),ensure_ascii=False,indent=1)
