#!/usr/bin/env python3
"""Preview server for index.html with HTTP Range support, so the video players scrub.

Python's stock http.server ignores Range requests, which means a browser cannot
seek inside an mp4. Reviewing five trailers without scrubbing is painful, so this
adds partial content handling.

    python3 serve.py [port]

Then open http://127.0.0.1:<port>/index.html
"""
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))


class RangeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        code = args[1] if len(args) > 1 else ""
        if str(code).startswith(("4", "5")):
            sys.stderr.write("%s %s\n" % (self.path, code))

    def send_head(self):
        rng = self.headers.get("Range")
        if not rng:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path) or not os.path.exists(path):
            return super().send_head()

        m = re.match(r"bytes=(\d*)-(\d*)", rng.strip())
        if not m:
            return super().send_head()

        size = os.path.getsize(path)
        start, end = m.group(1), m.group(2)
        if start == "":                      # suffix range: last N bytes
            length = int(end or 0)
            start = max(0, size - length)
            end = size - 1
        else:
            start = int(start)
            end = int(end) if end else size - 1
        end = min(end, size - 1)
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return None

        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self._ranged = True
        self.end_headers()
        # hand back a reader bounded to the requested slice
        remaining = end - start + 1

        class Slice:
            def read(self, n=-1):
                nonlocal remaining
                if remaining <= 0:
                    return b""
                if n is None or n < 0 or n > remaining:
                    n = remaining
                chunk = f.read(n)
                remaining -= len(chunk)
                return chunk

            def close(self):
                f.close()

        return Slice()

    def end_headers(self):
        # advertise range support on full responses; the 206 path sets it itself
        if self.path.endswith(".mp4") and not getattr(self, "_ranged", False):
            self.send_header("Accept-Ranges", "bytes")
        self._ranged = False
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    # threaded: the page holds five video elements open at once, and a
    # single threaded server deadlocks under that
    srv = ThreadingHTTPServer(("127.0.0.1", port), RangeHandler)
    srv.daemon_threads = True
    print("serving %s" % ROOT)
    print("open http://127.0.0.1:%d/index.html" % port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
