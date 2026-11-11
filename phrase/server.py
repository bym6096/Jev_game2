"""말 조각 프로토타입 로컬 서버. index.html을 주고, POST /api/judge 로 Jev 판정을 대신 불러 준다.
실행: python3 phrase/server.py  (http://localhost:8020)
키: JEV_API_KEY 환경 변수가 있으면 Bearer로 붙이고, 없으면(클라우드) 프록시가 붙인다.
"""
import json, os, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jev
class H(BaseHTTPRequestHandler):
    def log_message(s, *a):
        pass

    def send(s, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        s.send_response(code)
        s.send_header("Content-Type", ctype)
        s.send_header("Content-Length", str(len(b)))
        s.send_header("Cache-Control", "no-store")
        s.end_headers()
        s.wfile.write(b)

    def do_GET(s):
        if s.path.split("?")[0] not in ("/", "/index.html"):
            return s.send(404, {"error": "not found"})
        s.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")

    def do_POST(s):
        if s.path != "/api/judge":
            return s.send(404, {"error": "not found"})
        try:
            n = int(s.headers.get("Content-Length", 0))
            req = json.loads(s.rfile.read(min(n, 20000)) or b"{}")
        except ValueError:
            return s.send(400, {"error": "요청 형식이 잘못되었습니다"})
        s.send(*jev.handle(req if isinstance(req, dict) else {}, s.headers))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8020"))
    print(f"http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
