"""Local toy server (stateless): serves index.html, POST /forge {"name", "lang"} -> card JSON, POST /hero {"names", "lang"} -> hero JSON.
Set JEV_API_KEY in the environment (or .env.local) first. Run: python server.py  then open http://localhost:8000
Add --lan to let other devices on the same Wi-Fi open it (they then spend your Jev key)."""
import json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import forge

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_BODY = 8192
# No server-side cache on purpose: the same name may come out a little differently each time (Jev wobbles near ties), and in the
# game each forging costs a blank card, so re-rolling is limited by the game, not by the server. The page keeps the cards a player
# has made (and the hero it got for a deck), so nothing that has been made changes afterwards.

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def _body(self):
        """The JSON object sent with the request, or None after answering 400 (never leave the connection hanging)."""
        try:
            n = int(self.headers.get("Content-Length", 0))
            if not 0 <= n <= MAX_BODY:
                raise ValueError
            body = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(body, dict):
                raise ValueError
            return body
        except (ValueError, UnicodeDecodeError):
            self._send(400, {"error": "요청 형식이 잘못되었습니다"})
            return None
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        self._send(404, {"error": "not found"})
    def do_POST(self):
        if self.path not in ("/forge", "/hero"):
            return self._send(404, {"error": "not found"})
        body = self._body()
        if body is None:
            return
        lang = body.get("lang")
        if self.path == "/hero":
            names, err = forge.check_deck(body.get("names"), lang)
            if err:
                return self._send(400, {"error": err})
            try:
                hero, _ = forge.hero_of(names, lang)
            except Exception as e:
                return self._send(502, {"error": f"Jev 호출 실패: {e}"})
            return self._send(200, hero)
        name, err = forge.check_name(body.get("name"), lang)
        if err:
            return self._send(400, {"error": err})
        try:
            card, _ = forge.forge(name, lang)
        except Exception as e:
            return self._send(502, {"error": f"Jev 호출 실패: {e}"})
        self._send(200, card)
    def log_message(self, *a): pass

if __name__ == "__main__":
    if not os.environ.get("JEV_API_KEY") and not forge._key_from_file():
        print("주의: JEV_API_KEY(환경 변수 또는 .env.local)가 없습니다. 키가 자동으로 붙는 환경이 아니면 호출이 실패합니다.")
    lan = "--lan" in sys.argv   # opt-in: other devices on the same Wi-Fi (phone) can open it, and spend the Jev key
    print("http://localhost:8000 을 브라우저에서 여세요")
    if lan:
        print("같은 와이파이의 다른 기기에서는 http://<이 PC의 IP>:8000 (이 PC의 IP는 ipconfig로 확인). 같은 망의 누구나 카드를 만들 수 있으니 집에서만 쓰세요")
    ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", 8000), H).serve_forever()
