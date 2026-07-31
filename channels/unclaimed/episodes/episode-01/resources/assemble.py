#!/usr/bin/env python3
"""Episode 1 master, FFmpeg assembly at 720p. Resumable. No generation."""
import os, json, subprocess, sys, time
from PIL import Image, ImageDraw, ImageFont

T0=time.time()
W,H,FPS = 1280,720,30
DIDONE='composition/fonts/playfair.ttf'
COND='composition/fonts/archivonarrow.ttf'
CREAM=(0xF2,0xED,0xDF); TAN=(0xC9,0xB4,0x8A)
TYPE_IN=1.5; FADE=0.4
SEG='seg'; TYP='typepng'
os.makedirs(SEG,exist_ok=True); os.makedirs(TYP,exist_ok=True)
S=json.load(open('script/scenes.json'))['scenes']

def run(c):
    r=subprocess.run(c,capture_output=True,text=True)
    if r.returncode!=0:
        sys.stderr.write(' '.join(c)+'\n'+r.stderr[-3000:]+'\n'); raise SystemExit(1)
    return r

def ok(p,mind=0.5):
    if not os.path.exists(p) or os.path.getsize(p)<10000: return False
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],
                     capture_output=True,text=True)
    try: return float(r.stdout.strip())>mind
    except: return False

# ---------- type layers ----------
def fit(txt,path,size,maxw):
    f=ImageFont.truetype(path,size)
    while size>20:
        f=ImageFont.truetype(path,size)
        if f.getbbox(txt)[2]-f.getbbox(txt)[0] <= maxw: break
        size-=4
    return f

def track(d,txt,f,cx,y,fill,tracking):
    ws=[f.getbbox(c)[2]-f.getbbox(c)[0] for c in txt]
    total=sum(ws)+tracking*(len(txt)-1)
    x=cx-total/2
    for c,w in zip(txt,ws):
        d.text((x,y),c,font=f,fill=fill); x+=w+tracking

def make_type(txt):
    img=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    if txt=='UNCLAIMED':
        f=fit(txt,DIDONE,72,int(W*0.72))
        em=f.getbbox('M')[3]-f.getbbox('M')[1]
        track(d,txt,f,W/2,int(H*0.14),CREAM+(255,),int(em*0.135))  # tracking 135
    else:
        f=fit(txt,COND,84,int(W*0.86))
        w=f.getbbox(txt)[2]-f.getbbox(txt)[0]
        d.text((W/2-w/2,int(H*0.13)),txt,font=f,fill=TAN+(255,))
    return img

nt=0
for s in S:
    if not s['type_layer']: continue
    p=f"{TYP}/{s['beat_index']:02d}.png"
    if not os.path.exists(p): make_type(s['type_layer']).save(p); nt+=1
print(f'type layers ready ({nt} built this run)')

# ---------- per beat segments ----------
DRIFT_APPLIED=False   # dropped: zoompan per-frame eval roughly doubles encode cost on 2 cores
built=skipped=0
for s in S:
    i=s['beat_index']; dur=s['duration_ms']/1000.0
    out=f'{SEG}/{i:02d}.mp4'
    if ok(out,dur-0.2): skipped+=1; continue
    tp=f'{TYP}/{i:02d}.png'
    if s['type_layer'] and os.path.exists(tp):
        fc=(f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},'
            f'tpad=stop_mode=clone:stop_duration=30[v];'
            f'[1:v]scale={W}:{H},format=rgba,fade=t=in:st={TYPE_IN}:d={FADE}:alpha=1[t];'
            f'[v][t]overlay=0:0:format=auto[o]')
        cmd=['ffmpeg','-loglevel','error','-y','-i',f'clips/{i:02d}.mp4','-loop','1','-i',tp,
             '-filter_complex',fc,'-map','[o]']
    else:
        fc=(f'[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},'
            f'tpad=stop_mode=clone:stop_duration=30[o]')
        cmd=['ffmpeg','-loglevel','error','-y','-i',f'clips/{i:02d}.mp4',
             '-filter_complex',fc,'-map','[o]']
    cmd+=['-t',f'{dur:.3f}','-an','-c:v','libx264','-preset','ultrafast','-crf','18',
          '-pix_fmt','yuv420p','-threads','0',out]
    run(cmd); built+=1
print(f'segments: {built} built, {skipped} reused')

# ---------- concat list ----------
with open('concat.txt','w') as f:
    for s in S: f.write(f"file '{SEG}/{s['beat_index']:02d}.mp4'\n")
print('concat list written')
print('elapsed %.1fs' % (time.time()-T0))
