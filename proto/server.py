"""Local dev server: serves index.html/style.css/app.js and POST /api/app (same handler as the Vercel function). Run: python proto/server.py"""
import os, sys, json, traceback
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core
FILES = {"/": ("index.html", "text/html; charset=utf-8"), "/index.html": ("index.html", "text/html; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/fonts/GabiaBombaram.woff2": ("fonts/GabiaBombaram.woff2", "font/woff2")}
class H(BaseHTTPRequestHandler):
    def log_message(s, *a): pass
    def send(s, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        s.send_response(code); s.send_header("Content-Type", ctype); s.send_header("Content-Length", str(len(b))); s.send_header("Cache-Control", "no-store"); s.end_headers(); s.wfile.write(b)
    def do_GET(s):
        f = FILES.get(s.path.split("?")[0])
        if not f: return s.send(404, {"error": "not found"})
        s.send(200, open(os.path.join(HERE, f[0]), "rb").read(), f[1])
    def do_POST(s):
        try:
            n = int(s.headers.get("Content-Length", 0)); body = json.loads(s.rfile.read(n) if 0 <= n <= 400000 else b"{}")
            code, out = core.handle(body if isinstance(body, dict) else {}); s.send(code, out)
        except Exception as e: traceback.print_exc(); s.send(500, {"error": f"서버 오류: {e}"})
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8010")); print(f"http://localhost:{port}"); ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
