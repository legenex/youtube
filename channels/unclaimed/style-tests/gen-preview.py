#!/usr/bin/env python3
"""Build a single self contained preview page with the videos embedded.

index.html references out/*.mp4 on disk, so it only works next to the files or
behind serve.py. This produces one HTML file that carries everything inline:
the trailers as data URIs, the Inter faces as data URIs, and the guides as
modals. It can be published or emailed and it will play anywhere.

    python3 gen-preview.py [dst.html]

The embedded trailers are preview encodes, not the masters: 960 wide, CRF 31,
72k audio. The masters in out/ stay at the contract encode. Re-encoding is
needed because the ten masters total 34.6 MB, which is past the size ceiling of
every host that will take a single file, while the preview set is 8.3 MB.
"""
import base64
import glob
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
GUIDES = os.path.join(HERE, "guides")
FONTS = os.path.join(HERE, "work-ep02", "fonts")
PREV = os.path.join(HERE, "work-ep02", "preview")

sys.path.insert(0, HERE)
import measure

_spec = importlib.util.spec_from_file_location("genindex", os.path.join(HERE, "gen-index.py"))
_gi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gi)
md_to_html, EP5_STYLES, EP2_STYLES = _gi.md_to_html, _gi.EP5_STYLES, _gi.EP2_STYLES


def preview_encode(src):
    """Cache a small encode of one trailer. Idempotent, like everything else here."""
    os.makedirs(PREV, exist_ok=True)
    dst = os.path.join(PREV, os.path.basename(src))
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                        "-vf", "scale=960:-2", "-c:v", "libx264", "-preset", "slow",
                        "-crf", "31", "-pix_fmt", "yuv420p", "-profile:v", "high",
                        "-c:a", "aac", "-b:a", "72k", "-ac", "2", "-ar", "44100",
                        "-movflags", "+faststart", dst], check=True)
    return dst


# A representative frame per trailer, so a card reads as its style before anyone
# presses play. Chosen by hand on the beat where that style's type has landed.
POSTER_AT = {"style-1.mp4": 1.0, "style-2.mp4": 1.0, "style-3.mp4": 2.0,
             "style-4.mp4": 3.0, "style-5.mp4": 2.0,
             "ep02-style-2b.mp4": 0.95, "ep02-style-6.mp4": 8.60,
             "ep02-style-7.mp4": 0.95, "ep02-style-8.mp4": 1.90,
             "ep02-style-9.mp4": 0.95}


def poster(src):
    """Cache a JPEG poster frame for one trailer."""
    os.makedirs(PREV, exist_ok=True)
    base = os.path.basename(src)
    dst = os.path.join(PREV, base.replace(".mp4", ".jpg"))
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.2f" % POSTER_AT[base],
                        "-i", src, "-frames:v", "1", "-vf", "scale=960:-2",
                        "-q:v", "6", dst], check=True)
    return dst


def data_uri(path, mime):
    with open(path, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode())


def font_face(name, weight):
    src = os.path.join(FONTS, name)
    if not os.path.exists(src):
        return ""
    return ("@font-face{font-family:Inter;font-style:normal;font-weight:%d;"
            "font-display:block;src:url(%s) format('truetype')}"
            % (weight, data_uri(src, "font/ttf")))


CSS_EXTRA = """
/* The page commits to one dark world on purpose: these are graded films and a
   light ground would sit brighter than half the frames in the set. Both theme
   hooks are pinned to the same tokens so the viewer's toggle cannot wash it out. */
:root,:root[data-theme="dark"],:root[data-theme="light"]{
  --ink:#0B0B0C; --panel:#131417; --panel2:#191A1E; --line:#26282E;
  --text:#E9E6DF; --dim:#9A968E; --em:#3AAE5C; --tan:#D8B26A; --red:#C0392B;
  color-scheme:dark;
}
html,body{background:#0B0B0C}
body{font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}
table.cmp td,table.mx td,.stat .v{font-variant-numeric:tabular-nums}
button.guide:focus-visible,.tabs button:focus-visible,.sheet .close:focus-visible{
  outline:2px solid var(--em);outline-offset:2px}
video:focus-visible{outline:2px solid var(--em);outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
.note-embed{margin:0;padding:0 20px 16px;color:var(--dim);font-size:13px}
"""


