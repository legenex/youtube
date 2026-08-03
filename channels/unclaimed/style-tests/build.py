#!/usr/bin/env python3
"""Assemble five style-test trailers for UNCLAIMED Episode 5 from one shared asset pool.

One script, five videos. Every style uses the same voiceover, the same music bed and
the same pool of documents, generated stills and generated clips. Only the grade, the
type and the cutting change, so the comparison is fair.

    python3 build.py            # build all five
    python3 build.py 1 4        # build only styles 1 and 4

This ffmpeg has no drawtext filter, so every piece of type is rendered as a
transparent PNG by headless Chrome and composited. That costs nothing and gives
real control over condensed faces and letter spacing.

Encode contract: 1280x720, 30fps, H.264 yuv420p, CRF 21, AAC 192k, -14 LUFS, faststart.
"""

import hashlib
import os
import shutil
import subprocess
import sys
from urllib.parse import urlencode

# ----------------------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, "assets", "shared")
DOCS = os.path.join(SH, "docs")
GEN = os.path.join(SH, "gen")
OVL = os.path.join(SH, "overlay")
BOARD = os.path.join(SH, "board")
HTML = os.path.join(SH, "html")
WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "out")
FONTDIR = os.path.join(WORK, "fonts")
CARDS = os.path.join(WORK, "cards")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

W, H, FPS = 1280, 720, 30
CW, CH = 1728, 972          # composite canvas: headroom so zoom stays sharp
K = CW / float(W)           # canvas scale for coordinates authored in 1280 space
RUNTIME = 25.0

# ----------------------------------------------------------------------------- palette
INK = "0D0D0D"
EMERALD = "3AAE5C"
BONE = "F5F0E3"
TAN = "D8B26A"
MONO = "E8E8E8"
RED = "C0392B"
GREY = "8A8578"

EM_R, EM_G, EM_B = 0.227, 0.682, 0.361   # emerald as channel-mixer coefficients

FONT_SRC = {
    "impact": "/System/Library/Fonts/Supplemental/Impact.ttf",
    "cond": os.path.expanduser("~/Library/Fonts/HelveticaNeue BlackCond.ttf"),
    "narrow": "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
    "black": "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "arial": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "courier": "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    "times": "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    "inter": os.path.expanduser("~/Library/Fonts/Inter_18pt-Black.ttf"),
    "intersemi": os.path.expanduser("~/Library/Fonts/Inter_18pt-SemiBold.ttf"),
}

RECTS_CSS = {
    "opinion": {"caption": [150, 275, 980, 49], "opinion": [150, 471, 980, 31],
                "record": [150, 609, 980, 102], "dispute": [150, 732, 980, 68],
                "hold": [150, 834, 980, 71], "uncon": [150, 939, 980, 68],
                "vote": [150, 1108, 980, 122]},
    "surplus": {"title": [64, 196, 1152, 28], "note": [64, 300, 980, 69],
                "stamp": [997, 237, 195, 72], "rowhit": [64, 477, 1152, 44],
                "debt": [478, 477, 167, 44], "price": [645, 477, 193, 44],
                "surplus": [838, 477, 211, 44]},
    "notice": {"title": [90, 252, 1100, 51], "year": [92, 509, 1096, 68],
               "owed": [92, 578, 1096, 68], "sold": [92, 646, 1096, 68],
               "surplus": [92, 783, 1096, 82], "returned": [92, 865, 1096, 67],
               "warn": [90, 1056, 1010, 89]},
    "brsurplus": {"url": [108, 50, 1160, 34], "title": [40, 280, 1200, 28],
                  "alert": [40, 368, 1000, 41], "rowhit": [40, 497, 1200, 38],
                  "debt": [475, 497, 172, 38], "price": [647, 497, 202, 38],
                  "surplus": [849, 497, 217, 38]},
}
RECTS = {d: {k: [v * 2 for v in r] for k, r in rs.items()} for d, rs in RECTS_CSS.items()}

DOC_FILE = {"opinion": os.path.join(DOCS, "doc-opinion.png"),
            "surplus": os.path.join(DOCS, "doc-surplus.png"),
            "notice": os.path.join(DOCS, "doc-notice.png"),
            "brsurplus": os.path.join(DOCS, "br-surplus.png")}
DOC_SIZE = {"opinion": (2560, 3800), "surplus": (2560, 3000),
            "notice": (2560, 3240), "brsurplus": (2560, 1440)}

IMG = {"condo": "img-01-condo-empty.png", "keys": "img-02-keys-counter.png",
       "mail": "img-03-envelope-mat.png", "exterior": "img-04-condo-exterior.png",
       "court": "img-05-courthouse.png", "office": "img-06-county-office.png",
       "folders": "img-07-desk-folders.png", "sign": "img-08-yard-sign.png",
       "aerial": "img-09-aerial-suburb.png", "bedroom": "img-10-bedroom-empty.png",
       "vault": "img-11-vault-boxes.png", "stamp": "img-12-stamp-macro.png"}
CLIP = {"court": "clip-1-courthouse-push.mp4", "condo": "clip-2-condo-drift.mp4",
        "aerial": "clip-3-aerial-suburb.mp4", "desk": "clip-4-desk-papers.mp4"}

# Crops that remove content we must not show.
#   vault:  the generated still contains a gloved hand holding cash, and no shot in
#           this channel may depict a person.
#   court:  the generated frieze reads "FRANKLIN COUNTY COURTHOUSE - AD 1891", which
#           invents both a county and a date the narration never states. Cropped to
#           the colonnade so the building stays anonymous.
IMG_CROP = {"vault": (0, 0, 900, 500), "court": (0, 250, 1376, 518)}

SHOTS = []
COUNTER = {}


# ----------------------------------------------------------------------------- util
def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write("\n>>> FAILED: %s\n%s\n" % (" ".join(args[:12]), p.stderr[-2500:]))
        raise SystemExit(1)
    return p


