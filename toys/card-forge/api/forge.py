"""Vercel serverless function: POST /api/forge {"name": ...} -> card JSON.
Env vars (set in Vercel project settings): JEV_API_KEY (required), ACCESS_CODE (optional; if set, requests must send it)."""
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
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        code = os.environ.get("ACCESS_CODE")
        if code and body.get("code") != code:
            return self._send(403, {"error": "입장 코드가 맞지 않습니다", "need_code": True})
        name = str(body.get("name", "")).strip()
        lang, err = forge.check_name(name)
        if err:
            return self._send(400, {"error": err})
        try:
            card, _ = forge.forge(name)
        except Exception as e:
            return self._send(502, {"error": f"Jev 호출 실패: {e}"})
        self._send(200, card)
