import re,html,sys,urllib.parse
path,base=sys.argv[1],sys.argv[2]
raw=open(path,'rb').read()
for enc in ('utf-8','gb18030'):
    try: s=raw.decode(enc); break
    except: pass
s=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>','',s)
for m in re.finditer(r'(?is)<img[^>]+>',s):
    tag=m.group(0)
    src=re.search(r'(?:data-original|data-src|src)\s*=\s*["\']([^"\']+)',tag)
    if not src: continue
    u=urllib.parse.urljoin(base,html.unescape(src.group(1)))
    if any(k in u.lower() for k in ('logo','icon','.gif','avatar','qrcode','ewm')): continue
    def txt(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x))).strip()
    before=txt(s[max(0,m.start()-600):m.start()])[-80:]
    after=txt(s[m.end():m.end()+600])[:80]
    print('IMG',u); print('   <<',before); print('   >>',after)
