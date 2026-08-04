#!/usr/bin/env python3
"""Build style-tests/index.html: two episode tabs, measured stats, guides as modals.

Episode 5 is the original five style test. Episode 2 adds the Style 2B revision
and four new styles, with the differentiation matrix at the top of its tab.

Self contained. No frameworks, no build step, no CDN except Google Fonts. The
guide markdown is converted to HTML here, at build time, and inlined, so nothing
is fetched at runtime. Every stat is measured from the finished file, never
estimated.
"""
import html
import os
import re

import measure

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
GUIDES = os.path.join(HERE, "guides")

EP5_STYLES = [
    (1, "Redacted Document",
     "A document fills the frame, dimmed; one line burns emerald as each fact lands.",
     0, "no generation"),
    (2, "Kinetic Type Over Footage",
     "Bold condensed type slams on the beat over heavily graded footage.",
     14, "14 of the shared pool"),
    (3, "Annotated Screen",
     "A real government page marked up live: cursor, circles, arrows, underlines.",
     0, "no generation"),
    (4, "High Speed Cut",
     "A visual change every half second in a serious register. Speed is the effect.",
     16, "16 of the shared pool"),
    (5, "Case File",
     "A manila folder opens and the evidence accumulates under one side light.",
     3, "3 of the shared pool"),
]

# Episode 2. Matrix axes are (A source, B ground, C subject, D tempo); no two
# styles share more than one axis value, against a limit of two.
EP2_STYLES = [
    ("2b", "Kinetic Type, Slam Half",
     "Style 2 with a second gear. The trailer shows the slam half only.",
     ("generated footage", "near black", "type", "fast slam"), 0),
    ("6", "Screen Native",
     "A facsimile state portal doing a real search: cursor, field, results, one row.",
     ("real screen recording", "paper white", "interface", "steady procedural"), 0),
    ("7", "Tabletop Overhead",
     "Warm light on a desk, every figure arriving on a printed sheet.",
     ("photographed objects", "warm light", "physical object", "slow reveal"), 0),
    ("8", "Data First",
     "The chart is the protagonist: a bar climbs, a dot field resolves.",
     ("vector data graphics", "paper white", "chart", "medium build"), 0),
    ("9", "Archival Print",
     "Halftone photographs cut into cream, heavy type, ink out of register.",
     ("archival collage", "mid grey to cream", "texture", "medium build"), 0),
]


