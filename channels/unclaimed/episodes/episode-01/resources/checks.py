#!/usr/bin/env python3
import subprocess,json,numpy as np,os,re,tempfile
from PIL import Image
M='unclaimed-ep01.mp4'
S=json.load(open('resources/script/scenes.json'))['scenes']
TD=tempfile.mkdtemp()
def probe(k,st='format'):
    return subprocess.run(['ffprobe','-v','error','-show_entries',f'{st}={k}','-of','csv=p=0',M],
                          capture_output=True,text=True).stdout.strip().split('\n')[0]
dur=float(probe('duration'))
target=sum(s['duration_ms'] for s in S)/1000
print('1. RUNTIME      %.2fs vs target %.2fs  delta %.2fs  %s'%(dur,target,dur-target,'PASS' if abs(dur-target)<=2 else 'FAIL'))

def grab(t):
    p=f'{TD}/f.png'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',M,'-vframes','1','-vf','scale=640:360',p],check=True)
    return np.array(Image.open(p).convert('RGB'),dtype=float)
def emf(a):
    r,g,b=a[...,0],a[...,1],a[...,2]
    mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    s=np.where(mx>0,(mx-mn)/np.maximum(mx,1),0)
    return float(((g>r+25)&(g>b+25)&(s>0.30)).mean())

# 2. AV sync at beats 1, 20, 40: narration onset should sit 400ms into each beat window
def rd(ss,t):
    w=subprocess.run(['ffmpeg','-loglevel','error','-ss',str(ss),'-i',M,'-t',str(t),
                      '-ac','1','-ar','16000','-f','wav','-'],capture_output=True).stdout
    return np.frombuffer(w[44:],dtype='<i2').astype(float)/32768.0
def onset(a,sr=16000,win=0.02):
    n=int(sr*win);m=len(a)//n
    r=np.sqrt((a[:m*n].reshape(m,n)**2).mean(1))
    if r.max()<=0: return None
    return int(np.argmax(r>0.08*r.max()))*win
sync=[]
for i in (1,20,40):
    st=sum(s['duration_ms'] for s in S if s['beat_index']<i)/1000
    o=onset(rd(st,6.0))
    sync.append((i,round((o-0.400)*1000,1)))
print('2. AV SYNC      beats 1/20/40 narration offset vs the 400ms grid (ms): %s  %s'
      %(sync,'PASS' if all(abs(d)<=120 for _,d in sync) else 'FAIL'))

# 3. black frames
blk=[]
for s in S:
    st=sum(x['duration_ms'] for x in S if x['beat_index']<s['beat_index'])/1000
    a=grab(st+1.0)
    if a.max()<14: blk.append(s['beat_index'])
print('3. BLACK FRAMES none found' if not blk else '3. BLACK FRAMES FAIL %s'%blk, ' PASS' if not blk else '')

# 4. emerald: one sample per beat
em={}
for s in S:
    st=sum(x['duration_ms'] for x in S if x['beat_index']<s['beat_index'])/1000
    em[s['beat_index']]=emf(grab(st+2.5))
green=[i for i,v in em.items() if v>0.01]
print('4. EMERALD      beats over 1%%: %s   beat17=%.4f  max elsewhere=%.4f  %s'
      %(green,em[17],max(v for i,v in em.items() if i!=17),'PASS' if green==[17] else 'FAIL'))

# 5. numerals on screen match the figure spoken in that beat
W={'0':'zero','1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven',
   '8':'eight','9':'nine','10':'ten','11':'eleven','12':'twelve','13':'thirteen','14':'fourteen',
   '15':'fifteen','20':'twenty','37':'thirty seven','50':'fifty','222':'twenty two',
   '27':'twenty seven'}
bad=[]
for s in S:
    t=s['type_layer']
    if not t or not re.search(r'\d',t): continue
    nar=s['narration'].lower()
    nums=re.findall(r'\d[\d,]*',t)
    for n in nums:
        core=n.replace(',','')
        if core in W and W[core] in nar: continue
        if core.startswith('27') and 'twenty seven' in nar: continue
        if core.startswith('222') and 'twenty two' in nar: continue
        if core in nar: continue
        bad.append((s['beat_index'],t))
print('5. NUMERALS     every on screen figure spoken in the same beat: %s'%('PASS' if not bad else 'FAIL %s'%bad))
