# flag duplicates among name1/2/3.jpg (same md5 or same pixel size); removes the higher-numbered dup (files we created), updates imgsrc
import os,re,json,hashlib,subprocess,sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT='/Users/sean/workspace/oldbridge/杭州市'
src=json.load(open(S+'/build/imgsrc.json'))
def sig(p):
    o=subprocess.run(['sips','-g','pixelWidth','-g','pixelHeight',p],capture_output=True,text=True).stdout.split()
    return hashlib.md5(open(p,'rb').read()).hexdigest(), (o[-3],o[-1])
for root,_,fs in os.walk(ROOT):
    groups={}
    for f in fs:
        m=re.match(r'(.+?)([123])\.jpg$',f)
        if m: groups.setdefault(m.group(1),[]).append((int(m.group(2)),f))
    for base,items in groups.items():
        items.sort(); seen={}
        for n,f in items:
            p=os.path.join(root,f); h,wh=sig(p)
            if h in seen or wh in seen:
                print('DUP',os.path.relpath(p,ROOT),'==',seen.get(h) or seen.get(wh)); os.remove(p); src.pop(os.path.relpath(p,ROOT),None)
            else: seen[h]=f; seen[wh]=f
json.dump(src,open(S+'/build/imgsrc.json','w'),ensure_ascii=False,indent=1)