def font(name):
    return os.path.join(FONTDIR, name + ".ttf")


def card(**params):
    """Render a full-frame transparent type card with Chrome. Cached by parameters."""
    q = urlencode(params)
    key = hashlib.sha1(q.encode()).hexdigest()[:16]
    path = os.path.join(CARDS, key + ".png")
    if not os.path.exists(path):
        run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             "--default-background-color=00000000", "--force-device-scale-factor=2",
             "--window-size=1280,720", "--screenshot=" + path,
             "file://" + os.path.join(HTML, "type.html") + "?" + q])
    return path


def fit_crop(src_w, src_h, box):
    """Clamp a crop box to the source and widen it to the 16:9 output ratio."""
    x, y, w, h = box
    target = W / float(H)
    if w / float(h) < target:
        nw = h * target
        x -= (nw - w) / 2.0
        w = nw
    else:
        nh = w / target
        y -= (nh - h) / 2.0
        h = nh
    if w > src_w:
        w = src_w
        h = w / target
    if h > src_h:
        h = src_h
        w = h * target
    x = max(0, min(x, src_w - w))
    y = max(0, min(y, src_h - h))
    return int(round(x)), int(round(y)), int(round(w)), int(round(h))


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
    d = os.path.join(WORK, "s%d" % style)
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
    """Composite a list of card specs onto `base` (a 1280x720 label). Returns new label."""
    last = base
    for i, spec in enumerate(cards):
        png = spec["png"]
        inputs.append(img_in(png, dur))
        n = len(inputs) - 1
        tag = "cd%s%d" % (base, i)
        f.append("[%d:v]scale=%d:%d,format=rgba[%s]" % (n, W, H, tag))
        t0 = spec.get("t0", 0.0)
        slam = spec.get("slam", 0)
        y = "0"
        if slam:
            y = "0-max(0\\,%d-(t-%.3f)*%d)" % (slam, t0, int(slam * FPS / 2.5))
        en = ":enable='%s'" % spec["enable"] if spec.get("enable") else (
            ":enable='gte(t,%.3f)'" % t0 if t0 > 0 else "")
        nxt = "ov%s%d" % (base, i)
        f.append("[%s][%s]overlay=x=0:y='%s'%s[%s]" % (last, tag, y, en, nxt))
        last = nxt
    return last


def timeline(pairs, total=RUNTIME):
    out = []
    for i, (t, payload) in enumerate(pairs):
        end = pairs[i + 1][0] if i + 1 < len(pairs) else total
        out.append((t, round(end - t, 4), payload))
    return out


def reveal_cards(text_stages, t0, step, **style):
    """Digit reveal: redaction blocks resolve into the real figure, then lock.

    No intermediate figure is ever shown, so nothing is invented on screen.
    """
    out = []
    for i, stage in enumerate(text_stages[:-1]):
        a = t0 + i * step
        b = t0 + (i + 1) * step
        out.append({"png": card(t=stage, **style),
                    "enable": "between(t,%.3f,%.3f)" % (a, b), "t0": a})
    lock = t0 + (len(text_stages) - 1) * step
    out.append({"png": card(t=text_stages[-1], **style),
                "enable": "gte(t,%.3f)" % lock, "t0": lock})
    return out


def money_stages(digits, label=None):
    """'15000' -> the redaction-to-figure reveal stages for $15,000.

    With a label, each stage carries the caption underneath so the figure is
    never shown without saying what it is.
    """
    d = digits
    stages = ["${2},{3}", "$%s{1},{3}" % d[0], "$%s,{3}" % d[:2],
              "$%s,%s{2}" % (d[:2], d[2]), "$%s,%s" % (d[:2], d[2:])]
    if not label:
        return stages
    cap = ('<br><span style="font-family:farial;font-size:0.20em;letter-spacing:.26em;'
           'color:%%23%s">%s</span>' % (GREY, label))
    return [s + cap for s in stages]


MONEY_LABEL = {"15000": "TAX DEBT OWED", "40000": "SOLD FOR", "25000": "SURPLUS KEPT"}


# ----------------------------------------------------------------------------- prep
def prep():
    for p in (WORK, OUT, FONTDIR, CARDS):
        os.makedirs(p, exist_ok=True)
    for name, src in FONT_SRC.items():
        if not os.path.exists(font(name)):
            if not os.path.exists(src):
                raise SystemExit("missing font: %s" % src)
            shutil.copy(src, font(name))
    for key, fn in CLIP.items():
        dst = os.path.join(WORK, "clip-%s.mp4" % key)
        if not os.path.exists(dst):
            run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(GEN, fn),
                 "-vf", "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d"
                 % (CW, CH, CW, CH, FPS),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "15",
                 "-pix_fmt", "yuv420p", "-an", dst])
    for key, (x, y, w, h) in IMG_CROP.items():
        dst = os.path.join(WORK, "img-%s.png" % key)
        if not os.path.exists(dst):
            run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(GEN, IMG[key]),
                 "-vf", "crop=%d:%d:%d:%d" % (w, h, x, y), dst])


def img_path(key):
    p = os.path.join(WORK, "img-%s.png" % key)
    return p if os.path.exists(p) else os.path.join(GEN, IMG[key])


def clip_path(key):
    return os.path.join(WORK, "clip-%s.mp4" % key)


GRADE = {
    2: "hue=s=0.14,eq=contrast=1.22:brightness=-0.22:saturation=0.62,"
       "colorchannelmixer=rr=0.82:gg=0.88:bb=0.96",
    4: "hue=s=0.34,eq=contrast=1.28:brightness=-0.10:saturation=0.88",
    5: "eq=contrast=1.06:brightness=-0.03:saturation=0.82",
}


def fill_canvas(size=None):
    w, h = size or (CW, CH)
    return "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (w, h, w, h)


