#!/usr/bin/env python3
"""Build one HyperFrames thumbnail composition per variant.

Type is composed here, never generated into the frame. Four words maximum,
upper third, wordmark present. Colour comes only from palette.css.

Recorded palette exception (carried from the Episode 1 build log): thumbnail
type is warm tan --type-warm rather than bone cream, because cream on sage
disappears at feed size. The episode body keeps cream.
"""
import json, os, html

VARIANTS = [
    ('a', 'They Still Owe You', True),
    ('b', 'Check Your Name',    False),
    ('c', 'Nobody Claimed It',  False),
]

TPL = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=%(W)d, height=%(H)d" />
    <title>UNCLAIMED Episode 1 thumbnail %(KEY)s</title>
    <script src="gsap.min.js"></script>
    <link rel="stylesheet" href="palette.css" />
    <style>
      @font-face { font-family: "Ep Didone"; src: url("fonts/playfair.ttf") format("truetype"); font-weight: 400 900; font-display: block; }
      @font-face { font-family: "Ep Condensed"; src: url("fonts/archivonarrow.ttf") format("truetype"); font-weight: 400 700; font-display: block; }
      body { margin: 0; background: var(--ground); }
      #root { position: relative; width: %(W)dpx; height: %(H)dpx; overflow: hidden; }
      #stage { position: absolute; inset: 0; background: var(--ground); }
      img.clip { position: absolute; inset: 0; width: %(W)dpx; height: %(H)dpx; object-fit: cover; display: block; }
      .band {
        position: absolute; left: 0; top: 0; width: %(W)dpx; height: %(BAND)dpx;
        display: flex; flex-direction: column; align-items: center; justify-content: center; gap: %(GAP)dpx;
      }
      .headline {
        font-family: "Ep Condensed", sans-serif; font-weight: 700;
        font-size: %(FS)dpx; letter-spacing: -0.005em; text-transform: uppercase;
        color: var(--type-warm); line-height: 0.98; text-align: center; margin: 0;
      }
      .wordmark {
        font-family: "Ep Didone", serif; font-weight: 500;
        font-size: %(WM)dpx; letter-spacing: 0.135em; text-transform: uppercase;
        color: var(--type-cream); line-height: 1; margin: 0;
      }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="thumb-%(KEY)s" data-start="0" data-width="%(W)d" data-height="%(H)d" data-duration="1">
      <div id="stage"></div>
      <img id="obj-%(KEY)s" class="clip" src="%(SRC)s" data-start="0" data-duration="1" data-track-index="0" alt="" />
      <div id="band-%(KEY)s" class="clip band" data-start="0" data-duration="1" data-track-index="5">
        <p class="headline">%(TEXT)s</p>
        <p class="wordmark">UNCLAIMED</p>
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["thumb-%(KEY)s"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
'''

for key, text, emerald in VARIANTS:
    assert len(text.split()) <= 4, text
    for asp, W, H, BAND, FS, WM, GAP in (('16x9', 1920, 1080, 380, 132, 46, 26),
                                         ('1x1', 1080, 1080, 340, 104, 38, 22)):
        src = '../frames/thumb-%s-%s.png' % (key, asp)
        doc = TPL % dict(W=W, H=H, BAND=BAND, FS=FS, WM=WM, GAP=GAP, KEY=key,
                         SRC='assets/thumb-%s-%s.png' % (key, asp),
                         TEXT=html.escape(text))
        open('thumb-%s-%s.html' % (key, asp), 'w').write(doc)
print('wrote', len(VARIANTS) * 2, 'thumbnail compositions')
for key, text, em in VARIANTS:
    print('  %s: %-20r words=%d emerald=%s' % (key, text, len(text.split()), em))
