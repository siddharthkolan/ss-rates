#!/usr/bin/env python3
"""
Shree S S Jewellers - Rate Board server
Run:   python serve.py
Open:  http://localhost:8000   (press F for full screen)

Ye script ek hi baar upstream feed se rates leti hai (har 1 second) aur
board page ko deti hai. Chahe 1 screen ho ya 5, upstream pe load same rehta hai.
Sirf Python 3 chahiye, koi package install nahi karna.
"""
import json
import os
import ssl
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Windows ke certificate store se verify karo (Chrome jaisa). Iske liye:  pip install truststore
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

# Aakhri raasta (kam safe): set RATE_INSECURE=1 to certificate check band.
SSL_CONTEXT = ssl._create_unverified_context() if os.environ.get("RATE_INSECURE") == "1" else None

UPSTREAM = os.environ.get(
    "RATE_UPSTREAM",
    "https://bcast.bhavyalaxmibullion.com:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/bhavyalaxmi",
)
POLL_SECONDS = 1.0
PORT = int(os.environ.get("PORT", "8000"))
HERE = os.path.dirname(os.path.abspath(__file__))

state = {"text": "", "fetched_at": 0.0, "ok": False, "error": "starting"}
lock = threading.Lock()


def poller():
    while True:
        try:
            req = urllib.request.Request(UPSTREAM, headers={"User-Agent": "ShopRateBoard/1.0"})
            with urllib.request.urlopen(req, timeout=5, context=SSL_CONTEXT) as r:
                text = r.read().decode("utf-8", "replace")
            with lock:
                state.update(text=text, fetched_at=time.time(), ok=True, error="")
        except Exception as e:  # network down, server busy, etc.
            with lock:
                state.update(ok=False, error=str(e))
        time.sleep(POLL_SECONDS)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/feed":
            with lock:
                payload = dict(state)
            payload["server_time"] = time.time()
            self._send(200, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")
        elif path in ("/", "/index.html"):
            with open(os.path.join(HERE, "rate_board.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif path.startswith("/logo.") and path.count("/") == 1:
            ext = os.path.splitext(path)[1].lower()
            ctypes = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                      ".webp": "image/webp", ".svg": "image/svg+xml"}
            fp = os.path.join(HERE, path.lstrip("/"))
            if ext in ctypes and os.path.isfile(fp):
                with open(fp, "rb") as f:
                    self._send(200, f.read(), ctypes[ext])
            else:
                self._send(404, b"not found", "text/plain")
        else:
            self._send(404, b"not found", "text/plain")

    def log_message(self, *args):  # quiet
        pass


if __name__ == "__main__":
    threading.Thread(target=poller, daemon=True).start()
    print(f"Rate board chal raha hai: http://localhost:{PORT}  (band karne ke liye Ctrl+C)")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
