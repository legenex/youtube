#!/usr/bin/env python3
"""Regenerate every derived asset from the tracked HTML sources.

The document facsimiles, annotation overlays and evidence board states are all
screenshots of hand written HTML, so they are reproducible and do not need to be
carried in git. Run this once after a fresh clone, before build.py.

    python3 render-assets.py

Requires headless Chrome and the Higgsfield stills in assets/shared/gen/.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, "assets", "shared")
HTML = os.path.join(SH, "html")
DOCS = os.path.join(SH, "docs")
OVL = os.path.join(SH, "overlay")
BOARD = os.path.join(SH, "board")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def shot(dst, size, url, scale=2, transparent=False):
    args = [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=%s" % scale,
            "--window-size=%d,%d" % size, "--virtual-time-budget=1500",
            "--screenshot=" + dst, url]
    if transparent:
        args.insert(4, "--default-background-color=00000000")
    p = subprocess.run(args, capture_output=True, text=True)
    if not os.path.exists(dst):
        sys.stderr.write("failed: %s\n%s\n" % (dst, p.stderr[-800:]))
        raise SystemExit(1)
    print("  %s" % os.path.relpath(dst, HERE))


def page(name):
    return "file://" + os.path.join(HTML, name)


def main():
    for d in (DOCS, OVL, BOARD):
        os.makedirs(d, exist_ok=True)

    print("documents and browser pages")
    shot(os.path.join(DOCS, "doc-opinion.png"), (1280, 1900), page("doc-opinion.html"))
    shot(os.path.join(DOCS, "doc-surplus.png"), (1280, 1500), page("doc-surplus.html"))
    shot(os.path.join(DOCS, "doc-notice.png"), (1280, 1620), page("doc-notice.html"))
    shot(os.path.join(DOCS, "br-surplus.png"), (1280, 720), page("browser-surplus.html"))
    shot(os.path.join(DOCS, "br-search-0.png"), (1280, 720),
         page("browser-search.html") + "?nofocus=1")
    shot(os.path.join(DOCS, "br-search-1.png"), (1280, 720),
         page("browser-search.html") + "?q=T")
    shot(os.path.join(DOCS, "br-search-2.png"), (1280, 720),
         page("browser-search.html") + "?q=TYLER&y1=2015")
    shot(os.path.join(DOCS, "tex-paper.png"), (1280, 720), page("texture.html") + "?k=paper")
    shot(os.path.join(DOCS, "tex-manila.png"), (1280, 720), page("texture.html") + "?k=manila")

    print("annotation overlays")
    for name, size, key in [
        ("an-circle", (1280, 720), "circle"),
        ("an-circlewide", (1280, 500), "circleWide&h=500"),
        ("an-underline", (1160, 90), "underline&w=1160&h=90"),
        ("an-arrow", (720, 360), "arrow&w=720&h=360"),
        ("an-arrowup", (700, 430), "arrowUp&w=700&h=430"),
        ("an-box", (1280, 270), "box&h=270"),
        ("an-cursor", (120, 150), "cursor&w=120&h=150"),
    ]:
        shot(os.path.join(OVL, name + ".png"), size,
             page("annot.html") + "?k=" + key, transparent=True)

    print("evidence board states")
    # the board embeds work/img-court.png, so make sure the crops exist first
    sys.path.insert(0, HERE)
    import build
    build.prep()
    for n in range(1, 10):
        shot(os.path.join(BOARD, "state-%d.png" % n), (1920, 1080),
             page("board.html") + "?n=%d" % n, scale=1.6)

    print("done. now run: python3 build.py")


if __name__ == "__main__":
    main()
