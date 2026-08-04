#!/usr/bin/env python3
"""Assemble five style-test trailers for UNCLAIMED Episode 2 from one shared pool.

    python3 build-ep02.py              # build every style that is missing
    python3 build-ep02.py 2b 7         # build only those styles
    python3 build-ep02.py --force 8    # rebuild even if the output already exists

Styles: 2b (kinetic slam), 6 (screen native), 7 (tabletop overhead),
        8 (data first), 9 (archival print).

Idempotent by design, because this run may resume in a different container:
a style whose output already exists and probes valid is skipped, and every
intermediate (fonts, page screenshots, type cards, graded plates) is cached on
disk by content or by parameter hash.

One voiceover, one music bed, one pool. Only the grade, the type and the cutting
change, so the comparison between styles is fair.

Encode contract: 1280x720, 30fps, H.264 yuv420p, CRF 21, AAC 192k, -14 LUFS,
faststart. FFmpeg only.
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import urlencode

# ----------------------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.join(HERE, "assets", "ep02", "shared")
HTML = os.path.join(EP, "html")
POOL = os.path.join(HERE, "assets", "shared", "gen")        # Episode 5 photographic pool
OVL5 = os.path.join(HERE, "assets", "shared", "overlay")    # Episode 5 overlays (cursor)
WORK = os.path.join(HERE, "work-ep02")
OUT = os.path.join(HERE, "out")
FONTDIR = os.path.join(WORK, "fonts")
CARDS = os.path.join(WORK, "cards")
PAGES = os.path.join(WORK, "pages")
PLATES = os.path.join(WORK, "plates")

CHROME = os.environ.get("CHROME_BIN", "/opt/pw-browsers/chromium")

W, H, FPS = 1280, 720, 30
CW, CH = 1728, 972          # composite canvas: headroom so a push stays sharp
RUNTIME = 9.60

# ----------------------------------------------------------------------------- palette
INK = "0D0D0D"
EMERALD = "3AAE5C"
BONE = "F5F0E3"
TAN = "D8B26A"

# Measured phrase boundaries of assets/ep02/shared/vo.wav, from silencedetect.
# Nothing here is estimated; see build-log.md for the table.
VO = {
    "b1": (0.00, 1.566),    # "Seventy billion dollars."
    "b2": (2.252, 5.196),   # "One in seven Americans has money waiting in their own name."
    "b3": (6.014, 7.338),   # "The money may be unclaimed."
    "b4": (7.781, 9.077),   # "It does not have to stay that way."
}

SHOTS = []
COUNTER = {}


# ----------------------------------------------------------------------------- util
def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write("\n>>> FAILED: %s\n%s\n" % (" ".join(args[:14]), p.stderr[-2500:]))
        raise SystemExit(1)
    return p


# Chromium's new headless mode subtracts the window chrome from the painted
# viewport: --window-size=1280,720 lays out at 1280x720 but only paints the top
# 633 CSS pixels, leaving the bottom 87 blank while the PNG is still full size.
# Anything in the lower eighth of the frame silently disappears. Ask for a
# window that much taller and crop back, so a card at y=628 actually renders.
CHROME_CHROME_H = 87


def shoot(dst, url, size=(W, H), scale=2, transparent=False):
    """Screenshot a local page with headless Chrome. Cached by destination path."""
    if os.path.exists(dst):
        return dst
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    raw = dst + ".raw.png"
    args = [CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=%s" % scale,
            "--window-size=%d,%d" % (size[0], size[1] + CHROME_CHROME_H),
            "--virtual-time-budget=2500", "--screenshot=" + raw, url]
    if transparent:
        args.insert(5, "--default-background-color=00000000")
    p = subprocess.run(args, capture_output=True, text=True)
    if not os.path.exists(raw):
        sys.stderr.write("screenshot failed: %s\n%s\n" % (dst, p.stderr[-900:]))
        raise SystemExit(1)
    run(["ffmpeg", "-y", "-v", "error", "-i", raw,
         "-vf", "crop=%d:%d:0:0" % (size[0] * scale, size[1] * scale), dst])
    os.remove(raw)
    return dst


def page(name, **params):
    """Render one state of a shared HTML page. Cached by parameter hash."""
    q = urlencode(params)
    key = "%s-%s" % (name, hashlib.sha1(q.encode()).hexdigest()[:14])
    dst = os.path.join(PAGES, key + ".png")
    return shoot(dst, "file://" + os.path.join(HTML, name + ".html") + "?" + q)


def card(**params):
    """Full-frame transparent type card. Cached by parameter hash."""
    q = urlencode(params)
    key = hashlib.sha1(q.encode()).hexdigest()[:16]
    dst = os.path.join(CARDS, key + ".png")
    return shoot(dst, "file://" + os.path.join(HTML, "type.html") + "?" + q, transparent=True)


def elem(name, **params):
    """Transparent element from print.html or paper.html. Cached by parameter hash."""
    q = urlencode(params)
    key = "%s-%s" % (name, hashlib.sha1(q.encode()).hexdigest()[:14])
    dst = os.path.join(CARDS, key + ".png")
    return shoot(dst, "file://" + os.path.join(HTML, name + ".html") + "?" + q, transparent=True)


def drift(z0, z1, dur, dx=0.0, dy=0.0):
    n = max(1, int(round(dur * FPS)))
    z = "%.5f+(%.5f)*on/%d" % (z0, z1 - z0, n)
    xe = "iw/2-(iw/zoom/2)+(%.4f)*iw*on/%d" % (dx, n)
    ye = "ih/2-(ih/zoom/2)+(%.4f)*ih*on/%d" % (dy, n)
    return "zoompan=z='%s':x='%s':y='%s':d=1:fps=%d:s=%dx%d" % (z, xe, ye, FPS, W, H)


def img_in(path, dur):
    return ["-loop", "1", "-framerate", str(FPS), "-t", "%.4f" % (dur + 0.25), "-i", path]


def vid_in(path, ss, dur):
    return ["-ss", "%.3f" % ss, "-t", "%.4f" % (dur + 0.25), "-i", path]


def color_in(col, dur):
    return ["-f", "lavfi", "-t", "%.4f" % (dur + 0.25),
            "-i", "color=c=0x%s:s=%dx%d:r=%d" % (col, W, H, FPS)]


def render(style, filters, dur, inputs, label=""):
    idx = COUNTER.get(style, 0)
    COUNTER[style] = idx + 1
    d = os.path.join(WORK, "s%s" % style)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "shot-%03d.mp4" % idx)
    args = ["ffmpeg", "-y", "-v", "error"]
    for i in inputs:
        args += i
    args += ["-filter_complex", filters, "-map", "[v]", "-t", "%.4f" % dur,
             "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
             "-pix_fmt", "yuv420p", "-an", path]
    run(args)
    SHOTS.append((style, idx, path, dur, label))
    return path


def overlay_cards(f, inputs, base, cards, dur):
    """Composite card specs onto `base`. Each spec may slide, slam or just enable."""
    last = base
    for i, spec in enumerate(cards):
        inputs.append(img_in(spec["png"], dur))
        n = len(inputs) - 1
        tag = "cd%s%d" % (base, i)
        f.append("[%d:v]scale=%d:%d,format=rgba[%s]" % (n, W, H, tag))
        t0 = spec.get("t0", 0.0)
        x, y = "0", "0"
        if spec.get("slam"):
            d = spec["slam"]
            y = "0-max(0\\,%d-(t-%.3f)*%d)" % (d, t0, int(d * FPS / 2.5))
        if spec.get("slide"):
            # travel from dx,dy to rest over `sd` seconds, linear, no fade
            dx, dy, sd = spec["slide"]
            k = "min(1\\,max(0\\,(t-%.3f)/%.3f))" % (t0, sd)
            x = "(%d)*(1-%s)" % (dx, k)
            y = "(%d)*(1-%s)" % (dy, k)
        en = ":enable='%s'" % spec["enable"] if spec.get("enable") else (
            ":enable='gte(t,%.3f)'" % t0 if t0 > 0 else "")
        nxt = "ov%s%d" % (base, i)
        f.append("[%s][%s]overlay=x='%s':y='%s'%s[%s]" % (last, tag, x, y, en, nxt))
        last = nxt
    return last


def timeline(pairs, total=RUNTIME):
    out = []
    for i, (t, payload) in enumerate(pairs):
        end = pairs[i + 1][0] if i + 1 < len(pairs) else total
        out.append((t, round(end - t, 4), payload))
    return out


def reveal_cards(stages, t0, step, **style):
    """Redaction blocks resolve into the real figure, then lock.

    No intermediate figure is ever rendered, which is a hard channel rule.
    """
    out = []
    for i, s in enumerate(stages[:-1]):
        a, b = t0 + i * step, t0 + (i + 1) * step
        out.append({"png": card(t=s, **style),
                    "enable": "between(t,%.3f,%.3f)" % (a, b), "t0": a})
    lock = t0 + (len(stages) - 1) * step
    out.append({"png": card(t=stages[-1], **style), "enable": "gte(t,%.3f)" % lock, "t0": lock})
    return out


def billion_stages():
    """'$70 BILLION' arriving out of redaction. Never shows a wrong number."""
    return ["${2} {7}", "$7{1} {7}", "$70 {7}", "$70 BILLION"]


def one_in_seven_stages():
    """'1 IN 7' arriving out of redaction."""
    return ["{1} IN {1}", "1 IN {1}", "1 IN 7"]


# ----------------------------------------------------------------------------- prep
def prep():
    for p in (WORK, OUT, FONTDIR, CARDS, PAGES, PLATES):
        os.makedirs(p, exist_ok=True)
    need = ["anton.ttf", "publicsans.ttf", "publicsans-bold.ttf", "plexmono.ttf",
            "plexmono-bold.ttf", "sourceserif.ttf", "dmserif.ttf", "oswald-bold.ttf",
            "inter-regular.ttf", "inter-semibold.ttf", "inter-bold.ttf",
            "archivoblack.ttf", "barlowcond.ttf", "spacemono-bold.ttf"]
    missing = [n for n in need if not os.path.exists(os.path.join(FONTDIR, n))]
    if missing:
        raise SystemExit("missing fonts in %s: %s\nrun fetch-fonts.sh" % (FONTDIR, missing))
    music()


def music():
    """One bed, synthesised locally, reused by all five styles. Costs nothing.

    Envato is search only through the connector in this environment, so no track
    could be licensed or downloaded; see build-log.md.
    """
    dst = os.path.join(EP, "music.wav")
    if os.path.exists(dst):
        return dst
    # three low drones with independent slow tremolo, brown noise air, long fades
    src = (
        "sine=frequency=55:duration=12[a];"
        "sine=frequency=82.5:duration=12[b];"
        "sine=frequency=110:duration=12[c];"
        "anoisesrc=d=12:c=brown:a=0.09[n];"
        "[a]tremolo=f=0.19:d=0.55,volume=0.40[a1];"
        "[b]tremolo=f=0.13:d=0.42,volume=0.24[b1];"
        "[c]tremolo=f=0.27:d=0.35,volume=0.13[c1];"
        "[n]lowpass=f=1600,volume=0.55[n1];"
        "[a1][b1][c1][n1]amix=inputs=4:normalize=0,"
        "lowpass=f=1800,aecho=0.8:0.85:320:0.28,"
        "afade=t=in:st=0:d=2.6,afade=t=out:st=9.4:d=2.6,"
        "aresample=48000[out]"
    )
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex", src, "-map", "[out]", "-t", "12", "-ar", "48000", "-ac", "2", dst])
    return dst


def pool(key):
    """A photographic plate from the Episode 5 shared pool."""
    names = {"mail": "img-03-envelope-mat.png", "vault": "img-11-vault-boxes.png",
             "folders": "img-07-desk-folders.png", "office": "img-06-county-office.png",
             "keys": "img-02-keys-counter.png", "aerial": "img-09-aerial-suburb.png",
             "bedroom": "img-10-bedroom-empty.png", "stamp": "img-12-stamp-macro.png"}
    return os.path.join(POOL, names[key])


def pool_clip(key):
    names = {"desk": "clip-4-desk-papers.mp4", "aerial": "clip-3-aerial-suburb.mp4"}
    return os.path.join(POOL, names[key])


def cropped(key, box, tag):
    """Cache a crop of a pool plate. Used to remove invented text from a frame."""
    dst = os.path.join(PLATES, "%s-%s.png" % (key, tag))
    if not os.path.exists(dst):
        x, y, w, h = box
        run(["ffmpeg", "-y", "-v", "error", "-i", pool(key),
             "-vf", "crop=%d:%d:%d:%d" % (w, h, x, y), dst])
    return dst


def fill(w=CW, h=CH):
    return "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (w, h, w, h)


# grades, one per style
GRADE = {
    # slam mode, exactly as style-2.md specifies
    "2b": "hue=s=0.14,eq=contrast=1.22:brightness=-0.22:saturation=0.62,"
          "colorchannelmixer=rr=0.82:gg=0.88:bb=0.96",
    # warm daylight: lift the tungsten pool plates toward window light
    "7": "eq=contrast=1.04:brightness=0.10:saturation=1.16:gamma=1.18,"
         "colorchannelmixer=rr=1.05:gg=1.00:bb=0.94",
}


# ----------------------------------------------------------------------------- style 2B
def style_2b():
    """KINETIC TYPE, SLAM HALF. Type is the event; footage is a graded bed."""
    S = "2b"
    C = "anton"

    def shot(dur, src, lines=(), ss=None, z=(1.02, 1.14), dx=0.0, dy=0.0,
             block=None, reveal=None):
        if ss is None:
            inputs = [img_in(src, dur)]
            head = "[0:v]%s,%s,%s[bg]" % (fill(), GRADE["2b"], drift(z[0], z[1], dur, dx, dy))
        else:
            inputs = [vid_in(src, ss, dur)]
            head = ("[0:v]fps=%d,%s,%s,%s[bg]"
                    % (FPS, fill(), GRADE["2b"], drift(z[0], z[1], dur, dx, dy)))
        f = [head]
        last = "bg"
        if block:
            col, by, bh, bt = block
            f.append("[%s]drawbox=x='-w+min(1\\,(t-%.2f)/0.20)*(w*2)':y=%d:w=iw:h=%d:"
                     "color=0x%s@0.94:t=fill:enable='gte(t\\,%.2f)'[bk]"
                     % (last, bt, by, bh, col, bt))
            last = "bk"
        cards = []
        for (text, fnt, size, x, y, col, t0, ls) in lines:
            cards.append({"png": card(t=text, f=fnt, s=size, c=col, x=x, y=y, ls=ls,
                                      tt="uppercase", sh="0 4px 18px rgba(0,0,0,.85)"),
                          "t0": t0, "slam": 20})
        if reveal:
            stages, t0, y, size, col = reveal
            cards += reveal_cards(stages, t0, 0.07, f=C, s=size, c=col, x="c", y=y,
                                  sh="0 4px 18px rgba(0,0,0,.85)")
        last = overlay_cards(f, inputs, last, cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "kinetic slam")

    # the vault plate contains a gloved hand holding cash, and no shot in this
    # channel may depict a person; the Episode 5 crop removes it
    vault = cropped("vault", (0, 0, 900, 500), "nohand")

    plan = timeline([
        # "Seventy billion dollars."
        (0.00, dict(src=vault, z=(1.04, 1.16),
                    reveal=(billion_stages(), 0.10, 250, 150, EMERALD),
                    lines=[("held by the states", C, 40, "c", 452, BONE, 0.66, ".09")])),
        # the measured pause after the first sentence gets its own dark plate
        (1.56, dict(src=pool("mail"), z=(1.02, 1.10))),
        # "One in seven Americans ..."
        (2.25, dict(src=pool("aerial"), z=(1.03, 1.15),
                    block=(EMERALD, 300, 9, 0.05),
                    lines=[("one in seven", C, 104, "c", 300, BONE, 0.05, ".01")])),
        (3.30, dict(src=pool("office"), z=(1.03, 1.14),
                    reveal=(one_in_seven_stages(), 0.08, 246, 196, TAN),
                    lines=[("americans", C, 42, "c", 478, BONE, 0.44, ".10")])),
        (4.20, dict(src=pool("folders"), z=(1.02, 1.13), dx=0.03,
                    lines=[("has money waiting", C, 66, 70, 360, BONE, 0.05, ".02")])),
        (5.20, dict(src=pool("keys"), z=(1.02, 1.12),
                    block=(BONE, 252, 7, 0.05),
                    lines=[("in their own name", C, 72, "c", 300, BONE, 0.05, ".02")])),
        # "The money may be unclaimed."
        (6.01, dict(src=pool("mail"), z=(1.03, 1.15),
                    lines=[("the money may be", C, 58, "c", 196, BONE, 0.05, ".05"),
                           ("unclaimed", C, 122, "c", 286, EMERALD, 0.26, "0")])),
        # "It does not have to stay that way."
        (7.78, dict(src=pool("keys"), z=(1.02, 1.13),
                    lines=[("it does not have to", C, 56, "c", 196, BONE, 0.05, ".05"),
                           ("stay that way.", C, 98, "c", 286, EMERALD, 0.28, "0")])),
    ])
    for _, dur, kw in plan:
        shot(dur, **kw)


# ----------------------------------------------------------------------------- style 6
def style_6():
    """SCREEN NATIVE. A real interface doing a real thing. Type is chrome only."""
    S = "6"
    CURSOR = os.path.join(OVL5, "an-cursor.png")

    def shot(dur, states, z=(1.0, 1.0), dx=0.0, dy=0.0, cursor=None, cap=None):
        """states: list of (png, enable_expr or None). First is the base plate.

        Each plate is already framed by the page itself, so there is no crop
        here and nothing can land out of bounds.
        """
        # The plate is already exactly one frame, so it is scaled to W x H and
        # zoompan starts at z=1.0, which means "the whole frame". Any headroom
        # upscale here would silently crop the framing the page just computed.
        inputs = [img_in(states[0][0], dur)]
        f = ["[0:v]scale=%d:%d,%s[bg]" % (W, H, drift(z[0], z[1], dur, dx, dy))]
        last = "bg"
        # later page states swap in on top, hard, never crossfaded
        for i, (png, en) in enumerate(states[1:]):
            inputs.append(img_in(png, dur))
            n = len(inputs) - 1
            t = "st%d" % i
            f.append("[%d:v]scale=%d:%d,%s[%s]"
                     % (n, W, H, drift(z[0], z[1], dur, dx, dy), t))
            nxt = "sw%d" % i
            f.append("[%s][%s]overlay=x=0:y=0:enable='%s'[%s]" % (last, t, en, nxt))
            last = nxt
        cards = []
        if cursor:
            x0, y0, x1, y1, ct = cursor
            inputs.append(img_in(CURSOR, dur))
            n = len(inputs) - 1
            f.append("[%d:v]scale=44:-1,format=rgba[cur]" % n)
            k = "min(1\\,max(0\\,t/%.3f))" % ct
            f.append("[%s][cur]overlay=x='%d+(%d)*%s':y='%d+(%d)*%s'[cs]"
                     % (last, x0, x1 - x0, k, y0, y1 - y0, k))
            last = "cs"
        if cap:
            text, t0 = cap
            cards.append({"png": card(t=text, f="publicb", s=27, c="FFFFFF", x="c", y=628,
                                      bg="14161A", pad="15 30", ls=".01"), "t0": t0})
        if cards:
            last = overlay_cards(f, inputs, last, cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "screen native")

    # Element boxes measured from the rendered page, so a framing is expressed as
    # "centre on this element at this zoom" instead of a hand-guessed crop.
    BOX = {"stats": (0, 167, 1280, 59), "form": (46, 278, 720, 44),
           "go": (673, 278, 93, 44), "table": (46, 365, 1188, 216),
           "hl": (46, 425, 1188, 39), "foot": (0, 607, 1280, 86),
           "page": (0, 0, 1280, 720)}

    def framing(key, zoom, cx=None, cy=None, fit=True, margin=34):
        """Centre the frame on an element. `fit` caps the zoom so the element
        plus a margin still fits, which is what stops a framing from slicing
        through the thing it is meant to be showing."""
        x, y, w, h = BOX[key]
        if fit:
            zoom = min(zoom, 1280.0 / (w + 2 * margin), 720.0 / (h + 2 * margin))
        zoom = max(zoom, 1.0)
        cx = x + w / 2.0 if cx is None else cx
        cy = y + h / 2.0 if cy is None else cy
        vw, vh = 1280.0 / zoom, 720.0 / zoom
        sx = min(max(cx - vw / 2.0, 0.0), max(0.0, 1280.0 - vw))
        sy = min(max(cy - vh / 2.0, 0.0), max(0.0, 760.0 - vh))
        return {"zoom": "%.4f" % zoom, "sx": "%.1f" % sx, "sy": "%.1f" % sy}

    F_WIDE = framing("page", 1.0)
    # a full width band, so fit would cap the zoom to 1.0 and this framing
    # would become identical to F_WIDE; zoom into its centre instead
    F_STATS = framing("stats", 1.55, fit=False)
    F_FORM = framing("form", 1.85)
    # framed so the end of the typed query and the button are both in shot
    F_GO = framing("go", 1.75, cx=410, fit=False)
    F_TABLE = framing("table", 1.50)
    # the row close-up sits on the redacted owner cell and the property type,
    # which is the part of the row that carries meaning
    F_ROW = framing("hl", 2.10, cx=430, fit=False)
    F_FOOT = framing("foot", 1.28)

    # page states, each a cached screenshot of the facsimile at a given framing
    p_stats = page("gov", state="empty", **F_STATS)
    p_focus = page("gov", state="empty", focus="1", **F_WIDE)
    p_typ1 = page("gov", state="empty", focus="1", q="YOUR", **F_FORM)
    p_typ2 = page("gov", state="empty", focus="1", q="YOUR NAME", **F_FORM)
    p_go = page("gov", state="empty", q="YOUR NAME", **F_GO)
    p_load = page("gov", state="loading", q="YOUR NAME", **F_TABLE)
    p_res = page("gov", state="results", q="YOUR NAME", **F_TABLE)
    p_row = page("gov", state="results", q="YOUR NAME", hl="2", **F_ROW)
    p_foot = page("gov", state="results", q="YOUR NAME", hl="2", **F_FOOT)

    plan = timeline([
        # "Seventy billion dollars." the stat strip carries both figures
        (0.00, dict(states=[(p_stats, None)], z=(1.00, 1.05),
                    cursor=(1210, 690, 690, 300, 1.30))),
        (1.56, dict(states=[(p_focus, None)], z=(1.01, 1.05),
                    cursor=(690, 300, 300, 300, 0.52))),
        # "One in seven Americans has money waiting in their own name."
        (2.25, dict(states=[(p_typ1, None), (p_typ2, "gte(t,0.50)")],
                    z=(1.02, 1.06), cursor=(300, 300, 250, 292, 0.40))),
        (3.30, dict(states=[(p_go, None)], z=(1.03, 1.08),
                    cursor=(240, 292, 690, 356, 0.66))),
        (4.35, dict(states=[(p_load, None), (p_res, "gte(t,0.90)")], z=(1.00, 1.04))),
        # "The money may be unclaimed."
        (6.01, dict(states=[(p_row, None)], z=(1.01, 1.07), dy=0.015)),
        # "It does not have to stay that way." small caption, never a slam
        (7.78, dict(states=[(p_foot, None)], z=(1.04, 1.00),
                    cap=("It does not have to stay that way.", 0.16))),
    ])
    for _, dur, kw in plan:
        shot(dur, **kw)


# ----------------------------------------------------------------------------- style 7
def style_7():
    """TABLETOP OVERHEAD. Photographed objects, warm light, paper slides in."""
    S = "7"

    def shot(dur, src, ss=None, z=(1.02, 1.08), dx=0.0, dy=0.0, sheets=()):
        if ss is None:
            inputs = [img_in(src, dur)]
            head = "[0:v]%s,%s,%s[bg]" % (fill(), GRADE["7"], drift(z[0], z[1], dur, dx, dy))
        else:
            inputs = [vid_in(src, ss, dur)]
            head = ("[0:v]fps=%d,%s,%s,%s[bg]"
                    % (FPS, fill(), GRADE["7"], drift(z[0], z[1], dur, dx, dy)))
        f = [head]
        cards = [{"png": s[0], "t0": s[1], "slide": s[2]} for s in sheets]
        last = overlay_cards(f, inputs, "bg", cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "tabletop")

    # printed sheets. Figures arrive on paper, never as a screen graphic.
    s_bill = elem("paper", k="fig", t="$70 BILLION", s=104, w=660, x=310, y=190,
                  kick="Held by the states", cap="Reported and held in the owner's name", rot="-1.4")
    s_seven = elem("paper", k="fig", t="1 IN 7", s=132, w=560, x=380, y=210,
                   kick="Americans", cap="Have property on file", rot="1.1")
    s_name = elem("paper", k="body", t="Money waiting in their own name.", s=38, w=680,
                  x=300, y=250, kick="On file")
    s_uncl = elem("paper", k="slip", t="The money may be unclaimed.", s=38, w=700,
                  x=290, y=232, kick="Status", stamp="UNCLAIMED")
    s_sign = elem("paper", k="body", t="It does not have to stay that way.", s=40, w=720,
                  x=280, y=248, kick="")

    # the pool plate carries an invented case number on a folder tab; crop it out
    desk = cropped("folders", (250, 60, 1130, 636), "nolabel")

    plan = timeline([
        (0.00, dict(src=desk, z=(1.03, 1.09), sheets=[(s_bill, 0.06, (0, 470, 0.42))])),
        (2.10, dict(src=pool("mail"), z=(1.04, 1.10), dy=0.02,
                    sheets=[(s_seven, 0.10, (-560, 0, 0.40))])),
        (4.20, dict(src=pool_clip("desk"), ss=1.2, z=(1.02, 1.08),
                    sheets=[(s_name, 0.10, (0, 430, 0.38))])),
        (6.01, dict(src=desk, z=(1.05, 1.11), dx=-0.02,
                    sheets=[(s_uncl, 0.08, (620, 0, 0.36))])),
        (7.78, dict(src=pool_clip("desk"), ss=3.4, z=(1.03, 1.09),
                    sheets=[(s_sign, 0.10, (0, 460, 0.40))])),
    ])
    for _, dur, kw in plan:
        shot(dur, **kw)


# ----------------------------------------------------------------------------- style 8
def style_8():
    """DATA FIRST. The chart is the protagonist. Vector only, paper white."""
    S = "8"
    PAPER = "F7F5F0"

    def shot(dur, base, wipe=None, cards=(), z=(1.0, 1.0), dx=0.0, dy=0.0):
        """wipe: (x, y, w, h, t0, dur, direction) reveals the bar by uncovering it."""
        inputs = [img_in(base, dur)]
        f = ["[0:v]scale=%d:%d,%s[bg]" % (CW, CH, drift(z[0], z[1], dur, dx, dy))]
        last = "bg"
        if wipe:
            x, y, w, h, t0, wd = wipe
            # a paper coloured box shrinks upward off the bar: the bar appears to climb
            f.append("[%s]drawbox=x=%d:y=%d:w=%d:"
                     "h='%d*(1-min(1\\,max(0\\,(t-%.3f)/%.3f)))':color=0x%s:t=fill[wp]"
                     % (last, x, y, w, h, t0, wd, PAPER))
            last = "wp"
        specs = [{"png": c[0], "t0": c[1], **({"enable": c[2]} if len(c) > 2 else {})}
                 for c in cards]
        last = overlay_cards(f, inputs, last, specs, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "data first")

    bar = page("chart", scene="bar", h="384")
    grid_on = page("chart", scene="grid", acc="0")
    grid_acc = page("chart", scene="grid", acc="1")
    plain = page("chart", scene="plain", k="Waiting to be claimed")

    # the figure resolves out of redaction, so no intermediate number is drawn
    bill = reveal_cards(billion_stages(), 0.62, 0.08, f="publicb", s=76, c="14161A",
                        x=372, y=196, al="left")
    seven = reveal_cards(one_in_seven_stages(), 0.30, 0.09, f="publicb", s=150,
                         c="14161A", x=792, y=474, al="left")

    c_uncl = card(t="The money may be unclaimed.", f="public", s=44, c="14161A",
                  x=150, y=300, al="left")
    c_rule = card(t=" ", f="public", s=10, c=PAPER, x=150, y=250, bg="14161A",
                  pad="1 490")
    c_sign = card(t="It does not have to stay that way.", f="publicb", s=46,
                  c="14161A", x=150, y=300, al="left")
    c_acc = card(t=" ", f="public", s=10, c=EMERALD, x=150, y=372, bg=EMERALD,
                 pad="2 210")

    plan = timeline([
        # bar climbs; the label locks only once the bar has arrived
        (0.00, dict(base=bar, wipe=(150, 204, 176, 384, 0.10, 0.62),
                    cards=[(c[  "png"], c["t0"], c["enable"]) for c in bill])),
        (1.56, dict(base=bar, z=(1.0, 1.04),
                    cards=[(bill[-1]["png"], 0.0)])),
        # dot grid, one in seven marked
        (2.25, dict(base=grid_on, z=(1.0, 1.03))),
        (4.20, dict(base=grid_acc, z=(1.0, 1.04),
                    cards=[(c["png"], c["t0"], c["enable"]) for c in seven])),
        (6.01, dict(base=plain, cards=[(c_rule, 0.0), (c_uncl, 0.10)])),
        (7.78, dict(base=plain, cards=[(c_rule, 0.0), (c_sign, 0.12), (c_acc, 0.42)])),
    ])
    for _, dur, kw in plan:
        shot(dur, **kw)


# ----------------------------------------------------------------------------- style 9
def style_9():
    """ARCHIVAL PRINT. Halftone, grain, misregistration, cut paper. Nothing fades."""
    S = "9"
    CREAM = "EFE7D6"
    RED = "B23A2E"

    def halftone(key, tag, box=None):
        """A pool photograph reduced to newsprint: desaturated, posterised, dithered."""
        dst = os.path.join(PLATES, "ht-%s-%s.png" % (key, tag))
        if not os.path.exists(dst):
            vf = ("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,"
                  "format=gray,eq=contrast=1.5:brightness=0.06,"
                  "noise=alls=13:allf=t+u,"
                  "format=gray" % (CW, CH, CW, CH))
            if box:
                x, y, w, h = box
                vf = "crop=%d:%d:%d:%d," % (w, h, x, y) + vf
            run(["ffmpeg", "-y", "-v", "error", "-i", pool(key), "-vf", vf, dst])
        return dst

    def shot(dur, plate=None, ground=CREAM, elems=(), z=(1.0, 1.0), dx=0.0, dy=0.0,
             tint=True, shift=2):
        inputs = [color_in(ground, dur)]
        f = ["[0:v]scale=%d:%d[gr]" % (CW, CH)]
        last = "gr"
        if plate:
            inputs.append(img_in(plate, dur))
            n = len(inputs) - 1
            # newsprint sits as an ink layer on the cream stock, never full bleed
            f.append("[%d:v]scale=%d:%d,format=gray,format=rgba,"
                     "colorchannelmixer=aa=0.80[pl]" % (n, CW, CH))
            f.append("[%s][pl]overlay=x=0:y=0[pv]" % last)
            last = "pv"
        f.append("[%s]%s[bs]" % (last, drift(z[0], z[1], dur, dx, dy)))
        last = "bs"
        specs = [{"png": e[0], "t0": e[1], **({"slide": e[2]} if len(e) > 2 and e[2] else {})}
                 for e in elems]
        last = overlay_cards(f, inputs, last, specs, dur)
        # misregistration and paper grain, applied last so they sit over everything
        f.append("[%s]rgbashift=rh=%d:bv=%d,noise=alls=9:allf=t,"
                 "eq=saturation=0.86:contrast=1.03,format=yuv420p[v]" % (last, shift, -shift))
        return render(S, ";".join(f), dur, inputs, "archival print")

    e_kick = elem("print", k="strip", t="Public notice", x=104, y=96, w=420)
    e_bill = elem("print", k="figure", t="$70 BILLION", s=112, x=104, y=210, w=760,
                  cap="Held by the states")
    e_seven = elem("print", k="slab", t="One in seven", s=104, x=104, y=180, w=800,
                   bg=CREAM, c="22201C")
    e_amer = elem("print", k="osw", t="Americans", s=76, x=104, y=350, w=560,
                  bg=RED, c=CREAM, torn="0")
    e_name = elem("print", k="note", t="Money waiting in their own name.", s=46,
                  x=104, y=470, w=760)
    e_uncl = elem("print", k="slab", t="The money may be unclaimed.", s=72,
                  x=96, y=240, w=880, bg=CREAM, c="22201C")
    e_sign = elem("print", k="note", t="It does not have to stay that way.", s=52,
                  x=104, y=300, w=820)
    e_rule = elem("print", k="strip", t="Unclaimed property", x=104, y=560, w=470)

    ht_vault = halftone("vault", "wide", (0, 0, 900, 500))
    ht_mail = halftone("mail", "wide")
    ht_office = halftone("office", "wide")

    plan = timeline([
        (0.00, dict(plate=ht_vault, z=(1.02, 1.06),
                    elems=[(e_kick, 0.04, (-460, 0, 0.24)), (e_bill, 0.30, (0, 420, 0.30))])),
        (1.56, dict(plate=ht_vault, z=(1.06, 1.09), shift=3,
                    elems=[(e_bill, 0.0, None)])),
        (2.25, dict(plate=ht_office, z=(1.01, 1.05),
                    elems=[(e_seven, 0.06, (-840, 0, 0.26)), (e_amer, 0.46, (600, 0, 0.24))])),
        (4.20, dict(plate=ht_office, z=(1.05, 1.08),
                    elems=[(e_seven, 0.0, None), (e_amer, 0.0, None),
                           (e_name, 0.12, (0, 380, 0.28))])),
        (6.01, dict(plate=ht_mail, z=(1.02, 1.06), shift=3,
                    elems=[(e_uncl, 0.06, (0, -420, 0.28)), (e_rule, 0.52, (-500, 0, 0.22))])),
        (7.78, dict(plate=ht_mail, z=(1.06, 1.10),
                    elems=[(e_sign, 0.08, (0, 400, 0.30))])),
    ])
    for _, dur, kw in plan:
        shot(dur, **kw)


# ----------------------------------------------------------------------------- mux
def assemble(style):
    shots = sorted([s for s in SHOTS if s[0] == style], key=lambda s: s[1])
    d = os.path.join(WORK, "s%s" % style)
    listing = os.path.join(d, "concat.txt")
    with open(listing, "w") as fh:
        for s in shots:
            fh.write("file '%s'\n" % s[2])
    silent = os.path.join(d, "silent.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", listing,
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-an", silent])
    dst = os.path.join(OUT, "ep02-style-%s.mp4" % style)
    af = ("[1:a]volume=1.0[v0];"
          "[2:a]volume=0.15,highpass=f=70,lowpass=f=2400[m0];"
          "[v0][m0]amix=inputs=2:duration=first:normalize=0,"
          "loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", silent,
         "-i", os.path.join(EP, "vo.wav"), "-i", os.path.join(EP, "music.wav"),
         "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-t", "%.3f" % RUNTIME,
         "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-level", "4.0",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", dst])
    return dst, len(shots)


def normalise_audio(path, target=-14.0, tp=-2.5, lra=11.0):
    """Two-pass loudnorm to hit the target exactly. Single pass lands short."""
    import json as _json
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                        "loudnorm=I=%s:TP=%s:LRA=%s:print_format=json" % (target, tp, lra),
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        sys.stderr.write("loudnorm measurement failed for %s\n" % path)
        return None
    d = _json.loads(m[-1])
    af = ("loudnorm=I=%s:TP=%s:LRA=%s:measured_I=%s:measured_TP=%s:measured_LRA=%s:"
          "measured_thresh=%s:offset=%s:linear=true"
          % (target, tp, lra, d["input_i"], d["input_tp"], d["input_lra"],
             d["input_thresh"], d["target_offset"]))
    tmp = path + ".norm.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", path, "-map", "0:v", "-map", "0:a",
         "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-ac", "2", "-movflags", "+faststart", tmp])
    os.replace(tmp, path)
    return d


def valid(path):
    """An output counts as done if it probes as a real a/v file of the right length."""
    if not os.path.exists(path) or os.path.getsize(path) < 200000:
        return False
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type", "-of", "default=nw=1", path],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return False
    dur = re.search(r"duration=([0-9.]+)", p.stdout)
    types = set(re.findall(r"codec_type=(\w+)", p.stdout))
    return bool(dur) and abs(float(dur.group(1)) - RUNTIME) < 0.6 and \
        {"video", "audio"} <= types


BUILDERS = {"2b": style_2b, "6": style_6, "7": style_7, "8": style_8, "9": style_9}
ORDER = ["2b", "6", "7", "8", "9"]

if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    force = "--force" in args
    want = [a for a in args if a != "--force"] or ORDER
    prep()
    for s in want:
        dst = os.path.join(OUT, "ep02-style-%s.mp4" % s)
        if not force and valid(dst):
            print("style %s: already built, skipping (%.2f MB)"
                  % (s, os.path.getsize(dst) / 1048576.0))
            continue
        print("building style %s ..." % s)
        BUILDERS[s]()
        path, n = assemble(s)
        normalise_audio(path)
        print("  style %s: %d shots, %.2f MB -> %s"
              % (s, n, os.path.getsize(path) / 1048576.0, path))
