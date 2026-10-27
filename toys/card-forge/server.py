"""Local toy server: serves index.html and POST /forge {"name": ...} -> card JSON.
Set JEV_API_KEY in the environment first. Run: python server.py  then open http://localhost:8000"""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import forge

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(HERE, "forged_cache.json")
try:
    CACHE = json.load(open(CACHE_PATH, encoding="utf-8"))
except Exception:
    CACHE = {}

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        self._send(404, {"error": "not found"})
    def do_POST(self):
        if self.path != "/forge":
            return self._send(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length", 0))
        name = json.loads(self.rfile.read(n) or b"{}").get("name", "").strip()[:24]
        if not name:
            return self._send(400, {"error": "이름을 적어 주세요"})
        if name in CACHE:  # same name -> same card
            return self._send(200, CACHE[name])
        try:
            card, _ = forge.forge(name)
        except Exception as e:
            return self._send(502, {"error": f"Jev 호출 실패: {e}"})
        CACHE[name] = card
        json.dump(CACHE, open(CACHE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        self._send(200, card)
    def log_message(self, *a): pass

if __name__ == "__main__":
    if not os.environ.get("JEV_API_KEY"):
        print("주의: JEV_API_KEY 환경 변수가 없습니다. 키가 자동으로 붙는 환경이 아니면 호출이 실패합니다.")
    print("http://localhost:8000 을 브라우저에서 여세요")
    ThreadingHTTPServer(("127.0.0.1", 8000), H).serve_forever()
