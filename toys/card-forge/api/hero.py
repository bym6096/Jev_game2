"""Vercel serverless function: POST /api/hero {"names": [...]} -> hero JSON (deck judged as a whole).
Env vars: JEV_API_KEY (required), ACCESS_CODE (optional; if set, requests must send it)."""
import json, os, sys
from http.server import BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import forge

class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _cors(self):
        # Only for a Unity WebGL build on another address; off unless ALLOW_ORIGIN is set (e.g. https://my-game.itch.io)
        origin = (os.environ.get("ALLOW_ORIGIN") or "").strip()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) if 0 <= n <= 8192 else b"[]")
            if not isinstance(body, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            return self._send(400, {"error": "요청 형식이 잘못되었습니다"})
        code = os.environ.get("ACCESS_CODE")
        if code and body.get("code") != code:
            return self._send(403, {"error": "입장 코드가 맞지 않습니다", "need_code": True})
        lang = body.get("lang")
        names, err = forge.check_deck(body.get("names"), lang)
        if err:
            return self._send(400, {"error": err})
        if not (os.environ.get("JEV_API_KEY") or "").strip():
            return self._send(500, {"error": "서버에 JEV_API_KEY가 없습니다"})
        try:
            hero, _ = forge.hero_of(names, lang)
        except Exception as e:
            return self._send(502, {"error": f"Jev 호출 실패: {e}"})
        self._send(200, hero)
