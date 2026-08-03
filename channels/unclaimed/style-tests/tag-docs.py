#!/usr/bin/env python3
"""Tag document facsimile elements with data-hl names and append a rect dumper.

The build script needs exact pixel rectangles for the lines it lights up
(style 1) and annotates (style 3). Rather than eyeballing coordinates, we let
the browser report getBoundingClientRect for every tagged element, dump it into
the DOM, and read it back with --dump-dom.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "assets", "shared", "html")

SNIP = """
<script id="__rectdump">
(function () {
  var out = {};
  document.querySelectorAll('[data-hl]').forEach(function (el) {
    var r = el.getBoundingClientRect();
    out[el.getAttribute('data-hl')] = [Math.round(r.left), Math.round(r.top + window.scrollY),
                                       Math.round(r.width), Math.round(r.height)];
  });
  var pre = document.createElement('pre');
  pre.id = '__rects';
  pre.textContent = 'RECTS=' + JSON.stringify(out);
  pre.style.display = 'none';
  document.body.appendChild(pre);
})();
</script>
"""

EDITS = {
    "doc-surplus.html": [
        ('<h1>Tax forfeiture', '<h1 data-hl="title">Tax forfeiture'),
        ('<div class="note">', '<div class="note" data-hl="note">'),
        ('<div class="stamp">UNCLAIMED</div>', '<div class="stamp" data-hl="stamp">UNCLAIMED</div>'),
        ('<tr class="hit">', '<tr class="hit" data-hl="rowhit">'),
        ('<td class="money">$15,000.00</td>', '<td class="money" data-hl="debt">$15,000.00</td>'),
        ('<td class="money">$40,000.00</td>', '<td class="money" data-hl="price">$40,000.00</td>'),
        ('<td class="money"><b>$25,000.00</b></td>', '<td class="money" data-hl="surplus"><b>$25,000.00</b></td>'),
    ],
    "doc-notice.html": [
        ('<h1>Notice of forfeiture and sale</h1>', '<h1 data-hl="title">Notice of forfeiture and sale</h1>'),
        ('<div class="row"><div class="k">Tax year of delinquency</div>',
         '<div class="row" data-hl="year"><div class="k">Tax year of delinquency</div>'),
        ('<div class="row"><div class="k">Total tax debt owed to county</div>',
         '<div class="row" data-hl="owed"><div class="k">Total tax debt owed to county</div>'),
        ('<div class="row"><div class="k">Property sold at forfeiture sale for</div>',
         '<div class="row" data-hl="sold"><div class="k">Property sold at forfeiture sale for</div>'),
        ('<div class="row big"><div class="k">Surplus in excess of debt</div>',
         '<div class="row big" data-hl="surplus"><div class="k">Surplus in excess of debt</div>'),
        ('<div class="row"><div class="k">Amount returned to owner of record</div>',
         '<div class="row" data-hl="returned"><div class="k">Amount returned to owner of record</div>'),
        ('<div class="warn">', '<div class="warn" data-hl="warn">'),
    ],
    "doc-opinion.html": [
        ('<div class="v">TYLER', '<div class="v" data-hl="caption">TYLER'),
        ('<h2>Opinion of the Court</h2>', '<h2 data-hl="opinion">Opinion of the Court</h2>'),
        ('<p>The record establishes', '<p data-hl="record">The record establishes'),
        ('<p>The county does not dispute', '<p data-hl="dispute">The county does not dispute'),
        ('<div class="hold">', '<div class="hold" data-hl="hold">'),
        ("<p>The county's retention", "<p data-hl=\"uncon\">The county's retention"),
        ('<div class="vote">', '<div class="vote" data-hl="vote">'),
    ],
    "browser-surplus.html": [
        ('<div class="url">', '<div class="url" data-hl="url">'),
        ('<h1>Unclaimed surplus funds</h1>', '<h1 data-hl="title">Unclaimed surplus funds</h1>'),
        ('<div class="alert">', '<div class="alert" data-hl="alert">'),
        ('<tr id="target">', '<tr id="target" data-hl="rowhit">'),
        ('<td class="money">$15,000.00</td>', '<td class="money" data-hl="debt">$15,000.00</td>'),
        ('<td class="money">$40,000.00</td>', '<td class="money" data-hl="price">$40,000.00</td>'),
        ('<td class="money"><b>$25,000.00</b></td>', '<td class="money" data-hl="surplus"><b>$25,000.00</b></td>'),
    ],
}

for name, subs in EDITS.items():
    path = os.path.join(HTML, name)
    with open(path) as fh:
        src = fh.read()
    for old, new in subs:
        if 'data-hl' in old:
            continue
        if old not in src:
            print("MISS  %s  %s" % (name, old[:60]))
            continue
        src = src.replace(old, new, 1)
    if "__rectdump" not in src:
        src = src.rstrip() + "\n" + SNIP
    with open(path, "w") as fh:
        fh.write(src)
    print("ok    %-22s tagged=%d" % (name, src.count("data-hl=")))
