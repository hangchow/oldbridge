import os
import json,sys
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
P=json.load(open(S+'/build/plan.json')); a,b=int(sys.argv[1]),int(sys.argv[2]); T=1019819896
A=[]
for i,j,slot in P[a:b]:
    A+=[{"name":"javascript_tool","input":{"action":"javascript_exec","tabId":T,"text":f"eval(localStorage.go)({i})"}},
        {"name":"computer","input":{"action":"wait","tabId":T,"duration":2.2}},
        {"name":"javascript_tool","input":{"action":"javascript_exec","tabId":T,"text":f"eval(localStorage.pk)({i},{j})"}},
        {"name":"computer","input":{"action":"wait","tabId":T,"duration":2.5}},
        {"name":"computer","input":{"action":"left_click","tabId":T,"coordinate":[1060,590],"action_summary":"Clicks 下载 on the image detail page"}},
        {"name":"computer","input":{"action":"wait","tabId":T,"duration":1.5}}]
print(json.dumps(A,ensure_ascii=False,separators=(',',':')))