# ----------------------------------------------------------------------------- style 1
def style1():
    """REDACTED DOCUMENT. One line lit in emerald, everything else dim."""
    S = 1
    dim = "colorchannelmixer=rr=0.40:gg=0.40:bb=0.40"
    to_em = ("colorchannelmixer=rr=%.3f:rg=0:rb=0:gr=%.3f:gg=0:gb=0:br=%.3f:bg=0:bb=0"
             % (EM_R, EM_G, EM_B))

    def doc_shot(doc, view_key, hl_key, dur, big=None, big_t=0.0, pad=2.0, zoom=0.045,
                 dim_level=0.40):
        src_w, src_h = DOC_SIZE[doc]
        vr = RECTS[doc][view_key]
        if pad <= 1.2:
            # close on the lit line: the line fills the frame, so the shot reads as
            # a hard change of mass against a wide dim page
            box = (vr[0] - 46, vr[1] - 46, vr[2] + 92, vr[3] + 92)
        else:
            box = (vr[0] - vr[2] * (pad - 1) / 2.0, vr[1] - vr[3] * (pad - 1) * 1.4,
                   vr[2] * pad, vr[3] * pad * 2.2)
        vx, vy, vw, vh = fit_crop(src_w, src_h, box)
        dim = ("colorchannelmixer=rr=%.2f:gg=%.2f:bb=%.2f,eq=brightness=0.045:contrast=1.06"
               % (dim_level, dim_level, dim_level))
        scale = CW / float(vw)
        hl = RECTS[doc][hl_key]
        hx = int(round((hl[0] - vx) * scale))
        hy = int(round((hl[1] - vy) * scale))
        hw = max(4, int(round(hl[2] * scale)))
        hh = max(4, int(round(hl[3] * scale)))
        hx = max(0, min(hx, CW - 8))
        hy = max(0, min(hy, CH - 8))
        hw = min(hw, CW - hx)
        hh = min(hh, CH - hy)

        inputs = [img_in(DOC_FILE[doc], dur)]
        f = ["[0:v]crop=%d:%d:%d:%d,scale=%d:%d,hue=s=0,negate,split=2[a][b]"
             % (vw, vh, vx, vy, CW, CH),
             "[a]%s[base]" % dim,
             "[b]%s,crop=%d:%d:%d:%d,format=rgba[lit]" % (to_em, hw, hh, hx, hy),
             # composite first, then drift, so the lit line stays registered
             "[base][lit]overlay=x=%d:y=%d[comp]" % (hx, hy),
             "[comp]%s[bg]" % drift(1.0, 1.0 + zoom, dur)]
        last = "bg"
        cards = []
        if big:
            html = ('%s<br><span style="font-family:farial;font-size:0.20em;'
                    'letter-spacing:.26em;color:%%23%s">%s</span>'
                    % (big, GREY, "UNANIMOUS"))
            cards.append({"png": card(t=html, f="black", s=112, c=EMERALD, x="c", y=452,
                                      lh="1.16", al="center", bg="060606E8",
                                      pad="18 40"), "t0": big_t})
        last = overlay_cards(f, inputs, last, cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "doc:%s/%s" % (doc, hl_key))

    def signoff(dur, stage, ghost=None, z=(1.0, 1.03)):
        """Sign-off card. `ghost` puts a very dim document behind it so the three
        closing beats differ in mass and do not read as one long hold."""
        if ghost:
            inputs = [img_in(DOC_FILE[ghost[0]], dur)]
            gx, gy, gw, gh = fit_crop(DOC_SIZE[ghost[0]][0], DOC_SIZE[ghost[0]][1], ghost[1])
            f = ["[0:v]crop=%d:%d:%d:%d,scale=%d:%d,hue=s=0,negate,"
                 "colorchannelmixer=rr=%.2f:gg=%.2f:bb=%.2f,%s[bg]"
                 % (gw, gh, gx, gy, CW, CH, ghost[2], ghost[2], ghost[2],
                    drift(z[0], z[1], dur))]
        else:
            inputs = [color_in("050505", dur)]
            f = ["[0:v]%s[bg]" % drift(z[0], z[1], dur)]
        cards = []
        if stage == 1:
            cards.append({"png": card(t="The money may be unclaimed.", f="intersemi",
                                      s=56, c=EMERALD, x="c", y=330), "t0": 0.0})
        else:
            cards.append({"png": card(t="The money may be unclaimed.", f="intersemi",
                                      s=52, c=EMERALD, x="c", y=296), "t0": 0.0})
            cards.append({"png": card(t="It does not have to stay that way.", f="intersemi",
                                      s=52, c=BONE, x="c", y=376),
                          "t0": 0.0 if stage == 3 else 0.22})
        last = overlay_cards(f, inputs, "bg", cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "signoff")

    # No two consecutive shots share a document, and the framing alternates between
    # a wide page and a tight line. Without that contrast the detector, and the eye,
    # read a run of dim-document shots as one long static hold.
    # Three framings alternate: a wide dim page, a mid page, and a close on the lit
    # line where emerald fills the frame. Alternating document AND framing is what
    # keeps a run of dim-document shots from reading as one static hold.
    WIDE, MID, CLOSE = 3.4, 2.2, 1.1
    plan = timeline([
        (0.00, ("notice", "year", "year", None, 0, CLOSE, 0.68)),
        (1.15, ("notice", "owed", "owed", money_stages("15000", MONEY_LABEL["15000"]), 0.10, WIDE, 0.44)),
        (2.60, ("opinion", "record", "record", None, 0, MID, 0.50)),
        (3.90, ("surplus", "title", "title", None, 0, WIDE, 0.58)),
        (5.00, ("notice", "title", "title", None, 0, CLOSE, 0.72)),
        (6.30, ("surplus", "rowhit", "rowhit", None, 0, MID, 0.56)),
        (7.45, ("notice", "sold", "sold", money_stages("40000", MONEY_LABEL["40000"]), 0.30, CLOSE, 0.60)),
        (8.90, ("opinion", "dispute", "dispute", None, 0, WIDE, 0.62)),
        (10.25, ("notice", "surplus", "surplus", money_stages("25000", MONEY_LABEL["25000"]), 0.20, CLOSE, 0.80)),
        (11.40, ("surplus", "rowhit", "surplus", None, 0, WIDE, 0.52)),
        (12.15, ("opinion", "caption", "caption", None, 0, CLOSE, 0.66)),
        (12.95, ("surplus", "stamp", "stamp", None, 0, MID, 0.42)),
        (13.60, ("opinion", "uncon", "uncon", None, 0, CLOSE, 0.72)),
        (14.40, ("notice", "warn", "warn", None, 0, WIDE, 0.48)),
        (15.20, ("opinion", "vote", "vote", "9 to 0", 0.20, MID, 0.50)),
        (16.05, ("surplus", "note", "note", None, 0, CLOSE, 0.60)),
        (16.70, ("notice", "returned", "returned", None, 0, WIDE, 0.58)),
        (17.90, ("surplus", "surplus", "surplus", None, 0, CLOSE, 0.54)),
        (19.20, ("opinion", "hold", "hold", None, 0, MID, 0.50)),
        (20.40, ("surplus", "rowhit", "rowhit", None, 0, WIDE, 0.58)),
        (21.45, ("SIGN", 1)),
        (22.60, ("SIGN", 2)),
        (23.80, ("SIGN", 3)),
    ])
    for start, dur, spec in plan:
        if spec[0] == "SIGN":
            stage = spec[1]
            if stage == 1:
                signoff(dur, 1, ghost=("surplus", RECTS["surplus"]["rowhit"], 0.52))
            elif stage == 2:
                signoff(dur, 2)
            else:
                signoff(dur, 3, ghost=("notice", RECTS["notice"]["surplus"], 0.34),
                        z=(1.06, 1.14))
            continue
        doc, view, hl, big, bt, pad, dl = spec
        if isinstance(big, list):
            # figure arrives as a digit reveal that locks
            doc_shot_reveal(S, doc, view, hl, dur, big, bt, dim, to_em, pad=pad,
                            dim_level=dl)
        else:
            doc_shot(doc, view, hl, dur, big=big, big_t=bt, pad=pad, dim_level=dl)


