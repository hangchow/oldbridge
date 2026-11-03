import subprocess,os,struct,sys,tempfile
def ahash(p):
    t=tempfile.mktemp(suffix='.bmp')
    subprocess.run(['sips','-s','format','bmp','-z','8','8',p,'--out',t],capture_output=True)
    b=open(t,'rb').read(); os.remove(t)
    off=struct.unpack('<I',b[10:14])[0]; w,h=struct.unpack('<ii',b[18:26]); bpp=struct.unpack('<H',b[28:30])[0]
    px=[]; row=((bpp*w+31)//32)*4; step=bpp//8
    for y in range(abs(h)):
        for x in range(w):
            i=off+y*row+x*step; bb,g,r=b[i],b[i+1],b[i+2]; px.append(0.299*r+0.587*g+0.114*bb)
    m=sum(px)/len(px); return sum((1<<i) for i,v in enumerate(px) if v>m)
def dist(a,b): return bin(a^b).count('1')
if __name__=='__main__':
    a=ahash(sys.argv[1]); b=ahash(sys.argv[2]); print(dist(a,b))