# ------------------------------------------------------------------ markdown to html
def md_to_html(src):
    out = []
    lines = src.split("\n")
    i = 0
    in_list = False

    def inline(t):
        t = html.escape(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        return t

    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()

        if not stripped:
            if in_list:
                out.append("</ul>")
                in_list = False
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue

        # table: header row, separator, body rows
        if stripped.startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            if in_list:
                out.append("</ul>")
                in_list = False
            head = [c.strip() for c in stripped.strip("|").split("|")]
            out.append("<table><thead><tr>" +
                       "".join("<th>%s</th>" % inline(c) for c in head) +
                       "</tr></thead><tbody>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue

        def consume_item(text_start):
            """Collect a list item plus any wrapped continuation lines."""
            parts = [text_start]
            j = i + 1
            while j < len(lines) and lines[j].strip() and \
                    not re.match(r"^(#{1,4}\s|[-*]\s|\d+\.\s|\|)", lines[j].strip()):
                parts.append(lines[j].strip())
                j += 1
            return " ".join(parts), j

        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            text, i = consume_item(m.group(1))
            out.append("<li>%s</li>" % inline(text))
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            if not in_list:
                out.append("<ol>")
                in_list = "ol"
            text, i = consume_item(m.group(2))
            out.append("<li>%s</li>" % inline(text))
            continue

        # paragraph, joining wrapped lines
        buf = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and \
                not re.match(r"^(#{1,4}\s|[-*]\s|\d+\.\s|\|)", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        if in_list:
            out.append("</ol>" if in_list == "ol" else "</ul>")
            in_list = False
        out.append("<p>%s</p>" % inline(" ".join(buf)))

    if in_list:
        out.append("</ol>" if in_list == "ol" else "</ul>")
    return "\n".join(out).replace("</ul>\n<ol>", "</ul><ol>")


CSS = """
:root{
  --ink:#0B0B0C; --panel:#131417; --panel2:#191A1E; --line:#26282E;
  --text:#E9E6DF; --dim:#9A968E; --em:#3AAE5C; --tan:#D8B26A; --red:#C0392B;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--ink); color:var(--text);
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; line-height:1.55;
}
.wrap{max-width:1360px;margin:0 auto;padding:56px 24px 96px}
header.top{border-bottom:1px solid var(--line);padding-bottom:28px;margin-bottom:36px}
.kicker{font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:var(--em);
  font-weight:600;margin-bottom:14px}
h1{font-size:clamp(28px,4vw,44px);line-height:1.12;margin:0 0 12px;font-weight:800;
  letter-spacing:-.02em}
.sub{color:var(--dim);max-width:70ch;font-size:15.5px;margin:0}
.sub b{color:var(--text);font-weight:600}

.compare{margin:0 0 44px;border:1px solid var(--line);border-radius:12px;
  background:var(--panel);overflow-x:auto}
.compare h2{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--dim);
  margin:0;padding:16px 20px 12px;border-bottom:1px solid var(--line);font-weight:600}
table.cmp{width:100%;border-collapse:collapse;font-size:14px;min-width:760px}
table.cmp th{text-align:left;padding:11px 20px;font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--dim);font-weight:600;border-bottom:1px solid var(--line)}
table.cmp td{padding:13px 20px;border-bottom:1px solid #1E2025;font-variant-numeric:tabular-nums}
table.cmp tr:last-child td{border-bottom:0}
table.cmp td.name{font-weight:600}
table.cmp td .n{color:var(--em);font-weight:700}
table.cmp td .free{color:var(--tan)}
.bar{display:block;height:7px;background:#22242A;border-radius:4px;position:relative;
  min-width:110px;width:100%;max-width:190px}
.bar i{position:absolute;top:0;bottom:0;left:0;background:var(--em);border-radius:4px;
  display:block}

.grid{display:grid;gap:22px;grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  overflow:hidden;display:flex;flex-direction:column}
.card video{width:100%;display:block;background:#000;aspect-ratio:16/9}
.card .body{padding:18px 20px 20px;display:flex;flex-direction:column;gap:12px;flex:1}
.card .no{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--em);
  font-weight:700}
.card h3{margin:0;font-size:19px;font-weight:700;letter-spacing:-.01em}
.card .desc{margin:0;color:var(--dim);font-size:14px}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;margin-top:2px;
  border-top:1px solid var(--line);padding-top:14px}
.stat{display:flex;flex-direction:column;gap:2px}
.stat .k{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:#7C7A74}
.stat .v{font-size:15px;font-weight:700;font-variant-numeric:tabular-nums}
.stat .v.em{color:var(--em)}
button.guide{margin-top:auto;background:transparent;color:var(--text);
  border:1px solid #34373F;border-radius:8px;padding:11px 16px;font:inherit;font-size:14px;
  font-weight:600;cursor:pointer;transition:.15s}
button.guide:hover{border-color:var(--em);color:var(--em)}

.modal{position:fixed;inset:0;background:rgba(6,6,7,.82);display:none;z-index:50;
  padding:32px 18px;overflow-y:auto;backdrop-filter:blur(3px)}
.modal[open]{display:block}
.sheet{max-width:760px;margin:0 auto;background:var(--panel2);border:1px solid var(--line);
  border-radius:14px;padding:12px 0 0}
.sheet .head{display:flex;align-items:center;justify-content:space-between;gap:16px;
  padding:10px 26px 16px;border-bottom:1px solid var(--line);position:sticky;top:0;
  background:var(--panel2);border-radius:14px 14px 0 0}
.sheet .head strong{font-size:13px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--dim);font-weight:600}
.sheet .close{background:transparent;border:1px solid #34373F;color:var(--text);
  border-radius:7px;width:32px;height:32px;font-size:17px;cursor:pointer;line-height:1}
.sheet .close:hover{border-color:var(--em);color:var(--em)}
.doc{padding:6px 26px 30px;font-size:14.5px}
.doc h1{font-size:24px;margin:18px 0 6px;letter-spacing:-.01em}
.doc h2{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--em);
  margin:26px 0 8px;font-weight:700}
.doc p{margin:0 0 12px;color:#DCD8D0}
.doc ul,.doc ol{margin:0 0 14px;padding-left:22px;color:#DCD8D0}
.doc li{margin-bottom:6px}
.doc code{background:#0E0F12;border:1px solid var(--line);border-radius:4px;
  padding:1px 6px;font-size:12.5px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
  color:var(--tan)}
.doc table{width:100%;border-collapse:collapse;margin:0 0 16px;font-size:13.5px;
  display:block;overflow-x:auto}
.doc th{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);
  font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--dim)}
.doc td{padding:9px 10px;border-bottom:1px solid #1E2025;vertical-align:top;color:#DCD8D0}
footer{margin-top:52px;padding-top:22px;border-top:1px solid var(--line);
  color:#77756F;font-size:13px}
footer code{color:var(--tan)}
@media (max-width:520px){.stats{grid-template-columns:1fr}}

/* episode switcher */
.tabs{display:flex;gap:8px;margin:0 0 30px;border-bottom:1px solid var(--line);
  padding-bottom:0}
.tabs button{background:transparent;border:0;border-bottom:2px solid transparent;
  color:var(--dim);font:inherit;font-size:14.5px;font-weight:600;cursor:pointer;
  padding:12px 16px;transition:.15s}
.tabs button:hover{color:var(--text)}
.tabs button[aria-selected="true"]{color:var(--em);border-bottom-color:var(--em)}
.ep{display:none}
.ep[data-active="1"]{display:block}
.ep .sub{margin:0 0 30px}

/* differentiation matrix */
.matrix{margin:0 0 34px;border:1px solid var(--line);border-radius:12px;
  background:var(--panel);overflow-x:auto}
.matrix h2{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--dim);
  margin:0;padding:16px 20px 6px;font-weight:600}
.matrix p.note{margin:0;padding:0 20px 14px;color:var(--dim);font-size:13.5px;
  border-bottom:1px solid var(--line);max-width:none}
table.mx{width:100%;border-collapse:collapse;font-size:13.5px;min-width:820px}
table.mx th{text-align:left;padding:11px 20px;font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--dim);font-weight:600;border-bottom:1px solid var(--line)}
table.mx td{padding:12px 20px;border-bottom:1px solid #1E2025;color:#DCD8D0}
table.mx tr:last-child td{border-bottom:0}
table.mx td.name{font-weight:600;color:var(--text);white-space:nowrap}
"""

JS = """
function showEp(id){
  document.querySelectorAll('.ep').forEach(function(s){
    s.setAttribute('data-active', s.id === id ? '1' : '0');
  });
  document.querySelectorAll('.tabs button').forEach(function(b){
    b.setAttribute('aria-selected', b.dataset.ep === id ? 'true' : 'false');
  });
  document.querySelectorAll('.ep video').forEach(function(v){ v.pause(); });
  // the hash deliberately does not match a section id: '#ep2' would make the
  // browser scroll to that element and hide the header on a deep link
  if (history.replaceState) history.replaceState(null, '', '#tab-' + id);
}
window.addEventListener('DOMContentLoaded', function(){
  var h = (location.hash || '').replace('#tab-','').replace('#','');
  if (h === 'ep5' || h === 'ep2') showEp(h);
});
function openGuide(n){
  document.getElementById('m'+n).setAttribute('open','');
  document.body.style.overflow='hidden';
}
function closeGuide(n){
  document.getElementById('m'+n).removeAttribute('open');
  document.body.style.overflow='';
}
document.addEventListener('click',function(e){
  if(e.target.classList.contains('modal')){
    e.target.removeAttribute('open'); document.body.style.overflow='';
  }
});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){
    document.querySelectorAll('.modal[open]').forEach(function(m){m.removeAttribute('open')});
    document.body.style.overflow='';
  }
});
"""


def _stats_for(paths):
    return {k: measure.stats(p) for k, p in paths.items()}


def _cards_and_modals(entries, path_for, guide_for, prefix):
    """One card and one guide modal per style. Stats are measured, never typed."""
    cards, modals = [], []
    for key, name, desc, extra, hf in entries:
        s = measure.stats(path_for(key))
        cards.append("""
      <article class="card">
        <video src="%s" controls preload="metadata" playsinline></video>
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
      </article>""" % (path_for(key), html.escape(str(key).upper()), html.escape(name),
                       html.escape(desc), s["shots"], s["longest_hold"],
                       s["avg_interval"], "Free" if hf == 0 else "%d gen" % hf,
                       prefix, key))
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
    </div>""" % (prefix, key, html.escape(str(key).upper()), prefix, key, body))
    return cards, modals


def build():
    # ---------------------------------------------------------------- episode 5
    ep5_stats = _stats_for({n: os.path.join(OUT, "style-%d.mp4" % n)
                            for n, _, _, _, _ in EP5_STYLES})
    max_shots5 = max(s["shots"] for s in ep5_stats.values())
    rows5 = []
    for n, name, desc, hf, hf_note in EP5_STYLES:
        s = ep5_stats[n]
        rows5.append(
            '<tr><td class="name">%d &middot; %s</td>'
            '<td><span class="n">%d</span></td>'
            '<td><span class="bar"><i style="width:%.1f%%"></i></span></td>'
            '<td>%.2fs</td><td>%.2fs</td>'
            '<td class="%s">%s</td><td>%.1f MB</td></tr>'
            % (n, html.escape(name), s["shots"], 100.0 * s["shots"] / max_shots5,
               s["longest_hold"], s["avg_interval"], "free" if hf == 0 else "",
               "free" if hf == 0 else "%d assets" % hf, s["size_mb"]))

    cards5, modals5 = _cards_and_modals(
        [(n, name, desc, None, hf) for n, name, desc, hf, _ in EP5_STYLES],
        lambda k: "out/style-%d.mp4" % k,
        lambda k: os.path.join(GUIDES, "style-%d.md" % k), "")

    # ---------------------------------------------------------------- episode 2
    ep2_stats = _stats_for({k: os.path.join(OUT, "ep02-style-%s.mp4" % k)
                            for k, _, _, _, _ in EP2_STYLES})
    max_shots2 = max(s["shots"] for s in ep2_stats.values())
    rows2, mrows = [], []
    for key, name, desc, mx, hf in EP2_STYLES:
        s = ep2_stats[key]
        rows2.append(
            '<tr><td class="name">%s &middot; %s</td>'
            '<td><span class="n">%d</span></td>'
            '<td><span class="bar"><i style="width:%.1f%%"></i></span></td>'
            '<td>%.2fs</td><td>%.2fs</td>'
            '<td class="free">free</td><td>%.1f MB</td></tr>'
            % (html.escape(str(key).upper()), html.escape(name), s["shots"],
               100.0 * s["shots"] / max_shots2, s["longest_hold"],
               s["avg_interval"], s["size_mb"]))
        mrows.append(
            '<tr><td class="name">%s &middot; %s</td><td>%s</td><td>%s</td>'
            '<td>%s</td><td>%s</td></tr>'
            % ((html.escape(str(key).upper()), html.escape(name)) +
               tuple(html.escape(v) for v in mx)))

    cards2, modals2 = _cards_and_modals(
        EP2_STYLES,
        lambda k: "out/ep02-style-%s.mp4" % k,
        lambda k: os.path.join(GUIDES, "style-%s.md" % k), "e2-")

    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UNCLAIMED &middot; style tests</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
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
      <table class="cmp">
        <thead><tr>
          <th>Style</th><th>Shots</th><th>Relative pace</th><th>Longest hold</th>
          <th>Avg cut</th><th>Generation cost</th><th>File</th>
        </tr></thead>
        <tbody>%s</tbody>
      </table>
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
      <table class="mx">
        <thead><tr>
          <th>Style</th><th>A Source</th><th>B Ground</th><th>C Subject</th><th>D Tempo</th>
        </tr></thead>
        <tbody>%s</tbody>
      </table>
    </section>

    <section class="compare">
      <h2>The tradeoff at a glance</h2>
      <table class="cmp">
        <thead><tr>
          <th>Style</th><th>Shots</th><th>Relative pace</th><th>Longest hold</th>
          <th>Avg cut</th><th>Generation cost</th><th>File</th>
        </tr></thead>
        <tbody>%s</tbody>
      </table>
    </section>

    <div class="grid">%s
    </div>
  </section>

  <footer>
    Episode 5 built by <code>build.py</code>, Episode 2 by <code>build-ep02.py</code>,
    each from one shared asset pool. Rhythm measured by <code>measure.py</code> and
    <code>measure-ep02.py</code>. Documents and web pages on screen are facsimiles built
    in HTML for these tests. Every field not stated in the narration is redacted rather
    than invented, no real record is reproduced, and no identifiable person appears.
  </footer>
</div>
%s%s
<script>%s</script>
</body>
</html>
""" % (CSS, "\n".join(rows5), "".join(cards5), "\n".join(mrows),
       "\n".join(rows2), "".join(cards2), "".join(modals5), "".join(modals2), JS)

    dst = os.path.join(HERE, "index.html")
    with open(dst, "w") as fh:
        fh.write(page)
    print("wrote %s (%.1f KB)" % (dst, os.path.getsize(dst) / 1024.0))
    return dst


if __name__ == "__main__":
    build()
