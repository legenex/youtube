#!/usr/bin/env python3
"""Measure the rhythm of each Episode 2 trailer. Nothing here is estimated.

Runs the scene-change detector the brief specifies, counts detected changes, and
reports the longest static hold and the average interval between changes.

    python3 measure-ep02.py           # all five
    python3 measure-ep02.py 7 9       # only those

Per-style maximum static hold: 2.0s for 2B and 8, 2.5s for 6, 7 and 9.
Fewer than 4 detected changes is a failure.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ORDER = ["2b", "6", "7", "8", "9"]
MAX_HOLD = {"2b": 2.0, "6": 2.5, "7": 2.5, "8": 2.0, "9": 2.5}


def stats(path, thresh=0.1):
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "default=nw=1", path],
                           capture_output=True, text=True).stdout
    dur = float(re.search(r"duration=([0-9.]+)", probe).group(1))
    p = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf",
                        "select='gt(scene,%s)',showinfo" % thresh, "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    t = sorted(float(m) for m in re.findall(r"pts_time:([0-9.]+)", p.stderr))
    marks = [0.0] + t + [dur]
    gaps = [marks[i + 1] - marks[i] for i in range(len(marks) - 1)]
    return {"duration": dur, "changes": len(t), "shots": len(t) + 1,
            "longest_hold": max(gaps) if gaps else dur,
            "avg_interval": dur / (len(t) + 1),
            "size_mb": os.path.getsize(path) / 1048576.0,
            "cuts": t}


if __name__ == "__main__":
    want = [a for a in sys.argv[1:]] or ORDER
    print("%-7s %7s %8s %6s %13s %13s %9s  %s"
          % ("style", "dur", "changes", "shots", "longest hold", "avg interval",
             "size MB", "verdict"))
    for s in want:
        p = os.path.join(OUT, "ep02-style-%s.mp4" % s)
        if not os.path.exists(p):
            continue
        d = stats(p)
        bad = []
        if d["changes"] < 4:
            bad.append("FEWER THAN 4 CHANGES")
        if d["longest_hold"] > MAX_HOLD[s] + 0.01:
            bad.append("HOLD OVER %.1fs" % MAX_HOLD[s])
        print("%-7s %6.2fs %8d %6d %12.2fs %12.2fs %9.2f  %s"
              % (s, d["duration"], d["changes"], d["shots"], d["longest_hold"],
                 d["avg_interval"], d["size_mb"], "; ".join(bad) if bad else "ok"))
