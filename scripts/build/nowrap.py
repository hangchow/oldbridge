# 后处理：表格中 名次/序号/市/区县/乡镇/乡镇（街道） 列不换行
import os,re
O='/Users/sean/workspace/oldbridge'; COLS={'名次','序号','市','区县','乡镇','乡镇（街道）','级别','数量'}
def wrap(c):
    c=c.strip().replace('⁠','')
    if not c or c.startswith('<nobr>') or set(c)<=set('-'): return f' {c} '
    return f' <nobr>{c}</nobr> '
n=0
for root,_,fs in os.walk(O):
    for f in fs:
        if not f.endswith('.md'): continue
        p=os.path.join(root,f); L=open(p,encoding='utf8').read().replace('⁠','').split('\n'); idx=None; out=[]
        for l in L:
            if l.startswith('|'):
                cells=l.strip().strip('|').split('|')
                if idx is None:
                    idx={i for i,c in enumerate(cells) if re.sub(r'<.*?>','',c).strip() in COLS}
                    cells=[wrap(c) if i in idx else c for i,c in enumerate(cells)]
                elif set(''.join(cells).strip())<=set('-: '): pass
                else: cells=[wrap(c) if i in idx else c for i,c in enumerate(cells)]
                l='|'+'|'.join(cells)+'|'
            else: idx=None
            out.append(l)
        open(p,'w',encoding='utf8').write('\n'.join(out)); n+=1
print('processed',n)
