import json,os,re,urllib.request,urllib.parse,urllib.error,time
S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
ROOT='/Users/sean/workspace/oldbridge/苏州市'
R=json.load(open(S+'/sz/rows.json')); IMG=json.load(open(S+'/sz/imgsrc.json'))
UA={'User-Agent':'oldbridge-research/1.0 (personal project)'}
def get(u):
    for k in range(5):
        try:
            time.sleep(1.2); return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40))
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(20 * (k + 1))
    raise SystemExit('rate limited')
core=lambda n:re.sub(r'（.*?）|\(.*?\)','',n)
DS={'姑苏区':'苏州','虎丘区':'苏州','吴中区':'吴中','相城区':'相城','吴江区':'吴江','苏州工业园区':'苏州','常熟市':'常熟','张家港市':'张家港','昆山市':'昆山','太仓市':'太仓'}
n=0
for r in R:
    b=core(r['name']); dst=f"{ROOT}/{r['dist']}/{b}1.jpg"
    if os.path.exists(dst): continue
    for t in [f'{b} ({DS[r["dist"]]})', f'{b} (苏州)', f'{b} ({r["dist"][:2]})', b]:
        q=get('https://zh.wikipedia.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',titles=t,prop='pageimages|extracts|info',piprop='original|name',exintro=1,explaintext=1,redirects=1,format='json',inprop='url')))
        pg=list(q['query']['pages'].values())[0]
        if 'missing' in pg or 'original' not in pg: continue
        ex=pg.get('extract','')
        if not ('桥' in ex and (DS[r['dist']] in ex or r['dist'][:2] in ex or (r['town']!='—' and r['town'][:2] in ex))): continue
        u=pg['original']['source'].split('?')[0]; fn=pg['pageimage']
        if not re.search(r'\.(jpe?g)$',u,re.I): break
        th=get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',titles='File:'+fn,prop='imageinfo',iiprop='url',iiurlwidth=1600,format='json')))
        ii=list(th['query']['pages'].values())[0].get('imageinfo',[{}])[0]
        src=ii.get('thumburl') or u
        data=urllib.request.urlopen(urllib.request.Request(src,headers=UA),timeout=60).read()
        open(dst,'wb').write(data)
        IMG[f"{r['dist']}/{b}1.jpg"]=f'[维基共享资源：{fn}](https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(fn)})（维基百科条目“{pg["title"]}”配图，许可见文件页）'
        print('OK',r['dist'],b,'<-',pg['title'],fn); n+=1; break
    time.sleep(0.3)
json.dump(IMG,open(S+'/sz/imgsrc.json','w'),ensure_ascii=False,indent=1)
print('added',n)
