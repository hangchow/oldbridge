import re,html,sys,subprocess,hashlib,os
url=sys.argv[1]; S = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))   # scripts/ 目录
fn=S+'/l4/p_'+hashlib.md5(url.encode()).hexdigest()[:8]+'.html'
if not os.path.exists(fn): subprocess.run(['curl','-sL','-m','60','-A','Mozilla/5.0 (Macintosh) Chrome/124','-o',fn,url])
raw=open(fn,'rb').read()
try: s=raw.decode('utf-8')
except: s=raw.decode('gb18030','ignore')
s=re.sub(r'(?is)<(script|style).*?</\1>','',s)
print('PAGE',url,len(s),re.search(r'<title>(.*?)</title>',s,re.S).group(1).strip() if '<title>' in s else '')
for m in re.finditer(r'href="([^"]+\.(?:xls|xlsx|doc|docx|pdf|wps|et))"[^>]*>([^<]*)',s,re.I): print('ATT',m.group(1),m.group(2).strip())
for m in re.finditer(r'href="([^"]*file-download[^"]*)"',s): print('ATT',m.group(1))
rows=[]
for tr in re.findall(r'<tr.*?</tr>',s,re.S):
    cells=[re.sub(r'\s+','',html.unescape(re.sub(r'<[^>]+>','',c))) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',tr,re.S)]
    if cells: rows.append(cells)
print('ROWS',len(rows), rows[0] if rows else '')
hdr=[r for r in rows if any('名称' in c for c in r)][:3]
for h in hdr: print('HDR',h)
for r in rows:
    if len(r)>2 and any(re.search(r'桥',c) for c in r[1:3]): print(' | '.join(r))
if len(sys.argv)>2:
    t=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))); i=t.find(sys.argv[2]); print('TXT',t[i:i+800])
