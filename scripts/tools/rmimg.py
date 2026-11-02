import sys,os,json
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录; ROOT='/Users/sean/workspace/oldbridge/杭州市'
src=json.load(open(S+'/build/imgsrc.json'))
for p in sys.argv[1:]:
    f=os.path.join(ROOT,p)
    if os.path.exists(f): os.remove(f); src.pop(p,None); print('removed',p)
json.dump(src,open(S+'/build/imgsrc.json','w'),ensure_ascii=False,indent=1)
