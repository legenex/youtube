#!/usr/bin/env python3
"""Build style-tests/index.html: five cards, measured stats, guides inlined as modals.

Self contained. No frameworks, no build step, no CDN except Google Fonts. The
guide markdown is converted to HTML here, at build time, and inlined, so nothing
is fetched at runtime.
"""
import html
import os
import re

import measure

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
GUIDES = os.path.join(HERE, "guides")

STYLES = [
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
"""

JS = """
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


def build():
    stats = {}
    for n, _, _, _, _ in STYLES:
        p = os.path.join(OUT, "style-%d.mp4" % n)
        stats[n] = measure.stats(p)

    max_shots = max(s["shots"] for s in stats.values())

    rows = []
    for n, name, desc, hf, hf_note in STYLES:
        s = stats[n]
        pct = 100.0 * s["shots"] / max_shots
        cost = "free" if hf == 0 else "%d assets" % hf
        rows.append(
            '<tr><td class="name">%d &middot; %s</td>'
            '<td><span class="n">%d</span></td>'
            '<td><span class="bar"><i style="width:%.1f%%"></i></span></td>'
            '<td>%.2fs</td><td>%.2fs</td>'
            '<td class="%s">%s</td><td>%.1f MB</td></tr>'
            % (n, html.escape(name), s["shots"], pct, s["longest_hold"],
               s["avg_interval"], "free" if hf == 0 else "", cost, s["size_mb"]))

    cards, modals = [], []
    for n, name, desc, hf, hf_note in STYLES:
        s = stats[n]
        cards.append("""
      <article class="card">
        <video src="out/style-%d.mp4" controls preload="metadata" playsinline></video>
        <div class="body">
          <div class="no">Style %d</div>
          <h3>%s</h3>
          <p class="desc">%s</p>
          <div class="stats">
            <div class="stat"><span class="k">Shots</span><span class="v em">%d</span></div>
            <div class="stat"><span class="k">Longest hold</span><span class="v">%.2fs</span></div>
            <div class="stat"><span class="k">Avg cut</span><span class="v">%.2fs</span></div>
            <div class="stat"><span class="k">Asset cost</span><span class="v">%s</span></div>
          </div>
          <button class="guide" onclick="openGuide(%d)">Style guide</button>
        </div>
      </article>""" % (n, n, html.escape(name), html.escape(desc), s["shots"],
                       s["longest_hold"], s["avg_interval"],
                       "Free" if hf == 0 else "%d gen" % hf, n))

        with open(os.path.join(GUIDES, "style-%d.md" % n)) as fh:
            body = md_to_html(fh.read())
        modals.append("""
    <div class="modal" id="m%d">
      <div class="sheet">
        <div class="head">
          <strong>Style guide %d</strong>
          <button class="close" onclick="closeGuide(%d)" aria-label="Close">&times;</button>
        </div>
        <div class="doc">%s</div>
      </div>
    </div>""" % (n, n, n, body))

    total_hf = 16
    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UNCLAIMED &middot; Episode 5 style test</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="kicker">Unclaimed &middot; style test</div>
    <h1>Five visual styles, one script</h1>
    <p class="sub">Episode 5, <b>Tyler v. Hennepin County</b>. Same narration, same
    voiceover file, same music bed, same 25 second runtime in all five. Only the grade,
    the type and the cutting change, so the comparison is fair. Every figure and hold
    below is <b>measured</b> from the finished file with ffmpeg scene detection at a
    threshold of 0.1, not estimated. Total generation spend across all five was
    <b>54 Higgsfield credits</b> for a shared pool of %d assets.</p>
  </header>

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

  <footer>
    Built with one script, <code>build.py</code>, from a shared asset pool. Rhythm
    measured by <code>measure.py</code>. Documents on screen are facsimiles built in
    HTML for this test: they imitate the structure of a court filing and a county
    surplus listing, and every field not stated in the narration is redacted rather
    than invented. No real record is reproduced and no identifiable person appears.
  </footer>
</div>
%s
<script>%s</script>
</body>
</html>
""" % (CSS, total_hf, "\n".join(rows), "".join(cards), "".join(modals), JS)

    dst = os.path.join(HERE, "index.html")
    with open(dst, "w") as fh:
        fh.write(page)
    print("wrote %s (%.1f KB)" % (dst, os.path.getsize(dst) / 1024.0))
    return dst


if __name__ == "__main__":
    build()
