import json,os,re,subprocess,urllib.parse,time
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT='/Users/sean/workspace/oldbridge'
R=json.load(open(S+'/build/all_rows.json'))
src=json.load(open(S+'/build/imgsrc.json')) if os.path.exists(S+'/build/imgsrc.json') else {}
COUNTIES=['桐庐县','淳安县','建德市']
def folder(r): return os.path.join(ROOT,r['dist']) if r['dist'] in COUNTIES else os.path.join(ROOT,r['dist'],r['town'])
def imgname(n): return re.sub(r'（.*?）|\(.*?\)','',n).strip()+'.jpg'
for r in R:
    if not r.get('commons'): continue
    dst=os.path.join(folder(r),imgname(r['name']))
    if os.path.exists(dst): continue
    f=r['commons']; tmp=S+'/img/commons/'+re.sub(r'[/ ]','_',f)
    url='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(f)+'?width=1280'
    subprocess.run(['curl','-sL','-m','60','-A','oldbridge-research/1.0 (personal heritage notes)','-o',tmp,url])
    t=subprocess.run(['file','-b',tmp],capture_output=True,text=True).stdout
    if 'JPEG' in t: subprocess.run(['cp','-n',tmp,dst])
    elif 'PNG' in t: subprocess.run(['sips','-s','format','jpeg',tmp,'--out',dst],capture_output=True)
    else: print('FAIL',f,t[:60]); continue
    page='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(f.replace(' ','_'))
    src[os.path.relpath(dst,ROOT)]=f'[维基共享资源：{f}]({page})（许可见文件页）'
    print('OK',r['dist'],r['town'],r['name'],'<-',f); time.sleep(1)
json.dump(src,open(S+'/build/imgsrc.json','w'),ensure_ascii=False,indent=1)