def doc_shot_reveal(S, doc, view_key, hl_key, dur, stages, t0, dim, to_em, pad=2.0,
                    dim_level=0.40):
    """Style 1 shot whose figure resolves out of redaction blocks."""
    src_w, src_h = DOC_SIZE[doc]
    vr = RECTS[doc][view_key]
    if pad <= 1.2:
        box = (vr[0] - 46, vr[1] - 46, vr[2] + 92, vr[3] + 92)
    else:
        box = (vr[0] - vr[2] * (pad - 1) / 2.0, vr[1] - vr[3] * (pad - 1) * 1.4,
               vr[2] * pad, vr[3] * pad * 2.2)
    vx, vy, vw, vh = fit_crop(src_w, src_h, box)
    dim = ("colorchannelmixer=rr=%.2f:gg=%.2f:bb=%.2f,eq=brightness=0.045:contrast=1.06"
               % (dim_level, dim_level, dim_level))
    scale = CW / float(vw)
    hl = RECTS[doc][hl_key]
    hx = max(0, min(int(round((hl[0] - vx) * scale)), CW - 8))
    hy = max(0, min(int(round((hl[1] - vy) * scale)), CH - 8))
    hw = min(max(4, int(round(hl[2] * scale))), CW - hx)
    hh = min(max(4, int(round(hl[3] * scale))), CH - hy)
    inputs = [img_in(DOC_FILE[doc], dur)]
    f = ["[0:v]crop=%d:%d:%d:%d,scale=%d:%d,hue=s=0,negate,split=2[a][b]"
         % (vw, vh, vx, vy, CW, CH),
         "[a]%s[base]" % dim,
         "[b]%s,crop=%d:%d:%d:%d,format=rgba[lit]" % (to_em, hw, hh, hx, hy),
         "[base][lit]overlay=x=%d:y=%d[comp]" % (hx, hy),
         "[comp]%s[bg]" % drift(1.0, 1.045, dur)]
    cards = reveal_cards(stages, t0, 0.075, f="black", s=112, c=EMERALD, x="c", y=452,
                         lh="1.16", al="center", bg="060606E8", pad="18 40")
    last = overlay_cards(f, inputs, "bg", cards, dur)
    f.append("[%s]format=yuv420p[v]" % last)
    return render(S, ";".join(f), dur, inputs, "doc:%s/%s" % (doc, hl_key))


