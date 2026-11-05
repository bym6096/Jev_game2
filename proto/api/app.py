"""Vercel serverless function: POST /api/app {"op": "new|write|start|play|end_turn", "blob": ..., ...} -> game view JSON.
Env vars (Vercel project settings): JEV_API_KEY (required for writing new orbs), STATE_SECRET (recommended), ACCESS_CODE (optional; if set, requests must send it)."""
import json, os, sys
from http.server import BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core

class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) if 0 <= n <= 400000 else b"{}")
            if not isinstance(body, dict): raise ValueError
        except (ValueError, UnicodeDecodeError): return self._send(400, {"error": "요청 형식이 잘못되었습니다"})
        try: code, out = core.handle(body)
        except Exception as e: return self._send(500, {"error": f"서버 오류: {type(e).__name__}"})
        self._send(code, out)
