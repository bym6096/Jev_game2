"""Vercel 서버리스 함수: POST /api/judge {"situation", "phrase"} -> Jev 판정 확률.
환경 변수: JEV_API_KEY(필수), ACCESS_CODE(선택: 설정하면 주소 끝 ?code=... 가 맞아야 판정)."""
import json, os, sys
from http.server import BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jev


class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(min(n, 20000)) or b"{}")
        except (ValueError, UnicodeDecodeError):
            return self._send(400, {"error": "요청 형식이 잘못되었습니다"})
        self._send(*jev.handle(req if isinstance(req, dict) else {}, self.headers))