# ----------------------------------------------------------------------------- style 2
def style2():
    """KINETIC TYPE OVER FOOTAGE. Type is the event; footage is a graded bed."""
    S = 2

    def shot(dur, src, lines=(), ss=None, z=(1.02, 1.14), dx=0.0, dy=0.0,
             block=None, reveal=None):
        if ss is None:
            inputs = [img_in(src, dur)]
            head = "[0:v]%s,%s,%s[bg]" % (fill_canvas(), GRADE[2], drift(z[0], z[1], dur, dx, dy))
        else:
            inputs = [vid_in(src, ss, dur)]
            head = ("[0:v]fps=%d,%s,%s,%s[bg]"
                    % (FPS, fill_canvas(), GRADE[2], drift(z[0], z[1], dur, dx, dy)))
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
            cards.append({"png": card(t=text, f=fnt, s=size, c=col, x=x, y=y,
                                      ls=ls, tt="uppercase",
                                      sh="0 4px 18px rgba(0,0,0,.85)"),
                          "t0": t0, "slam": 20})
        if reveal:
            stages, t0, y, size, col = reveal
            cards += reveal_cards(stages, t0, 0.07, f="impact", s=size, c=col, x="c", y=y,
                                  sh="0 4px 18px rgba(0,0,0,.85)")
        last = overlay_cards(f, inputs, last, cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "kinetic")

    C = "impact"
    plan = timeline([
        (0.00, dict(src=img_path("exterior"), z=(1.05, 1.17),
                    lines=[("2015", C, 200, "c", 250, BONE, 0.04, "0")])),
        (1.15, dict(src=img_path("mail"), z=(1.02, 1.12),
                    reveal=(money_stages("15000"), 0.06, 250, 168, EMERALD),
                    lines=[("property tax owed", C, 44, "c", 470, BONE, 0.42, ".08")])),
        (2.75, dict(src=img_path("condo"), z=(1.02, 1.13), dx=0.03,
                    block=(EMERALD, 300, 9, 0.04),
                    lines=[("a condo she no", C, 80, 70, 172, BONE, 0.04, ".01"),
                           ("longer lived in", C, 80, 70, 330, BONE, 0.20, ".01")])),
        (4.30, dict(src=clip_path("condo"), ss=0.35,
                    lines=[("she owed", C, 56, 70, 400, BONE, 0.04, ".06"),
                           ("$15,000", C, 132, 70, 460, TAN, 0.18, "0")])),
        (5.65, dict(src=img_path("court"), z=(1.04, 1.16),
                    block=(RED, 92, 78, 0.03),
                    lines=[("hennepin county", C, 58, "c", 104, INK, 0.09, ".05"),
                           ("seized it", C, 138, "c", 340, BONE, 0.32, "0")])),
        (7.10, dict(src=img_path("sign"), z=(1.03, 1.14),
                    lines=[("sold it for", C, 56, "c", 178, BONE, 0.04, ".07")],
                    reveal=(money_stages("40000"), 0.26, 250, 182, TAN))),
        (8.85, dict(src=img_path("vault"), z=(1.03, 1.15),
                    lines=[("kept every cent", C, 92, "c", 300, BONE, 0.04, ".01")])),
        (10.25, dict(src=img_path("keys"), z=(1.02, 1.10),
                     block=(BONE, 252, 7, 0.04),
                     lines=[("not the debt.", C, 96, "c", 296, BONE, 0.05, ".01")])),
        (11.10, dict(src=img_path("bedroom"), z=(1.02, 1.11),
                     lines=[("all of it.", C, 136, "c", 276, EMERALD, 0.03, "0")])),
        (12.15, dict(src=img_path("court"), z=(1.06, 1.19), dy=-0.02,
                     lines=[("2023", C, 152, "c", 92, BONE, 0.04, "0"),
                            ("the supreme court", C, 62, "c", 400, BONE, 0.58, ".05")])),
        (13.70, dict(src=clip_path("court"), ss=1.5,
                     block=(EMERALD, 468, 100, 0.28),
                     lines=[("unconstitutional", C, 76, "c", 480, INK, 0.40, ".01")])),
        (15.25, dict(src=img_path("stamp"), z=(1.04, 1.17),
                     lines=[("9 to 0", C, 226, "c", 230, BONE, 0.04, "0"),
                            ("unanimous", C, 38, "c", 520, TAN, 0.32, ".24")])),
        (16.70, dict(src=clip_path("aerial"), ss=0.4,
                     lines=[("counties are still", C, 60, 62, 400, BONE, 0.04, ".03"),
                            ("sitting on surplus", C, 60, 62, 480, BONE, 0.28, ".03")])),
        (18.20, dict(src=img_path("office"), z=(1.03, 1.15),
                     reveal=(money_stages("25000"), 0.16, 240, 190, EMERALD),
                     lines=[("held by the county", C, 42, "c", 480, BONE, 0.52, ".08")])),
        (19.90, dict(src=img_path("aerial"), z=(1.03, 1.14),
                     block=(TAN, 320, 9, 0.04),
                     lines=[("it belongs to the", C, 64, "c", 176, BONE, 0.04, ".03"),
                            ("people they took it from", C, 52, "c", 350, BONE, 0.26, ".03")])),
        (21.45, dict(src=img_path("mail"), z=(1.02, 1.11),
                     lines=[("the money may be", C, 60, "c", 196, BONE, 0.04, ".04"),
                            ("unclaimed", C, 122, "c", 290, EMERALD, 0.24, "0")])),
        (22.90, dict(src=img_path("keys"), z=(1.02, 1.12),
                     lines=[("it does not have to", C, 56, "c", 196, BONE, 0.04, ".04"),
                            ("stay that way.", C, 98, "c", 290, EMERALD, 0.28, "0")])),
    ])
    for start, dur, kw in plan:
        shot(dur, **kw)