def cards_and_modals(entries, src_for, guide_for, prefix):
    cards, modals = [], []
    for key, name, desc, extra, hf in entries:
        s = measure.stats(os.path.join(OUT, os.path.basename(src_for(key))))
        master = os.path.join(OUT, os.path.basename(src_for(key)))
        uri = data_uri(preview_encode(master), "video/mp4")
        pos = data_uri(poster(master), "image/jpeg")
        cards.append("""
      <article class="card">
        <video src="%s" poster="%s" controls preload="none" playsinline></video>
        <div class="body">
          <div class="no">Style %s</div>
          <h3>%s</h3>
          <p class="desc">%s</p>
          <div class="stats">
            <div class="stat"><span class="k">Shots</span><span class="v em">%d</span></div>
            <div class="stat"><span class="k">Longest hold</span><span class="v">%.2fs</span></div>
            <div class="stat"><span class="k">Avg cut</span><span class="v">%.2fs</span></div>
            <div class="stat"><span class="k">Asset cost</span><span class="v">%s</span></div>
          </div>
          <button class="guide" onclick="openGuide('%s%s')">Style guide</button>
        </div>
      </article>""" % (uri, pos, str(key).upper(), name, desc, s["shots"],
                       s["longest_hold"], s["avg_interval"],
                       "Free" if hf == 0 else "%d gen" % hf, prefix, key))
        with open(guide_for(key)) as fh:
            body = md_to_html(fh.read())
        modals.append("""
    <div class="modal" id="m%s%s">
      <div class="sheet">
        <div class="head">
          <strong>Style guide %s</strong>
          <button class="close" onclick="closeGuide('%s%s')" aria-label="Close">&times;</button>
        </div>
        <div class="doc">%s</div>
      </div>
    </div>""" % (prefix, key, str(key).upper(), prefix, key, body))
    return cards, modals


