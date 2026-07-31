#!/usr/bin/env python3
"""
Build the Episode 1 HyperFrames composition from scenes.json.

Deterministic: same scenes.json + same assets produce a byte-identical index.html.
Colour is never written inline; every composed colour is a custom property from
palette.css, itself generated from Contract A's CLOSED PALETTE table.

Timing grid (verified against the programme audio by cross-correlation):
  beat i occupies [(i-1)*15s, +15s); beat 40 occupies [585s, +20s)
  narration for each beat starts 400ms into its window
"""
import json, os, html, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(HERE)
SCENES = os.path.join(RES, 'script', 'scenes.json')

BEAT_S = 15.0
FINAL_BEAT_S = 20.0
CLIP_S = 5.0
LEAD_IN = 0.4
TYPE_IN = 1.5
WORDMARK = {'UNCLAIMED'}

def beat_start(i): return (i - 1) * BEAT_S
def beat_len(i): return FINAL_BEAT_S if i == 40 else BEAT_S

def build():
    d = json.load(open(SCENES))
    scenes = d['scenes']
    total = beat_start(40) + FINAL_BEAT_S
    assert total == 605.0, total

    parts = []
    for s in scenes:
        i = s['beat_index']; st = beat_start(i); dur = beat_len(i)
        tl = s.get('type_layer'); nn = '%02d' % i
        parts.append(
            '      <video id="clip-%s" class="clip" src="assets/clips/%s.mp4"\n'
            '             data-start="%g" data-duration="%g" data-track-index="0"\n'
            '             muted playsinline></video>' % (nn, nn, st, CLIP_S))
        parts.append(
            '      <img id="hold-%s" class="clip" src="holds/%s.png"\n'
            '           data-start="%g" data-duration="%g" data-track-index="0" alt="" />'
            % (nn, nn, st + CLIP_S, dur - CLIP_S))
        if tl:
            kind = 'wordmark' if tl in WORDMARK else 'label'
            accent = ''
            if s['is_green']:
                accent = '\n        <span id="accent-%s" class="accent-rule"></span>' % nn
            parts.append(
                '      <div id="type-%s" class="clip type-slot"\n'
                '           data-start="%g" data-duration="%g" data-track-index="5">\n'
                '        <span class="%s">%s</span>%s\n'
                '      </div>' % (nn, st + TYPE_IN, dur - TYPE_IN, kind, html.escape(tl), accent))

    parts.append(
        '      <audio id="programme" src="assets/voice/episode-audio-master.wav"\n'
        '             data-start="0" data-duration="%g" data-track-index="10" data-volume="1"></audio>' % total)

    tw = []
    for s in scenes:
        i = s['beat_index']
        if not s.get('type_layer'): continue
        nn = '%02d' % i
        at = beat_start(i) + TYPE_IN
        kind = 'wordmark' if s['type_layer'] in WORDMARK else 'label'
        tw.append('      tl.fromTo("#type-%s .%s", { opacity: 0, y: 18 }, '
                  '{ opacity: 1, y: 0, duration: 0.7, ease: "power2.out" }, %g);' % (nn, kind, at))
        if s['is_green']:
            tw.append('      tl.fromTo("#accent-%s", { scaleX: 0 }, '
                      '{ scaleX: 1, duration: 0.6, ease: "power2.out" }, %g);' % (nn, at + 0.9))

    doc = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>UNCLAIMED Episode 1</title>
    <script src="gsap.min.js"></script>
    <link rel="stylesheet" href="palette.css" />
    <style>
      @font-face {
        font-family: "Ep Didone";
        src: url("fonts/playfair.ttf") format("truetype");
        font-weight: 400 900;
        font-display: block;
      }
      @font-face {
        font-family: "Ep Condensed";
        src: url("fonts/archivonarrow.ttf") format("truetype");
        font-weight: 400 700;
        font-display: block;
      }
      body { margin: 0; background: var(--ground); }
      #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
      /* full-bleed child, never the root itself: the producer can drop a root background */
      #stage { position: absolute; inset: 0; background: var(--ground); }
      video.clip, img.clip {
        position: absolute; inset: 0;
        width: 1920px; height: 1080px;
        object-fit: cover; display: block;
      }
      /* type occupies the upper third; the subject keeps the lower two thirds */
      .type-slot {
        position: absolute; left: 0; top: 0;
        width: 1920px; height: 360px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        gap: 18px;
      }
      .wordmark {
        display: block;
        font-family: "Ep Didone", serif;
        font-weight: 500;
        font-size: 92px;
        letter-spacing: 0.135em;
        text-transform: uppercase;
        color: var(--type-cream);
        line-height: 1;
      }
      .label {
        display: block;
        font-family: "Ep Condensed", sans-serif;
        font-weight: 700;
        font-size: 104px;
        letter-spacing: -0.005em;
        text-transform: uppercase;
        color: var(--type-warm);
        line-height: 1;
      }
      .accent-rule {
        display: block;
        width: 340px; height: 10px;
        background: var(--recoverable);
        transform-origin: center center;
      }
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="unclaimed-ep01"
      data-start="0"
      data-width="1920"
      data-height="1080"
      data-duration="__TOTAL__"
    >
      <div id="stage"></div>
__PARTS__
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
__TWEENS__
      window.__timelines["unclaimed-ep01"] = tl;
    </script>
  </body>
</html>
'''
    doc = doc.replace('__TOTAL__', '%g' % total)
    doc = doc.replace('__PARTS__', '\n'.join(parts))
    doc = doc.replace('__TWEENS__', '\n'.join(tw))
    out = os.path.join(HERE, 'index.html')
    open(out, 'w').write(doc)
    print('wrote', out)
    print('duration %gs  beats %d  clips %d  holds %d  type layers %d'
          % (total, len(scenes), len(scenes), len(scenes),
             sum(1 for s in scenes if s.get('type_layer'))))
    print('index.html sha256', hashlib.sha256(doc.encode()).hexdigest())

if __name__ == '__main__':
    build()