# ----------------------------------------------------------------------------- style 3
def style3():
    """ANNOTATED SCREEN. A real browser marked up live: cursor, circles, arrows."""
    S = 3
    SCR = {"s0": os.path.join(DOCS, "br-search-0.png"),
           "s1": os.path.join(DOCS, "br-search-1.png"),
           "s2": os.path.join(DOCS, "br-search-2.png"),
           "list": os.path.join(DOCS, "br-surplus.png"),
           "op": os.path.join(DOCS, "doc-opinion.png")}
    SRC_SIZE = {"s0": (2560, 1440), "s1": (2560, 1440), "s2": (2560, 1440),
                "list": (2560, 1440), "op": (2560, 3800)}

    def wipe(t0, d=0.32):
        """Progressive left-to-right alpha reveal, so the mark draws itself on.

        crop cannot animate its width, so the reveal is done as a per-pixel alpha
        mask instead. The overlays are small, so geq stays cheap.
        """
        return ("geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                "a='if(lt(X,W*clip((T-%.3f)/%.3f,0,1)),alpha(X,Y),0)'" % (t0, d))

    def shot(dur, base, view=None, z=(1.0, 1.03), pan=(0, 0), annots=(), cursor=None,
             labels=()):
        src = SCR[base]
        sw, sh = SRC_SIZE[base]
        inputs = [img_in(src, dur)]
        crop = ""
        if view:
            cx, cy, cw, ch = fit_crop(sw, sh, view)
            crop = "crop=%d:%d:%d:%d," % (cw, ch, cx, cy)
        f = ["[0:v]%sscale=%d:%d[page]" % (crop, CW, CH)]
        last = "page"
        # annotations composite onto the page at canvas scale so they track the drift
        for i, (png, ax, ay, aw, t0) in enumerate(annots):
            inputs.append(img_in(os.path.join(OVL, png), dur))
            n = len(inputs) - 1
            f.append("[%d:v]scale=%d:-1,%s,format=rgba[an%d]"
                     % (n, int(aw * K), wipe(t0), i))
            f.append("[%s][an%d]overlay=x=%d:y=%d[oa%d]"
                     % (last, i, int(ax * K), int(ay * K), i))
            last = "oa%d" % i
        if cursor:
            xe, ye = cursor
            inputs.append(img_in(os.path.join(OVL, "an-cursor.png"), dur))
            n = len(inputs) - 1
            f.append("[%d:v]scale=%d:-1,format=rgba[cur]" % (n, int(52 * K)))
            f.append("[%s][cur]overlay=x='%s':y='%s'[oc]" % (last, xe, ye))
            last = "oc"
        f.append("[%s]%s[bg]" % (last, drift(z[0], z[1], dur, pan[0], pan[1])))
        cards = []
        for (text, size, x, y, t0) in labels:
            cards.append({"png": card(t=text, f="intersemi", s=size, c="07130B",
                                      x=x, y=y, bg=EMERALD, pad="12 20"), "t0": t0})
        last = overlay_cards(f, inputs, "bg", cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "screen")

    R = RECTS["brsurplus"]
    plan = timeline([
        (0.00, dict(base="s0", z=(1.0, 1.03),
                    cursor=("%d-%d*min(1,t/0.95)" % (int(1150 * K), int(700 * K)),
                            "%d-%d*min(1,t/0.95)" % (int(640 * K), int(300 * K))))),
        (1.15, dict(base="s1", z=(1.03, 1.07), view=(60, 430, 1600, 560),
                    cursor=(str(int(430 * K)), str(int(292 * K))))),
        (2.60, dict(base="s2", z=(1.0, 1.04),
                    annots=[("an-underline.png", 148, 604, 620, 0.18)],
                    cursor=("%d+%d*min(1,t/0.8)" % (int(300 * K), int(70 * K)),
                            str(int(548 * K))))),
        (3.90, dict(base="s2", z=(1.04, 1.10), view=(60, 880, 1500, 500),
                    labels=[("no fee to search, no fee to claim", 32, "c", 560, 0.14)])),
        (5.00, dict(base="list", z=(1.0, 1.04),
                    annots=[("an-box.png", 18, 250, 700, 0.22)])),
        (6.30, dict(base="list", z=(1.02, 1.07), view=(40, 860, 2480, 340),
                    annots=[("an-circlewide.png", 56, 250, 1170, 0.16)])),
        (7.45, dict(base="list", z=(1.0, 1.05),
                    view=(R["debt"][0] - 300, R["debt"][1] - 190, 1200, 500),
                    annots=[("an-arrow.png", 110, 74, 470, 0.20)],
                    labels=[("owed", 38, 130, 100, 0.40)])),
        (8.90, dict(base="list", z=(1.02, 1.08),
                    view=(R["price"][0] - 320, R["price"][1] - 170, 1180, 480),
                    annots=[("an-arrowup.png", 120, 240, 450, 0.18)],
                    labels=[("sold for", 38, 150, 560, 0.38)])),
        (10.25, dict(base="list", z=(1.03, 1.13),
                     view=(R["surplus"][0] - 360, R["surplus"][1] - 160, 1120, 460),
                     annots=[("an-circle.png", 40, 40, 980, 0.18)],
                     labels=[("kept", 42, "c", 560, 0.52)])),
        (12.15, dict(base="op", z=(1.0, 1.05), view=(280, 460, 2020, 720),
                     annots=[("an-underline.png", 110, 236, 920, 0.28)])),
        (13.70, dict(base="op", z=(1.02, 1.09), view=(280, 1780, 2020, 700),
                     annots=[("an-circlewide.png", 60, 190, 1160, 0.22)])),
        # a break back to the county listing so the run of opinion shots does not
        # read as one long hold
        (14.45, dict(base="list", z=(1.04, 1.10), view=(40, 460, 2480, 520),
                     annots=[("an-underline.png", 90, 300, 1000, 0.18)])),
        (15.20, dict(base="op", z=(1.04, 1.15), view=(280, 2140, 2020, 680),
                     annots=[("an-circle.png", 180, 60, 900, 0.20)])),
        (16.70, dict(base="list", z=(1.0, 1.05), view=(40, 840, 2480, 740),
                     annots=[("an-box.png", 36, 84, 1210, 0.20)])),
        (18.20, dict(base="list", z=(1.02, 1.09),
                     view=(R["alert"][0] - 70, R["alert"][1] - 110, 2240, 500),
                     annots=[("an-underline.png", 84, 420, 1090, 0.28)],
                     labels=[("you can do this yourself, for free", 32, "c", 592, 0.50)])),
        (19.90, dict(base="list", z=(1.0, 1.05),
                     annots=[("an-circlewide.png", 36, 360, 1210, 0.20)],
                     cursor=("%d-%d*min(1,t/1.1)" % (int(700 * K), int(340 * K)),
                             "%d+%d*min(1,t/1.1)" % (int(280 * K), int(230 * K))))),
        (21.45, dict(base="list", z=(1.06, 1.20),
                     view=(R["rowhit"][0], R["rowhit"][1] - 150, 2400, 460),
                     labels=[("The money may be unclaimed.", 38, "c", 566, 0.08)])),
        (22.90, dict(base="list", z=(1.10, 1.26),
                     view=(R["surplus"][0] - 380, R["surplus"][1] - 170, 1160, 470),
                     labels=[("It does not have to stay that way.", 36, "c", 566, 0.18)])),
    ])
    for start, dur, kw in plan:
        shot(dur, **kw)


# ----------------------------------------------------------------------------- style 4
def style4():
    """HIGH SPEED CUT. A visual change every 0.5 to 1 second. Speed is the effect."""
    S = 4

    def punch(dur, src=None, text=None, size=92, col=MONO, ss=None, zoom=1.16,
              doc=None, inv=False, y=280, ls=".01"):
        if doc:
            sw, sh = DOC_SIZE[doc[0]]
            r = RECTS[doc[0]][doc[1]]
            cx, cy, cw, ch = fit_crop(sw, sh, (r[0] - 110, r[1] - 150, r[2] + 220, r[3] + 300))
            base = ("[0:v]crop=%d:%d:%d:%d,scale=%d:%d,hue=s=0%s,%s[bg]"
                    % (cw, ch, cx, cy, CW, CH,
                       ",negate,colorchannelmixer=rr=0.56:gg=0.56:bb=0.56" if inv else "",
                       drift(1.0, zoom, dur)))
            inputs = [img_in(DOC_FILE[doc[0]], dur)]
        elif ss is not None:
            base = ("[0:v]fps=%d,%s,%s,%s[bg]"
                    % (FPS, fill_canvas(), GRADE[4], drift(1.0, zoom, dur)))
            inputs = [vid_in(src, ss, dur)]
        else:
            base = ("[0:v]%s,%s,%s[bg]"
                    % (fill_canvas(), GRADE[4], drift(1.0, zoom, dur)))
            inputs = [img_in(src, dur)]
        f = [base]
        cards = []
        if text:
            cards.append({"png": card(t=text, f="cond", s=size, c=col, x="c", y=y,
                                      ls=ls, tt="uppercase",
                                      sh="0 4px 16px rgba(0,0,0,.9)"), "t0": 0.0})
        last = overlay_cards(f, inputs, "bg", cards, dur)
        f.append("[%s]format=yuv420p[v]" % last)
        return render(S, ";".join(f), dur, inputs, "punch")

    def flash(col, dur):
        inputs = [color_in(col, dur)]
        return render(S, "[0:v]format=yuv420p[v]", dur, inputs, "flash")

    F = 2.0 / FPS
    seq = [
        (0.62, dict(src=img_path("exterior"), text="2015", size=200, y=230)),
        (0.55, dict(src=img_path("mail"), zoom=1.20)),
        (F, "F:" + MONO),
        (0.60, dict(doc=("notice", "year"), inv=True)),
        (0.55, dict(doc=("surplus", "rowhit"), inv=True, zoom=1.22)),
        (0.62, dict(src=img_path("keys"), text="$15,000", size=126, col=EMERALD, y=280)),
        (F, "F:" + EMERALD),
        (0.58, dict(src=img_path("condo"), text="property tax", size=64, y=310, ls=".06")),
        (0.66, dict(src=clip_path("condo"), ss=0.3)),
        (0.62, dict(src=img_path("bedroom"), text="she had moved out", size=52, y=330, ls=".05")),
        (F, "F:" + MONO),
        (0.60, dict(src=img_path("aerial"), zoom=1.22)),
        (0.62, dict(src=img_path("court"), text="the county", size=78, col=RED, y=300)),
        (0.58, dict(src=clip_path("court"), ss=0.4)),
        (F, "F:" + RED),
        (0.60, dict(src=img_path("office"), text="seized it", size=98, y=290)),
        (0.58, dict(doc=("notice", "title"), inv=True)),
        (0.62, dict(src=img_path("sign"), text="sold", size=142, y=270)),
        (0.60, dict(doc=("notice", "sold"), inv=True)),
        (0.66, dict(src=img_path("vault"), text="$40,000", size=136, col=EMERALD, y=270)),
        (F, "F:" + EMERALD),
        (0.60, dict(src=clip_path("desk"), ss=0.5)),
        (0.58, dict(src=img_path("folders"), text="kept every cent", size=58, y=320, ls=".04")),
        (0.62, dict(doc=("notice", "returned"), inv=True)),
        (F, "F:" + MONO),
        (0.60, dict(src=img_path("stamp"), text="not the debt", size=72, y=300)),
        (0.62, dict(src=img_path("keys"), text="all of it", size=120, col=EMERALD, y=280)),
        (F, "F:" + EMERALD),
        (0.62, dict(src=img_path("court"), text="2023", size=178, zoom=1.22, y=250)),
        (0.60, dict(doc=("opinion", "caption"), inv=True)),
        (0.58, dict(src=clip_path("court"), ss=2.0)),
        (0.62, dict(doc=("opinion", "uncon"), inv=True)),
        (0.60, dict(src=img_path("court"), text="unconstitutional", size=62,
                    col=EMERALD, y=320, ls=".03")),
        (F, "F:" + EMERALD),
        (0.62, dict(doc=("opinion", "vote"), inv=True)),
        (0.66, dict(src=img_path("stamp"), text="9 to 0", size=192, y=250)),
        (0.58, dict(src=img_path("folders"), text="unanimous", size=64, y=310, ls=".14")),
        (0.60, dict(src=clip_path("aerial"), ss=0.6)),
        (0.58, dict(src=img_path("aerial"), text="every county", size=74, zoom=1.20, y=300)),
        (0.62, dict(doc=("surplus", "title"), inv=True)),
        (F, "F:" + MONO),
        (0.60, dict(doc=("surplus", "rowhit"), inv=True)),
        (0.66, dict(src=img_path("vault"), text="$25,000", size=138, col=EMERALD, y=270)),
        (F, "F:" + EMERALD),
        (0.60, dict(src=img_path("office"), text="still held", size=90, y=290)),
        (0.58, dict(doc=("surplus", "stamp"), inv=True)),
        (0.62, dict(src=img_path("mail"), text="it is yours", size=94, col=EMERALD, y=290)),
        (0.70, dict(src=img_path("condo"), text="the money may be", size=58, y=310, ls=".05")),
        (0.75, dict(src=img_path("keys"), text="unclaimed", size=126, col=EMERALD, y=280)),
        (F, "F:" + EMERALD),
        (0.80, dict(src=img_path("mail"), text="it does not have to", size=54, y=320, ls=".05")),
        # the closing line is split so even the last beat stays under one second
        (0.62, dict(src=img_path("condo"), text="stay that way", size=106, col=EMERALD,
                    y=280, zoom=1.08)),
        (0.68, dict(src=img_path("keys"), text="stay that way", size=118, col=EMERALD,
                    y=270, zoom=1.14)),
    ]
    total = sum(d for d, _ in seq)
    scale = RUNTIME / total
    for dur, spec in seq:
        d = dur * scale
        if isinstance(spec, str):
            flash(spec.split(":", 1)[1], d)
        else:
            punch(d, **spec)


# ----------------------------------------------------------------------------- style 5
def style5():
    """CASE FILE. An evidence board that always carries slow continuous motion."""
    S = 5

    def board(dur, n, z=(1.02, 1.10), dx=0.0, dy=0.0):
        src = os.path.join(BOARD, "state-%d.png" % n)
        f = ["[0:v]%s,%s,%s[bg]" % (fill_canvas(), GRADE[5], drift(z[0], z[1], dur, dx, dy)),
             "[bg]format=yuv420p[v]"]
        return render(S, ";".join(f), dur, [img_in(src, dur)], "board-%d" % n)

    plan = timeline([
        (0.00, dict(n=1, z=(1.16, 1.06), dx=0.02, dy=0.03)),
        (1.15, dict(n=2, z=(1.06, 1.15), dx=-0.03, dy=-0.02)),
        (2.60, dict(n=2, z=(1.22, 1.30), dx=-0.06, dy=0.05)),
        (4.30, dict(n=3, z=(1.05, 1.14), dx=0.04, dy=-0.03)),
        (6.30, dict(n=3, z=(1.24, 1.15), dx=-0.05, dy=0.04)),
        (7.45, dict(n=4, z=(1.06, 1.16), dx=0.05, dy=0.02)),
        (8.90, dict(n=4, z=(1.26, 1.17), dx=-0.04, dy=-0.05)),
        (10.25, dict(n=5, z=(1.04, 1.15), dx=0.03, dy=0.04)),
        (12.15, dict(n=6, z=(1.08, 1.17), dx=-0.05, dy=-0.03)),
        (13.70, dict(n=6, z=(1.24, 1.32), dx=0.04, dy=0.05)),
        (15.20, dict(n=7, z=(1.05, 1.14), dx=0.03, dy=-0.04)),
        (16.70, dict(n=7, z=(1.22, 1.13), dx=-0.05, dy=0.03)),
        (18.20, dict(n=8, z=(1.05, 1.15), dx=0.04, dy=0.03)),
        (19.90, dict(n=8, z=(1.24, 1.15), dx=-0.03, dy=-0.05)),
        (21.45, dict(n=9, z=(1.12, 1.03), dx=0.02, dy=0.02)),
        (23.30, dict(n=9, z=(1.04, 1.12), dx=-0.02, dy=-0.02)),
    ])
    for start, dur, kw in plan:
        board(dur, **kw)


# ----------------------------------------------------------------------------- mux
def assemble(style):
    shots = sorted([s for s in SHOTS if s[0] == style], key=lambda s: s[1])
    d = os.path.join(WORK, "s%d" % style)
    listing = os.path.join(d, "concat.txt")
    with open(listing, "w") as fh:
        for s in shots:
            fh.write("file '%s'\n" % s[2])
    silent = os.path.join(d, "silent.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", listing,
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-an", silent])
    dst = os.path.join(OUT, "style-%d.mp4" % style)
    af = ("[1:a]volume=1.0[v0];"
          "[2:a]volume=0.15,highpass=f=70,lowpass=f=2400[m0];"
          "[v0][m0]amix=inputs=2:duration=first:normalize=0,"
          "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", silent,
         "-i", os.path.join(SH, "vo.wav"), "-i", os.path.join(SH, "music.wav"),
         "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-t", "%.3f" % RUNTIME,
         "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
         "-profile:v", "high", "-level", "4.0",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", dst])
    return dst, len(shots)


def normalise_audio(path, target=-14.0, tp=-1.5, lra=11.0):
    """Two-pass loudnorm to hit the target exactly. Single pass lands ~1.7 LU short.

    The video stream is copied, so this only rewrites audio.
    """
    import json as _json
    import re as _re
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                        "loudnorm=I=%s:TP=%s:LRA=%s:print_format=json" % (target, tp, lra),
                        "-f", "null", "-"], capture_output=True, text=True)
    m = _re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, _re.S)
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


BUILDERS = {1: style1, 2: style2, 3: style3, 4: style4, 5: style5}

if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
    prep()
    for s in want:
        print("building style %d ..." % s)
        BUILDERS[s]()
        path, n = assemble(s)
        normalise_audio(path)
        print("  style %d: %d shots, %.2f MB -> %s"
              % (s, n, os.path.getsize(path) / 1048576.0, path))
