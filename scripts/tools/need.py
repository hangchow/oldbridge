import json,os,re,sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT='/Users/sean/workspace/oldbridge/杭州市'; C3=['桐庐县','淳安县','建德市']
K=json.load(open(S+'/build/qkeys.json')); cnt=json.loads(sys.argv[1])
plan=[]
for i,c in cnt.items():
    i=int(i); d,t,n=K[i].split('|'); f=os.path.join(ROOT,d) if d in C3 else os.path.join(ROOT,d,t)
    base=re.sub(r'（.*?）','',n); have=[k for k in (1,2,3) if os.path.exists(os.path.join(f,f'{base}{k}.jpg'))]
    free=[k for k in (1,2,3) if k not in have]
    for j,slot in zip(range(c),free): plan.append([i,j,slot])
json.dump(plan,open(S+'/build/plan.json','w')); print(len(plan))
