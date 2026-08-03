#!/usr/bin/env python3
"""Measure the rhythm of each finished trailer. Nothing here is estimated.

Runs the scene-change detector the brief specifies, counts detected changes, and
reports the longest static hold and the average interval between changes.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def probe(path):
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=width,height,r_frame_rate,nb_frames",
                        "-of", "default=nw=1", path],
                       capture_output=True, text=True).stdout
    return d


def scenes(path, thresh=0.1):
    p = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf",
                        "select='gt(scene,%s)',showinfo" % thresh, "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    times = []
    for m in re.finditer(r"pts_time:([0-9.]+)", p.stderr):
        times.append(float(m.group(1)))
    return sorted(times)


def stats(path, thresh=0.1):
    dur = float(re.search(r"duration=([0-9.]+)", probe(path)).group(1))
    t = scenes(path, thresh)
    # boundaries: start of file, every detected change, end of file
    marks = [0.0] + t + [dur]
    gaps = [marks[i + 1] - marks[i] for i in range(len(marks) - 1)]
    return {
        "duration": dur,
        "changes": len(t),
        "shots": len(t) + 1,
        "longest_hold": max(gaps) if gaps else dur,
        "avg_interval": (dur / (len(t) + 1)) if t else dur,
        "size_mb": os.path.getsize(path) / 1048576.0,
    }


if __name__ == "__main__":
    thresh = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
    print("%-9s %8s %8s %7s %13s %13s %9s" %
          ("style", "dur", "changes", "shots", "longest hold", "avg interval", "size MB"))
    for n in (1, 2, 3, 4, 5):
        p = os.path.join(OUT, "style-%d.mp4" % n)
        if not os.path.exists(p):
            continue
        s = stats(p, thresh)
        flag = "" if s["changes"] >= 8 else "   FAILS rhythm test"
        print("style-%d  %7.2fs %8d %7d %12.2fs %12.2fs %9.2f%s"
              % (n, s["duration"], s["changes"], s["shots"], s["longest_hold"],
                 s["avg_interval"], s["size_mb"], flag))
