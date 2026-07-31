#!/usr/bin/env python3
"""Compose the four word string and wordmark over each thumbnail object frame at 1280x720.
Type colour is Contract B ink navy #1F3A6E, a considered amendment recorded in build-log.md:
cream and tan on sage measure 1.15:1 and 1.50:1 and vanish at feed size."""
import os
from PIL import Image, ImageDraw, ImageFont
W,H=1280,720
DIDONE='resources/composition/fonts/playfair.ttf'
COND='resources/composition/fonts/archivonarrow.ttf'
NAVY=(0x1F,0x3A,0x6E)
V=[('a','They Still Owe You'),('b','Check Your Name'),('c','Nobody Claimed It')]

def fit(txt,path,size,maxw):
    while size>20:
        f=ImageFont.truetype(path,size)
        if f.getbbox(txt)[2]-f.getbbox(txt)[0]<=maxw: return f
        size-=4
    return ImageFont.truetype(path,size)

def track(d,txt,f,cx,y,fill,tr):
    ws=[f.getbbox(c)[2]-f.getbbox(c)[0] for c in txt]
    x=cx-(sum(ws)+tr*(len(txt)-1))/2
    for c,w in zip(txt,ws): d.text((x,y),c,font=f,fill=fill); x+=w+tr

for key,text in V:
    assert len(text.split())<=4
    base=Image.open(f'resources/frames/thumb-{key}-16x9.png').convert('RGB').resize((W,H),Image.LANCZOS)
    d=ImageDraw.Draw(base)
    f=fit(text.upper(),COND,116,int(W*0.88))
    w=f.getbbox(text.upper())[2]-f.getbbox(text.upper())[0]
    d.text((W/2-w/2,int(H*0.09)),text.upper(),font=f,fill=NAVY)
    wm=ImageFont.truetype(DIDONE,34)
    em=wm.getbbox('M')[3]-wm.getbbox('M')[1]
    track(d,'UNCLAIMED',wm,W/2,int(H*0.265),NAVY,int(em*0.135))
    base.save(f'thumbnail-{key}.png')
    print('thumbnail-%s.png  %r  words=%d'%(key,text,len(text.split())))