def build(dst):
    ep5 = {n: measure.stats(os.path.join(OUT, "style-%d.mp4" % n))
           for n, _, _, _, _ in EP5_STYLES}
    ep2 = {k: measure.stats(os.path.join(OUT, "ep02-style-%s.mp4" % k))
           for k, _, _, _, _ in EP2_STYLES}
    mx5, mx2 = max(s["shots"] for s in ep5.values()), max(s["shots"] for s in ep2.values())

    rows5 = ["".join([
        '<tr><td class="name">%d &middot; %s</td><td><span class="n">%d</span></td>'
        '<td><span class="bar"><i style="width:%.1f%%"></i></span></td>'
        '<td>%.2fs</td><td>%.2fs</td><td class="%s">%s</td><td>%.1f MB</td></tr>'
        % (n, name, ep5[n]["shots"], 100.0 * ep5[n]["shots"] / mx5,
           ep5[n]["longest_hold"], ep5[n]["avg_interval"],
           "free" if hf == 0 else "", "free" if hf == 0 else "%d assets" % hf,
           ep5[n]["size_mb"])]) for n, name, _, hf, _ in EP5_STYLES]

    rows2, mrows = [], []
    for key, name, desc, mx, hf in EP2_STYLES:
        s = ep2[key]
        rows2.append(
            '<tr><td class="name">%s &middot; %s</td><td><span class="n">%d</span></td>'
            '<td><span class="bar"><i style="width:%.1f%%"></i></span></td>'
            '<td>%.2fs</td><td>%.2fs</td><td class="free">free</td><td>%.1f MB</td></tr>'
            % (str(key).upper(), name, s["shots"], 100.0 * s["shots"] / mx2,
               s["longest_hold"], s["avg_interval"], s["size_mb"]))
        mrows.append('<tr><td class="name">%s &middot; %s</td><td>%s</td><td>%s</td>'
                     '<td>%s</td><td>%s</td></tr>'
                     % ((str(key).upper(), name) + tuple(mx)))

    cards5, modals5 = cards_and_modals(
        [(n, name, desc, None, hf) for n, name, desc, hf, _ in EP5_STYLES],
        lambda k: "style-%d.mp4" % k,
        lambda k: os.path.join(GUIDES, "style-%d.md" % k), "")
    cards2, modals2 = cards_and_modals(
        EP2_STYLES, lambda k: "ep02-style-%s.mp4" % k,
        lambda k: os.path.join(GUIDES, "style-%s.md" % k), "e2-")

    faces = (font_face("inter-regular.ttf", 400) + font_face("inter-semibold.ttf", 600)
             + font_face("inter-bold.ttf", 700))

    page = """<title>UNCLAIMED &middot; style tests</title>
<style>%s
%s
%s</style>
<div class="wrap">
  <header class="top">
    <div class="kicker">Unclaimed &middot; style tests</div>
    <h1>Visual styles, one script each</h1>
    <p class="sub">Two style tests. Every figure and hold below is <b>measured</b> from
    the finished file with ffmpeg scene detection at a threshold of 0.1, never
    estimated. Within an episode the narration, voiceover file, music bed and runtime
    are identical across styles, so only the grade, the type and the cutting differ.</p>
  </header>

  <div class="tabs" role="tablist">
    <button data-ep="ep5" aria-selected="true" onclick="showEp('ep5')">Episode 5 &middot; Home equity</button>
    <button data-ep="ep2" aria-selected="false" onclick="showEp('ep2')">Episode 2 &middot; Unclaimed property</button>
  </div>

  <section class="ep" id="ep5" data-active="1">
    <p class="sub">Episode 5, <b>Tyler v. Hennepin County</b>. Same narration, same
    voiceover file, same music bed, same 25 second runtime in all five. Total
    generation spend across all five was <b>54 Higgsfield credits</b> for a shared pool
    of 16 assets.</p>
    <section class="compare">
      <h2>The tradeoff at a glance</h2>
      <table class="cmp"><thead><tr>
        <th>Style</th><th>Shots</th><th>Relative pace</th><th>Longest hold</th>
        <th>Avg cut</th><th>Generation cost</th><th>File</th>
      </tr></thead><tbody>%s</tbody></table>
    </section>
    <div class="grid">%s
    </div>
  </section>

  <section class="ep" id="ep2" data-active="0">
    <p class="sub">Episode 2, <b>How to Check if a State Is Holding Money in Your
    Name</b>. Five trailers at 9.60 seconds, one voiceover generation and one music bed
    shared by all five. Style 2B is the two mode revision of Style 2, built here to its
    slam half only because a trailer this short has no room to alternate. Generation
    spend on the finished films: <b>none</b>.</p>
    <section class="matrix">
      <h2>Differentiation matrix</h2>
      <p class="note">Written before the build. The Episode 5 set failed because two
      styles collapsed into each other, so every style here was assigned four axis
      values first and the set checked for collisions. No pair shares more than one
      axis value, against a limit of two.</p>
      <table class="mx"><thead><tr>
        <th>Style</th><th>A Source</th><th>B Ground</th><th>C Subject</th><th>D Tempo</th>
      </tr></thead><tbody>%s</tbody></table>
    </section>
    <section class="compare">
      <h2>The tradeoff at a glance</h2>
      <table class="cmp"><thead><tr>
        <th>Style</th><th>Shots</th><th>Relative pace</th><th>Longest hold</th>
        <th>Avg cut</th><th>Generation cost</th><th>File</th>
      </tr></thead><tbody>%s</tbody></table>
    </section>
    <div class="grid">%s
    </div>
  </section>

  <footer>
    Episode 5 built by <code>build.py</code>, Episode 2 by <code>build-ep02.py</code>,
    each from one shared asset pool. Rhythm measured by <code>measure.py</code> and
    <code>measure-ep02.py</code>, and the shots, holds and cuts above are those
    measurements, not the edit list. The <b>File</b> column is the size of the master
    in <code>out/</code>; the players on this page carry 960 wide preview encodes so the
    whole set fits in one file. Documents and web pages on screen are facsimiles built
    in HTML for these tests. Every field not stated in the narration is redacted rather
    than invented, no real record is reproduced, and no identifiable person appears.
  </footer>
</div>
%s%s
<script>%s</script>
""" % (_gi.CSS, CSS_EXTRA, faces, "\n".join(rows5), "".join(cards5),
       "\n".join(mrows), "\n".join(rows2), "".join(cards2),
       "".join(modals5), "".join(modals2), _gi.JS)

    with open(dst, "w") as fh:
        fh.write(page)
    print("wrote %s (%.2f MB)" % (dst, os.path.getsize(dst) / 1048576.0))
    return dst


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "preview.html"))
